"""Limpieza, cuarentena y validación Pandera de fuentes en bronce."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import pandera.errors

from src import config
from src.quality.schemas import SCHEMAS

HOUR_COLUMNS = [f"Hour{i:02d}" for i in range(1, 25)]
MUNICIPALITY_FIXES = {
    "MEDELIN": "MEDELLIN",
    "MEDELLINN": "MEDELLIN",
    "RIONEGRO ANTIOQUIA": "RIONEGRO",
    "SANTAFE DE ANTIOQUIA": "SANTA FE DE ANTIOQUIA",
    "EL RETIRO ANTIOQUIA": "EL RETIRO",
}
SPANISH_MONTHS = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}


class QualityRun:
    def __init__(self) -> None:
        self.stats: dict[str, dict[str, int]] = {}
        self.quarantines: dict[str, list[pd.DataFrame]] = {}

    def quarantine(self, source: str, rows: pd.DataFrame, reason: str) -> None:
        if rows.empty:
            return
        out = rows.copy()
        out["motivo"] = reason
        self.quarantines.setdefault(source, []).append(out)

    def save(self, table: str, df: pd.DataFrame, source: str, input_rows: int) -> None:
        df = df.reset_index(drop=True)
        SCHEMAS[table].validate(df, lazy=True)
        target = config.RAIZ / "data" / "silver" / f"{table}.parquet"
        target.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(target, index=False)
        self.stats[source] = {
            "antes": int(input_rows),
            "despues": int(len(df)),
            "cuarentena": sum(len(x) for x in self.quarantines.get(source, [])),
        }

    def write_quarantines(self) -> None:
        folder = config.RAIZ / "data" / "silver"
        folder.mkdir(parents=True, exist_ok=True)
        for source, parts in self.quarantines.items():
            path = folder / f"cuarentena_{source}.parquet"
            pd.concat(parts, ignore_index=True, sort=False).to_parquet(path, index=False)


def _read(name: str) -> pd.DataFrame:
    path = config.DIR_BRONZE / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Falta fuente bronce requerida: {path}")
    return pd.read_parquet(path)


def _normal(value) -> str:
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^A-Z0-9]+", " ", text.upper()).strip()


def _municipality(value) -> str:
    key = _normal(value)
    key = MUNICIPALITY_FIXES.get(key, key)
    return " ".join(word.capitalize() for word in key.split())


def _numeric(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(text, errors="coerce")


def _parse_month(value):
    if pd.isna(value):
        return pd.NaT
    text = str(value).strip().lower().replace(".", "")
    text = re.sub(r"\s+", "", text)
    match = re.fullmatch(r"(\d{1,2})/(\d{4})", text)
    if match:
        month, year = map(int, match.groups())
        return pd.Timestamp(year, month, 1) if 1 <= month <= 12 else pd.NaT
    match = re.fullmatch(r"(\d{4})-(\d{1,2})", text)
    if match:
        year, month = map(int, match.groups())
        return pd.Timestamp(year, month, 1) if 1 <= month <= 12 else pd.NaT
    match = re.fullmatch(r"([a-zñ]{3})[-/](\d{2,4})", text)
    if match and match.group(1)[:3] in SPANISH_MONTHS:
        month, year = SPANISH_MONTHS[match.group(1)[:3]], int(match.group(2))
        year = year + (2000 if year < 70 else 1900) if year < 100 else year
        return pd.Timestamp(year, month, 1)
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=True, format="mixed")
    if pd.isna(parsed):
        return pd.NaT
    return pd.Timestamp(parsed.year, parsed.month, 1)


def _sales_headers(raw: pd.DataFrame):
    aliases = {
        "fecha": ("FECHA", "PERIODO", "MES"),
        "municipio": ("MUNICIPIO", "MUNICIPIO DE VENTA"),
        "segmento": ("SEGMENTO", "SEGMENTO CLIENTE"),
        "tipo_compra": ("TIPO COMPRA", "MODALIDAD", "TIPO DE COMPRA"),
        "energia": ("ENERGIA KWH", "ENERGIA", "CONSUMO KWH"),
        "unidad": ("UNIDAD",),
        "valor": ("VALOR COP", "VALOR", "VALOR $"),
        "clientes": ("CLIENTES", "NUM CLIENTES", "NUMERO CLIENTES"),
    }
    for row_index in range(min(25, len(raw))):
        vals = [_normal(v) for v in raw.iloc[row_index].tolist()]
        found = {}
        for field, variants in aliases.items():
            for idx, val in enumerate(vals):
                if any(val == _normal(alias) or val.startswith(_normal(alias) + " ") for alias in variants):
                    found[field] = idx
                    break
        if {"fecha", "municipio", "energia"}.issubset(found):
            return row_index, found
    raise ValueError("No se encontró encabezado de columnas reconocible en la hoja EnerAndes")


def clean_sales(run: QualityRun) -> None:
    frames, total = [], 0
    for year in range(2023, 2027):
        raw = _read(f"enerandes_ventas_{year}")
        total += len(raw)
        try:
            header_row, positions = _sales_headers(raw)
        except ValueError:
            run.quarantine("enerandes", raw, "No se detectó una fila de encabezados válida")
            continue
        part = pd.DataFrame()
        for field, idx in positions.items():
            part[field] = raw.iloc[header_row + 1 :, idx].to_numpy()
        for field, fallback in (("segmento", "No informado"), ("tipo_compra", "No informado"),
                                ("valor", None), ("clientes", None), ("unidad", None)):
            if field not in part:
                part[field] = fallback
        part["fecha"] = part["fecha"].map(_parse_month)
        part["municipio"] = part["municipio"].map(_municipality)
        part["municipio_key"] = part["municipio"].map(_normal)
        part["segmento"] = part["segmento"].fillna("No informado").astype(str).str.strip()
        part["tipo_compra"] = part["tipo_compra"].fillna("No informado").astype(str).str.strip()
        part["energia_kwh"] = _numeric(part["energia"])
        if year == 2024:
            unit = part["unidad"].fillna("MWh").map(_normal)
            part.loc[unit.isin(["MWH", "MEGAWATT HORA", "MEGAWATT HOUR"]), "energia_kwh"] *= 1000
        part["valor_cop"] = _numeric(part["valor"]).fillna(0)
        part["clientes"] = _numeric(part["clientes"]).fillna(0).round().astype("Int64")
        bad = part["fecha"].isna() | part["municipio_key"].eq("") | part["energia_kwh"].isna()
        reason = np.select(
            [part["fecha"].isna(), part["municipio_key"].eq(""), part["energia_kwh"].isna(),
             part["energia_kwh"].lt(0) | part["valor_cop"].lt(0)],
            ["Fecha inválida o nota/título", "Municipio vacío", "Energía o valor no numérico",
             "Medida negativa"],
            default="",
        )
        negative = part["energia_kwh"].lt(0) | part["valor_cop"].lt(0)
        invalid = bad | negative
        source_rows = raw.iloc[header_row + 1 :].reset_index(drop=True)
        for why in pd.unique(reason[invalid]):
            run.quarantine("enerandes", source_rows.loc[reason == why], str(why))
        clean = part.loc[~invalid, [
            "fecha", "municipio", "municipio_key", "segmento", "tipo_compra",
            "energia_kwh", "valor_cop", "clientes",
        ]].copy()
        frames.append(clean)
    result = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
        columns=SCHEMAS["enerandes_ventas_mensual"].columns
    )
    dupes = result.duplicated(["fecha", "municipio_key", "segmento", "tipo_compra"], keep="first")
    run.quarantine("enerandes", result.loc[dupes], "Registro mensual duplicado")
    result = result.loc[~dupes].copy()
    result["clientes"] = result["clientes"].astype("int64")
    run.save("enerandes_ventas_mensual", result, "enerandes", total)


def _hourly(raw: pd.DataFrame, source: str, value_name: str, output: str,
            value_range=None, code_column=False) -> pd.DataFrame:
    dates = pd.to_datetime(raw["Date"], errors="coerce")
    ids = raw.get("code", raw.get("Id", pd.Series("", index=raw.index))).fillna("").astype(str)
    values = np.column_stack([_numeric(raw[col]).to_numpy(dtype=float, na_value=np.nan)
                              for col in HOUR_COLUMNS])
    n = len(raw)
    expanded = pd.DataFrame({
        "fecha": np.repeat(dates.to_numpy(), 24),
        "hora": np.tile(np.arange(1, 25), n),
        value_name: values.reshape(-1),
    })
    if code_column:
        expanded["codigo_recurso"] = np.repeat(ids.to_numpy(), 24)
    invalid = expanded["fecha"].isna() | expanded[value_name].isna()
    if value_range:
        invalid |= ~expanded[value_name].between(value_range[0], value_range[1])
    if code_column:
        invalid |= expanded["codigo_recurso"].str.strip().eq("")
    reason = "Fecha, recurso o medida faltante/fuera de rango"
    run = _ACTIVE_RUN
    run.quarantine(source, expanded.loc[invalid], reason)
    key = ["fecha", "hora"] + (["codigo_recurso"] if code_column else [])
    result = expanded.loc[~invalid].drop_duplicates(key, keep="first").copy()
    if code_column:
        duplicates = expanded.loc[~invalid].duplicated(key, keep="first")
        run.quarantine(source, expanded.loc[~invalid].loc[duplicates], "Registro horario duplicado")
    run.save(output, result, source, len(raw) * 24)
    return result


_ACTIVE_RUN: QualityRun


def clean_xm(run: QualityRun) -> None:
    global _ACTIVE_RUN
    _ACTIVE_RUN = run
    _hourly(_read("xm_precio_bolsa"), "xm_precio_bolsa", "precio_cop_kwh",
            "xm_precio_bolsa_horario", (-100000, 100000000))
    _hourly(_read("xm_demanda"), "xm_demanda", "demanda_kwh", "xm_demanda_horaria", (0, 1e12))
    for source, output, value_name, scale in (
        ("xm_embalses", "xm_embalses_diario", "volumen_util_pct", 100.0),
        ("xm_aportes_hidricos", "xm_aportes_hidricos_diario", "aportes_mwh", 1.0),
    ):
        raw = _read(source)
        dates = pd.to_datetime(raw["Date"], errors="coerce")
        values = _numeric(raw["Value"]) * scale
        frame = pd.DataFrame({"fecha": dates, value_name: values})
        invalid = frame["fecha"].isna() | frame[value_name].isna() | frame[value_name].lt(0)
        if source == "xm_embalses":
            invalid |= frame[value_name].gt(100)
        run.quarantine(source, raw.loc[invalid], "Fecha o medida diaria inválida/fuera de rango")
        result = frame.loc[~invalid].drop_duplicates("fecha").copy()
        duplicate_indices = frame.index[~invalid][frame.loc[~invalid].duplicated("fecha")]
        run.quarantine(source, raw.loc[duplicate_indices], "Registro diario duplicado")
        run.save(output, result, source, len(raw))
    _hourly(_read("xm_generacion_recurso"), "xm_generacion_recurso", "generacion_kwh",
            "xm_generacion_recurso_horario", (0, 1e12), code_column=True)

    raw = _read("xm_listado_recursos")
    result = pd.DataFrame({
        "codigo_recurso": raw["Code"].astype("string").str.strip().str.upper(),
        "recurso": raw["Name"].astype("string").str.strip(),
        "tipo_recurso": raw["Type"].fillna("No informado").astype(str).str.strip(),
        "empresa": raw["CompanyCode"].fillna("No informado").astype(str).str.strip(),
        "fuente_energia": raw["EnerSource"].fillna("No informado").astype(str).str.strip(),
        "estado": raw["State"].fillna("No informado").astype(str).str.strip(),
    })
    invalid = result["codigo_recurso"].isna() | result["codigo_recurso"].eq("") | result["recurso"].isna()
    run.quarantine("xm_listado_recursos", raw.loc[invalid], "Código o nombre del recurso vacío")
    result = result.loc[~invalid]
    duplicates = result.duplicated("codigo_recurso", keep="first")
    run.quarantine("xm_listado_recursos", raw.loc[result.index[duplicates]], "Código de recurso duplicado")
    result = result.loc[~duplicates].reset_index(drop=True)
    run.save("xm_listado_recursos", result, "xm_listado_recursos", len(raw))


def clean_ideam(run: QualityRun) -> None:
    definitions = [
        ("ideam_precipitacion_diaria", "precipitacion_mm", ["codigoestacion", "nombreestacion",
         "municipio", "fecha", "precipitacion_mm", "latitud", "longitud"]),
        ("ideam_temperatura_diaria", "temperatura", ["codigoestacion", "nombreestacion",
         "municipio", "fecha", "temperatura_media_c", "temperatura_minima_c",
         "temperatura_maxima_c", "latitud", "longitud"]),
    ]
    for source, _, _ in definitions:
        raw = _read(source)
        frame = pd.DataFrame({
            "codigo_estacion": raw["codigoestacion"].astype("string").str.strip(),
            "estacion": raw["nombreestacion"].astype("string").str.strip(),
            "municipio": raw["municipio"].map(_municipality),
            "municipio_key": raw["municipio"].map(_normal),
            "fecha": pd.to_datetime(raw["fecha"], errors="coerce"),
            "latitud": _numeric(raw["latitud"]),
            "longitud": _numeric(raw["longitud"]),
        })
        if source == "ideam_precipitacion_diaria":
            frame["precipitacion_mm"] = _numeric(raw["precipitacion_mm"])
            invalid = (frame["fecha"].isna() | frame["codigo_estacion"].isna()
                       | frame["precipitacion_mm"].isna() | frame["precipitacion_mm"].lt(0))
            output = source
            keys = ["codigo_estacion", "fecha"]
        else:
            for col in ("temperatura_media_c", "temperatura_minima_c", "temperatura_maxima_c"):
                frame[col] = _numeric(raw[col])
            invalid = frame["fecha"].isna() | frame["codigo_estacion"].isna() | frame[
                ["temperatura_media_c", "temperatura_minima_c", "temperatura_maxima_c"]
            ].isna().any(axis=1)
            invalid |= frame["temperatura_minima_c"].gt(frame["temperatura_maxima_c"])
            output = source
            keys = ["codigo_estacion", "fecha"]
        invalid |= frame["municipio_key"].eq("") | frame["latitud"].isna() | frame["longitud"].isna()
        run.quarantine(source, raw.loc[invalid], "Estación, municipio, fecha o medición inválida")
        result = frame.loc[~invalid].copy()
        duplicates = result.duplicated(keys, keep="first")
        run.quarantine(source, raw.loc[result.index[duplicates]], "Registro estación-fecha duplicado")
        run.save(output, result.loc[~duplicates].reset_index(drop=True), source, len(raw))


def clean_noaa(run: QualityRun) -> None:
    raw = _read("noaa_oni")
    seasons = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
               "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}
    month = raw["SEAS"].astype(str).str.upper().map(seasons)
    year = _numeric(raw["YR"])
    oni = _numeric(raw["ANOM"])
    result = pd.DataFrame({"fecha": pd.to_datetime(
        {"year": year, "month": month, "day": 1}, errors="coerce"
    ), "oni": oni})
    result["fase_enso"] = np.select(
        [result["oni"].ge(0.5), result["oni"].le(-0.5)],
        ["El Niño", "La Niña"], default="Neutral",
    )
    invalid = result["fecha"].isna() | result["oni"].isna()
    run.quarantine("noaa_oni", raw.loc[invalid], "Trimestre, año u ONI inválido")
    result = result.loc[~invalid]
    duplicates = result.duplicated("fecha", keep="first")
    run.quarantine("noaa_oni", raw.loc[result.index[duplicates]], "Mes central duplicado")
    run.save("noaa_oni_mensual", result.loc[~duplicates].reset_index(drop=True),
             "noaa_oni", len(raw))


def clean_divipola(run: QualityRun) -> None:
    raw = _read("divipola_municipios")
    result = pd.DataFrame({
        "codigo_municipio": raw["idmupio"].astype("string").str.strip().str.zfill(5),
        "municipio": raw["nommpio"].map(_municipality),
        "municipio_key": raw["nommpio"].map(_normal),
        "codigo_departamento": raw["iddepto"].astype("string").str.strip().str.zfill(2),
        "latitud": _numeric(raw["mpiolatitud"]),
        "longitud": _numeric(raw["mpiolongitud"]),
    })
    invalid = result.isna().any(axis=1) | result["municipio_key"].eq("")
    run.quarantine("divipola", raw.loc[invalid], "Código, municipio o coordenada DIVIPOLA inválida")
    result = result.loc[~invalid]
    duplicates = result.duplicated("codigo_municipio", keep="first")
    run.quarantine("divipola", raw.loc[result.index[duplicates]], "Código DIVIPOLA duplicado")
    result = result.loc[~duplicates].drop_duplicates("municipio_key", keep="first")
    run.save("divipola_municipios", result.reset_index(drop=True), "divipola", len(raw))


def execute() -> QualityRun:
    run = QualityRun()
    clean_sales(run)
    clean_xm(run)
    clean_ideam(run)
    clean_noaa(run)
    clean_divipola(run)
    run.write_quarantines()
    return run

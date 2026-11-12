from __future__ import annotations

import re
import unicodedata

import numpy as np
import pandas as pd

from src import config
from src.quality.schemas import SCHEMAS

COLUMNAS_HORA = [f"Hour{i:02d}" for i in range(1, 25)]

CORRECCIONES_MUNICIPIO = {
    "MEDELIN": "MEDELLIN",
    "MEDELLINN": "MEDELLIN",
    "MEDELL N": "MEDELLIN",
    "MEDELLIN D E": "MEDELLIN",
    "APARTAD": "APARTADO",
    "RIONEGRO ANT": "RIONEGRO",
    "RIONEGRO ANTIOQUIA": "RIONEGRO",
    "RIO NEGRO": "RIONEGRO",
    "SANTAFE DE ANTIOQUIA": "SANTA FE DE ANTIOQUIA",
    "STA FE DE ANTIOQUIA": "SANTA FE DE ANTIOQUIA",
    "EL RETIRO ANTIOQUIA": "EL RETIRO",
}

MESES = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
    "jan": 1, "apr": 4, "aug": 8, "dec": 12,
}

_EJECUCION_ACTIVA: EjecucionCalidad


class EjecucionCalidad:
    def __init__(self) -> None:
        self.stats: dict[str, dict[str, int]] = {}
        self.cuarentenas: dict[str, list[pd.DataFrame]] = {}
        self.metricas_reglas: list[dict[str, object]] = []

    def enviar_cuarentena(self, fuente: str, filas: pd.DataFrame, motivo: str) -> None:
        if filas.empty:
            return
        salida = filas.copy()
        salida["motivo"] = motivo
        self.cuarentenas.setdefault(fuente, []).append(salida)

    def registrar_regla(self, fuente: str, problema: str, regla: str, antes: int, despues: int) -> None:
        self.metricas_reglas.append({
            "fuente": fuente,
            "problema": problema,
            "regla": regla,
            "antes": int(antes),
            "despues": int(despues),
        })

    def guardar(
        self, tabla: str, df: pd.DataFrame, fuente: str, filas_entrada: int,
        fuera_alcance: int = 0,
    ) -> None:
        df = df.reset_index(drop=True)
        SCHEMAS[tabla].validate(df, lazy=True)
        destino = config.RAIZ / "data" / "silver" / f"{tabla}.parquet"
        destino.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(destino, index=False)
        self.stats[fuente] = {
            "antes": int(filas_entrada),
            "despues": int(len(df)),
            "cuarentena": sum(len(x) for x in self.cuarentenas.get(fuente, [])),
            "fuera_alcance": int(fuera_alcance),
        }

    def escribir_cuarentenas(self) -> None:
        carpeta = config.RAIZ / "data" / "silver"
        carpeta.mkdir(parents=True, exist_ok=True)
        for fuente, partes in self.cuarentenas.items():
            ruta = carpeta / f"cuarentena_{fuente}.parquet"
            pd.concat(partes, ignore_index=True, sort=False).to_parquet(ruta, index=False)

    def resumen_cuarentenas(self) -> dict[str, dict[str, int]]:
        return {
            fuente: {
                str(motivo): int(conteo)
                for motivo, conteo in pd.concat(partes, ignore_index=True)["motivo"]
                .value_counts(dropna=False).items()
            }
            for fuente, partes in self.cuarentenas.items()
        }


def _leer(nombre: str) -> pd.DataFrame:
    ruta = config.DIR_BRONZE / f"{nombre}.parquet"
    if not ruta.exists():
        raise FileNotFoundError(f"Falta fuente bronce requerida: {ruta}")
    return pd.read_parquet(ruta)


def _normalizar(valor) -> str:
    if pd.isna(valor):
        return ""
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^A-Z0-9]+", " ", texto.upper()).strip()


def _limpiar_municipio(valor) -> str:
    clave = _normalizar(valor)
    clave = CORRECCIONES_MUNICIPIO.get(clave, clave)
    return " ".join(palabra.capitalize() for palabra in clave.split())


def _a_numerico(serie: pd.Series) -> pd.Series:
    texto = serie.astype("string").str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce")


def _energia_a_kwh(valores: pd.Series, unidades: pd.Series) -> tuple[pd.Series, pd.Series]:
    energia = _a_numerico(valores)
    unidad_norm = unidades.map(_normalizar)
    es_mwh = unidad_norm.isin(["MWH", "MEGAWATT HORA", "MEGAWATT HOUR"])
    es_kwh = unidad_norm.isin(["KWH", "KILOWATT HORA", "KILOWATT HOUR"])
    energia.loc[es_mwh] *= 1000
    return energia, ~(es_mwh | es_kwh)


def _parsear_mes(valor):
    if pd.isna(valor):
        return pd.NaT
    texto = str(valor).strip().lower().replace(".", "")
    texto = re.sub(r"\s+", "", texto)

    m = re.fullmatch(r"(\d{1,2})/(\d{4})", texto)
    if m:
        mes, anio = map(int, m.groups())
        return pd.Timestamp(anio, mes, 1) if 1 <= mes <= 12 else pd.NaT

    m = re.fullmatch(r"(\d{4})-(\d{1,2})", texto)
    if m:
        anio, mes = map(int, m.groups())
        return pd.Timestamp(anio, mes, 1) if 1 <= mes <= 12 else pd.NaT

    m = re.fullmatch(r"([a-zñ]{3})[-/](\d{2,4})", texto)
    if m and m.group(1)[:3] in MESES:
        mes, anio = MESES[m.group(1)[:3]], int(m.group(2))
        anio = anio + (2000 if anio < 70 else 1900) if anio < 100 else anio
        return pd.Timestamp(anio, mes, 1)

    fecha = pd.to_datetime(texto, errors="coerce", dayfirst=True, format="mixed")
    if pd.isna(fecha) or fecha.year < 1900:
        return pd.NaT
    return pd.Timestamp(fecha.year, fecha.month, 1)


def _detectar_encabezados_ventas(crudo: pd.DataFrame):
    alias_cols = {
        "fecha": ("FECHA", "PERIODO", "MES", "FECHA CORTE"),
        "municipio": ("MUNICIPIO", "MUNICIPIO DE VENTA", "CIUDAD"),
        "segmento": ("SEGMENTO", "SEGMENTO CLIENTE", "TIPO CLIENTE"),
        "tipo_compra": ("TIPO COMPRA", "MODALIDAD", "TIPO DE COMPRA", "COMPRA"),
        "energia": ("ENERGIA KWH", "ENERGIA", "CONSUMO KWH", "KWH"),
        "unidad": ("UNIDAD",),
        "valor": ("VALOR COP", "VALOR", "VALOR $", "FACTURADO", "TOTAL FACTURADO COP"),
        "clientes": ("CLIENTES", "NUM CLIENTES", "NUMERO CLIENTES", "USUARIOS", "CLIENTES ACTIVOS"),
    }
    for idx_fila in range(min(25, len(crudo))):
        valores = [_normalizar(v) for v in crudo.iloc[idx_fila].tolist()]
        encontrados = {}
        for campo, variantes in alias_cols.items():
            for idx_col, val in enumerate(valores):
                if any(val == _normalizar(a) or val.startswith(_normalizar(a) + " ") for a in variantes):
                    encontrados[campo] = idx_col
                    break
        if {"fecha", "municipio", "energia"}.issubset(encontrados):
            return idx_fila, encontrados
    raise ValueError("No se encontró encabezado de columnas reconocible en la hoja EnerAndes")


def limpiar_ventas(ejecucion: EjecucionCalidad) -> None:
    partes, total = [], 0
    divipola = pd.read_parquet(config.RAIZ / "data" / "silver" / "divipola_municipios.parquet")
    codigos_municipio = dict(zip(divipola["municipio_key"], divipola["codigo_municipio"]))

    for anio in range(2023, 2027):
        crudo = _leer(f"enerandes_ventas_{anio}")
        total += len(crudo)
        try:
            fila_encabezado, posiciones = _detectar_encabezados_ventas(crudo)
        except ValueError:
            ejecucion.enviar_cuarentena("enerandes", crudo, "No se detectó una fila de encabezados válida")
            ejecucion.registrar_regla(
                "enerandes", "Encabezado ausente o irreconocible",
                "Detectar encabezados en las primeras 25 filas; hoja sin encabezado válido a cuarentena.",
                len(crudo), 0,
            )
            continue

        ejecucion.registrar_regla(
            "enerandes", f"Hoja {anio}: encabezados en posiciones distintas",
            "Buscar la fila de encabezado por nombres de columnas, no por una posición fija.",
            len(crudo), len(crudo) - fila_encabezado - 1,
        )
        ejecucion.enviar_cuarentena("enerandes", crudo.iloc[:fila_encabezado], "Título o nota anterior a los encabezados")
        ejecucion.enviar_cuarentena("enerandes", crudo.iloc[[fila_encabezado]], "Fila de encabezado")

        filas_datos = crudo.iloc[fila_encabezado + 1 :].reset_index(drop=True)
        if filas_datos.empty:
            es_total = pd.Series(False, index=filas_datos.index)
        else:
            es_total = filas_datos.astype("string").apply(
                lambda col: col.str.contains(r"\btotal\b|\bsubtotal\b", case=False, na=False)
            ).any(axis=1)

        ejecucion.enviar_cuarentena("enerandes", filas_datos.loc[es_total], "Fila de total o subtotal")
        ejecucion.registrar_regla(
            "enerandes", f"Hoja {anio}: filas de totales mezcladas con observaciones",
            "Excluir las filas TOTAL/SUBTOTAL del conjunto analítico y conservarlas en cuarentena.",
            len(filas_datos), len(filas_datos) - int(es_total.sum()),
        )
        filas_datos = filas_datos.loc[~es_total].reset_index(drop=True)

        bloque = pd.DataFrame()
        for campo, idx in posiciones.items():
            bloque[campo] = filas_datos.iloc[:, idx].to_numpy()

        for campo, defecto in (
            ("segmento", "No informado"), ("tipo_compra", "No informado"),
            ("valor", None), ("clientes", None), ("unidad", None)
        ):
            if campo not in bloque:
                bloque[campo] = defecto

        bloque["fecha"] = pd.to_datetime(bloque["fecha"].map(_parsear_mes), errors="coerce")
        bloque["municipio"] = bloque["municipio"].map(_limpiar_municipio)
        bloque["municipio_key"] = bloque["municipio"].map(_normalizar)

        antes = len(bloque)
        fechas_validas = bloque["fecha"].notna()
        ejecucion.registrar_regla(
            "enerandes", f"Hoja {anio}: formatos de fecha mixtos",
            "Interpretar formatos mixtos y llevar la fecha al primer día del mes; fechas inválidas a cuarentena.",
            antes, int(fechas_validas.sum()),
        )

        municipios_validos = bloque["municipio_key"].ne("")
        ejecucion.registrar_regla(
            "enerandes", f"Hoja {anio}: nombres de municipio vacíos o mal escritos",
            "Normalizar tildes y alias; resolver el nombre canónico con el código DIVIPOLA de Antioquia.",
            antes, int(municipios_validos.sum()),
        )

        bloque["codigo_municipio"] = bloque["municipio_key"].map(codigos_municipio)
        bloque["segmento"] = bloque["segmento"].fillna("No informado").astype(str).str.strip().map(
            lambda v: {"IND": "Industrial", "INDUSTRIAL": "Industrial"}.get(_normalizar(v), v)
        )
        bloque["tipo_compra"] = bloque["tipo_compra"].fillna("No informado").astype(str).str.strip().map(
            lambda v: {"CONTRATOS": "Contrato", "CONTRATO": "Contrato", "BOLSA": "Bolsa"}.get(_normalizar(v), v)
        )

        bloque["energia_kwh"] = _a_numerico(bloque["energia"])
        unidad_invalida = pd.Series(False, index=bloque.index)
        if anio == 2024:
            bloque["energia_kwh"], unidad_invalida = _energia_a_kwh(bloque["energia"], bloque["unidad"])
            ejecucion.registrar_regla(
                "enerandes", f"Hoja {anio}: unidades de energía faltantes o no reconocidas",
                "Convertir MWh a kWh y conservar kWh; las demás unidades se envían a cuarentena.",
                len(bloque), int((~unidad_invalida).sum()),
            )

        bloque["valor_cop"] = _a_numerico(bloque["valor"])
        bloque["clientes"] = _a_numerico(bloque["clientes"])

        sin_fecha = bloque["fecha"].isna()
        sin_municipio = bloque["municipio_key"].eq("")
        sin_divipola = bloque["codigo_municipio"].isna()
        sin_energia = bloque["energia_kwh"].isna()
        sin_valor = bloque["valor_cop"].isna()
        sin_clientes = bloque["clientes"].isna()
        negativo = (
            bloque["energia_kwh"].lt(0) | bloque["valor_cop"].lt(0) | bloque["clientes"].lt(0)
        ).fillna(False)

        motivo = np.select(
            [sin_fecha, sin_municipio, sin_divipola, sin_energia,
             sin_valor, sin_clientes, unidad_invalida, negativo],
            ["Fecha inválida o fila sin fecha", "Municipio vacío", "Municipio sin correspondencia DIVIPOLA",
             "Energía no numérica o vacía", "Valor facturado no numérico o vacío",
             "Clientes no numéricos o vacíos", "Unidad de energía vacía o desconocida",
             "Medida negativa"],
            default="",
        )
        invalido = (
            sin_fecha | sin_municipio | sin_divipola | sin_energia
            | sin_valor | sin_clientes | unidad_invalida | negativo
        )

        filas_origen = filas_datos.reset_index(drop=True)
        for razon in pd.unique(motivo[invalido]):
            ejecucion.enviar_cuarentena("enerandes", filas_origen.loc[motivo == razon], str(razon))

        ejecucion.registrar_regla(
            "enerandes", f"Hoja {anio}: valores vacíos o no numéricos",
            "Exigir energía, valor facturado y cantidad de clientes; no reemplazar nulos por cero.",
            antes, int((~(sin_energia | sin_valor | sin_clientes)).sum()),
        )
        ejecucion.registrar_regla(
            "enerandes", f"Hoja {anio}: medidas negativas",
            "Enviar energía, valor o clientes negativos a cuarentena.",
            antes, int((~negativo).sum()),
        )
        ejecucion.registrar_regla(
            "enerandes", f"Hoja {anio}: municipios sin código oficial",
            "Unir por nombre normalizado al catálogo DIVIPOLA; no inventar códigos para los no resueltos.",
            antes, int((~sin_divipola).sum()),
        )

        limpio = bloque.loc[~invalido, [
            "fecha", "codigo_municipio", "municipio", "municipio_key", "segmento", "tipo_compra",
            "energia_kwh", "valor_cop", "clientes",
        ]].copy()
        limpio["clientes"] = limpio["clientes"].round().astype("int64")
        partes.append(limpio)

    resultado = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(
        columns=SCHEMAS["enerandes_ventas_mensual"].columns
    )
    duplicados_exactos = resultado.duplicated(keep="first")
    ejecucion.enviar_cuarentena("enerandes", resultado.loc[duplicados_exactos], "Registro exactamente duplicado")
    ejecucion.registrar_regla(
        "enerandes", "Filas exactamente duplicadas",
        "Conservar una copia de cada duplicado exacto en cuarentena y mantener una sola en Plata.",
        len(resultado), int((~duplicados_exactos).sum()),
    )
    resultado = resultado.loc[~duplicados_exactos].copy()

    antes_agrupar = len(resultado)
    resultado = resultado.groupby(
        ["fecha", "codigo_municipio", "municipio", "municipio_key", "segmento", "tipo_compra"],
        as_index=False,
        dropna=False,
    )[["energia_kwh", "valor_cop", "clientes"]].sum()
    resultado["clientes"] = resultado["clientes"].astype("int64")

    ejecucion.registrar_regla(
        "enerandes", "Más de una fila válida para el mismo grano mensual",
        "Consolidar sumando medidas por mes, municipio DIVIPOLA, segmento y modalidad.",
        antes_agrupar, len(resultado),
    )
    ejecucion.guardar("enerandes_ventas_mensual", resultado, "enerandes", total)


def _despivotar_horario(
    crudo: pd.DataFrame, fuente: str, nombre_valor: str, salida: str,
    rango_valores=None, con_codigo=False
) -> pd.DataFrame:
    fechas = pd.to_datetime(crudo["Date"], errors="coerce")
    ids = crudo.get("code", crudo.get("Id", pd.Series("", index=crudo.index))).fillna("").astype(str)
    valores = np.column_stack([
        _a_numerico(crudo[col]).to_numpy(dtype=float, na_value=np.nan)
        for col in COLUMNAS_HORA
    ])
    n = len(crudo)
    expandido = pd.DataFrame({
        "fecha": np.repeat(fechas.to_numpy(), 24),
        "hora": np.tile(np.arange(1, 25), n),
        nombre_valor: valores.reshape(-1),
    })
    if con_codigo:
        expandido["codigo_recurso"] = np.repeat(ids.to_numpy(), 24)

    fecha_invalida = expandido["fecha"].isna()
    valor_nulo = expandido[nombre_valor].isna()
    fuera_rango = pd.Series(False, index=expandido.index)
    if rango_valores:
        fuera_rango = expandido[nombre_valor].notna() & ~expandido[nombre_valor].between(
            rango_valores[0], rango_valores[1]
        )
    codigo_vacio = pd.Series(False, index=expandido.index)
    if con_codigo:
        codigo_vacio = expandido["codigo_recurso"].str.strip().eq("")

    invalido = fecha_invalida | valor_nulo | fuera_rango | codigo_vacio
    ejecucion = _EJECUCION_ACTIVA

    motivo = np.select(
        [fecha_invalida, codigo_vacio, valor_nulo, fuera_rango],
        ["Fecha inválida", "Código de recurso vacío",
         "Valor horario nulo o no numérico", "Valor horario fuera de rango"],
        default="",
    )
    for razon in pd.unique(motivo[invalido]):
        ejecucion.enviar_cuarentena(fuente, expandido.loc[motivo == razon], str(razon))

    ejecucion.registrar_regla(
        fuente, "24 columnas Hour01–Hour24 en formato ancho",
        "Despivotar las 24 horas a una fila por fecha y hora.",
        len(crudo), len(expandido),
    )
    horas_validas = expandido["hora"].between(1, 24)
    ejecucion.registrar_regla(
        fuente, "Hora comercial ausente o fuera del rango 1–24",
        "Asignar las horas del nombre de columna Hour01–Hour24.",
        len(expandido), int(horas_validas.sum()),
    )
    ejecucion.registrar_regla(
        fuente, "Fechas, claves o medidas faltantes/no numéricas/fuera de rango",
        "Conservar observaciones válidas y llevar cada rechazo a cuarentena con causa.",
        len(expandido), int((~invalido).sum()),
    )

    clave = ["fecha", "hora"] + (["codigo_recurso"] if con_codigo else [])
    validos = expandido.loc[~invalido]
    resultado = validos.drop_duplicates(clave, keep="first").copy()
    duplicados = validos.duplicated(clave, keep="first")

    ejecucion.enviar_cuarentena(fuente, validos.loc[duplicados], "Registro horario duplicado")
    ejecucion.registrar_regla(
        fuente, "Claves fecha-hora-recurso duplicadas",
        "Mantener una observación por el grano horario de la métrica y guardar repeticiones en cuarentena.",
        len(validos), len(validos) - int(duplicados.sum()),
    )
    ejecucion.guardar(salida, resultado, fuente, len(crudo) * 24)
    return resultado


def limpiar_xm(ejecucion: EjecucionCalidad) -> None:
    global _EJECUCION_ACTIVA
    _EJECUCION_ACTIVA = ejecucion

    _despivotar_horario(
        _leer("xm_precio_bolsa"), "xm_precio_bolsa", "precio_cop_kwh",
        "xm_precio_bolsa_horario", (-100000, 100000000)
    )
    _despivotar_horario(
        _leer("xm_demanda"), "xm_demanda", "demanda_kwh",
        "xm_demanda_horaria", (0, 1e12)
    )

    for fuente, salida, nombre_valor, escala in (
        ("xm_embalses", "xm_embalses_diario", "volumen_util_pct", 100.0),
        ("xm_aportes_hidricos", "xm_aportes_hidricos_diario", "aportes_mwh", 1.0),
    ):
        crudo = _leer(fuente)
        fechas = pd.to_datetime(crudo["Date"], errors="coerce")
        valores = _a_numerico(crudo["Value"]) * escala
        tabla = pd.DataFrame({"fecha": fechas, nombre_valor: valores})

        fecha_invalida = tabla["fecha"].isna()
        medida_nula = tabla[nombre_valor].isna()
        medida_invalida = tabla[nombre_valor].lt(0)
        if fuente == "xm_embalses":
            medida_invalida |= tabla[nombre_valor].gt(100)

        invalido = fecha_invalida | medida_nula | medida_invalida
        motivo = np.select(
            [fecha_invalida, medida_nula, medida_invalida],
            ["Fecha diaria inválida", "Medida diaria nula o no numérica",
             "Medida diaria negativa o fuera de rango"],
            default="",
        )
        for razon in pd.unique(motivo[invalido]):
            ejecucion.enviar_cuarentena(fuente, crudo.loc[motivo == razon], str(razon))

        regla_medida = (
            "Validar porcentaje de embalses entre 0–100; aportes hídricos no negativos."
            if fuente == "xm_embalses"
            else "Validar aporte hídrico numérico y no negativo."
        )
        ejecucion.registrar_regla(
            fuente, "Fecha y medida diaria inválidas",
            f"Convertir la fecha y {regla_medida}",
            len(crudo), int((~invalido).sum()),
        )

        resultado = tabla.loc[~invalido].drop_duplicates("fecha").copy()
        idx_duplicados = tabla.index[~invalido][tabla.loc[~invalido].duplicated("fecha")]
        ejecucion.enviar_cuarentena(fuente, crudo.loc[idx_duplicados], "Registro diario duplicado")
        ejecucion.registrar_regla(
            fuente, "Filas diarias con fecha duplicada",
            "Conservar una fila por fecha y guardar duplicados en cuarentena.",
            int((~invalido).sum()), int((~invalido).sum() - len(idx_duplicados)),
        )
        ejecucion.guardar(salida, resultado, fuente, len(crudo))

    _despivotar_horario(
        _leer("xm_generacion_recurso"), "xm_generacion_recurso", "generacion_kwh",
        "xm_generacion_recurso_horario", (0, 1e12), con_codigo=True
    )

    crudo = _leer("xm_listado_recursos")
    resultado = pd.DataFrame({
        "codigo_recurso": crudo["Code"].astype("string").str.strip().str.upper(),
        "recurso": crudo["Name"].astype("string").str.strip(),
        "tipo_recurso": crudo["Type"].fillna("No informado").astype(str).str.strip(),
        "empresa": crudo["CompanyCode"].fillna("No informado").astype(str).str.strip(),
        "fuente_energia": crudo["EnerSource"].fillna("No informado").astype(str).str.strip(),
        "estado": crudo["State"].fillna("No informado").astype(str).str.strip(),
    })
    invalido = (
        resultado["codigo_recurso"].isna()
        | resultado["codigo_recurso"].eq("")
        | resultado["recurso"].isna()
        | resultado["recurso"].astype("string").str.strip().eq("")
    )
    ejecucion.enviar_cuarentena("xm_listado_recursos", crudo.loc[invalido], "Código o nombre del recurso vacío")
    ejecucion.registrar_regla(
        "xm_listado_recursos", "Código o nombre del recurso vacío",
        "Exigir código y nombre de planta/recurso; registros incompletos a cuarentena.",
        len(crudo), int((~invalido).sum()),
    )
    resultado = resultado.loc[~invalido]
    duplicados = resultado.duplicated("codigo_recurso", keep="first")
    ejecucion.enviar_cuarentena("xm_listado_recursos", crudo.loc[resultado.index[duplicados]], "Código de recurso duplicado")
    ejecucion.registrar_regla(
        "xm_listado_recursos", "Código de recurso repetido",
        "Publicar una fila por código XM y guardar duplicados en cuarentena.",
        len(resultado), int((~duplicados).sum()),
    )
    resultado = resultado.loc[~duplicados].reset_index(drop=True)
    ejecucion.guardar("xm_listado_recursos", resultado, "xm_listado_recursos", len(crudo))


def limpiar_ideam(ejecucion: EjecucionCalidad) -> None:
    divipola = pd.read_parquet(config.RAIZ / "data" / "silver" / "divipola_municipios.parquet")
    codigos_municipio = dict(zip(divipola["municipio_key"], divipola["codigo_municipio"]))

    for fuente in ("ideam_precipitacion_diaria", "ideam_temperatura_diaria"):
        crudo = _leer(fuente)
        tabla = pd.DataFrame({
            "codigo_estacion": crudo["codigoestacion"].astype("string").str.strip(),
            "estacion": crudo["nombreestacion"].astype("string").str.strip(),
            "municipio": crudo["municipio"].map(_limpiar_municipio),
            "municipio_key": crudo["municipio"].map(lambda v: _normalizar(_limpiar_municipio(v))),
            "fecha": pd.to_datetime(crudo["fecha"], errors="coerce"),
            "latitud": _a_numerico(crudo["latitud"]),
            "longitud": _a_numerico(crudo["longitud"]),
        })
        tabla["codigo_municipio"] = tabla["municipio_key"].map(codigos_municipio)

        if fuente == "ideam_precipitacion_diaria":
            tabla["precipitacion_mm"] = _a_numerico(crudo["precipitacion_mm"])
            invalido = (
                tabla["fecha"].isna()
                | tabla["codigo_estacion"].isna()
                | tabla["precipitacion_mm"].isna()
                | tabla["precipitacion_mm"].lt(0)
            )
        else:
            cols_temp = ["temperatura_media_c", "temperatura_minima_c", "temperatura_maxima_c"]
            for col in cols_temp:
                tabla[col] = _a_numerico(crudo[col])
            invalido = (
                tabla["fecha"].isna()
                | tabla["codigo_estacion"].isna()
                | tabla[cols_temp].isna().any(axis=1)
                | tabla["temperatura_minima_c"].gt(tabla["temperatura_maxima_c"])
                | ~tabla[cols_temp].apply(lambda col: col.between(-90, 60)).all(axis=1)
            )

        ubicacion_invalida = (
            tabla["municipio_key"].eq("")
            | tabla["codigo_municipio"].isna()
            | ~tabla["latitud"].between(-90, 90)
            | ~tabla["longitud"].between(-180, 180)
        )
        invalido |= ubicacion_invalida

        ejecucion.registrar_regla(
            fuente, "Estación, fecha, medición o asociación municipal inválida",
            "Estandarizar tipos, validar coordenadas y asociar el municipio al código DIVIPOLA.",
            len(crudo), int((~invalido).sum()),
        )
        ejecucion.enviar_cuarentena(fuente, crudo.loc[invalido], "Estación, municipio, fecha o medición inválida")

        resultado = tabla.loc[~invalido].copy()
        duplicados = resultado.duplicated(["codigo_estacion", "fecha"], keep="first")
        ejecucion.enviar_cuarentena(fuente, crudo.loc[resultado.index[duplicados]], "Registro estación-fecha duplicado")
        ejecucion.registrar_regla(
            fuente, "Clave estación-fecha duplicada",
            "Mantener una fila por estación y día; duplicados a cuarentena.",
            len(resultado), int((~duplicados).sum()),
        )
        ejecucion.guardar(fuente, resultado.loc[~duplicados].reset_index(drop=True), fuente, len(crudo))


def limpiar_noaa(ejecucion: EjecucionCalidad) -> None:
    crudo = _leer("noaa_oni")
    trimestres = {
        "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
        "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
    }
    mes = crudo["SEAS"].astype(str).str.upper().map(trimestres)
    anio = _a_numerico(crudo["YR"])
    oni = _a_numerico(crudo["ANOM"])

    resultado = pd.DataFrame({
        "fecha": pd.to_datetime({"year": anio, "month": mes, "day": 1}, errors="coerce"),
        "oni": oni,
    })
    resultado["fase_enso"] = np.select(
        [resultado["oni"].ge(0.5), resultado["oni"].le(-0.5)],
        ["El Niño", "La Niña"],
        default="Neutral",
    )

    invalido = resultado["fecha"].isna() | resultado["oni"].isna() | ~resultado["oni"].between(-5, 5)
    ejecucion.registrar_regla(
        "noaa_oni", "Trimestre móvil, año u ONI inválido",
        "Mapear los 12 trimestres al mes central y convertir año/ONI a tipos numéricos.",
        len(crudo), int((~invalido).sum()),
    )
    ejecucion.enviar_cuarentena("noaa_oni", crudo.loc[invalido], "Trimestre, año u ONI inválido")

    resultado = resultado.loc[~invalido]
    duplicados = resultado.duplicated("fecha", keep="first")
    ejecucion.enviar_cuarentena("noaa_oni", crudo.loc[resultado.index[duplicados]], "Mes central duplicado")
    ejecucion.registrar_regla(
        "noaa_oni", "Mes central ONI duplicado",
        "Conservar una observación ONI por mes central.",
        len(resultado), int((~duplicados).sum()),
    )
    ejecucion.registrar_regla(
        "noaa_oni", "Fase ENSO no clasificada",
        "Clasificar ONI ≥ 0,5 como El Niño, ≤ -0,5 como La Niña y el resto como Neutral.",
        len(resultado), int(resultado["fase_enso"].isin(["El Niño", "La Niña", "Neutral"]).sum()),
    )
    ejecucion.guardar("noaa_oni_mensual", resultado.loc[~duplicados].reset_index(drop=True), "noaa_oni", len(crudo))


def limpiar_divipola(ejecucion: EjecucionCalidad) -> None:
    crudo = _leer("divipola_municipios")
    departamento = crudo["iddepto"].astype("string").str.strip().str.zfill(2)
    antioquia = crudo.loc[departamento.eq("05")].copy()

    ejecucion.registrar_regla(
        "divipola", "Catálogo nacional contiene municipios fuera del alcance geográfico",
        "Limitar la dimensión municipal a Antioquia, región de EnerAndes e IDEAM en este proyecto.",
        len(crudo), len(antioquia),
    )

    resultado = pd.DataFrame({
        "codigo_municipio": antioquia["idmupio"].astype("string").str.strip().str.zfill(5),
        "municipio": antioquia["nommpio"].map(_limpiar_municipio),
        "municipio_key": antioquia["nommpio"].map(lambda v: _normalizar(_limpiar_municipio(v))),
        "codigo_departamento": departamento.loc[antioquia.index],
        "latitud": _a_numerico(antioquia["mpiolatitud"]),
        "longitud": _a_numerico(antioquia["mpiolongitud"]),
    })

    invalido = (
        resultado.isna().any(axis=1)
        | resultado["municipio_key"].eq("")
        | ~resultado["latitud"].between(-90, 90)
        | ~resultado["longitud"].between(-180, 180)
    )
    ejecucion.enviar_cuarentena("divipola", antioquia.loc[invalido], "Código, municipio o coordenada DIVIPOLA inválida")
    ejecucion.registrar_regla(
        "divipola", "Código, nombre o coordenadas municipales inválidos",
        "Exigir código DANE, nombre no vacío y coordenadas numéricas antes de publicar.",
        len(resultado), int((~invalido).sum()),
    )

    resultado = resultado.loc[~invalido]
    duplicados = resultado.duplicated("codigo_municipio", keep="first")
    ejecucion.enviar_cuarentena("divipola", antioquia.loc[resultado.index[duplicados]], "Código DIVIPOLA duplicado")
    ejecucion.registrar_regla(
        "divipola", "Códigos municipales repetidos",
        "Conservar una fila por código DIVIPOLA; no deduplicar municipios distintos por nombre.",
        len(resultado), int((~duplicados).sum()),
    )

    resultado = resultado.loc[~duplicados]
    ejecucion.guardar(
        "divipola_municipios", resultado.reset_index(drop=True), "divipola", len(crudo),
        fuera_alcance=len(crudo) - len(antioquia),
    )


def ejecutar() -> EjecucionCalidad:
    ejecucion = EjecucionCalidad()
    limpiar_divipola(ejecucion)
    limpiar_ventas(ejecucion)
    limpiar_xm(ejecucion)
    limpiar_ideam(ejecucion)
    limpiar_noaa(ejecucion)
    ejecucion.escribir_cuarentenas()
    return ejecucion
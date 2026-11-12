import pandas as pd

from src.transform import cleaners


def test_fechas_mixtas_a_mes_central():
    assert cleaners._parse_month("2025-03") == pd.Timestamp("2025-03-01")
    assert cleaners._parse_month("mar-25") == pd.Timestamp("2025-03-01")
    assert cleaners._parse_month("03/2025") == pd.Timestamp("2025-03-01")
    assert cleaners._parse_month("28/03/2025") == pd.Timestamp("2025-03-01")
    assert cleaners._parse_month("apr-24") == pd.Timestamp("2024-04-01")


def test_energia_mwh_se_convierte_a_kwh_y_unidad_desconocida_se_marca():
    energy, invalid_unit = cleaners._energy_to_kwh(
        pd.Series(["1.25", "300", "4"]),
        pd.Series(["MWh", "kWh", "GWh"]),
    )

    assert energy.tolist() == [1250, 300, 4]
    assert invalid_unit.tolist() == [False, False, True]


def test_hoja_enerandes_detecta_encabezado_variable():
    df = pd.DataFrame([
        ["Ventas anuales", None, None, None],
        ["Periodo", "Municipio", "Energia", "Unidad"],
        ["mar-25", "Medellinn", "2", "MWh"],
    ])

    row, columns = cleaners._sales_headers(df)

    assert row == 1
    assert columns["fecha"] == 0
    assert columns["municipio"] == 1
    assert columns["energia"] == 2
    assert cleaners._municipality("Medellinn") == "Medellin"


def test_unpivot_horario_crea_24_registros(tmp_path, monkeypatch):
    raw = pd.DataFrame({"Date": ["2025-01-01"], "Id": ["Sistema"], "code": ["Sistema"]})
    for hour in cleaners.HOUR_COLUMNS:
        raw[hour] = "1.5"
    run = cleaners.QualityRun()
    saved = {}
    monkeypatch.setattr(run, "save", lambda table, df, source, input_rows: saved.update(
        table=table, df=df.copy(), input_rows=input_rows
    ))
    monkeypatch.setattr(cleaners, "_ACTIVE_RUN", run, raising=False)

    result = cleaners._hourly(
        raw, "test", "precio_cop_kwh", "xm_precio_bolsa_horario", (0, 100)
    )

    assert len(result) == 24
    assert result["hora"].tolist() == list(range(1, 25))
    assert saved["input_rows"] == 24


def test_noaa_asigna_mes_central_y_fase(monkeypatch):
    raw = pd.DataFrame({
        "SEAS": ["DJF", "JFM", "FMA"],
        "YR": ["2025", "2025", "2025"],
        "ANOM": ["0.5", "-0.5", "0.49"],
    })
    run = cleaners.QualityRun()
    saved = {}
    monkeypatch.setattr(cleaners, "_read", lambda _: raw)
    monkeypatch.setattr(run, "save", lambda table, df, source, input_rows: saved.update(df=df.copy()))

    cleaners.clean_noaa(run)

    assert saved["df"]["fecha"].dt.month.tolist() == [1, 2, 3]
    assert saved["df"]["fase_enso"].tolist() == ["El Niño", "La Niña", "Neutral"]


def test_cuarentena_registra_motivo():
    run = cleaners.QualityRun()
    run.quarantine("fuente", pd.DataFrame({"dato": [None]}), "dato inválido")

    assert run.quarantines["fuente"][0]["motivo"].tolist() == ["dato inválido"]


def test_oni_con_temporada_desconocida_es_fecha_invalida(monkeypatch):
    raw = pd.DataFrame({"SEAS": ["XXX"], "YR": ["2025"], "ANOM": ["0.1"]})
    run = cleaners.QualityRun()
    monkeypatch.setattr(cleaners, "_read", lambda _: raw)
    saved = {}
    monkeypatch.setattr(run, "save", lambda table, df, source, input_rows: saved.update(df=df.copy()))

    cleaners.clean_noaa(run)

    assert saved["df"].empty
    assert run.quarantines["noaa_oni"][0]["motivo"].iloc[0] == "Trimestre, año u ONI inválido"


def test_ventas_quita_duplicado_exacto_y_agrega_parciales(monkeypatch):
    source = pd.DataFrame([
        ["Fecha", "Municipio", "Segmento", "Tipo_Compra", "Energia_kWh", "Valor_COP", "Clientes"],
        ["2023-01", "Medellin", "Industrial", "Bolsa", "2", "20", "1"],
        ["2023-01", "Medellin", "Industrial", "Bolsa", "2", "20", "1"],
        ["2023-01", "Medellin", "Industrial", "Bolsa", "3", "30", "1"],
    ])
    headers_only = pd.DataFrame([
        ["Fecha", "Municipio", "Segmento", "Tipo_Compra", "Energia_kWh", "Valor_COP", "Clientes"]
    ])
    monkeypatch.setattr(
        cleaners, "_read",
        lambda name: source if name.endswith("_2023") else headers_only,
    )
    monkeypatch.setattr(
        cleaners.pd, "read_parquet",
        lambda path: pd.DataFrame({
            "municipio_key": ["MEDELLIN"],
            "codigo_municipio": ["05001"],
        }),
    )
    run = cleaners.QualityRun()
    saved = {}
    monkeypatch.setattr(
        run, "save",
        lambda table, df, origin, input_rows: saved.update(df=df.copy(), input_rows=input_rows),
    )

    cleaners.clean_sales(run)

    assert len(saved["df"]) == 1
    assert saved["df"]["energia_kwh"].iloc[0] == 5
    assert saved["input_rows"] == 7
    assert run.quarantines["enerandes"][-1]["motivo"].iloc[0] == "Registro exactamente duplicado"

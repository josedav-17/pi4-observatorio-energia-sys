"""Contratos Pandera para todas las tablas publicadas en la capa plata."""
import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

NONEMPTY = Check.str_length(min_value=1)
NONNEGATIVE = Check.ge(0)
DATE = Column(pa.DateTime, nullable=False)
TEXT = Column(str, checks=NONEMPTY, nullable=False)
NUMBER = Column(float, nullable=False)
COUNT = Column(int, checks=NONNEGATIVE, nullable=False)


def schema(columns, unique=None):
    return DataFrameSchema(
        columns,
        checks=[] if unique is None else [Check(lambda df: not df.duplicated(unique).any())],
        strict=True,
        coerce=True,
    )


SCHEMAS = {
    "enerandes_ventas_mensual": schema(
        {
            "fecha": DATE,
            "municipio": TEXT,
            "municipio_key": TEXT,
            "segmento": TEXT,
            "tipo_compra": TEXT,
            "energia_kwh": Column(float, checks=NONNEGATIVE, nullable=False),
            "valor_cop": Column(float, checks=NONNEGATIVE, nullable=False),
            "clientes": Column(int, checks=NONNEGATIVE, nullable=False),
        },
        ["fecha", "municipio_key", "segmento", "tipo_compra"],
    ),
    "xm_precio_bolsa_horario": schema(
        {"fecha": DATE, "hora": Column(int, Check.in_range(1, 24), nullable=False),
         "precio_cop_kwh": NUMBER},
        ["fecha", "hora"],
    ),
    "xm_demanda_horaria": schema(
        {"fecha": DATE, "hora": Column(int, Check.in_range(1, 24), nullable=False),
         "demanda_kwh": Column(float, checks=NONNEGATIVE, nullable=False)},
        ["fecha", "hora"],
    ),
    "xm_embalses_diario": schema(
        {"fecha": DATE, "volumen_util_pct": Column(float, Check.in_range(0, 100), nullable=False)},
        ["fecha"],
    ),
    "xm_aportes_hidricos_diario": schema(
        {"fecha": DATE, "aportes_mwh": Column(float, checks=NONNEGATIVE, nullable=False)},
        ["fecha"],
    ),
    "xm_generacion_recurso_horario": schema(
        {"fecha": DATE, "hora": Column(int, Check.in_range(1, 24), nullable=False),
         "codigo_recurso": TEXT, "generacion_kwh": Column(float, checks=NONNEGATIVE, nullable=False)},
        ["fecha", "hora", "codigo_recurso"],
    ),
    "xm_listado_recursos": schema(
        {"codigo_recurso": TEXT, "recurso": TEXT, "tipo_recurso": TEXT,
         "empresa": TEXT, "fuente_energia": TEXT, "estado": TEXT},
        ["codigo_recurso"],
    ),
    "ideam_precipitacion_diaria": schema(
        {"codigo_estacion": TEXT, "estacion": TEXT, "municipio": TEXT, "municipio_key": TEXT,
         "fecha": DATE, "precipitacion_mm": Column(float, checks=NONNEGATIVE, nullable=False),
         "latitud": NUMBER, "longitud": NUMBER},
        ["codigo_estacion", "fecha"],
    ),
    "ideam_temperatura_diaria": schema(
        {"codigo_estacion": TEXT, "estacion": TEXT, "municipio": TEXT, "municipio_key": TEXT,
         "fecha": DATE, "temperatura_media_c": NUMBER, "temperatura_minima_c": NUMBER,
         "temperatura_maxima_c": NUMBER, "latitud": NUMBER, "longitud": NUMBER},
        ["codigo_estacion", "fecha"],
    ),
    "noaa_oni_mensual": schema(
        {"fecha": DATE, "oni": NUMBER,
         "fase_enso": Column(str, Check.isin(["El Niño", "La Niña", "Neutral"]), nullable=False)},
        ["fecha"],
    ),
    "divipola_municipios": schema(
        {"codigo_municipio": TEXT, "municipio": TEXT, "municipio_key": TEXT,
         "codigo_departamento": TEXT, "latitud": NUMBER, "longitud": NUMBER},
        ["codigo_municipio"],
    ),
}

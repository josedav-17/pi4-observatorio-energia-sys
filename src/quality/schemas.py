import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

NO_VACIO = Check.str_length(min_value=1)
NO_NEGATIVO = Check.ge(0)

FECHA = Column(pa.DateTime, nullable=False)
TEXTO = Column(str, checks=NO_VACIO, nullable=False)
LATITUD = Column(float, Check.in_range(-90, 90), nullable=False)
LONGITUD = Column(float, Check.in_range(-180, 180), nullable=False)


def crear_esquema(columnas, clave_unica=None):
    validaciones = [] if clave_unica is None else [Check(lambda df: not df.duplicated(clave_unica).any())]
    return DataFrameSchema(
        columnas,
        checks=validaciones,
        strict=True,
        coerce=True,
    )


SCHEMAS = {
    "enerandes_ventas_mensual": crear_esquema(
        {
            "fecha": FECHA,
            "codigo_municipio": TEXTO,
            "municipio": TEXTO,
            "municipio_key": TEXTO,
            "segmento": TEXTO,
            "tipo_compra": TEXTO,
            "energia_kwh": Column(float, checks=NO_NEGATIVO, nullable=False),
            "valor_cop": Column(float, checks=NO_NEGATIVO, nullable=False),
            "clientes": Column(int, checks=NO_NEGATIVO, nullable=False),
        },
        ["fecha", "municipio_key", "segmento", "tipo_compra"],
    ),
    "xm_precio_bolsa_horario": crear_esquema(
        {
            "fecha": FECHA,
            "hora": Column(int, Check.in_range(1, 24), nullable=False),
            "precio_cop_kwh": Column(float, Check.in_range(-100000, 100000000), nullable=False),
        },
        ["fecha", "hora"],
    ),
    "xm_demanda_horaria": crear_esquema(
        {
            "fecha": FECHA,
            "hora": Column(int, Check.in_range(1, 24), nullable=False),
            "demanda_kwh": Column(float, Check.in_range(0, 1e12), nullable=False),
        },
        ["fecha", "hora"],
    ),
    "xm_embalses_diario": crear_esquema(
        {
            "fecha": FECHA,
            "volumen_util_pct": Column(float, Check.in_range(0, 100), nullable=False),
        },
        ["fecha"],
    ),
    "xm_aportes_hidricos_diario": crear_esquema(
        {
            "fecha": FECHA,
            "aportes_mwh": Column(float, checks=NO_NEGATIVO, nullable=False),
        },
        ["fecha"],
    ),
    "xm_generacion_recurso_horario": crear_esquema(
        {
            "fecha": FECHA,
            "hora": Column(int, Check.in_range(1, 24), nullable=False),
            "codigo_recurso": TEXTO,
            "generacion_kwh": Column(float, Check.in_range(0, 1e12), nullable=False),
        },
        ["fecha", "hora", "codigo_recurso"],
    ),
    "xm_listado_recursos": crear_esquema(
        {
            "codigo_recurso": TEXTO,
            "recurso": TEXTO,
            "tipo_recurso": TEXTO,
            "empresa": TEXTO,
            "fuente_energia": TEXTO,
            "estado": TEXTO,
        },
        ["codigo_recurso"],
    ),
    "ideam_precipitacion_diaria": crear_esquema(
        {
            "codigo_estacion": TEXTO,
            "estacion": TEXTO,
            "codigo_municipio": TEXTO,
            "municipio": TEXTO,
            "municipio_key": TEXTO,
            "fecha": FECHA,
            "precipitacion_mm": Column(float, checks=NO_NEGATIVO, nullable=False),
            "latitud": LATITUD,
            "longitud": LONGITUD,
        },
        ["codigo_estacion", "fecha"],
    ),
    "ideam_temperatura_diaria": crear_esquema(
        {
            "codigo_estacion": TEXTO,
            "estacion": TEXTO,
            "codigo_municipio": TEXTO,
            "municipio": TEXTO,
            "municipio_key": TEXTO,
            "fecha": FECHA,
            "temperatura_media_c": Column(float, Check.in_range(-90, 60), nullable=False),
            "temperatura_minima_c": Column(float, Check.in_range(-90, 60), nullable=False),
            "temperatura_maxima_c": Column(float, Check.in_range(-90, 60), nullable=False),
            "latitud": LATITUD,
            "longitud": LONGITUD,
        },
        ["codigo_estacion", "fecha"],
    ),
    "noaa_oni_mensual": crear_esquema(
        {
            "fecha": FECHA,
            "oni": Column(float, Check.in_range(-5, 5), nullable=False),
            "fase_enso": Column(str, Check.isin(["El Niño", "La Niña", "Neutral"]), nullable=False),
        },
        ["fecha"],
    ),
    "divipola_municipios": crear_esquema(
        {
            "codigo_municipio": TEXTO,
            "municipio": TEXTO,
            "municipio_key": TEXTO,
            "codigo_departamento": TEXTO,
            "latitud": LATITUD,
            "longitud": LONGITUD,
        },
        ["codigo_municipio"],
    ),
}
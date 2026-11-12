# Diccionario de datos — capa Oro

Todos los modelos Oro son tablas DuckDB creadas por dbt. `fecha_key` es la fecha
formateada como `YYYYMMDD`; las claves de negocio se conservan para trazabilidad.

## `dim_fecha`

| Columna | Tipo lógico | Descripción | Origen |
|---|---|---|---|
| fecha_key | INTEGER | Clave YYYYMMDD | Derivada de Plata |
| fecha | DATE | Día calendario | EnerAndes / calendario |
| anio, mes, trimestre | INTEGER | Partes calendario | Derivadas |
| nombre_mes | VARCHAR | Nombre del mes | DuckDB |
| dia_mes, dia_semana | INTEGER | Día del mes e ISO weekday | DuckDB |
| nombre_dia | VARCHAR | Nombre del día | DuckDB |
| fase_enso | VARCHAR | El Niño, La Niña, Neutral o Sin clasificación | NOAA ONI |
| oni | DOUBLE | Anomalía ONI mensual | NOAA |

## `dim_municipio`

| Columna | Tipo lógico | Descripción | Origen |
|---|---|---|---|
| codigo_municipio | VARCHAR | Código DIVIPOLA o marcador NO-DANE para unmatched | MinSalud/DIVIPOLA + EnerAndes |
| municipio | VARCHAR | Nombre normalizado | DIVIPOLA / EnerAndes |
| municipio_key | VARCHAR | Nombre sin diacríticos, mayúsculas y separadores | Derivada |
| codigo_departamento | VARCHAR | Código de departamento | DIVIPOLA |
| latitud, longitud | DOUBLE | Coordenadas de referencia | DIVIPOLA |
| es_divipola | BOOLEAN | Indica match con referencia oficial | Derivada |

## `dim_recurso`

| Columna | Tipo lógico | Descripción | Origen |
|---|---|---|---|
| codigo_recurso | VARCHAR | Identificador único de planta/recurso XM | Catálogo XM |
| recurso | VARCHAR | Nombre del recurso | Catálogo XM |
| tipo_recurso | VARCHAR | Tipo técnico | Catálogo XM |
| empresa | VARCHAR | Código de agente | Catálogo XM |
| fuente_energia | VARCHAR | Fuente de energía | Catálogo XM |
| estado | VARCHAR | Estado operativo reportado | Catálogo XM |

## `dim_estacion`

| Columna | Tipo lógico | Descripción | Origen |
|---|---|---|---|
| codigo_estacion | VARCHAR | Clave de estación IDEAM | IDEAM |
| estacion | VARCHAR | Nombre de estación | IDEAM |
| municipio, municipio_key | VARCHAR | Municipio relacionado | IDEAM |
| latitud, longitud | DOUBLE | Coordenadas reportadas | IDEAM |

## `dim_enso`

| Columna | Tipo lógico | Descripción | Origen |
|---|---|---|---|
| enso_key | INTEGER | Clave YYYYMM | Derivada |
| mes | DATE | Mes central del trimestre móvil | NOAA |
| oni | DOUBLE | Oceanic Niño Index anomaly | NOAA |
| fase_enso | VARCHAR | Clasificación por umbrales ±0,5 | Derivada de NOAA |

## `fact_ventas_mensual`

| Columna | Tipo lógico | Descripción | Origen |
|---|---|---|---|
| fecha_key | INTEGER | Fecha de inicio del mes | EnerAndes / dim_fecha |
| municipio_key | VARCHAR | Código municipio relacionado | DIVIPOLA / dim_municipio |
| segmento | VARCHAR | Segmento del cliente | EnerAndes |
| tipo_compra | VARCHAR | Modalidad de compra | EnerAndes |
| energia_kwh | DOUBLE | Energía mensual | EnerAndes; MWh 2024 convertido |
| valor_cop | DOUBLE | Valor monetario | EnerAndes |
| clientes | BIGINT | Clientes reportados agregados | EnerAndes |

## `fact_mercado_horario`

| Columna | Tipo lógico | Descripción | Origen |
|---|---|---|---|
| fecha_key | INTEGER | Fecha de observación | XM / dim_fecha |
| hora | INTEGER | Hora comercial 1–24 | XM |
| precio_cop_kwh | DOUBLE | Precio de bolsa | XM |
| demanda_kwh | DOUBLE | Demanda real | XM |
| volumen_util_pct | DOUBLE | Porcentaje de embalses útiles | XM |
| aportes_mwh | DOUBLE | Aportes hídricos reportados | XM |
| oni | DOUBLE | Anomalía ONI del mes | NOAA |
| fase_enso | VARCHAR | Fase ONI | NOAA |

## `fact_generacion_recurso`

| Columna | Tipo lógico | Descripción | Origen |
|---|---|---|---|
| fecha_key | INTEGER | Fecha de generación | XM / dim_fecha |
| hora | INTEGER | Hora comercial 1–24 | XM |
| recurso_key | VARCHAR | Código del recurso | XM / dim_recurso |
| generacion_kwh | DOUBLE | Generación horaria | XM |

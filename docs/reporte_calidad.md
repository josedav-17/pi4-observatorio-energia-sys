# Reporte de calidad de datos — EA2

Última ejecución: 2026-11-12T03:17:03+00:00.

Generado automáticamente por `python -m src.transformar`. En las tablas, **Antes** es el número de filas evaluadas por la regla y **Después** el número que la supera. Las filas no corregibles se guardan en `data/silver/cuarentena_<fuente>.parquet` con la columna `motivo`.

## Resumen por fuente

| Fuente | Filas de entrada | Filas Plata | Cuarentena | Fuera de alcance |
|---|---:|---:|---:|---:|
| divipola | 1,122 | 125 | 0 | 997 |
| enerandes | 4,184 | 3,979 | 205 | 0 |
| ideam_precipitacion_diaria | 29,804 | 29,804 | 0 | 0 |
| ideam_temperatura_diaria | 17,349 | 17,349 | 0 | 0 |
| noaa_oni | 920 | 920 | 0 | 0 |
| xm_aportes_hidricos | 1,004 | 1,004 | 0 | 0 |
| xm_demanda | 24,096 | 24,096 | 0 | 0 |
| xm_embalses | 1,004 | 1,004 | 0 | 0 |
| xm_generacion_recurso | 8,408,664 | 5,935,449 | 2,473,215 | 0 |
| xm_listado_recursos | 2,493 | 2,491 | 2 | 0 |
| xm_precio_bolsa | 24,096 | 24,096 | 0 | 0 |

DIVIPOLA se limita a Antioquia, región de EnerAndes e IDEAM en este proyecto. Los municipios de otros departamentos se reportan como fuera de alcance, no como errores ni cuarentena. En las fuentes XM horarias, la entrada representa filas anchas (una por día/recurso) y Plata representa observaciones despivotadas.

## Reglas, problemas y métricas antes/después

Cada fuente tiene su propia tabla. Las reglas y los conteos de Antes/Después se registran durante el proceso de limpieza; no se escriben como cifras fijas.

### divipola

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| Catálogo nacional contiene municipios fuera del alcance geográfico | Limitar la dimensión municipal a Antioquia, región de EnerAndes e IDEAM en este proyecto. | 1,122 | 125 |
| Código, nombre o coordenadas municipales inválidos | Exigir código DANE, nombre no vacío y coordenadas numéricas antes de publicar. | 125 | 125 |
| Códigos municipales repetidos | Conservar una fila por código DIVIPOLA; no deduplicar municipios distintos por nombre. | 125 | 125 |

### enerandes

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| Hoja 2023: encabezados en posiciones distintas | Buscar la fila de encabezado por nombres de columnas, no por una posición fija. | 1,114 | 1,113 |
| Hoja 2023: filas de totales mezcladas con observaciones | Excluir las filas TOTAL/SUBTOTAL del conjunto analítico y conservarlas en cuarentena. | 1,113 | 1,112 |
| Hoja 2023: formatos de fecha mixtos | Interpretar formatos mixtos y llevar la fecha al primer día del mes; fechas inválidas a cuarentena. | 1,112 | 1,112 |
| Hoja 2023: nombres de municipio vacíos o mal escritos | Normalizar tildes y alias; resolver el nombre canónico con el código DIVIPOLA de Antioquia. | 1,112 | 1,112 |
| Hoja 2023: valores vacíos o no numéricos | Exigir energía, valor facturado y cantidad de clientes; no reemplazar nulos por cero. | 1,112 | 1,096 |
| Hoja 2023: medidas negativas | Enviar energía, valor o clientes negativos a cuarentena. | 1,112 | 1,105 |
| Hoja 2023: municipios sin código oficial | Unir por nombre normalizado al catálogo DIVIPOLA; no inventar códigos para los no resueltos. | 1,112 | 1,112 |
| Hoja 2024: encabezados en posiciones distintas | Buscar la fila de encabezado por nombres de columnas, no por una posición fija. | 1,114 | 1,113 |
| Hoja 2024: filas de totales mezcladas con observaciones | Excluir las filas TOTAL/SUBTOTAL del conjunto analítico y conservarlas en cuarentena. | 1,113 | 1,112 |
| Hoja 2024: formatos de fecha mixtos | Interpretar formatos mixtos y llevar la fecha al primer día del mes; fechas inválidas a cuarentena. | 1,112 | 1,112 |
| Hoja 2024: nombres de municipio vacíos o mal escritos | Normalizar tildes y alias; resolver el nombre canónico con el código DIVIPOLA de Antioquia. | 1,112 | 1,112 |
| Hoja 2024: unidades de energía faltantes o no reconocidas | Convertir MWh a kWh y conservar kWh; las demás unidades se envían a cuarentena. | 1,112 | 1,112 |
| Hoja 2024: valores vacíos o no numéricos | Exigir energía, valor facturado y cantidad de clientes; no reemplazar nulos por cero. | 1,112 | 1,094 |
| Hoja 2024: medidas negativas | Enviar energía, valor o clientes negativos a cuarentena. | 1,112 | 1,109 |
| Hoja 2024: municipios sin código oficial | Unir por nombre normalizado al catálogo DIVIPOLA; no inventar códigos para los no resueltos. | 1,112 | 1,112 |
| Hoja 2025: encabezados en posiciones distintas | Buscar la fila de encabezado por nombres de columnas, no por una posición fija. | 1,117 | 1,113 |
| Hoja 2025: filas de totales mezcladas con observaciones | Excluir las filas TOTAL/SUBTOTAL del conjunto analítico y conservarlas en cuarentena. | 1,113 | 1,112 |
| Hoja 2025: formatos de fecha mixtos | Interpretar formatos mixtos y llevar la fecha al primer día del mes; fechas inválidas a cuarentena. | 1,112 | 1,112 |
| Hoja 2025: nombres de municipio vacíos o mal escritos | Normalizar tildes y alias; resolver el nombre canónico con el código DIVIPOLA de Antioquia. | 1,112 | 1,112 |
| Hoja 2025: valores vacíos o no numéricos | Exigir energía, valor facturado y cantidad de clientes; no reemplazar nulos por cero. | 1,112 | 1,102 |
| Hoja 2025: medidas negativas | Enviar energía, valor o clientes negativos a cuarentena. | 1,112 | 1,108 |
| Hoja 2025: municipios sin código oficial | Unir por nombre normalizado al catálogo DIVIPOLA; no inventar códigos para los no resueltos. | 1,112 | 1,112 |
| Hoja 2026: encabezados en posiciones distintas | Buscar la fila de encabezado por nombres de columnas, no por una posición fija. | 839 | 835 |
| Hoja 2026: filas de totales mezcladas con observaciones | Excluir las filas TOTAL/SUBTOTAL del conjunto analítico y conservarlas en cuarentena. | 835 | 834 |
| Hoja 2026: formatos de fecha mixtos | Interpretar formatos mixtos y llevar la fecha al primer día del mes; fechas inválidas a cuarentena. | 834 | 834 |
| Hoja 2026: nombres de municipio vacíos o mal escritos | Normalizar tildes y alias; resolver el nombre canónico con el código DIVIPOLA de Antioquia. | 834 | 834 |
| Hoja 2026: valores vacíos o no numéricos | Exigir energía, valor facturado y cantidad de clientes; no reemplazar nulos por cero. | 834 | 822 |
| Hoja 2026: medidas negativas | Enviar energía, valor o clientes negativos a cuarentena. | 834 | 830 |
| Hoja 2026: municipios sin código oficial | Unir por nombre normalizado al catálogo DIVIPOLA; no inventar códigos para los no resueltos. | 834 | 834 |
| Filas exactamente duplicadas | Conservar una copia de cada duplicado exacto en cuarentena y mantener una sola en Plata. | 4,096 | 3,979 |
| Más de una fila válida para el mismo grano mensual | Consolidar sumando medidas por mes, municipio DIVIPOLA, segmento y modalidad. | 3,979 | 3,979 |

### ideam_precipitacion_diaria

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| Estación, fecha, medición o asociación municipal inválida | Estandarizar tipos, validar coordenadas y asociar el municipio al código DIVIPOLA. | 29,804 | 29,804 |
| Clave estación-fecha duplicada | Mantener una fila por estación y día; duplicados a cuarentena. | 29,804 | 29,804 |

### ideam_temperatura_diaria

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| Estación, fecha, medición o asociación municipal inválida | Estandarizar tipos, validar coordenadas y asociar el municipio al código DIVIPOLA. | 17,349 | 17,349 |
| Clave estación-fecha duplicada | Mantener una fila por estación y día; duplicados a cuarentena. | 17,349 | 17,349 |

### noaa_oni

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| Trimestre móvil, año u ONI inválido | Mapear los 12 trimestres al mes central y convertir año/ONI a tipos numéricos. | 920 | 920 |
| Mes central ONI duplicado | Conservar una observación ONI por mes central. | 920 | 920 |
| Fase ENSO no clasificada | Clasificar ONI ≥ 0,5 como El Niño, ≤ -0,5 como La Niña y el resto como Neutral. | 920 | 920 |

### xm_aportes_hidricos

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| Fecha y medida diaria inválidas | Convertir la fecha y Validar aporte hídrico numérico y no negativo. | 1,004 | 1,004 |
| Filas diarias con fecha duplicada | Conservar una fila por fecha y guardar duplicados en cuarentena. | 1,004 | 1,004 |

### xm_demanda

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| 24 columnas Hour01–Hour24 en formato ancho | Despivotar las 24 horas a una fila por fecha y hora. | 1,004 | 24,096 |
| Hora comercial ausente o fuera del rango 1–24 | Asignar las horas del nombre de columna Hour01–Hour24. | 24,096 | 24,096 |
| Fechas, claves o medidas faltantes/no numéricas/fuera de rango | Conservar observaciones válidas y llevar cada rechazo a cuarentena con causa. | 24,096 | 24,096 |
| Claves fecha-hora-recurso duplicadas | Mantener una observación por el grano horario de la métrica y guardar repeticiones en cuarentena. | 24,096 | 24,096 |

### xm_embalses

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| Fecha y medida diaria inválidas | Convertir la fecha y Validar porcentaje de embalses entre 0–100; aportes hídricos no negativos. | 1,004 | 1,004 |
| Filas diarias con fecha duplicada | Conservar una fila por fecha y guardar duplicados en cuarentena. | 1,004 | 1,004 |

### xm_generacion_recurso

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| 24 columnas Hour01–Hour24 en formato ancho | Despivotar las 24 horas a una fila por fecha y hora. | 350,361 | 8,408,664 |
| Hora comercial ausente o fuera del rango 1–24 | Asignar las horas del nombre de columna Hour01–Hour24. | 8,408,664 | 8,408,664 |
| Fechas, claves o medidas faltantes/no numéricas/fuera de rango | Conservar observaciones válidas y llevar cada rechazo a cuarentena con causa. | 8,408,664 | 5,935,449 |
| Claves fecha-hora-recurso duplicadas | Mantener una observación por el grano horario de la métrica y guardar repeticiones en cuarentena. | 5,935,449 | 5,935,449 |

### xm_listado_recursos

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| Código o nombre del recurso vacío | Exigir código y nombre de planta/recurso; registros incompletos a cuarentena. | 2,493 | 2,493 |
| Código de recurso repetido | Publicar una fila por código XM y guardar duplicados en cuarentena. | 2,493 | 2,491 |

### xm_precio_bolsa

| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |
|---|---|---:|---:|
| 24 columnas Hour01–Hour24 en formato ancho | Despivotar las 24 horas a una fila por fecha y hora. | 1,004 | 24,096 |
| Hora comercial ausente o fuera del rango 1–24 | Asignar las horas del nombre de columna Hour01–Hour24. | 24,096 | 24,096 |
| Fechas, claves o medidas faltantes/no numéricas/fuera de rango | Conservar observaciones válidas y llevar cada rechazo a cuarentena con causa. | 24,096 | 24,096 |
| Claves fecha-hora-recurso duplicadas | Mantener una observación por el grano horario de la métrica y guardar repeticiones en cuarentena. | 24,096 | 24,096 |

## Cuarentena: cantidad y motivo

Las filas no corregibles se conservan en Parquet con su razón de rechazo. Los motivos y cantidades de esta tabla se agrupan directamente desde esas filas.

| Fuente | Motivo | Filas en cuarentena |
|---|---|---:|
| enerandes | Energía no numérica o vacía | 27 |
| enerandes | Fila de encabezado | 4 |
| enerandes | Fila de total o subtotal | 4 |
| enerandes | Medida negativa | 18 |
| enerandes | Registro exactamente duplicado | 117 |
| enerandes | Título o nota anterior a los encabezados | 6 |
| enerandes | Valor facturado no numérico o vacío | 29 |
| xm_generacion_recurso | Valor horario nulo o no numérico | 2,473,215 |
| xm_listado_recursos | Código de recurso duplicado | 2 |
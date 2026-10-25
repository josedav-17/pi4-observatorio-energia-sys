# Perfilamiento de datos de bronce

Perfil calculado sobre los archivos Parquet generados por `python -m src.pipeline`. Las columnas de linaje (`_fuente`, `_origen`, `_extraido_en`) se incluyen porque hacen parte de la capa bronce. Los porcentajes de nulos usan el total de filas de cada archivo; filas duplicadas significa duplicado exacto en todas las columnas.

## Resumen por archivo

| Archivo | Filas | Columnas | Filas duplicadas | Rango de fechas |
|---|---:|---:|---:|---|
| `enerandes_ventas_2023.parquet` | 1,114 | 10 | 32 | 2023-01-01 a 2023-12-01 |
| `enerandes_ventas_2024.parquet` | 1,114 | 11 | 32 | 2024-01-01 a 2024-12-01 |
| `enerandes_ventas_2025.parquet` | 1,117 | 10 | 32 | 2025-01-01 a 2025-12-01 |
| `enerandes_ventas_2026.parquet` | 839 | 10 | 24 | 2026-01-01 a 2026-09-01 |
| `ideam_precipitacion_diaria.parquet` | 29,804 | 11 | 0 | 2025-01-01 a 2026-07-24 |
| `ideam_temperatura_diaria.parquet` | 17,349 | 14 | 0 | 2025-01-01 a 2026-07-24 |
| `noaa_oni.parquet` | 920 | 7 | 0 | 1950 a 2026 (columna YR) |
| `xm_aportes_hidricos.parquet` | 1,004 | 6 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_demanda.parquet` | 1,004 | 30 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_embalses.parquet` | 1,004 | 6 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_generacion_recurso.parquet` | 350,361 | 30 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_listado_recursos.parquet` | 2,493 | 14 | 2 | 2026-10-24 a 2026-10-24 |
| `xm_precio_bolsa.parquet` | 1,004 | 30 | 0 | 2024-01-01 a 2026-09-30 |

## `enerandes_ventas_2023.parquet`

- Filas: **1,114**; columnas: **10**; filas duplicadas exactas: **32**.
- Rango de fechas: **2023-01-01 a 2023-12-01**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `col_0` | `str` | 0.00% |
| `col_1` | `str` | 0.09% |
| `col_2` | `str` | 1.44% |
| `col_3` | `str` | 0.09% |
| `col_4` | `str` | 0.90% |
| `col_5` | `str` | 0.72% |
| `col_6` | `str` | 0.09% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `enerandes_ventas_2024.parquet`

- Filas: **1,114**; columnas: **11**; filas duplicadas exactas: **32**.
- Rango de fechas: **2024-01-01 a 2024-12-01**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `col_0` | `str` | 0.00% |
| `col_1` | `str` | 0.09% |
| `col_2` | `str` | 0.36% |
| `col_3` | `str` | 0.09% |
| `col_4` | `str` | 0.72% |
| `col_5` | `str` | 0.09% |
| `col_6` | `str` | 1.08% |
| `col_7` | `str` | 0.09% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `enerandes_ventas_2025.parquet`

- Filas: **1,117**; columnas: **10**; filas duplicadas exactas: **32**.
- Rango de fechas: **2025-01-01 a 2025-12-01**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `col_0` | `str` | 0.09% |
| `col_1` | `str` | 0.36% |
| `col_2` | `str` | 0.90% |
| `col_3` | `str` | 0.36% |
| `col_4` | `str` | 0.90% |
| `col_5` | `str` | 0.72% |
| `col_6` | `str` | 0.36% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `enerandes_ventas_2026.parquet`

- Filas: **839**; columnas: **10**; filas duplicadas exactas: **24**.
- Rango de fechas: **2026-01-01 a 2026-09-01**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `col_0` | `str` | 0.12% |
| `col_1` | `str` | 0.48% |
| `col_2` | `str` | 1.07% |
| `col_3` | `str` | 0.48% |
| `col_4` | `str` | 1.07% |
| `col_5` | `str` | 1.31% |
| `col_6` | `str` | 0.48% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `ideam_precipitacion_diaria.parquet`

- Filas: **29,804**; columnas: **11**; filas duplicadas exactas: **0**.
- Rango de fechas: **2025-01-01 a 2026-07-24**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `codigoestacion` | `str` | 0.00% |
| `nombreestacion` | `str` | 0.00% |
| `municipio` | `str` | 0.00% |
| `latitud` | `str` | 0.00% |
| `longitud` | `str` | 0.00% |
| `fecha` | `str` | 0.00% |
| `precipitacion_mm` | `str` | 0.00% |
| `n_obs` | `str` | 0.00% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `ideam_temperatura_diaria.parquet`

- Filas: **17,349**; columnas: **14**; filas duplicadas exactas: **0**.
- Rango de fechas: **2025-01-01 a 2026-07-24**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `codigoestacion` | `str` | 0.00% |
| `nombreestacion` | `str` | 0.00% |
| `departamento` | `str` | 0.00% |
| `municipio` | `str` | 0.00% |
| `latitud` | `str` | 0.00% |
| `longitud` | `str` | 0.00% |
| `fecha` | `str` | 0.00% |
| `temperatura_media_c` | `str` | 0.00% |
| `temperatura_minima_c` | `str` | 0.00% |
| `temperatura_maxima_c` | `str` | 0.00% |
| `n_obs` | `str` | 0.00% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `noaa_oni.parquet`

- Filas: **920**; columnas: **7**; filas duplicadas exactas: **0**.
- Rango de fechas: **1950 a 2026 (columna YR)**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `SEAS` | `str` | 0.00% |
| `YR` | `str` | 0.00% |
| `TOTAL` | `str` | 0.00% |
| `ANOM` | `str` | 0.00% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `xm_aportes_hidricos.parquet`

- Filas: **1,004**; columnas: **6**; filas duplicadas exactas: **0**.
- Rango de fechas: **2024-01-01 a 2026-09-30**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `Date` | `str` | 0.00% |
| `Id` | `str` | 0.00% |
| `Value` | `str` | 0.00% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `xm_demanda.parquet`

- Filas: **1,004**; columnas: **30**; filas duplicadas exactas: **0**.
- Rango de fechas: **2024-01-01 a 2026-09-30**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `Date` | `str` | 0.00% |
| `Id` | `str` | 0.00% |
| `code` | `str` | 0.00% |
| `Hour01` | `str` | 0.00% |
| `Hour02` | `str` | 0.00% |
| `Hour03` | `str` | 0.00% |
| `Hour04` | `str` | 0.00% |
| `Hour05` | `str` | 0.00% |
| `Hour06` | `str` | 0.00% |
| `Hour07` | `str` | 0.00% |
| `Hour08` | `str` | 0.00% |
| `Hour09` | `str` | 0.00% |
| `Hour10` | `str` | 0.00% |
| `Hour11` | `str` | 0.00% |
| `Hour12` | `str` | 0.00% |
| `Hour13` | `str` | 0.00% |
| `Hour14` | `str` | 0.00% |
| `Hour15` | `str` | 0.00% |
| `Hour16` | `str` | 0.00% |
| `Hour17` | `str` | 0.00% |
| `Hour18` | `str` | 0.00% |
| `Hour19` | `str` | 0.00% |
| `Hour20` | `str` | 0.00% |
| `Hour21` | `str` | 0.00% |
| `Hour22` | `str` | 0.00% |
| `Hour23` | `str` | 0.00% |
| `Hour24` | `str` | 0.00% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `xm_embalses.parquet`

- Filas: **1,004**; columnas: **6**; filas duplicadas exactas: **0**.
- Rango de fechas: **2024-01-01 a 2026-09-30**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `Date` | `str` | 0.00% |
| `Id` | `str` | 0.00% |
| `Value` | `str` | 0.00% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `xm_generacion_recurso.parquet`

- Filas: **350,361**; columnas: **30**; filas duplicadas exactas: **0**.
- Rango de fechas: **2024-01-01 a 2026-09-30**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `Date` | `str` | 0.00% |
| `Id` | `str` | 0.00% |
| `code` | `str` | 0.00% |
| `Hour01` | `str` | 0.00% |
| `Hour02` | `str` | 0.00% |
| `Hour03` | `str` | 0.00% |
| `Hour04` | `str` | 0.00% |
| `Hour05` | `str` | 0.00% |
| `Hour06` | `str` | 0.00% |
| `Hour07` | `str` | 0.00% |
| `Hour08` | `str` | 0.00% |
| `Hour09` | `str` | 0.00% |
| `Hour10` | `str` | 0.00% |
| `Hour11` | `str` | 0.00% |
| `Hour12` | `str` | 0.00% |
| `Hour13` | `str` | 0.00% |
| `Hour14` | `str` | 0.00% |
| `Hour15` | `str` | 0.00% |
| `Hour16` | `str` | 0.00% |
| `Hour17` | `str` | 0.00% |
| `Hour18` | `str` | 0.00% |
| `Hour19` | `str` | 0.00% |
| `Hour20` | `str` | 0.00% |
| `Hour21` | `str` | 0.00% |
| `Hour22` | `str` | 0.00% |
| `Hour23` | `str` | 0.00% |
| `Hour24` | `str` | 0.00% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `xm_listado_recursos.parquet`

- Filas: **2,493**; columnas: **14**; filas duplicadas exactas: **2**.
- Rango de fechas: **2026-10-24 a 2026-10-24**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `Date` | `str` | 0.00% |
| `Id` | `str` | 0.00% |
| `Code` | `str` | 0.00% |
| `Name` | `str` | 0.00% |
| `Type` | `str` | 0.00% |
| `Disp` | `str` | 0.00% |
| `RecType` | `str` | 0.00% |
| `CompanyCode` | `str` | 0.00% |
| `EnerSource` | `str` | 0.00% |
| `OperStartdate` | `str` | 0.00% |
| `State` | `str` | 0.00% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## `xm_precio_bolsa.parquet`

- Filas: **1,004**; columnas: **30**; filas duplicadas exactas: **0**.
- Rango de fechas: **2024-01-01 a 2026-09-30**.

| Columna | Tipo de dato | Nulos |
|---|---|---:|
| `Date` | `str` | 0.00% |
| `Id` | `str` | 0.00% |
| `code` | `str` | 0.00% |
| `Hour01` | `str` | 0.00% |
| `Hour02` | `str` | 0.00% |
| `Hour03` | `str` | 0.00% |
| `Hour04` | `str` | 0.00% |
| `Hour05` | `str` | 0.00% |
| `Hour06` | `str` | 0.00% |
| `Hour07` | `str` | 0.00% |
| `Hour08` | `str` | 0.00% |
| `Hour09` | `str` | 0.00% |
| `Hour10` | `str` | 0.00% |
| `Hour11` | `str` | 0.00% |
| `Hour12` | `str` | 0.00% |
| `Hour13` | `str` | 0.00% |
| `Hour14` | `str` | 0.00% |
| `Hour15` | `str` | 0.00% |
| `Hour16` | `str` | 0.00% |
| `Hour17` | `str` | 0.00% |
| `Hour18` | `str` | 0.00% |
| `Hour19` | `str` | 0.00% |
| `Hour20` | `str` | 0.00% |
| `Hour21` | `str` | 0.00% |
| `Hour22` | `str` | 0.00% |
| `Hour23` | `str` | 0.00% |
| `Hour24` | `str` | 0.00% |
| `_fuente` | `str` | 0.00% |
| `_origen` | `str` | 0.00% |
| `_extraido_en` | `str` | 0.00% |

## Hallazgos de calidad

1. **Filas duplicadas en EnerAndes.** Se detectaron 32 filas duplicadas exactas en `enerandes_ventas_2023`, 32 en `enerandes_ventas_2024`, 32 en `enerandes_ventas_2025` y 24 en `enerandes_ventas_2026`; deben revisarse antes de agregarlas para evitar doble conteo.
2. **Formato de periodo inconsistente en EnerAndes 2024.** La primera columna mezcla, entre otros, `jun-24`, `09/2024` y `2024-07`; las cuatro hojas conservan los valores originales como texto, por lo que la capa plata debe normalizar el periodo antes de unirlas.
3. **Metadatos previos a las filas de ventas.** Las hojas de 2025 y 2026 comienzan con titulos y notas de fuente antes del encabezado. En ambas, las tres primeras filas no son observaciones de venta y deben excluirse durante la limpieza, no en bronce.
4. **Vacios temporales en precipitacion IDEAM.** La extraccion devolvio 0 filas en cada una de las ventanas 2025-02-05 a 2025-02-11, 2025-02-12 a 2025-02-18 y 2025-02-19 a 2025-02-25 (21 dias consecutivos sin registros para Antioquia).
5. **Duplicados en el catalogo de recursos XM.** `xm_listado_recursos.parquet` contiene 2 filas duplicadas exactas de 2,493 (0.08%); revisar su clave de recurso antes de usar el catalogo como dimension.

## Nota de interpretacion

Los archivos de EnerAndes, NOAA y XM se guardan en bronce tal como llegan, sin corregir duplicados, encabezados ni tipos. Los hallazgos son alertas para las capas posteriores; la agregacion de IDEAM se realiza en el servidor mediante SoQL.

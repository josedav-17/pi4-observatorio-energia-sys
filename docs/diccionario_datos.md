# Perfilamiento de datos — Capa Bronce

Resultados obtenidos sobre los archivos Parquet generados por `python -m src.pipeline`. Todos los campos se almacenan como texto (`str`) junto con las columnas de trazabilidad (`_fuente`, `_origen`, `_extraido_en`). Los porcentajes de nulos se calculan sobre el total de filas de cada archivo y los duplicados corresponden a filas exactamente iguales en todas sus columnas.

## Resumen general

| Archivo | Filas | Columnas | Duplicados | Rango de fechas |
|---|---:|---:|---:|---|
| `enerandes_ventas_2023.parquet` | 1,114 | 10 | 32 | 2023-01-01 a 2023-12-01 |
| `enerandes_ventas_2024.parquet` | 1,114 | 11 | 32 | 2024-01-01 a 2024-12-01 |
| `enerandes_ventas_2025.parquet` | 1,117 | 10 | 32 | 2025-01-01 a 2025-12-01 |
| `enerandes_ventas_2026.parquet` | 839 | 10 | 24 | 2026-01-01 a 2026-09-01 |
| `ideam_precipitacion_diaria.parquet` | 29,804 | 11 | 0 | 2025-01-01 a 2026-07-24 |
| `ideam_temperatura_diaria.parquet` | 17,349 | 14 | 0 | 2025-01-01 a 2026-07-24 |
| `noaa_oni.parquet` | 920 | 7 | 0 | 1950 a 2026 (columna `YR`) |
| `xm_aportes_hidricos.parquet` | 1,004 | 6 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_demanda.parquet` | 1,004 | 30 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_embalses.parquet` | 1,004 | 6 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_generacion_recurso.parquet` | 350,361 | 30 | 0 | 2024-01-01 a 2026-09-30 |
| `xm_listado_recursos.parquet` | 2,493 | 14 | 2 | 2026-10-24 a 2026-10-24 |
| `xm_precio_bolsa.parquet` | 1,004 | 30 | 0 | 2024-01-01 a 2026-09-30 |

## Detalle por fuente

### `enerandes_ventas_2023.parquet`
* **Registros:** 1,114 filas | 10 columnas | 32 duplicados exactos.
* **Periodo:** 2023-01-01 a 2023-12-01.

| Columna | Tipo | Nulos |
|---|---|---:|
| `col_0` | `str` | 0.00% |
| `col_1` | `str` | 0.09% |
| `col_2` | `str` | 1.44% |
| `col_3` | `str` | 0.09% |
| `col_4` | `str` | 0.90% |
| `col_5` | `str` | 0.72% |
| `col_6` | `str` | 0.09% |
| `_fuente`, `_origen`, `_extraido_en` | `str` | 0.00% |

### `enerandes_ventas_2024.parquet`
* **Registros:** 1,114 filas | 11 columnas | 32 duplicados exactos.
* **Periodo:** 2024-01-01 a 2024-12-01.

| Columna | Tipo | Nulos |
|---|---|---:|
| `col_0` | `str` | 0.00% |
| `col_1` | `str` | 0.09% |
| `col_2` | `str` | 0.36% |
| `col_3` | `str` | 0.09% |
| `col_4` | `str` | 0.72% |
| `col_5` | `str` | 0.09% |
| `col_6` | `str` | 1.08% |
| `col_7` | `str` | 0.09% |
| `_fuente`, `_origen`, `_extraido_en` | `str` | 0.00% |

### `enerandes_ventas_2025.parquet`
* **Registros:** 1,117 filas | 10 columnas | 32 duplicados exactos.
* **Periodo:** 2025-01-01 a 2025-12-01.

| Columna | Tipo | Nulos |
|---|---|---:|
| `col_0` | `str` | 0.09% |
| `col_1` | `str` | 0.36% |
| `col_2` | `str` | 0.90% |
| `col_3` | `str` | 0.36% |
| `col_4` | `str` | 0.90% |
| `col_5` | `str` | 0.72% |
| `col_6` | `str` | 0.36% |
| `_fuente`, `_origen`, `_extraido_en` | `str` | 0.00% |

### `enerandes_ventas_2026.parquet`
* **Registros:** 839 filas | 10 columnas | 24 duplicados exactos.
* **Periodo:** 2026-01-01 a 2026-09-01.

| Columna | Tipo | Nulos |
|---|---|---:|
| `col_0` | `str` | 0.12% |
| `col_1` | `str` | 0.48% |
| `col_2` | `str` | 1.07% |
| `col_3` | `str` | 0.48% |
| `col_4` | `str` | 1.07% |
| `col_5` | `str` | 1.31% |
| `col_6` | `str` | 0.48% |
| `_fuente`, `_origen`, `_extraido_en` | `str` | 0.00% |

### `ideam_precipitacion_diaria.parquet`
* **Registros:** 29,804 filas | 11 columnas | 0 duplicados.
* **Periodo:** 2025-01-01 a 2026-07-24.
* **Columnas (`0.00%` nulos, todas `str`):** `codigoestacion`, `nombreestacion`, `municipio`, `latitud`, `longitud`, `fecha`, `precipitacion_mm`, `n_obs`, `_fuente`, `_origen`, `_extraido_en`.

### `ideam_temperatura_diaria.parquet`
* **Registros:** 17,349 filas | 14 columnas | 0 duplicados.
* **Periodo:** 2025-01-01 a 2026-07-24.
* **Columnas (`0.00%` nulos, todas `str`):** `codigoestacion`, `nombreestacion`, `departamento`, `municipio`, `latitud`, `longitud`, `fecha`, `temperatura_media_c`, `temperatura_minima_c`, `temperatura_maxima_c`, `n_obs`, `_fuente`, `_origen`, `_extraido_en`.

### `noaa_oni.parquet`
* **Registros:** 920 filas | 7 columnas | 0 duplicados.
* **Periodo:** 1950 a 2026 (columna `YR`).
* **Columnas (`0.00%` nulos, todas `str`):** `SEAS`, `YR`, `TOTAL`, `ANOM`, `_fuente`, `_origen`, `_extraido_en`.

### Series horarias XM (`xm_demanda`, `xm_precio_bolsa`, `xm_generacion_recurso`)
* **Registros:** 1,004 filas en demanda y precio de bolsa; 350,361 filas en generación por recurso | 30 columnas | 0 duplicados.
* **Periodo:** 2024-01-01 a 2026-09-30.
* **Columnas (`0.00%` nulos, todas `str`):** `Date`, `Id`, `code`, `Hour01` a `Hour24`, `_fuente`, `_origen`, `_extraido_en`.

### Series diarias y catálogo XM (`xm_aportes_hidricos`, `xm_embalses`, `xm_listado_recursos`)
* **Aportes hídricos y embalses:** 1,004 filas | 6 columnas (`Date`, `Id`, `Value`, `_fuente`, `_origen`, `_extraido_en`) | `0.00%` nulos | 0 duplicados | 2024-01-01 a 2026-09-30.
* **Listado de recursos:** 2,493 filas | 14 columnas (`Date`, `Id`, `Code`, `Name`, `Type`, `Disp`, `RecType`, `CompanyCode`, `EnerSource`, `OperStartdate`, `State`, `_fuente`, `_origen`, `_extraido_en`) | `0.00%` nulos | 2 duplicados exactos | corte 2026-10-24.

## Hallazgos y alertas para la capa Plata

1. **Duplicados en EnerAndes:** Hay 32 filas repetidas en cada hoja de 2023 a 2025 y 24 en 2026. Deben deduplicarse antes de consolidar para no inflar las métricas de ventas.
2. **Fechas mezcladas en EnerAndes 2024:** La columna de periodo combina formatos como `jun-24`, `09/2024` y `2024-07`. Como en bronce todo se guarda como texto crudo, Plata debe unificar estas fechas al primer día del mes.
3. **Filas de encabezado y notas en EnerAndes 2025–2026:** Ambas hojas arrancan con títulos y notas de fuente antes de la tabla real (las primeras 3 filas no son registros de venta) y contienen filas de totales al final que deben enviarse a cuarentena.
4. **Brecha temporal en precipitación IDEAM:** La consulta a datos.gov.co devolvió 0 registros para Antioquia durante 21 días seguidos (entre el 5 y el 25 de febrero de 2025).
5. **Duplicados en catálogo XM:** `xm_listado_recursos.parquet` trae 2 registros exactamente repetidos sobre 2,493 (0.08%), por lo que requiere limpieza por `Code` antes de alimentar `dim_recurso`.
# Consultas de negocio en Oro

Ejecutar desde la raíz después de `python -m src.transformar`. Los tres SQL están en esta
carpeta y consultan los modelos dbt construidos en DuckDB.

## Consultas y resultados

Resultados de la corrida local con los Parquet disponibles (se regeneran al actualizar
fuentes):

1. `01_ventas_mensuales_por_municipio.sql` — top 20 combinaciones mes/municipio por energía.
   **Resultado:** Medellín, agosto de 2026, lidera con 30.982.163 kWh; le siguen
   junio de 2026 (30.869.312 kWh) y julio de 2026 (30.317.940 kWh).
   Se devuelven 20 grupos mensuales.
2. `02_precio_demanda_por_hora.sql` — promedio de precio y demanda por hora (24 filas).
   **Resultado:** las 24 horas tienen 1.004 observaciones cada una; la hora 1 presenta
   precio promedio de 420,37 COP/kWh y demanda promedio de 8.712.276,21 kWh.
3. `03_generacion_por_fuente_energia.sql` — generación anual por fuente energética.
   **Resultado:** en 2024, AGUA aporta la generación agregada más alta
   (54.494.304.158,49 kWh), seguida de GAS (12.620.635.725,43 kWh) y CARBON
   (9.473.290.904,59 kWh). Los valores se consultan por año y fuente.

Las salidas reproducibles se consultan en `data/gold/observatorio.duckdb`.

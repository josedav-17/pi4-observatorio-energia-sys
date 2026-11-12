# Consultas de negocio en Oro

Ejecutar desde la raíz después de `python -m src.transformar`. Los tres SQL están en esta
carpeta y consultan los modelos dbt construidos en DuckDB.

## Consultas y resultados

Los resultados cambian al actualizar las fuentes. Para no documentar cifras ficticias,
el resumen se debe completar con la salida real tras la corrida final:

1. `01_ventas_mensuales_por_municipio.sql` — top 20 combinaciones mes/municipio por energía.
   **Resultado de la corrida:** pendiente de ejecutar con el conjunto Plata definitivo.
2. `02_precio_demanda_por_hora.sql` — promedio de precio y demanda por hora (24 filas).
   **Resultado de la corrida:** pendiente de ejecutar con el conjunto Plata definitivo.
3. `03_generacion_por_fuente_energia.sql` — generación anual por fuente energética.
   **Resultado de la corrida:** pendiente de ejecutar con el conjunto Plata definitivo.

Las salidas reproducibles se consultan en `data/gold/observatorio.duckdb`.

# Reporte de calidad de datos — EA2

Este archivo se genera en cada ejecución de `python -m src.transformar`; las cifras se
calculan desde Parquet de bronce y plata. Ejecutar el orquestador para ver métricas
antes/después y cuantificación real de cuarentena. No consignar métricas estimadas.

## Reglas aplicadas

1. Detección dinámica de encabezados EnerAndes en cada hoja.
2. Normalización YYYY-MM, mar-YY, MM/YYYY y DD/MM/YYYY al primer día del mes.
3. Conversión MWh a kWh para energía con esa unidad (hoja 2024).
4. Normalización de municipios y corrección de alias frecuentes.
5. Energía y valor de ventas no negativos; inválidos a cuarentena.
6. Ventas únicas por fecha, municipio, segmento y tipo de compra.
7. Unpivot de Hour01–Hour24 en observaciones fecha/hora.
8. Hora comercial dentro de 1–24.
9. Precio de bolsa en rango físico/operativo configurado.
10. Demanda y generación numéricas y no negativas.
11. Embalses expresados entre 0 y 100 por ciento.
12. Aportes hídricos no negativos.
13. Catálogo de recursos con código y nombre no vacíos y código único.
14. IDEAM con código estación, fecha, municipio y coordenadas asociables.
15. Precipitación no negativa.
16. Temperaturas numéricas con mínima menor o igual a máxima.
17. NOAA con temporada móvil válida; DJF→enero, JFM→febrero y así sucesivamente.
18. Fase NOAA: ONI ≥ 0,5 El Niño; ONI ≤ -0,5 La Niña; demás Neutral.
19. DIVIPOLA con código municipal único y coordenadas numéricas.
20. Pandera valida schema, tipos, rangos y llaves antes de escribir cada tabla.

## Métricas

| Fuente | Filas antes | Filas Plata | Cuarentena |
|---|---:|---:|---:|
| Pendiente | Ejecutar `python -m src.transformar` | — | — |

Los datos concretos se escriben en esta tabla por el proceso de limpieza; si la
ejecución falla, no se deben tratar estos valores como una corrida exitosa.

## Justificación de cuarentena

Las filas no corregibles se conservan en `data/silver/cuarentena_<fuente>.parquet`,
con columna `motivo`. Casos típicos: notas/totales sin observación fechada, fechas no
interpretables, claves vacías, cifras no numéricas o negativas, medidas fuera de
rango y duplicados. Revisar la regla y el dato de origen antes de corregir o excluir.

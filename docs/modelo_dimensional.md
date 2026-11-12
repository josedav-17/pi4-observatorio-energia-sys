# Modelo dimensional de la capa Oro

## Esquema estrella

```mermaid
erDiagram
    DIM_FECHA ||--o{ FACT_VENTAS_MENSUAL : fecha_key
    DIM_MUNICIPIO ||--o{ FACT_VENTAS_MENSUAL : municipio_key
    DIM_FECHA ||--o{ FACT_MERCADO_HORARIO : fecha_key
    DIM_FECHA ||--o{ FACT_GENERACION_RECURSO : fecha_key
    DIM_RECURSO ||--o{ FACT_GENERACION_RECURSO : recurso_key
    DIM_FECHA {
        int fecha_key PK
        date fecha
        int anio
        int mes
        int trimestre
        int dia_semana
        string fase_enso
    }
    DIM_MUNICIPIO {
        string codigo_municipio PK
        string municipio
        string codigo_departamento
        boolean es_divipola
    }
    DIM_RECURSO {
        string codigo_recurso PK
        string recurso
        string tipo_recurso
        string fuente_energia
    }
    DIM_ESTACION {
        string codigo_estacion PK
        string estacion
        string municipio
    }
    DIM_ENSO {
        int enso_key PK
        date mes
        double oni
        string fase_enso
    }
    FACT_VENTAS_MENSUAL {
        int fecha_key FK
        string municipio_key FK
        string segmento
        string tipo_compra
        double energia_kwh
        double valor_cop
        int clientes
    }
    FACT_MERCADO_HORARIO {
        int fecha_key FK
        int hora
        double precio_cop_kwh
        double demanda_kwh
        double volumen_util_pct
        double aportes_mwh
        string fase_enso
    }
    FACT_GENERACION_RECURSO {
        int fecha_key FK
        int hora
        string recurso_key FK
        double generacion_kwh
    }
```

`dim_estacion` y `dim_enso` son dimensiones conformadas para consultas de clima y ENSO
(la medición diaria IDEAM y la serie mensual ONI quedan en Plata; no se inventa una
cuarta tabla de hechos de clima). Las pruebas de dbt verifican unicidad/no nulidad de
las claves dimensionales y relaciones de las claves foráneas declaradas.

## Grano de hechos

| Modelo | Grano | Medidas |
|---|---|---|
| `fact_ventas_mensual` | Mes, municipio, segmento y modalidad de compra EnerAndes | kWh vendidos, COP facturados y clientes |
| `fact_mercado_horario` | Fecha y hora del sistema eléctrico nacional | Precio, demanda, nivel de embalses y aportes |
| `fact_generacion_recurso` | Fecha, hora y recurso/planta XM | Generación kWh |

`fecha_key` usa `YYYYMMDD`; las fechas de venta representan el primer día del mes de
origen. `dim_fecha` cubre los días calendario de los años con ventas disponibles. El
mes central ONI (por ejemplo, DJF → enero) alimenta la fase ENSO de la dimensión fecha.
DIVIPOLA es la fuente externa municipal; los municipios de ventas no encontrados en
la referencia se mantienen identificados con `es_divipola = false` para no perder
ventas silenciosamente.

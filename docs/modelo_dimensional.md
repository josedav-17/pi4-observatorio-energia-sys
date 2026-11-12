# Modelo dimensional — Capa Oro

## Diagrama entidad-relación

# Claves de tiempo: fecha_key sigue el formato entero YYYYMMDD. Para las ventas mensuales se toma el primer día del mes (YYYYMM01). dim_fecha abarca todos los días calendario ## de los años con ventas registradas e incluye la fase ENSO correspondiente según el mes central del trimestre móvil ONI (ej. DJF → enero).

## Geografía: Se toma DIVIPOLA (filtrado a Antioquia) como tabla maestra de municipios. Tanto las ventas de EnerAndes como las estaciones del IDEAM cruzan contra este código oficial; los registros cuyo municipio no logra homologarse quedan en cuarentena en Plata y no pasan a Oro.

## Alcance de hechos: Las series climáticas diarias del IDEAM y el índice ONI mensual se mantienen en Plata y como dimensiones de apoyo (dim_estacion, dim_enso) sin forzar una ## tabla de hechos adicional.

## Pruebas: dbt valida unicidad, valores no nulos e integridad referencial en todas las llaves primarias y foráneas del modelo. -


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
        string codigo_municipio FK
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










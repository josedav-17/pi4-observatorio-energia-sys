# Observatorio de Energía y Clima

> Proyecto Integrado IV – Integración de Información · IU Digital de Antioquia · 2026-2

## 👥 Integrantes

| Nombre | Usuario GitHub | Rol |
|---|---|---|
| José David Cardona Mazo | `josedav17` | Líder técnico / Data Engineer |

## 🎯 Objetivo

Integrar datos del mercado eléctrico (XM), del clima (IDEAM y NOAA) y de ventas internas (EnerAndes) con la división político-administrativa oficial (DIVIPOLA) para analizar el comportamiento de ventas, precios, demanda y generación eléctrica ante el riesgo climático de El Niño 2026.

## 🏗️ Arquitectura y flujo del pipeline

```text
Fuentes (Excel / APIs REST / SoQL / TXT)
   │
   ▼  [python -m src.pipeline]
Capa Bronce (data/bronze/*.parquet) ──► Datos crudos + columnas de trazabilidad
   │
   ▼  [python -m src.transformar]
Capa Plata  (data/silver/*.parquet) ──► Limpieza, homologación DIVIPOLA, Pandera y cuarentena
   │
   ▼  [dbt build]
Capa Oro    (data/gold/observatorio.duckdb) ──► Modelo estrella (5 dimensiones, 3 hechos) ──► Dashboard
```

## 📦 Fuentes de datos

| Fuente | Tipo / Origen | Archivo en `data/bronze/` | Cobertura y granularidad |
|---|---|---|---|
| **XM – API Sinergox** | API REST (`POST`, JSON) | `xm_precio_bolsa`, `xm_demanda`, `xm_embalses`, `xm_generacion_recurso`, `xm_listado_recursos`, `xm_aportes_hidricos` | Horaria / Diaria (2024-01-01 a 2026-09-30) |
| **IDEAM – datos.gov.co** | API Socrata (`SoQL`) | `ideam_precipitacion_diaria`, `ideam_temperatura_diaria` | Diaria por estación en Antioquia (2025-01-01 a 2026-09-30) |
| **NOAA – Índice ONI** | Archivo de texto plano | `noaa_oni` | Trimestral móvil (1950 a 2026) |
| **EnerAndes** | Excel interno (`ventas_enerandes_2023_2026.xlsx`) | `enerandes_ventas_2023` … `enerandes_ventas_2026` | Mensual por municipio (2023–2026) |
| **DIVIPOLA – MinSalud** | Datos Abiertos (`pqwj-3fi4`) | `divipola_municipios` | Maestra oficial de municipios de Antioquia |

### Notas técnicas de extracción

* **Fuente externa propia (DIVIPOLA):** Incorporada desde [Datos Abiertos MinSalud](https://www.datos.gov.co/Salud-y-Protecci%C3%B3n-Social/MinSalud-Divipola-Municipios/pqwj-3fi4) para estandarizar códigos municipales de Antioquia (`05`). El extractor `src/extract/xm_aportes.py` (`AporEner`) consulta aportes hídricos como métrica complementaria de XM y no como fuente externa propia.
* **Agregación en servidor (IDEAM):** Las consultas se ejecutan en ventanas semanales filtradas para Antioquia y se agregan por día y estación mediante SoQL (`avg`, `min`, `max` sobre el dataset `sbwg-7ju4` para temperatura y suma diaria para precipitación).
* **Idempotencia y muestras:** `src.pipeline` omite archivos Parquet existentes; para volver a descargar todo se ejecuta `python -m src.pipeline --forzar`. Las muestras de las primeras 200 filas por tabla se exportan automáticamente a `data/sample/`.

## 📂 Estructura del repositorio

```text
├── consultas/
│   └── oro/                      # Consultas SQL de negocio sobre DuckDB
├── data/
│   ├── insumos/                  # Excel fuente de EnerAndes (manual)
│   ├── bronze/                   # Parquets crudos (generado localmente)
│   ├── silver/                   # Parquets limpios y cuarentena_*.parquet (generado localmente)
│   ├── gold/                     # Base analítica observatorio.duckdb (generado localmente)
│   └── sample/                   # Muestras CSV de las primeras 200 filas por fuente
├── dbt/                          # Modelos SQL dimensionales y pruebas de integridad
├── docs/
│   ├── bitacoras/                # Seguimiento individual del desarrollo
│   ├── diccionario_datos.md      # Definición de columnas y tipos en capa Oro
│   ├── modelo_dimensional.md     # Diagrama ER y granularidad de hechos/dimensiones
│   ├── perfilamiento_bronce.md   # Diagnóstico inicial de nulos, duplicados y brechas
│   └── reporte_calidad.md        # Métricas antes/después y motivos de cuarentena (autogenerado)
├── evidencias/                   # Capturas de ejecución y validación del entorno
├── src/
│   ├── extract/                  # Extractores independientes por fuente (xm, ideam, noaa, enerandes, divipola)
│   ├── quality/                  # Contratos de validación de esquemas en Pandera
│   ├── transform/                # Reglas de limpieza, normalización y envío a cuarentena
│   ├── config.py                 # Rutas, URLs, ventanas de extracción y parámetros globales
│   ├── consultar.py              # Ejecutor de consultas SQL sobre DuckDB
│   ├── pipeline.py               # Orquestador de extracción hacia capa Bronce
│   ├── transformar.py            # Orquestador de capa Plata, reporte de calidad y dbt build
│   └── utils.py                  # Cliente HTTP con reintentos, paginación por ventanas y persistencia
└── tests/                        # Pruebas unitarias (pytest)
```

## ⚙️ Requisitos e instalación

Requiere **Python 3.11 o superior**. En PowerShell, desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Antes de ejecutar la extracción, ubicar el insumo manual en `data/insumos/ventas_enerandes_2023_2026.xlsx`.

## 🚀 Ejecución del pipeline

```powershell
# 1. Extraer fuentes a capa Bronce y generar muestras CSV
python -m src.pipeline

# 2. Ejecutar limpieza Plata, validaciones Pandera, reporte de calidad y dbt build (Oro)
python -m src.transformar

# 3. Correr consultas SQL de negocio en DuckDB
python -m src.consultar

# 4. Ejecutar suite de pruebas unitarias
python -m pytest
```

> **Nota:** `src.transformar` descarga `divipola_municipios.parquet` desde Datos Abiertos si aún no existe en `data/bronze/`, valida cada tabla Plata con Pandera, guarda filas no corregibles en `data/silver/cuarentena_<fuente>.parquet`, actualiza `docs/reporte_calidad.md` y construye el modelo estrella en `data/gold/observatorio.duckdb`.

## 📊 Consultas de negocio (Capa Oro)

Las consultas SQL se encuentran en [`consultas/oro/`](consultas/oro/) y se ejecutan directamente sobre las tablas dimensionales en DuckDB. Resultados de referencia de la corrida local:

1. **Ventas mensuales por municipio** ([`01_ventas_mensuales_por_municipio.sql`](consultas/oro/01_ventas_mensuales_por_municipio.sql)): Medellín lidera la demanda mensual con `30.982.163 kWh` en agosto de 2026, seguido de junio (`30.869.312 kWh`) y julio (`30.317.940 kWh`).
2. **Precio y demanda por hora** ([`02_precio_demanda_por_hora.sql`](consultas/oro/02_precio_demanda_por_hora.sql)): La hora 1 promedia `420,37 COP/kWh` y `8.712.276,21 kWh` de demanda sobre `1.004` observaciones diarias.
3. **Generación por fuente energética** ([`03_generacion_por_fuente_energia.sql`](consultas/oro/03_generacion_por_fuente_energia.sql)): En 2024, la generación hidráulica (`AGUA`) suma `54.494.304.158,49 kWh`, seguida de `GAS` (`12.620.635.725,43 kWh`) y `CARBON` (`9.473.290.904,59 kWh`).

El detalle completo y el alcance de cada consulta están documentados en [`consultas/oro/README.md`](consultas/oro/README.md).

## 📚 Documentación y entregables

* **Modelo dimensional y granularidad:** [`docs/modelo_dimensional.md`](docs/modelo_dimensional.md) (`dim_fecha`, `dim_municipio`, `dim_recurso`, `dim_estacion`, `dim_enso`, `fact_ventas_mensual`, `fact_mercado_horario`, `fact_generacion_recurso`).
* **Diccionario de datos (Capa Oro):** [`docs/diccionario_datos.md`](docs/diccionario_datos.md).
* **Perfilamiento inicial (Capa Bronce):** [`docs/perfilamiento_bronce.md`](docs/perfilamiento_bronce.md).
* **Reporte de calidad y cuarentenas:** [`docs/reporte_calidad.md`](docs/reporte_calidad.md).
* **Bitácora individual:** [`docs/bitacoras/Cardona_Jose.md`](docs/bitacoras/Cardona_Jose.md).

### Archivos excluidos de Git

Por tamaño y reproducibilidad, se ignoran `.venv/`, `data/bronze/`, `data/silver/`, `data/gold/`, `*.duckdb`, `dbt/target/` y `dbt/logs/`. Todo el almacenamiento analítico se reconstruye localmente ejecutando los scripts del pipeline.

## 🤖 Uso de IA

Se utilizó Gemini como apoyo para estructurar la guía de evidencias relevantes del proyecto según los requerimientos de la entrega, con el fin de priorizar las capturas técnicas clave y mantener la documentación clara y concisa.

## 📸 Evidencias

![Evidencia 01 - Entorno](evidencias/evidencia_01_entorno.png)

![Evidencia 02 - Repositorio](evidencias/evidencia_02_repositorio.png)

![Evidencia 03 - Repositorio](evidencias/evidencia_03_repositorio.png)

![Evidencia 04 - Repositorio](evidencias/evidencia_04_repositorio.png)

![Evidencia 05 - Repositorio](evidencias/evidencia_05_repositorio.png)

![Evidencia 06 - Repositorio](evidencias/evidencia_06_repositorio.png)

![Evidencia 07 - Repositorio](evidencias/evidencia_07_repositorio.png)
# Observatorio Energía y Clima – Equipo <nombre>

> Proyecto Integrado IV – Integración de Información · IU Digital de Antioquia · 2026-2

## 👥 Integrantes

| Nombre | Usuario GitHub | Rol |
|---|---|---|
| José David Cardona Mazo| josedav17 | Líder técnico / Data Engineer |


## 🎯 Objetivo

Integrar datos del mercado eléctrico (XM), del clima (IDEAM y NOAA) y de ventas internas (EnerAndes) para analizar el riesgo energético de Colombia ante El Niño 2026.

## 📦 Fuentes de datos (capa bronce)

| Fuente | Tipo | Archivo en `data/bronze/` |
|---|---|---|
| XM – API Sinergox | API REST (POST, JSON) | Precio de bolsa, demanda, embalses, generacion por recurso, catalogo de recursos y aportes hidricos |
| IDEAM – datos.gov.co | API Socrata (SoQL) | Precipitacion y temperatura diaria por estacion |
| NOAA – índice ONI | Archivo de texto | `noaa_oni` |
| EnerAndes | Excel interno | `enerandes_ventas_2023` … `enerandes_ventas_2026` |

### Fuente XM adicional: aportes hídricos (no es fuente propia)

El extractor `src/extract/xm_aportes.py` consulta `AporEner` en el endpoint diario de la API Sinergox de XM (entidad `Sistema`). Es una fuente complementaria de XM y no se presenta como fuente propia. La fuente externa propia incorporada para EA2 es DIVIPOLA, publicada por MinSalud en Datos Abiertos.

IDEAM se consulta en ventanas semanales con filtros de Antioquia y fechas, y cada resultado se agrega por día y estación mediante SoQL en el servidor. Temperatura media, mínima y máxima se calculan sobre las observaciones del dataset `sbwg-7ju4`.

## ⚙️ Cómo ejecutar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# ubicar ventas_enerandes_2023_2026.xlsx en data/insumos/ (si se necesita extraer bronce)
python -m src.transformar     # una orden: Plata + Pandera + dbt build (Oro)
python -m src.pipeline          # descarga a data/bronze/ y crea muestras CSV
python -m src.consultar         # consultas SQL de BI con DuckDB
python -m pytest                # pruebas automáticas
```

### EA2: calidad y modelo dimensional

```powershell
python -m pip install -r requirements.txt
python -m src.transformar
```

`src.transformar` descarga DIVIPOLA desde la API oficial de Datos Abiertos si aún no
está en `data/bronze/`, transforma y valida cada tabla Plata con Pandera, conserva
rechazos en cuarentena, escribe métricas en [`docs/reporte_calidad.md`](docs/reporte_calidad.md)
y ejecuta `dbt build` sobre DuckDB. El esquema estrella, granos y diccionario están en
[`docs/modelo_dimensional.md`](docs/modelo_dimensional.md) y
[`docs/diccionario_datos.md`](docs/diccionario_datos.md). Las consultas y sus resultados
se documentan en [`consultas/oro/README.md`](consultas/oro/README.md).

La fuente propia externa es **DIVIPOLA — MinSalud / datos.gov.co**, separada de XM:
https://www.datos.gov.co/Salud-y-Protecci%C3%B3n-Social/MinSalud-Divipola-Municipios/pqwj-3fi4
La bitácora individual está en [`docs/bitacoras/Cardona_Jose.md`](docs/bitacoras/Cardona_Jose.md).
Completar con enlaces verificables los commits y la revisión por compañero requeridos por
el flujo de equipo; no se pueden afirmar hasta que se ejecuten realmente.

El reporte de calidad genera conteos reales después de una ejecución; no versionar ni
presentar como resultado las cifras de una corrida que falló. Los Parquet de bronce,
plata, gold, el DuckDB local, `dbt/target` y `dbt/logs` están excluidos de Git.

XM se consulta desde el 1 de enero de 2024 hasta el 30 de septiembre de 2026; IDEAM desde el 1 de enero de 2025 hasta la fecha final. El archivo Excel de EnerAndes debe estar disponible en `data/insumos/ventas_enerandes_2023_2026.xlsx`.

El pipeline omite archivos Parquet existentes. Para volver a descargar todo: `python -m src.pipeline --forzar`. Las muestras de las primeras 200 filas de cada Parquet se escriben en `data/sample/`; los datos completos de `data/bronze/` no se versionan. El perfilamiento y sus hallazgos están en `docs/perfilamiento.md`.

## 🏗️ Arquitectura

```
Fuentes -> BRONCE (dato tal cual + linaje) -> PLATA (limpio) -> ORO (modelo estrella) -> Dashboard
```

## 🤖 Uso de IA

SE USO GEMINI PARA GENERAR UNA GUIA SOBRE QUE EVIDENCIAS SON IMPORTANTES PARA ESTE PROYECTO BASADO EN LOS REQUIERIMIENTOS DE LA TAREA, ES QUE ERAN BASTANTES COSITAS Y HONESTAMENTE NO SABIA QUE QUERIA EL PROFE VER SOBRE EL DESARROLLO (POR MI COLOCO MIL CAPTURAS) ENTONCES SI QUERIA TENER UNA IDEA SOBRE QUE ERA LO MAS IMPORTANTE Y QUE DEBIA MOSTRAR ASI NI MI VIDEO, NI MIS CAPTURAS COLAPSARIAN EL PROYECTO Y SE VERIA MAS PROFESIONAL (SOY DECENTE DESARROLLANDO Y NO TAN BUENO CON DOCUMENTACIÓN -SALUDOS LOS QUIERO <3 )

## 🤖 EVIDENCIAS

![alt text](evidencias/evidencia_01_entorno.png)

![alt text](evidencias/evidencia_02_repositorio.png)

![alt text](evidencias/evidencia_03_repositorio.png)

![alt text](evidencias/evidencia_04_repositorio.png)

![alt text](evidencias/evidencia_05_repositorio.png)

![alt text](evidencias/evidencia_06_repositorio.png)

![alt text](evidencias/evidencia_07_repositorio.png)



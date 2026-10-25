# Observatorio Energía y Clima – Equipo <nombre>

> Proyecto Integrado IV – Integración de Información · IU Digital de Antioquia · 2026-2

## 👥 Integrantes

| Nombre | Usuario GitHub | Rol |
|---|---|---|
| José David Cardona Mazo| josedav17 | Líder técnico / Data Engineer |
| | | Data Quality Analyst |
| | | Analytics Engineer |
| | | BI Analyst / Storyteller |

## 🎯 Objetivo

Integrar datos del mercado eléctrico (XM), del clima (IDEAM y NOAA) y de ventas internas (EnerAndes) para analizar el riesgo energético de Colombia ante El Niño 2026.

## 📦 Fuentes de datos (capa bronce)

| Fuente | Tipo | Archivo en `data/bronze/` |
|---|---|---|
| XM – API Sinergox | API REST (POST, JSON) | Precio de bolsa, demanda, embalses, generacion por recurso, catalogo de recursos y aportes hidricos |
| IDEAM – datos.gov.co | API Socrata (SoQL) | Precipitacion y temperatura diaria por estacion |
| NOAA – índice ONI | Archivo de texto | `noaa_oni` |
| EnerAndes | Excel interno | `enerandes_ventas_2023` … `enerandes_ventas_2026` |

### Fuente propia del equipo: aportes hídricos de XM

El extractor `src/extract/xm_aportes.py` consulta `AporEner` en el endpoint diario de la API Sinergox de XM (entidad `Sistema`). Se agrega al rango del mercado eléctrico y se guarda como `xm_aportes_hidricos`. Este indicador mide los aportes de agua al sistema y permitirá contrastar la disponibilidad hídrica con la generación y el comportamiento de los embalses. El catálogo `ListadoRecursos` se consulta aparte en el endpoint `lists`, sin fechas, y se aplana desde `ListEntities`.

IDEAM se consulta en ventanas semanales con filtros de Antioquia y fechas, y cada resultado se agrega por día y estación mediante SoQL en el servidor. Temperatura media, mínima y máxima se calculan sobre las observaciones del dataset `sbwg-7ju4`.

## ⚙️ Cómo ejecutar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# ubicar ventas_enerandes_2023_2026.xlsx en data/insumos/
python -m src.pipeline          # descarga a data/bronze/ y crea muestras CSV
python -m src.consultar         # consultas SQL de BI con DuckDB
python -m pytest                # pruebas automáticas
```

XM se consulta desde el 1 de enero de 2024 hasta el 30 de septiembre de 2026; IDEAM desde el 1 de enero de 2025 hasta la fecha final. El archivo Excel de EnerAndes debe estar disponible en `data/insumos/ventas_enerandes_2023_2026.xlsx`.

El pipeline omite archivos Parquet existentes. Para volver a descargar todo: `python -m src.pipeline --forzar`. Las muestras de las primeras 200 filas de cada Parquet se escriben en `data/sample/`; los datos completos de `data/bronze/` no se versionan. El perfilamiento y sus hallazgos están en `docs/perfilamiento.md`.

## 🏗️ Arquitectura

```
Fuentes -> BRONCE (dato tal cual + linaje) -> PLATA (limpio) -> ORO (modelo estrella) -> Dashboard
```

## 🤖 Uso de IA

SE USO GEMINI PARA GENERAR UNA GUIA SOBRE QUE EVIDENCIAS SON IMPORTANTES PARA ESTE PROYECTO BASADO EN LOS REQUIERIMIENTOS DE LA TAREA, ES QUE ERAN BASTANTES COSITAS Y HONESTAMENTE NO SABIA QUE QUERIA EL PROFE VER EN EL DESARROLLO ENTONCES SI QUERIA SABER QUE ERA LO MAS IMPORTANTE Y QUE DEBIA MOSTRAR ASI NI MI VIDEO, NI MIS CAPTURAS COLAPSARIAN EL PROYECTO Y SE VERIA MAS PROFESIONAL (SOY DECENTE DESARROLLANDO Y NO TAN BUENO CON DOCUMENTACIÓN -SALUDOS LOS QUIERO <3 )

## 🤖 EVIDENCIAS

![alt text](/evidencias/evidencia_01_entorno.png)

![alt text](/evidencias/evidencia_02_repositorio.png)

![alt text](/evidencias/evidencia_03_repositorio.png)

![alt text](/evidencias/evidencia_04_repositorio.png)
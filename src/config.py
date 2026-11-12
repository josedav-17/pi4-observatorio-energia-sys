from datetime import date
from pathlib import Path

FECHA_INICIO = date(2024, 1, 1)
FECHA_FIN = date(2026, 9, 30)

RAIZ = Path(__file__).resolve().parent.parent
DIR_INSUMOS = RAIZ / "data" / "insumos"
DIR_BRONZE = RAIZ / "data" / "bronze"

# XM
XM_URL = "https://servapibi.xm.com.co/{periodo}"
XM_MAX_DIAS = 30  # Límite de días por petición de la API
XM_METRICAS = [
    ("PrecBolsNaci", "Sistema", "hourly", "xm_precio_bolsa"),
    ("DemaReal", "Sistema", "hourly", "xm_demanda"),
    ("PorcVoluUtilDiar", "Sistema", "daily", "xm_embalses"),
    ("Gene", "Recurso", "hourly", "xm_generacion_recurso"),
]
XM_CATALOGO_METRICA = "ListadoRecursos"
XM_APORTES_METRICA = ("AporEner", "Sistema", "daily", "xm_aportes_hidricos")

# IDEAM (datos.gov.co)
IDEAM_URL = "https://www.datos.gov.co/resource/s54a-sgyg.json"
IDEAM_TEMPERATURA_URL = "https://www.datos.gov.co/resource/sbwg-7ju4.json"
IDEAM_DEPARTAMENTO = "ANTIOQUIA"
IDEAM_DIAS_VENTANA = 7  # Ventanas cortas para evitar timeouts en Socrata
IDEAM_FECHA_INICIO = date(2025, 1, 1)

# NOAA
NOAA_ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"

# EnerAndes
ENERANDES_EXCEL = DIR_INSUMOS / "ventas_enerandes_2023_2026.xlsx"

# HTTP
HTTP_TIMEOUT = 120
HTTP_REINTENTOS = 4
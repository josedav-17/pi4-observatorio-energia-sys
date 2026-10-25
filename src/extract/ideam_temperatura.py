"""Temperatura diaria por estacion, agregada en el servidor de datos.gov.co."""
import pandas as pd

from src import config
from src.utils import guardar_bronce, http_json, log, ventanas, ya_existe

NOMBRE = "ideam_temperatura_diaria"
CAMPOS = "codigoestacion, nombreestacion, departamento, municipio, latitud, longitud"
PAGINA = 50000


def consulta_soql(inicio, fin, offset: int) -> dict:
    """Prepara una agregacion diaria de temperatura en SoQL."""
    return {
        "$select": (
            f"{CAMPOS}, date_trunc_ymd(fechaobservacion) AS fecha, "
            "avg(valorobservado) AS temperatura_media_c, "
            "min(valorobservado) AS temperatura_minima_c, "
            "max(valorobservado) AS temperatura_maxima_c, "
            "count(*) AS n_obs"
        ),
        "$where": (
            f"departamento = '{config.IDEAM_DEPARTAMENTO}' AND "
            f"fechaobservacion BETWEEN '{inicio}T00:00:00' AND '{fin}T23:59:59'"
        ),
        "$group": f"{CAMPOS}, fecha",
        "$order": "fecha, codigoestacion",
        "$limit": PAGINA,
        "$offset": offset,
    }


def extraer(forzar: bool = False) -> None:
    """Descarga temperaturas medias, minimas y maximas por dia y estacion."""
    log("IDEAM - temperatura del aire (SoQL)")
    if ya_existe(NOMBRE, forzar):
        return

    filas = []
    for inicio, fin in ventanas(
        config.IDEAM_FECHA_INICIO, config.FECHA_FIN, config.IDEAM_DIAS_VENTANA
    ):
        offset = 0
        while True:
            lote = http_json(
                "GET",
                config.IDEAM_TEMPERATURA_URL,
                params=consulta_soql(inicio, fin, offset),
            )
            filas.extend(lote)
            if len(lote) < PAGINA:
                break
            offset += PAGINA
        log(f"   semana {inicio} a {fin}: {len(lote)} filas")

    guardar_bronce(
        pd.DataFrame(filas),
        NOMBRE,
        fuente="IDEAM",
        origen=config.IDEAM_TEMPERATURA_URL,
    )


if __name__ == "__main__":
    import sys
    extraer(forzar="--forzar" in sys.argv)

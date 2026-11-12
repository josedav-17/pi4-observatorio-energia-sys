"""Descarga la referencia DIVIPOLA publicada por MinSalud en Datos Abiertos."""
import pandas as pd

from src import config
from src.utils import guardar_bronce, http_json, log, ya_existe

URL = "https://www.datos.gov.co/resource/pqwj-3fi4.json"


def extraer(forzar: bool = False) -> None:
    nombre = "divipola_municipios"
    if ya_existe(nombre, forzar):
        return
    log("DIVIPOLA - MinSalud / datos.gov.co")
    filas = http_json(
        "GET",
        URL,
        params={"$select": "idmupio,nommpio,iddepto,mpiolatitud,mpiolongitud", "$limit": 50000},
    )
    if not filas:
        raise RuntimeError(f"La fuente DIVIPOLA no devolvió registros: {URL}")
    guardar_bronce(
        pd.DataFrame(filas),
        nombre,
        fuente="MinSalud-DIVIPOLA",
        origen=URL,
    )


if __name__ == "__main__":
    import sys

    extraer(forzar="--forzar" in sys.argv)

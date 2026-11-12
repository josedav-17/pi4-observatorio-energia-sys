import io
import pandas as pd

from src import config
from src.utils import guardar_bronce, http_texto, log, ya_existe

NOMBRE = "noaa_oni"


def extraer(forzar: bool = False) -> None:
    log("NOAA - indice ONI (El Nino)")
    if ya_existe(NOMBRE, forzar):
        return

    texto = http_texto(config.NOAA_ONI_URL)
    df = pd.read_csv(io.StringIO(texto), sep=r"\s+", dtype=str)
    guardar_bronce(df, NOMBRE, fuente="NOAA", origen=config.NOAA_ONI_URL)


if __name__ == "__main__":
    import sys
    extraer(forzar="--forzar" in sys.argv)
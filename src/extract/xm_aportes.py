"""Fuente propia: aportes hidricos diarios de XM (AporEner)."""
import pandas as pd

from src import config
from src.extract.xm import aplanar
from src.utils import guardar_bronce, http_json, log, ventanas, ya_existe


def extraer(forzar: bool = False) -> None:
    """Consulta AporEner en ventanas diarias de hasta XM_MAX_DIAS."""
    metrica, entidad, periodo, nombre = config.XM_APORTES_METRICA
    log("XM - aportes hidricos diarios (AporEner)")
    if ya_existe(nombre, forzar):
        return

    url = config.XM_URL.format(periodo=periodo)
    filas = []
    for inicio, fin in ventanas(config.FECHA_INICIO, config.FECHA_FIN, config.XM_MAX_DIAS):
        cuerpo = {
            "MetricId": metrica,
            "Entity": entidad,
            "StartDate": str(inicio),
            "EndDate": str(fin),
            "Filter": [],
        }
        nuevas = aplanar(http_json("POST", url, json=cuerpo), periodo)
        filas.extend(nuevas)
        log(f"   {metrica} {inicio} a {fin}: {len(nuevas)} filas")
    guardar_bronce(pd.DataFrame(filas), nombre, fuente="XM", origen=f"{url} MetricId={metrica}")


if __name__ == "__main__":
    import sys
    extraer(forzar="--forzar" in sys.argv)

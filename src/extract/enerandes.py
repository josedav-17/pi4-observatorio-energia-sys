import pandas as pd

from src import config
from src.utils import guardar_bronce, log, ya_existe


def extraer(forzar: bool = False) -> None:
    log("EnerAndes - Excel interno")
    archivo = config.ENERANDES_EXCEL
    if not archivo.exists():
        raise FileNotFoundError(f"No se encontro {archivo}. Copielo en data/insumos/.")

    # Leemos todas las hojas crudas como texto; la detección de encabezados va en Silver
    hojas = pd.read_excel(archivo, sheet_name=None, header=None, dtype=str)
    for nombre_hoja, df in hojas.items():
        nombre = "enerandes_" + nombre_hoja.lower().replace(" ", "_")
        if ya_existe(nombre, forzar):
            continue

        # Parquet exige nombres de columna tipo string
        df.columns = [f"col_{i}" for i in range(df.shape[1])]
        guardar_bronce(df, nombre, fuente="EnerAndes", origen=f"{archivo.name}#{nombre_hoja}")


if __name__ == "__main__":
    import sys
    extraer(forzar="--forzar" in sys.argv)
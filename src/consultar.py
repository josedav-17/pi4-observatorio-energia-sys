import os
import duckdb

from src import config
from src.utils import log


def main() -> None:
    # Necesario porque las rutas dentro de los .sql son relativas a la raíz del proyecto
    os.chdir(config.RAIZ)
    con = duckdb.connect()

    for archivo in sorted((config.RAIZ / "consultas").glob("*.sql")):
        log(f"Consulta: {archivo.name}")
        sql = archivo.read_text(encoding="utf-8")
        print(con.sql(sql).df().to_string(index=False))
        print()


if __name__ == "__main__":
    main()
"""Ejecuta la capa plata, genera su reporte de calidad y construye dbt/Oro."""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone

from src import config
from src.extract import divipola
from src.transform.cleaners import execute


QUALITY_RULES = [
    "Encabezados de EnerAndes detectados por contenido y no por posición fija.",
    "Fechas normalizadas al primer día del mes y fuera de calendario a cuarentena.",
    "Energia 2024 en MWh convertida a kWh según la unidad de origen.",
    "Municipios normalizados, corregidos por alias y sin claves vacías.",
    "Ventas con medidas negativas o energía no numérica enviadas a cuarentena.",
    "Ventas sin duplicados por fecha, municipio, segmento y modalidad.",
    "XM horario en formato largo: una fila por fecha, hora y recurso cuando aplique.",
    "La hora XM debe pertenecer al rango inclusivo 1–24.",
    "Precio de bolsa acotado a -100.000–100.000.000 COP/kWh.",
    "Demanda y generación deben ser numéricas y no negativas.",
    "Embalses expresados en porcentaje entre 0 y 100.",
    "Aportes hídricos no negativos.",
    "Catálogo XM con código único y nombre de recurso informado.",
    "IDEAM con fecha, código de estación, municipio, coordenadas y medición válidos.",
    "Precipitación no negativa y temperatura mínima menor o igual a máxima.",
    "ONI trimestral asignado al mes central y fase clasificada con umbral ±0,5.",
    "DIVIPOLA con código municipal único, nombre y coordenadas numéricas.",
    "Cada tabla plata valida tipos, rangos y llaves con Pandera antes de persistir.",
]


def _write_quality_report(stats: dict[str, dict[str, int]]) -> None:
    report = [
        "# Reporte de calidad de datos — EA2",
        "",
        f"Última ejecución: {datetime.now(timezone.utc).isoformat(timespec='seconds')}.",
        "",
        "Los indicadores se calculan sobre las filas bronce inspeccionadas y las filas plata "
        "persistidas. Las filas rechazadas permanecen en `data/silver/cuarentena_*.parquet` "
        "con una columna `motivo`. No se reportan cifras simuladas: si una fuente no pudo "
        "procesarse, el comando termina con error.",
        "",
        "| Fuente | Filas antes | Filas plata | Cuarentena |",
        "|---|---:|---:|---:|",
    ]
    for source, values in sorted(stats.items()):
        report.append(
            f"| {source} | {values['antes']:,} | {values['despues']:,} | "
            f"{values['cuarentena']:,} |"
        )
    report.extend(["", "## Reglas aplicadas", ""])
    report.extend(f"{index}. {rule}" for index, rule in enumerate(QUALITY_RULES, 1))
    report.extend([
        "",
        "## Interpretación de cuarentena",
        "",
        "Se retienen las filas con fechas o claves vacías/ilegibles, medidas no numéricas, "
        "valores fuera de rango, claves duplicadas y encabezados/notas que no representan "
        "observaciones. Las ventas repetidas se excluyen del agregado plata después de "
        "guardar una copia de la fila duplicada con su motivo. Revisar cada archivo "
        "`cuarentena_<fuente>.parquet` antes de cambiar reglas.",
        "",
        "## Reconciliación",
        "",
        "La columna `Filas antes` cuenta registros de origen (en fuentes horarias de XM, "
        "una fila por día/recurso en formato ancho); `Filas plata` cuenta observaciones "
        "después del unpivot. Por ello, esos dos valores no son comparables directamente "
        "en tablas horarias. El conteo de cuarentena corresponde a observaciones rechazadas.",
        "",
    ])
    target = config.RAIZ / "docs" / "reporte_calidad.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    dane_file = config.DIR_BRONZE / "divipola_municipios.parquet"
    if not dane_file.exists():
        divipola.extraer()
    run = execute()
    _write_quality_report(run.stats)
    env = os.environ.copy()
    env["EA2_SILVER_DIR"] = (config.RAIZ / "data" / "silver").resolve().as_posix()
    env["EA2_DUCKDB_PATH"] = (
        config.RAIZ / "data" / "gold" / "observatorio.duckdb"
    ).resolve().as_posix()
    (config.RAIZ / "data" / "gold").mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable, "-m", "dbt.cli.main", "build",
        "--project-dir", str(config.RAIZ / "dbt"),
        "--profiles-dir", str(config.RAIZ / "dbt"),
    ]
    subprocess.run(command, cwd=config.RAIZ, env=env, check=True)


if __name__ == "__main__":
    main()

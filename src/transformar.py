from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone

from src import config
from src.extract import (
    divipola,
    enerandes,
    ideam,
    ideam_temperatura,
    noaa,
    xm,
    xm_aportes,
)
from src.transform.cleaners import ejecutar


def _preparar_bronce() -> None:
    extractores = (
        xm,
        xm_aportes,
        ideam,
        ideam_temperatura,
        noaa,
        enerandes,
        divipola,
    )
    for extractor in extractores:
        extractor.extraer()


def _escribir_reporte_calidad(
    stats: dict[str, dict[str, int]],
    metricas_reglas: list[dict[str, object]],
    resumen_cuarentenas: dict[str, dict[str, int]],
) -> None:
    reporte = [
        "# Reporte de calidad de datos — EA2",
        "",
        f"Última ejecución: {datetime.now(timezone.utc).isoformat(timespec='seconds')}.",
        "",
        "Generado automáticamente por `python -m src.transformar`. En las tablas, "
        "**Antes** es el número de filas evaluadas por la regla y **Después** el número "
        "que la supera. Las filas no corregibles se guardan en "
        "`data/silver/cuarentena_<fuente>.parquet` con la columna `motivo`.",
        "",
        "## Resumen por fuente",
        "",
        "| Fuente | Filas de entrada | Filas Plata | Cuarentena | Fuera de alcance |",
        "|---|---:|---:|---:|---:|",
    ]

    for fuente, valores in sorted(stats.items()):
        reporte.append(
            f"| {fuente} | {valores['antes']:,} | {valores['despues']:,} | "
            f"{valores['cuarentena']:,} | {valores['fuera_alcance']:,} |"
        )

    reporte.extend([
        "",
        "DIVIPOLA se limita a Antioquia, región de EnerAndes e IDEAM en este proyecto. "
        "Los municipios de otros departamentos se reportan como fuera de alcance, no como "
        "errores ni cuarentena. En las fuentes XM horarias, la entrada representa filas "
        "anchas (una por día/recurso) y Plata representa observaciones despivotadas.",
        "",
        "## Reglas, problemas y métricas antes/después",
        "",
        "Cada fuente tiene su propia tabla. Las reglas y los conteos de Antes/Después "
        "se registran durante el proceso de limpieza; no se escriben como cifras fijas.",
        "",
    ])

    for fuente in sorted({str(m["fuente"]) for m in metricas_reglas}):
        reporte.extend([
            f"### {fuente}",
            "",
            "| Problema detectado | Regla aplicada | Antes (filas) | Después (filas) |",
            "|---|---|---:|---:|",
        ])
        for metrica in metricas_reglas:
            if metrica["fuente"] == fuente:
                reporte.append(
                    f"| {metrica['problema']} | {metrica['regla']} | "
                    f"{metrica['antes']:,} | {metrica['despues']:,} |"
                )
        reporte.append("")

    reporte.extend([
        "## Cuarentena: cantidad y motivo",
        "",
        "Las filas no corregibles se conservan en Parquet con su razón de rechazo. "
        "Los motivos y cantidades de esta tabla se agrupan directamente desde esas filas.",
        "",
        "| Fuente | Motivo | Filas en cuarentena |",
        "|---|---|---:|",
    ])

    for fuente, motivos in sorted(resumen_cuarentenas.items()):
        for motivo, conteo in sorted(motivos.items()):
            reporte.append(f"| {fuente} | {motivo} | {conteo:,} |")

    if not resumen_cuarentenas:
        reporte.append("| — | No hubo filas para cuarentena | 0 |")

    destino = config.RAIZ / "docs" / "reporte_calidad.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(reporte), encoding="utf-8")


def main() -> None:
    _preparar_bronce()
    ejecucion = ejecutar()
    _escribir_reporte_calidad(
        ejecucion.stats,
        ejecucion.metricas_reglas,
        ejecucion.resumen_cuarentenas(),
    )

    entorno = os.environ.copy()
    entorno["EA2_SILVER_DIR"] = (config.RAIZ / "data" / "silver").resolve().as_posix()
    entorno["EA2_DUCKDB_PATH"] = (
        config.RAIZ / "data" / "gold" / "observatorio.duckdb"
    ).resolve().as_posix()

    (config.RAIZ / "data" / "gold").mkdir(parents=True, exist_ok=True)
    comando = [
        sys.executable, "-m", "dbt.cli.main", "build",
        "--project-dir", str(config.RAIZ / "dbt"),
        "--profiles-dir", str(config.RAIZ / "dbt"),
    ]
    subprocess.run(comando, cwd=config.RAIZ, env=entorno, check=True)


if __name__ == "__main__":
    main()
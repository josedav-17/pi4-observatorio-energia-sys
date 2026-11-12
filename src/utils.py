import time
from datetime import datetime, timedelta, timezone
import pandas as pd
import requests

from src import config


def log(mensaje: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {mensaje}", flush=True)


def _con_reintentos(funcion, descripcion: str):
    # Backoff exponencial (2s, 4s, 8s...) para errores transitorios de red
    for intento in range(1, config.HTTP_REINTENTOS + 1):
        try:
            return funcion()
        except requests.RequestException as error:
            if intento == config.HTTP_REINTENTOS:
                raise RuntimeError(f"Fallo definitivo en {descripcion}: {error}") from error
            espera = 2 ** intento
            log(f"   ! intento {intento} fallo ({type(error).__name__}); reintento en {espera} s")
            time.sleep(espera)


def http_json(metodo: str, url: str, **kwargs):
    def llamar():
        r = requests.request(metodo, url, timeout=config.HTTP_TIMEOUT, **kwargs)
        r.raise_for_status()
        return r.json()
    return _con_reintentos(llamar, f"{metodo} {url}")


def http_texto(url: str) -> str:
    def llamar():
        r = requests.get(url, timeout=config.HTTP_TIMEOUT)
        r.raise_for_status()
        return r.text
    return _con_reintentos(llamar, f"GET {url}")


def ventanas(inicio, fin, dias: int):
    """Divide el rango de fechas en bloques inclusivos de N días."""
    a = inicio
    while a <= fin:
        b = min(a + timedelta(days=dias - 1), fin)
        yield a, b
        a = b + timedelta(days=1)


def ruta_bronce(nombre: str):
    return config.DIR_BRONZE / f"{nombre}.parquet"


def ya_existe(nombre: str, forzar: bool) -> bool:
    if ruta_bronce(nombre).exists() and not forzar:
        log(f"   = {nombre}.parquet ya existe; se omite (use --forzar para repetir)")
        return True
    return False


def guardar_bronce(df: pd.DataFrame, nombre: str, fuente: str, origen: str) -> None:
    # Capa bronze: persistimos el dato crudo añadiendo solo trazabilidad
    df = df.copy()
    df["_fuente"] = fuente
    df["_origen"] = origen
    df["_extraido_en"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    config.DIR_BRONZE.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ruta_bronce(nombre), index=False)
    log(f"   + {nombre}.parquet guardado: {len(df):,} filas x {df.shape[1]} columnas")
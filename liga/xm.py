"""Descarga de datos de XM con la librería oficial pydataxm.

Repositorio oficial de XM: https://github.com/EquipoAnaliticaXM/API_XM
Instalación:              pip install pydataxm

Métricas que usa la liga:
    api.request_data("ListadoRecursos", "Sistema", ini, fin)   # catálogo de plantas → filtramos VIENTO
    api.request_data("Gene", "Recurso", ini, fin)              # generación horaria por planta (kWh)
    api.request_data("PrecBolsNaci", "Sistema", ini, fin)      # precio de bolsa nacional horario (COP/kWh)
"""
from __future__ import annotations

import datetime as dt
import time
from functools import lru_cache

import pandas as pd
import requests
from pydataxm.pydataxm import ReadDB

from .config import PALABRA_CLAVE

# pydataxm llama a requests SIN timeout: ponemos uno por defecto para no quedar colgados.
_request_original = requests.Session.request


def _request_con_timeout(self, method, url, **kw):
    if kw.get("timeout") is None:
        kw["timeout"] = (20, 120)
    return _request_original(self, method, url, **kw)


requests.Session.request = _request_con_timeout
HORAS = [f"Hour{h:02d}" for h in range(1, 25)]


def _con_reintentos(f, intentos=4, espera=20):
    for i in range(1, intentos + 1):
        try:
            return f()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"  XM no responde (intento {i}/{intentos}): {type(e).__name__}")
            if i == intentos:
                raise
            time.sleep(espera * i)


@lru_cache(maxsize=1)
def api() -> ReadDB:
    return ReadDB()


def _col(df: pd.DataFrame, sufijo: str) -> str:
    for c in df.columns:
        if c.lower().endswith(sufijo.lower()):
            return c
    raise KeyError(f"No encontré la columna '*{sufijo}' en {list(df.columns)}")


def _a_largo(df: pd.DataFrame, valor: str, id_cols: list[str]) -> pd.DataFrame:
    """Columnas Values_Hour01..24 → filas (fecha_hora, valor). Hour01 = 00:00–01:00 hora Colombia."""
    cols_h = [c for c in df.columns if c.split("_")[-1] in HORAS]
    largo = df.melt(id_vars=id_cols, value_vars=cols_h, var_name="h", value_name=valor)
    largo["fecha_hora"] = pd.to_datetime(largo["Date"]) + pd.to_timedelta(largo["h"].str[-2:].astype(int) - 1, unit="h")
    largo[valor] = pd.to_numeric(largo[valor], errors="coerce")
    return largo


def recursos_eolicos() -> pd.DataFrame:
    """Plantas cuya fuente es el viento (Values_EnerSource contiene VIENTO/EOLIC)."""
    hoy = dt.date.today()
    df = _con_reintentos(lambda: api().request_data("ListadoRecursos", "Sistema", hoy - dt.timedelta(days=1), hoy))
    texto = df.astype(str).apply(lambda c: c.str.upper())
    try:
        fuente = texto[_col(df, "EnerSource")]
        es_eolica = fuente.str.contains("VIENTO") | fuente.str.contains("EOLIC")
    except KeyError:
        es_eolica = texto.apply(lambda c: c.str.contains("VIENTO") | c.str.contains("EOLIC")).any(axis=1)
    out = pd.DataFrame({"codigo": texto.loc[es_eolica, _col(df, "Code")]})
    try:
        out["nombre"] = texto.loc[es_eolica, _col(df, "Name")]
    except KeyError:
        out["nombre"] = out["codigo"]
    out = out.drop_duplicates("codigo").reset_index(drop=True)
    print(f"  XM: recursos eólicos → {out.to_dict(orient='records')}")
    return out


def codigo_objetivo() -> str:
    """Código XM del parque objetivo: el recurso eólico cuyo nombre contiene PALABRA_CLAVE."""
    rec = recursos_eolicos()
    if rec.empty:
        raise RuntimeError("XM no reporta recursos eólicos. Revisa ListadoRecursos (Values_EnerSource).")
    hit = rec[rec.nombre.str.contains(PALABRA_CLAVE) | rec.codigo.str.contains(PALABRA_CLAVE)]
    if hit.empty and len(rec) == 1:
        hit = rec
    if hit.empty:
        raise RuntimeError(f"Ningún recurso eólico contiene '{PALABRA_CLAVE}': {rec.to_dict(orient='records')}. "
                           "Ajusta PALABRA_CLAVE en liga/config.py.")
    return hit.codigo.iloc[0]


def generacion_parque(codigo: str, inicio: dt.date, fin: dt.date) -> pd.DataFrame:
    """Generación horaria real del parque (MWh): fecha_hora, eolica_mwh."""
    df = _con_reintentos(lambda: api().request_data("Gene", "Recurso", inicio, fin))
    if df is None or df.empty:
        return pd.DataFrame(columns=["fecha_hora", "eolica_mwh"])
    col_codigo = _col(df, "code")
    df = df[df[col_codigo].astype(str).str.upper() == codigo]
    largo = _a_largo(df, "kwh", ["Date", col_codigo])
    largo["eolica_mwh"] = largo["kwh"] / 1000.0
    return largo[["fecha_hora", "eolica_mwh"]].sort_values("fecha_hora").reset_index(drop=True)


def precio_bolsa(inicio: dt.date, fin: dt.date) -> pd.DataFrame:
    """Precio de bolsa nacional horario: fecha_hora, precio_cop_kwh."""
    df = _con_reintentos(lambda: api().request_data("PrecBolsNaci", "Sistema", inicio, fin))
    if df is None or df.empty:
        return pd.DataFrame(columns=["fecha_hora", "precio_cop_kwh"])
    largo = _a_largo(df, "precio_cop_kwh", ["Date"])
    return largo[["fecha_hora", "precio_cop_kwh"]].dropna().sort_values("fecha_hora").reset_index(drop=True)

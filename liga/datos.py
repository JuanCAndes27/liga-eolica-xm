"""Construye y cachea el dataset horario: generación del parque (XM) + precio de bolsa (XM) + viento (Open-Meteo).

datos/historico.csv  -> fecha_hora, eolica_mwh, precio_cop_kwh, viento_10m, viento_80m, viento_120m,
                        direccion_80m, rafagas_10m, temperatura, presion
datos/clima.csv      -> clima reciente + pronóstico (incluye los días que vienen)
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

from .config import CAPACIDAD_MW

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
HIST = DATOS / "historico.csv"
CLIMA = DATOS / "clima.csv"
DIAS_HISTORIA = 90


def actualizar(demo: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    DATOS.mkdir(exist_ok=True)
    if demo:
        gen, clima = datos_sinteticos()
    else:
        from . import clima as cl, xm
        hoy = dt.date.today()
        inicio = hoy - dt.timedelta(days=DIAS_HISTORIA)
        print("Descargando viento de Open-Meteo…")
        try:
            clima = cl.clima_parque()
        except Exception as e:  # noqa: BLE001
            raise RuntimeError("Open-Meteo no respondió: sin pronóstico de viento no se puede comprometer. "
                               "Vuelve a correr la liga más tarde.") from e
        viejo = (pd.read_csv(HIST, parse_dates=["fecha_hora"])[["fecha_hora", "eolica_mwh", "precio_cop_kwh"]]
                 if HIST.exists() else None)
        print("Descargando generación del parque y precio de bolsa de XM…")
        try:
            codigo = xm.codigo_objetivo()
            g = xm.generacion_parque(codigo, inicio, hoy)
            p = xm.precio_bolsa(inicio, hoy)
            gen = g.merge(p, on="fecha_hora", how="inner")
        except Exception as e:  # noqa: BLE001
            if viejo is None:
                raise RuntimeError("XM no respondió y no hay datos guardados en datos/historico.csv todavía. "
                                   "Vuelve a correr la liga más tarde.") from e
            print(f"  ⚠ XM no respondió ({type(e).__name__}): uso la generación guardada "
                  f"(hasta {viejo.fecha_hora.max():%Y-%m-%d}) con el viento nuevo de Open-Meteo.")
            gen = viejo
        if viejo is not None:
            gen = pd.concat([viejo, gen]).drop_duplicates("fecha_hora", keep="last")
    gen = _dias_completos(gen)
    hist = gen.merge(clima, on="fecha_hora", how="left").sort_values("fecha_hora")
    hist.to_csv(HIST, index=False)
    clima.to_csv(CLIMA, index=False)
    print(f"Histórico: {hist.fecha_hora.min():%Y-%m-%d} → {hist.fecha_hora.max():%Y-%m-%d} "
          f"({hist.fecha_hora.dt.date.nunique()} días)")
    return hist, clima


def cargar() -> tuple[pd.DataFrame, pd.DataFrame]:
    return (pd.read_csv(HIST, parse_dates=["fecha_hora"]),
            pd.read_csv(CLIMA, parse_dates=["fecha_hora"]))


def _dias_completos(gen: pd.DataFrame) -> pd.DataFrame:
    """XM publica con rezago: dejamos solo días con las 24 horas de generación y precio.
    Los días con generación total 0 son paradas del parque (mantenimiento): no se pronostican."""
    g = gen.dropna(subset=["eolica_mwh", "precio_cop_kwh"]).copy()
    g["fecha"] = g.fecha_hora.dt.date
    stats = g.groupby("fecha")["eolica_mwh"].agg(["count", "sum"])
    ok = stats[(stats["count"] == 24) & (stats["sum"] > 0)].index
    return g[g.fecha.isin(ok)].drop(columns="fecha").reset_index(drop=True)


def curva_potencia(v, cap=CAPACIDAD_MW, v_in=3.0, v_nom=12.0, v_out=25.0):
    """Curva de potencia genérica (solo para los datos de juguete)."""
    v = np.asarray(v, dtype=float)
    return cap * np.clip((v**3 - v_in**3) / (v_nom**3 - v_in**3), 0, 1) * (v < v_out)


def datos_sinteticos(dias: int = DIAS_HISTORIA, semilla: int = 7):
    """Datos realistas de juguete para probar sin internet (modo --demo)."""
    rng = np.random.default_rng(semilla)
    hoy = pd.Timestamp(dt.date.today())
    horas = pd.date_range(hoy - pd.Timedelta(days=dias), hoy + pd.Timedelta(days=3), freq="h", inclusive="left")
    h, doy, n = horas.hour.values, horas.dayofyear.values, len(horas)
    # Alisios de La Guajira: más fuertes en la noche/madrugada y en dic–abr y jun–ago
    estacion = 1 + 0.20 * np.cos(2 * np.pi * (doy - 30) / 365) + 0.10 * np.cos(4 * np.pi * (doy - 200) / 365)
    diurno = 1 + 0.15 * np.cos(2 * np.pi * (h - 2) / 24)
    sinop = np.zeros(n)
    for i in range(1, n):
        sinop[i] = 0.97 * sinop[i - 1] + rng.normal(0, 0.30)          # sistemas que duran días
    v80 = np.clip(9.0 * estacion * diurno + sinop, 0.3, None)
    clima = pd.DataFrame({
        "fecha_hora": horas, "viento_10m": v80 * 0.78, "viento_80m": v80, "viento_120m": v80 * 1.05,
        "direccion_80m": (75 + rng.normal(0, 15, n)) % 360, "rafagas_10m": v80 * 1.25 + rng.gamma(2, 0.5, n),
        "temperatura": 28 + 3 * np.sin(2 * np.pi * (h - 9) / 24), "presion": 1010 + rng.normal(0, 1, n)})
    real = v80 + rng.normal(0, 0.9, n)                                   # el pronóstico no es perfecto
    disponible = np.where(rng.random(n // 24 + 1) < 0.05, 0.6, 1.0).repeat(24)[:n]   # 5 % de días con 4 de 10 turbinas fuera
    eolica = np.clip(curva_potencia(real) * disponible * 0.95 + rng.normal(0, 0.3, n), 0, CAPACIDAD_MW)
    pico = 1 + 0.35 * np.exp(-((h - 19) ** 2) / 4)                       # la bolsa sube en la punta de la noche
    precio = 300 * pico * np.repeat(rng.lognormal(0, 0.25, n // 24 + 1), 24)[:n]
    ultimo_xm = hoy - pd.Timedelta(days=1)                               # rezago de publicación de XM
    gen = pd.DataFrame({"fecha_hora": horas, "eolica_mwh": eolica, "precio_cop_kwh": precio})
    gen = gen[gen.fecha_hora < ultimo_xm]
    return gen, clima

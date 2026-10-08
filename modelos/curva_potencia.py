"""Línea base #3 (física): curva de potencia EMPÍRICA del parque aplicada al viento pronosticado.

1. Con la historia, agrupa el viento a 80 m en intervalos de 0,5 m/s y promedia la generación real.
   Esa curva ya incluye densidad del aire, estelas, disponibilidad y pérdidas eléctricas del parque.
2. Aplica la curva al viento pronosticado para mañana.

Es lo que haría un ingeniero de operación con una hoja de cálculo. Predice la MEDIA condicional.
"""
import numpy as np
import pandas as pd

NOMBRE = "Curva de potencia empírica"
AUTOR = "profe"
ANCHO = 0.5


def predecir(historia, clima_dia):
    h = historia.dropna(subset=["viento_80m", "eolica_mwh"])
    bins = np.arange(0, h.viento_80m.max() + 2 * ANCHO, ANCHO)
    g = h.groupby(pd.cut(h.viento_80m, bins, labels=bins[:-1]), observed=True)["eolica_mwh"].agg(["mean", "count"])
    g = g[g["count"] >= 3]
    vx = g.index.astype(float).to_numpy() + ANCHO / 2
    vy = np.maximum.accumulate(g["mean"].to_numpy())          # una curva de potencia no baja con más viento
    return np.interp(clima_dia.viento_80m.to_numpy(), vx, vy, left=0.0, right=vy[-1])

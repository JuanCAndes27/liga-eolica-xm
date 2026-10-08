"""Viento horario desde Open-Meteo (gratis, sin API key) en el sitio del parque.

Con past_days=92 obtenemos el pasado reciente + el pronóstico de los próximos días en una sola consulta.
Alturas disponibles en la API de pronóstico: 10, 80 y 120 m (los rotores modernos están entre 80 y 120 m).
"""
from __future__ import annotations

import pandas as pd
import requests

from .config import LAT, LON

VARIABLES = ["wind_speed_10m", "wind_speed_80m", "wind_speed_120m", "wind_direction_80m",
             "wind_gusts_10m", "temperature_2m", "surface_pressure"]
RENOMBRE = {"wind_speed_10m": "viento_10m", "wind_speed_80m": "viento_80m", "wind_speed_120m": "viento_120m",
            "wind_direction_80m": "direccion_80m", "wind_gusts_10m": "rafagas_10m",
            "temperature_2m": "temperatura", "surface_pressure": "presion"}


def clima_parque(past_days: int = 92, forecast_days: int = 3) -> pd.DataFrame:
    r = requests.get("https://api.open-meteo.com/v1/forecast", timeout=60, params={
        "latitude": LAT, "longitude": LON, "hourly": ",".join(VARIABLES), "wind_speed_unit": "ms",
        "timezone": "America/Bogota", "past_days": past_days, "forecast_days": forecast_days})
    r.raise_for_status()
    h = pd.DataFrame(r.json()["hourly"])
    h["fecha_hora"] = pd.to_datetime(h.pop("time"))
    return h.rename(columns=RENOMBRE)

"""Funciones compartidas por los modelos de machine learning del profe (empieza por _: la liga no lo carga)."""
import numpy as np
import pandas as pd


def features(df: pd.DataFrame) -> pd.DataFrame:
    """Variables explicativas a partir del clima y la hora (las mismas para entrenar y para predecir)."""
    hora = df.fecha_hora.dt.hour
    rad = np.deg2rad(df.direccion_80m)
    return pd.DataFrame({
        "v80": df.viento_80m, "v120": df.viento_120m, "v10": df.viento_10m,
        "v80_cubo": np.clip(df.viento_80m, 0, 13) ** 3,          # la potencia sube con v³ hasta la nominal
        "cizalladura": df.viento_120m / df.viento_10m.clip(lower=0.5),
        "rafagas": df.rafagas_10m, "dir_sin": np.sin(rad), "dir_cos": np.cos(rad),
        "hora_sin": np.sin(2 * np.pi * hora / 24), "hora_cos": np.cos(2 * np.pi * hora / 24),
        "temperatura": df.temperatura, "presion": df.presion,
    }, index=df.index)


def entrenamiento(historia: pd.DataFrame):
    h = historia.dropna(subset=["eolica_mwh", "viento_80m", "viento_120m", "viento_10m", "direccion_80m"])
    return features(h), h["eolica_mwh"].to_numpy()

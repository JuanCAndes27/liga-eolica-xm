"""Línea base #2 (estadística): perfil horario promedio de los últimos 14 días.

Captura el ciclo diario de los alisios (más viento en la noche y la madrugada), pero no sabe nada del
viento de mañana.
"""
import numpy as np

NOMBRE = "Perfil horario 14 días"
AUTOR = "profe"


def predecir(historia, clima_dia):
    ult = historia[historia.fecha_hora >= historia.fecha_hora.max() - np.timedelta64(14, "D")]
    return ult.groupby(ult.fecha_hora.dt.hour)["eolica_mwh"].mean().reindex(range(24)).fillna(0).to_numpy()

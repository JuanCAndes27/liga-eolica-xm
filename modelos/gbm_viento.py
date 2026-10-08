"""Modelo del profe: gradient boosting sobre viento (10/80/120 m), dirección, ráfagas, hora y clima.

Se re-entrena cada día con toda la historia disponible (aprendizaje en línea). Minimiza el error
cuadrático → predice la MEDIA condicional. Suele tener el mejor MAE… pero ¿el mejor puntaje en dólares?
"""
import sys
from pathlib import Path

from sklearn.ensemble import HistGradientBoostingRegressor

sys.path.insert(0, str(Path(__file__).parent))
from _ml_comun import entrenamiento, features  # noqa: E402

NOMBRE = "GBM viento"
AUTOR = "profe"


def predecir(historia, clima_dia):
    X, y = entrenamiento(historia)
    m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                      min_samples_leaf=20, l2_regularization=1.0, random_state=0)
    m.fit(X, y)
    return m.predict(features(clima_dia))

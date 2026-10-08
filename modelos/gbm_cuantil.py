"""Modelo del profe: el mismo GBM, pero entrenado para COMPROMETER el cuantil óptimo.

Como faltar cuesta 50 % del precio y sobrar 20 %, el compromiso que minimiza el costo esperado no es la
media sino el cuantil τ = 0,2 / (0,2 + 0,5) ≈ 0,29 de la distribución de generación (problema del
vendedor de periódicos). Se entrena con pérdida pinball en ese cuantil y ponderando cada hora por su
precio de bolsa: equivocarse en la punta de la noche cuesta más que en la madrugada.

Lección: tendrá PEOR MAE que "GBM viento"… y debería perder MENOS dinero.
"""
import sys
from pathlib import Path

from sklearn.ensemble import HistGradientBoostingRegressor

sys.path.insert(0, str(Path(__file__).parent))
from _ml_comun import entrenamiento, features  # noqa: E402
from liga.config import CUANTIL_OPTIMO  # noqa: E402

NOMBRE = "GBM cuantil óptimo"
AUTOR = "profe"


def predecir(historia, clima_dia):
    X, y = entrenamiento(historia)
    peso = historia.loc[X.index, "precio_cop_kwh"].fillna(historia["precio_cop_kwh"].median()).to_numpy()
    m = HistGradientBoostingRegressor(loss="quantile", quantile=CUANTIL_OPTIMO, max_iter=300, learning_rate=0.05,
                                      max_leaf_nodes=15, min_samples_leaf=20, l2_regularization=1.0, random_state=0)
    m.fit(X, y, sample_weight=peso / peso.mean())
    return m.predict(features(clima_dia))

"""El puntaje de la liga: cuánto dinero pierde el parque por equivocarse en su compromiso.

Para cada hora h, con generación real R, compromiso F (el pronóstico) y precio de bolsa P:

    costo_h = P_h × [ α_exc · max(R − F, 0)  +  α_falt · max(F − R, 0) ]

Es una *pinball loss* ponderada por el precio. Dos consecuencias que vale la pena discutir en clase:
  1. Equivocarse a las 7 p. m. (bolsa cara) cuesta más que a las 4 a. m.
  2. Como faltar (α_falt = 0.5) castiga más que sobrar (α_exc = 0.2), conviene comprometer MENOS
     que el valor esperado: el compromiso óptimo es el cuantil α_exc / (α_exc + α_falt) ≈ 0.29.
"""
from __future__ import annotations

import numpy as np

from .config import ALFA_EXCEDENTE, ALFA_FALTANTE, TRM


def precio_usd_mwh(precio_cop_kwh):
    return np.asarray(precio_cop_kwh, dtype=float) * 1000.0 / TRM


def costo_desvio_usd(real, pron, precio_cop_kwh):
    """Costo (USD) de cada hora por desviarse del compromiso."""
    real, pron = np.asarray(real, dtype=float), np.asarray(pron, dtype=float)
    p = precio_usd_mwh(precio_cop_kwh)
    return p * (ALFA_EXCEDENTE * np.clip(real - pron, 0, None) + ALFA_FALTANTE * np.clip(pron - real, 0, None))


def valor_energia_usd(real, precio_cop_kwh):
    """Lo que valdría la energía si el pronóstico fuera perfecto (referencia para el %)."""
    return np.asarray(real, dtype=float) * precio_usd_mwh(precio_cop_kwh)

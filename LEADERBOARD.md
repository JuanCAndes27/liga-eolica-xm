# 🌬️ Liga de Pronóstico Eólico Colombia — Leaderboard

_Actualizado: 2026-10-17 09:49 (hora Colombia) · Parque: **Guajira I** (20 MW) · Gana quien **pierde menos dinero por desviaciones**: faltar cuesta 50% del precio de bolsa, sobrar cuesta 20% · TRM 3,800 · Cuantil óptimo teórico ≈ 0.29_

## 🏆 Liga oficial (compromisos hechos ANTES de conocer el dato real)

| # | Modelo | Autor | Días | 💵 Costo de desvío (USD/día) | % del valor de la energía | Skill $ vs persistencia | MAE (MWh) | Sesgo (MWh) |
|---|---|---|---|---|---|---|---|---|
| 🥇 | GBM cuantil óptimo | profe | 4 | 3,055 | 5.2% | +43.6% | 3.50 | -2.78 |
| 🥈 | GBM viento | profe | 4 | 3,237 | 5.5% | +40.2% | 3.06 | -1.50 |
| 🥉 | Perfil horario 14 días | profe | 4 | 3,469 | 5.9% | +36.0% | 2.90 | -0.94 |
| 4 | Curva de potencia empírica | profe | 4 | 3,661 | 6.3% | +32.4% | 3.22 | -1.21 |
| 5 | Persistencia | profe | 4 | 5,417 | 9.3% | — | 5.28 | -3.04 |

![último día](resultados/ultimo_dia.png)

## 🧪 Backtest (días pasados, para arrancar en frío)

_Ojo: en el backtest el 'pronóstico' de viento es casi el viento observado → resultados optimistas._

| # | Modelo | Autor | Días | 💵 Costo de desvío (USD/día) | % del valor de la energía | Skill $ vs persistencia | MAE (MWh) | Sesgo (MWh) |
|---|---|---|---|---|---|---|---|---|
| 🥇 | GBM cuantil óptimo | profe | 14 | 3,390 | 5.8% | +46.4% | 2.85 | -0.80 |
| 🥈 | GBM viento | profe | 14 | 3,832 | 6.6% | +39.4% | 2.72 | +0.29 |
| 🥉 | Curva de potencia empírica | profe | 14 | 4,027 | 6.9% | +36.4% | 3.11 | -0.26 |
| 4 | Perfil horario 14 días | profe | 14 | 5,566 | 9.6% | +12.0% | 3.52 | +1.73 |
| 5 | Persistencia | profe | 14 | 6,328 | 10.9% | — | 4.55 | +0.66 |

![backtest](resultados/backtest.png)

**Cómo leer la tabla:** el *sesgo* negativo significa que el modelo compromete menos de lo que genera. Con estas reglas eso **conviene** un poco: faltar castiga más que sobrar.

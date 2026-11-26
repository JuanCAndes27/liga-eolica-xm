# 🌬️ Liga de Pronóstico Eólico Colombia — Leaderboard

_Actualizado: 2026-11-26 15:49 (hora Colombia) · Parque: **Guajira I** (20 MW) · Gana quien **pierde menos dinero por desviaciones**: faltar cuesta 50% del precio de bolsa, sobrar cuesta 20% · TRM 3,800 · Cuantil óptimo teórico ≈ 0.29_

## 🏆 Liga oficial (compromisos hechos ANTES de conocer el dato real)

| # | Modelo | Autor | Días | 💵 Costo de desvío (USD/día) | % del valor de la energía | Skill $ vs persistencia | MAE (MWh) | Sesgo (MWh) |
|---|---|---|---|---|---|---|---|---|
| 🥇 | GBM cuantil óptimo | profe | 25 | 3,729 | 7.7% | +33.7% | 3.38 | -0.43 |
| 🥈 | GBM viento | profe | 25 | 4,141 | 8.5% | +26.4% | 3.36 | +0.62 |
| 🥉 | Curva de potencia empírica | profe | 25 | 4,461 | 9.2% | +20.7% | 3.73 | +0.70 |
| 4 | Perfil horario 14 días | profe | 25 | 4,630 | 9.5% | +17.7% | 4.06 | -0.51 |
| 5 | Persistencia | profe | 25 | 5,626 | 11.6% | — | 5.56 | -2.26 |

![último día](resultados/ultimo_dia.png)

## 🧪 Backtest (días pasados, para arrancar en frío)

_Ojo: en el backtest el 'pronóstico' de viento es casi el viento observado → resultados optimistas._

| # | Modelo | Autor | Días | 💵 Costo de desvío (USD/día) | % del valor de la energía | Skill $ vs persistencia | MAE (MWh) | Sesgo (MWh) |
|---|---|---|---|---|---|---|---|---|
| 🥇 | GBM cuantil óptimo | profe | 14 | 3,377 | 5.8% | +46.3% | 2.85 | -0.80 |
| 🥈 | GBM viento | profe | 14 | 3,818 | 6.6% | +39.3% | 2.72 | +0.29 |
| 🥉 | Curva de potencia empírica | profe | 14 | 4,013 | 6.9% | +36.2% | 3.11 | -0.26 |
| 4 | Perfil horario 14 días | profe | 14 | 5,531 | 9.5% | +12.1% | 3.52 | +1.73 |
| 5 | Persistencia | profe | 14 | 6,292 | 10.8% | — | 4.55 | +0.66 |

![backtest](resultados/backtest.png)

**Cómo leer la tabla:** el *sesgo* negativo significa que el modelo compromete menos de lo que genera. Con estas reglas eso **conviene** un poco: faltar castiga más que sobrar.

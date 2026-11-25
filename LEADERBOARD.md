# 🌬️ Liga de Pronóstico Eólico Colombia — Leaderboard

_Actualizado: 2026-11-25 15:57 (hora Colombia) · Parque: **Guajira I** (20 MW) · Gana quien **pierde menos dinero por desviaciones**: faltar cuesta 50% del precio de bolsa, sobrar cuesta 20% · TRM 3,800 · Cuantil óptimo teórico ≈ 0.29_

## 🏆 Liga oficial (compromisos hechos ANTES de conocer el dato real)

| # | Modelo | Autor | Días | 💵 Costo de desvío (USD/día) | % del valor de la energía | Skill $ vs persistencia | MAE (MWh) | Sesgo (MWh) |
|---|---|---|---|---|---|---|---|---|
| 🥇 | GBM cuantil óptimo | profe | 24 | 3,739 | 8.0% | +34.3% | 3.38 | -0.33 |
| 🥈 | GBM viento | profe | 24 | 4,186 | 8.9% | +26.5% | 3.38 | +0.73 |
| 🥉 | Curva de potencia empírica | profe | 24 | 4,517 | 9.6% | +20.6% | 3.77 | +0.80 |
| 4 | Perfil horario 14 días | profe | 24 | 4,578 | 9.7% | +19.6% | 4.04 | -0.38 |
| 5 | Persistencia | profe | 24 | 5,692 | 12.1% | — | 5.68 | -2.33 |

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

# 🌬️ Liga de Pronóstico Eólico Colombia — Leaderboard

_Actualizado: 2026-11-12 14:25 (hora Colombia) · Parque: **Guajira I** (20 MW) · Gana quien **pierde menos dinero por desviaciones**: faltar cuesta 50% del precio de bolsa, sobrar cuesta 20% · TRM 3,800 · Cuantil óptimo teórico ≈ 0.29_

## 🏆 Liga oficial (compromisos hechos ANTES de conocer el dato real)

| # | Modelo | Autor | Días | 💵 Costo de desvío (USD/día) | % del valor de la energía | Skill $ vs persistencia | MAE (MWh) | Sesgo (MWh) |
|---|---|---|---|---|---|---|---|---|
| 🥇 | GBM cuantil óptimo | profe | 14 | 2,942 | 5.8% | +46.2% | 3.30 | -1.73 |
| 🥈 | GBM viento | profe | 14 | 3,162 | 6.2% | +42.2% | 3.08 | -0.63 |
| 🥉 | Curva de potencia empírica | profe | 14 | 3,932 | 7.7% | +28.1% | 3.63 | -0.29 |
| 4 | Perfil horario 14 días | profe | 14 | 4,074 | 8.0% | +25.5% | 3.51 | -0.11 |
| 5 | Persistencia | profe | 14 | 5,470 | 10.8% | — | 5.21 | -1.68 |

![último día](resultados/ultimo_dia.png)

## 🧪 Backtest (días pasados, para arrancar en frío)

_Ojo: en el backtest el 'pronóstico' de viento es casi el viento observado → resultados optimistas._

| # | Modelo | Autor | Días | 💵 Costo de desvío (USD/día) | % del valor de la energía | Skill $ vs persistencia | MAE (MWh) | Sesgo (MWh) |
|---|---|---|---|---|---|---|---|---|
| 🥇 | GBM cuantil óptimo | profe | 14 | 3,385 | 5.8% | +46.4% | 2.85 | -0.80 |
| 🥈 | GBM viento | profe | 14 | 3,828 | 6.6% | +39.4% | 2.72 | +0.29 |
| 🥉 | Curva de potencia empírica | profe | 14 | 4,020 | 6.9% | +36.3% | 3.11 | -0.26 |
| 4 | Perfil horario 14 días | profe | 14 | 5,555 | 9.6% | +12.0% | 3.52 | +1.73 |
| 5 | Persistencia | profe | 14 | 6,315 | 10.9% | — | 4.55 | +0.66 |

![backtest](resultados/backtest.png)

**Cómo leer la tabla:** el *sesgo* negativo significa que el modelo compromete menos de lo que genera. Con estas reglas eso **conviene** un poco: faltar castiga más que sobrar.

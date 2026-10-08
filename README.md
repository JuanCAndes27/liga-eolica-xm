# 🌬️ Liga de Pronóstico Eólico Colombia

**Un Kaggle vivo con dinero de verdad en juego (bueno, casi).**
Cada mañana, GitHub Actions descarga la generación real del parque **Guajira I** (20 MW, La Guajira) y el
precio de bolsa desde **XM**, el pronóstico de viento de **Open-Meteo**, y cada modelo de la clase
**compromete** cuánta energía generará el parque mañana, hora a hora.

Cuando XM publica lo que realmente pasó, la liga calcula **cuánto dinero perdió cada modelo por
equivocarse**. El `LEADERBOARD.md` se actualiza solo.

> En la Liga Solar ganaba el menor error. Aquí gana **quien pierde menos plata**, y no siempre es el mismo modelo.

## ¿Cómo funciona?

```
 07:00 COL  ┌───────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌────────────────────┐
 (cron) ──▶ │ pydataxm (XM)     │──▶│ Open-Meteo       │──▶│ Todos los modelos│──▶│ Costo de desvío    │
            │ Gene Guajira I    │   │ viento 10/80/120m│   │ de modelos/*.py  │   │ con precio de bolsa│
            │ PrecBolsNaci      │   │ dirección, ráfaga│   │ comprometen      │   │ real → LEADERBOARD │
            └───────────────────┘   └──────────────────┘   └──────────────────┘   └────────────────────┘
```

## Las reglas del mercado

Cada hora *h*, con generación real **R**, compromiso **F** (tu pronóstico) y precio de bolsa **P**:

| Si el parque… | Pasa esto | Costo para el parque |
|---|---|---|
| genera **menos** de lo comprometido | compra el faltante en bolsa con recargo | **50 %** del precio × MWh faltantes |
| genera **más** de lo comprometido | vende el excedente con descuento | **20 %** del precio × MWh sobrantes |

$$\text{costo}_h = P_h \cdot \big[\,0{,}2\cdot(R_h-F_h)^+ \;+\; 0{,}5\cdot(F_h-R_h)^+\,\big]$$

Son **reglas de clase** inspiradas en los cargos por desviación del mercado eléctrico (están en `liga/config.py`).
El puntaje se expresa en USD con una TRM fija.

**Dos consecuencias que valen la clase entera:**
1. **Equivocarse a las 7 p. m. cuesta más que a las 4 a. m.**, porque la bolsa es más cara en la punta.
2. **Conviene comprometer por debajo de lo esperado.** Como faltar castiga más que sobrar, el compromiso
   óptimo no es la media sino el **cuantil 0,29** de la distribución de generación (el problema del
   *vendedor de periódicos*). Por eso el modelo con mejor MAE no necesariamente gana.

| Métrica del leaderboard | Qué significa |
|---|---|
| 💵 **Costo de desvío (USD/día)** | El puntaje: menos es mejor |
| % del valor de la energía | Qué fracción del ingreso perfecto se pierde por errores |
| Skill $ vs persistencia | 1 − costo / costo de la persistencia (positivo = le ganas) |
| MAE, Sesgo | Solo de referencia. Sesgo negativo = compromete menos de lo que genera |

**Anti-trampa:** el primer compromiso de cada día queda congelado en `predicciones/AAAA-MM-DD.csv`
(el historial de git lo demuestra). XM publica con 1–2 días de rezago, así que el dato real llega después.

## Participar (estudiantes)

1. Haz **fork** de este repositorio.
2. Copia `modelos/_plantilla.py` como `modelos/<tu_usuario>.py` y escribe tu `predecir(historia, clima_dia)`.
3. Pruébalo localmente: `python -m liga.run_diario --demo --backtest 7`
4. Abre un **Pull Request**. El workflow *Validar modelos* lo prueba automáticamente.
5. Cuando el profe lo aprueba (merge), tu modelo compite desde la mañana siguiente.

## Correr localmente / en Colab

```bash
pip install -r requirements.txt
python -m liga.run_diario --demo --backtest 7     # sin internet, datos sintéticos
python -m liga.run_diario --backtest 14           # datos reales de XM + Open-Meteo
python -m experimentos.cuantil_optimo --dias 10   # ¿qué cuantil conviene comprometer?
```

En Colab: `!git clone https://github.com/<usuario>/liga-eolica-xm && %cd liga-eolica-xm` y los mismos comandos con `!`.

## Estructura

| Carpeta | Qué hay |
|---|---|
| `liga/config.py` | Parque, coordenadas, reglas de mercado (α de faltante y excedente), TRM |
| `liga/xm.py` | **pydataxm**: busca el recurso eólico en `ListadoRecursos`, baja `Gene` y `PrecBolsNaci` |
| `liga/clima.py` | Open-Meteo en el sitio del parque: viento a 10/80/120 m, dirección, ráfagas, temperatura, presión |
| `liga/mercado.py` | El puntaje: costo de desvío en USD |
| `liga/datos.py` | Arma el dataset, limpia días incompletos o con el parque parado, modo `--demo` |
| `liga/run_diario.py` | Orquesta: compromiso oficial, backtest, calificación, leaderboard y gráficas |
| `modelos/` | Un archivo `.py` por participante (los que empiezan por `_` se ignoran) |
| `experimentos/` | Barrido del cuantil comprometido: costo vs MAE |
| `predicciones/` | Compromisos oficiales congelados, uno por día |
| `.github/workflows/` | Pronóstico diario (cron), validación de PRs y Claude como analista |

### Modelos de referencia

| Modelo | Idea | Qué enseña |
|---|---|---|
| `Persistencia` | Mañana = último día conocido | La línea base que hay que vencer |
| `Perfil horario 14 días` | Promedio por hora de las últimas 2 semanas | El ciclo diario de los alisios, sin pronóstico |
| `Curva de potencia empírica` | Generación media por intervalo de viento a 80 m, aplicada al pronóstico | La física del parque con una hoja de cálculo |
| `GBM viento` | Gradient boosting con viento, dirección, ráfagas, cizalladura y hora | El mejor estimador de la **media** |
| `GBM cuantil óptimo` | El mismo GBM con pérdida pinball en τ = 0,29, ponderado por precio | Optimiza **dinero**, no MAE |

## Claude como analista de la liga (opcional)

Con el secreto `ANTHROPIC_API_KEY` configurado, cualquiera puede escribir en un issue o PR:

- `@claude ¿por qué todos los modelos perdieron plata ayer en la noche?`
- `@claude revisa mi modelo y dime si estoy comprometiendo demasiado`
- `@claude agrega la dirección del viento por sectores a la curva de potencia y abre un PR`

Las instrucciones que Claude sigue están en `CLAUDE.md`.

## Fuentes de datos

- **XM**: librería oficial `pydataxm` ([github.com/EquipoAnaliticaXM/API_XM](https://github.com/EquipoAnaliticaXM/API_XM)),
  API pública `servapibi.xm.com.co`, sin clave. `ListadoRecursos` (filtrando `EnerSource = VIENTO`), `Gene` por
  recurso (kWh horarios) y `PrecBolsNaci` (COP/kWh horario).
- **Open-Meteo**: pronóstico meteorológico abierto (`api.open-meteo.com`), sin clave.

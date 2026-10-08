"""PLANTILLA — copia este archivo como modelos/<tu_usuario_github>.py y edítalo.

Reglas de la liga:
  1. Define NOMBRE, AUTOR y la función predecir(historia, clima_dia).
  2. predecir devuelve 24 números: lo que el parque COMPROMETE generar (MWh) en cada hora del día objetivo.
     Se recorta entre 0 y la capacidad (20 MW).
  3. Debe correr en CPU en menos de 2 minutos (GitHub Actions gratis).
  4. Solo puedes usar lo que recibes: nada de descargar la respuesta real 😉

Entradas:
  historia   DataFrame horario: fecha_hora, eolica_mwh, precio_cop_kwh, viento_10m, viento_80m, viento_120m,
             direccion_80m, rafagas_10m, temperatura, presion
             (termina en el último día que XM ya publicó: 1-2 días de rezago)
  clima_dia  DataFrame de 24 filas con el PRONÓSTICO del día objetivo (mismas columnas de clima, sin
             eolica_mwh ni precio_cop_kwh: el precio de mañana tampoco se conoce)

El puntaje NO es el MAE: es el dinero que pierdes por desviarte (ver liga/mercado.py).
Faltar cuesta 50 % del precio de bolsa y sobrar 20 % → conviene comprometer un poco por debajo.
"""
import numpy as np

NOMBRE = "Mi modelo"
AUTOR = "tu_usuario_github"


def predecir(historia, clima_dia):
    # Ejemplo: promedio horario de los últimos 7 días
    ult = historia[historia.fecha_hora >= historia.fecha_hora.max() - np.timedelta64(7, "D")]
    return ult.groupby(ult.fecha_hora.dt.hour)["eolica_mwh"].mean().reindex(range(24), fill_value=0).to_numpy()

"""Línea base #1: 'mañana será igual al último día conocido'. Todo modelo debe vencerla."""
NOMBRE = "Persistencia"
AUTOR = "profe"


def predecir(historia, clima_dia):
    ultimo = historia[historia.fecha_hora.dt.date == historia.fecha_hora.dt.date.max()]
    return ultimo.sort_values("fecha_hora")["eolica_mwh"].to_numpy()

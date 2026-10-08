"""Parámetros de la liga. Todo lo que el profe quiera ajustar está aquí."""

# --- Parque objetivo -------------------------------------------------------------------
PARQUE = "Guajira I"
PALABRA_CLAVE = "GUAJIRA"      # se busca en el nombre del recurso eólico en XM
CAPACIDAD_MW = 20.0            # capacidad instalada (Isagen, en operación desde 2022)
LAT, LON = 12.17, -72.10       # Cabo de la Vela (aprox.); la celda de Open-Meteo mide ~10 km

# --- Reglas de mercado de la liga (inspiradas en los cargos por desviación) ------------
# Cada día, a las 07:00, el parque COMPROMETE su generación horaria del día siguiente.
#   · Si genera MENOS de lo comprometido, compra el faltante en bolsa con recargo:  P × (1 + ALFA_FALTANTE)
#   · Si genera MÁS, vende el excedente con descuento:                               P × (1 − ALFA_EXCEDENTE)
# Costo del error en la hora h:  P_h × [ ALFA_EXCEDENTE·(real − pron)⁺ + ALFA_FALTANTE·(pron − real)⁺ ]
ALFA_FALTANTE = 0.50
ALFA_EXCEDENTE = 0.20
TRM = 3800.0                   # COP/USD para expresar el puntaje en dólares

# Cuantil que minimiza el costo esperado (problema del "vendedor de periódicos"):
CUANTIL_OPTIMO = ALFA_EXCEDENTE / (ALFA_EXCEDENTE + ALFA_FALTANTE)   # ≈ 0.29

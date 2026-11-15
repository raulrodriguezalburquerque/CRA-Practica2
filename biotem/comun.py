"""Elementos comunes a las versiones de Biotem: variables, tabla de reglas y mecanismo de inferencia."""
from motor_difuso import VariableLinguistica, inferir_mamdani, mostrar_traza
from comun import TRIPLA, BIOTEMPERATURA, mostrar_fase, mostrar_fuzzificacion

# Etiquetas para las regiones latitudinales y los pisos altitudinales
REGIONES = ["Tropical", "Subtropical", "Templado cálido", "Templado frío", "Boreal", "Subpolar", "Polar"]
PISOS = ["Basal", "Premontano", "Montano bajo", "Montano", "Subalpino", "Alpino", "Nival"]

# Latitud
LATITUD = VariableLinguistica("latitud", (0, 90), {
    "Tropical":        ("trapecio", [0, 0, 9.8, 16.2]),
    "Subtropical":     ("trapecio", [9.8, 16.2, 23.9, 31.1]),
    "Templado cálido": ("trapecio", [23.9, 31.1, 39.1, 46.9]),
    "Templado frío":   ("trapecio", [39.1, 46.9, 57.2, 59.8]),
    "Boreal":          ("trapecio", [57.2, 59.8, 63.2, 64.3]),
    "Subpolar":        ("trapecio", [63.2, 64.3, 65.4, 66.6]),
    "Polar":           ("trapecio", [65.4, 66.6, 90, 90]),
})
# Altitud
ALTITUD = VariableLinguistica("altitud", (0, 5000), {
    "Basal":        ("trapecio", [0, 0, 750, 1250]),
    "Premontano":   ("trapecio", [750, 1250, 1750, 2250]),
    "Montano bajo": ("trapecio", [1750, 2250, 2750, 3250]),
    "Montano":      ("trapecio", [2750, 3250, 3875, 4125]),
    "Subalpino":    ("trapecio", [3875, 4125, 4437.5, 4562.5]),
    "Alpino":       ("trapecio", [4437.5, 4562.5, 4687.5, 4812.5]),
    "Nival":        ("trapecio", [4687.5, 4812.5, 5000, 5000]),
})
# La biotemperatura (salida) está en el comun.py de la raíz, porque también la usa el Zonificador
# Variables de entrada para el motor difuso de biotem
VARIABLES_BIOTEM = {"latitud": LATITUD, "altitud": ALTITUD}

# Tabla de reglas de biotemperatura
TABLA_BIOTEM = {
    #                   Basal              Premontano         Montano bajo       Montano            Subalpino   Alpino      Nival
    "Tropical":        ["Tropical",        "Subtropical",     "Templado cálido", "Templado frío",   "Boreal",   "Subpolar", "Polar"],
    "Subtropical":     ["Subtropical",     "Templado cálido", "Templado frío",   "Boreal",          "Subpolar", "Polar",    "Polar"],
    "Templado cálido": ["Templado cálido", "Templado frío",   "Boreal",          "Subpolar",        "Polar",    "Polar",    "Polar"],
    "Templado frío":   ["Templado frío",   "Boreal",          "Subpolar",        "Polar",           "Polar",    "Polar",    "Polar"],
    "Boreal":          ["Boreal",          "Subpolar",        "Polar",           "Polar",           "Polar",    "Polar",    "Polar"],
    "Subpolar":        ["Subpolar",        "Polar",           "Polar",           "Polar",           "Polar",    "Polar",    "Polar"],
    "Polar":           ["Polar",           "Polar",           "Polar",           "Polar",           "Polar",    "Polar",    "Polar"],
}

# Mecanismo de inferencia Mamdani clásico
IMPLICACION, DEFUZZIFICADOR = "mamdani", "centroide"

# Entradas para el motor difuso (latitud en valor absoluto).
def entradas(latitud, altitud):
    return {"latitud": abs(latitud), "altitud": altitud}

# Biotemperatura inferida con una base de reglas Mamdani.
def inferir_con_mamdani(reglas, latitud, altitud, traza=False):
    # Calculamos las entradas para el motor difuso
    e = entradas(latitud, altitud)
    # Inferimos la biotemperatura con el mecanismo de Mamdani
    valor, t = inferir_mamdani(e, VARIABLES_BIOTEM, reglas, BIOTEMPERATURA,
                               tripla=TRIPLA, implicacion=IMPLICACION, defuzzificador=DEFUZZIFICADOR)
    # Si se pide la traza, mostramos cada fase de la inferencia
    if traza:
        mostrar_fase(1, "Fuzzificación")
        mostrar_fuzzificacion(e, VARIABLES_BIOTEM)
        mostrar_fase(2, "Reglas disparadas (grado de disparo)")
        mostrar_traza(t)
        mostrar_fase(3, "Agregación (máximo) y defuzzificación (centroide)")
        print(f"   ABT = {valor:.4f} °C")
    return valor

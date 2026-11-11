"""Elementos comunes a las versiones de Biotem: variables, tabla de reglas y mecanismo de inferencia."""
from motor_difuso import VariableLinguistica, inferir_mamdani, mostrar_traza

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
# Biotemperatura
BIOTEMPERATURA = VariableLinguistica("biotemperatura", (0, 30), {
    "Polar":             ("trapecio", [0, 0, 1.2, 1.8]),
    "Subpolar":          ("trapecio", [1.2, 1.8, 2.7, 3.3]),
    "Boreal":            ("trapecio", [2.7, 3.3, 5.4, 6.6]),
    "Templado frío":     ("trapecio", [5.4, 6.6, 10.9, 13.1]),
    "Templado cálido":   ("trapecio", [10.9, 13.1, 16.9, 19.1]),
    "Subtropical":       ("trapecio", [16.9, 19.1, 22.9, 25.1]),
    "Tropical":          ("trapecio", [22.9, 25.1, 30, 30]),
    "Línea de escarcha": ("triangulo", [16.9, 18, 19.1]),
})
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
TRIPLA, IMPLICACION, DEFUZZIFICADOR = "zadeh", "mamdani", "centroide"

# Entradas para el motor difuso (latitud en valor absoluto).
def entradas(latitud, altitud):
    return {"latitud": abs(latitud), "altitud": altitud}

# Biotemperatura inferida con una base de reglas Mamdani.
def inferir_con_mamdani(reglas, latitud, altitud, traza=False):
    valor, t = inferir_mamdani(entradas(latitud, altitud), VARIABLES_BIOTEM, reglas, BIOTEMPERATURA,
                               tripla=TRIPLA, implicacion=IMPLICACION, defuzzificador=DEFUZZIFICADOR)
    if traza:
        mostrar_traza(t)
    return valor

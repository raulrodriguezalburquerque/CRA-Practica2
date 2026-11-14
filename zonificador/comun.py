# ===========================================================================
# Zonificador: variables, tabla de zonas de vida y nombres de las zonas
# ===========================================================================
from motor_difuso import VariableLinguistica
from comun import BIOTEMPERATURA

# Biotemperatura
ABT = BIOTEMPERATURA

# Precipitación
PRECIPITACIONES = ["Extremadamente escasa", "Muy escasa", "Escasa", "Moderada", "Abundante",
                   "Muy abundante", "Extremadamente abundante", "Excepcional"]

# Precipitación anual (mm)
APP = VariableLinguistica("app", (0, 16000), {
    "Extremadamente escasa":    ("trapecio", [0, 0, 101, 149]),
    "Muy escasa":               ("trapecio", [101, 149, 226, 274]),
    "Escasa":                   ("trapecio", [226, 274, 452, 548]),
    "Moderada":                 ("trapecio", [452, 548, 905, 1095]),
    "Abundante":                ("trapecio", [905, 1095, 1810, 2190]),
    "Muy abundante":            ("trapecio", [1810, 2190, 3620, 4380]),
    "Extremadamente abundante": ("trapecio", [3620, 4380, 7240, 8760]),
    "Excepcional":              ("trapecio", [7240, 8760, 16000, 16000]),
})
# PER (No se usa, explicación en apartado 1.5 del documento)
PER = VariableLinguistica("per", (0, 32), {
    "Súper-húmedo": ("trapecio", [0, 0, 0.20, 0.30]),
    "Per-húmedo":   ("trapecio", [0.20, 0.30, 0.45, 0.55]),
    "Húmedo":       ("trapecio", [0.45, 0.55, 0.91, 1.1]),
    "Sub-húmedo":   ("trapecio", [0.91, 1.1, 1.81, 2.19]),
    "Semi-árido":   ("trapecio", [1.81, 2.19, 3.62, 4.38]),
    "Árido":        ("trapecio", [3.62, 4.38, 7.24, 8.76]),
    "Per-árido":    ("trapecio", [7.24, 8.76, 14.48, 17.52]),
    "Súper-árido":  ("trapecio", [14.48, 17.52, 32, 32]),
})
# Variables de entrada para el motor difuso del Zonificador
VARIABLES_ZONIFICADOR = {"abt": ABT, "app": APP, "per": PER}

# Tabla de zonas de vida
TABLA_ZONIFICADOR = {
    #                  ExEsc MuyEsc Esc  Mod  Abu  MuyAbu ExAbu Exc
    "Polar":           [1,    1,    1,   1,   1,   1,    1,    1],
    "Subpolar":        [2,    3,    4,   5,   5,   5,    5,    5],
    "Boreal":          [6,    7,    8,   9,   10,  10,   10,   10],
    "Templado frío":   [11,   12,   13,  14,  15,  16,   16,   16],
    "Templado cálido": [17,   18,   19,  20,  21,  22,   23,   23],
    "Subtropical":     [24,   25,   26,  27,  28,  29,   30,   30],
    "Tropical":        [31,   32,   33,  34,  35,  36,   37,   38],
}

# Nombre de cada zona de vida
NOMBRES_ZONAS = {
    1: "Desierto polar",
    2: "Tundra seca",
    3: "Tundra húmeda",
    4: "Tundra muy húmeda",
    5: "Tundra pluvial",
    6: "Desierto boreal",
    7: "Matorral boreal seco",
    8: "Bosque boreal húmedo",
    9: "Bosque boreal muy húmedo",
    10: "Bosque boreal pluvial",
    11: "Desierto templado frío",
    12: "Matorral templado frío",
    13: "Estepa templada fría",
    14: "Bosque húmedo templado frío",
    15: "Bosque muy húmedo templado frío",
    16: "Bosque pluvial templado frío",
    17: "Desierto templado cálido",
    18: "Matorral xerófilo templado cálido",
    19: "Matorral espinoso templado cálido",
    20: "Bosque seco templado cálido",
    21: "Bosque húmedo templado cálido",
    22: "Bosque muy húmedo templado cálido",
    23: "Bosque pluvial templado cálido",
    24: "Desierto subtropical",
    25: "Matorral xerófilo subtropical",
    26: "Floresta espinosa subtropical",
    27: "Bosque seco subtropical",
    28: "Selva húmeda subtropical",
    29: "Selva muy húmeda subtropical",
    30: "Selva pluvial subtropical",
    31: "Desierto tropical",
    32: "Matorral xerófilo tropical",
    33: "Floresta espinosa tropical",
    34: "Bosque muy seco tropical",
    35: "Bosque seco tropical",
    36: "Selva húmeda tropical",
    37: "Selva muy húmeda tropical",
    38: "Selva pluvial tropical",
}

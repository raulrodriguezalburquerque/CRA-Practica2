# ===========================================================================
# Elementos comunes a Biotem y al Zonificador
# ===========================================================================
from motor_difuso import VariableLinguistica

# Tripla de operadores para Y, O y NO (mínimo, máximo y complemento)
TRIPLA = "zadeh"

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

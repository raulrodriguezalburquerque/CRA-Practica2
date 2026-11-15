# ===========================================================================
# Elementos comunes a Biotem y al Zonificador
# ===========================================================================
from motor_difuso import VariableLinguistica

# Tripla de operadores para Y, O y NO (mínimo, máximo y complemento)
TRIPLA = "zadeh"

# Traza: cabecera de cada fase de la inferencia
def mostrar_fase(numero, titulo):
    print(f" [{numero}] {titulo}")

# Traza: grado de pertenencia de cada entrada a sus etiquetas (solo las que no valen 0)
def mostrar_fuzzificacion(entradas, variables):
    for nombre, variable in variables.items():
        grados = {e: g for e, g in variable.grados(entradas[nombre]).items() if g > 0}
        print(f"   {nombre} = {entradas[nombre]:g}: " + ", ".join(f"{e}={g:.4f}" for e, g in grados.items()))

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

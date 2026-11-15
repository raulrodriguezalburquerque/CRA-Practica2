# ===========================================================================
# Elementos comunes a Biotem y al Zonificador
# ===========================================================================
from motor_difuso import VariableLinguistica

# Tripla de operadores para Y, O y NO (mínimo, máximo y complemento)
TRIPLA = "zadeh"

# Función auxiliar de la traza que muestra la cabecera de cada fase de la inferencia
def mostrar_fase(numero, titulo):
    print(f" [{numero}] {titulo}")

# Función auxiliar de la traza que muestra el grado de pertenencia de cada entrada a sus etiquetas
def mostrar_fuzzificacion(entradas, variables):
    # Recorremos cada variable de entrada
    for nombre, variable in variables.items():
        # Nos quedamos solo con las etiquetas cuyo grado no es 0
        grados = {e: g for e, g in variable.grados(entradas[nombre]).items() if g > 0}
        # Mostramos el valor de la entrada y su grado en cada etiqueta
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

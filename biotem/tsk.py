# ===========================================================================
# Biotem versión 3: TSK de orden 1
# ===========================================================================
from motor_difuso import es, inferir_tsk, mostrar_traza
from .comun import REGIONES, VARIABLES_BIOTEM, TRIPLA, entradas

"""Biotem versión 3: TSK de orden 1, ABT = b + m * L - 0,006 * h."""

# Puntos (L, ABT) de cada región
PUNTOS_TABLA2 = {
    "Tropical":        ((0, 30),     (13, 24)),
    "Subtropical":     ((13, 24),    (27.5, 18)),
    "Templado cálido": ((27.5, 18),  (43, 12)),
    "Templado frío":   ((43, 12),    (58.5, 6)),
    "Boreal":          ((58.5, 6),   (63.75, 3)),
    "Subpolar":        ((63.75, 3),  (66, 1.5)),
    "Polar":           ((66, 1.5),   (90, 0)),
}
# Descenso de la biotemperatura con la altitud (°C por metro)
GRADIENTE_ALTITUDINAL = 0.006

# Función que devuelve la pendiente y la ordenada en el origen de la recta que une dos puntos
def _recta(p1, p2):
    # Sacamos latitud y biotemperatura de cada punto
    (x1, y1), (x2, y2) = p1, p2
    # Calculamos la pendiente
    m = (y2 - y1) / (x2 - x1)
    # Calculamos la ordenada en el origen
    b = y1 - m * x1
    # Devolvemos la pendiente y la ordenada en el origen
    return m, b

# Disccionario que asocia a cada región latitudinal la pendiente y la ordenada en el origen de la recta que une los dos puntos de la tabla
# Ver apartado 1.4 de memoria de prácticas para ver la tabla con las rectas de cada región latitudinal
RECTAS = {region: _recta(*PUNTOS_TABLA2[region]) for region in REGIONES}

# Función que devuelve la biotemperatura media anual inferida a partir de la latitud y la altitud, siguiendo la formula: ABT = b + m · L − 0,006 · h
def _consecuente(m, b):
    return lambda e: b + m * e["latitud"] - GRADIENTE_ALTITUDINAL * e["altitud"]

# Reglas por región latitudinal (R1-R7)
# Ver apartado 1.4 de memoria de prácticas para ver la lista de reglas por cada región latitudinal
REGLAS = [(es("latitud", region), _consecuente(*RECTAS[region])) for region in REGIONES]

# Función de inferencia de biotem con base de reglas canónica TSK de orden 1
def inferir(latitud, altitud, traza=False):
    valor, t = inferir_tsk(entradas(latitud, altitud), VARIABLES_BIOTEM, REGLAS, tripla=TRIPLA)
    if traza:
        mostrar_traza(t)
    # Acotamos el valor a [0, 30] °C
    return min(30.0, max(0.0, valor))

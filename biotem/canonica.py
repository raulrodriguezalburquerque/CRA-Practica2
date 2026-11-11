# ===========================================================================
# Biotem versión 1: Mamdani con base de reglas canónica.
# ===========================================================================
from motor_difuso import es, Y
from .comun import REGIONES, PISOS, TABLA_BIOTEM, inferir_con_mamdani

# Base canónica: una regla por celda (R1-R49)
# Ver apartado 1.3 de memoria de prácticas para ver las reglas y la justificación de la base canónica
REGLAS = [
    (Y(es("latitud", region), es("altitud", piso)), TABLA_BIOTEM[region][j])
    for region in REGIONES
    for j, piso in enumerate(PISOS)
]

# Función de inferencia de biotem con base de reglas canónica
def inferir(latitud, altitud, traza=False):
    return inferir_con_mamdani(REGLAS, latitud, altitud, traza)

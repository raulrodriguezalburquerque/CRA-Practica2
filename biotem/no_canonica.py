# ===========================================================================
# Biotem versión 2: Mamdani con base de reglas no canónica.
# ===========================================================================
from motor_difuso import es, Y, O
from .comun import inferir_con_mamdani

# Función auxiliar que devuelve si la latitud es la etiqueta etq
def _lat(etq):
    return es("latitud", etq)

# Función auxiliar que devuelve si la altitud es una de las etiquetas etqs
def _alt(*etqs):
    return es("altitud", etqs[0]) if len(etqs) == 1 else O(*[es("altitud", e) for e in etqs])

# Base no canónica: una regla por consecuente (R1-R7)
# Ver apartado 1.3 de memoria de prácticas para ver las reglas y la justificación de la base no canónica
REGLAS = [
    # R1
    (Y(_lat("Tropical"), _alt("Basal")), "Tropical"),
    # R2
    (O(Y(_lat("Subtropical"), _alt("Basal")),
       Y(_lat("Tropical"), _alt("Premontano"))), "Subtropical"),
    # R3
    (O(Y(_lat("Templado cálido"), _alt("Basal")),
       Y(_lat("Subtropical"), _alt("Premontano")),
       Y(_lat("Tropical"), _alt("Montano bajo"))), "Templado cálido"),
    # R4
    (O(Y(_lat("Templado frío"), _alt("Basal")),
       Y(_lat("Templado cálido"), _alt("Premontano")),
       Y(_lat("Subtropical"), _alt("Montano bajo")),
       Y(_lat("Tropical"), _alt("Montano"))), "Templado frío"),
    # R5
    (O(Y(_lat("Boreal"), _alt("Basal")),
       Y(_lat("Templado frío"), _alt("Premontano")),
       Y(_lat("Templado cálido"), _alt("Montano bajo")),
       Y(_lat("Subtropical"), _alt("Montano")),
       Y(_lat("Tropical"), _alt("Subalpino"))), "Boreal"),
    # R6
    (O(Y(_lat("Subpolar"), _alt("Basal")),
       Y(_lat("Boreal"), _alt("Premontano")),
       Y(_lat("Templado frío"), _alt("Montano bajo")),
       Y(_lat("Templado cálido"), _alt("Montano")),
       Y(_lat("Subtropical"), _alt("Subalpino")),
       Y(_lat("Tropical"), _alt("Alpino"))), "Subpolar"),
    # R7
    (O(_lat("Polar"),
       Y(_lat("Subpolar"), _alt("Premontano", "Montano bajo", "Montano", "Subalpino", "Alpino", "Nival")),
       Y(_lat("Boreal"), _alt("Montano bajo", "Montano", "Subalpino", "Alpino", "Nival")),
       Y(_lat("Templado frío"), _alt("Montano", "Subalpino", "Alpino", "Nival")),
       Y(_lat("Templado cálido"), _alt("Subalpino", "Alpino", "Nival")),
       Y(_lat("Subtropical"), _alt("Alpino", "Nival")),
       Y(_lat("Tropical"), _alt("Nival"))), "Polar"),
]

# Función de inferencia de biotem con base de reglas no canónicas
def inferir(latitud, altitud, traza=False):
    return inferir_con_mamdani(REGLAS, latitud, altitud, traza)

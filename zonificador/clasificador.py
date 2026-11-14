# ===========================================================================
# Zonificador: clasificador difuso de zonas de vida
# ===========================================================================
from motor_difuso import es, Y, O, clasificar, mostrar_traza
from comun import TRIPLA
from .comun import PRECIPITACIONES, TABLA_ZONIFICADOR, VARIABLES_ZONIFICADOR

# Función auxiliar que devuelve si la precipitación es una de las etiquetas etqs
def _app(*etqs):
    return es("app", etqs[0]) if len(etqs) == 1 else O(*[es("app", e) for e in etqs])

# Función que construye las reglas a partir de la tabla: una por zona de vida (R1-R38)
# Ver apartado 1.5 de memoria de prácticas para ver la lista de reglas
def _reglas():
    reglas = []
    # Recorremos la tabla de zonas de vida, fila a fila
    for fila, codigos in TABLA_ZONIFICADOR.items():
        # Zonas de la fila, en orden
        for codigo in dict.fromkeys(codigos):
            # Franjas de precipitación que ocupa la zona
            columnas = [p for p, c in zip(PRECIPITACIONES, codigos) if c == codigo]
            # Si la zona ocupa toda la fila, solo depende de la biotemperatura
            if len(columnas) == len(PRECIPITACIONES):
                antecedente = es("abt", fila)
            # Si no, depende de la biotemperatura y de la precipitación
            else:
                antecedente = Y(es("abt", fila), _app(*columnas))
            # Guardamos la regla
            reglas.append((antecedente, codigo))
    return reglas

# Reglas del Zonificador: una por cada zona de vida (R1-R38)
REGLAS = _reglas()

# Decisión por suma normalizada
METODO_DECISION = "suma"

# Función de inferencia del Zonificador: zona asignada, su grado y los grados de las 38 zonas
def inferir(abt, app, traza=False):
    entradas = {"abt": abt, "app": app, "per": 58.93 * abt / app if app > 0 else 0.0}
    codigo, grado, grados, t = clasificar(entradas, VARIABLES_ZONIFICADOR, REGLAS, list(range(1, 39)),
                                          tripla=TRIPLA, metodo=METODO_DECISION)
    if traza:
        mostrar_traza(t)
    return codigo, grado, grados

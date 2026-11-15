# ===========================================================================
# Zonificador: clasificador difuso de zonas de vida
# ===========================================================================
from motor_difuso import es, Y, O, clasificar, mostrar_traza
from comun import TRIPLA, mostrar_fase, mostrar_fuzzificacion
from .comun import PRECIPITACIONES, TABLA_ZONIFICADOR, VARIABLES_ZONIFICADOR, ABT, APP, NOMBRES_ZONAS

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

# Función de inferencia del Zonificador: zona asignada, su grado, el margen y los grados de las 38 zonas
def inferir(abt, app, traza=False):
    # Calculamos las entradas para el motor difuso
    # La PER se calcula a partir de la ABT y la APP
    entradas = {"abt": abt, "app": app, "per": 58.93 * abt / app if app > 0 else 0.0}
    # Clasificamos con suma normalizada: zona asignada, su grado y los grados de las 38 zonas
    codigo, grado, grados, t = clasificar(entradas, VARIABLES_ZONIFICADOR, REGLAS, list(range(1, 39)),
                                          tripla=TRIPLA, metodo=METODO_DECISION)
    # Calculamos el margen: diferencia entre el grado de la zona asignada y el de la segunda con más grado
    margen = grado - sorted(grados.values(), reverse=True)[1]
    # Si se pide la traza, mostramos cada fase de la inferencia
    if traza:
        # La PER no se muestra porque no interviene en las reglas
        mostrar_fase(1, "Fuzzificación")
        mostrar_fuzzificacion(entradas, {"abt": ABT, "app": APP})
        mostrar_fase(2, "Reglas disparadas (grado de disparo)")
        mostrar_traza(t)
        mostrar_fase(3, "Suma normalizada (grado de cada zona)")
        print("   " + ", ".join(f"zona {c}={g:.4f}" for c, g in grados.items() if g > 0))
        mostrar_fase(4, "Decisión")
        print(f"   zona {codigo} {NOMBRES_ZONAS[codigo]}, grado {grado:.4f}, margen {margen:.4f}")
    return codigo, grado, margen, grados

"""
VUESTRA ESPECIFICACIÓN: Biotem (dos versiones) y el Zonificador.

Rellenad las partes marcadas con TODO a partir de vuestra especificación
(Sección 1.1 del Informe 2). Cada elemento debe coincidir EXACTAMENTE con
lo que figura en el informe. Mirad ejemplo_incendio.py para ver el formato.
"""
import numpy as np
from motor_difuso import (VariableLinguistica, es, Y, O, NO, inferir_mamdani,
                          inferir_tsk, clasificar, mostrar_traza, procesar_csv)

# ===========================================================================
# BIOTEM
# ===========================================================================
LATITUD = VariableLinguistica("latitud", (0, 90), {
    # TODO: "etiqueta": ("trapecio", [a, b, c, d]), ...
})
ALTITUD = VariableLinguistica("altitud", (0, 5000), {
    # TODO
})
BIOTEMPERATURA = VariableLinguistica("biotemperatura", (0, 30), {
    # TODO
})
VARIABLES_BIOTEM = {"latitud": LATITUD, "altitud": ALTITUD}

# Versión Mamdani, en dos formas: (antecedente, etiqueta de biotemperatura)
# Base canónica: una regla por combinación de etiquetas, siempre con la forma
#   (Y(es("latitud", "..."), es("altitud", "...")), "...")
REGLAS_BIOTEM_CANONICA = [
    # TODO
]
# Base no canónica: reglas parciales y reglas con O / NO, por ejemplo
#   (es("latitud", "..."), "...")   o   (Y(O(es(...), es(...)), NO(es(...))), "...")
REGLAS_BIOTEM_NO_CANONICA = [
    # TODO
]

# Segunda versión de Biotem (version=3): elegid su tipo de sistema y escribid sus reglas.
#   TIPO_BIOTEM_V2 = "mamdani": reglas (antecedente, etiqueta de biotemperatura)
#   TIPO_BIOTEM_V2 = "tsk":     reglas (antecedente, función del consecuente); la función
#                               recibe el diccionario de entradas: e["latitud"], e["altitud"]
TIPO_BIOTEM_V2 = None   # TODO: "mamdani" o "tsk"
REGLAS_BIOTEM_V2 = [
    # TODO
]

# Mecanismo de inferencia de la versión Mamdani (basta indicarlo si es el clásico)
TRIPLA, IMPLICACION, DEFUZZIFICADOR = "zadeh", "mamdani", "centroide"   # TODO: revisad

def biotem(latitud, altitud, version=1, traza=False):
    """Biotemperatura media anual inferida (°C).
    version: 1 (Mamdani, base canónica), 2 (Mamdani, base no canónica) o 3 (segunda versión)."""
    entradas = {"latitud": abs(latitud), "altitud": altitud}
    if version == 1:
        reglas, tipo = REGLAS_BIOTEM_CANONICA, "mamdani"
    elif version == 2:
        reglas, tipo = REGLAS_BIOTEM_NO_CANONICA, "mamdani"
    elif version == 3:
        reglas, tipo = REGLAS_BIOTEM_V2, TIPO_BIOTEM_V2
    else:
        raise ValueError("version debe ser 1, 2 o 3")
    if tipo == "mamdani":
        valor, t = inferir_mamdani(entradas, VARIABLES_BIOTEM, reglas, BIOTEMPERATURA,
                                   tripla=TRIPLA, implicacion=IMPLICACION, defuzzificador=DEFUZZIFICADOR)
    elif tipo == "tsk":
        valor, t = inferir_tsk(entradas, VARIABLES_BIOTEM, reglas, tripla=TRIPLA)
        valor = max(0.0, valor)   # la biotemperatura no puede ser negativa
    else:
        raise ValueError("Indicad TIPO_BIOTEM_V2: 'mamdani' o 'tsk'")
    if traza:
        mostrar_traza(t)
    return valor

# ===========================================================================
# ZONIFICADOR
# ===========================================================================
ABT = VariableLinguistica("abt", (0, 30), {
    # TODO
})
APP = VariableLinguistica("app", (np.log2(62.5), np.log2(16000)), {
    # TODO (si trabajáis en escala logarítmica, parámetros en log2)
}, transformacion=np.log2)
PER = VariableLinguistica("per", (-3, 5), {
    # TODO (solo si vuestras reglas usan la PER)
}, transformacion=np.log2)
VARIABLES_ZONIFICADOR = {"abt": ABT, "app": APP, "per": PER}

NOMBRES_ZONAS = {
    # TODO: código (1-38) -> nombre, según la Tabla 1 del documento de Coloreado de Mapas
}
# Reglas: (antecedente, código de zona de vida)
REGLAS_ZONIFICADOR = [
    # TODO
]
METODO_DECISION = "maximo"   # TODO: "maximo" o "suma"; justificadlo en el informe

def zonify(abt, app, traza=False):
    """Zona de vida asignada: código, nombre, grado, margen y grados de las 38 zonas."""
    entradas = {"abt": abt, "app": app, "per": 58.93 * abt / app if app > 0 else 0.0}
    codigo, grado, grados, t = clasificar(entradas, VARIABLES_ZONIFICADOR, REGLAS_ZONIFICADOR,
                                          list(range(1, 39)), tripla=TRIPLA, metodo=METODO_DECISION)
    if traza:
        mostrar_traza(t)
    segundo = sorted(grados.values(), reverse=True)[1]
    resultado = {"zona_codigo": codigo, "zona_nombre": NOMBRES_ZONAS.get(codigo, ""), "zona_grado": grado,
                 "zona_margen": grado - segundo}
    resultado.update({f"grado_{c:02d}": g for c, g in grados.items()})
    return resultado

# ===========================================================================
# Uso por lotes (ejemplos; ajustad nombres de columnas y archivos)
# ===========================================================================
if __name__ == "__main__":
    # Verificación: comparad con vuestros cálculos a mano
    # for v in (1, 2, 3):
    #     print(v, biotem(42.75, 971, v, traza=True))
    #
    # Estaciones: biotemperatura medida (de los datos mensuales) e inferida
    # from datos import leer_estaciones, leer_mensuales, abt_app
    # est = leer_estaciones("LISTA-ESTACIONES.csv")
    # abt, app, anios = abt_app(leer_mensuales("BU02_Valle_de_Valdelucio_01_01_2018_01_08_2024.csv"))
    # print(abt, app, [biotem(42.75, 971, v) for v in (1, 2, 3)], zonify(abt, app))
    #
    # Cuadrícula: Biotem -> Zonificador, por lotes
    # import pandas as pd
    # from datos import leer_cuadricula
    # cua = leer_cuadricula("DATOS-CUADRICULA.csv")
    # cua["abt"] = [biotem(la, al, 1) for la, al in zip(cua["latitud"], cua["altitud"])]
    # res = pd.concat([cua, pd.DataFrame([zonify(a, p) for a, p in zip(cua["abt"], cua["app"])])], axis=1)
    # res.to_csv("cuadricula_zonas.csv", index=False)
    #
    # Mapas (ver mapas.py)
    # from mapas import leer_paleta, dibujar_mapa_zonas, dibujar_mapa_margen
    # dibujar_mapa_zonas(res, leer_paleta(), ruta_shape="gadm41_ESP_1.shp")
    # dibujar_mapa_margen(res, ruta_shape="gadm41_ESP_1.shp")
    pass

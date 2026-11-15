"""
VUESTRA ESPECIFICACIÓN: Biotem (dos versiones) y el Zonificador.

Rellenad las partes marcadas con TODO a partir de vuestra especificación
(Sección 1.1 del Informe 2). Cada elemento debe coincidir EXACTAMENTE con
lo que figura en el informe. Mirad ejemplo_incendio.py para ver el formato.
"""
from motor_difuso import procesar_csv
from biotem import canonica, no_canonica, tsk
from zonificador import clasificador
from zonificador.comun import NOMBRES_ZONAS

# ===========================================================================
# BIOTEM
# ===========================================================================
# Versiones: 1 (Mamdani, base canónica), 2 (Mamdani, base no canónica), 3 (TSK)
VERSIONES_BIOTEM = {1: canonica, 2: no_canonica, 3: tsk}

def biotem(latitud, altitud, version=1, traza=False):
    """Biotemperatura media anual inferida (°C)."""
    if version not in VERSIONES_BIOTEM:
        raise ValueError("version debe ser 1, 2 o 3")
    return VERSIONES_BIOTEM[version].inferir(latitud, altitud, traza)

# ===========================================================================
# ZONIFICADOR
# ===========================================================================
def zonify(abt, app, traza=False):
    """Zona de vida asignada: código, nombre, grado, margen y grados de las 38 zonas."""
    codigo, grado, margen, grados = clasificador.inferir(abt, app, traza)
    resultado = {"zona_codigo": codigo, "zona_nombre": NOMBRES_ZONAS.get(codigo, ""), "zona_grado": grado,
                 "zona_margen": margen}
    resultado.update({f"grado_{c:02d}": g for c, g in grados.items()})
    return resultado

# ===========================================================================
# USO POR LOTES SOBRE UN CSV
# ===========================================================================
# Biotem para una fila: biotemperatura inferida con cada versión (columnas abt_v1, abt_v2, abt_v3)
def biotem_fila(latitud, altitud, versiones=(1, 2, 3)):
    return {f"abt_v{v}": biotem(latitud, altitud, v) for v in versiones}

# Aplica Biotem a cada fila de un CSV con columnas de latitud y altitud
def biotem_csv(entrada, salida, col_latitud="latitud", col_altitud="altitud", versiones=(1, 2, 3)):
    return procesar_csv(entrada, salida, biotem_fila, [col_latitud, col_altitud], versiones=versiones)

# Aplica el Zonificador a cada fila de un CSV con columnas de ABT y APP
def zonify_csv(entrada, salida, col_abt="abt", col_app="app"):
    return procesar_csv(entrada, salida, zonify, [col_abt, col_app])

# ===========================================================================
# VERIFICACIÓN
# ===========================================================================
# Trazas para comparar con los cálculos a mano
def verificar():
    for v in (1, 2, 3):
        print(f"Biotem v{v} - BU02 (42.75, 971 m):")
        biotem(42.75, 971, v, traza=True)
    # Zonificador: puntos P1, P2 y P3 de la práctica
    for punto, abt, app in (("P1", 15.2, 640), ("P2", 16.5, 495), ("P3", 12.3, 820)):
        print(f"Zonificador - {punto} (ABT {abt} °C, APP {app} mm):")
        zonify(abt, app, traza=True)

# Uso:
#   python sistemas.py                                 -> trazas de verificación
#   python sistemas.py biotem entrada.csv salida.csv   -> añade abt_v1, abt_v2 y abt_v3
#   python sistemas.py zonify entrada.csv salida.csv   -> añade zona_codigo ... grado_38
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        verificar()
    elif len(sys.argv) == 4 and sys.argv[1] in ("biotem", "zonify"):
        sistema, entrada, salida = sys.argv[1:]
        (biotem_csv if sistema == "biotem" else zonify_csv)(entrada, salida)
        print(f"Resultados guardados en {salida}")
    else:
        print("Uso: python sistemas.py [biotem|zonify entrada.csv salida.csv]")

    # Ejemplos para el ejercicio 3 (pendientes)
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

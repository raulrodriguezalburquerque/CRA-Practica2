# ===========================================================================
# Explotación de Biotem y el Zonificador sobre las estaciones y la cuadrícula
# ===========================================================================
import glob
import os
import numpy as np
import pandas as pd
from sistemas import biotem, zonify
from datos import leer_estaciones, leer_cuadricula, leer_mensuales, abt_app

# Rutas de entrada
RUTA_ESTACIONES = "datos/LISTA-ESTACIONES.csv"
RUTA_CUADRICULA = "datos/DATOS-CUADRICULA.csv"
CARPETA_MENSUALES = "datos/DatosClimaticos"

# Rutas de salida
SALIDA_ESTACIONES = "resultados/estaciones.csv"
SALIDA_METRICAS = "resultados/metricas_estaciones.csv"
SALIDA_BIOTEM_CUADRICULA = "resultados/biotem/cuadricula.csv"
SALIDA_ZONAS_CUADRICULA = "resultados/zonificador/cuadricula_v{}.csv"

# Versiones de Biotem
VERSIONES = (1, 2, 3)
# Versiones de Biotem que se encadenan con el Zonificador en la cuadrícula
VERSIONES_CADENA = (1, 3)

# ===========================================================================
# ESTACIONES
# ===========================================================================
# Función que devuelve un diccionario con la ruta del archivo de datos mensuales de cada estación
def _archivos_mensuales():
    rutas = glob.glob(os.path.join(CARPETA_MENSUALES, "*.csv"))
    return {os.path.basename(r).split("_")[0]: r for r in rutas}

# Función que aplica Biotem y el Zonificador a cada estación y compara con la ABT medida
def estaciones():
    # Leemos la lista de estaciones y los archivos mensuales
    est = leer_estaciones(RUTA_ESTACIONES)
    archivos = _archivos_mensuales()
    # Array para guardar los resultados de cada estación
    filas = []

    # Recorremos cada estación
    for _, e in est.iterrows():
        fila = {"id": e["id"], "provincia": e["provincia"], "municipio": e["municipio"],
                "latitud": e["latitud"], "altitud": e["altitud"]}
        # ABT inferida por cada versión de Biotem
        for v in VERSIONES:
            fila[f"abt_v{v}"] = biotem(e["latitud"], e["altitud"], v)
        # Si la estación tiene datos mensuales, calculamos la ABT y la APP medidas
        if e["id"] in archivos:
            # Leemos los datos mensuales y calculamos la ABT y la APP medidas
            abt, app, anios = abt_app(leer_mensuales(archivos[e["id"]]))
            # Guardamos la ABT y la APP medidas y el número de años con datos
            fila.update({"abt_medida": abt, "app_medida": app, "anios": len(anios)})
            # Error de cada versión frente a la ABT medida
            for v in VERSIONES:
                fila[f"error_v{v}"] = fila[f"abt_v{v}"] - abt

            # Zona con la ABT medida
            z = zonify(abt, app)
            # Guardamos el código de zona, el nombre y el margen de la zona medida
            fila.update({"zona_medida": z["zona_codigo"], "nombre_medida": z["zona_nombre"],
                         "margen_medida": z["zona_margen"]})
            # Zona con la ABT inferida por cada versión
            for v in VERSIONES:
                z = zonify(fila[f"abt_v{v}"], app)
                fila.update({f"zona_v{v}": z["zona_codigo"], f"margen_v{v}": z["zona_margen"]})
        filas.append(fila)
    
    # Creamos un DataFrame con los resultados
    df = pd.DataFrame(filas)
    # Las estaciones sin datos dejan huecos, así que guardamos los códigos de zona y los años como enteros con nulos
    enteras = [c for c in df.columns if c.startswith("zona_")] + ["anios"]
    df[enteras] = df[enteras].astype("Int64")
    # Guardamos el DataFrame en un CSV
    df.to_csv(SALIDA_ESTACIONES, index=False)
    return df

# Función que calcula el error de cada versión y la coincidencia de zonas en las estaciones con datos
def metricas(df):
    # Filtramos las estaciones con datos de ABT medida
    con_datos = df.dropna(subset=["abt_medida"])
    # Array para guardar los resultados de cada estación
    filas = []

    # Recorremos cada versión
    for v in VERSIONES:
        # Calculamos el error frente a la ABT medida
        error = con_datos[f"error_v{v}"]
        filas.append({"version": v,
                      "sesgo": error.mean(),
                      "mae": error.abs().mean(),
                      "rmse": np.sqrt((error ** 2).mean()),
                      "error_max": error.abs().max(),
                      "estacion_error_max": con_datos.loc[error.abs().idxmax(), "id"],
                      "coincidencia_zona": (con_datos[f"zona_v{v}"] == con_datos["zona_medida"]).mean()})
    # Creamos un DataFrame con los resultados y lo guardamos en un CSV
    met = pd.DataFrame(filas)
    met.to_csv(SALIDA_METRICAS, index=False)
    return met

# ===========================================================================
# CUADRÍCULA
# ===========================================================================
# Función que aplica Biotem a la cuadrícula y encadena el Zonificador con la ABT inferida
def cuadricula():
    # Leemos la cuadrícula
    cua = leer_cuadricula(RUTA_CUADRICULA)
    # ABT inferida por cada versión de Biotem
    for v in VERSIONES:
        cua[f"abt_v{v}"] = [biotem(la, al, v) for la, al in zip(cua["latitud"], cua["altitud"])]
    # Guardamos la cuadrícula con la ABT inferida en un CSV
    cua.to_csv(SALIDA_BIOTEM_CUADRICULA, index=False)

    # Biotem -> Zonificador, un CSV por versión
    zonas = {}
    # Recorremos cada versión que se encadena con el Zonificador
    for v in VERSIONES_CADENA:
        # Creamos un DataFrame con la longitud, latitud, altitud, APP y ABT inferida
        base = cua[["longitud", "latitud", "altitud", "app"]].assign(abt=cua[f"abt_v{v}"])
        # Aplicamos el Zonificador a cada fila y guardamos el resultado en un DataFrame
        res = pd.DataFrame([zonify(a, p) for a, p in zip(base["abt"], base["app"])])
        # Guardamos el DataFrame con la ABT inferida y la zona en un CSV
        zonas[v] = pd.concat([base, res], axis=1)
        zonas[v].to_csv(SALIDA_ZONAS_CUADRICULA.format(v), index=False)
    return cua, zonas

# ===========================================================================
# COMPARATIVAS
# ===========================================================================
# Función que compara la versión 1 y la 2 y resume el rango de salida de cada versión
def comparativas(est, cua, zonas):
    # Diferencia entre la base canónica y la no canónica
    for nombre, df in (("estaciones", est), ("cuadrícula", cua)):
        dif = (df["abt_v1"] - df["abt_v2"]).abs()
        print(f"   v1 - v2 en {nombre}: diferencia máxima {dif.max():.6f}, puntos distintos {(dif > 1e-9).sum()}")
    # Rango de la ABT inferida en la cuadrícula
    for v in VERSIONES:
        print(f"   v{v} en cuadrícula: ABT de {cua[f'abt_v{v}'].min():.4f} a {cua[f'abt_v{v}'].max():.4f} °C")
    # Coincidencia de zona entre las versiones encadenadas en la cuadrícula
    igual = (zonas[1]["zona_codigo"] == zonas[3]["zona_codigo"]).mean()
    print(f"   zona igual con v1 y v3 en cuadrícula: {100 * igual:.1f} %")


# ===========================================================================
# PRUEBAS
# ===========================================================================
if __name__ == "__main__":
    pd.set_option("display.width", 200)
    # Aplicamos Biotem y el Zonificador a las estaciones y calculamos las métricas
    print("Estaciones:")
    est = estaciones()
    print(est[["id", "abt_medida", "abt_v1", "abt_v3", "zona_medida", "zona_v1", "zona_v3"]].round(2).to_string(index=False))
    print("\nMétricas (estaciones con datos):")
    print(metricas(est).round(4).to_string(index=False))
    # Aplicamos Biotem y el Zonificador a la cuadrícula y comparamos las versiones
    print("\nCuadrícula...")
    cua, zonas = cuadricula()
    print("\nComparativas:")
    comparativas(est, cua, zonas)

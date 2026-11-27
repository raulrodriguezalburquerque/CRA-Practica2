# ===========================================================================
# Explotación de Biotem y el Zonificador sobre las estaciones y la cuadrícula
# ===========================================================================
import glob
import textwrap
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter
from sistemas import biotem, zonify
from datos import leer_estaciones, leer_cuadricula, leer_mensuales, abt_app
from mapas import leer_paleta, dibujar_mapa_zonas, dibujar_mapa_margen
from zonificador.comun import NOMBRES_ZONAS, TABLA_ZONIFICADOR, PRECIPITACIONES

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
# FIGURAS
# ===========================================================================
# Carpeta de salida de las figuras
CARPETA_FIGURAS = "resultados/figuras"
# Color de cada versión
VERSIONES_FIGURA = {1: ("Mamdani (v1)", "#3a6fb8"), 3: ("TSK (v3)", "#e06b3a")}
SECUNDARIO, REJILLA = "#555555", "#dddddd"
# Límites nítidos de las regiones latitudinales y de los pisos altitudinales
LIMITES_LATITUD = (13, 27.5, 43, 58.5)
LIMITES_ALTITUD = (1000, 2000, 3000)

# Función auxiliar que aplica el estilo común a unos ejes
def _estilo(ax):
    # Coma decimal en los ejes
    coma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    ax.xaxis.set_major_formatter(coma)
    ax.yaxis.set_major_formatter(coma)
    ax.grid(color=REJILLA, lw=0.6)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)

# Función auxiliar que dibuja la ABT de v1 y v3 al variar una entrada, con un panel por cada valor fijo de la otra
def _paneles(xs, fijos, f_entradas, etiqueta_fijo, limites, xlabel):
    fig, axes = plt.subplots(len(fijos), 1, figsize=(11, 8), sharex=True)
    for ax, fijo in zip(axes, fijos):
        # Curva de cada versión
        for v, (nombre, color) in VERSIONES_FIGURA.items():
            ax.plot(xs, [biotem(*f_entradas(x, fijo), v) for x in xs], color=color, lw=2.2, label=nombre)
        # Límites nítidos dentro del rango dibujado
        for limite in limites:
            if xs[0] < limite < xs[-1]:
                ax.axvline(limite, color=SECUNDARIO, ls=":", lw=1)
        ax.set_title(etiqueta_fijo(fijo), loc="left", fontsize=11, fontweight="bold")
        ax.set_ylabel("ABT inferida (°C)")
        _estilo(ax)
    axes[-1].set_xlabel(xlabel)
    axes[-1].legend(loc="upper center", bbox_to_anchor=(0.5, -0.35), frameon=False, ncol=2)
    return fig

# Función auxiliar que guarda una figura en la carpeta de figuras
def _guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(os.path.join(CARPETA_FIGURAS, nombre), dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)

# Función que genera las figuras de continuidad y de ABT medida frente a inferida
def figuras(est):
    os.makedirs(CARPETA_FIGURAS, exist_ok=True)
    plt.rcParams.update({"font.size": 11})

    # ABT frente a la latitud, con la altitud fija
    fig = _paneles(np.arange(25, 50.01, 0.05), (0, 1000, 2000), lambda x, h: (x, h),
                   lambda h: f"Altitud {h} m", LIMITES_LATITUD,
                   "Latitud |φ| (°)  ·  líneas punteadas: límites de las regiones latitudinales")
    _guardar(fig, "continuidad_latitud.png")

    # ABT frente a la altitud, con la latitud fija
    fig = _paneles(np.arange(0, 3501, 10), (28, 38, 43), lambda x, la: (la, x),
                   lambda la: f"Latitud {la}°", LIMITES_ALTITUD,
                   "Altitud (m)  ·  líneas punteadas: límites de los pisos altitudinales")
    _guardar(fig, "continuidad_altitud.png")

    # ABT medida frente a inferida en las estaciones con datos
    con_datos = est.dropna(subset=["abt_medida"])
    fig, ax = plt.subplots(figsize=(7, 6.5))
    ax.plot([4, 20], [4, 20], color=SECUNDARIO, lw=1, ls=":", label="ABT inferida = ABT medida")
    for (v, (nombre, color)), marcador in zip(VERSIONES_FIGURA.items(), ("o", "s")):
        ax.scatter(con_datos["abt_medida"], con_datos[f"abt_v{v}"], color=color, marker=marcador, s=45,
                   edgecolor="white", lw=1, zorder=3, label=nombre)
    ax.set_xlim(4, 20)
    ax.set_ylim(4, 20)
    ax.set_aspect("equal")
    ax.set_xlabel("Biotemperatura medida (°C)")
    ax.set_ylabel("Biotemperatura inferida (°C)")
    _estilo(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False, ncol=3, fontsize=10)
    _guardar(fig, "medida_inferida.png")

# ===========================================================================
# MAPAS
# ===========================================================================
# Rutas de la paleta, la silueta de España y la carpeta de salida de los mapas
RUTA_PALETA = "PaletaZonasVida.csv"
RUTA_SILUETA = "datos/IGN/gadm41_ESP_1.shp"
CARPETA_MAPAS = "resultados/mapas"
# Versión de Biotem elegida para los mapas
VERSION_MAPAS = 1
# Tamaño de cada punto, para que no queden huecos entre los puntos de la cuadrícula
TAM_PUNTO = 10
# Margen por debajo del cual consideramos ambigua la asignación de un punto
UMBRAL_AMBIGUEDAD = 0.5
# Columnas con el grado de cada zona
COLUMNAS_GRADOS = [f"grado_{c:02d}" for c in range(1, 39)]
# Número de transiciones más frecuentes que se resaltan en la tabla de zonas de vida
N_TRANSICIONES = 4

# Función que dibuja el mapa de zonas de vida y el de ambigüedad con las funciones de la plantilla
def mapas(zonas):
    os.makedirs(CARPETA_MAPAS, exist_ok=True)
    # Cuadrícula encadenada con la versión elegida
    df = zonas[VERSION_MAPAS]
    # Mapa de zonas de vida
    fig = dibujar_mapa_zonas(df, leer_paleta(RUTA_PALETA), ruta_shape=RUTA_SILUETA,
                             archivo=os.path.join(CARPETA_MAPAS, "mapa_zonas.png"), tam=TAM_PUNTO)
    plt.close(fig)
    # Mapa de ambigüedad
    fig = dibujar_mapa_margen(df, ruta_shape=RUTA_SILUETA, archivo=os.path.join(CARPETA_MAPAS, "mapa_ambiguedad.png"),
                              tam=TAM_PUNTO)
    plt.close(fig)

# Función que resume las zonas asignadas en la cuadrícula y las parejas de zonas que compiten en los puntos ambiguos
def resumen_mapas(zonas):
    # Cuadrícula encadenada con la versión elegida
    df = zonas[VERSION_MAPAS]
    # Número y porcentaje de puntos de cada zona
    cuenta = df["zona_codigo"].value_counts()
    resumen = pd.DataFrame({"zona": cuenta.index, "nombre": [NOMBRES_ZONAS[z] for z in cuenta.index],
                            "puntos": cuenta.values, "porcentaje": 100 * cuenta.values / len(df)})
    resumen.to_csv(os.path.join(CARPETA_MAPAS, "zonas.csv"), index=False)

    # Puntos ambiguos y pareja formada por sus dos zonas con más grado
    ambiguos = df[df["zona_margen"] < UMBRAL_AMBIGUEDAD]
    dos_mayores = np.argsort(-ambiguos[COLUMNAS_GRADOS].to_numpy(), axis=1)[:, :2] + 1
    parejas = pd.Series([tuple(sorted(p)) for p in dos_mayores]).value_counts()
    parejas = pd.DataFrame({"zona_1": [p[0] for p in parejas.index], "zona_2": [p[1] for p in parejas.index],
                            "puntos": parejas.values, "porcentaje": 100 * parejas.values / len(ambiguos)})
    parejas.to_csv(os.path.join(CARPETA_MAPAS, "parejas_ambiguas.csv"), index=False)

    # Mostramos el resumen
    print(resumen.round(1).to_string(index=False))
    print(f"   puntos con margen 1: {100 * (df['zona_margen'] == 1).mean():.1f} %")
    print(f"   puntos ambiguos (margen < {UMBRAL_AMBIGUEDAD:g}): {100 * len(ambiguos) / len(df):.1f} %")
    print(parejas.head(10).round(1).to_string(index=False))
    # Puntos sin precipitación, posible fallo de los datos de la cuadrícula
    sin_app = df[df["app"] == 0]
    print(f"   puntos con APP = 0: {len(sin_app)}")
    print(sin_app[["longitud", "latitud", "altitud", "zona_codigo"]].to_string(index=False))
    return parejas

# Función auxiliar que devuelve la fila y la columna de dos celdas vecinas de la tabla de zonas de vida con las zonas a y b
def _celdas_vecinas(a, b):
    celdas = {z: [] for z in (a, b)}
    for i, region in enumerate(TABLA_ZONIFICADOR):
        for j, z in enumerate(TABLA_ZONIFICADOR[region]):
            if z in celdas:
                celdas[z].append((i, j))
    for ca in celdas[a]:
        for cb in celdas[b]:
            if abs(ca[0] - cb[0]) + abs(ca[1] - cb[1]) == 1:
                return ca, cb

# Rangos de precipitación y de biotemperatura que se muestran en la cabecera de la tabla
RANGOS_PRECIPITACION = ["< 125 mm", "125 – 250", "250 – 500", "500 – 1000", "1000 – 2000", "2000 – 4000",
                        "4000 – 8000", "> 8000 mm"]
RANGOS_BIOTEMPERATURA = ["< 1,5 °C", "1,5 – 3 °C", "3 – 6 °C", "6 – 12 °C", "12 – 18 °C", "18 – 24 °C", "> 24 °C"]
# Color de cada región de biotemperatura en la tabla
COLORES_REGIONES = ["#3b6db3", "#5aa3c8", "#2a9d8f", "#7ab648", "#e0a93b", "#e07040", "#c8384e"]
# Tamaño de las celdas de la tabla y separación entre ellas
ANCHO_ETIQUETA, ALTO_CABECERA, HUECO = 1.25, 0.6, 0.06

# Función auxiliar que aclara un color mezclándolo con blanco
def _aclarar(color, f):
    return tuple(1 - f * (1 - np.array(color)))

# Función auxiliar que dibuja una celda redondeada con una barra de color en el borde
def _celda(ax, x, y, ancho, alto, fondo, barra=None, lado="abajo", alpha=1):
    ax.add_patch(FancyBboxPatch((x, y), ancho, alto, boxstyle="round,pad=0,rounding_size=0.04",
                                facecolor=fondo, edgecolor="none", alpha=alpha))
    if barra is not None:
        rect = (x, y + alto - 0.05, ancho, 0.05) if lado == "abajo" else (x, y, 0.05, alto)
        ax.add_patch(plt.Rectangle(rect[:2], *rect[2:], facecolor=barra, edgecolor="none", alpha=alpha))

# Función que dibuja la tabla de zonas de vida resaltando las transiciones más frecuentes (T1, T2, ...)
def figura_transiciones(parejas):
    paleta = leer_paleta(RUTA_PALETA)
    regiones = list(TABLA_ZONIFICADOR)
    # Celdas vecinas de cada una de las transiciones más frecuentes
    transiciones = [_celdas_vecinas(a, b) for a, b in parejas.head(N_TRANSICIONES)[["zona_1", "zona_2"]].to_numpy()]
    resaltadas = {TABLA_ZONIFICADOR[regiones[i]][j] for t in transiciones for i, j in t}
    # Posición de cada columna y de cada fila
    x0 = lambda j: ANCHO_ETIQUETA + HUECO + j
    y0 = lambda i: ALTO_CABECERA + HUECO + i
    fig, ax = plt.subplots(figsize=(16, 10))

    # Cabecera con los niveles de precipitación
    ax.text(ANCHO_ETIQUETA / 2, ALTO_CABECERA / 2, "Biotemperatura ↓\nPrecipitación →", ha="center", va="center",
            fontsize=10, style="italic", color=SECUNDARIO)
    for j, (nivel, rango) in enumerate(zip(PRECIPITACIONES, RANGOS_PRECIPITACION)):
        _celda(ax, x0(j) + HUECO / 2, 0, 1 - HUECO, ALTO_CABECERA, "#efefef")
        nivel = nivel.replace("Extremadamente", "Extr.")
        ax.text(x0(j) + 0.5, 0.22, nivel, ha="center", va="center", fontsize=9.5, fontweight="bold")
        ax.text(x0(j) + 0.5, 0.43, rango, ha="center", va="center", fontsize=9, color=SECUNDARIO)
    ax.plot([0, x0(len(PRECIPITACIONES))], [ALTO_CABECERA + HUECO / 2] * 2, color="#444444", lw=1.5)

    # Una fila por región de biotemperatura
    for i, region in enumerate(regiones):
        # Etiqueta de la región, con su color en el borde izquierdo
        _celda(ax, 0, y0(i) + HUECO / 2, ANCHO_ETIQUETA, 1 - HUECO, _aclarar(to_rgb(COLORES_REGIONES[i]), 0.12),
               COLORES_REGIONES[i], lado="izquierda")
        ax.text(0.12, y0(i) + 0.38, region, ha="left", va="center", fontsize=11, fontweight="bold")
        ax.text(0.12, y0(i) + 0.68, RANGOS_BIOTEMPERATURA[i], ha="left", va="center", fontsize=9, color=SECUNDARIO)
        # Zonas de la fila, uniendo las celdas consecutivas de la misma zona
        fila, j = TABLA_ZONIFICADOR[region], 0
        while j < len(fila):
            z, ancho = fila[j], 1
            while j + ancho < len(fila) and fila[j + ancho] == z:
                ancho += 1
            activa = z in resaltadas
            _celda(ax, x0(j) + HUECO / 2, y0(i) + HUECO / 2, ancho - HUECO, 1 - HUECO, _aclarar(paleta[z], 0.45),
                   paleta[z], alpha=1 if activa else 0.3)
            color_texto = "black" if activa else "#999999"
            nombre = textwrap.fill(NOMBRES_ZONAS[z], 16 if ancho == 1 else 40)
            ax.text(x0(j) + ancho / 2, y0(i) + 0.33, z, ha="center", va="center", fontsize=12, fontweight="bold",
                    color=color_texto)
            ax.text(x0(j) + ancho / 2, y0(i) + 0.48, nombre, ha="center", va="top", fontsize=8, color=color_texto,
                    linespacing=1)
            j += ancho

    # Flecha y etiqueta de cada transición, cruzando el borde entre sus dos celdas
    for k, ((ia, ja), (ib, jb)) in enumerate(transiciones, start=1):
        # Transición vertical (biotemperatura): flecha entre filas, con la etiqueta a la derecha
        if ja == jb:
            x, y = x0(ja) + 0.5, y0(max(ia, ib))
            inicio, fin, etiqueta = (x, y - 0.2), (x, y + 0.2), (x + 0.1, y)
        # Transición horizontal (precipitación): flecha entre columnas, bajo los nombres, con la etiqueta a la izquierda
        else:
            x, y = x0(max(ja, jb)), y0(ia) + 0.85
            inicio, fin, etiqueta = (x - 0.25, y), (x + 0.25, y), (x - 0.5, y)
        ax.annotate("", xy=fin, xytext=inicio, arrowprops=dict(arrowstyle="<->", color="black", lw=2))
        ax.text(*etiqueta, f"T{k}", ha="left", va="center", fontsize=10, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="black", lw=1.2))

    ax.set_xlim(0, x0(len(PRECIPITACIONES)))
    ax.set_ylim(y0(len(regiones)), 0)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(CARPETA_MAPAS, "tabla_transiciones.png"), dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)

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
    # Generamos las figuras
    figuras(est)
    print(f"\nFiguras guardadas en {CARPETA_FIGURAS}")
    # Dibujamos los mapas con la versión elegida y resumimos las zonas de la cuadrícula
    mapas(zonas)
    print(f"\nMapas guardados en {CARPETA_MAPAS} (versión {VERSION_MAPAS}). Resumen de la cuadrícula:")
    parejas = resumen_mapas(zonas)
    # Dibujamos la tabla de zonas de vida con las transiciones más frecuentes
    figura_transiciones(parejas)

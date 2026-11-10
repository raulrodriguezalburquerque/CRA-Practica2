"""
Funciones para colorear los mapas del Informe 2.

Este módulo está terminado: NO hace falta modificarlo.
  - leer_paleta(): lee PaletaZonasVida.csv (código -> color RGB).
  - color_zonas(...): color de un punto mezclando en CIELAB sus dos zonas con más grado.
  - dibujar_mapa_zonas(...) y dibujar_mapa_margen(...): dibujan los dos mapas obligatorios.
"""
import csv
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Paleta
# ---------------------------------------------------------------------------
def leer_paleta(ruta="PaletaZonasVida.csv"):
    """Devuelve {código: (R, G, B)} con valores entre 0 y 1."""
    paleta = {}
    with open(ruta, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            paleta[int(fila["codigo"])] = tuple(int(fila[c]) / 255 for c in ("R", "G", "B"))
    return paleta

# ---------------------------------------------------------------------------
# Conversión sRGB <-> CIELAB (iluminante D65), con NumPy
# ---------------------------------------------------------------------------
_M = np.array([[0.4124564, 0.3575761, 0.1804375],
               [0.2126729, 0.7151522, 0.0721750],
               [0.0193339, 0.1191920, 0.9503041]])
_MINV = np.linalg.inv(_M)
_BLANCO = np.array([0.95047, 1.0, 1.08883])

def rgb_a_lab(rgb):
    rgb = np.asarray(rgb, dtype=float)
    lineal = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    xyz = lineal @ _M.T / _BLANCO
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)

def lab_a_rgb(lab):
    lab = np.asarray(lab, dtype=float)
    fy = (lab[..., 0] + 16) / 116
    f = np.stack([fy + lab[..., 1] / 500, fy, fy - lab[..., 2] / 200], axis=-1)
    xyz = np.where(f > 6 / 29, f ** 3, 3 * (6 / 29) ** 2 * (f - 4 / 29)) * _BLANCO
    lineal = xyz @ _MINV.T
    rgb = np.where(lineal <= 0.0031308, 12.92 * lineal, 1.055 * np.clip(lineal, 0, None) ** (1 / 2.4) - 0.055)
    return np.clip(rgb, 0, 1)

# ---------------------------------------------------------------------------
# Color de un punto
# ---------------------------------------------------------------------------
def color_zonas(grados, paleta):
    """
    grados: {código de zona: grado} (por ejemplo, las columnas grado_01 ... grado_38 de un punto).
    Mezcla en CIELAB los colores de las dos zonas con mayor grado, ponderados por esos grados.
    """
    (z1, g1), (z2, g2) = sorted(grados.items(), key=lambda kv: kv[1], reverse=True)[:2]
    if g1 + g2 == 0:
        return (1.0, 1.0, 1.0)            # ninguna regla disparada: blanco
    lab = (g1 * rgb_a_lab(paleta[z1]) + g2 * rgb_a_lab(paleta[z2])) / (g1 + g2)
    return tuple(lab_a_rgb(lab))

def grados_de_fila(fila):
    """Extrae {código: grado} de una fila con columnas grado_01 ... grado_38."""
    return {c: float(fila[f"grado_{c:02d}"]) for c in range(1, 39)}

# ---------------------------------------------------------------------------
# Mapas
# ---------------------------------------------------------------------------
def _silueta(ax, ruta_shape):
    if ruta_shape:
        import geopandas as gpd           # solo si se dibuja la silueta de España
        gpd.read_file(ruta_shape).boundary.plot(ax=ax, color="black", linewidth=0.5)

def dibujar_mapa_zonas(df, paleta, ruta_shape=None, archivo="mapa_zonas.png", tam=6):
    """df: resultados del Zonificador con columnas longitud, latitud y grado_01 ... grado_38."""
    colores = [color_zonas(grados_de_fila(f), paleta) for _, f in df.iterrows()]
    fig, ax = plt.subplots(figsize=(9, 7))
    _silueta(ax, ruta_shape)
    ax.scatter(df["longitud"], df["latitud"], c=colores, s=tam, marker="s", linewidths=0)
    ax.set_title("Zonas de vida (mezcla en CIELAB de las dos zonas con más grado)")
    ax.set_aspect("equal"); ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
    fig.savefig(archivo, dpi=200, bbox_inches="tight")
    return fig

def dibujar_mapa_margen(df, ruta_shape=None, archivo="mapa_margen.png", tam=6, columna="zona_margen"):
    """Mapa de ambigüedad: más claro cuanto menor es el margen (zonas que compiten)."""
    fig, ax = plt.subplots(figsize=(9, 7))
    _silueta(ax, ruta_shape)
    sc = ax.scatter(df["longitud"], df["latitud"], c=df[columna], cmap="Blues", vmin=0, vmax=1,
                    s=tam, marker="s", linewidths=0)
    fig.colorbar(sc, ax=ax, label="Margen entre las dos zonas con más grado")
    ax.set_title("Ambigüedad de la asignación")
    ax.set_aspect("equal"); ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
    fig.savefig(archivo, dpi=200, bbox_inches="tight")
    return fig

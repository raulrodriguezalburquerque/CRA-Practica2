"""
Lectura de los datos del Informe 2 y cálculo de la ABT y la APP de las estaciones.

Este módulo está terminado: NO hace falta modificarlo.
  - leer_estaciones("LISTA-ESTACIONES.csv")
  - leer_cuadricula("DATOS-CUADRICULA.csv")
  - leer_mensuales("ID_municipio_fechaIni_fechaFin.csv")
  - abt_app(df_mensual): biotemperatura y precipitación media anual de una estación.
Todas las tablas devueltas usan los nombres de columna longitud, latitud, altitud (y app).
"""
import io
import pandas as pd

def _numero(x):
    """Convierte '42,75', '-7.51' o 42.75 en número (los decimales vienen mezclados)."""
    return float(str(x).strip().replace(",", "."))

def leer_estaciones(ruta="LISTA-ESTACIONES.csv"):
    df = pd.read_csv(ruta, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"Identificador": "id", "Provincia": "provincia", "Municipio": "municipio",
                            "Latitud": "latitud", "Longitud": "longitud", "Altitud": "altitud"})
    for c in ("latitud", "longitud", "altitud"):
        df[c] = df[c].map(_numero)
    return df[["id", "provincia", "municipio", "longitud", "latitud", "altitud"]]

def leer_cuadricula(ruta="DATOS-CUADRICULA.csv"):
    df = pd.read_csv(ruta, sep=";", decimal=",")
    return df.rename(columns={"X": "longitud", "Y": "latitud", "ELEVA": "altitud", "PRECIPITA": "app"})

def leer_mensuales(ruta):
    """Los archivos de datos climáticos están codificados en UTF-16, con ';' y coma decimal."""
    with open(ruta, "rb") as f:
        texto = f.read().decode("utf-16")
    return pd.read_csv(io.StringIO(texto), sep=";", decimal=",")

def abt_app(df, col_temp="Temp Media (ºC)", col_prec="Precipitación (mm)"):
    """
    ABT: media de las temperaturas medias mensuales, recortadas a [0, 30] °C.
    APP: media, a lo largo de los años, de la precipitación TOTAL de cada año
         (suma de las mensuales; no la media de las mensuales).
    Solo se usan los años completos (12 meses): un año a medias falsearía la APP.
    Devuelve (abt, app, años_usados).
    """
    meses = df.groupby("Año")["Mes"].count()
    completos = meses[meses == 12].index
    d = df[df["Año"].isin(completos)]
    abt = d[col_temp].clip(0, 30).mean()
    app = d.groupby("Año")[col_prec].sum().mean()
    return float(abt), float(app), list(completos)

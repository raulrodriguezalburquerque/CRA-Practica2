"""
Motor de inferencia difusa para el Informe 2 de CRA (Tema 3).

Este módulo está terminado y probado: NO hace falta modificarlo.
Contiene las piezas genéricas (funciones de pertenencia, triplas, inferencia
Mamdani y TSK, clasificador difuso, defuzzificadores y procesamiento de CSV).
Vuestra especificación va en el archivo sistemas.py.
"""
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Funciones de pertenencia
# ---------------------------------------------------------------------------
def trapecio(x, a, b, c, d):
    """Trapecio (a, b, c, d). Con a == b o c == d se obtiene un hombro."""
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)
    y = np.where((x >= b) & (x <= c), 1.0, y)
    if b > a:
        y = np.where((x > a) & (x < b), (x - a) / (b - a), y)
    if d > c:
        y = np.where((x > c) & (x < d), (d - x) / (d - c), y)
    return y

def triangulo(x, a, b, c):
    return trapecio(x, a, b, b, c)

def gaussiana(x, m, s):
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * ((x - m) / s) ** 2)

FAMILIAS = {"trapecio": trapecio, "triangulo": triangulo, "gaussiana": gaussiana}

# ---------------------------------------------------------------------------
# Variables lingüísticas
# ---------------------------------------------------------------------------
class VariableLinguistica:
    """
    nombre: nombre de la variable.
    universo: (mínimo, máximo) en la escala en la que se definen las etiquetas.
    etiquetas: {nombre_etiqueta: (familia, [parámetros])}.
    transformacion: None o una función que se aplica a la entrada antes de
        calcular los grados (por ejemplo, np.log2). Los parámetros y el
        universo se expresan en la escala transformada.
    Las entradas fuera del universo se saturan a sus extremos.
    """
    def __init__(self, nombre, universo, etiquetas, transformacion=None):
        self.nombre = nombre
        self.universo = universo
        self.etiquetas = etiquetas
        self.transformacion = transformacion

    def preparar(self, valor):
        v = self.transformacion(valor) if self.transformacion else valor
        return float(np.clip(v, self.universo[0], self.universo[1]))

    def grado(self, valor, etiqueta):
        familia, params = self.etiquetas[etiqueta]
        return float(FAMILIAS[familia](self.preparar(valor), *params))

    def grados(self, valor):
        return {e: self.grado(valor, e) for e in self.etiquetas}

    def funcion(self, etiqueta, puntos):
        """Función de pertenencia evaluada en un vector de puntos (para la salida)."""
        familia, params = self.etiquetas[etiqueta]
        return FAMILIAS[familia](puntos, *params)

# ---------------------------------------------------------------------------
# Triplas De Morgan
# ---------------------------------------------------------------------------
TRIPLAS = {
    "zadeh":       {"Y": min, "O": max, "NO": lambda x: 1 - x},
    "algebraica":  {"Y": lambda x, y: x * y, "O": lambda x, y: x + y - x * y, "NO": lambda x: 1 - x},
    "lukasiewicz": {"Y": lambda x, y: max(0.0, x + y - 1), "O": lambda x, y: min(1.0, x + y), "NO": lambda x: 1 - x},
}

# ---------------------------------------------------------------------------
# Antecedentes: proposiciones simples y compuestas
#   ("es", "variable", "etiqueta")
#   ("Y", p, q, ...)   ("O", p, q, ...)   ("NO", p)
# ---------------------------------------------------------------------------
def es(variable, etiqueta):
    return ("es", variable, etiqueta)

def Y(*ps):
    return ("Y",) + ps

def O(*ps):
    return ("O",) + ps

def NO(p):
    return ("NO", p)

def grado_de_verdad(prop, entradas, variables, tripla="zadeh"):
    """Grado de verdad de una proposición para unos valores de entrada."""
    op = prop[0]
    T = TRIPLAS[tripla]
    if op == "es":
        _, var, etq = prop
        return variables[var].grado(entradas[var], etq)
    if op == "NO":
        return T["NO"](grado_de_verdad(prop[1], entradas, variables, tripla))
    grados = [grado_de_verdad(p, entradas, variables, tripla) for p in prop[1:]]
    g = grados[0]
    for h in grados[1:]:
        g = T[op](g, h)
    return g

# ---------------------------------------------------------------------------
# Defuzzificadores (sobre el universo de salida discretizado)
# ---------------------------------------------------------------------------
def defuzzificar(y, mu, metodo="centroide"):
    if mu.sum() == 0:
        raise ValueError("Conjunto agregado vacío: ninguna regla se ha disparado (¿base de reglas incompleta?).")
    if metodo == "centroide":
        return float((y * mu).sum() / mu.sum())
    if metodo == "bisectriz":
        acumulado = np.cumsum(mu)
        return float(y[np.searchsorted(acumulado, acumulado[-1] / 2)])
    maximos = y[np.isclose(mu, mu.max())]
    if metodo == "som":
        return float(maximos.min())
    if metodo == "lom":
        return float(maximos.max())
    if metodo == "mom":
        return float(maximos.mean())
    raise ValueError(f"Defuzzificador desconocido: {metodo}")

# ---------------------------------------------------------------------------
# Inferencia Mamdani
#   reglas: lista de (antecedente, etiqueta_de_salida)
# ---------------------------------------------------------------------------
def inferir_mamdani(entradas, variables, reglas, salida, tripla="zadeh",
                    implicacion="mamdani", defuzzificador="centroide", puntos=1001):
    y = np.linspace(salida.universo[0], salida.universo[1], puntos)
    agregado = np.zeros_like(y)
    traza = []
    for i, (ante, etq) in enumerate(reglas, start=1):
        alfa = grado_de_verdad(ante, entradas, variables, tripla)     # grado de disparo
        consecuente = salida.funcion(etq, y)
        if implicacion == "mamdani":
            conclusion = np.minimum(alfa, consecuente)
        elif implicacion == "larsen":
            conclusion = alfa * consecuente
        else:
            raise ValueError(f"Implicación desconocida: {implicacion}")
        agregado = np.maximum(agregado, conclusion)                  # agregación (máximo)
        traza.append({"regla": i, "consecuente": etq, "grado_disparo": alfa})
    valor = defuzzificar(y, agregado, defuzzificador)
    return valor, {"reglas": traza, "universo": y, "agregado": agregado}

# ---------------------------------------------------------------------------
# Inferencia TSK
#   reglas: lista de (antecedente, funcion_consecuente)
#   funcion_consecuente(entradas) -> número  (orden 0: constante; orden 1: lineal)
# ---------------------------------------------------------------------------
def inferir_tsk(entradas, variables, reglas, tripla="zadeh"):
    pesos, salidas, traza = [], [], []
    for i, (ante, f) in enumerate(reglas, start=1):
        alfa = grado_de_verdad(ante, entradas, variables, tripla)
        valor = float(f(entradas))
        pesos.append(alfa)
        salidas.append(valor)
        traza.append({"regla": i, "grado_disparo": alfa, "salida_regla": valor})
    pesos = np.array(pesos)
    if pesos.sum() == 0:
        raise ValueError("Ninguna regla se ha disparado (¿base de reglas incompleta?).")
    return float((pesos * np.array(salidas)).sum() / pesos.sum()), {"reglas": traza}

# ---------------------------------------------------------------------------
# Clasificador difuso
#   reglas: lista de (antecedente, clase)
#   metodo: "maximo" (regla ganadora) o "suma" (suma normalizada de grados)
# ---------------------------------------------------------------------------
def clasificar(entradas, variables, reglas, clases, tripla="zadeh", metodo="maximo"):
    grados = {c: 0.0 for c in clases}
    traza = []
    for i, (ante, clase) in enumerate(reglas, start=1):
        alfa = grado_de_verdad(ante, entradas, variables, tripla)
        if metodo == "maximo":
            grados[clase] = max(grados[clase], alfa)
        elif metodo == "suma":
            grados[clase] += alfa
        else:
            raise ValueError(f"Método desconocido: {metodo}")
        traza.append({"regla": i, "clase": clase, "grado_disparo": alfa})
    if metodo == "suma":
        total = sum(grados.values())
        if total > 0:
            grados = {c: g / total for c, g in grados.items()}
    ganadora = max(grados, key=grados.get)
    return ganadora, grados[ganadora], grados, {"reglas": traza}

# ---------------------------------------------------------------------------
# Traza legible
# ---------------------------------------------------------------------------
def mostrar_traza(traza, solo_disparadas=True):
    for r in traza["reglas"]:
        if solo_disparadas and r["grado_disparo"] == 0:
            continue
        print("  ", ", ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}" for k, v in r.items()))

# ---------------------------------------------------------------------------
# Procesamiento por lotes de un CSV
# ---------------------------------------------------------------------------
def procesar_csv(entrada, salida, funcion, columnas_entrada, **opciones):
    """
    Aplica funcion(*valores_de_columnas_entrada, **opciones) a cada fila.
    La función debe devolver un diccionario {columna_de_salida: valor}.
    """
    df = pd.read_csv(entrada)
    resultados = [funcion(*[fila[c] for c in columnas_entrada], **opciones) for _, fila in df.iterrows()]
    df = pd.concat([df, pd.DataFrame(resultados)], axis=1)
    df.to_csv(salida, index=False)
    return df

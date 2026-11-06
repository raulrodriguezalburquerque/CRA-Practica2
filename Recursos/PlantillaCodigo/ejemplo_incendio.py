"""
Ejemplo de uso del motor con el sistema de riesgo de incendio de las
diapositivas de la Teoría 2. Sirve para comprobar que el motor funciona
y para ver cómo se escriben variables y reglas.

Valores esperados (Teoría 2, humedad 42 % y viento 19 km/h):
  grados de disparo 0,3 / 0,7 / 0,6 ; centroide 4,38 ; media ponderada 4,25
"""
from motor_difuso import (VariableLinguistica, es, Y, O, inferir_mamdani,
                          inferir_tsk, clasificar, mostrar_traza)

humedad = VariableLinguistica("humedad", (0, 100), {
    "seca":     ("trapecio", [0, 0, 35, 45]),
    "moderada": ("trapecio", [35, 45, 65, 75]),
    "humeda":   ("trapecio", [65, 75, 100, 100]),
})
viento = VariableLinguistica("viento", (0, 50), {
    "flojo":  ("trapecio", [0, 0, 15, 25]),
    "fuerte": ("trapecio", [15, 25, 50, 50]),
})
riesgo = VariableLinguistica("riesgo", (0, 10), {
    "bajo":  ("trapecio", [0, 0, 2, 4]),
    "medio": ("triangulo", [2, 5, 8]),
    "alto":  ("trapecio", [6, 8, 10, 10]),
})
variables = {"humedad": humedad, "viento": viento}

reglas = [
    (Y(es("humedad", "seca"), es("viento", "fuerte")), "alto"),    # R1
    (es("humedad", "moderada"), "medio"),                         # R2
    (O(es("humedad", "humeda"), es("viento", "flojo")), "bajo"),  # R3
]
entradas = {"humedad": 42, "viento": 19}

valor, traza = inferir_mamdani(entradas, variables, reglas, riesgo, puntos=10001)
print(f"Mamdani + centroide: {valor:.2f}")
mostrar_traza(traza)
for d in ["bisectriz", "som", "mom", "lom"]:
    v, _ = inferir_mamdani(entradas, variables, reglas, riesgo, defuzzificador=d, puntos=10001)
    print(f"  {d}: {v:.2f}")

# El mismo sistema como TSK de orden 0 (consecuentes = centros de alto, medio y bajo: 9, 5, 1)
reglas_tsk = [(a, (lambda e, c=c: c)) for (a, _), c in zip(reglas, [9, 5, 1])]
v, _ = inferir_tsk(entradas, variables, reglas_tsk)
print(f"TSK orden 0 (media ponderada de centros): {v:.2f}")

# Un clasificador difuso con las mismas reglas: la clase es la etiqueta de riesgo
clase, grado, grados, _ = clasificar(entradas, variables, reglas, ["bajo", "medio", "alto"])
print(f"Clasificador (regla ganadora): {clase} con grado {grado:.2f}; todos: {grados}")

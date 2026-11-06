# Plantilla de código · Informe 2 (CRA, Tema 3)

## Archivos

| Archivo | Qué es | ¿Hay que tocarlo? |
|---|---|---|
| `motor_difuso.py` | Motor genérico: funciones de pertenencia, triplas, inferencia Mamdani y TSK, clasificador difuso, defuzzificadores, traza y procesamiento de CSV. | No. |
| `ejemplo_incendio.py` | El sistema de riesgo de incendio de la Teoría 2, ya programado. Sirve para comprobar que todo funciona y para ver el formato de variables y reglas. | No. Ejecutadlo primero. |
| `sistemas.py` | Biotem (versión Mamdani con base canónica y no canónica, y segunda versión) y el Zonificador, con la interfaz del enunciado. | **Sí:** completad las partes marcadas con `TODO`. |
| `datos.py` | Lectura de las estaciones, la cuadrícula y los datos mensuales (en UTF-16), y cálculo de la ABT y la APP de cada estación. | No. |
| `mapas.py` | Mezcla de colores en CIELAB y dibujo de los dos mapas (zonas de vida y ambigüedad). | No. |
| `PaletaZonasVida.csv` | Paleta de colores de las 38 zonas de vida (Tabla 1 del documento de Coloreado de Mapas). | No. |

Requisitos: Python 3, `numpy`, `pandas` y `matplotlib`; `geopandas` solo para dibujar la silueta de España.

## Cómo empezar

1. Ejecutad `python ejemplo_incendio.py`. Debe dar un centroide de 4,38 y los demás valores de las diapositivas de la Teoría 2.
2. Copiad vuestra especificación (Sección 1.1 del informe) en `sistemas.py`: variables, etiquetas con sus parámetros, reglas y mecanismo de inferencia.
3. Verificad con vuestros cálculos a mano (Sección 1.2.2): `biotem(42.75, 971, v, traza=True)` con v = 1, 2 o 3 muestra el grado de disparo de cada regla.
4. Procesad los CSV con `procesar_csv` (hay ejemplos al final de `sistemas.py`).
5. Para las estaciones, calculad la biotemperatura y la precipitación medidas con `abt_app` de `datos.py`. Solo usa años completos: un año a medias (como 2024 en los archivos) falsearía la precipitación anual.
6. Dibujad los mapas con `dibujar_mapa_zonas` y `dibujar_mapa_margen` de `mapas.py`. El primero colorea cada punto mezclando, en el espacio de color CIELAB, los colores de sus dos zonas con mayor grado; el segundo representa el margen.

## Cómo se escriben las reglas

- Proposición simple: `es("latitud", "templada fría")`
- Conectivas: `Y(p, q)`, `O(p, q)`, `NO(p)`. Se pueden anidar: `Y(O(p, q), NO(r))`.
- Regla Mamdani: `(antecedente, "etiqueta de salida")`
- Regla TSK: `(antecedente, lambda e: ... )`, donde `e["nombre_de_variable"]` da el valor de cada entrada.
- Regla del Zonificador: `(antecedente, código de zona)`

## Programar con ayuda de una IA

Se permite usar herramientas de IA, pero el grupo es responsable del código y debe poder explicarlo. Recomendaciones:

1. **Especificad primero, implementad después.** Una IA no puede saber qué etiquetas, parámetros y reglas habéis decidido: dádselos explícitamente (por ejemplo, pegando vuestra tabla de especificación).
2. **Pedid cambios concretos y pequeños**, sobre `sistemas.py`, sin modificar `motor_difuso.py`.
3. **Verificad siempre con los cálculos a mano.** Si el código y el cálculo no coinciden, el error puede estar en cualquiera de los dos: buscad la causa antes de cambiar nada.
4. **No aceptéis código que no entendáis.** En el informe tendréis que justificar cada decisión.

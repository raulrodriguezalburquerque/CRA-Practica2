# CRA · Informe 2: Biotem y Zonificador

Sistemas de inferencia difusos para la clasificación bioclimática de Holdridge
(Conocimiento y Razonamiento Aproximado, Máster en IA, Universidad de Murcia):

- **Biotem**: estima la biotemperatura media anual (ABT) a partir de la latitud y la altitud.
- **Zonificador**: asigna la zona de vida de Holdridge (1–38) a partir de la ABT y la precipitación anual (APP).

## Instalación

Requisitos: **Python 3.12** (o superior) y `git`.

```bash
git clone https://github.com/raulrodriguezalburquerque/CRA-Practica2.git
cd CRA-Practica2
```

Crear el entorno virtual e instalar las dependencias:

**Windows (PowerShell)**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

**Linux / macOS**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Para activar el entorno y usar directamente `python`:

- Windows: `.venv\Scripts\Activate.ps1` (si PowerShell lo bloquea, ejecutar antes
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, o usar siempre `.venv\Scripts\python`).
- Linux / macOS: `source .venv/bin/activate`

## Estructura

| Ruta | Contenido |
|---|---|
| `sistemas.py` | Punto de entrada: `biotem()`, `zonify()` y pruebas. |
| `explotacion.py` | Aplicación de los sistemas a las estaciones y a la cuadrícula, con métricas y comparativas. |
| `comun.py` | Elementos compartidos por Biotem y el Zonificador (tripla y biotemperatura). |
| `biotem/` | Biotem: elementos comunes (`comun.py`) y las tres versiones (`canonica.py`, `no_canonica.py`, `tsk.py`). |
| `zonificador/` | Zonificador: variables, tabla y nombres de zonas (`comun.py`) y reglas e inferencia (`clasificador.py`). |
| `motor_difuso.py` | Motor de inferencia difusa de la plantilla (no se modifica). |
| `datos.py` | Lectura de estaciones, cuadrícula y datos mensuales; cálculo de ABT y APP. |
| `mapas.py` | Dibujo de los mapas de zonas de vida y de ambigüedad. |
| `PaletaZonasVida.csv` | Códigos, nombres y colores de las 38 zonas de vida. |
| `datos/` | Estaciones, datos climáticos mensuales, cuadrícula de España y silueta (IGN). |
| `resultados/` | CSV de salida: estaciones y métricas en la raíz, y cuadrícula separada por sistema en `biotem/` y `zonificador/`. |
| `Recursos/` | Material original proporcionado por la asignatura (sin modificar). |

Todos los scripts se ejecutan desde la raíz del repositorio.

## Ejecución

Trazas de verificación de las estaciones BU02, P01 y BA05 (Biotem en sus tres versiones y Zonificador
con la ABT y la APP medidas):

```bash
.venv/Scripts/python sistemas.py
```

Explotación sobre las estaciones y la cuadrícula:

```bash
.venv/Scripts/python explotacion.py
```

Genera:

- `resultados/estaciones.csv`: ABT y APP medidas (años completos), ABT inferida por cada versión, su error y la zona
  asignada con la ABT medida y con la inferida. TE01 y SP01 no tienen datos mensuales, así que solo llevan la ABT inferida.
- `resultados/metricas_estaciones.csv`: sesgo, MAE, RMSE, error máximo y coincidencia de zona de cada versión.
- `resultados/biotem/cuadricula.csv`: ABT inferida por cada versión en los puntos de la cuadrícula.
- `resultados/zonificador/cuadricula_v1.csv` y `cuadricula_v3.csv`: cadena Biotem → Zonificador con la versión 1 y la 3
  (la versión 2 da los mismos resultados que la 1).

Procesamiento por lotes de un CSV (separado por comas, con punto decimal):

```bash
.venv/Scripts/python sistemas.py biotem entrada.csv resultados/biotem/salida.csv
.venv/Scripts/python sistemas.py zonify entrada.csv resultados/zonificador/salida.csv
```

- `biotem` necesita las columnas `latitud` y `altitud`, y añade `abt_v1`, `abt_v2` y `abt_v3`.
- `zonify` necesita las columnas `abt` y `app`, y añade `zona_codigo`, `zona_nombre`, `zona_grado`,
  `zona_margen` y `grado_01` a `grado_38`.

Desde Python también se pueden usar directamente:

```python
from sistemas import biotem, zonify, biotem_csv, zonify_csv
biotem(42.75, 971, 1, traza=True)   # versión 1, 2 o 3
zonify(15.2, 640, traza=True)
```

(En Linux / macOS, `.venv/bin/python` en lugar de `.venv/Scripts/python`.)

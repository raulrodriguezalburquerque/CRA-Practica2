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
| `sistemas.py` | Especificación e implementación de Biotem y del Zonificador. |
| `motor_difuso.py` | Motor de inferencia difusa de la plantilla (no se modifica). |
| `datos.py` | Lectura de estaciones, cuadrícula y datos mensuales; cálculo de ABT y APP. |
| `mapas.py` | Dibujo de los mapas de zonas de vida y de ambigüedad. |
| `PaletaZonasVida.csv` | Códigos, nombres y colores de las 38 zonas de vida. |
| `datos/` | Estaciones, datos climáticos mensuales, cuadrícula de España y silueta (IGN). |
| `Recursos/` | Material original proporcionado por la asignatura (sin modificar). |

Todos los scripts se ejecutan desde la raíz del repositorio.

## Ejecución

*(Pendiente: se completará al implementar los sistemas.)*

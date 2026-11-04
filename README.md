# Proyecto Red — ADAG2

Implementación académica de algoritmos de optimización para un problema de selección de nodos y asignación discreta de presupuesto, con simulación por rondas, fallos y efectos de vecindad.

El repositorio reúne algoritmos voraces, verificadores exactos para instancias pequeñas y experimentos reproducibles. Los datos de los experimentos son sintéticos y sirven para estudiar el comportamiento de las implementaciones; no representan por sí solos resultados de un sistema real.

## Contenido

- [Objetivo y alcance](#objetivo-y-alcance)
- [Algoritmos implementados](#algoritmos-implementados)
- [Modelo y supuestos](#modelo-y-supuestos)
- [Requisitos](#requisitos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Pruebas](#pruebas)
- [Experimentos](#experimentos)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Complejidad](#complejidad)
- [Limitaciones](#limitaciones)
- [Análisis teórico](#análisis-teórico)

## Objetivo y alcance

El proyecto estudia dos decisiones relacionadas:

1. **Selección de nodos:** escoger hasta un número determinado de nodos para maximizar la cobertura de elementos.
2. **Asignación de presupuesto:** distribuir unidades discretas entre los nodos seleccionados para maximizar la suma de sus utilidades.

Además, se incluye una simulación de varias rondas. En ella pueden ocurrir fallos de nodos y la asignación de una ronda puede influir en las ganancias marginales de sus vecinos en la ronda siguiente.

## Algoritmos implementados

| Módulo | Algoritmo | Propósito |
|---|---|---|
| `src/allocation.py` | `greedy_allocate` | Reparto discreto mediante un max-heap. Es óptimo bajo la hipótesis de ganancias marginales no crecientes. |
| `src/allocation.py` | `brute_force_allocate` | Verificador exacto por enumeración para instancias pequeñas. |
| `src/selection.py` | `greedy_max_coverage` | Selección voraz para Maximum Coverage con restricción de cardinalidad. |
| `src/selection.py` | `exact_max_coverage` | Solución exacta por enumeración para comparar instancias pequeñas. |
| `src/selection.py` | `greedy_budgeted_coverage` | Heurística basada en ganancia marginal/costo para la variante con presupuesto. |
| `src/simulation.py` | `run_rounds` | Simulación temporal de selección, asignación, fallos y efectos de vecindad. |

## Modelo y supuestos

- El presupuesto de asignación se expresa en **unidades enteras**.
- Cada nodo tiene una secuencia de ganancias marginales no negativas y no crecientes. Esta condición representa una utilidad discreta cóncava.
- En Maximum Coverage, cada nodo representa un conjunto de elementos y la utilidad es el tamaño de la unión de los conjuntos seleccionados.
- En la simulación, cada nodo falla de manera independiente con una probabilidad fija por ronda. Los nodos que fallan no participan en esa ronda.
- La asignación de una ronda modifica las ganancias marginales base de los vecinos en la ronda siguiente mediante un factor de influencia. La semilla aleatoria permite repetir los mismos escenarios sintéticos.
- Los generadores de instancias reciben una semilla para facilitar la reproducibilidad.

Estos supuestos describen el modelo computacional utilizado en esta implementación. Si el enunciado del proyecto define otra interpretación para los fallos, costos o interacciones entre nodos, el modelo debe ajustarse antes de presentar los resultados como equivalentes.

## Requisitos

- Python **3.10 o superior**.
- Matplotlib **3.8 o superior** (opcional; se utiliza para generar las gráficas del benchmark).

No se requieren dependencias externas para ejecutar los algoritmos y las pruebas unitarias.

## Instalación y ejecución

Clonar el repositorio y entrar a la carpeta:

```bash
git clone -b feat/algoritmos-optimizacion https://github.com/Mttzputnik/ProyectoRed_ADAG2.git
cd ProyectoRed_ADAG2
```

Crear y activar un entorno virtual (recomendado):

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

Ejecutar el ejemplo principal:

```bash
python main.py
```

El programa muestra una demostración de selección voraz, comparación con el óptimo exacto en una instancia pequeña, reparto del presupuesto y simulación de cinco rondas.

## Pruebas

Ejecutar desde la raíz del repositorio:

```bash
python -m unittest discover -s tests -v
```

Las pruebas cubren, entre otros aspectos:

- Comparación del reparto voraz con el verificador exacto en una instancia pequeña.
- Rechazo de secuencias de ganancias marginales que incumplen la concavidad discreta.
- Comparación de Maximum Coverage voraz con el óptimo exacto.
- Respeto del presupuesto en la variante con costos.
- Reproducibilidad de la simulación cuando se utiliza la misma semilla.

### Resultado de ejecución verificado

En una ejecución local reportada para esta versión del proyecto se obtuvieron los siguientes resultados:

**Pruebas unitarias**

Comando:

```bash
python -m unittest discover -s tests -v
```

Resultado: **5 pruebas ejecutadas, 5 aprobadas y 0 fallidas** (`Ran 5 tests`, `OK`). Las pruebas verificaron el reparto voraz frente al método exacto en un caso pequeño, la validación de concavidad, las restricciones de presupuesto, la comparación de cobertura y la reproducibilidad de la simulación.

**Programa principal**

Comando:

```bash
python main.py
```

Resultados observados:

- Selección de nodos: Greedy obtuvo utilidad `36.0`; el óptimo exacto de esa instancia también obtuvo `36.0` (cociente `1.0`).
- Reparto de presupuesto: asignación `(0, 4, 8, 6)`, con utilidad `129.86505299450974`.
- Simulación multirronda: se completaron cinco rondas. La utilidad de cobertura observada fue `36.0`, `35.0`, `34.0`, `36.0` y `36.0`, respectivamente.

Estos resultados corresponden a la instancia de demostración y al entorno de esa ejecución; no constituyen una garantía de que Greedy alcance siempre el óptimo ni una evaluación con datos reales.

## Experimentos

Ejecutar el benchmark:

```bash
python experiments/benchmark.py
```

El experimento evalúa tamaños de entrada `N = 20, 40, 80, 160, 320`. Para cada tamaño mide la mediana de tres ejecuciones de los algoritmos de asignación y Maximum Coverage voraz.

Los resultados se guardan en la carpeta `results/`:

- `benchmark.csv`: tiempos medidos y parámetros de cada caso.
- `allocation_heap.png`: gráfica de tiempo del algoritmo de asignación (si Matplotlib está instalado).
- `maximum_coverage_greedy.png`: gráfica de tiempo de Maximum Coverage (si Matplotlib está instalado).

Los tiempos dependen del equipo y del entorno de ejecución. Para comparar ejecuciones, se recomienda utilizar el mismo equipo, versión de Python y condiciones de carga.

## Estructura del repositorio

```text
ProyectoRed_ADAG2/
├── src/
│   ├── allocation.py       # Asignación de presupuesto
│   ├── selection.py        # Algoritmos de selección
│   ├── simulation.py       # Simulación por rondas
│   ├── instances.py        # Generación de instancias sintéticas
│   └── __init__.py
├── tests/
│   └── test_algorithms.py  # Pruebas unitarias
├── experiments/
│   └── benchmark.py        # Experimentos de rendimiento
├── main.py                 # Ejecución de demostración
├── requirements.txt
├── ANALISIS_TEORICO.md     # Formalización y análisis de algoritmos
└── README.md
```

## Complejidad

Las complejidades principales, bajo las representaciones utilizadas, son:

| Algoritmo | Complejidad temporal | Observación |
|---|---:|---|
| Asignación con max-heap | `O(N + B log N)` | `N`: número de nodos; `B`: unidades asignadas. |
| Maximum Coverage voraz | `O(Nk)` evaluaciones marginales | El costo real también depende de las operaciones sobre conjuntos. |
| Maximum Coverage exacto | `O(C(N,k) · U)` como cota simple | Exponencial; se reserva para instancias pequeñas. |

Donde `k` es el número de nodos que se seleccionan y `U` es el tamaño del universo de elementos cubiertos.

## Limitaciones

- El generador de instancias es sintético; los resultados no deben interpretarse como mediciones de una red real.
- El algoritmo exacto de selección tiene crecimiento combinatorio y no está pensado para entradas grandes.
- La heurística de cobertura con costos **no tiene atribuida en este proyecto una garantía automática de aproximación de `1 - 1/e`**.
- La garantía clásica de `1 - 1/e` corresponde a Maximum Coverage monótono submodular con restricción de cardinalidad. No se extiende automáticamente a la variante con costos ni a la simulación con efectos entre vecinos.
- El modelo de fallos y de influencia de vecinos es una hipótesis de simulación explícita; debe contrastarse con la definición final del problema.

## Análisis teórico

El documento [ANALISIS_TEORICO.md](ANALISIS_TEORICO.md) desarrolla la formalización del reparto discreto, la justificación de optimalidad del algoritmo con heap, la submodularidad de Maximum Coverage, la discusión de NP-dureza y el alcance de las garantías de aproximación.

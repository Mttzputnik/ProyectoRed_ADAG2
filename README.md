# Proyecto Red — ADAG2

Implementación académica de algoritmos de optimización para selección de nodos, asignación discreta de presupuesto y simulación multirronda con fallos y efectos de vecindad.

El repositorio incluye algoritmos voraces, verificadores exactos para instancias pequeñas, pruebas automatizadas y experimentos reproducibles. Los generadores producen instancias sintéticas: sus resultados no representan por sí solos mediciones de una red real.

## Objetivos

1. Seleccionar hasta $k$ nodos para maximizar la cobertura de elementos.
2. Distribuir un presupuesto entero entre los nodos seleccionados maximizando la utilidad total.
3. Simular rondas con fallos independientes y efectos temporales entre vecinos.
4. Comparar soluciones voraces con métodos exactos en instancias pequeñas y estudiar tiempos de ejecución.

## Algoritmos

| Módulo | Función | Descripción |
|---|---|---|
| `src/allocation.py` | `greedy_allocate` | Asignación discreta óptima cuando las ganancias marginales son no negativas y no crecientes. |
| `src/allocation.py` | `brute_force_allocate` | Verificador exacto para instancias pequeñas. |
| `src/selection.py` | `greedy_max_coverage` | Maximum Coverage con restricción de cardinalidad. |
| `src/selection.py` | `exact_max_coverage` | Solución exacta por enumeración. |
| `src/selection.py` | `greedy_budgeted_coverage` | Heurística marginal/costo para cobertura con presupuesto. |
| `src/simulation.py` | `run_rounds` | Simulación multirronda de fallos, selección, asignación e influencia vecinal. |

## Modelo y supuestos

- Las ganancias marginales de cada nodo son finitas, no negativas y no crecientes.
- El presupuesto de asignación se expresa en unidades enteras.
- Maximum Coverage maximiza el tamaño de la unión de los conjuntos asociados a los nodos seleccionados.
- En cada ronda, los fallos son independientes y tienen una probabilidad común $p$.
- La asignación de la ronda anterior escala las ganancias marginales de los vecinos mediante $1 + \alpha \sum_j x_j$.
- Las ganancias marginales se alinean con el orden de inserción de las claves de `sets_by_node`; los identificadores pueden ser arbitrarios.
- Las semillas permiten reproducir los escenarios sintéticos.

Estos supuestos describen la implementación, no necesariamente cualquier formulación externa del problema. Si el enunciado académico define otra semántica de fallos o externalidades, debe prevalecer ese enunciado.

## Requisitos

- Python 3.10 o superior.
- Matplotlib 3.8 o superior para generar gráficas.
- NetworkX 3.3 o superior para construir y visualizar la topología de la red en la interfaz.

Los algoritmos y las pruebas utilizan únicamente la biblioteca estándar de Python.

## Instalación

Clonar la rama principal:

```bash
git clone https://github.com/Mttzputnik/ProyectoRed_ADAG2.git
cd ProyectoRed_ADAG2
```

Crear un entorno virtual e instalar dependencias:

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Ejecución

Demostración:

```bash
python main.py
```

Pruebas:

```bash
python -m unittest discover -s tests -v
```

## Interfaz gráfica interactiva

El laboratorio visual permite modificar parámetros y observar las tres partes del modelo: selección de nodos, asignación de presupuesto y simulación multirronda. También muestra la topología de la red con NetworkX, permite cambiar entre distribuciones (spring, circular, Kamada-Kawai y shell), resalta los nodos seleccionados por Maximum Coverage y conserva las matrices de cobertura y adyacencia.

Iniciar desde la raíz del proyecto:

```bash
streamlit run app.py
```

La aplicación abre un panel local en el navegador. Los parámetros se configuran en la barra lateral y el botón **Generar y ejecutar** actualiza la instancia. La comparación exacta de cobertura se limita a instancias pequeñas porque utiliza enumeración. La pestaña **Datos de la red** representa el grafo que también consume la simulación; los diseños visuales solo cambian la posición de los nodos, no las conexiones.

## Experimentos

Ejecutar el benchmark:

```bash
python experiments/benchmark.py
```

Se puede cambiar el número de repeticiones desde Python:

```python
from experiments.benchmark import run
run(repetitions=15)
```

El experimento genera `results/benchmark.csv` y una gráfica PNG por algoritmo. Incluye:

- Escalabilidad de asignación, Maximum Coverage, cobertura con costos y simulación multirronda.
- Comparación voraz/exacto de Maximum Coverage para tamaños pequeños.
- Comparación voraz/exacto de asignación en instancias acotadas.

El CSV registra parámetros, repeticiones, mediana, promedio, desviación estándar y razón de utilidad respecto al exacto cuando aplica. Los métodos exactos se restringen a instancias pequeñas para evitar tiempos combinatorios excesivos.

## Complejidad y garantías

| Algoritmo | Complejidad / garantía |
|---|---|
| `greedy_allocate` | $O(N + B\log N)$ tiempo; óptimo bajo concavidad discreta y factibilidad del presupuesto. |
| `greedy_max_coverage` | $O(Nk)$ evaluaciones marginales; garantía clásica $1-1/e$ para Maximum Coverage monótono con cardinalidad. El costo real depende de las operaciones sobre conjuntos. |
| `exact_max_coverage` | `binomial(N, k)` candidatos; exponencial. |
| `greedy_budgeted_coverage` | Heurística marginal/costo; no se le atribuye automáticamente la garantía $1-1/e$. |
| `run_rounds` | Depende del número de rondas, nodos activos, selección y asignación de cada ronda. Las externalidades no heredan automáticamente garantías de submodularidad. |

## Resultados y reproducibilidad

Los tiempos se deben generar en el equipo donde se realiza la evaluación. No se fijan aquí cifras de rendimiento que puedan confundirse con resultados de una ejecución que no se haya realizado en ese entorno.

Para reproducir una ejecución, registrar la versión de Python, equipo, parámetros, semilla y número de repeticiones junto al CSV producido.

## Estructura

```text
ProyectoRed_ADAG2/
├── src/
│   ├── allocation.py
│   ├── selection.py
│   ├── simulation.py
│   └── instances.py
├── tests/
│   └── test_algorithms.py
├── experiments/
│   └── benchmark.py
├── docs/
│   └── analisis_teorico.md
├── results/                 # CSV y gráficas generados
├── main.py
├── requirements.txt
└── README.md
```

## Documentación teórica

La formalización, las pruebas de optimalidad, el análisis de submodularidad y las limitaciones de las garantías se desarrollan en [docs/analisis_teorico.md](docs/analisis_teorico.md).

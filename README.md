# Proyecto Red — ADAG2

Implementación académica del problema de reparto de presupuesto y selección de participantes descrito en `Proyecto_ADAG2.docx`.

## Requisitos

- Python 3.10 o superior.
- `matplotlib` es opcional y se utiliza para generar gráficas.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python main.py
python experiments/benchmark.py
```

Los experimentos generan `results/benchmark.csv` y, si Matplotlib está instalado, una gráfica PNG por algoritmo.

## Estructura

```text
src/
  allocation.py   # reparto discreto óptimo mediante max-heap
  selection.py    # Maximum Coverage: greedy, exacto y variante con costos
  instances.py    # generadores sintéticos reproducibles
  simulation.py   # rondas, fallos y efecto de vecinos
experiments/
  benchmark.py    # tiempos para cinco tamaños de N
 tests/
  test_algorithms.py
main.py
```

## Modelos y supuestos

1. El reparto se modela en unidades discretas. Cada nodo recibe una secuencia de ganancias marginales no negativas y no crecientes; esta condición representa utilidad cóncava discreta.
2. La selección base es Maximum Coverage: cada nodo cubre un subconjunto del universo y la utilidad es el tamaño de la unión.
3. La variante de costos usa una heurística de ganancia marginal/costo. **No se le atribuye automáticamente la garantía `1-1/e`** del caso de cardinalidad; la garantía para presupuesto requiere especificar y aplicar el algoritmo y las hipótesis del resultado correspondiente.
4. En la simulación temporal, los fallos se generan de forma independiente con probabilidad fija por ronda. La asignación de una ronda modifica las ganancias marginales base de los vecinos en la ronda siguiente. Este es un modelo sintético explícito, no un mecanismo diferencial de privacidad ni un protocolo real de aprendizaje federado.
5. La interacción entre nodos puede alterar las propiedades de submodularidad. La garantía clásica de Maximum Coverage se aplica a la función de cobertura base; no debe extrapolarse a cualquier función acoplada sin demostrar submodularidad y cumplir las hipótesis.

## Algoritmos y complejidad

- Reparto voraz con heap: `O(B log N)` tiempo y `O(N)` espacio, con `B` unidades discretas y disponibilidad suficiente.
- Maximum Coverage voraz: `O(N k)` evaluaciones de ganancia marginal. Con conjuntos explícitos, el costo real también depende del tamaño de los conjuntos/universo manipulado.
- Óptimo exacto de Maximum Coverage: enumera `C(N,k)` subconjuntos; costo `O(C(N,k) * U)` como cota simple si cada utilidad recorre hasta `U` elementos.

Consulta `docs/analisis_teorico.md` para formalización, prueba de intercambio, reducción y discusión de garantías.

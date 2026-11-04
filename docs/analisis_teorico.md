# Análisis teórico — Proyecto Red

## 1. Reparto discreto de presupuesto

**Entrada.** `N` nodos, presupuesto entero `B` y para cada nodo `i` una lista `g_i(1),...,g_i(m_i)` de ganancias marginales. Se exige `g_i(j) >= 0` y `g_i(j+1) <= g_i(j)`. La utilidad de asignar `x_i` unidades es `u_i(x_i)=sum_{j=1}^{x_i} g_i(j)`.

**Salida.** Enteros `x_i >= 0`, con `sum_i x_i=B`, que maximizan `sum_i u_i(x_i)`.

**Algoritmo.** Mantener en un max-heap la siguiente ganancia marginal disponible de cada nodo. Extraer el máximo, asignar esa unidad al nodo y volver a insertar su siguiente marginal, si existe.

**Optimalidad por intercambio.** Considérese la secuencia formada por todas las ganancias marginales disponibles. Por concavidad discreta, las marginales de cada nodo están en orden no creciente. Una asignación factible selecciona un prefijo de la secuencia marginal de cada nodo. Si una solución óptima no seleccionara las `B` mayores marginales factibles, existiría una unidad seleccionada con ganancia menor que una unidad no seleccionada disponible como siguiente marginal. Intercambiar ambas no viola la estructura de prefijos (o, equivalentemente, se desplaza una unidad dentro del mismo nodo usando marginales no crecientes) y no reduce la utilidad; si la desigualdad es estricta, la mejora contradice optimalidad. Por tanto, extraer iterativamente la mayor marginal produce una asignación óptima.

**Complejidad.** Inicializar el heap cuesta `O(N)`. Cada una de las `B` extracciones y reinserciones cuesta `O(log N)`. Por tanto `T(N,B)=O(N+B log N)`, que para `B>=N` se expresa usualmente como `O(B log N)`. El espacio auxiliar es `O(N)`. La implementación también valida que el presupuesto no exceda la capacidad marginal disponible.

## 2. Selección de participantes: Maximum Coverage

**Entrada.** Universo `U`, colección `S_1,...,S_N` y entero `k<N`.

**Salida.** Un conjunto `A` de exactamente `k` índices que maximiza `f(A)=|union_{i in A} S_i|`.

**Submodularidad.** Para `A subseteq B` y nodo `v` no seleccionado, `f(A union {v})-f(A)=|S_v minus union(A)|` es al menos `|S_v minus union(B)|=f(B union {v})-f(B)`. Es decir, hay rendimientos marginales decrecientes. La función es además monótona y no negativa.

**NP-dureza (reducción desde Maximum Coverage).** Una instancia de Maximum Coverage consiste en un universo `U`, subconjuntos `S_1,...,S_N` y un límite `k`; pregunta qué `k` subconjuntos maximizan la cantidad de elementos cubiertos. Se transforma en una instancia de selección de nodos creando un nodo por cada subconjunto y definiendo la utilidad de un grupo de nodos como el tamaño de la unión de sus subconjuntos. La transformación es polinomial, conserva exactamente las soluciones y los valores objetivo. Por tanto, si se resolviera óptimamente la selección general en tiempo polinomial, también se resolvería Maximum Coverage en tiempo polinomial. Como Maximum Coverage es NP-difícil (a partir de Set Cover/Maximum Coverage según la formulación de decisión), la selección es NP-difícil.

**Voraz y garantía.** En cada paso se incorpora el nodo de mayor ganancia marginal. Para funciones monótonas submodulares no negativas con restricción de cardinalidad `k`, el resultado clásico de Nemhauser, Wolsey y Fisher (1978) garantiza `f(A_greedy) >= (1-1/e) f(A_opt)`, aproximadamente `0.632`. Esta garantía corresponde al problema base de cardinalidad; se debe comprobar empíricamente la razón respecto al óptimo exacto en instancias pequeñas, sin confundir esa comprobación con la prueba general.

**Complejidad.** Hay `k` iteraciones y en cada una se evalúan hasta `N` nodos: `O(Nk)` evaluaciones marginales. Con conjuntos explícitos, cada marginal calcula una diferencia de conjuntos, cuyo costo depende de la representación y del tamaño del universo; el benchmark reporta tiempo real además del conteo abstracto de evaluaciones.

**Óptimo exacto de referencia.** Enumerar todos los subconjuntos de tamaño `k` cuesta `binom(N,k)` evaluaciones. Con evaluación directa de un universo de tamaño `|U|`, una cota es `O(binomial(N,k) * |U|)`. Se utiliza únicamente para tamaños pequeños y para medir la calidad del algoritmo aproximado.

## 3. Variante con costos

Cada nodo tiene costo positivo `c_i` y se impone `sum_{i in A} c_i <= C`. La regla implementada selecciona iterativamente por ganancia marginal/costo entre nodos factibles. Es una heurística de referencia; **no se afirma que tenga por sí sola la garantía `1-1/e`**. El enunciado exige una garantía específica para Budgeted Maximum Coverage: el informe final debe identificar el algoritmo teórico exacto, sus hipótesis (incluido el tratamiento de elementos individuales cuando corresponda) y citar la cota correcta antes de atribuirla a resultados experimentales.

## 4. Rondas, fallos y vecinos

La simulación genera fallos independientes por ronda con probabilidad `p`. Los nodos fallidos no pueden ser seleccionados en esa ronda. Se aplica Maximum Coverage voraz sobre los nodos activos. La asignación de presupuesto de la ronda `t` escala las ganancias marginales de cada nodo en `t+1` por `1 + alpha * suma(x_j)` sobre sus vecinos `j` en el grafo.

Al fijar la influencia al inicio de una ronda, las marginales de cada nodo siguen siendo no crecientes si las marginales base lo eran. Sin embargo, una utilidad conjunta con externalidades puede dejar de ser submodular. Por ello, la garantía `1-1/e` no se extiende automáticamente a la variante acoplada; debe verificarse/probarse la propiedad para la función concreta o presentarse como simulación heurística separada.

## 5. Validación experimental

`experiments/benchmark.py` genera cinco tamaños `N={20,40,80,160,320}`, mide medianas de varias ejecuciones y exporta CSV y gráficas. Para una entrega rigurosa:

- Mantener fija la semilla y reportar repeticiones.
- Variar `N` y declarar cómo crecen `B`, `k` y `|U|`.
- Comparar tiempos observados con `B log N` y `N k`.
- Medir el exacto solo en tamaños pequeños, pues su crecimiento es combinatorio.
- Reportar también la razón `f(greedy)/f(exacto)` en instancias donde el exacto sea computable.

## Referencia clásica

Nemhauser, G. L., Wolsey, L. A., & Fisher, M. L. (1978). *An analysis of approximations for maximizing submodular set functions—I*. Mathematical Programming, 14, 265–294.

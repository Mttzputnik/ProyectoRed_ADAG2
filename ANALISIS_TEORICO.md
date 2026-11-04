# Análisis teórico — Proyecto Red

## 1. Reparto discreto de presupuesto

**Entrada.** `N` nodos, presupuesto entero `B` y para cada nodo `i` una lista `g_i(1),...,g_i(m_i)` de ganancias marginales. Se exige `g_i(j) >= 0` y `g_i(j+1) <= g_i(j)`. La utilidad de asignar `x_i` unidades es `u_i(x_i)=sum_{j=1}^{x_i} g_i(j)`.

**Salida.** Enteros `x_i >= 0`, con `sum_i x_i=B`, que maximizan `sum_i u_i(x_i)`.

**Algoritmo.** Mantener en un max-heap la siguiente ganancia marginal disponible de cada nodo. Extraer el máximo, asignar esa unidad al nodo y volver a insertar su siguiente marginal, si existe.

**Optimalidad por intercambio.** Por concavidad discreta, las marginales de cada nodo están en orden no creciente y una asignación factible toma un prefijo de cada secuencia. Si una solución no elige las B mayores marginales disponibles, existe una marginal seleccionada menor que otra marginal disponible. Intercambiar la unidad de menor ganancia por la mayor no reduce la utilidad y, si la desigualdad es estricta, contradice la optimalidad. Por tanto, extraer iterativamente la mayor marginal produce una asignación óptima.

**Complejidad.** Inicializar el heap cuesta `O(N)`. Cada una de las `B` extracciones y reinserciones cuesta `O(log N)`. Por tanto `T(N,B)=O(N+B log N)`; para `B>=N`, se expresa como `O(B log N)`. Espacio auxiliar `O(N)`.

## 2. Selección: Maximum Coverage

**Entrada.** Universo `U`, colección `S_1,...,S_N` y entero `k<N`. **Salida.** Un conjunto `A` de exactamente `k` índices que maximiza `f(A)=|union_{i in A} S_i|`.

**Submodularidad.** Para `A subseteq B` y nodo `v` no seleccionado, `f(A union {v})-f(A)=|S_v minus union(A)|` es al menos `|S_v minus union(B)|=f(B union {v})-f(B)`. La función es monótona y no negativa.

**NP-dureza.** Se reduce Maximum Coverage creando un nodo por cada subconjunto de la instancia original y definiendo la utilidad conjunta como el tamaño de la unión de los subconjuntos elegidos. La transformación es polinomial y conserva soluciones y valores objetivo. Como Maximum Coverage es NP-difícil, la selección general también lo es.

**Voraz y garantía.** En cada paso se incorpora el nodo de mayor ganancia marginal. Para funciones monótonas submodulares no negativas con restricción de cardinalidad `k`, Nemhauser, Wolsey y Fisher (1978) garantizan `f(A_greedy) >= (1-1/e) f(A_opt)`, aproximadamente `0.632`. Esta garantía corresponde al problema base de cardinalidad, no se extiende automáticamente a variantes acopladas.

**Complejidad.** `k` iteraciones con hasta `N` evaluaciones marginales: `O(Nk)` evaluaciones. Con conjuntos explícitos, el tiempo real depende además del tamaño del universo y de la representación. El óptimo exacto enumera `binom(N,k)` subconjuntos; una cota simple es `O(binomial(N,k)*|U|)`.

## 3. Variante con costos

Con costos `c_i>0` y presupuesto `C`, la implementación usa ganancia marginal/costo entre nodos factibles. Es una heurística de referencia; no se le atribuye por sí sola `1-1/e`. La entrega final debe identificar el algoritmo teórico de Budgeted Maximum Coverage, sus hipótesis y la cota correcta antes de reportar una garantía.

## 4. Rondas, fallos y vecinos

La simulación genera fallos independientes por ronda con probabilidad `p`; los nodos fallidos no participan. La asignación de la ronda `t` escala las ganancias marginales base de los vecinos en `t+1` por `1 + alpha * suma(x_j)` sobre sus vecinos. Al fijar la influencia al inicio de cada ronda, las marginales por nodo conservan el orden no creciente. Sin embargo, una utilidad conjunta con externalidades puede dejar de ser submodular: la garantía `1-1/e` no se extiende sin una demostración para la función concreta.

## 5. Validación experimental

`experiments/benchmark.py` genera cinco tamaños `N={20,40,80,160,320}`, mide medianas y exporta CSV y gráficas. Para el informe: declarar cómo crecen `B`, `k` y `|U|`; comparar tiempos observados con `B log N` y `Nk`; medir el exacto solo en tamaños pequeños; reportar `f(greedy)/f(exacto)` donde sea computable.

**Referencia:** Nemhauser, G. L., Wolsey, L. A., & Fisher, M. L. (1978). *An analysis of approximations for maximizing submodular set functions—I*. Mathematical Programming, 14, 265–294.

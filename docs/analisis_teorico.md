# Análisis teórico — Proyecto Red ADAG2

## 1. Asignación discreta de presupuesto

Sean (N) nodos y un presupuesto entero (B). Para cada nodo (i), se conoce una secuencia de ganancias marginales (g_i(1),\ldots,g_i(m_i)), que satisface:

[
g_i(j) \geq 0, \qquad g_i(j+1) \leq g_i(j).
]

La utilidad de asignar (x_i) unidades al nodo (i) es:

[
u_i(x_i)=\sum_{j=1}^{x_i}g_i(j).
]

Se busca maximizar (\sum_i u_i(x_i)), sujeto a (\sum_i x_i=B) y (0\leq x_i\leq m_i).

### Algoritmo y optimalidad

El algoritmo mantiene en un max-heap la siguiente ganancia marginal disponible de cada nodo. Extrae la mayor, asigna esa unidad y agrega la siguiente marginal de ese mismo nodo, si existe. La condición de marginales no crecientes garantiza que una unidad posterior de un nodo nunca puede ser preferible a una unidad anterior de ese mismo nodo.

Por tanto, el algoritmo selecciona las (B) mayores marginales respetando los prefijos de cada secuencia. Mediante intercambio, cualquier asignación que omita una marginal disponible mayor y conserve una menor puede mejorarse o igualarse sustituyendo la unidad correspondiente. El procedimiento voraz es óptimo para este modelo separable y cóncavo discreto, siempre que el presupuesto sea factible.

### Complejidad

La construcción del heap con `heapq.heapify` cuesta (O(N)). Cada una de las (B) extracciones y posibles inserciones cuesta (O(\log N)). La complejidad es:

[
O(N+B\log N)
]

El heap usa (O(N)) espacio auxiliar. El resultado almacena además las (B) ganancias seleccionadas.

## 2. Maximum Coverage

Sea (U) un universo y (S_1,\ldots,S_N\subseteq U) los conjuntos asociados a los nodos. Para una selección (A), la utilidad es:

[
f(A)=\left|\bigcup_{i\in A}S_i\right|.
]

La función es no negativa y monótona. También es submodular: si (A\subseteq B), la ganancia de añadir un nodo (v) a (A) es:

[
f(A\cup\{v\})-f(A)
=\left|S_v\setminus\bigcup_{i\in A}S_i\right|,
]

que no es menor que la ganancia de añadirlo a (B), porque (B) ya cubre al menos los elementos cubiertos por (A).

Con restricción de cardinalidad (|A|\leq k), el algoritmo voraz que elige la mayor ganancia marginal obtiene la garantía clásica (1-1/e\) para funciones monótonas submodulares no negativas (Nemhauser, Wolsey y Fisher, 1978). Esta garantía es aproximadamente 0.632 y corresponde al problema de cardinalidad descrito, no a todas las variantes del proyecto.

Maximum Coverage es NP-difícil. Una instancia de Maximum Coverage se transforma directamente en selección de nodos creando un nodo por cada conjunto y manteniendo la misma función de unión; la transformación conserva soluciones y valores objetivo.

### Complejidad

El algoritmo voraz realiza (O(Nk)) evaluaciones marginales. Con conjuntos explícitos, cada evaluación calcula una diferencia de conjuntos y su costo depende del tamaño de los conjuntos y de la representación. Por ello, (O(Nk)) cuenta evaluaciones, no necesariamente operaciones elementales.

El método exacto enumera ({N\choose k}) subconjuntos. Si cada unión se evalúa recorriendo un universo de tamaño (|U|), una cota simple es (O({N\choose k}|U|)).

## 3. Maximum Coverage con costos

Cada nodo tiene un costo positivo (c_i), y la restricción es:

[
\sum_{i\in A}c_i\leq C.
]

La implementación utiliza una heurística que selecciona nodos factibles por razón ganancia marginal/costo. No se afirma que esta regla aislada alcance una garantía (1-1/e). Las garantías de aproximación para Budgeted Maximum Coverage dependen del algoritmo concreto y de condiciones adicionales; no deben transferirse desde el caso de cardinalidad sin una demostración aplicable.

## 4. Simulación multirronda y externalidades

En cada ronda, cada nodo falla independientemente con probabilidad (p). Los nodos activos son candidatos para Maximum Coverage. Las ganancias marginales de la siguiente ronda se escalan mediante:

[
g_i^{(t+1)}(j)=g_i(j)
\left(1+\alpha\sum_{v\in N(i)}x_v^{(t)}\right),
]

donde (N(i)) es el vecindario de (i), (x_v^{(t)}) es la asignación de la ronda anterior y (alpha\geq0) controla la influencia.

Al fijarse el factor al comienzo de la ronda, multiplicar una secuencia por un factor no negativo conserva su orden no creciente. Sin embargo, esto no demuestra submodularidad de una función conjunta que incorpore interacciones entre nodos. En consecuencia, la garantía de Maximum Coverage no se extiende automáticamente a la simulación acoplada.

La simulación admite identificadores de nodos arbitrarios. Las filas de ganancias marginales deben estar alineadas con el orden de inserción de las claves del mapeo de conjuntos.

## 5. Diseño experimental

El benchmark registra mediana, promedio, desviación estándar y número de repeticiones. También registra parámetros de entrada y, en las instancias pequeñas, razón de utilidad respecto al método exacto.

Para interpretar resultados:

- Mantener semilla, versión de Python y condiciones de equipo documentadas.
- Declarar cómo varían (B), (k) y (|U|) cuando crece (N).
- No usar los métodos exactos en tamaños que provoquen enumeraciones excesivas.
- Separar mediciones de tiempo de argumentos teóricos de complejidad.
- Considerar la desviación entre repeticiones; no presentar un tiempo aislado como conclusión general.

## Referencia

Nemhauser, G. L., Wolsey, L. A., & Fisher, M. L. (1978). *An analysis of approximations for maximizing submodular set functions—I*. Mathematical Programming, 14, 265–294.

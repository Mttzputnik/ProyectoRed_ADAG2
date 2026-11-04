"""Selección submodular: Maximum Coverage y variante con costos."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Hashable, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class SelectionResult:
    selected: tuple[Hashable, ...]
    utility: float
    marginal_gains: tuple[float, ...]


def coverage_utility(selected: Iterable[Hashable], sets_by_node: Mapping[Hashable, set]) -> int:
    covered: set = set()
    for node in selected:
        covered.update(sets_by_node[node])
    return len(covered)


def greedy_max_coverage(sets_by_node: Mapping[Hashable, set], k: int) -> SelectionResult:
    """Voraz de Maximum Coverage. Garantía (1-1/e) para cardinalidad k.

    Evaluación directa: O(N*k*U) en esta implementación con conjuntos,
    donde U acota el tamaño de las uniones manipuladas; el conteo abstracto
    de evaluaciones de marginales es O(N*k), como exige el enunciado.
    """
    if k < 0 or k > len(sets_by_node):
        raise ValueError("k debe estar entre 0 y N")
    chosen: list[Hashable] = []
    gains: list[float] = []
    covered: set = set()
    remaining = list(sets_by_node)
    for _ in range(k):
        best_node = None
        best_gain = -1
        for node in remaining:
            gain = len(sets_by_node[node] - covered)
            if gain > best_gain:
                best_node, best_gain = node, gain
        if best_node is None:
            break
        chosen.append(best_node)
        gains.append(float(best_gain))
        covered.update(sets_by_node[best_node])
        remaining.remove(best_node)
    return SelectionResult(tuple(chosen), float(len(covered)), tuple(gains))


def exact_max_coverage(sets_by_node: Mapping[Hashable, set], k: int) -> SelectionResult:
    """Óptimo exacto por enumeración; exponencial, destinado a instancias pequeñas."""
    nodes = list(sets_by_node)
    if k < 0 or k > len(nodes):
        raise ValueError("k debe estar entre 0 y N")
    best_nodes: tuple[Hashable, ...] = ()
    best_value = -1
    for candidate in combinations(nodes, k):
        value = coverage_utility(candidate, sets_by_node)
        if value > best_value:
            best_nodes, best_value = candidate, value
    return SelectionResult(best_nodes, float(best_value), ())


def greedy_budgeted_coverage(sets_by_node: Mapping[Hashable, set], costs: Mapping[Hashable, float], budget: float) -> SelectionResult:
    """Heurística por ganancia marginal/costo para cobertura con presupuesto.

    Importante: esta variante NO hereda automáticamente la garantía 1-1/e
    del caso cardinalidad. La garantía depende de la variante exacta y de sus
    condiciones (p.ej. tratamiento del mejor singleton y esquema de selección).
    """
    if budget < 0:
        raise ValueError("budget debe ser >= 0")
    if any(node not in costs or costs[node] <= 0 for node in sets_by_node):
        raise ValueError("Cada nodo debe tener un costo positivo")
    chosen: list[Hashable] = []
    gains: list[float] = []
    covered: set = set()
    remaining = set(sets_by_node)
    spent = 0.0
    while remaining:
        feasible = [n for n in remaining if spent + costs[n] <= budget]
        if not feasible:
            break
        node = max(feasible, key=lambda n: (len(sets_by_node[n] - covered) / costs[n], -costs[n]))
        gain = len(sets_by_node[node] - covered)
        if gain <= 0:
            break
        chosen.append(node)
        gains.append(float(gain))
        covered.update(sets_by_node[node])
        spent += costs[node]
        remaining.remove(node)
    return SelectionResult(tuple(chosen), float(len(covered)), tuple(gains))

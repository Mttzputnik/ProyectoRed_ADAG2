"""Algoritmos para Maximum Coverage y su variante con costos."""
from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations
from numbers import Integral, Real
from typing import Hashable, Iterable, Mapping


@dataclass(frozen=True)
class SelectionResult:
    selected: tuple[Hashable, ...]
    utility: float
    marginal_gains: tuple[float, ...]


def _validate_k(k: int, n: int) -> None:
    if isinstance(k, bool) or not isinstance(k, Integral):
        raise ValueError("k debe ser un entero")
    if not 0 <= k <= n:
        raise ValueError("k debe estar entre 0 y N")


def _validate_sets(sets_by_node: Mapping[Hashable, set]) -> None:
    if not isinstance(sets_by_node, Mapping):
        raise ValueError("sets_by_node debe ser un mapeo")
    if any(not isinstance(elements, (set, frozenset)) for elements in sets_by_node.values()):
        raise ValueError("Cada nodo debe asociarse con un set o frozenset")


def coverage_utility(selected: Iterable[Hashable], sets_by_node: Mapping[Hashable, set]) -> int:
    _validate_sets(sets_by_node)
    covered: set = set()
    for node in selected:
        if node not in sets_by_node:
            raise ValueError(f"Nodo desconocido: {node!r}")
        covered.update(sets_by_node[node])
    return len(covered)


def greedy_max_coverage(sets_by_node: Mapping[Hashable, set], k: int) -> SelectionResult:
    """Voraz de Maximum Coverage (1 - 1/e) para cardinalidad.

    Realiza O(N*k) evaluaciones marginales. El costo de cada evaluación
    depende de la implementación y tamaño de los conjuntos.
    """
    _validate_sets(sets_by_node)
    nodes = list(sets_by_node)
    _validate_k(k, len(nodes))
    chosen: list[Hashable] = []
    gains: list[float] = []
    covered: set = set()
    remaining = nodes.copy()
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
    """Óptimo exacto por enumeración; exponencial y destinado a casos pequeños."""
    _validate_sets(sets_by_node)
    nodes = list(sets_by_node)
    _validate_k(k, len(nodes))
    best_nodes: tuple[Hashable, ...] = ()
    best_value = -1
    for candidate in combinations(nodes, k):
        value = coverage_utility(candidate, sets_by_node)
        if value > best_value:
            best_nodes, best_value = candidate, value
    return SelectionResult(best_nodes, float(best_value), ())


def greedy_budgeted_coverage(
    sets_by_node: Mapping[Hashable, set],
    costs: Mapping[Hashable, float],
    budget: float,
) -> SelectionResult:
    """Heurística marginal/costo; no atribuye por sí sola garantía 1 - 1/e."""
    _validate_sets(sets_by_node)
    if isinstance(budget, bool) or not isinstance(budget, Real) or not math.isfinite(float(budget)) or budget < 0:
        raise ValueError("budget debe ser un número finito >= 0")
    if not isinstance(costs, Mapping):
        raise ValueError("costs debe ser un mapeo")

    normalized_costs: dict[Hashable, float] = {}
    for node in sets_by_node:
        if node not in costs:
            raise ValueError(f"Falta el costo del nodo {node!r}")
        cost = costs[node]
        if isinstance(cost, bool) or not isinstance(cost, Real) or not math.isfinite(float(cost)) or cost <= 0:
            raise ValueError(f"El costo de {node!r} debe ser positivo y finito")
        normalized_costs[node] = float(cost)

    chosen: list[Hashable] = []
    gains: list[float] = []
    covered: set = set()
    remaining = set(sets_by_node)
    spent = 0.0
    while remaining:
        feasible = [node for node in remaining if spent + normalized_costs[node] <= budget]
        if not feasible:
            break
        node = max(
            feasible,
            key=lambda item: (
                len(sets_by_node[item] - covered) / normalized_costs[item],
                -normalized_costs[item],
            ),
        )
        gain = len(sets_by_node[node] - covered)
        if gain <= 0:
            break
        chosen.append(node)
        gains.append(float(gain))
        covered.update(sets_by_node[node])
        spent += normalized_costs[node]
        remaining.remove(node)
    return SelectionResult(tuple(chosen), float(len(covered)), tuple(gains))

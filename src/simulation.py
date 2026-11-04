"""Simulación multirronda con fallos y externalidades temporales de vecindad.

Las filas de marginal_gains se alinean con el orden de inserción de sets_by_node.
Los identificadores pueden ser arbitrarios; allocation conserva ese orden.
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass
from numbers import Integral, Real
from typing import Hashable, Mapping, Sequence
from .allocation import greedy_allocate
from .selection import greedy_max_coverage


@dataclass(frozen=True)
class RoundResult:
    round_number: int
    active_nodes: tuple[Hashable, ...]
    selected_nodes: tuple[Hashable, ...]
    coverage_utility: float
    allocation: tuple[int, ...]
    allocation_utility: float


def _require_int(name: str, value: int, minimum: int = 0) -> None:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} debe ser un entero >= {minimum}")


def run_rounds(
    sets_by_node: Mapping[Hashable, set],
    marginal_gains: Sequence[Sequence[float]],
    *,
    rounds: int,
    k: int,
    budget_per_round: int,
    failure_probability: float = 0.0,
    seed: int = 0,
    graph: Mapping[Hashable, set[Hashable]] | None = None,
    neighbor_alpha: float = 0.0,
) -> list[RoundResult]:
    """Ejecuta rondas reproducibles con fallos independientes por nodo y ronda."""
    if not isinstance(sets_by_node, Mapping):
        raise ValueError("sets_by_node debe ser un mapeo")
    _require_int("rounds", rounds, 1)
    _require_int("k", k)
    _require_int("budget_per_round", budget_per_round)
    if isinstance(failure_probability, bool) or not isinstance(failure_probability, Real):
        raise ValueError("failure_probability debe estar en [0, 1]")
    if not math.isfinite(float(failure_probability)) or not 0 <= failure_probability <= 1:
        raise ValueError("failure_probability debe estar en [0, 1]")
    if isinstance(neighbor_alpha, bool) or not isinstance(neighbor_alpha, Real):
        raise ValueError("neighbor_alpha debe ser un número finito >= 0")
    if not math.isfinite(float(neighbor_alpha)) or neighbor_alpha < 0:
        raise ValueError("neighbor_alpha debe ser un número finito >= 0")

    nodes = list(sets_by_node)
    try:
        marginal_count = len(marginal_gains)
    except TypeError as exc:
        raise ValueError("marginal_gains debe ser una secuencia") from exc
    if marginal_count != len(nodes):
        raise ValueError("Debe existir una función marginal por nodo, alineada al orden del mapeo")
    greedy_allocate(marginal_gains, 0)  # valida también las filas de nodos que fallen

    if graph is not None:
        if not isinstance(graph, Mapping):
            raise ValueError("graph debe ser un mapeo de nodo a conjunto de vecinos")
        for node, neighbors in graph.items():
            if not isinstance(neighbors, (set, frozenset)):
                raise ValueError(f"Los vecinos de {node!r} deben ser un conjunto")
        unknown = {v for neighbors in graph.values() for v in neighbors if v not in sets_by_node}
        unknown.update(node for node in graph if node not in sets_by_node)
        if unknown:
            raise ValueError(f"El grafo contiene nodos desconocidos: {unknown!r}")

    node_to_index = {node: index for index, node in enumerate(nodes)}
    rng = random.Random(seed)
    previous_allocation = [0] * len(nodes)
    results = []
    for round_number in range(1, rounds + 1):
        active = [node for node in nodes if rng.random() >= failure_probability]
        allocation = [0] * len(nodes)
        if not active:
            results.append(RoundResult(round_number, (), (), 0.0, tuple(allocation), 0.0))
            previous_allocation = allocation
            continue

        active_sets = {node: sets_by_node[node] for node in active}
        selection = greedy_max_coverage(active_sets, min(int(k), len(active)))
        selected = list(selection.selected)
        adjusted = []
        for node in selected:
            neighbors = (graph or {}).get(node, set())
            influence = math.fsum(previous_allocation[node_to_index[v]] for v in neighbors)
            factor = 1.0 + float(neighbor_alpha) * influence
            adjusted.append([float(gain) * factor for gain in marginal_gains[node_to_index[node]]])

        allocation_utility = 0.0
        if selected and budget_per_round:
            capacity = sum(len(row) for row in adjusted)
            result = greedy_allocate(adjusted, min(int(budget_per_round), capacity))
            allocation_utility = result.utility
            for local_index, node in enumerate(selected):
                allocation[node_to_index[node]] = result.allocation[local_index]

        results.append(RoundResult(
            round_number, tuple(active), tuple(selected), selection.utility,
            tuple(allocation), allocation_utility,
        ))
        previous_allocation = allocation
    return results

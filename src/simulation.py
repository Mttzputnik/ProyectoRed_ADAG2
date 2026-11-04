"""Simulación de T rondas con fallos y externalidades de vecindad.

Modelo explícito de la variante: los nodos que fallan se excluyen de la ronda.
La asignación de una ronda afecta las ganancias marginales base de sus vecinos
EN LA RONDA SIGUIENTE mediante un factor 1 + alpha * suma_asignaciones_vecinas.
Este acoplamiento temporal conserva concavidad si el factor se fija al inicio
de cada ronda; no implica por sí solo submodularidad de la utilidad de selección.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Mapping, Sequence

from .allocation import AllocationResult, greedy_allocate
from .selection import SelectionResult, greedy_max_coverage


@dataclass(frozen=True)
class RoundResult:
    round_number: int
    active_nodes: tuple[int, ...]
    selected_nodes: tuple[int, ...]
    coverage_utility: float
    allocation: tuple[int, ...]
    allocation_utility: float


def run_rounds(
    sets_by_node: Mapping[int, set],
    marginal_gains: Sequence[Sequence[float]],
    *, rounds: int, k: int, budget_per_round: int,
    failure_probability: float = 0.0, seed: int = 0,
    graph: Mapping[int, set[int]] | None = None, neighbor_alpha: float = 0.0,
) -> list[RoundResult]:
    """Ejecuta rondas; la semilla hace reproducibles los fallos sintéticos."""
    n = len(sets_by_node)
    if rounds < 1 or not 0 <= failure_probability <= 1:
        raise ValueError("rounds debe ser positivo y failure_probability estar en [0,1]")
    if len(marginal_gains) != n:
        raise ValueError("Debe existir una función marginal por nodo")
    if neighbor_alpha < 0:
        raise ValueError("neighbor_alpha debe ser >= 0")
    rng = random.Random(seed)
    previous_allocation = [0] * n
    results: list[RoundResult] = []

    for t in range(1, rounds + 1):
        active = [i for i in range(n) if rng.random() >= failure_probability]
        if not active:
            results.append(RoundResult(t, (), (), 0.0, tuple([0] * n), 0.0))
            previous_allocation = [0] * n
            continue

        active_sets = {i: sets_by_node[i] for i in active}
        selection: SelectionResult = greedy_max_coverage(active_sets, min(k, len(active)))
        selected = list(selection.selected)

        adjusted: list[list[float]] = []
        for i in selected:
            neighbors = (graph or {}).get(i, set())
            influence = sum(previous_allocation[j] for j in neighbors if 0 <= j < n)
            factor = 1.0 + neighbor_alpha * influence
            adjusted.append([float(g) * factor for g in marginal_gains[i]])
        allocation_result: AllocationResult | None = None
        if selected and budget_per_round:
            capacity = sum(len(row) for row in adjusted)
            allocation_result = greedy_allocate(adjusted, min(budget_per_round, capacity))
            allocation = [0] * n
            for local, node in enumerate(selected):
                allocation[node] = allocation_result.allocation[local]
            allocation_utility = allocation_result.utility
        else:
            allocation = [0] * n
            allocation_utility = 0.0

        results.append(RoundResult(t, tuple(active), tuple(selected), selection.utility,
                                   tuple(allocation), allocation_utility))
        previous_allocation = allocation
    return results

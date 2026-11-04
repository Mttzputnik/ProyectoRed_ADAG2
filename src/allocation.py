"""Reparto discreto óptimo de presupuesto con utilidades cóncavas.

Cada utilidad se representa mediante sus ganancias marginales discretas.
La concavidad equivale a que estas ganancias sean no crecientes.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class AllocationResult:
    allocation: tuple[int, ...]
    utility: float
    marginal_gains: tuple[float, ...]


def greedy_allocate(marginal_gains: Sequence[Sequence[float]], budget: int) -> AllocationResult:
    """Asigna B unidades usando un max-heap; óptimo para utilidades discretas cóncavas.

    marginal_gains[i][j] es la ganancia de entregar la unidad j+1 al nodo i.
    Cada secuencia debe ser no creciente. El presupuesto debe ser asignable.
    Complejidad: O(B log N), espacio O(N).
    """
    if budget < 0:
        raise ValueError("budget debe ser >= 0")
    if not marginal_gains and budget:
        raise ValueError("No hay nodos a los cuales asignar presupuesto")

    gains = [tuple(float(x) for x in row) for row in marginal_gains]
    for i, row in enumerate(gains):
        if any(x < 0 for x in row):
            raise ValueError(f"Las ganancias marginales del nodo {i} deben ser no negativas")
        if any(row[j] < row[j + 1] for j in range(len(row) - 1)):
            raise ValueError(f"La utilidad del nodo {i} no es cóncava: marginales crecientes")

    allocation = [0] * len(gains)
    heap: list[tuple[float, int]] = []
    for i, row in enumerate(gains):
        if row:
            heapq.heappush(heap, (-row[0], i))

    selected: list[float] = []
    for _ in range(budget):
        if not heap:
            raise ValueError("El presupuesto excede las unidades disponibles en las funciones")
        neg_gain, i = heapq.heappop(heap)
        gain = -neg_gain
        selected.append(gain)
        allocation[i] += 1
        next_index = allocation[i]
        if next_index < len(gains[i]):
            heapq.heappush(heap, (-gains[i][next_index], i))

    return AllocationResult(tuple(allocation), sum(selected), tuple(selected))


def brute_force_allocate(marginal_gains: Sequence[Sequence[float]], budget: int) -> AllocationResult:
    """Verificador exacto pequeño por enumeración de asignaciones (no usar en producción)."""
    from itertools import product

    rows = [tuple(map(float, row)) for row in marginal_gains]
    best: AllocationResult | None = None
    ranges = [range(len(row) + 1) for row in rows]
    for allocation in product(*ranges):
        if sum(allocation) != budget:
            continue
        chosen = tuple(rows[i][j] for i, amount in enumerate(allocation) for j in range(amount))
        value = sum(chosen)
        if best is None or value > best.utility:
            best = AllocationResult(tuple(allocation), value, chosen)
    if best is None:
        raise ValueError("No existe asignación factible para ese presupuesto")
    return best

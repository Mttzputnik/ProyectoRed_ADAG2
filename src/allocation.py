"""Reparto discreto óptimo de presupuesto para utilidades cóncavas."""
from __future__ import annotations
import heapq
import math
from dataclasses import dataclass
from numbers import Real
from typing import Sequence


@dataclass(frozen=True)
class AllocationResult:
    allocation: tuple[int, ...]
    utility: float
    marginal_gains: tuple[float, ...]


def _validate_budget(budget: int) -> None:
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise ValueError("budget debe ser un entero")
    if budget < 0:
        raise ValueError("budget debe ser >= 0")


def _normalize_gains(marginal_gains: Sequence[Sequence[float]]) -> list[tuple[float, ...]]:
    try:
        rows = []
        for row in list(marginal_gains):
            values = list(row)
            if any(isinstance(value, bool) or not isinstance(value, Real) for value in values):
                raise ValueError("Las ganancias deben ser numéricas, no booleanos ni cadenas")
            rows.append(tuple(float(value) for value in values))
    except (TypeError, OverflowError) as exc:
        raise ValueError("marginal_gains debe contener secuencias de números") from exc
    for i, row in enumerate(rows):
        if any(not math.isfinite(value) for value in row):
            raise ValueError(f"Las ganancias del nodo {i} deben ser finitas")
        if any(value < 0 for value in row):
            raise ValueError(f"Las ganancias del nodo {i} deben ser no negativas")
        if any(row[j] < row[j + 1] for j in range(len(row) - 1)):
            raise ValueError(f"La utilidad del nodo {i} no es cóncava: marginales crecientes")
    return rows


def greedy_allocate(marginal_gains: Sequence[Sequence[float]], budget: int) -> AllocationResult:
    """Asigna B unidades con max-heap; óptimo si cada fila es no creciente.

    Tiempo O(N + B log N); espacio auxiliar O(N), más el resultado de tamaño O(N+B).
    """
    _validate_budget(budget)
    gains = _normalize_gains(marginal_gains)
    if not gains and budget:
        raise ValueError("No hay nodos a los cuales asignar presupuesto")
    allocation = [0] * len(gains)
    heap = [(-row[0], i) for i, row in enumerate(gains) if row]
    heapq.heapify(heap)
    selected: list[float] = []
    for _ in range(budget):
        if not heap:
            raise ValueError("El presupuesto excede las unidades disponibles en las funciones")
        negative_gain, node = heapq.heappop(heap)
        selected.append(-negative_gain)
        allocation[node] += 1
        next_index = allocation[node]
        if next_index < len(gains[node]):
            heapq.heappush(heap, (-gains[node][next_index], node))
    return AllocationResult(tuple(allocation), math.fsum(selected), tuple(selected))


def brute_force_allocate(marginal_gains: Sequence[Sequence[float]], budget: int) -> AllocationResult:
    """Verificador exacto por enumeración; reservar para instancias pequeñas."""
    from itertools import product
    _validate_budget(budget)
    rows = _normalize_gains(marginal_gains)
    best: AllocationResult | None = None
    for allocation in product(*(range(len(row) + 1) for row in rows)):
        if sum(allocation) != budget:
            continue
        chosen = tuple(rows[i][j] for i, amount in enumerate(allocation) for j in range(amount))
        value = math.fsum(chosen)
        if best is None or value > best.utility:
            best = AllocationResult(tuple(allocation), value, chosen)
    if best is None:
        raise ValueError("No existe asignación factible para ese presupuesto")
    return best

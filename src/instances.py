"""Generadores deterministas de instancias sintéticas."""
from __future__ import annotations

import math
import random


def _positive_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} debe ser un entero positivo")


def generate_coverage_instance(
    n_nodes: int, universe_size: int, density: float = 0.15, seed: int = 0
) -> dict[int, set[int]]:
    _positive_int("n_nodes", n_nodes)
    _positive_int("universe_size", universe_size)
    if isinstance(density, bool) or not isinstance(density, (int, float)):
        raise ValueError("density debe estar en [0, 1]")
    if not math.isfinite(float(density)) or not 0 <= density <= 1:
        raise ValueError("density debe estar en [0, 1]")
    rng = random.Random(seed)
    return {
        node: {element for element in range(universe_size) if rng.random() < density}
        for node in range(n_nodes)
    }


def generate_concave_marginals(
    n_nodes: int, units_per_node: int, seed: int = 0
) -> list[list[float]]:
    _positive_int("n_nodes", n_nodes)
    _positive_int("units_per_node", units_per_node)
    rng = random.Random(seed)
    rows = []
    for _ in range(n_nodes):
        initial = rng.uniform(2.0, 10.0)
        decay = rng.uniform(0.05, 0.5)
        rows.append([max(0.0, initial - decay * unit) for unit in range(units_per_node)])
    return rows


def generate_graph(
    n_nodes: int, edge_probability: float = 0.1, seed: int = 0
) -> dict[int, set[int]]:
    _positive_int("n_nodes", n_nodes)
    if isinstance(edge_probability, bool) or not isinstance(edge_probability, (int, float)):
        raise ValueError("edge_probability debe estar en [0, 1]")
    if not math.isfinite(float(edge_probability)) or not 0 <= edge_probability <= 1:
        raise ValueError("edge_probability debe estar en [0, 1]")
    rng = random.Random(seed)
    graph = {node: set() for node in range(n_nodes)}
    for left in range(n_nodes):
        for right in range(left + 1, n_nodes):
            if rng.random() < edge_probability:
                graph[left].add(right)
                graph[right].add(left)
    return graph

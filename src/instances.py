"""Generadores de instancias sintéticas reproducibles."""
from __future__ import annotations
import random


def generate_coverage_instance(n_nodes: int, universe_size: int, density: float = 0.15, seed: int = 0):
    if n_nodes < 1 or universe_size < 1 or not 0 <= density <= 1:
        raise ValueError("Dimensiones positivas y density en [0,1] requeridas")
    rng = random.Random(seed)
    universe = set(range(universe_size))
    result = {}
    for node in range(n_nodes):
        subset = {element for element in universe if rng.random() < density}
        result[node] = subset
    return result


def generate_concave_marginals(n_nodes: int, units_per_node: int, seed: int = 0):
    if n_nodes < 1 or units_per_node < 1:
        raise ValueError("n_nodes y units_per_node deben ser positivos")
    rng = random.Random(seed)
    rows = []
    for _ in range(n_nodes):
        initial = rng.uniform(2.0, 10.0)
        decay = rng.uniform(0.05, 0.5)
        rows.append([max(0.0, initial - decay * j) for j in range(units_per_node)])
    return rows


def generate_graph(n_nodes: int, edge_probability: float = 0.1, seed: int = 0):
    if n_nodes < 1 or not 0 <= edge_probability <= 1:
        raise ValueError("n_nodes positivo y edge_probability en [0,1]")
    rng = random.Random(seed)
    graph = {i: set() for i in range(n_nodes)}
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if rng.random() < edge_probability:
                graph[i].add(j)
                graph[j].add(i)
    return graph

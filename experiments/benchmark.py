"""Benchmark reproducible de los algoritmos principales del proyecto.

Los métodos exactos se ejecutan únicamente en instancias pequeñas. Los tiempos
son descriptivos del entorno de ejecución y no constituyen pruebas asintóticas.
"""
from __future__ import annotations

import csv
import math
import os
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.allocation import brute_force_allocate, greedy_allocate
from src.instances import generate_concave_marginals, generate_coverage_instance, generate_graph
from src.selection import (
    exact_max_coverage,
    greedy_budgeted_coverage,
    greedy_max_coverage,
)
from src.simulation import run_rounds


def _measure(function, repetitions: int):
    samples = []
    for _ in range(repetitions):
        start = time.perf_counter()
        function()
        samples.append(time.perf_counter() - start)
    return {
        "seconds_median": statistics.median(samples),
        "seconds_mean": statistics.fmean(samples),
        "seconds_std": statistics.stdev(samples) if len(samples) > 1 else 0.0,
        "repetitions": repetitions,
    }


def _record(rows, algorithm, n, **metadata):
    rows.append({"algorithm": algorithm, "n": n, **metadata})


def run(repetitions: int = 7, output_dir: str | Path = ROOT / "results"):
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 1:
        raise ValueError("repetitions debe ser un entero positivo")

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    rows = []

    # Escalabilidad de los métodos voraces.
    for n in (20, 40, 80, 160, 320):
        budget = n * 20
        marginals = generate_concave_marginals(n, budget, seed=1000 + n)
        allocation_stats = _measure(lambda: greedy_allocate(marginals, budget), repetitions)
        _record(rows, "allocation_greedy", n, budget=budget, k="", universe_size="",
                quality_ratio="", **allocation_stats)

        universe_size = n * 10
        sets = generate_coverage_instance(n, universe_size, seed=2000 + n)
        k = max(1, n // 4)
        coverage_stats = _measure(lambda: greedy_max_coverage(sets, k), repetitions)
        _record(rows, "maximum_coverage_greedy", n, budget="", k=k,
                universe_size=universe_size, quality_ratio="", **coverage_stats)

        costs = {node: 1.0 + (node % 5) for node in sets}
        cost_budget = max(1.0, n * 1.5)
        budgeted_stats = _measure(
            lambda: greedy_budgeted_coverage(sets, costs, cost_budget), repetitions
        )
        _record(rows, "budgeted_coverage_greedy", n, budget=cost_budget, k="",
                universe_size=universe_size, quality_ratio="", **budgeted_stats)

        graph = generate_graph(n, edge_probability=0.08, seed=3000 + n)
        simulation_stats = _measure(
            lambda: run_rounds(
                sets, marginals, rounds=5, k=k, budget_per_round=min(budget, n * 5),
                failure_probability=0.1, seed=4000 + n, graph=graph, neighbor_alpha=0.02,
            ),
            repetitions,
        )
        _record(rows, "simulation_5_rounds", n, budget=budget, k=k,
                universe_size=universe_size, quality_ratio="", **simulation_stats)

    # Comparación con exacto en instancias pequeñas.
    for n, k in ((8, 2), (10, 3), (12, 4), (14, 4)):
        sets = generate_coverage_instance(n, n * 8, density=0.2, seed=5000 + n)
        greedy_result = greedy_max_coverage(sets, k)
        exact_result = exact_max_coverage(sets, k)
        ratio = (greedy_result.utility / exact_result.utility
                 if exact_result.utility else 1.0)
        greedy_stats = _measure(lambda: greedy_max_coverage(sets, k), repetitions)
        exact_stats = _measure(lambda: exact_max_coverage(sets, k), repetitions)
        _record(rows, "coverage_greedy_small", n, budget="", k=k,
                universe_size=n * 8, quality_ratio=ratio, **greedy_stats)
        _record(rows, "coverage_exact_small", n, budget="", k=k,
                universe_size=n * 8, quality_ratio=1.0, **exact_stats)

    # Comparación exacta de asignación en una instancia acotada.
    for n in (3, 4, 5):
        marginal_rows = generate_concave_marginals(n, 5, seed=6000 + n)
        budget = 5
        greedy_result = greedy_allocate(marginal_rows, budget)
        exact_result = brute_force_allocate(marginal_rows, budget)
        ratio = (greedy_result.utility / exact_result.utility
                 if exact_result.utility else 1.0)
        _record(
            rows, "allocation_greedy_small", n, budget=budget, k="", universe_size="",
            quality_ratio=ratio, **_measure(lambda: greedy_allocate(marginal_rows, budget), repetitions)
        )
        _record(
            rows, "allocation_exact_small", n, budget=budget, k="", universe_size="",
            quality_ratio=1.0, **_measure(lambda: brute_force_allocate(marginal_rows, budget), repetitions)
        )

    columns = [
        "algorithm", "n", "budget", "k", "universe_size", "quality_ratio",
        "repetitions", "seconds_median", "seconds_mean", "seconds_std",
    ]
    csv_path = output / "benchmark.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print(f"Matplotlib no está instalado; CSV generado en {csv_path}")
        return rows

    for algorithm in sorted({row["algorithm"] for row in rows}):
        subset = sorted(
            (row for row in rows if row["algorithm"] == algorithm),
            key=lambda row: row["n"],
        )
        plt.figure()
        plt.plot([row["n"] for row in subset],
                 [row["seconds_median"] for row in subset], marker="o")
        plt.xlabel("N (número de nodos)")
        plt.ylabel("Mediana del tiempo (segundos)")
        plt.title(algorithm)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output / f"{algorithm}.png")
        plt.close()

    print(f"Benchmark completado: {csv_path}")
    return rows


if __name__ == "__main__":
    run()

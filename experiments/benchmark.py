"""Benchmark reproducible de las complejidades O(B log N) y O(N*k)."""
from __future__ import annotations
import csv
import os
import statistics
import time
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.allocation import greedy_allocate
from src.instances import generate_concave_marginals, generate_coverage_instance
from src.selection import greedy_max_coverage


def run(repetitions: int = 3):
    os.makedirs("results", exist_ok=True)
    rows = []
    for n in (20, 40, 80, 160, 320):
        budget = n * 20
        marginals = generate_concave_marginals(n, budget, seed=n)
        samples = []
        for _ in range(repetitions):
            start = time.perf_counter(); greedy_allocate(marginals, budget); samples.append(time.perf_counter()-start)
        rows.append({"algorithm":"allocation_heap","n":n,"budget":budget,"k":"","seconds":statistics.median(samples)})

        universe_size = n * 10
        sets = generate_coverage_instance(n, universe_size, seed=n)
        k = max(1, n // 4)
        samples = []
        for _ in range(repetitions):
            start = time.perf_counter(); greedy_max_coverage(sets, k); samples.append(time.perf_counter()-start)
        rows.append({"algorithm":"maximum_coverage_greedy","n":n,"budget":"","k":k,"seconds":statistics.median(samples)})

    with open("results/benchmark.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
    try:
        import matplotlib.pyplot as plt
        for algorithm in {r["algorithm"] for r in rows}:
            subset = [r for r in rows if r["algorithm"] == algorithm]
            plt.figure(); plt.plot([r["n"] for r in subset], [r["seconds"] for r in subset], marker="o")
            plt.xlabel("N (número de nodos)"); plt.ylabel("Tiempo (segundos)"); plt.title(algorithm)
            plt.grid(True); plt.tight_layout(); plt.savefig(f"results/{algorithm}.png"); plt.close()
    except ImportError:
        print("matplotlib no está instalado; se generó únicamente el CSV")
    print("Resultados guardados en results/")

if __name__ == "__main__":
    run()

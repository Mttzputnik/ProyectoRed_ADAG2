"""Demostración ejecutable del Proyecto Red."""
from src.instances import generate_coverage_instance, generate_concave_marginals, generate_graph
from src.allocation import greedy_allocate
from src.selection import greedy_max_coverage, exact_max_coverage
from src.simulation import run_rounds


def main():
    n, universe_size, k, budget = 12, 60, 4, 18
    coverage = generate_coverage_instance(n, universe_size, seed=42)
    marginals = generate_concave_marginals(n, 8, seed=42)

    selection = greedy_max_coverage(coverage, k)
    allocation = greedy_allocate([marginals[i] for i in selection.selected], budget)
    exact = exact_max_coverage(coverage, k)
    print("=== Selección de nodos ===")
    print("Greedy:", selection.selected, "utilidad:", selection.utility)
    print("Óptimo exacto (instancia pequeña):", exact.selected, "utilidad:", exact.utility)
    print("Cociente greedy/óptimo:", selection.utility / exact.utility if exact.utility else 1.0)
    print("=== Reparto de presupuesto ===")
    print("Asignación por nodo seleccionado:", allocation.allocation)
    print("Utilidad de asignación:", allocation.utility)

    graph = generate_graph(n, seed=9)
    rounds = run_rounds(coverage, marginals, rounds=5, k=k, budget_per_round=budget,
                        failure_probability=0.1, seed=42, graph=graph, neighbor_alpha=0.02)
    print("=== Simulación multirronda ===")
    for result in rounds:
        print(result)

if __name__ == "__main__":
    main()

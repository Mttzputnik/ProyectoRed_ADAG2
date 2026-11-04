import math
import unittest

from src.allocation import brute_force_allocate, greedy_allocate
from src.instances import generate_concave_marginals, generate_coverage_instance
from src.selection import exact_max_coverage, greedy_budgeted_coverage, greedy_max_coverage
from src.simulation import run_rounds


class AllocationTests(unittest.TestCase):
    def test_greedy_matches_exact_small(self):
        rows = [[9, 6, 3], [8, 5, 2], [7, 4, 1]]
        self.assertAlmostEqual(greedy_allocate(rows, 5).utility, brute_force_allocate(rows, 5).utility)

    def test_heapify_handles_ties(self):
        result = greedy_allocate([[5, 3], [5, 2]], 2)
        self.assertEqual(sum(result.allocation), 2)
        self.assertEqual(result.utility, 10)

    def test_zero_budget(self):
        self.assertEqual(greedy_allocate([[2, 1], [3, 2]], 0).allocation, (0, 0))

    def test_budget_above_capacity(self):
        with self.assertRaises(ValueError):
            greedy_allocate([[2], [1]], 3)

    def test_rejects_negative_and_increasing_marginals(self):
        for rows in ([[-1]], [[1, 2]]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                greedy_allocate(rows, 1)

    def test_rejects_non_finite_marginals(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                greedy_allocate([[value]], 1)

    def test_rejects_invalid_budget_types(self):
        for value in (True, 1.5, "2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                greedy_allocate([[2, 1]], value)

    def test_rejects_boolean_or_string_marginals(self):
        for value in (True, "2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                greedy_allocate([[value]], 0)


class SelectionTests(unittest.TestCase):
    def test_greedy_is_bounded_by_exact(self):
        sets = {0: {1, 2, 3}, 1: {3, 4, 5}, 2: {6, 7}, 3: {1, 7, 8}}
        greedy = greedy_max_coverage(sets, 2)
        exact = exact_max_coverage(sets, 2)
        self.assertLessEqual(greedy.utility, exact.utility)
        self.assertEqual(len(greedy.selected), 2)

    def test_zero_k_and_empty_sets(self):
        sets = {"a": set(), "b": frozenset()}
        self.assertEqual(greedy_max_coverage(sets, 0).utility, 0)
        self.assertEqual(greedy_max_coverage(sets, 2).utility, 0)

    def test_budgeted_respects_budget(self):
        sets = {0: {1, 2, 3}, 1: {3, 4}, 2: {5, 6}}
        costs = {0: 3, 1: 2, 2: 2}
        result = greedy_budgeted_coverage(sets, costs, 4)
        self.assertLessEqual(sum(costs[node] for node in result.selected), 4)

    def test_budgeted_rejects_invalid_costs(self):
        sets = {"x": {1}, "y": {2}}
        for costs in ({"x": 0, "y": 1}, {"x": -1, "y": 1}, {"x": math.inf, "y": 1}):
            with self.subTest(costs=costs), self.assertRaises(ValueError):
                greedy_budgeted_coverage(sets, costs, 2)

    def test_budgeted_ties_follow_mapping_order(self):
        sets = {"first": {1}, "second": {2}}
        result = greedy_budgeted_coverage(sets, {"first": 1, "second": 1}, 1)
        self.assertEqual(result.selected, ("first",))

    def test_rejects_invalid_k(self):
        for k in (True, 1.5, -1, 3):
            with self.subTest(k=k), self.assertRaises(ValueError):
                greedy_max_coverage({0: {1}, 1: {2}}, k)


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.sets = generate_coverage_instance(8, 30, seed=3)
        self.gains = generate_concave_marginals(8, 5, seed=4)

    def test_rounds_reproducible(self):
        args = dict(rounds=3, k=3, budget_per_round=4, seed=7)
        self.assertEqual(run_rounds(self.sets, self.gains, **args),
                         run_rounds(self.sets, self.gains, **args))

    def test_probability_one_disables_all_nodes(self):
        results = run_rounds(self.sets, self.gains, rounds=2, k=3,
                             budget_per_round=4, failure_probability=1)
        self.assertTrue(all(not result.active_nodes for result in results))
        self.assertTrue(all(result.allocation == (0,) * 8 for result in results))

    def test_probability_zero_keeps_all_nodes(self):
        results = run_rounds(self.sets, self.gains, rounds=1, k=3,
                             budget_per_round=4, failure_probability=0)
        self.assertEqual(results[0].active_nodes, tuple(self.sets))

    def test_arbitrary_node_identifiers(self):
        sets = {"node-A": {1, 2}, "node-C": {2, 3}, "node-Z": {4}}
        gains = [[3, 2], [4, 2], [2, 1]]
        graph = {"node-A": {"node-C"}, "node-C": {"node-A"}, "node-Z": set()}
        results = run_rounds(sets, gains, rounds=2, k=2, budget_per_round=2,
                             graph=graph, neighbor_alpha=0.1)
        self.assertEqual(set(results[0].active_nodes), set(sets))
        self.assertEqual(len(results[0].allocation), 3)

    def test_rejects_unknown_graph_nodes(self):
        with self.assertRaises(ValueError):
            run_rounds({"a": {1}}, [[2, 1]], rounds=1, k=1,
                       budget_per_round=1, graph={"a": {"missing"}})

    def test_validates_marginals_for_failed_nodes_too(self):
        with self.assertRaises(ValueError):
            run_rounds({"a": {1}, "b": {2}}, [[2, 1], [1, 2]],
                       rounds=1, k=1, budget_per_round=1, failure_probability=1)

    def test_rejects_invalid_parameters(self):
        for kwargs in (
            {"rounds": 0, "k": 1, "budget_per_round": 1},
            {"rounds": 1, "k": True, "budget_per_round": 1},
            {"rounds": 1, "k": 1, "budget_per_round": -1},
            {"rounds": 1, "k": 1, "budget_per_round": 1, "failure_probability": float("nan")},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                run_rounds(self.sets, self.gains, **kwargs)


if __name__ == "__main__":
    unittest.main()

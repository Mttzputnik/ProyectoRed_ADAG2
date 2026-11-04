import unittest
from src.allocation import greedy_allocate, brute_force_allocate
from src.instances import generate_coverage_instance, generate_concave_marginals
from src.selection import greedy_max_coverage, exact_max_coverage, greedy_budgeted_coverage
from src.simulation import run_rounds


class AllocationTests(unittest.TestCase):
    def test_greedy_matches_exact_small(self):
        rows = [[9, 6, 3], [8, 5, 2], [7, 4, 1]]
        self.assertAlmostEqual(greedy_allocate(rows, 5).utility, brute_force_allocate(rows, 5).utility)

    def test_invalid_nonconcave(self):
        with self.assertRaises(ValueError):
            greedy_allocate([[1, 2]], 1)


class SelectionTests(unittest.TestCase):
    def test_greedy_valid_and_bounded_by_optimum(self):
        sets = {0: {1,2,3}, 1: {3,4,5}, 2: {6,7}, 3: {1,7,8}}
        greedy = greedy_max_coverage(sets, 2)
        exact = exact_max_coverage(sets, 2)
        self.assertLessEqual(greedy.utility, exact.utility)
        self.assertEqual(len(greedy.selected), 2)

    def test_budgeted_respects_budget(self):
        sets = {0:{1,2,3}, 1:{3,4}, 2:{5,6}}
        result = greedy_budgeted_coverage(sets, {0:3,1:2,2:2}, 4)
        self.assertLessEqual(sum({0:3,1:2,2:2}[n] for n in result.selected), 4)


class SimulationTests(unittest.TestCase):
    def test_rounds_reproducible(self):
        sets = generate_coverage_instance(8, 30, seed=3)
        gains = generate_concave_marginals(8, 5, seed=4)
        a = run_rounds(sets, gains, rounds=3, k=3, budget_per_round=4, seed=7)
        b = run_rounds(sets, gains, rounds=3, k=3, budget_per_round=4, seed=7)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 3)


if __name__ == "__main__":
    unittest.main()

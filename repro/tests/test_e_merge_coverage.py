import itertools
import unittest

from repro.src.verify_e_merge_coverage import run_cases, worst_case_tail_probability


class EMergeCoverageTests(unittest.TestCase):
    def test_exact_enumerations_pass_and_invalid_control_fails(self):
        summary = run_cases()["summary"]
        self.assertTrue(summary["all_merged_expectations_exact"])
        self.assertTrue(summary["all_markov_coverage_events_pass"])
        self.assertTrue(summary["all_arbitrary_dependence_coverage_pass"])
        self.assertTrue(summary["all_randomized_uniform_coverage_events_pass"])
        self.assertTrue(summary["all_randomized_arbitrary_dependence_coverage_pass"])
        self.assertTrue(summary["invalid_scaling_control_detected"])
        self.assertTrue(summary["invalid_arbitrary_dependence_detected"])
        self.assertEqual(summary["case_count"], 8)
        self.assertEqual(summary["equal_weight_case_count"], 2)
        self.assertEqual(summary["nonuniform_weight_case_count"], 6)
        self.assertEqual(summary["invalid_arbitrary_dependence_rejection_count"], 4)
        self.assertEqual(
            summary["invalid_randomized_arbitrary_dependence_rejection_count"], 8
        )
        self.assertEqual(summary["invalid_scaling_control_rejection_count"], 2)
        self.assertTrue(summary["adaptive_weight_control_detected"])
        self.assertEqual(summary["adaptive_weight_rejection_count"], 8)
        self.assertEqual(summary["adaptive_randomized_weight_rejection_count"], 8)
        self.assertGreater(summary["minimum_adaptive_tail_to_alpha_ratio"], 1.0)
        self.assertLessEqual(summary["maximum_valid_tail_to_alpha_ratio"], 1.0)
        self.assertLessEqual(
            summary["maximum_valid_randomized_tail_to_alpha_ratio"], 1.0
        )

    def test_two_fold_lp_matches_independent_permutation_enumeration(self):
        values = [0.0, 0.5, 2.0]
        threshold = 1.0
        lp_tail, variable_count = worst_case_tail_probability(
            values, 2, threshold, weights=(0.5, 0.5)
        )
        brute_tail = max(
            sum(
                0.5 * values[row] + 0.5 * values[column] >= threshold
                for row, column in enumerate(permutation)
            )
            / len(values)
            for permutation in itertools.permutations(range(len(values)))
        )
        self.assertEqual(variable_count, len(values) ** 2)
        self.assertAlmostEqual(lp_tail, brute_tail, places=12)

        randomized_lp_tail, randomized_variable_count = worst_case_tail_probability(
            values,
            2,
            threshold,
            weights=(0.5, 0.5),
            randomized_uniform_threshold=True,
        )
        randomized_brute_tail = max(
            sum(
                min((0.5 * values[row] + 0.5 * values[column]) / threshold, 1.0)
                for row, column in enumerate(permutation)
            )
            / len(values)
            for permutation in itertools.permutations(range(len(values)))
        )
        self.assertEqual(randomized_variable_count, len(values) ** 2)
        self.assertAlmostEqual(randomized_lp_tail, randomized_brute_tail, places=12)

    def test_lp_rejects_invalid_weight_vectors(self):
        with self.assertRaises(ValueError):
            worst_case_tail_probability([0.0, 1.0], 2, 1.0, weights=(1.0,))
        with self.assertRaises(ValueError):
            worst_case_tail_probability([0.0, 1.0], 2, 1.0, weights=(-0.1, 1.1))
        with self.assertRaises(ValueError):
            worst_case_tail_probability([0.0, 1.0], 2, 1.0, weights=(0.4, 0.4))

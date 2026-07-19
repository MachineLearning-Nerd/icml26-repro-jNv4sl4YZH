import unittest

from repro.src.verify_e_merge_coverage import run_cases


class EMergeCoverageTests(unittest.TestCase):
    def test_exact_enumerations_pass_and_invalid_control_fails(self):
        summary = run_cases()["summary"]
        self.assertTrue(summary["all_merged_expectations_exact"])
        self.assertTrue(summary["all_markov_coverage_events_pass"])
        self.assertTrue(summary["all_arbitrary_dependence_coverage_pass"])
        self.assertTrue(summary["invalid_scaling_control_detected"])
        self.assertTrue(summary["invalid_arbitrary_dependence_detected"])
        self.assertEqual(summary["invalid_arbitrary_dependence_rejection_count"], 2)
        self.assertEqual(summary["invalid_scaling_control_rejection_count"], 1)
        self.assertTrue(summary["adaptive_weight_control_detected"])
        self.assertEqual(summary["adaptive_weight_rejection_count"], 6)
        self.assertGreater(summary["minimum_adaptive_tail_to_alpha_ratio"], 1.0)
        self.assertLessEqual(summary["maximum_valid_tail_to_alpha_ratio"], 1.0)

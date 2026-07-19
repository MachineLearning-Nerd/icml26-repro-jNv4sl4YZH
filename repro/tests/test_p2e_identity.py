import unittest

from repro.src.verify_p2e_identity import evaluate_case, run_cases


class P2EIdentityTests(unittest.TestCase):
    def test_p2e_exactly_preserves_each_finite_rank_set(self):
        for alpha in (0.05, 0.1, 0.2):
            for n_calibration in (10, 20, 30, 50, 100, 200):
                row = evaluate_case(n_calibration, alpha)
                self.assertEqual(row["set_mismatches"], 0)
                self.assertLess(row["expectation_abs_error"], 1e-11)
                self.assertTrue(row["p2e_strictly_positive"])

    def test_classic_calibrator_controls_expand_the_set(self):
        row = evaluate_case(100, 0.1)
        self.assertTrue(all(value > 0 for value in row["classic_control_extra_members"].values()))

    def test_full_grid_summary_passes(self):
        summary = run_cases()["summary"]
        self.assertTrue(summary["all_set_identities_pass"])
        self.assertTrue(summary["all_exact_e_expectations_pass"])
        self.assertTrue(summary["all_positive_pass"])
        self.assertTrue(summary["all_classic_controls_inflate_sets"])

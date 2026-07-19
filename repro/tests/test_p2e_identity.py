import unittest

from repro.src.verify_p2e_identity import (
    EXCLUDED_DOMAIN_CASES,
    THEOREM_CASES,
    evaluate_case,
    in_theorem_domain,
    p2e_parameters,
    run_cases,
)


class P2EIdentityTests(unittest.TestCase):
    def test_p2e_exactly_preserves_each_finite_rank_set(self):
        self.assertEqual(len(THEOREM_CASES), 18)
        for n_calibration, alpha in THEOREM_CASES:
            row = evaluate_case(n_calibration, alpha)
            self.assertTrue(row["theorem_domain_verified"])
            self.assertEqual(row["set_mismatches"], 0)
            self.assertLess(row["threshold_log_error"], 1e-14)
            self.assertLess(row["expectation_abs_error"], 1e-11)
            self.assertTrue(row["p2e_strictly_positive"])

    def test_paper_theorem_domain_is_fail_closed(self):
        self.assertEqual(len(EXCLUDED_DOMAIN_CASES), 5)
        for n_calibration, alpha in EXCLUDED_DOMAIN_CASES:
            self.assertFalse(in_theorem_domain(n_calibration, alpha))
            with self.assertRaises(ValueError):
                p2e_parameters(n_calibration, alpha)

    def test_classic_calibrator_controls_expand_the_set(self):
        row = evaluate_case(100, 0.1)
        self.assertTrue(all(value > 0 for value in row["classic_control_extra_members"].values()))

    def test_full_grid_summary_passes(self):
        summary = run_cases()["summary"]
        self.assertTrue(summary["all_set_identities_pass"])
        self.assertTrue(summary["all_threshold_identities_pass"])
        self.assertTrue(summary["all_exact_e_expectations_pass"])
        self.assertTrue(summary["all_positive_pass"])
        self.assertTrue(summary["all_classic_controls_inflate_sets"])
        self.assertTrue(summary["all_theorem_domain_verified"])
        self.assertTrue(summary["all_domain_controls_rejected"])
        self.assertEqual(summary["case_count"], 18)
        self.assertEqual(summary["classic_control_case_count"], 18)
        self.assertEqual(summary["domain_control_count"], 5)

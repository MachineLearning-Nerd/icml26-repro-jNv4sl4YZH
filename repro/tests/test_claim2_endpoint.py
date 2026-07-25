from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from repro.src.verify_claim2_endpoint import (
    ALPHA_CASES,
    aon,
    build_result,
    endpoint_counterexample,
)


class Claim2EndpointTests(unittest.TestCase):
    def test_symbolic_endpoint_witness_differs_only_at_zero(self):
        for alpha in ALPHA_CASES:
            self.assertNotEqual(
                endpoint_counterexample(alpha, Fraction(0, 1)),
                aon(alpha, Fraction(0, 1)),
            )
            for denominator in (3, 7, 19, 101):
                for numerator in range(1, denominator + 1):
                    p = Fraction(numerator, denominator)
                    self.assertEqual(
                        endpoint_counterexample(alpha, p),
                        aon(alpha, p),
                    )

    def test_complete_claim_contract_and_controls_pass(self):
        result = build_result(0.0)
        self.assertEqual(result["verdict"], "FALSIFIED")
        self.assertTrue(
            result["counterexample"]["satisfies_every_printed_assumption"]
        )
        self.assertTrue(result["counterexample"]["contradicts_uniqueness"])
        self.assertTrue(result["negative_controls_pass"])

    def test_independent_checker_fails_closed_on_tampering(self):
        root = Path(__file__).resolve().parents[2]
        result = build_result(0.0)
        result["finite_exact_cross_checks"][0][
            "conformal_membership_mismatches_n_1_through_500"
        ] = 1
        with tempfile.TemporaryDirectory() as temporary:
            input_path = Path(temporary) / "tampered.json"
            output_path = Path(temporary) / "check.json"
            input_path.write_text(json.dumps(result), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(root / "repro/src/check_claim2_endpoint.py"),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            checked = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(checked["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()

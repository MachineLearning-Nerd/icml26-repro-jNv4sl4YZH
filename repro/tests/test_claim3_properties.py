from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from repro.src.verify_claim3_properties import analytic_case


class Claim3PropertiesTests(unittest.TestCase):
    def test_representative_analytic_certificate(self):
        result = analytic_case(100, 0.1)
        self.assertTrue(result["theorem_domain"])
        self.assertLess(result["expectation_abs_error"], 1e-11)
        self.assertTrue(result["all_derivatives_strictly_negative"])
        self.assertTrue(result["all_values_strictly_positive"])
        self.assertLess(result["maximum_inverse_roundtrip_error"], 1e-10)
        self.assertTrue(result["strict_pointwise_dominance_except_p_equals_alpha"])

    def test_independent_checker_fails_closed_on_tampered_aon_count(self):
        root = Path(__file__).resolve().parents[2]
        evidence = json.loads(
            (root / "outputs/claim3_properties_fullscale.json").read_text(
                encoding="utf-8"
            )
        )
        evidence["fullscale_direct_AoN"]["strictly_shorter_count"] = 8
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "tampered.json"
            output = Path(temporary) / "checked.json"
            source.write_text(json.dumps(evidence), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(root / "repro/src/check_claim3_properties.py"),
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["status"],
                "FAIL",
            )


if __name__ == "__main__":
    unittest.main()

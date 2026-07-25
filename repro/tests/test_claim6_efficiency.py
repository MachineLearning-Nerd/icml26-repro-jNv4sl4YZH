from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class Claim6EfficiencyTests(unittest.TestCase):
    def test_checker_rejects_missing_eccp_comparison(self):
        root = Path(__file__).resolve().parents[2]
        evidence = json.loads(
            (root / "outputs/claim6_full_protocol.json").read_text(encoding="utf-8")
        )
        evidence["eccp_full_protocol"]["comparison_count"] = 35
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "invalid.json"
            output = Path(temporary) / "checked.json"
            source.write_text(json.dumps(evidence), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(root / "repro/src/check_claim6_efficiency.py"),
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                ],
                check=False,
                cwd=root,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["status"],
                "FAIL",
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class Claim5WECATests(unittest.TestCase):
    def test_checker_rejects_missing_adaptive_control(self):
        root = Path(__file__).resolve().parents[2]
        evidence = json.loads(
            (root / "outputs/claim5_weca_full_protocol.json").read_text(
                encoding="utf-8"
            )
        )
        evidence["negative_controls"]["all_pass"] = False
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "invalid.json"
            output = Path(temporary) / "checked.json"
            source.write_text(json.dumps(evidence), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(root / "repro/src/check_claim5_weca.py"),
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

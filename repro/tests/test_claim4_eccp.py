from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class Claim4ECCPTests(unittest.TestCase):
    def test_checker_rejects_toy_row_count(self):
        root = Path(__file__).resolve().parents[2]
        evidence = json.loads(
            (root / "outputs/claim4_eccp_full_protocol.json").read_text(
                encoding="utf-8"
            )
        )
        evidence["full_protocol"]["raw_rows"] = 100
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "toy.json"
            output = Path(temporary) / "checked.json"
            source.write_text(json.dumps(evidence), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(root / "repro/src/check_claim4_eccp.py"),
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

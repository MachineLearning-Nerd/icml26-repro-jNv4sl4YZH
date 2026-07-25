from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class Claim1ReleaseTests(unittest.TestCase):
    def test_checker_rejects_membership_tampering(self):
        root = Path(__file__).resolve().parents[2]
        cleanroom = json.loads(
            (root / "outputs/claim1_independent.json").read_text(encoding="utf-8")
        )
        cleanroom["cases"][0]["set_mismatches"] = 1
        with tempfile.TemporaryDirectory() as temporary:
            clean_path = Path(temporary) / "clean.json"
            checked_path = Path(temporary) / "checked.json"
            clean_path.write_text(json.dumps(cleanroom), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(root / "repro/src/check_claim1_release.py"),
                    "--cleanroom",
                    str(clean_path),
                    "--source",
                    str(root / "outputs/claim1_source_crosscheck.json"),
                    "--output",
                    str(checked_path),
                ],
                check=False,
                cwd=root,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(
                json.loads(checked_path.read_text(encoding="utf-8"))["status"],
                "FAIL",
            )


if __name__ == "__main__":
    unittest.main()

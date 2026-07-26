from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from repro.src.audit_judge_prompt_visibility import (
    CAPSULE_END_MARKER,
    CAPSULE_MARKER,
    CLAIM_MARKERS,
    audit,
)


class JudgePromptVisibilityTest(unittest.TestCase):
    def make_tree(self, root: Path, include_capsule: bool) -> None:
        (root / "pages").mkdir(parents=True)
        (root / "pages/index.md").write_text("# Index\n", encoding="utf-8")
        (root / "pages/claim-1").mkdir()
        (root / "pages/claim-1/page.md").write_text(
            "# Historical rejected baseline\n" + ("x" * 120_000),
            encoding="utf-8",
        )
        if include_capsule:
            capsule = root / "pages/00-current-evidence"
            capsule.mkdir()
            capsule.joinpath("page.md").write_text(
                "\n".join(
                    [CAPSULE_MARKER, *CLAIM_MARKERS, CAPSULE_END_MARKER]
                ),
                encoding="utf-8",
            )

    def test_capsule_precedes_large_historical_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "parent"
            candidate = root / "candidate"
            self.make_tree(parent, include_capsule=False)
            self.make_tree(candidate, include_capsule=True)
            result = audit(candidate, parent)
            self.assertEqual(result["status"], "PASS")
            self.assertTrue(result["candidate"]["all_six_claim_markers_visible"])

    def test_tampered_historical_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "parent"
            candidate = root / "candidate"
            self.make_tree(parent, include_capsule=False)
            self.make_tree(candidate, include_capsule=True)
            candidate.joinpath("pages/claim-1/page.md").write_text(
                "# changed\n", encoding="utf-8"
            )
            result = audit(candidate, parent)
            self.assertEqual(result["status"], "FAIL")
            self.assertIn(
                "pages/claim-1/page.md",
                result["historical_subset"]["protected_changed"],
            )


if __name__ == "__main__":
    unittest.main()

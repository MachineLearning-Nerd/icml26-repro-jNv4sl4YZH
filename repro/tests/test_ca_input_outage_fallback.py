from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import openml

from repro.src.verify_ca_inputs import ROOT, verify_inputs


class CAInputOutageFallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(
            (ROOT / "repro/configs/ca_input_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.attestation = ROOT / "outputs/ca_input_audit.json"

    @mock.patch("repro.src.verify_ca_inputs.openml.tasks.get_task")
    def test_server_5xx_uses_exact_pinned_attestation(self, get_task) -> None:
        get_task.side_effect = openml.exceptions.OpenMLServerError(
            "upstream unavailable\nStatus code: 504"
        )
        result = verify_inputs(
            ROOT / "upstream", self.manifest, fallback_path=self.attestation
        )
        self.assertEqual(
            result["verification_mode"],
            "hash-pinned-prior-live-openml-attestation",
        )
        self.assertFalse(result["live_openml_available"])
        self.assertEqual(result["tasks"], self.manifest["tasks"])

    @mock.patch("repro.src.verify_ca_inputs.openml.tasks.get_task")
    def test_tampered_attestation_fails_closed(self, get_task) -> None:
        get_task.side_effect = openml.exceptions.OpenMLServerError(
            "upstream unavailable\nStatus code: 504"
        )
        tampered = json.loads(self.attestation.read_text(encoding="utf-8"))
        tampered["tasks"][0]["X_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tampered.json"
            path.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_inputs(
                    ROOT / "upstream", self.manifest, fallback_path=path
                )

    @mock.patch("repro.src.verify_ca_inputs.openml.tasks.get_task")
    def test_non_server_error_never_uses_fallback(self, get_task) -> None:
        get_task.side_effect = openml.exceptions.OpenMLServerError(
            "not found\nStatus code: 404"
        )
        with self.assertRaises(openml.exceptions.OpenMLServerError):
            verify_inputs(
                ROOT / "upstream", self.manifest, fallback_path=self.attestation
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path

from repro.src.publication_gate import (
    EXPECTED_CA_PROTOCOL,
    EXPECTED_CCP_PROTOCOL,
    SOURCE_COMMIT,
    assert_exact_ca_protocol,
    assert_exact_ccp_protocol,
    hygiene_gate,
    sha256,
    validate_evidence,
)


ROOT = Path(__file__).resolve().parents[2]


class PublicationEvidenceTests(unittest.TestCase):
    def test_saved_evidence_has_one_authoritative_verdict(self) -> None:
        endpoint = json.loads(
            (ROOT / "outputs/claim2_endpoint_counterexample.json").read_text()
        )
        final_cells = json.loads(
            (ROOT / "outputs/final_logbook_cells.json").read_text()
        )
        self.assertEqual(endpoint["verdict"], "FALSIFIED")
        self.assertTrue(endpoint["counterexample"]["satisfies_every_printed_assumption"])
        self.assertEqual(final_cells["summary"]["verified_claims"], 5)
        self.assertEqual(final_cells["summary"]["falsified_claims"], 1)
        self.assertIn("FALSIFIED", final_cells["claim_2"])

    def test_protocol_contracts_are_exact(self) -> None:
        ca = json.loads((ROOT / "outputs/claim2_independent.json").read_text())
        ccp = json.loads((ROOT / "outputs/claim3_independent.json").read_text())
        assert_exact_ca_protocol(ca["protocol"])
        assert_exact_ccp_protocol(ccp["protocol"])
        self.assertEqual(ca["rows_seen"], 1920)
        self.assertEqual(ccp["rows_seen"], 11700)
        self.assertEqual(EXPECTED_CA_PROTOCOL["M"], 512)
        self.assertEqual(EXPECTED_CCP_PROTOCOL["execution_adapter"], "vectorized-exact-postprocessing-v1")

    def test_source_artifacts_and_manifest_are_pinned(self) -> None:
        source = json.loads((ROOT / "repro/configs/source_manifest.json").read_text())
        self.assertEqual(source["git_commit"], SOURCE_COMMIT)
        self.assertEqual(
            sha256("sources/arxiv-v1/source.tar.gz"),
            "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db",
        )
        self.assertEqual(
            sha256("sources/arxiv-v1/main.tex"),
            "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857",
        )

    def test_publication_gate_evidence_contract_passes(self) -> None:
        result = validate_evidence()
        self.assertEqual(result["verified_claims"], 5)
        self.assertEqual(result["falsified_claims"], 1)
        self.assertEqual(result["ca_rows"], 1920)
        self.assertEqual(result["ccp_rows"], 11700)

    def test_canonical_tree_has_no_private_publisher_state(self) -> None:
        result = hygiene_gate()
        self.assertEqual(result["forbidden_paths"], [])
        self.assertEqual(result["env_files"], [])
        self.assertEqual(result["secret_hits"], [])
        self.assertEqual(result["absolute_path_hits"], [])


if __name__ == "__main__":
    unittest.main()

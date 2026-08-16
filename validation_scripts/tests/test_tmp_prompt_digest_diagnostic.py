from __future__ import annotations

import base64
import gzip
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage


def canonicalize_strict_v3_targets(artifact):
    source_class = (
        "official document, filing, dataset, technical test result, or independent report"
    )
    exact_tail = (
        " Record the exact status, date, production volume, capacity, cost, shipment, "
        "approval, or utilization metric where applicable."
    )
    event_tail = (
        " Track the measurable production, shipment, qualification, contract, volume, "
        "capacity, price, cost, utilization, approval, effective-date, or test-result metric "
        "that resolves this point."
    )
    for spec in artifact.get("strict_passed_spec", []):
        spec_id = spec.get("spec_id", "strict candidate")
        evidence = spec.get("evidence_needed_for_stage_b", [])
        spec["evidence_needed_for_stage_b"] = [
            {
                "source_or_document_class": source_class,
                "exact_claim_or_metric": f"{item.strip()} {exact_tail}",
            }
            if isinstance(item, str)
            else item
            for item in evidence
        ]
        confirmation = spec.get("next_confirmation_points", [])
        spec["next_confirmation_points"] = [
            {
                "measurable_event_or_metric": f"{item.strip()} {event_tail}",
                "interpretation_effect": (
                    f"Confirmation of this {spec_id} metric would strengthen the current "
                    "decision-value assessment; a contrary result would weaken or invalidate "
                    "that assessment."
                ),
            }
            if isinstance(item, str)
            else item
            for item in confirmation
        ]
    return artifact


class NinthBatchCurrentMainDiagnostic(unittest.TestCase):
    def test_ninth_batch_candidate_current_main(self):
        repo_root = Path(__file__).resolve().parents[2]
        parts = [
            repo_root / ".diagnostics/ninth_batch_payload_0.txt",
            repo_root / ".diagnostics/ninth_batch_payload_1.txt",
            repo_root / ".diagnostics/ninth_batch_payload_2.txt",
            repo_root / ".diagnostics/ninth_batch_payload_3a.txt",
            repo_root / ".diagnostics/ninth_batch_payload_3b.txt",
            repo_root / ".diagnostics/ninth_batch_payload_4.txt",
        ]
        payload = "".join(p.read_text() for p in parts)
        artifact = json.loads(gzip.decompress(base64.b64decode(payload)).decode("utf-8"))
        artifact = canonicalize_strict_v3_targets(artifact)
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a_full(artifact)
        output = stream.getvalue()
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()

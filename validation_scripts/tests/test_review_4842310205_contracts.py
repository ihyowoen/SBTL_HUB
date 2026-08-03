"""Regression coverage for Codex review 4842310205.

The suite locks real-host chronology evidence, resolved-target Related
deduplication, and phrase-level generic evidence detection.
"""

from __future__ import annotations

import copy
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)
from validation_scripts.tests.test_review_4841890896_contracts import (
    TestReview4841890896Contracts,
)


class TestReview4842310205Contracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_concrete_additional_data_center_target_passes(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "additional data center capacity for Project Alpha",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_generic_additional_data_placeholder_still_fails(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "additional data needed",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("evidence_needed_for_stage_b entries must identify", output)

    def test_placeholder_chronology_url_does_not_waive_inversion(self):
        parent, child = TestReview4841890896Contracts().provisional_cards(True)
        child["related_lineage"]["follow_up_date_precedes_predecessor_justification"]["evidence_source_urls"] = ["https://..."]
        by_id = {"PARENT_FINAL": parent, "CHILD_FINAL": child}
        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])
        errors, _ = related.check_card(
            child,
            by_id,
            require_contract=True,
            allow_provisional_related=True,
            provisional_by_id=provisional_by_id,
            ambiguous_provisional_ids=ambiguous,
        )
        self.assertIn(
            "follow-up chronology evidence_source_urls must contain parseable HTTP(S) URLs with a real host",
            errors,
        )
        self.assertIn(
            "follow-up date precedes provisional predecessor PARENT_SPEC",
            errors,
        )

    def test_http_scheme_without_host_is_rejected(self):
        self.assertFalse(related._valid_http_url("https://"))
        self.assertFalse(related._valid_http_url("https://..."))
        self.assertTrue(related._valid_http_url("https://example.com/filing"))

    def test_aliases_resolving_to_same_related_card_are_rejected(self):
        parent = {
            "id": "PARENT_FINAL",
            "card_id": "PARENT_ALIAS",
            "date": "2026-08-01",
        }
        child = {
            "id": "CHILD_FINAL",
            "date": "2026-08-02",
            "related": ["PARENT_FINAL", "PARENT_ALIAS"],
            "related_lineage": {
                "status": "PASS",
                "relation_type": "program_lineage",
                "related_ids": ["PARENT_FINAL", "PARENT_ALIAS"],
                "reason": "Both aliases refer to the same intended program predecessor.",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
            },
        }
        by_id = {
            "PARENT_FINAL": parent,
            "PARENT_ALIAS": parent,
            "CHILD_FINAL": child,
        }
        errors, _ = related.check_card(child, by_id, require_contract=True)
        self.assertIn(
            "related aliases resolve to duplicate target: PARENT_FINAL, PARENT_ALIAS",
            errors,
        )


if __name__ == "__main__":
    unittest.main()

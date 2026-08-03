from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4845534152Contracts(unittest.TestCase):
    """Regression coverage for the three validator edge cases in this review."""

    def base_v3_spec(self):
        return copy.deepcopy(TestReview4840844831Contracts().base_spec())

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_conflicting_malformed_provisional_arrays_fail_without_type_error(self):
        parent = {"draft_id": "PD", "source_spec_id": "PS"}
        child = {
            "id": "CHILD",
            "related": [],
            "related_candidate_spec_ids": ["PD", {}],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "program_lineage",
                "related_candidate_spec_ids": ["PS", []],
            },
        }
        errors, _ = related.check_card(
            child,
            {"CHILD": child},
            require_contract=True,
            allow_provisional_related=True,
            provisional_by_id={"PD": parent, "PS": parent},
        )
        self.assertTrue(any("before deduplication" in error for error in errors), errors)
        self.assertTrue(any("non-empty strings" in error for error in errors), errors)

    def test_source_class_compounds_and_inflections_are_accepted(self):
        for source_class in ("금융감독원 공시자료", "SEC filings"):
            with self.subTest(source_class=source_class):
                spec = self.base_v3_spec()
                spec["evidence_needed_for_stage_b"] = [{
                    "source_or_document_class": source_class,
                    "exact_claim_or_metric": "2027 revenue",
                }]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 0, output)

    def test_unofficial_does_not_match_official(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "unofficial rumor",
            "exact_claim_or_metric": "2027 revenue",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1, output)

    def test_none_format_risk_sentinel_is_treated_as_empty(self):
        spec = self.base_v3_spec()
        spec["format_risk_tags"] = ["none"]
        spec["structural_value_override_applied"] = False
        for field in lineage.STAGE_A_V3_OVERRIDE_REQUIRED:
            spec[field] = [] if field in {"anchor_classes", "evidence_needed_for_stage_b", "next_confirmation_points"} else None
        spec["execution_anchor_type"] = "production_start"
        spec["execution_anchor_strength"] = "strong"
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import io
import unittest
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4841207046Contracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_placeholder_narratives_fail_closed(self):
        for placeholder in ("not provided", "not provided yet", "N/A", "정보 없음"):
            with self.subTest(placeholder=placeholder):
                spec = copy.deepcopy(self.base_spec())
                for field in lineage.STAGE_A_V3_NARRATIVE_FIELDS:
                    spec[field] = placeholder
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn("must be item-specific narrative text", output)

    def test_meaningless_structured_evidence_target_fails(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "xx",
            "exact_claim_or_metric": "yy",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("source/document class and an exact claim", output)

    def test_meaningless_structured_confirmation_fails(self):
        spec = copy.deepcopy(self.base_spec())
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "xx",
            "interpretation_effect": "yy",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("measurable events or metrics", output)

    def test_concise_role_valid_structured_values_still_pass(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "2027 revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "2027 revenue",
            "interpretation_effect": "confirm thesis",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_merge_prep_rejects_provisional_edges_regardless_of_state(self):
        parent = {"id": "PARENT", "date": "2026-08-01"}
        child = {
            "id": "CHILD",
            "date": "2026-08-02",
            "related": ["PARENT"],
            "related_candidate_spec_ids": ["DRAFT_OTHER"],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "program_lineage",
                "related_ids": ["PARENT"],
                "reason": "Final edge exists but one provisional edge is still unresolved.",
            },
        }
        errors, warnings = related.check_card(
            child,
            {"PARENT": parent, "CHILD": child},
            require_contract=True,
            allow_provisional_related=False,
        )
        self.assertEqual(warnings, [])
        self.assertIn(
            "unresolved related_candidate_spec_ids remain after merge prep",
            errors,
        )


if __name__ == "__main__":
    unittest.main()

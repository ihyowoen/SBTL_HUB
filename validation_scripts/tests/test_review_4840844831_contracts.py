from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840783305_contracts import (
    TestReview4840783305Contracts,
)

ROOT = Path(__file__).resolve().parents[2]
STAGE_A_PROMPT = ROOT / "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md"

CANONICAL_STAGE_A_FIELDS = (
    "structural_value_override_reason",
    "anchor_classes",
    "incremental_information",
    "decision_relevance",
    "baseline_expectation_changed",
    "evidence_needed_for_stage_b",
    "next_confirmation_points",
    "why_execution_event_not_required",
    "prior_state",
    "new_verified_fact",
    "changed_judgment",
    "uncertainty_resolved",
    "remaining_uncertainty",
)


class TestReview4840844831Contracts(unittest.TestCase):
    def base_spec(self):
        spec = TestReview4840783305Contracts().valid_stage_a_spec()
        spec["uncertainty_resolved"] = "The final rule resolves whether the eligibility condition is mandatory."
        spec["remaining_uncertainty"] = "Implementation timing remains subject to the final agency guidance."
        return spec

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_stage_a_producer_enumerates_complete_exactly_one_route_contract(self):
        text = STAGE_A_PROMPT.read_text(encoding="utf-8")
        schema_start = text.index("Each strict_passed_spec must include:")
        schema_end = text.index("stage_b_requirement_note must state:", schema_start)
        schema = text[schema_start:schema_end]
        for field in CANONICAL_STAGE_A_FIELDS:
            self.assertIn(field, schema)

        route_start = text.index("Anchor-route contract for `strict_passed_spec[]`:")
        route_end = text.index("Each review_pool item must include:", route_start)
        route = text[route_start:route_end]
        self.assertIn("exactly one route must be complete", route)
        self.assertIn("Partial execution metadata", route)
        self.assertIn("both a source/document/dataset/transcript/filing/test/report class", route)
        self.assertIn("measurable event or metric", route)

    def test_complete_structured_v3_route_passes(self):
        result, output = self.run_stage_a(self.base_spec())
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_generic_evidence_variants_are_rejected(self):
        for generic in (
            "official sources for confirmation",
            "more evidence on adoption",
            "additional data needed for the claim",
        ):
            with self.subTest(generic=generic):
                spec = copy.deepcopy(self.base_spec())
                spec["evidence_needed_for_stage_b"] = [generic]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn("source/document class and an exact claim", output)

    def test_non_measurable_confirmation_variants_are_rejected(self):
        for generic in (
            "additional confirmation from the market",
            "more evidence will be needed later",
            "company commentary may provide context",
        ):
            with self.subTest(generic=generic):
                spec = copy.deepcopy(self.base_spec())
                spec["next_confirmation_points"] = [generic]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn("measurable events or metrics", output)

    def test_missing_uncertainty_chain_is_rejected(self):
        spec = self.base_spec()
        spec.pop("remaining_uncertainty")
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("incomplete V3 override package missing remaining_uncertainty", output)


if __name__ == "__main__":
    unittest.main()

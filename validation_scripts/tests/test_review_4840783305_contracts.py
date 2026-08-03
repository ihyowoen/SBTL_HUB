from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage

ROOT = Path(__file__).resolve().parents[2]
FINAL_QC = ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md"
MERGE_PREP = ROOT / "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md"

# Final QC and merge prep must preserve the same canonical package, while the
# Stage A validator accepts exactly one complete execution or V3 route.
CANONICAL_V3_FIELDS = (
    "structural_value_override_reason",
    "anchor_classes[]",
    "incremental_information",
    "decision_relevance",
    "baseline_expectation_changed",
    "evidence_needed_for_stage_b[]",
    "next_confirmation_points[]",
    "why_execution_event_not_required",
    "prior_state",
    "new_verified_fact",
    "changed_judgment",
)


class TestReview4840783305Contracts(unittest.TestCase):
    def test_final_qc_and_merge_prep_preserve_full_canonical_package(self):
        final_text = FINAL_QC.read_text(encoding="utf-8")
        merge_text = MERGE_PREP.read_text(encoding="utf-8")
        final_start = final_text.index("For every format-risk `publish_ready[]` item with `selected_anchor_path = v3_non_execution`")
        final_end = final_text.index("- evidence_complete: true", final_start)
        final_block = final_text[final_start:final_end]
        merge_start = merge_text.index("For `selected_anchor_path: v3_non_execution`")
        merge_end = merge_text.index("If metadata is missing", merge_start)
        merge_block = merge_text[merge_start:merge_end]
        for field in CANONICAL_V3_FIELDS:
            self.assertIn(field, final_block)
            self.assertIn(field, merge_block)

    def test_merge_prep_consumes_stage_07c_governance_proof(self):
        text = MERGE_PREP.read_text(encoding="utf-8")
        section_start = text.index("### 2A. Stage 0.7C governance-preflight consumer gate")
        section_end = text.index("## 3. Ordinary-run operations", section_start)
        section = text[section_start:section_end]
        for field in (
            "governing_contracts_read[]",
            "governing_contracts_same_revision: true",
            "v3_contract_preflight_passed: true",
            "prompt_0_8_authorized: true",
            "BLOCKED_STAGE_0_7C_GOVERNANCE_PREFLIGHT_INVALID",
        ):
            self.assertIn(field, section)
        for path in (
            "docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md",
            "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
            "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md",
            "docs/RELATED_LIFECYCLE_CONTRACT.md",
        ):
            self.assertIn(path, section)

    def valid_stage_a_spec(self):
        return {
            "spec_id": "SPEC_V3_001",
            "source_story_ids": ["STORY_1"],
            "strict_pass_gate": {"status": "pass", "reason": "all gates", "all_six_conditions_passed": True},
            "enhanced_selector_precision_version": "v3",
            "selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
            "strict_gate_check": "pass",
            "format_risk_tags": ["interview"],
            "baseline_relation": "new",
            "duplicate_risk": "low",
            "staleness_decision": "current",
            "source_access_risk": "low",
            "stage_a_evidence_status": "not_evidence_complete_no_fetch",
            "stage_b_evidence_package_required": True,
            "primary_url_semantics": "provided_source_candidate_not_evidence",
            "same_event_source_cluster": "cluster-1",
            "support_source_candidates": [],
            "source_domain_candidates": [],
            "source_diversity_path": {"status": "planned"},
            "source_cluster_preserved": True,
            "structural_value_override_applied": True,
            "structural_value_override_reason": "The verified policy change alters market-access eligibility for this project.",
            "anchor_classes": ["policy_regulatory_anchor"],
            "incremental_information": "The eligibility rule changed from discretionary to mandatory screening.",
            "decision_relevance": "The change alters supplier qualification and timing decisions.",
            "baseline_expectation_changed": "The baseline changed from discretionary eligibility to mandatory screening.",
            "evidence_needed_for_stage_b": ["Official rule text confirming the eligibility clause and effective date"],
            "next_confirmation_points": ["Publication of implementing guidance with the final effective date"],
            "why_execution_event_not_required": "The operative legal eligibility change is decision-useful before a commercial execution event.",
            "prior_state": "Eligibility was uncertain under draft guidance.",
            "new_verified_fact": "The final rule establishes the new eligibility condition.",
            "changed_judgment": "Market-access probability is now lower for non-compliant suppliers.",
            "uncertainty_resolved": "The final rule resolves whether the eligibility condition is mandatory.",
            "remaining_uncertainty": "Implementation timing remains subject to the final agency guidance.",
        }

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_stage_a_validator_accepts_complete_non_execution_route(self):
        result, output = self.run_stage_a(self.valid_stage_a_spec())
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_stage_a_validator_rejects_incomplete_or_dual_route(self):
        incomplete = self.valid_stage_a_spec()
        incomplete.pop("structural_value_override_reason")
        result, output = self.run_stage_a(incomplete)
        self.assertEqual(result, 1)
        self.assertIn("incomplete V3 override package", output)

        dual = copy.deepcopy(self.valid_stage_a_spec())
        dual["execution_anchor_type"] = "commercial_award"
        dual["execution_anchor_strength"] = "strong"
        result, output = self.run_stage_a(dual)
        self.assertEqual(result, 1)
        self.assertIn("requires exactly one complete execution or v3_non_execution path", output)


if __name__ == "__main__":
    unittest.main()

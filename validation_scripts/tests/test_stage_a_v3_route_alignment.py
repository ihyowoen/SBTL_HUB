from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage


class TestStageAV3RouteAlignment(unittest.TestCase):
    def base_non_execution_spec(self):
        return {
            "spec_id": "SPEC_V3_ROUTE_001",
            "source_story_ids": ["STORY_1"],
            "strict_pass_gate": {
                "status": "pass",
                "reason": "all gates",
                "all_six_conditions_passed": True,
            },
            "enhanced_selector_precision_version": "v3",
            "selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
            "structural_selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
            "strict_gate_check": "pass",
            "format_risk_tags": ["none"],
            "execution_anchor_type": None,
            "execution_anchor_strength": None,
            "baseline_relation": "new",
            "duplicate_risk": "low",
            "staleness_decision": "current",
            "source_access_risk": "low",
            "stage_a_evidence_status": "not_evidence_complete_no_fetch",
            "stage_b_evidence_package_required": True,
            "primary_url_semantics": "provided_source_candidate_not_evidence",
            "same_event_source_cluster": [
                {
                    "story_id": "STORY_1",
                    "url": "https://example.com/story",
                    "preserve_for_stage_b": True,
                }
            ],
            "support_source_candidates": [],
            "source_domain_candidates": ["example.com"],
            "source_diversity_path": {
                "status": "viable",
                "probable_independent_owner_count": 1,
                "official_or_source_owner_candidate_present": True,
                "independent_confirmation_candidate_present": False,
                "context_candidate_present": False,
            },
            "source_cluster_preserved": True,
            "structural_value_override_applied": True,
            "structural_value_override_reason": (
                "Official trade-flow data changes the near-term supply-availability judgment."
            ),
            "anchor_classes": ["data_financial_anchor"],
            "incremental_information": (
                "The newly published monthly dataset shows a material change in physical export flow."
            ),
            "decision_relevance": (
                "The trade-flow change alters near-term sourcing and supply-security decisions."
            ),
            "baseline_expectation_changed": (
                "The baseline shifts from policy-only concern to observed physical-flow evidence."
            ),
            "evidence_needed_for_stage_b": [
                "Official customs dataset confirming July 2026 rare-earth export tonnage and publication date"
            ],
            "next_confirmation_points": [
                "August 2026 customs export volume would confirm or weaken the persistence judgment"
            ],
            "why_execution_event_not_required": (
                "Official trade-flow data directly changes supply-demand judgment without a corporate execution event."
            ),
            "prior_state": "The prior view relied mainly on export-control policy signals.",
            "new_verified_fact": "The monthly customs dataset reports a lower July export volume.",
            "changed_judgment": "Near-term external supply availability is now assessed as tighter.",
            "uncertainty_resolved": "The direction of July physical export flow is measurable.",
            "remaining_uncertainty": "Persistence into August and product-level composition remain uncertain.",
        }

    def execution_spec(self):
        spec = self.base_non_execution_spec()
        spec.update(
            {
                "spec_id": "SPEC_EXEC_ROUTE_001",
                "format_risk_tags": ["product_news"],
                "execution_anchor_type": "production_start",
                "execution_anchor_strength": "strong",
                "structural_value_override_applied": False,
                "structural_value_override_reason": None,
                "why_execution_event_not_required": None,
                "anchor_classes": [
                    "execution_event_anchor",
                    "technology_commercialization_anchor",
                ],
                "incremental_information": (
                    "The product moved from introduction into an actual production-start state."
                ),
                "decision_relevance": (
                    "The production start changes commercialization and customer-availability judgment."
                ),
                "baseline_expectation_changed": (
                    "The baseline moves from product roadmap to current manufacturing execution."
                ),
                "evidence_needed_for_stage_b": [
                    "Company filing confirming the production start date and exact product model"
                ],
                "next_confirmation_points": [
                    "Named customer shipment volume would strengthen the commercialization judgment"
                ],
                "prior_state": "The product had been presented as a future commercial offering.",
                "new_verified_fact": "The company now reports production start for the named product.",
                "changed_judgment": "Commercial availability is more advanced than previously assumed.",
                "uncertainty_resolved": "The manufacturing stage is no longer only a roadmap claim.",
                "remaining_uncertainty": "Customer shipments and production volume remain unverified.",
            }
        )
        spec.pop("structural_selector_policy_version", None)
        return spec

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_ordinary_non_execution_route_is_valid(self):
        result, output = self.run_stage_a(self.base_non_execution_spec())
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_non_execution_route_requires_structural_selector_lineage(self):
        spec = self.base_non_execution_spec()
        spec.pop("structural_selector_policy_version")
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("structural_selector_policy_version must be STRUCTURAL_NEWS_VALUE_SELECTION_V3", output)

    def test_non_execution_route_rejects_duplicate_anchor_classes(self):
        spec = self.base_non_execution_spec()
        spec["anchor_classes"] = ["data_financial_anchor", "data_financial_anchor"]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("anchor_classes must be unique", output)

    def test_non_execution_route_rejects_falsey_noncanonical_execution_identity(self):
        for field, value in (
            ("execution_anchor_type", 0),
            ("execution_anchor_strength", False),
        ):
            with self.subTest(field=field):
                spec = self.base_non_execution_spec()
                spec[field] = value
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1, output)
                self.assertIn(f"requires canonical empty {field}", output)

    def test_malformed_format_risk_tags_are_not_sanitized(self):
        for tags in ([None], [123], [""], ["none", None]):
            with self.subTest(tags=tags):
                spec = self.base_non_execution_spec()
                spec["format_risk_tags"] = tags
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1, output)

    def test_format_risk_execution_route_retains_shared_v3_metadata(self):
        result, output = self.run_stage_a(self.execution_spec())
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_execution_route_requires_every_shared_v3_field(self):
        for field in lineage.STAGE_A_SHARED_STRICT_REQUIRED:
            with self.subTest(field=field):
                spec = self.execution_spec()
                spec.pop(field)
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1, output)
                self.assertIn(
                    f"execution route missing shared V3 field {field}",
                    output,
                )

    def test_execution_route_requires_execution_event_anchor_class(self):
        spec = self.execution_spec()
        spec["anchor_classes"] = ["technology_commercialization_anchor"]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1, output)
        self.assertIn(
            "execution route anchor_classes must include execution_event_anchor",
            output,
        )

    def test_execution_route_requires_explicit_false_marker(self):
        for marker in (None, "false", 0):
            with self.subTest(marker=marker):
                spec = self.execution_spec()
                if marker is None:
                    spec.pop("structural_value_override_applied")
                else:
                    spec["structural_value_override_applied"] = marker
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1, output)
                self.assertIn("requires structural_value_override_applied=false", output)

    def test_execution_route_rejects_true_override_only_metadata(self):
        spec = self.execution_spec()
        spec["structural_value_override_reason"] = (
            "This should not be populated when structural_value_override_applied is false."
        )
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("execution route must leave override-only field structural_value_override_reason empty", output)

    def test_dual_route_remains_invalid(self):
        spec = copy.deepcopy(self.base_non_execution_spec())
        spec["execution_anchor_type"] = "production_start"
        spec["execution_anchor_strength"] = "strong"
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("requires exactly one complete execution or v3_non_execution path", output)


if __name__ == "__main__":
    unittest.main()

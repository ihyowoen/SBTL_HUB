#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from card_audit_utils import (
    canonical_domain,
    canonical_url,
    is_landing_page,
    load_owner_registry,
    source_audit_measure,
    source_owner,
)
from date_role_freshness_check import check_card as check_date_card
from related_lifecycle_check import check_card
from recompute_source_audit_metadata import recompute
from run_workflow_contract_suite import validate_scope


class AuditUtilsTest(unittest.TestCase):
    def test_canonical_url_removes_tracking_and_mobile_prefix(self):
        self.assertEqual(
            canonical_url("https://m.Example.com/a/?utm_source=x&b=2"),
            "https://example.com/a?b=2",
        )

    def test_domain_and_owner_are_distinct_concepts(self):
        domains = {
            canonical_domain("https://pv-magazine-india.com/a"),
            canonical_domain("https://ess-news.com/b"),
            canonical_domain("https://business-standard.com/c"),
        }
        owners = {"pv_magazine_group", "business-standard.com"}
        self.assertEqual(len(domains), 3)
        self.assertEqual(len(owners), 2)

    def test_landing_page(self):
        self.assertTrue(is_landing_page("https://example.com/"))
        self.assertFalse(is_landing_page("https://example.com/2026/07/article"))

    def test_conditional_syndication_registry(self):
        payload = {
            "rules": [
                {
                    "owner_id": "bloomberg_syndication",
                    "domains": ["theedgemalaysia.com"],
                    "requires_metadata_contains_any": ["bloomberg"],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "owners.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            registry = load_owner_registry(path)
            syndicated = {
                "source_url": "https://theedgemalaysia.com/node/1",
                "source_owner_id_normalized": "bloomberg_syndication",
            }
            independent = {
                "source_url": "https://theedgemalaysia.com/node/2",
                "source_origin_type": "independent_media",
            }
            self.assertEqual(source_owner(syndicated, registry), "bloomberg_syndication")
            self.assertEqual(source_owner(independent, registry), "theedgemalaysia.com")

    def test_blank_source_url_is_not_counted_as_diversity(self):
        card = {
            "fact_sources": [
                {
                    "source_url": "https://example.com/article",
                    "evidence_role": "primary_event_evidence",
                    "supports": ["fact"],
                },
                {
                    "source_url": "",
                    "evidence_role": "secondary_event_evidence",
                    "supports": ["fact"],
                },
            ]
        }
        measure = source_audit_measure(card, {})
        self.assertEqual(measure["source_evidence_entry_count"], 2)
        self.assertEqual(measure["source_unique_url_count"], 1)
        self.assertEqual(measure["source_unique_domain_count"], 1)
        self.assertEqual(measure["source_independent_owner_count"], 1)
        self.assertEqual(measure["visible_source_url_count"], 1)
        self.assertEqual(measure["missing_visible_source_url_count"], 1)
        self.assertNotIn("https://", measure["canonical_urls"])
        self.assertNotIn("", measure["canonical_domains"])
        self.assertNotIn("", measure["independent_owners"])


class SourceAuditRecomputeTest(unittest.TestCase):
    def test_recompute_preserves_rejected_discovery_rows(self):
        card = {
            "source_spec_id": "TEST",
            "fact_sources": [
                {
                    "source_name": "Official",
                    "source_url": "https://example.gov/article",
                    "source_quote": "Body quote",
                    "source_quote_status": "official_material_quote_verified",
                    "evidence_role": "primary_event_evidence",
                    "supports": ["fact"],
                    "source_origin_type": "government_primary",
                    "claim": "Event occurred",
                }
            ],
            "source_discovery_ledger": [
                {
                    "source_url": "https://media.example/rejected",
                    "outcome": "rejected_wrong_event",
                    "reason": "different event",
                }
            ],
        }
        _, updated, _ = recompute(card, {}, True)
        outcomes = [row.get("outcome") for row in updated["source_discovery_ledger"]]
        self.assertIn("used_in_fact_sources", outcomes)
        self.assertIn("rejected_wrong_event", outcomes)
        used = next(
            row for row in updated["source_discovery_ledger"]
            if row.get("outcome") == "used_in_fact_sources"
        )
        self.assertEqual(used["source_domain"], "example.gov")


class DateRoleContractTest(unittest.TestCase):
    def test_valid_date_role(self):
        card = {
            "date": "2026-07-01",
            "related_lineage": {
                "relation_type": "distinct_follow_up",
                "fresh_follow_up_anchor": "commissioning",
            },
            "date_role": {
                "representative_date": "2026-07-01",
                "event_date": "2026-07-01",
                "publication_dates": ["2026-07-02"],
                "earliest_same_event_date_checked": True,
                "event_date_source_url": "https://example.com/article",
                "event_date_source_quote": "commissioned on July 1",
            },
        }
        self.assertEqual(check_date_card(card, True), [])

    def test_follow_up_requires_anchor(self):
        card = {
            "date": "2026-07-01",
            "related_lineage": {"relation_type": "distinct_follow_up"},
            "date_role": {
                "representative_date": "2026-07-01",
                "event_date": "2026-07-01",
                "publication_dates": ["2026-07-02"],
                "earliest_same_event_date_checked": True,
                "event_date_source_url": "https://example.com/article",
                "event_date_source_quote": "event date",
            },
        }
        self.assertTrue(
            any(
                "fresh_follow_up_anchor" in error
                for error in check_date_card(card, True)
            )
        )


class RelatedContractTest(unittest.TestCase):
    def setUp(self):
        self.parent = {"id": "2026-05-01_US_01", "date": "2026-05-01", "related": []}
        self.child = {
            "id": "2026-07-01_US_01",
            "date": "2026-07-01",
            "state": "publish_ready",
            "publish_ready": True,
            "related": [self.parent["id"]],
            "related_lineage": {
                "status": "PASS",
                "relation_type": "distinct_follow_up",
                "related_ids": [self.parent["id"]],
                "reason": "contract followed by commissioning",
                "fresh_follow_up_anchor_class": "execution_event_anchor",
                "fresh_follow_up_anchor": "commissioning",
                "incremental_fact_vs_predecessor": "Commissioning is now source-confirmed.",
                "changed_judgment_vs_predecessor": "The project moved from contracted to operating-stage evidence.",
                "related_candidate_spec_ids": [],
            },
        }
        self.by_id = {self.parent["id"]: self.parent, self.child["id"]: self.child}

    def test_valid_follow_up(self):
        self.child["related_lineage"]["same_event_checked"] = True
        self.child["related_lineage"]["earliest_same_event_date_checked"] = True
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertEqual(errors, [])

    def test_strict_contract_requires_review_flags(self):
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("same_event_checked" in error for error in errors))

    def test_distinct_follow_up_requires_valid_anchor_class(self):
        self.child["related_lineage"]["same_event_checked"] = True
        self.child["related_lineage"]["earliest_same_event_date_checked"] = True
        self.child["related_lineage"].pop("fresh_follow_up_anchor_class")
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("fresh_follow_up_anchor_class" in error for error in errors))

    def test_distinct_follow_up_rejects_invalid_anchor_class(self):
        self.child["related_lineage"]["same_event_checked"] = True
        self.child["related_lineage"]["earliest_same_event_date_checked"] = True
        self.child["related_lineage"]["fresh_follow_up_anchor_class"] = "generic_topic_anchor"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("fresh_follow_up_anchor_class" in error for error in errors))

    def test_distinct_follow_up_requires_incremental_fact(self):
        self.child["related_lineage"]["same_event_checked"] = True
        self.child["related_lineage"]["earliest_same_event_date_checked"] = True
        self.child["related_lineage"]["incremental_fact_vs_predecessor"] = ""
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("incremental_fact_vs_predecessor" in error for error in errors))

    def test_distinct_follow_up_requires_changed_judgment(self):
        self.child["related_lineage"]["same_event_checked"] = True
        self.child["related_lineage"]["earliest_same_event_date_checked"] = True
        self.child["related_lineage"]["changed_judgment_vs_predecessor"] = ""
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("changed_judgment_vs_predecessor" in error for error in errors))

    def test_legacy_mode_does_not_require_v2_follow_up_fields(self):
        child = deepcopy(self.child)
        child["related_lineage"].pop("fresh_follow_up_anchor_class")
        child["related_lineage"].pop("incremental_fact_vs_predecessor")
        child["related_lineage"].pop("changed_judgment_vs_predecessor")
        by_id = {self.parent["id"]: self.parent, child["id"]: child}
        errors, _ = check_card(child, by_id, False)
        strict_field_names = (
            "fresh_follow_up_anchor_class",
            "incremental_fact_vs_predecessor",
            "changed_judgment_vs_predecessor",
        )
        self.assertFalse(any(any(name in error for name in strict_field_names) for error in errors))

    def test_legacy_mode_still_requires_fresh_follow_up_anchor(self):
        child = deepcopy(self.child)
        child["related_lineage"].pop("fresh_follow_up_anchor")
        by_id = {self.parent["id"]: self.parent, child["id"]: child}
        errors, _ = check_card(child, by_id, False)
        self.assertTrue(any("fresh_follow_up_anchor" in error for error in errors))

    def test_duplicate_cannot_publish(self):
        self.child["related_lineage"]["relation_type"] = "same_event_duplicate"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("may not use" in error for error in errors))

    def test_non_cardable_relation_rejected_before_publish_state(self):
        child = deepcopy(self.child)
        child.pop("state")
        child.pop("publish_ready")
        child["related_lineage"]["relation_type"] = "same_event_duplicate"
        child["related_lineage"]["same_event_checked"] = True
        child["related_lineage"]["earliest_same_event_date_checked"] = True
        by_id = {self.parent["id"]: self.parent, child["id"]: child}
        errors, _ = check_card(child, by_id, True)
        self.assertTrue(any("validated new-card output" in error for error in errors))

    def test_unrelated_must_not_have_related(self):
        self.child["related_lineage"]["relation_type"] = "new_unrelated_event"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("empty related" in error for error in errors))


class SuiteScopeTest(unittest.TestCase):
    def write_json(self, directory: str, name: str, payload) -> str:
        path = Path(directory) / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    def test_scope_requires_all_requested_ids_to_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            cards = self.write_json(
                tmp,
                "cards.json",
                {"cards": [{"id": "A"}, {"id": "B"}]},
            )
            ids = self.write_json(tmp, "ids.json", ["A", "MISSING"])
            result = validate_scope(cards, ids)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["json"]["matched_card_count"], 1)
            self.assertEqual(result["json"]["missing_ids"], ["MISSING"])

    def test_scope_rejects_zero_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            cards = self.write_json(tmp, "cards.json", {"cards": [{"id": "A"}]})
            ids = self.write_json(tmp, "ids.json", ["MISSING"])
            result = validate_scope(cards, ids)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["json"]["matched_card_count"], 0)
            self.assertTrue(any("zero cards" in error for error in result["json"]["errors"]))

    def test_scope_rejects_empty_id_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            cards = self.write_json(tmp, "cards.json", {"cards": [{"id": "A"}]})
            ids = self.write_json(tmp, "ids.json", [])
            result = validate_scope(cards, ids)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("empty" in error for error in result["json"]["errors"]))

    def test_scope_passes_when_all_ids_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            cards = self.write_json(
                tmp,
                "cards.json",
                {"cards": [{"id": "A"}, {"id": "B"}]},
            )
            ids = self.write_json(tmp, "ids.json", ["A", "B"])
            result = validate_scope(cards, ids)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["json"]["requested_id_count"], 2)
            self.assertEqual(result["json"]["matched_card_count"], 2)


class StructuralV3PromptRegressionTest(unittest.TestCase):
    def read_prompt(self, relative_path: str) -> str:
        return (ROOT.parent / relative_path).read_text(encoding="utf-8")

    def test_stage_b_has_ten_required_docs_and_no_execution_only_blockers(self):
        text = self.read_prompt("docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md")
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertIn("list all 10 required docs", text)
        self.assertNotIn("All 8 documents above are mandatory.", text)
        self.assertNotIn("list all 8 required docs", text)
        self.assertNotIn("format has no concrete execution anchor", text)
        self.assertNotIn("format-risk item has no fetched evidence for a concrete execution anchor", text)
        self.assertIn("neither a fetched source-backed concrete execution anchor nor a complete fetched source-backed V3 non-execution Structural Value Override package", text)
        self.assertIn("has fetched evidence for neither a concrete execution anchor nor a complete V3 non-execution Structural Value Override package", text)

    def test_final_qc_overlay_accepts_both_source_backed_paths(self):
        text = self.read_prompt("docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md")
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertIn("list all 10 required docs", text)
        self.assertNotIn("All 8 documents above are mandatory.", text)
        self.assertNotIn("list all 8 required docs", text)
        self.assertNotIn("without a concrete fresh execution anchor, they must not have entered", text)
        self.assertNotIn("the execution anchor is explicitly covered by `fact_sources` and `source_claim_coverage_map`;", text)
        self.assertIn("without either a concrete fresh execution anchor or a complete V3 non-execution Structural Value Override", text)
        self.assertIn("exactly one source-backed path is complete", text)
        self.assertIn("lineage_and_anchor_guard.anchor_path_qc_passed: true", text)


class StructuralV3InterveningStageContractTest(unittest.TestCase):
    @staticmethod
    def read_prompt(path: str) -> str:
        return (ROOT.parent / path).read_text(encoding="utf-8")

    def test_stage_c_uses_two_path_anchor_gate(self):
        text = self.read_prompt("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertIn("Pass 2A — Anchor-path check for format-risk cards", text)
        self.assertIn("exactly one source-backed path", text)
        self.assertIn("structural_value_override_qc_status", text)
        self.assertNotIn("item lacks a concrete execution anchor", text)
        self.assertNotIn("without a concrete execution anchor", text)

    def test_evidence_qc_emits_route_specific_anchor_results(self):
        text = self.read_prompt("docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md")
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertIn("anchor_path_qc_summary", text)
        self.assertIn("execution_anchor_qc_status", text)
        self.assertIn("structural_value_override_qc_status", text)
        self.assertNotIn("without a concrete fresh execution anchor", text)
        self.assertNotIn("Execution-anchor evidence check", text)

    def test_content_polish_produces_final_qc_guard_schema(self):
        text = self.read_prompt("docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md")
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertIn("anchor_path_qc_passed", text)
        self.assertIn("selected_anchor_path", text)
        self.assertIn("execution_anchor_qc_status", text)
        self.assertIn("structural_value_override_qc_status", text)
        self.assertIn("non_applicable_anchor_path_reason", text)
        self.assertNotIn('"execution_anchor_qc_passed": true', text)
        self.assertNotIn("without a concrete fresh execution anchor", text)

    def test_stage_c_and_baseline_revalidation_preserve_anchor_path(self):
        stage_c = self.read_prompt("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        baseline = self.read_prompt("docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md")
        self.assertIn("Each accepted_fact_safe item must include:", stage_c)
        self.assertIn("anchor_path_validation", stage_c)
        self.assertIn("All 10 documents above are mandatory.", baseline)
        self.assertIn("copy Stage C `anchor_path_validation` byte-for-byte", baseline)
        self.assertIn("anchor_path_preservation_summary", baseline)
        self.assertIn("anchor_path_preserved", baseline)

    def test_production_and_remediation_accept_both_anchor_paths(self):
        production = self.read_prompt("docs/llm_prompts/v1/11_PROMPT_0_9_Production_Verification.md")
        remediation = self.read_prompt("docs/llm_prompts/v1/12_PROMPT_1_0_Remediation.md")
        for text in (production, remediation):
            self.assertIn("All 10 documents above are mandatory.", text)
            self.assertIn("exactly one source-backed route", text)
            self.assertIn("valid V3 non-execution route", text)
            self.assertNotIn("without a concrete fresh execution anchor, they must not have entered", text)
        self.assertIn("v3_non_execution_path_cards_checked_count", production)
        self.assertIn("anchor_path_defect_confirmed", remediation)

    def test_final_qc_consumes_route_status_schema(self):
        text = self.read_prompt("docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md")
        self.assertIn("execution_anchor_qc_status", text)
        self.assertIn("structural_value_override_qc_status", text)
        self.assertIn("non_applicable_anchor_path_reason", text)
        self.assertNotIn("execution_anchor_qc_passed: true` or `structural_value_override_qc_passed: true", text)


class StructuralV3MergePrepAndRevisionContractTest(unittest.TestCase):
    @staticmethod
    def read_prompt(path: str) -> str:
        return (ROOT.parent / path).read_text(encoding="utf-8")

    def test_merge_prep_accepts_both_v3_routes(self):
        canonical = self.read_prompt("docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md")
        legacy = self.read_prompt("docs/llm_prompts/v1/legacy/10_PROMPT_0_8_GitHub_Merge_Prep_LEGACY_BODY.md")
        self.assertIn("V3 anchor-path merge-prep gate", canonical)
        self.assertIn("selected_anchor_path: execution", canonical)
        self.assertIn("selected_anchor_path: v3_non_execution", canonical)
        self.assertIn("anchor_path_lineage_passed", canonical)
        self.assertIn("Anchor-path and selector-lineage safety overlay — V3", legacy)
        self.assertIn("exactly one source-backed route passed Final QC", legacy)
        self.assertNotIn("without a concrete fresh execution anchor, they must not have entered", legacy)

    def test_stage_c_allows_unresolved_route_only_for_revise_required(self):
        text = self.read_prompt("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        self.assertIn("For every accepted_fact_safe format-risk item", text)
        self.assertIn("A revise_required format-risk item may use", text)
        self.assertIn('"selected_anchor_path": "unresolved"', text)
        self.assertIn('"anchor_path_qc_passed": false', text)
        self.assertIn("must not enter `accepted_fact_safe[]`", text)
        self.assertNotIn("For every accepted_fact_safe or revise_required format-risk item", text)


class StructuralV3Review4838187744RegressionTest(unittest.TestCase):
    @staticmethod
    def read_prompt(path: str) -> str:
        return (ROOT.parent / path).read_text(encoding="utf-8")

    def test_final_qc_publish_ready_emits_route_metadata(self):
        text = self.read_prompt("docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md")
        self.assertIn("For every format-risk `publish_ready[]` item", text)
        for field in (
            "selected_anchor_path: execution|v3_non_execution",
            "anchor_path_qc_passed: true",
            "execution_anchor_qc_status: pass|not_applicable",
            "structural_value_override_qc_status: pass|not_applicable",
            "non_applicable_anchor_path_reason",
        ):
            self.assertIn(field, text)

    def test_revise_loop_preserves_and_validates_anchor_path(self):
        stage_b_revise = self.read_prompt("docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md")
        stage_c_revise = self.read_prompt("docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md")
        for text in (stage_b_revise, stage_c_revise):
            self.assertIn("All 10 documents above are mandatory.", text)
            self.assertNotIn("All 8 documents above are mandatory.", text)
            self.assertIn("anchor_path_validation", text)
        self.assertIn("anchor_path_resolution_action: preserved|resolved_from_unresolved", stage_b_revise)
        self.assertIn("accepted_with_v3_non_execution_path_count", stage_c_revise)

    def test_stage_c_uses_canonical_anchor_classes_array(self):
        text = self.read_prompt("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        self.assertIn("`anchor_classes[]` containing at least one valid non-execution anchor class", text)
        self.assertNotIn("one valid non-execution `anchor_class`", text)

    def test_retrospective_accepts_complete_v3_override(self):
        text = self.read_prompt("docs/llm_prompts/v1/13_PROMPT_1_1_Retrospective.md")
        self.assertIn("without either a source-backed concrete execution anchor or a complete V3 non-execution Structural Value Override package", text)
        self.assertIn("unless either a source-backed concrete battery/grid/ESS/EV/materials execution anchor or a complete V3 non-execution Structural Value Override package is present", text)
        self.assertNotIn("without a hard commercial/policy event", text)
        self.assertNotIn("unless a concrete battery/grid/ESS/EV/materials execution anchor is present", text)


class RelatedMalformedAnchorClassTest(unittest.TestCase):
    def test_unhashable_anchor_class_returns_validation_error(self):
        parent = {"id": "PARENT", "date": "2026-01-01", "related": []}
        child = {
            "id": "CHILD",
            "date": "2026-02-01",
            "state": "publish_ready",
            "publish_ready": True,
            "related": ["PARENT"],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "distinct_follow_up",
                "related_ids": ["PARENT"],
                "reason": "new development",
                "fresh_follow_up_anchor": "new evidence",
                "fresh_follow_up_anchor_class": ["execution_event_anchor"],
                "incremental_fact_vs_predecessor": "New evidence is available.",
                "changed_judgment_vs_predecessor": "The assessment changed.",
            },
        }
        errors, _ = check_card(child, {"PARENT": parent, "CHILD": child}, True)
        self.assertTrue(any("fresh_follow_up_anchor_class" in error for error in errors))


class FinalQcV3PackageContractTest(unittest.TestCase):
    def test_final_qc_preserves_complete_v3_package_for_publish_ready(self):
        prompt = (ROOT.parent / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md").read_text(encoding="utf-8")
        required = [
            "selected_anchor_path = v3_non_execution",
            "structural_value_override_applied: true",
            "anchor_classes[]",
            "evidence_needed_for_stage_b[]",
            "why_execution_event_not_required",
            "prior_state",
            "new_verified_fact",
            "changed_judgment",
            "must remain available to Prompt 0.8",
        ]
        for token in required:
            self.assertIn(token, prompt)


if __name__ == "__main__":
    unittest.main()

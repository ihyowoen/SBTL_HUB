from __future__ import annotations

import base64
import hashlib
import json
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHUNK_DIR = Path(__file__).resolve().parent / "fixtures"
EXPECTED_SHA256 = "7597e6bb4716c0764081d4255b11d1b2b84733620cfcffad7d40ea4b3d7274e7"
EXPECTED_IDS = {
    "STD26_A_007", "STD26_A_011", "STD26_A_023", "STD26_A_035",
    "STD26_A_036", "STD26_A_049", "STD26_A_056",
}
CHUNK_NAMES = [
    "stage_b_revise_r1_0_7c_rescue7_payload_00.txt",
    "stage_b_revise_r1_0_7c_rescue7_payload_01.txt",
    "stage_b_revise_r1_0_7c_rescue7_payload_02.txt",
    "stage_b_revise_r1_0_7c_rescue7_payload_03.txt",
]
CARD_REQUIRED = [
    "revision_pass", "previous_draft_id", "revised_draft_id", "source_spec_id",
    "source_story_ids", "region", "date", "cat", "sub_cat", "signal", "title",
    "sub", "gate", "fact", "implication", "urls", "related", "fact_sources",
    "anchor_path_validation", "anchor_path_resolution_action", "stage_b_revise_only",
    "publish_ready", "revision_change_log", "remaining_risks", "needs_stage_c_recheck",
    "strict_pass_gate", "enhanced_selector_precision_version", "selector_policy_version",
    "strict_gate_check", "format_risk_tags", "execution_anchor_type",
    "execution_anchor_strength", "baseline_relation", "duplicate_risk",
    "staleness_decision", "source_access_risk", "stage_a_evidence_status",
    "stage_b_evidence_package_required", "primary_url_semantics",
]
V3_REQUIRED = [
    "structural_value_override_applied", "structural_value_override_reason",
    "anchor_classes", "evidence_needed_for_stage_b", "why_execution_event_not_required",
    "prior_state", "new_verified_fact", "changed_judgment", "uncertainty_resolved",
    "remaining_uncertainty", "incremental_information", "baseline_expectation_changed",
    "decision_relevance", "next_confirmation_points",
]
DOWNSTREAM_FALSE = [
    "accepted_fact_safe", "addable_merge_safe", "evidence_complete",
    "source_claim_covered", "content_enriched", "language_terminology_polished",
    "publish_ready", "github_merge_ready",
]


def load_fixture():
    encoded = "".join((CHUNK_DIR / n).read_text(encoding="utf-8").strip() for n in CHUNK_NAMES)
    raw = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SHA256:
        raise AssertionError(f"fixture SHA mismatch: expected {EXPECTED_SHA256}, got {actual}")
    return json.loads(raw.decode("utf-8"))


class StageBReviseR107CRescue7FixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_fixture()

    def test_top_level_prompt_02r_contract(self):
        d = self.data
        self.assertEqual(d["stage"], "stage_b_revise")
        self.assertEqual(d["revision_pass"], "r1")
        self.assertEqual(d["revise_input_state"], "revise_required")
        self.assertEqual(d["revise_input_count"], 7)
        self.assertEqual(d["revise_required_input_count"], 7)
        self.assertEqual(d["revise_required_again_input_count"], 0)
        self.assertEqual(d["revised_draft_card_count"], 7)
        self.assertEqual(d["revise_blocked_needs_source_augmentation_count"], 0)
        self.assertEqual(d["revise_blocked_evidence_gap_count"], 0)
        self.assertEqual(d["revise_blocked_scope_change_required_count"], 0)
        self.assertEqual(d["revise_blocked_manual_review_count"], 0)
        self.assertEqual(d["outcome_total_count"], 7)
        self.assertTrue(d["accounting_matches_revise_input_count"])
        self.assertTrue(d["accounting_matches_revise_required_input_count"])
        for bucket in (
            "revised_draft_cards", "revise_blocked_needs_source_augmentation",
            "revise_blocked_evidence_gap", "revise_blocked_scope_change_required",
            "revise_blocked_manual_review", "revision_change_log", "decision_ledger",
        ):
            self.assertIn(bucket, d)
        a = d["anchor_path_revision_summary"]
        self.assertEqual(a["format_risk_input_count"], 7)
        self.assertEqual(a["anchor_path_preserved_count"], 7)
        self.assertEqual(a["anchor_path_resolved_count"], 0)
        self.assertEqual(a["anchor_path_still_unresolved_count"], 0)
        self.assertFalse(d["source_augmentation_authorized"])
        self.assertFalse(d["source_augmentation_performed"])
        self.assertEqual(d["new_source_url_count"], 0)
        self.assertEqual(d["stage_b_self_check"]["status"], "PASS")

    def test_card_contract_and_lineage(self):
        cards = self.data["revised_draft_cards"]
        self.assertEqual(len(cards), 7)
        self.assertEqual({c["source_spec_id"] for c in cards}, EXPECTED_IDS)
        self.assertEqual(len({c["source_spec_id"] for c in cards}), 7)
        for c in cards:
            sid = c["source_spec_id"]
            for field in CARD_REQUIRED:
                self.assertIn(field, c, f"{sid}: missing {field}")
            self.assertEqual(c["revision_pass"], "r1")
            self.assertTrue(c["stage_b_revise_only"])
            self.assertTrue(c["needs_stage_c_recheck"])
            self.assertEqual(str(c["strict_pass_gate"]["status"]).lower(), "pass")
            self.assertTrue(c["strict_pass_gate"]["all_six_conditions_passed"])
            self.assertEqual(c["stage_a_evidence_status"], "not_evidence_complete_no_fetch")
            self.assertTrue(c["stage_b_evidence_package_required"])
            self.assertEqual(c["primary_url_semantics"], "provided_source_candidate_not_evidence")
            self.assertEqual(c["anchor_path_resolution_action"], "preserved")
            ap = c["anchor_path_validation"]
            self.assertTrue(ap["anchor_path_qc_passed"])
            self.assertIn(ap["selected_anchor_path"], {"execution", "v3_non_execution"})
            if ap["selected_anchor_path"] == "v3_non_execution":
                for field in V3_REQUIRED:
                    self.assertIn(field, c, f"{sid}: missing V3 field {field}")
            for flag in DOWNSTREAM_FALSE:
                if flag in c:
                    self.assertFalse(c[flag], f"{sid}: forbidden downstream state {flag}=true")

    def test_schema_repairs_and_source_audit(self):
        cards = {c["source_spec_id"]: c for c in self.data["revised_draft_cards"]}
        self.assertEqual(cards["STD26_A_011"]["region"], "GL")
        self.assertEqual(cards["STD26_A_011"]["cat"], "AI")
        allowed_status = {"PASS_MULTI_SOURCE", "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION"}
        for sid, c in cards.items():
            self.assertEqual(c["source_evidence_entry_count"], len(c["fact_sources"]), sid)
            self.assertGreaterEqual(c["source_unique_url_count"], 1, sid)
            self.assertGreaterEqual(c["source_unique_domain_count"], 1, sid)
            self.assertGreaterEqual(c["source_independent_owner_count"], 1, sid)
            self.assertIn(c["source_diversity_status"], allowed_status, sid)
            if c["source_diversity_status"] == "PASS_MULTI_SOURCE":
                self.assertGreaterEqual(c["source_unique_url_count"], 2, sid)
                self.assertGreaterEqual(c["source_independent_owner_count"], 2, sid)
            else:
                self.assertEqual(sid, "STD26_A_036")
                self.assertTrue(c["single_source_exception"]["allowed"])

    def test_revision_scope_and_next_call(self):
        d = self.data
        self.assertEqual(d["later_discovered_evidence_used"], False)
        self.assertEqual(d["local_contract_validation"]["R2_change_scope"],
                         "metadata/accounting/current-contract lineage materialization only")
        rec = d["next_call_recommendation"]
        self.assertEqual(rec["recommended_prompt_id"], "Prompt 0.3R")
        self.assertTrue(rec["explicit_user_authorization_required"])
        self.assertIn("Prompt 0.8", rec["do_not_proceed_to"])


if __name__ == "__main__":
    unittest.main()

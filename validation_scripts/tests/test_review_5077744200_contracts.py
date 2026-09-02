#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import stage_artifact_contract_check as stage_contract

ROOT = Path(__file__).resolve().parents[2]
APPLY_ENGINE = ROOT / "scripts/apply_card_run.mjs"
JS_HARDENER = ROOT / "scripts/validate_card_run_v4_hardening.mjs"
APPLY_WORKFLOW = ROOT / ".github/workflows/apply-card-run.yml"


class Review5077744200Contracts(unittest.TestCase):
    def test_resolved_remediation_set_may_be_empty(self):
        self.assertEqual(binding.strings([], "remediation", allow_empty=True), set())
        with self.assertRaises(binding.Blocked):
            binding.strings([], "coverage axes")

    def test_insert_source_identity_is_one_to_one(self):
        known = {"BASE_CARD": "SPEC_BASE"}
        binding.validate_insert_identities(
            [{"card": {"id": "NEW_CARD", "source_spec_id": "SPEC_NEW"}}],
            known,
        )
        with self.assertRaises(binding.Blocked):
            binding.validate_insert_identities(
                [
                    {"card": {"id": "A", "source_spec_id": "SPEC_DUP"}},
                    {"card": {"id": "B", "source_spec_id": "SPEC_DUP"}},
                ],
                known,
            )
        with self.assertRaises(binding.Blocked):
            binding.validate_insert_identities(
                [{"card": {"id": "A", "source_spec_id": "SPEC_BASE"}}],
                known,
            )

    def test_update_cannot_rewrite_source_identity(self):
        with self.assertRaises(binding.Blocked):
            binding.validate_no_identity_mutation(
                {
                    "changes": [
                        {"op": "replace", "path": "/source_spec_id", "value": "OTHER"}
                    ]
                },
                "update[0]",
            )
        text = APPLY_ENGINE.read_text(encoding="utf-8")
        self.assertIn('"id", "source_spec_id", "changes"', text)
        self.assertIn("IMMUTABLE_SOURCE_SPEC_ID", text)
        self.assertIn('"source_spec_id", "identity_card_id"', text)

    def test_related_add_semantics_are_bound_to_reviewed_lineage(self):
        known = {"OLD": "SPEC_OLD"}
        inserted = {"NEW": "SPEC_NEW"}
        operation = {
            "source_id": "NEW",
            "target_id": "OLD",
            "source_spec_id": "SPEC_NEW",
            "identity_card_id": "NEW",
            "relation_type": "distinct_follow_up",
            "lineage_reason": "verified follow-up",
            "event_stage_relationship": "successor",
            "direction": "directional",
        }
        stage_a = {
            "spec_id": "SPEC_NEW",
            "related_prepass": {
                "status": "PASS",
                "relation_candidates": [
                    {"target_id": "OLD", "proposed_relation_type": "distinct_follow_up"}
                ],
            },
        }
        stage_b = {
            "source_spec_id": "SPEC_NEW",
            "related_evidence_review": {
                "status": "PASS",
                "target_id": "OLD",
                "final_relation_type": "distinct_follow_up",
            },
        }
        lineage = {
            "status": "PASS",
            "relation_type": "distinct_follow_up",
            "related_ids": ["OLD"],
            "reason": "verified follow-up",
            "event_stage_relationship": "successor",
            "direction": "directional",
        }
        rows = {
            "A": [stage_a],
            "B": [stage_b],
            **{
                stage: [{"source_spec_id": "SPEC_NEW", "related_lineage": dict(lineage)}]
                for stage in ("C", "0.4", "0.5", "0.6", "0.7")
            },
        }
        binding.validate_related_semantics(
            operation, "SPEC_NEW", rows, known, inserted, "related_add[0]"
        )
        rows["0.7"] = [
            {
                "source_spec_id": "SPEC_NEW",
                "related_lineage": {**lineage, "related_ids": ["SOME_OTHER_CARD"]},
            }
        ]
        with self.assertRaises(binding.Blocked):
            binding.validate_related_semantics(
                operation, "SPEC_NEW", rows, known, inserted, "related_add[0]"
            )

    def test_downstream_stage_gates_require_passing_values(self):
        blocked_cases = [
            ("B", "lineage_integrity_status", "BLOCKED"),
            ("B", "stage_a_validity_guard_applied", False),
            ("C", "accepted_pool_lineage_status", "FAIL"),
            ("0.5", "lineage_integrity_status", "BLOCKED"),
            ("0.6", "lineage_and_anchor_guard", "BLOCKED"),
            ("0.7", "lineage_and_anchor_guard", "BLOCKED"),
        ]
        for stage, field, value in blocked_cases:
            with self.subTest(stage=stage, field=field):
                self.assertIsNotNone(
                    stage_contract._top_level_gate_finding(stage, field, value)
                )
        self.assertIsNotNone(
            stage_contract._top_level_gate_finding(
                "0.8", "github_main_sync_gate", {"status": "BLOCKED"}
            )
        )
        self.assertIsNone(
            stage_contract._top_level_gate_finding(
                "0.8",
                "github_main_sync_gate",
                {
                    "status": "PASS",
                    "baseline_locked": True,
                    "main_unchanged_since_locked_preflight": True,
                    "silent_rebase_performed": False,
                },
            )
        )

    def test_js_gate_delegates_authoritative_baseline_and_related_binding(self):
        text = JS_HARDENER.read_text(encoding="utf-8")
        self.assertIn("cannot mutate source_spec_id", text)
        self.assertIn("reuses source_spec_id", text)
        self.assertIn("authoritative baseline/Related binding", text)
        self.assertIn("card_run_v4_binding_hardening.py", text)

    def test_apply_gate_has_historical_v1_audit_only_exception(self):
        text = APPLY_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("historical_v1_audit_only()", text)
        self.assertIn("git diff -M --diff-filter=ACMRD --name-status", text)
        self.assertIn('schema_name" == "manual_direct_add_v1"', text)
        self.assertIn('git cat-file -e "${base_sha}:${base_manifest}"', text)
        self.assertIn('git show "${base_sha}:${base_manifest}"', text)
        self.assertIn('base_schema_name" == "manual_direct_add_v1"', text)
        self.assertIn('if [[ "$status" == D* ]]; then', text)
        self.assertIn("historical preservation path only", text)


if __name__ == "__main__":
    unittest.main()

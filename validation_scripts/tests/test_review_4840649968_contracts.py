from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "validation_scripts/related_lifecycle_check.py"
STAGE_C = ROOT / "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md"


class TestReview4840649968Contracts(unittest.TestCase):
    # Untyped scope strings must fail closed when they identify different rows
    # through canonical and provisional namespaces.
    def run_validator(self, cards, selected_ids):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cards_path = tmp_path / "cards.json"
            ids_path = tmp_path / "ids.json"
            cards_path.write_text(json.dumps({"cards": cards}), encoding="utf-8")
            ids_path.write_text(json.dumps({"ids": selected_ids}), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(cards_path),
                    "--require-contract",
                    "--new-id-file",
                    str(ids_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            return result, json.loads(result.stdout)

    @staticmethod
    def unrelated_card(card_id, draft_id=None):
        card = {
            "id": card_id,
            "date": "2026-08-01",
            "related": [],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "new_unrelated_event",
                "related_ids": [],
                "reason": "Scope fixture.",
            },
        }
        if draft_id is not None:
            card["draft_id"] = draft_id
        return card

    def test_cross_row_canonical_provisional_collision_is_ambiguous(self):
        cards = [
            self.unrelated_card("shared-id"),
            self.unrelated_card("candidate-final", draft_id="shared-id"),
        ]
        result, report = self.run_validator(cards, ["shared-id"])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["cards_checked"], 0)
        self.assertEqual(report["id_scope"]["ambiguous_ids"], ["shared-id"])

    def test_same_row_canonical_and_provisional_identifier_remains_valid(self):
        card = self.unrelated_card("same-row-id", draft_id="same-row-id")
        result, report = self.run_validator([card], ["same-row-id"])
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertEqual(report["cards_checked"], 1)
        self.assertEqual(report["id_scope"]["status"], "PASS")

    def test_stage_c_r0_accepted_schema_preserves_complete_v3_package(self):
        text = STAGE_C.read_text(encoding="utf-8")
        start = text.index("Each accepted_fact_safe item must include:")
        end = text.index("Each revise_required item must include:", start)
        accepted_schema = text[start:end]
        self.assertIn("complete byte-for-byte canonical package", accepted_schema)
        for field in (
            "structural_value_override_applied",
            "structural_value_override_reason",
            "anchor_classes[]",
            "evidence_needed_for_stage_b[]",
            "why_execution_event_not_required",
            "prior_state",
            "new_verified_fact",
            "changed_judgment",
            "uncertainty_resolved",
            "remaining_uncertainty",
            "incremental_information",
            "baseline_expectation_changed",
            "decision_relevance",
            "next_confirmation_points[]",
        ):
            self.assertIn(field, accepted_schema)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


validator = Path("validation_scripts/related_lifecycle_check.py")
replace_once(
    validator,
    '''    for identifier in sorted(requested):
        canonical_matches = [
            card for card in rows if identifier in canonical_card_identifiers(card)
        ]
        if len(canonical_matches) == 1:
            matched.add(identifier)
            if canonical_matches[0] not in selected_rows:
                selected_rows.append(canonical_matches[0])
            continue
        if len(canonical_matches) > 1:
            ambiguous.append(identifier)
            continue

        alias_matches = [
            card for card in rows if identifier in provisional_card_identifiers(card)
        ]
        if len(alias_matches) == 1:
            matched.add(identifier)
            if alias_matches[0] not in selected_rows:
                selected_rows.append(alias_matches[0])
        elif len(alias_matches) > 1:
            ambiguous.append(identifier)
''',
    '''    for identifier in sorted(requested):
        canonical_matches = [
            card for card in rows if identifier in canonical_card_identifiers(card)
        ]
        alias_matches = [
            card for card in rows if identifier in provisional_card_identifiers(card)
        ]

        # Scope identifiers are intentionally untyped. If the same string names a
        # canonical identifier on one row and a provisional alias on another, the
        # requested row cannot be inferred safely and the scope must fail closed.
        if len(canonical_matches) > 1 or len(alias_matches) > 1:
            ambiguous.append(identifier)
            continue

        if len(canonical_matches) == 1:
            if alias_matches and alias_matches[0] is not canonical_matches[0]:
                ambiguous.append(identifier)
                continue
            matched.add(identifier)
            if canonical_matches[0] not in selected_rows:
                selected_rows.append(canonical_matches[0])
            continue

        if len(alias_matches) == 1:
            matched.add(identifier)
            if alias_matches[0] not in selected_rows:
                selected_rows.append(alias_matches[0])
''',
    "canonical/provisional scope collision handling",
)

stage_c = Path("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
replace_once(
    stage_c,
    '''  - structural_value_override_qc_status: pass|not_applicable
  - non_applicable_anchor_path_reason
- ordinary accepted items without `format_risk_tags` must not invent or be required to emit `anchor_path_validation`
''',
    '''  - structural_value_override_qc_status: pass|not_applicable
  - non_applicable_anchor_path_reason
- when `anchor_path_validation.selected_anchor_path = v3_non_execution`, the complete byte-for-byte canonical package: `structural_value_override_applied`, `structural_value_override_reason`, `anchor_classes[]`, `evidence_needed_for_stage_b[]`, `why_execution_event_not_required`, `prior_state`, `new_verified_fact`, `changed_judgment`, `uncertainty_resolved`, `remaining_uncertainty`, `incremental_information`, `baseline_expectation_changed`, `decision_relevance`, and `next_confirmation_points[]`
- ordinary accepted items without `format_risk_tags` must not invent or be required to emit `anchor_path_validation`
''',
    "Stage C r0 accepted V3 package",
)

prior_test = Path("validation_scripts/tests/test_review_4840276596_contracts.py")
replace_once(
    prior_test,
    '''    def test_canonical_identifier_wins_over_colliding_draft_alias(self):
        canonical = self.unrelated_card(card_id="stable-id")
        alias_collision = self.unrelated_card(
            card_id="other-final",
            draft_id="stable-id",
        )

        result, report = self.run_validator([canonical, alias_collision], ["stable-id"])

        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertEqual(report["cards_checked"], 1)
        self.assertEqual(report["id_scope"]["matched_count"], 1)
        self.assertEqual(report["id_scope"]["ambiguous_ids"], [])
''',
    '''    def test_canonical_provisional_cross_row_collision_fails_scope_as_ambiguous(self):
        canonical = self.unrelated_card(card_id="stable-id")
        alias_collision = self.unrelated_card(
            card_id="other-final",
            draft_id="stable-id",
        )

        result, report = self.run_validator([canonical, alias_collision], ["stable-id"])

        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["cards_checked"], 0)
        self.assertEqual(report["id_scope"]["matched_count"], 0)
        self.assertEqual(report["id_scope"]["ambiguous_ids"], ["stable-id"])
        self.assertIn("ID scope has 1 ambiguous ID(s)", report["id_scope"]["errors"])
''',
    "cross-row collision regression expectation",
)

new_test = Path("validation_scripts/tests/test_review_4840649968_contracts.py")
new_test.write_text('''from __future__ import annotations

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
''', encoding="utf-8")

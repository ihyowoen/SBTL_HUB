import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "validation_scripts/related_lifecycle_check.py"


class TestReview4840276596Contracts(unittest.TestCase):
    def run_validator(self, cards, selected_ids):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "cards.json"
            scope_path = tmp_path / "ids.json"
            input_path.write_text(json.dumps({"cards": cards}), encoding="utf-8")
            scope_path.write_text(json.dumps({"ids": selected_ids}), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(input_path),
                    "--require-contract",
                    "--new-id-file",
                    str(scope_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            return result, json.loads(result.stdout)

    @staticmethod
    def follow_up_card(*, card_id, draft_id, source_spec_id, related):
        return {
            "id": card_id,
            "draft_id": draft_id,
            "source_spec_id": source_spec_id,
            "date": "2026-08-02",
            "related": related,
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "distinct_follow_up",
                "related_ids": related,
                "fresh_follow_up_anchor": "verified execution update",
                "fresh_follow_up_anchor_class": "execution_event_anchor",
                "incremental_fact_vs_predecessor": "The project reached a later verified stage.",
                "changed_judgment_vs_predecessor": "Execution probability increased.",
                "reason": "Verified incremental follow-up.",
            },
        }

    def test_draft_alias_collision_does_not_pollute_related_target_map(self):
        parent = {
            "id": "legacy-parent",
            "draft_id": "old-draft",
            "date": "2026-08-01",
            "related": [],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "new_unrelated_event",
                "related_ids": [],
                "reason": "Baseline parent.",
            },
        }
        candidate = self.follow_up_card(
            card_id="candidate-final",
            draft_id="legacy-parent",
            source_spec_id="candidate-spec",
            related=["legacy-parent"],
        )

        result, report = self.run_validator([parent, candidate], ["candidate-spec"])

        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["cards_checked"], 1)
        self.assertEqual(report["id_scope"]["matched_count"], 1)

    def test_draft_alias_is_not_accepted_as_related_target(self):
        parent = {
            "id": "parent-final",
            "draft_id": "parent-draft-only",
            "date": "2026-08-01",
            "related": [],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "new_unrelated_event",
                "related_ids": [],
                "reason": "Baseline parent.",
            },
        }
        candidate = self.follow_up_card(
            card_id="candidate-final",
            draft_id="candidate-draft",
            source_spec_id="candidate-spec",
            related=["parent-draft-only"],
        )

        result, report = self.run_validator([parent, candidate], ["candidate-spec"])

        self.assertEqual(result.returncode, 1)
        messages = [
            message
            for finding in report["findings"]
            for message in finding["errors"]
        ]
        self.assertIn("dangling related ID: parent-draft-only", messages)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "validation_scripts/related_lifecycle_check.py"


def lineage(relation_type: str, provisional=None):
    return {
        "status": "PASS",
        "same_event_checked": True,
        "earliest_same_event_date_checked": True,
        "relation_type": relation_type,
        "related_ids": [],
        "related_candidate_spec_ids": provisional or [],
        "fresh_follow_up_anchor": "verified schedule change" if relation_type == "distinct_follow_up" else None,
        "fresh_follow_up_anchor_class": "follow_up_probability_anchor" if relation_type == "distinct_follow_up" else None,
        "incremental_fact_vs_predecessor": "schedule changed" if relation_type == "distinct_follow_up" else None,
        "changed_judgment_vs_predecessor": "timing assessment changed" if relation_type == "distinct_follow_up" else None,
        "reason": "current-run candidate relation",
    }


class TestReview4840598467Contracts(unittest.TestCase):
    def run_validator(self, parent_date: str, child_date: str):
        parent = {
            "source_spec_id": "SPEC_PARENT",
            "date": parent_date,
            "related": [],
            "related_lineage": lineage("new_unrelated_event"),
        }
        child = {
            "source_spec_id": "SPEC_CHILD",
            "date": child_date,
            "related": [],
            "related_candidate_spec_ids": ["SPEC_PARENT"],
            "related_lineage": lineage("distinct_follow_up", ["SPEC_PARENT"]),
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cards = tmp_path / "cards.json"
            ids = tmp_path / "ids.json"
            cards.write_text(json.dumps({"cards": [parent, child]}), encoding="utf-8")
            ids.write_text(json.dumps(["SPEC_PARENT", "SPEC_CHILD"]), encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable, str(VALIDATOR), str(cards),
                    "--require-contract", "--allow-provisional-related",
                    "--new-id-file", str(ids),
                ],
                cwd=ROOT, text=True, capture_output=True,
            )

    def test_provisional_follow_up_before_predecessor_is_rejected(self):
        result = self.run_validator("2026-08-02", "2026-08-01")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "follow-up date precedes provisional predecessor SPEC_PARENT",
            result.stdout,
        )

    def test_provisional_follow_up_on_or_after_predecessor_passes(self):
        result = self.run_validator("2026-08-01", "2026-08-02")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_validator_keeps_resolved_provisional_chronology_guard(self):
        text = VALIDATOR.read_text(encoding="utf-8")
        self.assertIn("resolved_provisional_targets", text)
        self.assertIn("follow-up date precedes provisional predecessor", text)


if __name__ == "__main__":
    unittest.main()

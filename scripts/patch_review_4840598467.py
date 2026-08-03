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
    '''    valid_provisional_edge = False\n    if allow_provisional_related and provisional:\n''',
    '''    valid_provisional_edge = False\n    resolved_provisional_targets: list[tuple[str, dict[str, Any]]] = []\n    if allow_provisional_related and provisional:\n''',
    "initialize resolved provisional targets",
)

replace_once(
    validator,
    '''                if resolved_target is card:\n                    errors.append("related_candidate_spec_ids contains self-reference")\n                elif resolved_target is None:\n                    errors.append(f"dangling provisional related ID: {target}")\n            valid_provisional_edge = bool(normalized_provisional) and not any(\n''',
    '''                if resolved_target is card:\n                    errors.append("related_candidate_spec_ids contains self-reference")\n                elif resolved_target is None:\n                    errors.append(f"dangling provisional related ID: {target}")\n                else:\n                    resolved_provisional_targets.append((target, resolved_target))\n            valid_provisional_edge = bool(normalized_provisional) and not any(\n''',
    "capture resolved provisional targets",
)

replace_once(
    validator,
    '''    if relation_type == "distinct_follow_up":\n        child_date = parse_date(card.get("date"))\n        for target in related:\n            parent = by_id.get(target)\n            parent_date = parse_date(parent.get("date")) if parent else None\n            if child_date and parent_date and child_date < parent_date:\n                errors.append(f"follow-up date precedes predecessor {target}")\n\n    unresolved = (\n''',
    '''    if relation_type == "distinct_follow_up":\n        child_date = parse_date(card.get("date"))\n        for target in related:\n            parent = by_id.get(target)\n            parent_date = parse_date(parent.get("date")) if parent else None\n            if child_date and parent_date and child_date < parent_date:\n                errors.append(f"follow-up date precedes predecessor {target}")\n        for target, parent in resolved_provisional_targets:\n            parent_date = parse_date(parent.get("date"))\n            if child_date and parent_date and child_date < parent_date:\n                errors.append(f"follow-up date precedes provisional predecessor {target}")\n\n    unresolved = (\n''',
    "validate provisional chronology",
)

test_path = Path("validation_scripts/tests/test_review_4840598467_contracts.py")
test_path.write_text('''from __future__ import annotations\n\nimport json\nimport subprocess\nimport sys\nimport tempfile\nimport unittest\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\nVALIDATOR = ROOT / "validation_scripts/related_lifecycle_check.py"\n\n\ndef lineage(relation_type: str, provisional=None):\n    return {\n        "status": "PASS",\n        "same_event_checked": True,\n        "earliest_same_event_date_checked": True,\n        "relation_type": relation_type,\n        "related_ids": [],\n        "related_candidate_spec_ids": provisional or [],\n        "fresh_follow_up_anchor": "verified schedule change" if relation_type == "distinct_follow_up" else None,\n        "fresh_follow_up_anchor_class": "follow_up_probability_anchor" if relation_type == "distinct_follow_up" else None,\n        "incremental_fact_vs_predecessor": "schedule changed" if relation_type == "distinct_follow_up" else None,\n        "changed_judgment_vs_predecessor": "timing assessment changed" if relation_type == "distinct_follow_up" else None,\n        "reason": "current-run candidate relation",\n    }\n\n\nclass TestReview4840598467Contracts(unittest.TestCase):\n    def run_validator(self, parent_date: str, child_date: str):\n        parent = {\n            "source_spec_id": "SPEC_PARENT",\n            "date": parent_date,\n            "related": [],\n            "related_lineage": lineage("new_unrelated_event"),\n        }\n        child = {\n            "source_spec_id": "SPEC_CHILD",\n            "date": child_date,\n            "related": [],\n            "related_candidate_spec_ids": ["SPEC_PARENT"],\n            "related_lineage": lineage("distinct_follow_up", ["SPEC_PARENT"]),\n        }\n        with tempfile.TemporaryDirectory() as tmp:\n            tmp_path = Path(tmp)\n            cards = tmp_path / "cards.json"\n            ids = tmp_path / "ids.json"\n            cards.write_text(json.dumps({"cards": [parent, child]}), encoding="utf-8")\n            ids.write_text(json.dumps(["SPEC_PARENT", "SPEC_CHILD"]), encoding="utf-8")\n            return subprocess.run(\n                [\n                    sys.executable, str(VALIDATOR), str(cards),\n                    "--require-contract", "--allow-provisional-related",\n                    "--new-id-file", str(ids),\n                ],\n                cwd=ROOT, text=True, capture_output=True,\n            )\n\n    def test_provisional_follow_up_before_predecessor_is_rejected(self):\n        result = self.run_validator("2026-08-02", "2026-08-01")\n        self.assertNotEqual(result.returncode, 0)\n        self.assertIn(\n            "follow-up date precedes provisional predecessor SPEC_PARENT",\n            result.stdout,\n        )\n\n    def test_provisional_follow_up_on_or_after_predecessor_passes(self):\n        result = self.run_validator("2026-08-01", "2026-08-02")\n        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)\n        self.assertEqual(json.loads(result.stdout)["status"], "PASS")\n\n    def test_validator_keeps_resolved_provisional_chronology_guard(self):\n        text = VALIDATOR.read_text(encoding="utf-8")\n        self.assertIn("resolved_provisional_targets", text)\n        self.assertIn("follow-up date precedes provisional predecessor", text)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''', encoding="utf-8")

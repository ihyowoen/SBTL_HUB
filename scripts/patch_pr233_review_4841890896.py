from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


stage = ROOT / "validation_scripts/stage_lineage_contract_check.py"
replace_once(
    stage,
    '''def _item_specific_narrative(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    return (
        len(text) >= 8
        and not _contains_generic_fragment(text)
        and not _placeholder_only_text(text)
    )
''',
    '''def _item_specific_narrative(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    # Narrative fields may legitimately describe residual unknowns or pending
    # confirmation. Reject placeholder-only semantics, not contextual words
    # such as "unknown" inside an otherwise item-specific explanation.
    return len(text) >= 8 and not _placeholder_only_text(text)
''',
    "contextual uncertainty narrative handling",
)

related = ROOT / "validation_scripts/related_lifecycle_check.py"
replace_once(
    related,
    '''def relation_object(card: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("related_lineage", "related_evidence_review", "related_prepass"):
        value = card.get(key)
        if isinstance(value, dict):
            return value
    return None


def check_card(
''',
    '''def relation_object(card: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("related_lineage", "related_evidence_review", "related_prepass"):
        value = card.get(key)
        if isinstance(value, dict):
            return value
    return None


def validate_follow_up_chronology_justification(
    lineage: dict[str, Any],
) -> tuple[set[str], str | None]:
    value = lineage.get("follow_up_date_precedes_predecessor_justification")
    if value in (None, "", {}):
        return set(), None
    if not isinstance(value, dict):
        return set(), "follow-up chronology justification must be an object"
    if value.get("applied") is not True:
        return set(), "follow-up chronology justification must set applied=true"

    identifiers = value.get("predecessor_identifiers")
    if not isinstance(identifiers, list) or not identifiers:
        return set(), "follow-up chronology justification requires predecessor_identifiers[]"
    normalized_identifiers = []
    for identifier in identifiers:
        if not isinstance(identifier, str) or not identifier.strip():
            return set(), "follow-up chronology predecessor_identifiers must be non-empty strings"
        normalized_identifiers.append(identifier.strip())
    if normalized_identifiers != dedupe(normalized_identifiers):
        return set(), "follow-up chronology predecessor_identifiers contains duplicates"

    basis = value.get("representative_date_basis")
    reason = value.get("reason")
    if not isinstance(basis, str) or len(basis.strip()) < 12:
        return set(), "follow-up chronology justification requires a specific representative_date_basis"
    if not isinstance(reason, str) or len(reason.strip()) < 20:
        return set(), "follow-up chronology justification requires a specific reason"

    source_urls = value.get("evidence_source_urls")
    if not isinstance(source_urls, list) or not source_urls:
        return set(), "follow-up chronology justification requires evidence_source_urls[]"
    for url in source_urls:
        if not isinstance(url, str) or not url.strip().startswith(("https://", "http://")):
            return set(), "follow-up chronology evidence_source_urls must contain HTTP(S) URLs"

    return set(normalized_identifiers), None


def chronology_exception_covers(
    requested_target: str,
    resolved_target: dict[str, Any] | None,
    exception_identifiers: set[str],
) -> bool:
    candidate_identifiers = {requested_target}
    if resolved_target is not None:
        candidate_identifiers.update(canonical_card_identifiers(resolved_target))
        candidate_identifiers.update(provisional_card_identifiers(resolved_target))
    return bool(candidate_identifiers & exception_identifiers)


def check_card(
''',
    "chronology justification helpers",
)

replace_once(
    related,
    '''    if not lineage.get("reason") and not lineage.get("relation_reason"):
        errors.append("relation reason is required")

    if relation_type == "distinct_follow_up":
        child_date = parse_date(card.get("date"))
        for target in related:
            parent = by_id.get(target)
            parent_date = parse_date(parent.get("date")) if parent else None
            if child_date and parent_date and child_date < parent_date:
                errors.append(f"follow-up date precedes predecessor {target}")
        for target, parent in resolved_provisional_targets:
            parent_date = parse_date(parent.get("date"))
            if child_date and parent_date and child_date < parent_date:
                errors.append(f"follow-up date precedes provisional predecessor {target}")
''',
    '''    if not lineage.get("reason") and not lineage.get("relation_reason"):
        errors.append("relation reason is required")

    chronology_exception_ids, chronology_exception_error = (
        validate_follow_up_chronology_justification(lineage)
    )
    if chronology_exception_error:
        errors.append(chronology_exception_error)

    if relation_type == "distinct_follow_up":
        child_date = parse_date(card.get("date"))
        for target in related:
            parent = by_id.get(target)
            parent_date = parse_date(parent.get("date")) if parent else None
            if (
                child_date
                and parent_date
                and child_date < parent_date
                and not chronology_exception_covers(target, parent, chronology_exception_ids)
            ):
                errors.append(f"follow-up date precedes predecessor {target}")
        for target, parent in resolved_provisional_targets:
            parent_date = parse_date(parent.get("date"))
            if (
                child_date
                and parent_date
                and child_date < parent_date
                and not chronology_exception_covers(target, parent, chronology_exception_ids)
            ):
                errors.append(f"follow-up date precedes provisional predecessor {target}")
''',
    "honor evidence-backed chronology exception",
)

contract = ROOT / "docs/RELATED_LIFECYCLE_CONTRACT.md"
replace_once(
    contract,
    '''    "same_event_checked": true,
    "earliest_same_event_date_checked": true,
    "rejected_relation_candidates": [],
''',
    '''    "same_event_checked": true,
    "earliest_same_event_date_checked": true,
    "follow_up_date_precedes_predecessor_justification": null,
    "rejected_relation_candidates": [],
''',
    "Stage C chronology exception field",
)
replace_once(
    contract,
    '''Stage C must not accept a new card with:

- `same_event_duplicate`;
''',
    '''`follow_up_date_precedes_predecessor_justification` must normally be `null` or absent. It may be populated only when a `distinct_follow_up` uses a representative date earlier than a predecessor date. The object must contain:

```json
{
  "applied": true,
  "predecessor_identifiers": ["final_or_provisional_predecessor_id"],
  "representative_date_basis": "specific explanation of what event the earlier date represents",
  "reason": "specific explanation of why the earlier representative date remains a later distinct follow-up judgment",
  "evidence_source_urls": ["https://..."]
}
```

The exception is target-specific and evidence-backed. A generic explanation, missing source URL, or identifier that does not resolve to the earlier predecessor does not waive the chronology invariant.

Stage C must not accept a new card with:

- `same_event_duplicate`;
''',
    "chronology exception contract",
)

test = ROOT / "validation_scripts/tests/test_review_4841890896_contracts.py"
test.write_text('''"""Regression coverage for Codex review 4841890896."""

from __future__ import annotations

import copy
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4841890896Contracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_contextual_unknown_in_uncertainty_narrative_passes(self):
        spec = copy.deepcopy(self.base_spec())
        spec["remaining_uncertainty"] = (
            "The named customer's volume remains unknown pending the August filing."
        )
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_placeholder_only_unknown_still_fails(self):
        spec = copy.deepcopy(self.base_spec())
        spec["remaining_uncertainty"] = "unknown"
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("must be item-specific narrative text", output)

    def provisional_cards(self, with_exception: bool):
        parent = {
            "id": "PARENT_FINAL",
            "draft_id": "PARENT_SPEC",
            "date": "2026-08-10",
        }
        lineage_obj = {
            "status": "PASS",
            "relation_type": "distinct_follow_up",
            "related_ids": [],
            "related_candidate_spec_ids": ["PARENT_SPEC"],
            "reason": "The retrospective finding changes the judgment on the same project.",
            "fresh_follow_up_anchor_class": "data_financial_anchor",
            "fresh_follow_up_anchor": "The filing retrospectively identifies the earlier operating event.",
            "incremental_fact_vs_predecessor": "The filing discloses a previously unknown customer-volume change.",
            "changed_judgment_vs_predecessor": "The project scale assessment is now lower.",
            "same_event_checked": True,
            "earliest_same_event_date_checked": True,
        }
        if with_exception:
            lineage_obj["follow_up_date_precedes_predecessor_justification"] = {
                "applied": True,
                "predecessor_identifiers": ["PARENT_SPEC"],
                "representative_date_basis": "The card date represents the operating event disclosed retrospectively.",
                "reason": "The later filing creates the distinct changed judgment even though the represented operating event occurred earlier.",
                "evidence_source_urls": ["https://example.com/filing"],
            }
        child = {
            "id": "CHILD_FINAL",
            "draft_id": "CHILD_SPEC",
            "date": "2026-08-01",
            "related": [],
            "related_candidate_spec_ids": ["PARENT_SPEC"],
            "related_lineage": lineage_obj,
        }
        return parent, child

    def run_provisional(self, with_exception: bool):
        parent, child = self.provisional_cards(with_exception)
        by_id = {"PARENT_FINAL": parent, "CHILD_FINAL": child}
        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])
        return related.check_card(
            child,
            by_id,
            require_contract=True,
            allow_provisional_related=True,
            provisional_by_id=provisional_by_id,
            ambiguous_provisional_ids=ambiguous,
        )

    def test_provisional_date_inversion_without_justification_fails(self):
        errors, _ = self.run_provisional(False)
        self.assertIn(
            "follow-up date precedes provisional predecessor PARENT_SPEC",
            errors,
        )

    def test_evidence_backed_provisional_chronology_exception_passes(self):
        errors, warnings = self.run_provisional(True)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_malformed_chronology_exception_does_not_waive_invariant(self):
        parent, child = self.provisional_cards(True)
        child["related_lineage"]["follow_up_date_precedes_predecessor_justification"]["evidence_source_urls"] = []
        by_id = {"PARENT_FINAL": parent, "CHILD_FINAL": child}
        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])
        errors, _ = related.check_card(
            child,
            by_id,
            require_contract=True,
            allow_provisional_related=True,
            provisional_by_id=provisional_by_id,
            ambiguous_provisional_ids=ambiguous,
        )
        self.assertIn(
            "follow-up chronology justification requires evidence_source_urls[]",
            errors,
        )
        self.assertIn(
            "follow-up date precedes provisional predecessor PARENT_SPEC",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

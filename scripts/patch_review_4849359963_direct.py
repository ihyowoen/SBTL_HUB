#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one replacement target, found {count}")
    file_path.write_text(text.replace(old, new), encoding="utf-8")


validator_path = "validation_scripts/stage_lineage_contract_check.py"
old_validator = '''    text = _normalized_text(value)
    has_measurable_event_or_metric = (
        _has_any_term(text, STAGE_A_CONFIRMATION_EVENT_TERMS)
        or _has_any_term(text, STAGE_A_EXACT_TARGET_TERMS)
    )
    return (
        bool(text)
        and len(text.split()) >= 4
        and not _placeholder_only_text(text)
        and not _contains_generic_target_fragment(text)
        and has_measurable_event_or_metric
    )
'''
new_validator = '''    text = _normalized_text(value)
    has_measurable_event_or_metric = (
        _has_any_term(text, STAGE_A_CONFIRMATION_EVENT_TERMS)
        or _has_any_term(text, STAGE_A_EXACT_TARGET_TERMS)
    )
    has_interpretation_effect = _has_any_term(
        text, STAGE_A_INTERPRETATION_EFFECT_TERMS
    )
    return (
        bool(text)
        and len(text.split()) >= 4
        and not _placeholder_only_text(text)
        and not _contains_generic_target_fragment(text)
        and has_measurable_event_or_metric
        and has_interpretation_effect
    )
'''
replace_once(validator_path, old_validator, new_validator)

old_message = '''            f'{spec_id}: next_confirmation_points entries must identify measurable '
            'events or metrics, not generic confirmation requests'
'''
new_message = '''            f'{spec_id}: next_confirmation_points entries must identify both a measurable '
            'event or metric and an interpretation effect, not generic confirmation requests'
'''
replace_once(validator_path, old_message, new_message)

replace_once(
    "validation_scripts/tests/test_review_4840783305_contracts.py",
    '"next_confirmation_points": ["Publication of implementing guidance with the final effective date"],',
    '"next_confirmation_points": ["Publication of implementing guidance with the final effective date would confirm the eligibility change"],',
)

replace_once(
    "validation_scripts/tests/test_review_4848883611_contracts.py",
    'value = "Publication of implementing guidance with the final effective date"',
    'value = "Publication of implementing guidance with the final effective date would confirm the eligibility change"',
)

focused_test = Path("validation_scripts/tests/test_review_4849359963_contracts.py")
if focused_test.exists():
    raise SystemExit(f"{focused_test}: file already exists")
focused_test.write_text(
    '''from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4849359963Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_free_text_confirmation_requires_interpretation_effect(self):
        self.assertFalse(
            lineage._valid_confirmation_point(
                "Project Alpha production capacity milestone"
            )
        )

    def test_supported_interpretation_effect_inflections_pass(self):
        values = (
            "Project Alpha production capacity milestone would confirm adoption",
            "Project Alpha production capacity milestone strengthens the thesis",
            "Project Alpha production capacity milestone weakened the thesis",
            "Project Alpha production capacity milestone invalidated the thesis",
            "Project Alpha production capacity milestone revised the outlook",
        )
        for value in values:
            with self.subTest(value=value):
                self.assertTrue(lineage._valid_confirmation_point(value))

    def test_complete_term_collision_does_not_create_effect(self):
        self.assertFalse(
            lineage._valid_confirmation_point(
                "Project Alpha production capacity milestone remained unchanged"
            )
        )

    def test_generic_confirmation_scaffolds_still_fail(self):
        for value in (
            "additional data needed to confirm adoption",
            "more evidence required for approval",
            "confirmation needed for production",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._valid_confirmation_point(value))

    def test_complete_v3_spec_rejects_metric_only_confirmation(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [
            "Project Alpha production capacity milestone"
        ]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages), messages
        )

    def test_complete_v3_spec_accepts_measurable_effect_confirmation(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [
            "Publication of additional data center capacity for Project Alpha would confirm adoption"
        ]
        messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages),
            messages,
        )
        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)

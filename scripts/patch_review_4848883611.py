from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


malformed = "python validation_scripts/stage_lineage_contract_check.py stage_a <STAGE_A_JSON>`."
correct = "`python validation_scripts/stage_lineage_contract_check.py stage_a <STAGE_A_JSON>`."
replace_once("validation_scripts/apply_prompt_contract_overlays.py", malformed, correct)
replace_once("docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md", malformed, correct)

old_confirmation = """def _valid_confirmation_point(value):
    if isinstance(value, dict):
        measurable = value.get('measurable_event_or_metric') or value.get('confirmation_event')
        interpretation_effect = value.get('interpretation_effect') or value.get('confirm_weaken_invalidate')
        return _structured_exact_target(measurable) and _structured_interpretation_effect(interpretation_effect)
    return _specific_string(value) and _has_any_term(value, STAGE_A_CONFIRMATION_EVENT_TERMS)
"""
new_confirmation = """def _valid_confirmation_point(value):
    if isinstance(value, dict):
        measurable = value.get('measurable_event_or_metric') or value.get('confirmation_event')
        interpretation_effect = value.get('interpretation_effect') or value.get('confirm_weaken_invalidate')
        return _structured_exact_target(measurable) and _structured_interpretation_effect(interpretation_effect)

    text = _normalized_text(value)
    has_measurable_event_or_metric = (
        _has_any_term(text, STAGE_A_CONFIRMATION_EVENT_TERMS)
        or _has_any_term(text, STAGE_A_EXACT_TARGET_TERMS)
    )
    return (
        isinstance(value, str)
        and len(text.split()) >= 4
        and not _placeholder_only_text(text)
        and not _contains_generic_target_fragment(text)
        and has_measurable_event_or_metric
        and _has_any_term(text, STAGE_A_INTERPRETATION_EFFECT_TERMS)
    )
"""
replace_once("validation_scripts/stage_lineage_contract_check.py", old_confirmation, new_confirmation)

Path("validation_scripts/tests/test_review_4848883611_contracts.py").write_text(
    '''from __future__ import annotations

import copy
import unittest
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4848883611Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_stage_a_exit_commands_are_valid_markdown(self):
        for path in (
            "validation_scripts/apply_prompt_contract_overlays.py",
            "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md",
        ):
            text = Path(path).read_text(encoding="utf-8")
            command = "`python validation_scripts/stage_lineage_contract_check.py stage_a <STAGE_A_JSON>`."
            self.assertIn(command, text)
            self.assertNotIn("\\npython validation_scripts/stage_lineage_contract_check.py stage_a <STAGE_A_JSON>`.", text)

    def test_specific_confirmation_with_additional_data_substring_passes(self):
        value = "Publication of additional data center capacity for Project Alpha would confirm adoption"
        self.assertTrue(lineage._valid_confirmation_point(value))

    def test_existing_metric_confirmation_remains_valid(self):
        value = "Publication of implementing guidance with the final effective date"
        self.assertTrue(lineage._valid_confirmation_point(value))

    def test_generic_confirmation_scaffolds_still_fail(self):
        for value in (
            "additional data needed to confirm adoption",
            "more evidence required for approval",
            "confirmation needed for production",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._valid_confirmation_point(value))

    def test_confirmation_requires_measurable_target_and_interpretation_effect(self):
        self.assertFalse(lineage._valid_confirmation_point("Publication of Project Alpha capacity data"))
        self.assertFalse(lineage._valid_confirmation_point("Project Alpha would confirm the thesis"))

    def test_complete_v3_spec_accepts_specific_confirmation_text(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [
            "Publication of additional data center capacity for Project Alpha would confirm adoption"
        ]
        messages = []
        self.assertTrue(lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages), messages)
        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "validation_scripts/stage_lineage_contract_check.py"
TEST_FILE = ROOT / "validation_scripts/tests/test_review_4850764924_contracts.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


text = VALIDATOR.read_text(encoding="utf-8")

text = replace_once(
    text,
    '''    "건수", "수치", "수준", "증가율",
}
_base.STAGE_A_SUBSTANTIVE_TARGET_PREDICATE_TERMS = (
''',
    '''    "건수", "수치", "수준", "증가율",
}
_base.STAGE_A_EFFECT_FIRST_MEASUREMENT_SUBJECT_TERMS = set(
    _base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS
) | set(_base.STAGE_A_EXACT_TARGET_TERMS)
_base.STAGE_A_INTERPRETATION_OBJECT_QUALIFIER_TERMS = {
    "for", "of", "regarding", "concerning", "about", "on", "around",
    "toward", "towards", "대한", "관련", "관한",
}
_base.STAGE_A_SUBSTANTIVE_TARGET_PREDICATE_TERMS = (
''',
    "measurement vocabulary constants",
)

text = replace_once(
    text,
    '''    if object_index < effect_index and any(
        token in _base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS
        for token in bridge
    ):
        return False
''',
    '''    if object_index < effect_index:
        measurement_positions = [
            index for index, token in enumerate(bridge)
            if token in _base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS
        ]
        if measurement_positions:
            qualifier_positions = [
                index for index, token in enumerate(bridge)
                if token in _base.STAGE_A_INTERPRETATION_OBJECT_QUALIFIER_TERMS
            ]
            measurement_terms_are_object_qualifiers = bool(qualifier_positions) and all(
                any(qualifier_index < measurement_index for qualifier_index in qualifier_positions)
                for measurement_index in measurement_positions
            )
            if not measurement_terms_are_object_qualifiers:
                return False
''',
    "interpretation-object qualifier handling",
)

text = replace_once(
    text,
    '''        has_measurement_subject = any(
            token in _base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS
            for token in subject_context
        )
''',
    '''        has_measurement_subject = any(
            token in _base.STAGE_A_EFFECT_FIRST_MEASUREMENT_SUBJECT_TERMS
            for token in subject_context
        )
''',
    "complete measurement-subject vocabulary",
)

text = replace_once(
    text,
    '''def _preserve_parenthetical_subject_modifiers(text):
    """Keep comma-delimited parenthetical modifiers with their subject."""
    parenthetical_leads = {
        "in", "at", "within", "from", "under", "inside", "amid", "during",
        "with", "without", "after", "before", "near", "across", "throughout",
        "located", "based", "on", "by",
        "에서", "내", "안", "아래", "중", "동안", "근처", "기반",
    }

    def replace(match):
        modifier = match.group(1).strip()
        tokens = _effect_tokens(modifier)
        if not tokens or tokens[0] not in parenthetical_leads:
            return match.group(0)
        has_effect_or_object = any(
            _base._has_any_term(
                token,
                _base.STAGE_A_INTERPRETATION_EFFECT_TERMS
                + _base.STAGE_A_INTERPRETATION_OBJECT_TERMS,
            )
            for token in tokens
        )
        if has_effect_or_object:
            return match.group(0)
        return f" {modifier} "

    return _base.re.sub(r",\\s*([^,;\\n.]+?)\\s*,", replace, text)
''',
    '''def _preserve_parenthetical_subject_modifiers(text):
    """Keep comma-delimited parenthetical modifiers with their subject."""
    parenthetical_leads = {
        "in", "at", "within", "from", "under", "inside", "amid", "during",
        "with", "without", "after", "before", "near", "across", "throughout",
        "located", "based", "on", "by",
        "에서", "내", "안", "아래", "중", "동안", "근처", "기반",
    }
    lead_pattern = "|".join(
        _base.re.escape(term)
        for term in sorted(parenthetical_leads, key=len, reverse=True)
    )

    def replace(match):
        modifier = match.group(1).strip()
        tokens = _effect_tokens(modifier)
        if not tokens or tokens[0] not in parenthetical_leads:
            return match.group(0)
        has_effect_or_object = any(
            _base._has_any_term(
                token,
                _base.STAGE_A_INTERPRETATION_EFFECT_TERMS
                + _base.STAGE_A_INTERPRETATION_OBJECT_TERMS,
            )
            for token in tokens
        )
        if has_effect_or_object:
            return match.group(0)
        return f" {modifier} "

    # Start only at a comma whose following token is a known parenthetical lead.
    # This avoids pairing an introductory comma with a later subject-boundary
    # comma, as in "In 2025, production, in the facility, was weakened ...".
    pattern = rf",\\s*((?:{lead_pattern})(?![\\w])[^,;\\n.]*?)\\s*,"
    return _base.re.sub(pattern, replace, text)
''',
    "parenthetical comma pairing",
)

VALIDATOR.write_text(text, encoding="utf-8")

TEST_FILE.write_text(
    '''from __future__ import annotations

# Regression lock for review 4850764924.
import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4850764924Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4840844831Contracts().base_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_introductory_comma_does_not_hide_parenthetical_measurement_subject(self):
        for effect in (
            "In 2025, Project Alpha production, in the northern manufacturing facility, was weakened under the current demand outlook",
            "In 2025, Project Alpha production, in the northern manufacturing facility, was confirmed under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_spec_rejects_introductory_comma_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "In 2025, Project Alpha production, in the northern manufacturing facility, was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_all_exact_metric_subjects_are_rejected_when_merely_attached(self):
        metrics = (
            "EBITDA", "profit", "utilization", "yield", "throughput",
            "capex", "opex",
        )
        for metric in metrics:
            effect = f"Project Alpha {metric} was weakened under the current demand outlook"
            with self.subTest(metric=metric):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_spec_rejects_exact_metric_attachment_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha EBITDA was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_metric_qualifiers_inside_interpretation_objects_remain_valid(self):
        for effect in (
            "The outlook for Project Alpha capacity would weaken",
            "The demand outlook regarding Project Alpha EBITDA would weaken",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_separate_reported_measurement_event_remains_rejected(self):
        self.assertFalse(
            lineage._valid_confirmation_point(self.confirmation_point(
                "The outlook report says Project Alpha capacity increased"
            ))
        )

    def test_introductory_comma_with_valid_parenthetical_transitive_effect_passes(self):
        self.assertTrue(
            lineage._valid_confirmation_point(self.confirmation_point(
                "In 2025, the filing, from the northern manufacturing facility, weakened the current demand outlook"
            ))
        )


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)

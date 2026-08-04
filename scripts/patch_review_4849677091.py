from pathlib import Path

validator = Path('validation_scripts/stage_lineage_contract_check.py')
text = validator.read_text(encoding='utf-8')
old = '''def _valid_confirmation_point(value):
    if isinstance(value, dict):
        measurable = value.get('measurable_event_or_metric') or value.get('confirmation_event')
        interpretation_effect = value.get('interpretation_effect') or value.get('confirm_weaken_invalidate')
        return _structured_exact_target(measurable) and _structured_interpretation_effect(interpretation_effect)
    text = _normalized_text(value)
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
new = '''STAGE_A_UNAMBIGUOUS_INTERPRETATION_EFFECT_TERMS = (
    'confirm', 'strengthen', 'support', 'weaken', 'invalidate', 'reject', 'revise',
    '확인', '강화', '지지', '약화', '무효', '기각', '수정',
)
STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS = (
    'change', 'raise', 'lower', 'increase', 'decrease', 'hold',
    '변경', '상향', '하향', '증가', '감소', '유지',
)
STAGE_A_INTERPRETATION_OBJECT_TERMS = (
    'thesis', 'interpretation', 'outlook', 'assessment', 'view', 'judgment',
    'expectation', 'confidence', 'probability', 'case', 'conclusion',
    '가설', '해석', '전망', '평가', '판단', '기대', '신뢰', '확률', '결론',
)


def _has_bound_interpretation_effect(value):
    if _has_any_term(value, STAGE_A_UNAMBIGUOUS_INTERPRETATION_EFFECT_TERMS):
        return True
    return (
        _has_any_term(value, STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS)
        and _has_any_term(value, STAGE_A_INTERPRETATION_OBJECT_TERMS)
    )


def _valid_confirmation_point(value):
    if isinstance(value, dict):
        measurable = value.get('measurable_event_or_metric') or value.get('confirmation_event')
        interpretation_effect = value.get('interpretation_effect') or value.get('confirm_weaken_invalidate')
        return _structured_exact_target(measurable) and _structured_interpretation_effect(interpretation_effect)
    text = _normalized_text(value)
    has_measurable_event_or_metric = (
        _has_any_term(text, STAGE_A_CONFIRMATION_EVENT_TERMS)
        or _has_any_term(text, STAGE_A_EXACT_TARGET_TERMS)
    )
    has_interpretation_effect = _has_bound_interpretation_effect(text)
    return (
        bool(text)
        and len(text.split()) >= 4
        and not _placeholder_only_text(text)
        and not _contains_generic_target_fragment(text)
        and has_measurable_event_or_metric
        and has_interpretation_effect
    )
'''
if old not in text:
    raise SystemExit('target confirmation function not found or not unique')
if text.count(old) != 1:
    raise SystemExit(f'target confirmation function count={text.count(old)}')
validator.write_text(text.replace(old, new), encoding='utf-8')

test_path = Path('validation_scripts/tests/test_review_4849677091_contracts.py')
test_path.write_text('''from __future__ import annotations

import unittest

from validation_scripts import stage_lineage_contract_check as lineage


class TestReview4849677091Contracts(unittest.TestCase):
    def test_metric_direction_is_not_an_interpretation_effect(self):
        for value in (
            "Project Alpha production capacity decreased by 10%",
            "Project Alpha production capacity increased to 100 MW",
            "Project Alpha production capacity change reached 100 MW",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._valid_confirmation_point(value))

    def test_directional_effect_bound_to_interpretation_passes(self):
        for value in (
            "Project Alpha production capacity decreased by 10%, lowering the thesis confidence",
            "Project Alpha production capacity increased to 100 MW and raised the adoption outlook",
            "Project Alpha production milestone would change the interpretation",
            "Project Alpha production milestone would hold the thesis",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._valid_confirmation_point(value))

    def test_unambiguous_effect_terms_remain_supported(self):
        for value in (
            "Project Alpha production capacity milestone would confirm adoption",
            "Project Alpha production capacity milestone weakened the thesis",
            "Project Alpha production capacity milestone invalidated the outlook",
            "Project Alpha production capacity milestone revised the assessment",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._valid_confirmation_point(value))

    def test_complete_term_collision_remains_blocked(self):
        self.assertFalse(
            lineage._valid_confirmation_point(
                "Project Alpha production capacity milestone remained unchanged"
            )
        )


if __name__ == "__main__":
    unittest.main()
''', encoding='utf-8')

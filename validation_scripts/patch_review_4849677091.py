#!/usr/bin/env python3
"""Apply and verify the review 4849677091 interpretation-binding patch."""
from pathlib import Path

VALIDATOR = Path("validation_scripts/stage_lineage_contract_check.py")
TEST_FILE = Path("validation_scripts/tests/test_review_4849359963_contracts.py")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {count}")
    return text.replace(old, new, 1)


def patch_validator() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")

    terms_old = """STAGE_A_INTERPRETATION_EFFECT_TERMS = (\n    'confirm', 'strengthen', 'support', 'weaken', 'invalidate', 'reject',\n    'revise', 'change', 'raise', 'lower', 'increase', 'decrease', 'hold',\n    '확인', '강화', '지지', '약화', '무효', '기각', '수정', '변경',\n    '상향', '하향', '증가', '감소', '유지',\n)\n"""
    terms_new = terms_old + """STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS = (\n    'change', 'raise', 'lower', 'increase', 'decrease', 'hold',\n    '변경', '상향', '하향', '증가', '감소', '유지',\n)\nSTAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS = tuple(\n    term for term in STAGE_A_INTERPRETATION_EFFECT_TERMS\n    if term not in STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS\n)\nSTAGE_A_INTERPRETATION_OBJECT_TERMS = (\n    'interpretation', 'thesis', 'outlook', 'judgment', 'judgement',\n    'expectation', 'assessment', 'probability', 'conviction', 'conclusion',\n    'view', 'forecast',\n    '해석', '논지', '전망', '판단', '기대', '평가', '확률', '확신',\n    '결론', '견해', '예측',\n)\n"""
    text = replace_once(text, terms_old, terms_new, "interpretation term constants")

    helper_old = """def _has_any_term(value, terms):\n    return bool(_matching_terms(value, terms))\n\n\ndef _valid_evidence_target(value):\n"""
    helper_new = """def _has_any_term(value, terms):\n    return bool(_matching_terms(value, terms))\n\n\ndef _has_bound_interpretation_effect(value):\n    \"\"\"Require directional terms to modify an interpretation object.\n\n    Direct semantic effects such as confirm/weaken/invalidate are sufficient on\n    their own. Ambiguous direction words such as increase/decrease/hold/change\n    count only when they occur in the same clause and within two intervening\n    tokens of thesis/outlook/interpretation-like language. This prevents a\n    measured event such as \"capacity decreased by 10%\" from masquerading as\n    an interpretation effect.\n    \"\"\"\n    text = _normalized_text(value)\n    if not text:\n        return False\n    if _has_any_term(text, STAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS):\n        return True\n\n    clauses = re.split(\n        r'[.;,\\n]+|\\b(?:but|while|whereas|although|however)\\b|(?:하지만|그러나|반면)',\n        text,\n    )\n    for clause in clauses:\n        clause = clause.strip()\n        if not clause:\n            continue\n        for direction in STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS:\n            direction_pattern = _term_pattern(direction)\n            if not re.search(direction_pattern, clause):\n                continue\n            for interpretation_object in STAGE_A_INTERPRETATION_OBJECT_TERMS:\n                object_pattern = _term_pattern(interpretation_object)\n                if not re.search(object_pattern, clause):\n                    continue\n                between = r'(?:[^\\w]+[\\w]+){0,2}[^\\w]+'\n                if (\n                    re.search(rf'{direction_pattern}{between}{object_pattern}', clause)\n                    or re.search(rf'{object_pattern}{between}{direction_pattern}', clause)\n                ):\n                    return True\n    return False\n\n\ndef _valid_evidence_target(value):\n"""
    text = replace_once(text, helper_old, helper_new, "bound interpretation helper")

    effect_old = """    has_interpretation_effect = _has_any_term(\n        text, STAGE_A_INTERPRETATION_EFFECT_TERMS\n    )\n"""
    effect_new = """    has_interpretation_effect = _has_bound_interpretation_effect(text)\n"""
    text = replace_once(text, effect_old, effect_new, "free-text interpretation effect")

    VALIDATOR.write_text(text, encoding="utf-8")


def patch_tests() -> None:
    text = TEST_FILE.read_text(encoding="utf-8")
    marker = """    def test_generic_confirmation_scaffolds_still_fail(self):\n"""
    additions = """    def test_metric_direction_does_not_count_as_interpretation_effect(self):\n        values = (\n            \"Project Alpha production capacity decreased by 10%\",\n            \"Project Alpha production capacity increased to 100 MW\",\n            \"Project Alpha production capacity held at 100 MW\",\n            \"Project Alpha production capacity changed by 10%\",\n        )\n        for value in values:\n            with self.subTest(value=value):\n                self.assertFalse(lineage._valid_confirmation_point(value))\n\n    def test_direction_bound_to_interpretation_object_passes(self):\n        values = (\n            \"Project Alpha production capacity decreased by 10%, lowering the outlook\",\n            \"Project Alpha production capacity increased to 100 MW, raising adoption probability\",\n            \"The thesis would change if Project Alpha production capacity fell by 10%\",\n            \"Project Alpha 생산 용량 감소는 전망을 하향할 것이다\",\n        )\n        for value in values:\n            with self.subTest(value=value):\n                self.assertTrue(lineage._valid_confirmation_point(value))\n\n    def test_complete_v3_spec_rejects_metric_direction_only_confirmation(self):\n        spec = self.base_v3_spec()\n        spec[\"next_confirmation_points\"] = [\n            \"Project Alpha production capacity decreased by 10%\"\n        ]\n        messages = []\n        self.assertFalse(\n            lineage.validate_stage_a_v3_override(spec, spec[\"spec_id\"], messages)\n        )\n        self.assertTrue(\n            any(\"interpretation effect\" in message for message in messages), messages\n        )\n\n"""
    text = replace_once(text, marker, additions + marker, "review regression tests")
    TEST_FILE.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    patch_validator()
    patch_tests()

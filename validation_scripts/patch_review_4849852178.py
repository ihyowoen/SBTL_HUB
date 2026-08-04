#!/usr/bin/env python3
"""Apply review 4849852178 semantic interpretation-effect fixes, then self-clean."""
from pathlib import Path

VALIDATOR = Path("validation_scripts/stage_lineage_contract_check.py")
TEST_FILE = Path("validation_scripts/tests/test_review_4849852178_contracts.py")
WORKFLOW = Path(".github/workflows/workflow-contract-validation.yml")
SELF = Path(__file__)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {count}")
    return text.replace(old, new, 1)


def patch_validator() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")

    constants_old = """STAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS = tuple(
    term for term in STAGE_A_INTERPRETATION_EFFECT_TERMS
    if term not in STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS
)
STAGE_A_INTERPRETATION_OBJECT_TERMS = (
    'interpretation', 'thesis', 'outlook', 'judgment', 'judgement',
    'expectation', 'assessment', 'probability', 'conviction', 'conclusion',
    'view', 'forecast',
    '해석', '논지', '전망', '판단', '기대', '평가', '확률', '확신',
    '결론', '견해', '예측',
)
"""
    constants_new = """STAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS = tuple(
    term for term in STAGE_A_INTERPRETATION_EFFECT_TERMS
    if term not in STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS
)
STAGE_A_AMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS = (
    'confirm', 'support', '확인', '지지',
)
STAGE_A_UNAMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS = tuple(
    term for term in STAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS
    if term not in STAGE_A_AMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS
)
STAGE_A_INTERPRETATION_OBJECT_TERMS = (
    'interpretation', 'thesis', 'outlook', 'judgment', 'judgement',
    'expectation', 'assessment', 'probability', 'conviction', 'conclusion',
    'view', 'forecast', 'adoption', 'eligibility', 'timeline', 'scenario',
    'case', 'risk',
    '해석', '논지', '전망', '판단', '기대', '평가', '확률', '확신',
    '결론', '견해', '예측', '채택', '적격성', '일정', '시나리오',
    '가정', '위험',
)
STAGE_A_EFFECT_AUXILIARY_TERMS = {
    'would', 'will', 'could', 'can', 'may', 'might', 'should', 'must',
    'do', 'does', 'did', 'to', 'is', 'are', 'was', 'were', 'be', 'been',
    'being',
}
STAGE_A_EFFECT_BRIDGE_BLOCKERS = {
    'and', 'or', 'but', 'then', 'while', 'whereas', 'although', 'however',
    'by', 'to', 'at', 'from', 'versus', 'vs', 'per', 'percent', 'pct',
    'mw', 'mwh', 'gw', 'gwh', 'units', 'unit', 'tons', 'tonnes',
    '그리고', '또는', '하지만', '그러나', '반면', '대비', '에서', '까지',
}
"""
    text = replace_once(text, constants_old, constants_new, "effect constants")

    structured_old = """def _structured_interpretation_effect(value):
    return (
        _structured_component(value)
        and not _contains_generic_fragment(value)
        and _has_any_term(value, STAGE_A_INTERPRETATION_EFFECT_TERMS)
    )
"""
    structured_new = """def _structured_interpretation_effect(value):
    return (
        _structured_component(value)
        and not _contains_generic_fragment(value)
        and _has_bound_interpretation_effect(value)
    )
"""
    text = replace_once(text, structured_old, structured_new, "structured effect binding")

    binder_old = """def _has_bound_interpretation_effect(value):
    \"\"\"Require directional terms to modify an interpretation object.

    Direct semantic effects such as confirm/weaken/invalidate are sufficient on
    their own. Ambiguous direction words such as increase/decrease/hold/change
    count only when they occur in the same clause and within two intervening
    tokens of thesis/outlook/interpretation-like language. This prevents a
    measured event such as \"capacity decreased by 10%\" from masquerading as
    an interpretation effect.
    \"\"\"
    text = _normalized_text(value)
    if not text:
        return False
    if _has_any_term(text, STAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS):
        return True

    clauses = re.split(
        r'[.;,\\n]+|\\b(?:but|while|whereas|although|however)\\b|(?:하지만|그러나|반면)',
        text,
    )
    all_bound_terms = (
        STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS
        + STAGE_A_INTERPRETATION_OBJECT_TERMS
    )
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue

        # Surround matched terms before tokenization. This preserves English
        # inflections and separates Korean particles (for example, 전망을 or
        # 감소는) without weakening complete-term collision protection.
        prepared = clause
        for term in sorted(set(all_bound_terms), key=len, reverse=True):
            prepared = re.sub(
                _term_pattern(term),
                lambda match: f' {match.group(0)} ',
                prepared,
            )
        tokens = re.findall(r'[a-z0-9가-힣]+', prepared)
        direction_positions = [
            index for index, token in enumerate(tokens)
            if _has_any_term(token, STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS)
        ]
        object_positions = [
            index for index, token in enumerate(tokens)
            if _has_any_term(token, STAGE_A_INTERPRETATION_OBJECT_TERMS)
        ]
        if any(
            abs(direction_index - object_index) - 1 <= 2
            for direction_index in direction_positions
            for object_index in object_positions
        ):
            return True
    return False
"""
    binder_new = """def _effect_tokens(clause):
    all_terms = (
        STAGE_A_INTERPRETATION_EFFECT_TERMS
        + STAGE_A_INTERPRETATION_OBJECT_TERMS
    )
    prepared = clause
    for term in sorted(set(all_terms), key=len, reverse=True):
        prepared = re.sub(
            _term_pattern(term),
            lambda match: f' {match.group(0)} ',
            prepared,
        )
    return re.findall(r'[a-z0-9가-힣]+', prepared)


def _effect_bridge_is_semantic(tokens, first_index, second_index):
    start, end = sorted((first_index, second_index))
    bridge = tokens[start + 1:end]
    if len(bridge) > 6:
        return False
    if any(any(char.isdigit() for char in token) for token in bridge):
        return False
    return not any(token in STAGE_A_EFFECT_BRIDGE_BLOCKERS for token in bridge)


def _has_verbal_effect_cue(clause, term):
    pattern = _term_pattern(term)
    base = _normalized_text(term)
    for match in re.finditer(pattern, clause):
        surface = match.group(0).lower()
        if surface != base:
            return True
        prefix_tokens = re.findall(r'[a-z0-9가-힣]+', clause[:match.start()])[-3:]
        if any(token in STAGE_A_EFFECT_AUXILIARY_TERMS for token in prefix_tokens):
            return True
    return False


def _has_bound_interpretation_effect(value):
    \"\"\"Require semantic or grammatical interpretation-effect binding.

    Directional metric words count only when they govern an interpretation
    object in the same clause. Ambiguous direct words such as support/confirm
    must be verbal or bind to thesis/outlook-like language, so metric nouns such
    as \"customer support volume\" cannot satisfy the contract. Ordinary
    determiners and modifiers may intervene, while numeric measurement syntax
    and conjunctions break the binding.
    \"\"\"
    text = _normalized_text(value)
    if not text:
        return False

    clauses = re.split(
        r'[.;,\\n]+|\\b(?:but|while|whereas|although|however)\\b|(?:하지만|그러나|반면)',
        text,
    )
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        tokens = _effect_tokens(clause)
        object_positions = [
            index for index, token in enumerate(tokens)
            if _has_any_term(token, STAGE_A_INTERPRETATION_OBJECT_TERMS)
        ]

        effect_positions = [
            (index, token)
            for index, token in enumerate(tokens)
            if _has_any_term(token, STAGE_A_INTERPRETATION_EFFECT_TERMS)
        ]
        for effect_index, effect_token in effect_positions:
            matched_directional = _matching_terms(
                effect_token, STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS
            )
            matched_direct = _matching_terms(
                effect_token, STAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS
            )

            if any(
                _effect_bridge_is_semantic(tokens, effect_index, object_index)
                for object_index in object_positions
            ):
                return True

            if matched_directional:
                continue

            for direct_term in matched_direct:
                if direct_term in STAGE_A_AMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS:
                    if _has_verbal_effect_cue(clause, direct_term):
                        return True
                elif (
                    direct_term in STAGE_A_UNAMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS
                    and _has_verbal_effect_cue(clause, direct_term)
                ):
                    return True
    return False
"""
    text = replace_once(text, binder_old, binder_new, "semantic effect binder")
    VALIDATOR.write_text(text, encoding="utf-8")


def write_tests() -> None:
    TEST_FILE.write_text(
        '''from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4849852178Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_structured_metric_direction_only_effect_fails(self):
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": "capacity increased",
            })
        )

    def test_structured_direction_bound_to_outlook_passes(self):
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": "would lower the current demand outlook",
            })
        )

    def test_support_metric_noun_does_not_count_as_effect(self):
        self.assertFalse(
            lineage._valid_confirmation_point(
                "Project Alpha customer support volume increased by 10%"
            )
        )

    def test_ambiguous_direct_terms_require_verbal_or_object_binding(self):
        passing = (
            "Project Alpha capacity milestone would confirm adoption",
            "Project Alpha results support the thesis",
            "Project Alpha thesis would be confirmed by the capacity filing",
        )
        for value in passing:
            with self.subTest(value=value):
                self.assertTrue(lineage._valid_confirmation_point(value))

    def test_modifiers_between_direction_and_outlook_are_allowed(self):
        self.assertTrue(
            lineage._valid_confirmation_point(
                "Project Alpha capacity milestone would lower the current demand outlook"
            )
        )

    def test_numeric_metric_bridge_does_not_bind_to_later_outlook(self):
        self.assertFalse(
            lineage._valid_confirmation_point(
                "Project Alpha capacity increased by 10 percent and the outlook remained available"
            )
        )

    def test_complete_v3_spec_rejects_structured_metric_direction_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha capacity 100 MW",
            "interpretation_effect": "capacity increased",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages), messages
        )


if __name__ == "__main__":
    unittest.main()
''',
        encoding="utf-8",
    )


def restore_workflow_and_self_clean() -> None:
    WORKFLOW.write_text(
        '''name: Workflow contract validation

on:
  pull_request:
    paths:
      - "docs/RELATED_LIFECYCLE_CONTRACT.md"
      - "docs/SOURCE_AUDIT_CONTRACT.md"
      - "docs/llm_prompts/v1/**"
      - "validation_data/source_owner_registry.json"
      - "validation_scripts/**"
      - "scripts/lean_cards.mjs"
      - ".github/workflows/lean-cards.yml"
      - ".github/workflows/workflow-contract-validation.yml"
  push:
    branches:
      - agent/workflow-contract-related-source-audit
    paths:
      - "docs/RELATED_LIFECYCLE_CONTRACT.md"
      - "docs/SOURCE_AUDIT_CONTRACT.md"
      - "docs/llm_prompts/v1/**"
      - "validation_data/source_owner_registry.json"
      - "validation_scripts/**"
      - "scripts/lean_cards.mjs"
      - ".github/workflows/lean-cards.yml"
      - ".github/workflows/workflow-contract-validation.yml"

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Compile validators
        run: python -m compileall -q validation_scripts

      - name: Run workflow-contract and exporter regression tests
        run: python -m unittest discover -s validation_scripts/tests -v

      - name: Verify prompt overlays
        run: python validation_scripts/apply_prompt_contract_overlays.py --check
''',
        encoding="utf-8",
    )
    SELF.unlink()


if __name__ == "__main__":
    patch_validator()
    write_tests()
    restore_workflow_and_self_clean()

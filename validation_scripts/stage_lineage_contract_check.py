#!/usr/bin/env python3
"""Compatibility entry point with semantic confirmation-effect binding."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_BASE_PATH = Path(__file__).with_name("stage_lineage_contract_check_base.py")
_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.stage_lineage_contract_check_base", _BASE_PATH
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load validator base from {_BASE_PATH}")
_base = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_base)

_base.STAGE_A_AMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS = (
    "confirm", "support", "확인", "지지",
)
_base.STAGE_A_UNAMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS = tuple(
    term for term in _base.STAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS
    if term not in _base.STAGE_A_AMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS
)
_base.STAGE_A_INTERPRETATION_OBJECT_TERMS = (
    "interpretation", "thesis", "outlook", "judgment", "judgement",
    "expectation", "assessment", "probability", "conviction", "conclusion",
    "view", "forecast", "adoption", "eligibility", "timeline", "scenario",
    "case", "risk",
    "해석", "논지", "전망", "판단", "기대", "평가", "확률", "확신",
    "결론", "견해", "예측", "채택", "적격성", "일정", "시나리오",
    "가정", "위험",
)
_base.STAGE_A_EFFECT_AUXILIARY_TERMS = {
    "would", "will", "could", "can", "may", "might", "should", "must",
    "do", "does", "did", "to", "is", "are", "was", "were", "be", "been",
    "being",
}
_base.STAGE_A_EFFECT_BRIDGE_BLOCKERS = {
    "and", "or", "but", "then", "while", "whereas", "although", "however",
    "by", "to", "at", "from", "versus", "vs", "per", "percent", "pct",
    "mw", "mwh", "gw", "gwh", "units", "unit", "tons", "tonnes",
    "그리고", "또는", "하지만", "그러나", "반면", "대비", "에서", "까지",
}


def _effect_tokens(clause):
    all_terms = (
        _base.STAGE_A_INTERPRETATION_EFFECT_TERMS
        + _base.STAGE_A_INTERPRETATION_OBJECT_TERMS
    )
    prepared = clause
    for term in sorted(set(all_terms), key=len, reverse=True):
        prepared = _base.re.sub(
            _base._term_pattern(term),
            lambda match: f" {match.group(0)} ",
            prepared,
        )
    return _base.re.findall(r"[a-z0-9가-힣]+", prepared)


def _effect_bridge_is_semantic(tokens, first_index, second_index):
    start, end = sorted((first_index, second_index))
    bridge = tokens[start + 1:end]
    if len(bridge) > 6:
        return False
    if any(any(char.isdigit() for char in token) for token in bridge):
        return False
    return not any(token in _base.STAGE_A_EFFECT_BRIDGE_BLOCKERS for token in bridge)


def _has_verbal_effect_cue(clause, term):
    pattern = _base._term_pattern(term)
    base = _base._normalized_text(term)
    for match in _base.re.finditer(pattern, clause):
        surface = match.group(0).lower()
        if surface != base:
            return True
        prefix_tokens = _base.re.findall(r"[a-z0-9가-힣]+", clause[:match.start()])[-3:]
        if any(token in _base.STAGE_A_EFFECT_AUXILIARY_TERMS for token in prefix_tokens):
            return True
    return False


def _has_bound_interpretation_effect(value):
    """Require semantic or grammatical interpretation-effect binding."""
    text = _base._normalized_text(value)
    if not text:
        return False

    clauses = _base.re.split(
        r"[.;,\n]+|\b(?:but|while|whereas|although|however)\b|(?:하지만|그러나|반면)",
        text,
    )
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        tokens = _effect_tokens(clause)
        object_positions = [
            index for index, token in enumerate(tokens)
            if _base._has_any_term(token, _base.STAGE_A_INTERPRETATION_OBJECT_TERMS)
        ]
        effect_positions = [
            (index, token)
            for index, token in enumerate(tokens)
            if _base._has_any_term(token, _base.STAGE_A_INTERPRETATION_EFFECT_TERMS)
        ]
        for effect_index, effect_token in effect_positions:
            matched_directional = _base._matching_terms(
                effect_token, _base.STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS
            )
            matched_direct = _base._matching_terms(
                effect_token, _base.STAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS
            )
            if any(
                _effect_bridge_is_semantic(tokens, effect_index, object_index)
                for object_index in object_positions
            ):
                return True
            if matched_directional:
                continue
            for direct_term in matched_direct:
                if direct_term in _base.STAGE_A_AMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS:
                    if _has_verbal_effect_cue(clause, direct_term):
                        return True
                elif (
                    direct_term in _base.STAGE_A_UNAMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS
                    and _has_verbal_effect_cue(clause, direct_term)
                ):
                    return True
    return False


def _structured_interpretation_effect(value):
    return (
        _base._structured_component(value)
        and not _base._contains_generic_fragment(value)
        and _has_bound_interpretation_effect(value)
    )


_base._efffect_tokens = _effect_tokens
_base._effect_bridge_is_semantic = _effect_bridge_is_semantic
_base._has_verbal_effect_cue = _has_verbal_effect_cue
_base._has_bound_interpretation_effect = _has_bound_interpretation_effect
_base._structured_interpretation_effect = _structured_interpretation_effect

for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)

if __name__ == "__main__":
    _base.sys.exit(_base.main())

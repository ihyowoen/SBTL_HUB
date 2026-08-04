#!/usr/bin/env python3
"""Compatibility entry point with qualified-object and clause-boundary guards."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_SEMANTIC_PATH = Path(__file__).with_name("stage_lineage_contract_check_semantic.py")
_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.stage_lineage_contract_check_semantic", _SEMANTIC_PATH
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load semantic validator from {_SEMANTIC_PATH}")
_semantic = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_semantic)

# Preserve the complete prior public/import surface before applying the narrow
# review-specific semantic refinements below.
for _name in dir(_semantic):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_semantic, _name)

_base = _semantic._base
_prior_effect_bridge_is_semantic = _semantic._effect_bridge_is_semantic
_prior_has_bound_interpretation_effect = _semantic._has_bound_interpretation_effect

_QUALIFIED_OBJECT_CONJUNCTION_TERMS = {"and", "or", "그리고", "또는"}
_CAUSAL_CLAUSE_PATTERN = (
    r"\b(?:because|since|as)\b|(?:때문에|이므로|므로)"
)


def _qualified_object_bridge_allows_conjunctions(tokens, effect_index, object_index):
    """Allow conjunctions only when they join qualified interpretation nouns."""
    if object_index >= effect_index:
        return False

    bridge = tokens[object_index + 1:effect_index]
    conjunction_positions = [
        index for index, token in enumerate(bridge)
        if token in _QUALIFIED_OBJECT_CONJUNCTION_TERMS
    ]
    if not conjunction_positions:
        return False

    qualifier_positions = [
        index for index, token in enumerate(bridge)
        if token in _base.STAGE_A_INTERPRETATION_OBJECT_QUALIFIER_TERMS
    ]
    measurement_positions = [
        index for index, token in enumerate(bridge)
        if token in _base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS
    ]
    if not qualifier_positions or len(measurement_positions) < 2:
        return False

    first_qualifier = min(qualifier_positions)
    if not all(first_qualifier < position for position in measurement_positions):
        return False

    # Each allowed conjunction must sit between two qualified measurement nouns;
    # this keeps ordinary clause-level conjunctions fail-closed.
    return all(
        conjunction_position > first_qualifier
        and any(
            first_qualifier < measurement_position < conjunction_position
            for measurement_position in measurement_positions
        )
        and any(
            conjunction_position < measurement_position
            for measurement_position in measurement_positions
        )
        for conjunction_position in conjunction_positions
    )


def _effect_bridge_is_semantic(tokens, effect_index, object_index):
    """Delegate to the prior binder, permitting only qualified noun joins."""
    if not _qualified_object_bridge_allows_conjunctions(
        tokens, effect_index, object_index
    ):
        return _prior_effect_bridge_is_semantic(
            tokens, effect_index, object_index
        )

    # A conjunction joining two nouns is grammatical structure, not another
    # semantic modifier. Remove only the validated join tokens before applying
    # the preserved six-token bridge contract, and adjust the effect index.
    sanitized_tokens = []
    removed_before_effect = 0
    for index, token in enumerate(tokens):
        if (
            object_index < index < effect_index
            and token in _QUALIFIED_OBJECT_CONJUNCTION_TERMS
        ):
            removed_before_effect += 1
            continue
        sanitized_tokens.append(token)
    return _prior_effect_bridge_is_semantic(
        sanitized_tokens,
        effect_index - removed_before_effect,
        object_index,
    )


def _parenthetical_modifier_is_safe(modifier, parenthetical_leads):
    """Preserve subject parentheticals unless they contain their own effect."""
    tokens = _semantic._effect_tokens(modifier)
    if not tokens or tokens[0] not in parenthetical_leads:
        return False
    return not any(
        _base._has_any_term(
            token,
            _base.STAGE_A_INTERPRETATION_EFFECT_TERMS,
        )
        for token in tokens
    )


def _sanitize_parenthetical_interpretation_objects(modifier):
    """Keep modifier context without exposing a stale object to effect binding."""
    sanitized = modifier
    for term in sorted(
        set(_base.STAGE_A_INTERPRETATION_OBJECT_TERMS), key=len, reverse=True
    ):
        sanitized = _base.re.sub(
            _base._term_pattern(term),
            "context",
            sanitized,
        )
    return sanitized


def _preserve_parenthetical_subject_modifiers(text):
    """Preserve one or more adjacent comma-delimited subject modifiers."""
    parenthetical_leads = {
        "in", "at", "within", "from", "under", "inside", "amid", "during",
        "with", "without", "after", "before", "near", "across", "throughout",
        "located", "based", "on", "by",
        "에서", "내", "안", "아래", "중", "동안", "근처", "기반",
    }

    result = text
    search_from = 0
    while True:
        opening_comma = result.find(",", search_from)
        if opening_comma < 0:
            break
        closing_comma = result.find(",", opening_comma + 1)
        if closing_comma < 0:
            break

        modifier = result[opening_comma + 1:closing_comma].strip()
        if not _parenthetical_modifier_is_safe(modifier, parenthetical_leads):
            search_from = opening_comma + 1
            continue

        modifiers = [_sanitize_parenthetical_interpretation_objects(modifier)]
        sequence_end = closing_comma
        while True:
            next_closing_comma = result.find(",", sequence_end + 1)
            if next_closing_comma < 0:
                break
            next_modifier = result[
                sequence_end + 1:next_closing_comma
            ].strip()
            if not _parenthetical_modifier_is_safe(
                next_modifier, parenthetical_leads
            ):
                break
            modifiers.append(
                _sanitize_parenthetical_interpretation_objects(next_modifier)
            )
            sequence_end = next_closing_comma

        replacement = " " + " ".join(modifiers) + " "
        result = (
            result[:opening_comma]
            + replacement
            + result[sequence_end + 1:]
        )
        search_from = opening_comma + len(replacement)

    return result


def _has_bound_interpretation_effect(value):
    """Evaluate causal clauses independently before semantic effect binding."""
    text = _base._normalized_text(value)
    if not text:
        return False

    causal_clauses = _base.re.split(_CAUSAL_CLAUSE_PATTERN, text)
    return any(
        _prior_has_bound_interpretation_effect(clause.strip())
        for clause in causal_clauses
        if clause.strip()
    )


def _structured_interpretation_effect(value):
    return (
        _base._structured_component(value)
        and not _base._contains_generic_target_fragment(value)
        and _has_bound_interpretation_effect(value)
    )


# The preserved semantic layer resolves these names at call time. Updating both
# module namespaces therefore keeps direct imports, CLI execution, and base
# validator callbacks on the same contract.
_semantic._effect_bridge_is_semantic = _effect_bridge_is_semantic
_semantic._preserve_parenthetical_subject_modifiers = (
    _preserve_parenthetical_subject_modifiers
)
_semantic._has_bound_interpretation_effect = _has_bound_interpretation_effect
_semantic._structured_interpretation_effect = _structured_interpretation_effect

_base._effect_bridge_is_semantic = _effect_bridge_is_semantic
_base._preserve_parenthetical_subject_modifiers = (
    _preserve_parenthetical_subject_modifiers
)
_base._has_bound_interpretation_effect = _has_bound_interpretation_effect
_base._structured_interpretation_effect = _structured_interpretation_effect

if __name__ == "__main__":
    _base.sys.exit(_base.main())

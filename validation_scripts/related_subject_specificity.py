#!/usr/bin/env python3
"""Stable Related subject-specificity policy implementation.

This module owns the latest subject-specificity policy directly. Historical
review-ID layers remain below this boundary and can be collapsed separately
without changing the public Related validator entrypoint.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Direct script execution starts with validation_scripts/ on sys.path. Add the
# repository root before absolute package imports, matching the public CLI.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from validation_scripts.module_seam import (
    clone_module_with_rebound_functions as _clone_module_with_rebound_functions,
)
from validation_scripts import related_subject_specificity_metric_base as _base

# Build a stable-only metric namespace. The inherited validator callables are
# explicitly rebound to the clone so the whole stable graph resolves through
# one isolated globals dictionary without the legacy callable seam.
_base = _clone_module_with_rebound_functions(
    _base,
    module_name=f"{__name__}._metric",
    function_names=("check_card", "main"),
)

# Keep source-level chronology contracts visible to static checks.
_RESOLVED_PROVISIONAL_TARGETS_CONTRACT = "resolved_provisional_targets"
_PROVISIONAL_CHRONOLOGY_ERROR_CONTRACT = (
    "follow-up date precedes provisional predecessor"
)

for _name, _value in vars(_base).items():
    if not _name.startswith("__") and _name not in {"_base", "_prior"}:
        globals()[_name] = _value

_prior_item_specific_lineage_assertion = _base.item_specific_lineage_assertion
_PERIOD_OR_COMPARATIVE_TERMS = {
    "fy", "cy", "yoy", "qoq", "mom", "wow", "ytd", "qtd", "mtd",
    "ttm", "ltm",
}
_RECURRING_PERIOD_TERMS = {
    "quarterly", "annual", "annually", "monthly", "weekly", "daily",
}
_GENERIC_TITLE_MODIFIERS = {
    "first", "ever", "extraordinary", "novel", "unexpected", "severe",
    "historic", "historical", "dramatic", "sudden", "record", "surprising",
    "unprecedented", "exceptional", "temporary", "persistent", "structural",
    "cyclical", "seasonal", "broad", "modest", "major", "minor", "large",
    "small", "rapid", "gradual", "significant", "material", "substantial",
    "sharp", "strong", "weak", "notable", "meaningful", "recent",
    "expected", "projected", "reported", "documented", "verified",
    "continued", "continuing", "further", "ongoing", "alarming", "steep",
    "abrupt", "emerging", "leading", "new", "global", "local", "public",
    "private",
}
_CORPORATE_NAME_SUFFIXES = {
    "motor", "motors", "energy", "power", "technology", "technologies",
    "holding", "holdings", "group", "corporation", "corp", "inc", "ltd",
    "company", "system", "systems", "solution", "solutions", "industry",
    "industries", "industrial",
}
_GOVERNED_SINGLE_TOKEN_ENTITY_NAMES = set(
    getattr(_base, "_KNOWN_SINGLE_TOKEN_ENTITY_NAMES", set())
) | {
    "tesla", "sbtl", "acme", "panasonic", "ford", "toyota",
}
_SPELLED_PERCENT_RE = re.compile(
    r"(?<![a-z0-9가-힣])[-+]?\d+(?:[.,]\d+)?\s*(?:percent|percentage|퍼센트)(?![a-z0-9가-힣])",
    re.IGNORECASE,
)
_EXPLICIT_CLASS_BOUND_RE = re.compile(
    r"\b(?i:project|plant|facility|site|line|phase|unit|factory|program)\s+"
    r"(?:[A-Z][A-Za-z0-9-]*|\d+)\b|"
    r"(?:제?\d+|[A-Za-z]\d*)\s*(?:공장|프로젝트|사업|시설|플랜트|라인|단지)"
)
_ENGLISH_CLASS_BOUND_CAPTURE_RE = re.compile(
    r"\b(?P<class>(?i:project|plant|facility|site|line|phase|unit|factory|program))\s+"
    r"(?P<identifier>[A-Z][A-Za-z0-9-]*|\d+)\b"
)


def _assertion_parts(value):
    normalized_value = _base._prior._normalize_assertion_text(value)
    normalized = _base._prior._base.re.sub(
        r"[^a-z0-9가-힣]+", " ", normalized_value
    ).strip()
    tokens = [token for token in normalized.split() if token]
    role_tokens = [
        _base._prior._normalize_assertion_role_token(token) for token in tokens
    ]
    subject_tokens = [
        _base._prior._normalize_subject_token(token) for token in role_tokens
    ]
    temporal_indexes = _base._prior._assertion_temporal_token_indexes(tokens)
    original_tokens = _base._original_assertion_tokens(value)
    return tokens, role_tokens, subject_tokens, temporal_indexes, original_tokens


def _candidate_indexes(role_tokens, subject_tokens, temporal_indexes):
    indexes = []
    for index, (role_token, subject_token) in enumerate(
        zip(role_tokens, subject_tokens)
    ):
        if index in temporal_indexes or subject_token.isdigit():
            continue
        if role_token in _base._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS:
            continue
        if role_token in _base._NOMINAL_CHANGE_TERMS:
            continue
        if role_token in _base._SUBJECTLESS_NOMINAL_MODIFIER_TERMS:
            continue
        if subject_token in _base._GENERIC_JUDGMENT_DESCRIPTOR_TERMS:
            continue
        if subject_token in _base._prior._ASSERTION_NEUTRAL_SUBJECT_TOKENS:
            continue
        if subject_token in _base._prior._GENERIC_OWNER_SINGULARS:
            continue
        if subject_token in _base._prior._base._GENERIC_LINEAGE_ASSERTION_TOKENS:
            continue
        indexes.append(index)
    return indexes


def _normalized_token_forms(token):
    raw = str(token).casefold()
    role = _base._prior._normalize_assertion_role_token(token)
    subject = _base._prior._normalize_subject_token(role)
    return {raw, role, subject}


def _identifier_is_blocked(identifier):
    raw_identifier = str(identifier)
    # A single uppercase letter is an explicit class-bound identifier, not the
    # neutral indefinite article produced by case-folding (Project A). Numeric
    # identifiers are likewise concrete labels (Plant 1, Facility 2).
    if re.fullmatch(r"(?:[A-Z]|\d+)", raw_identifier):
        return False
    blocked = (
        set(_base._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS)
        | set(_base._NOMINAL_CHANGE_TERMS)
        | set(_base._prior._ASSERTION_CHANGE_PREDICATE_TERMS)
        | set(_base._SUBJECTLESS_NOMINAL_MODIFIER_TERMS)
        | set(_base._GENERIC_JUDGMENT_DESCRIPTOR_TERMS)
        | set(_PERIOD_OR_COMPARATIVE_TERMS)
        | set(_RECURRING_PERIOD_TERMS)
        | set(_GENERIC_TITLE_MODIFIERS)
        | set(_CORPORATE_NAME_SUFFIXES)
        | set(_base._prior._ASSERTION_NEUTRAL_SUBJECT_TOKENS)
        | set(_base._prior._GENERIC_OWNER_SINGULARS)
        | set(_base._prior._base._GENERIC_LINEAGE_ASSERTION_TOKENS)
    )
    return bool(_normalized_token_forms(identifier) & blocked)


def _has_invalid_capitalized_class_identifier(value):
    matches = list(_ENGLISH_CLASS_BOUND_CAPTURE_RE.finditer(str(value)))
    return bool(matches) and any(
        _identifier_is_blocked(match.group("identifier")) for match in matches
    )


def _has_generic_corporate_suffix_bypass(
    role_tokens,
    subject_tokens,
    original_tokens,
):
    for index in range(1, len(subject_tokens)):
        suffix_forms = {
            str(original_tokens[index]).casefold(),
            role_tokens[index],
            subject_tokens[index],
        }
        if not (suffix_forms & _CORPORATE_NAME_SUFFIXES):
            continue
        lead_forms = {
            str(original_tokens[index - 1]).casefold(),
            role_tokens[index - 1],
            subject_tokens[index - 1],
        }
        if lead_forms & _GENERIC_TITLE_MODIFIERS:
            return True
    return False


def _has_bound_corporate_suffix(
    role_tokens,
    subject_tokens,
    original_tokens,
):
    for index in range(1, len(subject_tokens)):
        suffix_forms = {
            str(original_tokens[index]).casefold(),
            role_tokens[index],
            subject_tokens[index],
        }
        if not (suffix_forms & _CORPORATE_NAME_SUFFIXES):
            continue
        lead = str(original_tokens[index - 1])
        lead_forms = {
            lead.casefold(), role_tokens[index - 1], subject_tokens[index - 1]
        }
        if lead_forms & _GENERIC_TITLE_MODIFIERS:
            continue
        if (
            lead.casefold() in _GOVERNED_SINGLE_TOKEN_ENTITY_NAMES
            or lead[:1].isupper()
            or lead.isupper()
            or any(char.isupper() for char in lead[1:])
            or any(char.isdigit() for char in lead)
        ):
            return True
    return False


def _has_unsupported_single_titlecase_subject(
    value,
    role_tokens,
    subject_tokens,
    temporal_indexes,
    original_tokens,
):
    candidates = [
        index
        for index in _candidate_indexes(
            role_tokens, subject_tokens, temporal_indexes
        )
        if subject_tokens[index] not in _PERIOD_OR_COMPARATIVE_TERMS
        and subject_tokens[index] not in _GENERIC_TITLE_MODIFIERS
    ]
    if len(candidates) != 1 or candidates[0] != 0:
        return False
    original = original_tokens[0]
    subject = subject_tokens[0]
    if (
        subject in _GOVERNED_SINGLE_TOKEN_ENTITY_NAMES
        or original.isupper()
        or any(char.isupper() for char in original[1:])
        or any(char.isdigit() for char in original)
        or _EXPLICIT_CLASS_BOUND_RE.search(str(value))
        or _has_bound_corporate_suffix(role_tokens, subject_tokens, original_tokens)
        or "'" in str(value)
        or "’" in str(value)
    ):
        return False
    return (
        len(original) >= 2
        and original[:1].isupper()
        and original[1:].islower()
    )


def _has_unseen_single_token_entity(
    value,
    role_tokens,
    subject_tokens,
    temporal_indexes,
    original_tokens,
):
    candidates = [
        index
        for index in _candidate_indexes(
            role_tokens, subject_tokens, temporal_indexes
        )
        if subject_tokens[index] not in _PERIOD_OR_COMPARATIVE_TERMS
        and subject_tokens[index] not in _GENERIC_TITLE_MODIFIERS
    ]
    if len(candidates) != 1:
        return False
    index = candidates[0]
    original = original_tokens[index]
    return (
        index == 0
        and subject_tokens[index] in _GOVERNED_SINGLE_TOKEN_ENTITY_NAMES
        and len(original) >= 2
        and original[:1].isupper()
    )


def _has_positive_subject(
    value,
    tokens,
    role_tokens,
    subject_tokens,
    temporal_indexes,
    original_tokens,
):
    concrete_label = _base._prior._has_concrete_entity_label(tokens)
    if _EXPLICIT_CLASS_BOUND_RE.search(str(value)):
        return True
    if _has_bound_corporate_suffix(role_tokens, subject_tokens, original_tokens):
        return True
    if _base._has_positively_identifiable_subject(
        value,
        tokens,
        role_tokens,
        subject_tokens,
        temporal_indexes,
        concrete_label,
    ):
        return True
    return _has_unseen_single_token_entity(
        value,
        role_tokens,
        subject_tokens,
        temporal_indexes,
        original_tokens,
    )


def _is_titlecase_modifier_pair_without_entity_cue(
    value,
    role_tokens,
    subject_tokens,
    temporal_indexes,
    original_tokens,
):
    indexes = _candidate_indexes(role_tokens, subject_tokens, temporal_indexes)
    title_indexes = [
        index
        for index in indexes
        if original_tokens[index][:1].isupper()
        and original_tokens[index][1:].islower()
    ]
    if len(title_indexes) < 2:
        return False
    if _EXPLICIT_CLASS_BOUND_RE.search(str(value)):
        return False
    if _has_bound_corporate_suffix(role_tokens, subject_tokens, original_tokens):
        return False
    if "'" in str(value) or "’" in str(value):
        return False
    return True


def item_specific_lineage_assertion(value):
    """Close subject-fabrication bypasses while preserving named developments."""
    (
        tokens,
        role_tokens,
        subject_tokens,
        temporal_indexes,
        original_tokens,
    ) = _assertion_parts(value)
    if not tokens or len(original_tokens) != len(tokens):
        return _prior_item_specific_lineage_assertion(value)

    metric_roles = {
        token
        for token in role_tokens
        if token in _base._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
    }
    has_nominal_change = any(
        token in _base._NOMINAL_CHANGE_TERMS for token in role_tokens
    )
    has_change_predicate = has_nominal_change or any(
        token in _base._prior._ASSERTION_CHANGE_PREDICATE_TERMS
        for token in role_tokens
    )

    if metric_roles and _has_invalid_capitalized_class_identifier(value):
        return False
    if metric_roles and _has_generic_corporate_suffix_bypass(
        role_tokens, subject_tokens, original_tokens
    ):
        return False
    if metric_roles and _has_unsupported_single_titlecase_subject(
        value,
        role_tokens,
        subject_tokens,
        temporal_indexes,
        original_tokens,
    ):
        return False

    has_positive_subject = _has_positive_subject(
        value,
        tokens,
        role_tokens,
        subject_tokens,
        temporal_indexes,
        original_tokens,
    )

    if (
        metric_roles
        and has_change_predicate
        and _EXPLICIT_CLASS_BOUND_RE.search(str(value))
    ):
        return True

    candidates = _candidate_indexes(role_tokens, subject_tokens, temporal_indexes)
    if metric_roles and has_change_predicate and candidates and all(
        subject_tokens[index] in _PERIOD_OR_COMPARATIVE_TERMS
        for index in candidates
    ):
        return False

    if metric_roles and has_nominal_change:
        if _is_titlecase_modifier_pair_without_entity_cue(
            value,
            role_tokens,
            subject_tokens,
            temporal_indexes,
            original_tokens,
        ):
            return False
        if _has_unseen_single_token_entity(
            value,
            role_tokens,
            subject_tokens,
            temporal_indexes,
            original_tokens,
        ):
            return True

    if metric_roles and has_positive_subject:
        if any(token in _RECURRING_PERIOD_TERMS for token in role_tokens):
            return True
        if _SPELLED_PERCENT_RE.search(str(value)):
            return True

    return _prior_item_specific_lineage_assertion(value)


_base.item_specific_lineage_assertion = item_specific_lineage_assertion
check_card = _base.check_card
main = _base.main

if __name__ == "__main__":
    raise SystemExit(main())

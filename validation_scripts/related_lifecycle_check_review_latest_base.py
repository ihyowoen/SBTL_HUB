#!/usr/bin/env python3
"""Review follow-up compatibility layer for Related subject specificity."""
from __future__ import annotations

import re

from validation_scripts import related_lifecycle_check_review4871397803_base as _base

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
    "continued", "continuing", "further", "ongoing",
}
_CORPORATE_NAME_SUFFIXES = {
    "motors", "energy", "power", "technologies", "technology", "holdings",
    "group", "corporation", "corp", "inc", "ltd", "company", "systems",
    "solutions", "industries", "industrial",
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
        and len(original) >= 2
        and original[:1].isupper()
        and original[1:].islower()
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
    if any(
        subject_tokens[index] in _CORPORATE_NAME_SUFFIXES
        for index in title_indexes
    ):
        return False
    if "'" in str(value) or "’" in str(value):
        return False
    return True


def item_specific_lineage_assertion(value):
    """Close period/title bypasses while preserving real named developments."""
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


# `check_card` is a re-exported function whose globals belong to the original
# validator module. Patch that exact namespace so strict fields and CLI use the
# same final policy without mutating a guessed `_base/_prior` chain.
check_card = _base.check_card
check_card.__globals__["item_specific_lineage_assertion"] = (
    item_specific_lineage_assertion
)
main = _base.main
main.__globals__["check_card"] = check_card
globals()["item_specific_lineage_assertion"] = item_specific_lineage_assertion

if __name__ == "__main__":
    raise SystemExit(main())

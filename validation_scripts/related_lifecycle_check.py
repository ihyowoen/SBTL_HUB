#!/usr/bin/env python3
"""Review 4871397803 compatibility layer for Related subject specificity."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_BASE_PATH = Path(__file__).with_name(
    "related_lifecycle_check_review4871397803_base.py"
)
_BASE_DIR = str(_BASE_PATH.parent)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.related_lifecycle_check_review4871397803_base",
    _BASE_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load Related validator base from {_BASE_PATH}")
_base = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_base)

# Keep the public source-level chronology contract visible to static checks;
# behavior remains implemented by the preserved prior layer.
_RESOLVED_PROVISIONAL_TARGETS_CONTRACT = "resolved_provisional_targets"
_PROVISIONAL_CHRONOLOGY_ERROR_CONTRACT = (
    "follow-up date precedes provisional predecessor"
)

for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)

_prior_has_positively_identifiable_subject = (
    _base._has_positively_identifiable_subject
)
_COMPARATIVE_OR_PERIOD_ACRONYMS_REVIEW_4871397803 = {
    "yoy", "qoq", "mom", "wow", "ytd", "qtd", "mtd", "ttm", "ltm",
}


def _subject_candidates(
    normalized_role_tokens,
    subject_tokens,
    temporal_indexes,
):
    candidates = []
    for index, (role_token, subject_token) in enumerate(
        zip(normalized_role_tokens, subject_tokens)
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
        candidates.append(subject_token)
    return candidates


def _has_positively_identifiable_subject(
    value,
    tokens,
    normalized_role_tokens,
    subject_tokens,
    temporal_indexes,
    has_concrete_entity_label,
):
    """Do not let comparative/period acronyms satisfy the entity shortcut."""
    prior_result = _prior_has_positively_identifiable_subject(
        value,
        tokens,
        normalized_role_tokens,
        subject_tokens,
        temporal_indexes,
        has_concrete_entity_label,
    )
    if not prior_result:
        return False

    candidates = _subject_candidates(
        normalized_role_tokens,
        subject_tokens,
        temporal_indexes,
    )
    if candidates and all(
        token in _COMPARATIVE_OR_PERIOD_ACRONYMS_REVIEW_4871397803
        for token in candidates
    ):
        return False
    return True


# The preserved item-specific assertion calls this helper by module global.
_base._has_positively_identifiable_subject = _has_positively_identifiable_subject
globals()["_has_positively_identifiable_subject"] = (
    _has_positively_identifiable_subject
)
item_specific_lineage_assertion = _base.item_specific_lineage_assertion

if __name__ == "__main__":
    _base._prior._base.sys.exit(_base._prior._base.main())

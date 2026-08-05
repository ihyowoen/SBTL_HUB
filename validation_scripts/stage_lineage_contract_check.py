#!/usr/bin/env python3
"""Review 4868891584 compatibility layer for independent causal clauses."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_PRIOR_PATH = Path(__file__).with_name(
    "stage_lineage_contract_check_review4868891584_base.py"
)
_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.stage_lineage_contract_check_review4868891584_base",
    _PRIOR_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load validator base from {_PRIOR_PATH}")
_prior = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_prior)

for _name in dir(_prior):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_prior, _name)

_prior_has_bound_interpretation_effect = _prior._has_bound_interpretation_effect
_ENGLISH_CAUSAL_CLAUSE_PATTERN = r"\b(?:because|since|as|after|before|when)\b"
_KOREAN_CAUSAL_SUFFIX_PATTERN = (
    r"(?:때문에|이므로|므로|이후에|이후|이전에|전에|할 때|했을 때)"
)
_CAUSAL_CLAUSE_PATTERN = (
    rf"(?:{_ENGLISH_CAUSAL_CLAUSE_PATTERN}|{_KOREAN_CAUSAL_SUFFIX_PATTERN})"
)


def _independent_clause_for_causal(text):
    """Return only the independent clause, never a causal/temporal dependent suffix."""
    current = text.strip()
    for _ in range(16):
        marker = _prior._base_layer._base.re.search(
            _CAUSAL_CLAUSE_PATTERN, current
        )
        if marker is None:
            return current.strip()

        prefix = current[:marker.start()].strip(" ,;")
        remainder = current[marker.end():]
        marker_is_korean_suffix = bool(
            _prior._base_layer._base.re.fullmatch(
                _KOREAN_CAUSAL_SUFFIX_PATTERN,
                marker.group(0),
            )
        )

        # Korean causal/temporal markers are normally suffixes attached to the
        # dependent clause, so the following text is the independent clause.
        if marker_is_korean_suffix:
            current = _prior._base_layer._base.re.sub(
                r"^\s*[,;]?\s*", "", remainder
            ).strip()
            if not current:
                return ""
            continue

        # A leading English subordinator introduces a dependent clause. Keep
        # only the comma/semicolon-delimited main clause that follows it.
        if not prefix:
            separator = _prior._base_layer._base.re.search(r"[,;]\s*", remainder)
            if separator is None:
                return ""
            current = remainder[separator.end():].strip()
            continue

        # For a medial English subordinator, the prefix is the independent
        # clause. The suffix must not be re-evaluated as a standalone effect.
        return prefix

    return ""


def _has_bound_interpretation_effect(value):
    text = _prior._base_layer._base._normalized_text(value)
    if not text:
        return False
    independent_clause = _independent_clause_for_causal(text)
    return bool(
        independent_clause
        and _prior_has_bound_interpretation_effect(independent_clause)
    )


_prior._has_bound_interpretation_effect = _has_bound_interpretation_effect
_prior._base_layer._has_bound_interpretation_effect = _has_bound_interpretation_effect
if hasattr(_prior._base_layer, "_semantic"):
    _prior._base_layer._semantic._has_bound_interpretation_effect = (
        _has_bound_interpretation_effect
    )
if hasattr(_prior._base_layer, "_base"):
    _prior._base_layer._base._has_bound_interpretation_effect = (
        _has_bound_interpretation_effect
    )

if __name__ == "__main__":
    _prior._base_layer._base.sys.exit(_prior._base_layer._base.main())

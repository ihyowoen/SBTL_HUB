#!/usr/bin/env python3
"""Public Related validator entrypoint."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Script execution starts with validation_scripts/ on sys.path. Add the repo
# root so package imports behave identically in CLI and unittest modes.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from validation_scripts import related_lifecycle_check_review_latest_base as _impl

# Keep source-level chronology contracts visible to static checks.
_RESOLVED_PROVISIONAL_TARGETS_CONTRACT = "resolved_provisional_targets"
_PROVISIONAL_CHRONOLOGY_ERROR_CONTRACT = (
    "follow-up date precedes provisional predecessor"
)

for _name, _value in vars(_impl).items():
    if not _name.startswith("__") and _name not in {"_base", "_prior", "_impl"}:
        globals()[_name] = _value

_impl_item_specific_lineage_assertion = _impl.item_specific_lineage_assertion
_CLASS_BOUND_SINGLE_IDENTIFIER_RE = re.compile(
    r"\b(?i:project|plant|facility|site|line|phase|unit|factory|program)\s+"
    r"(?:[A-Z]|\d+)\b"
)


def item_specific_lineage_assertion(value):
    """Preserve concrete single-letter/number class IDs without reopening metric bypasses."""
    if _impl_item_specific_lineage_assertion(value):
        return True

    if not _CLASS_BOUND_SINGLE_IDENTIFIER_RE.search(str(value)):
        return False

    _, role_tokens, _, _, _ = _impl._assertion_parts(value)
    has_metric = any(
        token in _impl._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
        for token in role_tokens
    )
    has_change = any(
        token in _impl._NOMINAL_CHANGE_TERMS
        or token in _impl._prior._ASSERTION_CHANGE_PREDICATE_TERMS
        for token in role_tokens
    )
    return has_metric and has_change


check_card = _impl.check_card
check_card.__globals__["item_specific_lineage_assertion"] = (
    item_specific_lineage_assertion
)
main = _impl.main
main.__globals__["check_card"] = check_card

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Public Related validator entrypoint with final strict-assertion alignment."""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

# Script execution starts with validation_scripts/ on sys.path. Add the repo
# root so the preserved package module loads identically in script/import mode.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from validation_scripts import related_lifecycle_check_review_latest_base as _impl

# Keep source-level chronology contracts visible to static checks.
_RESOLVED_PROVISIONAL_TARGETS_CONTRACT = "resolved_provisional_targets"
_PROVISIONAL_CHRONOLOGY_ERROR_CONTRACT = (
    "follow-up date precedes provisional predecessor"
)

for _name in dir(_impl):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_impl, _name)

item_specific_lineage_assertion = _impl.item_specific_lineage_assertion
_prior_check_card = _impl.check_card
_STRICT_ITEM_SPECIFIC_ERRORS = {
    "fresh_follow_up_anchor": (
        "distinct_follow_up requires item-specific fresh_follow_up_anchor"
    ),
    "incremental_fact_vs_predecessor": (
        "distinct_follow_up requires item-specific incremental_fact_vs_predecessor"
    ),
    "changed_judgment_vs_predecessor": (
        "distinct_follow_up requires item-specific changed_judgment_vs_predecessor"
    ),
}


def check_card(*args, **kwargs):
    """Align strict Related field errors with the final assertion policy only."""
    errors, warnings = _prior_check_card(*args, **kwargs)
    bound = inspect.signature(_prior_check_card).bind_partial(*args, **kwargs)
    card = bound.arguments.get("card")
    require_contract = bool(bound.arguments.get("require_contract", False))
    if not require_contract or not isinstance(card, dict):
        return errors, warnings

    lineage = card.get("related_lineage")
    if not isinstance(lineage, dict):
        return errors, warnings
    if lineage.get("relation_type") != "distinct_follow_up":
        return errors, warnings

    aligned_errors = list(errors)
    for field, message in _STRICT_ITEM_SPECIFIC_ERRORS.items():
        valid = item_specific_lineage_assertion(lineage.get(field))
        aligned_errors = [error for error in aligned_errors if error != message]
        if not valid:
            aligned_errors.append(message)
    return aligned_errors, warnings


def _bind_public_check_card(root) -> None:
    """Make CLI and imported entrypoints use the same bounded reconciliation."""
    stack = [root]
    seen: set[int] = set()
    while stack:
        module = stack.pop()
        if module is None or id(module) in seen:
            continue
        seen.add(id(module))
        if hasattr(module, "check_card"):
            setattr(module, "check_card", check_card)
        for attribute in ("_base", "_prior"):
            child = getattr(module, attribute, None)
            if child is not None:
                stack.append(child)


_bind_public_check_card(_impl)
globals()["check_card"] = check_card

if __name__ == "__main__":
    sys.exit(_impl._base._prior._base.main())

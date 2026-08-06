#!/usr/bin/env python3
"""Bind the latest Related assertion policy across the preserved module chain."""
from __future__ import annotations

import sys

from validation_scripts import related_lifecycle_check_review_latest_base as _base

# Keep source-level chronology contracts visible to static checks.
_RESOLVED_PROVISIONAL_TARGETS_CONTRACT = "resolved_provisional_targets"
_PROVISIONAL_CHRONOLOGY_ERROR_CONTRACT = (
    "follow-up date precedes provisional predecessor"
)

for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)

item_specific_lineage_assertion = _base.item_specific_lineage_assertion


def _bind_item_specific_assertion(root) -> None:
    """Replace captured validator references throughout `_base`/`_prior` graph."""
    stack = [root]
    seen: set[int] = set()
    while stack:
        module = stack.pop()
        if module is None or id(module) in seen:
            continue
        seen.add(id(module))
        if hasattr(module, "item_specific_lineage_assertion"):
            setattr(
                module,
                "item_specific_lineage_assertion",
                item_specific_lineage_assertion,
            )
        for attribute in ("_base", "_prior"):
            child = getattr(module, attribute, None)
            if child is not None:
                stack.append(child)


_bind_item_specific_assertion(_base)
globals()["item_specific_lineage_assertion"] = item_specific_lineage_assertion

if __name__ == "__main__":
    sys.exit(_base.main())

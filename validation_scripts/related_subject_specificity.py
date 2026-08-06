#!/usr/bin/env python3
"""Stable Related subject-specificity policy seam.

The public Related validator imports this module instead of a review-ID module.
The legacy implementation remains behind this boundary until its historical
layers are collapsed in later, independently reviewable cleanup PRs.
"""
from __future__ import annotations

from validation_scripts.callable_seam import (
    clone_function_with_globals as _clone_function_with_globals,
)
from validation_scripts import related_lifecycle_check_review_latest_base as _legacy_impl

for _name, _value in vars(_legacy_impl).items():
    if not _name.startswith("__") and _name not in {
        "_base",
        "_prior",
        "_impl",
        "_legacy_impl",
    }:
        globals()[_name] = _value

item_specific_lineage_assertion = (
    _legacy_impl.item_specific_lineage_assertion
)
check_card = _clone_function_with_globals(
    _legacy_impl.check_card,
    {"item_specific_lineage_assertion": item_specific_lineage_assertion},
    module_name=__name__,
)
main = _clone_function_with_globals(
    _legacy_impl.main,
    {"check_card": check_card},
    module_name=__name__,
)

if __name__ == "__main__":
    raise SystemExit(main())

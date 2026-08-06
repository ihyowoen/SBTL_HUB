#!/usr/bin/env python3
"""Stable Related subject-specificity policy seam.

The public Related validator imports this module instead of a review-ID module.
The legacy implementation remains behind this boundary until its historical
layers are collapsed in later, independently reviewable cleanup PRs.
"""
from __future__ import annotations

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
check_card = _legacy_impl.check_card
main = _legacy_impl.main

# Keep the exported callable graph internally consistent for consumers that
# import this stable policy seam directly.
check_card.__globals__["item_specific_lineage_assertion"] = (
    item_specific_lineage_assertion
)
main.__globals__["check_card"] = check_card

if __name__ == "__main__":
    raise SystemExit(main())

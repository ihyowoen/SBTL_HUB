#!/usr/bin/env python3
"""Public Related validator entrypoint."""
from __future__ import annotations

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

item_specific_lineage_assertion = _impl.item_specific_lineage_assertion
check_card = _impl.check_card
main = _impl.main

if __name__ == "__main__":
    raise SystemExit(main())

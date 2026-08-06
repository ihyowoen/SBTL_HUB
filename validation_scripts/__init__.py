"""Package bootstrap for validation scripts.

Several long-lived validators retain direct sibling imports so they can also run
as standalone scripts. Register the package copy of the shared audit helpers
under that historical top-level name, allowing a validator to be imported as
the first ``validation_scripts`` submodule without mutating ``sys.path``.
"""
from __future__ import annotations

import sys as _sys

from . import card_audit_utils as _card_audit_utils

_sys.modules.setdefault("card_audit_utils", _card_audit_utils)

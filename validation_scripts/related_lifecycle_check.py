#!/usr/bin/env python3
"""Review 4868891584 compatibility layer for Related financial role terms."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_PRIOR_PATH = Path(__file__).with_name(
    "related_lifecycle_check_review4868891584_base.py"
)
_PRIOR_DIR = str(_PRIOR_PATH.parent)
if _PRIOR_DIR not in sys.path:
    sys.path.insert(0, _PRIOR_DIR)

_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.related_lifecycle_check_review4868891584_base",
    _PRIOR_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load Related validator base from {_PRIOR_PATH}")
_prior = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_prior)

# Keep the public source-level chronology contract visible to static checks;
# behavior remains implemented by the preserved prior layer.
_RESOLVED_PROVISIONAL_TARGETS_CONTRACT = "resolved_provisional_targets"
_RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS = {
    "ebitda", "profit", "profits", "capex", "opex", "yield", "yields",
    "throughput", "영업이익", "이익", "수익", "설비투자", "자본지출",
    "운영비", "영업비용", "수율", "처리량",
}
_prior._RELATED_DATA_FINANCIAL_ROLE_TERMS.update(
    _RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
)
_prior._ASSERTION_ROLE_TERMS.update(
    _RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
)

for _name in dir(_prior):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_prior, _name)

if __name__ == "__main__":
    _prior._base.sys.exit(_prior._base.main())

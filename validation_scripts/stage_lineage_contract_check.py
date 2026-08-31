#!/usr/bin/env python3
"""Authoritative Stage A V4 gate with frozen V3 machine compatibility behind it.

Current Stage A validation is fail-closed on the embedded V4 news-value contract.
The pre-V4 route/full-artifact validator chain is retained in
``stage_lineage_contract_check_v3_compat`` and still runs after V4 validation so
historical lineage, source-diversity, temporal and full-artifact protections are
not weakened. Historical tests/tools that intentionally exercise the old
contract must call ``check_stage_a_v3_compat`` explicitly; the active public
``check_stage_a`` entrypoint cannot be used to bypass V4 metadata.
"""
from __future__ import annotations

import sys
from pathlib import Path

_VALIDATION_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _VALIDATION_DIR.parent
for _import_path in (_ROOT_DIR, _VALIDATION_DIR):
    _text = str(_import_path)
    if _text not in sys.path:
        sys.path.insert(0, _text)

from validation_scripts import stage_lineage_contract_check_v3_compat as _compat  # noqa: E402
from validation_scripts.stage_a_v4_contract import (  # noqa: E402
    POLICY_VERSION as STAGE_A_V4_SELECTION_POLICY_VERSION,
    validate_stage_a_v4_payload,
    validate_stage_a_v4_spec,
)

# Preserve the historical public constants/helpers for downstream imports, then
# override only the active Stage A entrypoints below.
for _name in dir(_compat):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_compat, _name)

_prior_validate_stage_a_spec = _compat.validate_stage_a_spec
_prior_check_stage_a = _compat.check_stage_a
_prior_check_stage_a_full = _compat.check_stage_a_full


def validate_stage_a_spec(spec, index, messages):
    """Active per-spec validator: V4 first, then frozen V3 compatibility."""
    validate_stage_a_v4_spec(spec, index, messages, require_contract=True)
    return _prior_validate_stage_a_spec(spec, index, messages)


def _v4_gate(data):
    messages = validate_stage_a_v4_payload(data, require_contract=True)
    if messages:
        return _compat._compat_module.fail(messages)
    return None


def check_stage_a(data):
    """Active Stage A API. V4 metadata is mandatory for every strict item."""
    blocked = _v4_gate(data)
    if blocked is not None:
        return blocked
    return _prior_check_stage_a(data)


def check_stage_a_full(data):
    """Active full-artifact API. V4 plus historical full completeness are mandatory."""
    blocked = _v4_gate(data)
    if blocked is not None:
        return blocked
    return _prior_check_stage_a_full(data)


def check_stage_a_v3_compat(data):
    """Explicit historical compatibility API; never use as the active Stage A gate."""
    return _prior_check_stage_a(data)


def check_stage_a_full_v3_compat(data):
    """Explicit historical full-artifact compatibility API."""
    return _prior_check_stage_a_full(data)


if __name__ == "__main__":
    # The CLI is an active governance entrypoint and therefore always uses V4.
    # Patch only the nested dispatch target used by the historical CLI parser.
    if hasattr(_compat, "_patch_module_chain") and hasattr(_compat, "_compat_module"):
        _compat._patch_module_chain(_compat._compat_module, "check_stage_a", check_stage_a)
    _compat._compat_module._base_layer._base.sys.exit(
        _compat._compat_module._base_layer._base.main()
    )

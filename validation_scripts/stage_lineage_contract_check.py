#!/usr/bin/env python3
"""Authoritative Stage A V4 gate with frozen V3 machine compatibility behind it.

Current Stage A validation is fail-closed on the embedded V4 news-value contract.
The pre-V4 route/full-artifact validator chain is retained in
``stage_lineage_contract_check_v3_compat`` and still runs after V4 validation so
historical lineage, source-diversity, temporal and full-artifact protections are
not weakened. Historical tests/tools that intentionally exercise the old
contract must call ``check_stage_a_v3_compat`` explicitly; the active public
``check_stage_a`` entrypoint cannot be used to bypass V4 metadata.

The frozen V3 full-artifact checker contains historical document-presence
requirements. Those requirements are compatibility shape only: active authority
is derived from the lifecycle registry, and superseded/reference documents may
never be required or claimed as active Stage A authority. A private projection
is used only when invoking the frozen V3 checker; it is never emitted or
returned as a Stage A artifact.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Mapping

_VALIDATION_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _VALIDATION_DIR.parent
for _import_path in (_ROOT_DIR, _VALIDATION_DIR):
    _text = str(_import_path)
    if _text not in sys.path:
        sys.path.insert(0, _text)

from validation_scripts import stage_lineage_contract_check_v3_compat as _compat  # noqa: E402
from validation_scripts.stage_a_full_v3_completeness_review4943656188_final import (  # noqa: E402
    MANDATORY_STAGE_A_DOCS as _V3_MANDATORY_STAGE_A_DOCS,
)
from validation_scripts.stage_a_v4_contract import (  # noqa: E402
    POLICY_VERSION as STAGE_A_V4_SELECTION_POLICY_VERSION,
    validate_stage_a_v4_payload,
    validate_stage_a_v4_spec,
)
from validation_scripts.stage_a_v4_hardening import (  # noqa: E402
    validate_stage_a_v4_hardening,
    validate_stage_a_v4_hardening_payload,
)

# Preserve the historical public constants/helpers for downstream imports, then
# override only the active Stage A entrypoints below.
for _name in dir(_compat):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_compat, _name)

_prior_validate_stage_a_spec = _compat.validate_stage_a_spec
_prior_check_stage_a = _compat.check_stage_a
_prior_check_stage_a_full = _compat.check_stage_a_full

_REGISTRY_PATH = _ROOT_DIR / "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json"
_ACTIVE_LIFECYCLE_KEYS = (
    "active_canonical",
    "active_named_prompts",
    "active_validator_contracts",
    "open_remediations",
    "activation_required_migrations",
)
_NONOPERATIVE_LIFECYCLE_KEYS = (
    "superseded",
    "reference_only",
    "completed_reference",
    "archived",
)
_REQUIRED_DOC_ARRAY_FIELDS = (
    "docs_expected",
    "docs_read_from_github_main",
)


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load_registry_authority() -> tuple[set[str], set[str], tuple[str, ...], list[str]]:
    """Return active/non-operative authority and the active V3-compat doc subset."""
    messages: list[str] = []
    try:
        registry = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - normalized fail-closed path
        return set(), set(), (), [f"Stage A lifecycle registry cannot be loaded: {exc}"]
    if not isinstance(registry, Mapping):
        return set(), set(), (), ["Stage A lifecycle registry must be an object"]

    active: set[str] = set()
    nonoperative: set[str] = set()
    for key in _ACTIVE_LIFECYCLE_KEYS:
        values = registry.get(key, [])
        if not isinstance(values, list) or any(not _nonempty_text(value) for value in values):
            messages.append(f"Stage A lifecycle registry {key} must be an array of non-empty paths")
            continue
        if len(values) != len(set(values)):
            messages.append(f"Stage A lifecycle registry {key} contains duplicate paths")
        active.update(values)
    for key in _NONOPERATIVE_LIFECYCLE_KEYS:
        values = registry.get(key, [])
        if not isinstance(values, list) or any(not _nonempty_text(value) for value in values):
            messages.append(f"Stage A lifecycle registry {key} must be an array of non-empty paths")
            continue
        if len(values) != len(set(values)):
            messages.append(f"Stage A lifecycle registry {key} contains duplicate paths")
        nonoperative.update(values)

    overlap = sorted(active & nonoperative)
    if overlap:
        messages.append(
            "Stage A lifecycle registry classifies paths as both active and non-operative: "
            + ", ".join(overlap)
        )

    # The historical validator's dependency list is preserved as a compatibility
    # candidate set. Current mandatory authority is its intersection with the
    # active lifecycle registry; retired V3 policy/addendum files therefore
    # disappear automatically without weakening the remaining safeguards.
    unclassified_legacy = sorted(
        path for path in _V3_MANDATORY_STAGE_A_DOCS if path not in active and path not in nonoperative
    )
    if unclassified_legacy:
        messages.append(
            "Stage A historical dependency paths are unclassified by the lifecycle registry: "
            + ", ".join(unclassified_legacy)
        )
    active_required = tuple(path for path in _V3_MANDATORY_STAGE_A_DOCS if path in active)
    if not active_required:
        messages.append("Stage A active required-doc closure is empty")
    return active, nonoperative, active_required, messages


def _validate_active_required_docs(data: Mapping[str, Any]) -> list[str]:
    """Validate the persisted V4 required-doc claim against current authority."""
    active, nonoperative, mandatory, messages = _load_registry_authority()
    docs = data.get("required_docs_check")
    if not isinstance(docs, Mapping):
        messages.append("full Stage A artifact required_docs_check must be an object")
        return messages
    if docs.get("status") != "PASS":
        messages.append("full Stage A artifact required_docs_check.status must be PASS")

    for field in _REQUIRED_DOC_ARRAY_FIELDS:
        values = docs.get(field)
        if not isinstance(values, list):
            messages.append(f"full Stage A artifact required_docs_check.{field} must be an array")
            continue
        if any(not _nonempty_text(value) for value in values) or len(values) != len(set(values)):
            messages.append(
                f"full Stage A artifact required_docs_check.{field} must contain unique non-empty paths"
            )
            continue
        value_set = set(values)
        absent = sorted(set(mandatory) - value_set)
        if absent:
            messages.append(
                f"full Stage A artifact required_docs_check.{field} missing active mandatory documents: "
                + ", ".join(absent)
            )
        retired = sorted(value_set & nonoperative)
        if retired:
            messages.append(
                f"full Stage A artifact required_docs_check.{field} cannot claim superseded/reference authority: "
                + ", ".join(retired)
            )
        unknown = sorted(value_set - active - nonoperative)
        if unknown:
            messages.append(
                f"full Stage A artifact required_docs_check.{field} contains unregistered authority paths: "
                + ", ".join(unknown)
            )

    missing = docs.get("docs_missing_or_unreadable")
    if not isinstance(missing, list):
        messages.append(
            "full Stage A artifact required_docs_check.docs_missing_or_unreadable must be an array"
        )
    elif missing:
        messages.append(
            "full Stage A artifact required_docs_check.docs_missing_or_unreadable must be empty"
        )
    return messages


def _project_full_stage_a_for_v3_compat(data: Mapping[str, Any]) -> dict[str, Any]:
    """Supply frozen V3 doc-presence aliases in a private, non-emitted copy only."""
    projected = copy.deepcopy(dict(data))
    docs = projected.get("required_docs_check")
    if not isinstance(docs, dict):
        return projected
    for field in _REQUIRED_DOC_ARRAY_FIELDS:
        values = docs.get(field)
        if not isinstance(values, list):
            continue
        projected_values = list(values)
        for path in _V3_MANDATORY_STAGE_A_DOCS:
            if path not in projected_values:
                projected_values.append(path)
        docs[field] = projected_values
    return projected


def _prepare_v3_compat_payload(data: Mapping[str, Any], *, require_full: bool) -> tuple[Any, int | None]:
    """Enforce V4 authority first, then return a private V3 compatibility projection."""
    is_full = require_full or _compat.looks_like_full_stage_a_artifact(data)
    if not is_full:
        return data, None
    messages = _validate_active_required_docs(data)
    if messages:
        return data, _compat._compat_module.fail(messages)
    return _project_full_stage_a_for_v3_compat(data), None


def validate_stage_a_spec(spec, index, messages):
    """Active per-spec validator: V4 + hardening first, then frozen V3 compatibility."""
    validate_stage_a_v4_spec(spec, index, messages, require_contract=True)
    validate_stage_a_v4_hardening(spec, index, messages, require_contract=True)
    return _prior_validate_stage_a_spec(spec, index, messages)


def _v4_gate(data):
    messages = validate_stage_a_v4_payload(data, require_contract=True)
    messages.extend(validate_stage_a_v4_hardening_payload(data, require_contract=True))
    if messages:
        return _compat._compat_module.fail(messages)
    return None


def check_stage_a(data):
    """Active Stage A API. V4 metadata and current authority are mandatory."""
    blocked = _v4_gate(data)
    if blocked is not None:
        return blocked
    compat_payload, blocked = _prepare_v3_compat_payload(data, require_full=False)
    if blocked is not None:
        return blocked
    return _prior_check_stage_a(compat_payload)


def check_stage_a_full(data):
    """Active full-artifact API. V4 authority plus historical shape safeguards are mandatory."""
    blocked = _v4_gate(data)
    if blocked is not None:
        return blocked
    compat_payload, blocked = _prepare_v3_compat_payload(data, require_full=True)
    if blocked is not None:
        return blocked
    return _prior_check_stage_a_full(compat_payload)


def check_stage_a_v3_compat(data):
    """Explicit historical compatibility API; never use as the active Stage A gate."""
    return _prior_check_stage_a(data)


def check_stage_a_full_v3_compat(data):
    """Explicit historical full-artifact compatibility API."""
    return _prior_check_stage_a_full(data)


def _install_active_cli_gate() -> None:
    """Install the V4 Stage A gate into the historical CLI dispatcher or fail closed."""
    patcher = getattr(_compat, "_patch_module_chain", None)
    compat_module = getattr(_compat, "_compat_module", None)
    if not callable(patcher) or compat_module is None:
        raise RuntimeError(
            "Stage A V4 CLI cannot install the compatibility dispatch hook; refusing V3-only fallback"
        )
    patcher(compat_module, "check_stage_a", check_stage_a)


if __name__ == "__main__":
    # The CLI is an active governance entrypoint and therefore always uses V4.
    # Private compatibility-hook drift must stop the gate instead of silently
    # falling back to the historical V3-only dispatcher.
    _install_active_cli_gate()
    _compat._compat_module._base_layer._base.sys.exit(
        _compat._compat_module._base_layer._base.main()
    )

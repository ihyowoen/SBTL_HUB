#!/usr/bin/env python3
"""Stage A V3 route and full-artifact contract alignment layer.

The historical validator chain remains authoritative for unchanged lineage,
source-diversity, review-pool, and downstream checks.  This layer aligns it with
canonical Structural News Value V3 and delegates real-artifact completeness to
``stage_a_full_v3_completeness_review4943777463``.
"""
from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType

_VALIDATION_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _VALIDATION_DIR.parent
for _import_path in (_ROOT_DIR, _VALIDATION_DIR):
    _import_path_text = str(_import_path)
    if _import_path_text not in sys.path:
        sys.path.insert(0, _import_path_text)

from validation_scripts.stage_a_full_v3_completeness_review4943777463 import (  # noqa: E402
    CANONICAL_POLICY_VERSION,
    looks_like_full_stage_a_artifact,
    prevalidate_full_stage_a_artifact,
    validate_full_stage_a_artifact,
)
from validation_scripts.v3_stage_contracts import (  # noqa: E402
    stage_a_validator_constants,
)

_PRIOR_PATH = Path(__file__).with_name(
    "stage_lineage_contract_check_review4869324626_base.py"
)
_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.stage_lineage_contract_check_review4869324626_base",
    _PRIOR_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load validator base from {_PRIOR_PATH}")
_compat_module = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_compat_module)

for _name in dir(_compat_module):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_compat_module, _name)

_re = _compat_module._base_layer._base.re
_prior_is_temporal_noun_modifier = _compat_module._is_temporal_noun_modifier
_TEMPORAL_AUXILIARY_PATTERN = (
    r"(?:would|will|can|could|may|might|must|shall|should|is|are|was|were|"
    r"has|have|had)"
)
_SINCE_PERIOD_MODIFIER_HEAD_PATTERN = (
    r"(?:"
    r"(?:19|20)\d{2}|q[1-4]|[1-4]q|fy\d{2,4}|h[12]|[12]h|"
    r"last\s+(?:year|quarter|month)"
    r")"
)
_WHEN_REDUCED_STATUS_PATTERN = (
    r"(?:fully\s+|substantially\s+|formally\s+)?"
    r"(?:complete|completed|available|published|filed|finalized|finalised|"
    r"approved|ready|effective|released|disclosed)"
)

_CANONICAL_STRUCTURAL_SELECTOR_POLICY_VERSION = CANONICAL_POLICY_VERSION
_EXECUTION_ROUTE_SHARED_V3_FIELDS = (
    "anchor_classes",
    "incremental_information",
    "decision_relevance",
    "baseline_expectation_changed",
    "evidence_needed_for_stage_b",
    "next_confirmation_points",
    "prior_state",
    "new_verified_fact",
    "changed_judgment",
    "uncertainty_resolved",
    "remaining_uncertainty",
)
_EXECUTION_ROUTE_OVERRIDE_ONLY_FIELDS = (
    "structural_value_override_reason",
    "why_execution_event_not_required",
)
_EXECUTION_ROUTE_SHARED_NARRATIVE_FIELDS = (
    "incremental_information",
    "decision_relevance",
    "baseline_expectation_changed",
    "prior_state",
    "new_verified_fact",
    "changed_judgment",
    "uncertainty_resolved",
    "remaining_uncertainty",
)

# Public constants locked by v3_contract_drift_check.py.
STAGE_A_SHARED_STRICT_REQUIRED = _EXECUTION_ROUTE_SHARED_V3_FIELDS
STAGE_A_OVERRIDE_ONLY_REQUIRED = _EXECUTION_ROUTE_OVERRIDE_ONLY_FIELDS


def _is_temporal_noun_modifier(text, marker):
    """Preserve narrow period/reduced modifiers without retaining real clauses."""
    if _prior_is_temporal_noun_modifier(text, marker):
        return True
    marker_text = marker.group(0).lower()
    remainder = text[marker.end():]
    if marker_text == "since":
        # Only explicit period heads are safe noun modifiers. Event nouns followed
        # by finite auxiliaries or modals (for example "since publication would
        # strengthen ...") are dependent clauses and must not supply the effect.
        return bool(
            _re.match(
                rf"\s+(?:the\s+)?{_SINCE_PERIOD_MODIFIER_HEAD_PATTERN}"
                rf"(?:\s+(?:q[1-4]|[1-4]q|h[12]|[12]h))?"
                rf"\s*,?\s+{_TEMPORAL_AUXILIARY_PATTERN}\b",
                remainder,
            )
        )
    if marker_text == "when":
        return bool(
            _re.match(
                rf"\s+{_WHEN_REDUCED_STATUS_PATTERN}"
                rf"\s*,?\s+{_TEMPORAL_AUXILIARY_PATTERN}\b",
                remainder,
            )
        )
    return False


_compat_module._is_temporal_noun_modifier = _is_temporal_noun_modifier
_prior_validate_stage_a_spec = _compat_module.validate_stage_a_spec
_prior_check_stage_a = _compat_module.check_stage_a


def _normalized_format_risk_tags(spec):
    """Return normalized tags only when the original array is itself valid."""
    tags = spec.get("format_risk_tags") if isinstance(spec, dict) else None
    if not isinstance(tags, list):
        return None
    normalized = []
    for value in tags:
        if not isinstance(value, str) or not value.strip():
            return None
        normalized.append(value.strip().lower())
    return normalized


def _canonical_empty_route_value(value):
    return value is None or value == "" or value == [] or value == {}


def _ordinary_override_candidate(spec):
    if not isinstance(spec, dict):
        return False
    normalized_tags = _normalized_format_risk_tags(spec)
    if normalized_tags not in ([], ["none"]):
        return False
    return spec.get("structural_value_override_applied") is True


def _execution_identity_present(spec):
    if not isinstance(spec, dict):
        return False
    return not _canonical_empty_route_value(spec.get("execution_anchor_type")) or not _canonical_empty_route_value(
        spec.get("execution_anchor_strength")
    )


def _execution_route_candidate(spec):
    if not isinstance(spec, dict):
        return False
    execution_type = spec.get("execution_anchor_type")
    execution_strength = spec.get("execution_anchor_strength")
    return (
        isinstance(execution_type, str)
        and bool(execution_type.strip())
        and isinstance(execution_strength, str)
        and execution_strength in _compat_module.STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH
        and spec.get("structural_value_override_applied") is False
    )


def _validate_anchor_classes_unique(spec, spec_id, messages, *, execution):
    classes = spec.get("anchor_classes")
    if not isinstance(classes, list) or not classes:
        messages.append(f"{spec_id}: anchor_classes must be a non-empty array")
        return
    if any(not isinstance(value, str) or not value for value in classes):
        messages.append(f"{spec_id}: anchor_classes must contain non-empty strings")
        return
    if len(set(classes)) != len(classes):
        messages.append(f"{spec_id}: anchor_classes must be unique")
    allowed = set(_compat_module.STAGE_A_NON_EXECUTION_ANCHOR_CLASSES)
    if execution:
        allowed.add("execution_event_anchor")
        if "execution_event_anchor" not in classes:
            messages.append(
                f"{spec_id}: execution route anchor_classes must include execution_event_anchor"
            )
    invalid = [value for value in classes if value not in allowed]
    if invalid:
        messages.append(f"{spec_id}: invalid anchor_classes={invalid}")


def _validate_execution_shared_v3_metadata(spec, spec_id, messages):
    for field in _EXECUTION_ROUTE_SHARED_V3_FIELDS:
        if _compat_module.missing_nonempty(spec, field):
            messages.append(f"{spec_id}: execution route missing shared V3 field {field}")

    _validate_anchor_classes_unique(spec, spec_id, messages, execution=True)

    for field in _EXECUTION_ROUTE_SHARED_NARRATIVE_FIELDS:
        if not _compat_module._item_specific_narrative(spec.get(field)):
            messages.append(
                f"{spec_id}: execution route {field} must be item-specific narrative text"
            )

    evidence_targets = spec.get("evidence_needed_for_stage_b")
    if (
        not isinstance(evidence_targets, list)
        or not evidence_targets
        or any(not _compat_module._valid_evidence_target(value) for value in evidence_targets)
    ):
        messages.append(
            f"{spec_id}: execution route evidence_needed_for_stage_b entries must identify both "
            "a source/document class and an exact claim, metric, stage, or date"
        )

    confirmation_points = spec.get("next_confirmation_points")
    if (
        not isinstance(confirmation_points, list)
        or not confirmation_points
        or any(not _compat_module._valid_confirmation_point(value) for value in confirmation_points)
    ):
        messages.append(
            f"{spec_id}: execution route next_confirmation_points entries must identify measurable "
            "events or metrics and an interpretation effect"
        )


def _execution_route_validation_view(spec):
    """Hide shared fields only from the obsolete legacy residual-field detector."""
    routed_spec = dict(spec)
    for field in _EXECUTION_ROUTE_SHARED_V3_FIELDS:
        value = routed_spec.get(field)
        routed_spec[field] = [] if isinstance(value, list) else None
    return routed_spec


def _validate_ordinary_override_identity(spec, spec_id, messages):
    """Enforce canonical empty execution identity and unique anchor classes."""
    for field in ("execution_anchor_type", "execution_anchor_strength"):
        value = spec.get(field)
        if not _canonical_empty_route_value(value):
            messages.append(
                f"{spec_id}: v3_non_execution route requires canonical empty {field}"
            )
    _validate_anchor_classes_unique(spec, spec_id, messages, execution=False)


def _append_v3_lineage_errors(spec, spec_id, messages):
    if spec.get("structural_value_override_applied") is True:
        if spec.get("structural_selector_policy_version") != _CANONICAL_STRUCTURAL_SELECTOR_POLICY_VERSION:
            messages.append(
                f"{spec_id}: structural_selector_policy_version must be "
                f"{_CANONICAL_STRUCTURAL_SELECTOR_POLICY_VERSION} for v3_non_execution"
            )


def validate_stage_a_spec(spec, index, messages):
    """Align strict-route validation with canonical Structural News Value V3."""
    if not isinstance(spec, dict):
        return _prior_validate_stage_a_spec(spec, index, messages)

    spec_id = spec.get("spec_id", f"idx_{index}")
    _append_v3_lineage_errors(spec, spec_id, messages)

    # Any execution-shaped item must carry an explicit boolean route marker.
    if _execution_identity_present(spec) and spec.get("structural_value_override_applied") is not False:
        messages.append(
            f"{spec_id}: execution-shaped strict item requires structural_value_override_applied=false"
        )

    if _execution_route_candidate(spec):
        _validate_execution_shared_v3_metadata(spec, spec_id, messages)
        for field in _EXECUTION_ROUTE_OVERRIDE_ONLY_FIELDS:
            if spec.get(field) not in (None, "", [], {}):
                messages.append(
                    f"{spec_id}: execution route must leave override-only field {field} empty"
                )
        return _prior_validate_stage_a_spec(
            _execution_route_validation_view(spec), index, messages
        )

    if not _ordinary_override_candidate(spec):
        return _prior_validate_stage_a_spec(spec, index, messages)

    # Do not sanitize malformed risk tags: the candidate predicate returns false
    # for malformed arrays, so the legacy validator receives the original value.
    _validate_ordinary_override_identity(spec, spec_id, messages)
    routed_spec = dict(spec)
    routed_spec["format_risk_tags"] = ["ordinary_v3_route_contract"]
    message_start = len(messages)
    _prior_validate_stage_a_spec(routed_spec, index, messages)
    for message_index in range(message_start, len(messages)):
        messages[message_index] = messages[message_index].replace(
            "format-risk strict_passed_spec", "strict_passed_spec"
        ).replace(
            "for format-risk strict_passed_spec", "for strict_passed_spec"
        )


def check_stage_a(data):
    """Preflight malformed containers, run legacy checks, then full completeness."""
    preflight_messages = prevalidate_full_stage_a_artifact(data)
    if preflight_messages:
        return _compat_module.fail(preflight_messages)

    stream = io.StringIO()
    with redirect_stdout(stream):
        result = _prior_check_stage_a(data)
    legacy_output = stream.getvalue()
    if result != 0:
        print(legacy_output, end="")
        return result

    if not looks_like_full_stage_a_artifact(data):
        print(legacy_output, end="")
        return result

    messages = validate_full_stage_a_artifact(data, _compat_module)
    if messages:
        return _compat_module.fail(messages)
    print("RESULT: PASS_STAGE_A_SCHEMA_CONTRACT")
    return 0


def _patch_module_chain(root, name, value):
    seen = set()
    stack = [root]
    while stack:
        module = stack.pop()
        if not isinstance(module, ModuleType) or id(module) in seen:
            continue
        seen.add(id(module))
        if hasattr(module, name):
            setattr(module, name, value)
        for child_name in ("_prior", "_base_layer", "_semantic", "_base"):
            child = getattr(module, child_name, None)
            if isinstance(child, ModuleType):
                stack.append(child)


for _constant_name, _constant_value in stage_a_validator_constants().items():
    _patch_module_chain(_compat_module, _constant_name, _constant_value)
    globals()[_constant_name] = _constant_value

_patch_module_chain(_compat_module, "validate_stage_a_spec", validate_stage_a_spec)
_patch_module_chain(_compat_module, "check_stage_a", check_stage_a)

if __name__ == "__main__":
    _compat_module._base_layer._base.sys.exit(
        _compat_module._base_layer._base.main()
    )

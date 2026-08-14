#!/usr/bin/env python3
"""Stage A V3 route-alignment compatibility layer.

Keeps the existing validator chain, but aligns the Stage A strict-route consumer
with the canonical V3 policy hierarchy:

- ordinary strict items may use a complete V3 non-execution route;
- V3 non-execution routes must carry structural selector lineage;
- execution routes must retain and validate shared V3 before/after,
  evidence-target, confirmation-point, and changed-judgment metadata;
- truly override-only execution fields must remain empty.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

_VALIDATION_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _VALIDATION_DIR.parent
for _import_path in (_ROOT_DIR, _VALIDATION_DIR):
    _import_path_text = str(_import_path)
    if _import_path_text not in sys.path:
        sys.path.insert(0, _import_path_text)

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
_SINCE_MODIFIER_HEAD_PATTERN = (
    r"(?:"
    r"(?:19|20)\d{2}|q[1-4]|[1-4]q|fy\d{2,4}|h[12]|[12]h|"
    r"last\s+(?:year|quarter|month)|"
    r"publication|filing|launch|approval|completion|release|disclosure"
    r")"
)
_WHEN_REDUCED_STATUS_PATTERN = (
    r"(?:fully\s+|substantially\s+|formally\s+)?"
    r"(?:complete|completed|available|published|filed|finalized|finalised|"
    r"approved|ready|effective|released|disclosed)"
)

_CANONICAL_STRUCTURAL_SELECTOR_POLICY_VERSION = "STRUCTURAL_NEWS_VALUE_SELECTION_V3"
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

# Exported drift-check constants: these must stay aligned with the canonical
# machine-readable V3 contract, not with any individual run artifact.
STAGE_A_SHARED_STRICT_REQUIRED = _EXECUTION_ROUTE_SHARED_V3_FIELDS
STAGE_A_OVERRIDE_ONLY_REQUIRED = _EXECUTION_ROUTE_OVERRIDE_ONLY_FIELDS


def _is_temporal_noun_modifier(text, marker):
    """Preserve narrow since/when noun modifiers without retaining real clauses."""
    if _prior_is_temporal_noun_modifier(text, marker):
        return True

    marker_text = marker.group(0).lower()
    remainder = text[marker.end():]
    if marker_text == "since":
        return bool(
            _re.match(
                rf"\s+(?:the\s+)?{_SINCE_MODIFIER_HEAD_PATTERN}"
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


def _normalized_format_risk_tags(spec):
    tags = spec.get("format_risk_tags") if isinstance(spec, dict) else None
    if not isinstance(tags, list):
        return None
    return [
        value.strip().lower()
        for value in tags
        if isinstance(value, str) and value.strip()
    ]


def _ordinary_override_candidate(spec):
    """Identify a non-format-risk candidate that intentionally uses V3 override."""
    if not isinstance(spec, dict):
        return False
    normalized_tags = _normalized_format_risk_tags(spec)
    if normalized_tags not in ([], ["none"]):
        return False
    return spec.get("structural_value_override_applied") is True


def _execution_route_candidate(spec):
    """Identify a complete execution identity before legacy residual-field checks."""
    if not isinstance(spec, dict):
        return False
    execution_type = spec.get("execution_anchor_type")
    execution_strength = spec.get("execution_anchor_strength")
    return (
        isinstance(execution_type, str)
        and bool(execution_type.strip())
        and execution_strength in _compat_module.STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH
        and spec.get("structural_value_override_applied") is False
    )


def _validate_execution_shared_v3_metadata(spec, spec_id, messages):
    """Enforce the route-neutral V3 metadata required on execution strict items."""
    for field in _EXECUTION_ROUTE_SHARED_V3_FIELDS:
        if _compat_module.missing_nonempty(spec, field):
            messages.append(f"{spec_id}: execution route missing shared V3 field {field}")

    classes = spec.get("anchor_classes")
    allowed_classes = {
        "execution_event_anchor",
        *_compat_module.STAGE_A_NON_EXECUTION_ANCHOR_CLASSES,
    }
    if not isinstance(classes, list) or not classes:
        messages.append(
            f"{spec_id}: execution route anchor_classes must be a non-empty array"
        )
    else:
        invalid_classes = [
            value
            for value in classes
            if not isinstance(value, str) or value not in allowed_classes
        ]
        if invalid_classes:
            messages.append(
                f"{spec_id}: execution route invalid anchor_classes={invalid_classes}"
            )
        if "execution_event_anchor" not in classes:
            messages.append(
                f"{spec_id}: execution route anchor_classes must include execution_event_anchor"
            )
        if len(set(value for value in classes if isinstance(value, str))) != len(classes):
            messages.append(
                f"{spec_id}: execution route anchor_classes must be unique"
            )

    for field in _EXECUTION_ROUTE_SHARED_NARRATIVE_FIELDS:
        if not _compat_module._item_specific_narrative(spec.get(field)):
            messages.append(
                f"{spec_id}: execution route {field} must be item-specific narrative text"
            )

    evidence_targets = spec.get("evidence_needed_for_stage_b")
    if (
        not isinstance(evidence_targets, list)
        or not evidence_targets
        or any(
            not _compat_module._valid_evidence_target(value)
            for value in evidence_targets
        )
    ):
        messages.append(
            f"{spec_id}: execution route evidence_needed_for_stage_b entries must identify both "
            "a source/document class and an exact claim, metric, stage, or date"
        )

    confirmation_points = spec.get("next_confirmation_points")
    if (
        not isinstance(confirmation_points, list)
        or not confirmation_points
        or any(
            not _compat_module._valid_confirmation_point(value)
            for value in confirmation_points
        )
    ):
        messages.append(
            f"{spec_id}: execution route next_confirmation_points entries must identify measurable "
            "events or metrics and an interpretation effect"
        )


def _execution_route_validation_view(spec):
    """Hide shared V3 metadata only from the legacy residual-override detector.

    Shared metadata is validated above against the corrected canonical contract.
    The historical base interpreted every populated V3 field as override-only,
    so a shallow compatibility view is used only to avoid that obsolete check.
    The source artifact is never mutated.
    """
    routed_spec = dict(spec)
    for field in _EXECUTION_ROUTE_SHARED_V3_FIELDS:
        value = routed_spec.get(field)
        routed_spec[field] = [] if isinstance(value, list) else None
    return routed_spec


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

    # The legacy base only runs V3 override validation in the format-risk branch.
    # Route an ordinary non-execution candidate through that same contract without
    # changing the source artifact or pretending it is actually format-risk.
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

if __name__ == "__main__":
    _compat_module._base_layer._base.sys.exit(
        _compat_module._base_layer._base.main()
    )

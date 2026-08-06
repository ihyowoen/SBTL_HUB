#!/usr/bin/env python3
"""Review 4869541592 compatibility layer for ordinary V3 routes and clause modifiers."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

try:
    from validation_scripts.v3_stage_contracts import stage_a_validator_constants
except ModuleNotFoundError:
    from v3_stage_contracts import stage_a_validator_constants

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


def _ordinary_override_candidate(spec):
    if not isinstance(spec, dict):
        return False
    tags = spec.get("format_risk_tags")
    if not isinstance(tags, list):
        return False
    normalized_tags = [
        value.strip().lower()
        for value in tags
        if isinstance(value, str) and value.strip()
    ]
    if normalized_tags not in ([], ["none"]):
        return False
    residual_override_fields = [
        field
        for field in _compat_module.STAGE_A_V3_OVERRIDE_REQUIRED
        if spec.get(field) not in (None, "", [], {})
    ]
    return (
        spec.get("structural_value_override_applied") is True
        or bool(residual_override_fields)
    )


def validate_stage_a_spec(spec, index, messages):
    """Apply the same exactly-one route contract to ordinary V3 candidates."""
    if not _ordinary_override_candidate(spec):
        return _prior_validate_stage_a_spec(spec, index, messages)

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

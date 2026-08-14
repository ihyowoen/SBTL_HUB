#!/usr/bin/env python3
"""Stage A V3 route and full-artifact contract alignment layer.

The historical validator chain remains authoritative for unchanged lineage,
source-diversity, review-pool, and downstream checks. This layer aligns it with
canonical Structural News Value V3 by enforcing:

- ordinary strict items may use a complete V3 non-execution route;
- V3 non-execution routes carry structural selector lineage;
- execution routes retain shared V3 decision/evidence metadata;
- true override-only execution fields remain empty;
- full Stage A artifacts cannot PASS while Prompt 0.1S required item/summary
  surfaces are missing or internally inconsistent.
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
_CANONICAL_STRUCTURAL_SELECTOR_POLICY_FILE = "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md"
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

_SCORE_COMPONENT_LIMITS = {
    "market_structure_competition": 25,
    "supply_demand_price_utilisation": 25,
    "technology_performance_safety": 20,
    "cashflow_asset_value": 10,
    "law_policy_market_access": 10,
    "systemic_scale": 5,
    "persistence_irreversibility": 3,
    "decision_urgency_actionability": 2,
}
_SCORE_BANDS = (
    (85, "critical_structural"),
    (70, "high_decision_value"),
    (55, "material_industry_signal"),
    (40, "standard_monitoring"),
    (25, "context_or_reinforcement"),
    (0, "low_independent_value"),
)
_ANTI_BIAS_FIELDS = (
    "binding_status_used_as_importance_proxy",
    "legal_formality_used_as_importance_proxy",
    "headline_amount_used_without_denominator",
    "announced_capacity_treated_as_actual_output",
    "routine_execution_event_overranked",
    "conventional_execution_event_required_without_reason",
)
_FULL_ITEM_PRESENCE_FIELDS = (
    "structural_value_override_reason",
    "why_execution_event_not_required",
    "denominator_used",
    "denominator_gap",
    "baseline_follow_up_relation",
    "portfolio_coverage_contribution",
    "earnings_deep_dive_required",
    "earnings_release_available",
    "ir_deck_available",
    "call_or_transcript_expected",
    "qna_status",
    "prior_period_comparison_required",
    "earnings_rescue_questions",
    "anti_bias_check",
    "structural_rescue_required",
    "structural_rescue_question",
    "search_before_delete_status",
)
_FULL_SUMMARY_DICT_FIELDS = (
    "anchor_class_counts",
    "structural_lens_coverage_counts",
    "decision_value_classification_counts",
)
_FULL_SUMMARY_ARRAY_FIELDS = (
    "critical_structural_candidate_ids",
    "high_decision_value_candidate_ids",
    "high_value_review_pool_ids",
    "structural_signal_review_ids",
    "earnings_deep_dive_ids",
    "follow_up_candidate_ids",
    "zero_coverage_domains",
    "execution_or_formality_bias_findings",
    "technology_validation_gap_ids",
    "legal_policy_stage_gap_ids",
)
_FULL_SUMMARY_PASS_FIELDS = (
    "structural_value_selector_status",
    "portfolio_coverage_audit_status",
    "earnings_call_qna_audit_status",
    "follow_up_repromotion_audit_status",
    "execution_event_bias_audit_status",
    "content_depth_audit_status",
)
_REVIEW_POOLS_FOR_V3_COMPLETENESS = (
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
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
_prior_check_stage_a = _compat_module.check_stage_a


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
    """Enforce route-neutral V3 metadata required on execution strict items."""
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
        string_classes = [value for value in classes if isinstance(value, str)]
        if len(set(string_classes)) != len(classes):
            messages.append(f"{spec_id}: execution route anchor_classes must be unique")

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


def _is_full_stage_a_artifact(data):
    return (
        isinstance(data, dict)
        and data.get("stage") == "stage_a"
        and isinstance(data.get("summary"), dict)
        and isinstance(data.get("run_tag"), str)
        and bool(data.get("run_tag").strip())
    )


def _score_classification(score):
    for floor, classification in _SCORE_BANDS:
        if score >= floor:
            return classification
    return "low_independent_value"


def _validate_gate_objects(item, label, messages):
    credibility = item.get("execution_credibility_gate")
    if not isinstance(credibility, dict):
        messages.append(f"{label}: execution_credibility_gate must be an object")
    else:
        if credibility.get("status") not in {"PASS", "REVIEW", "FAIL"}:
            messages.append(f"{label}: execution_credibility_gate.status invalid")
        for field in ("anchor_type", "anchor_strength", "stage_precision_note"):
            if field not in credibility:
                messages.append(f"{label}: execution_credibility_gate missing {field}")
        if credibility.get("anchor_strength") not in {"strong", "moderate", "weak", "unknown"}:
            messages.append(f"{label}: execution_credibility_gate.anchor_strength invalid")

    cardability = item.get("independent_cardability_gate")
    if not isinstance(cardability, dict):
        messages.append(f"{label}: independent_cardability_gate must be an object")
    else:
        if cardability.get("status") not in {"PASS", "REVIEW", "FAIL"}:
            messages.append(f"{label}: independent_cardability_gate.status invalid")
        if not isinstance(cardability.get("distinct_event_or_stage_progression"), bool):
            messages.append(
                f"{label}: independent_cardability_gate.distinct_event_or_stage_progression must be boolean"
            )
        if cardability.get("full_schema_viability") not in {"PASS", "REVIEW", "FAIL"}:
            messages.append(f"{label}: independent_cardability_gate.full_schema_viability invalid")
        if not _compat_module._item_specific_narrative(
            cardability.get("duplicate_or_reinforcement_note")
        ):
            messages.append(
                f"{label}: independent_cardability_gate.duplicate_or_reinforcement_note must be item-specific"
            )


def _validate_decision_score(item, label, messages):
    score = item.get("decision_news_value_score")
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        messages.append(f"{label}: decision_news_value_score must be integer 0..100")
        return

    breakdown = item.get("decision_value_breakdown")
    if not isinstance(breakdown, dict):
        messages.append(f"{label}: decision_value_breakdown must be an object")
    else:
        if set(breakdown) != set(_SCORE_COMPONENT_LIMITS):
            messages.append(
                f"{label}: decision_value_breakdown keys must match canonical eight components"
            )
        else:
            total = 0
            for field, upper in _SCORE_COMPONENT_LIMITS.items():
                value = breakdown.get(field)
                if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= upper:
                    messages.append(
                        f"{label}: decision_value_breakdown.{field} must be integer 0..{upper}"
                    )
                else:
                    total += value
            if total != score:
                messages.append(
                    f"{label}: decision_value_breakdown sum {total} != decision_news_value_score {score}"
                )

    expected = _score_classification(score)
    if item.get("decision_value_classification") != expected:
        messages.append(
            f"{label}: decision_value_classification must be {expected!r} for score {score}"
        )


def _validate_publication_urgency(item, label, messages):
    urgency = item.get("publication_urgency")
    if not isinstance(urgency, dict):
        messages.append(f"{label}: publication_urgency must be an object")
        return
    if urgency.get("level") not in {"immediate", "near_term", "monitor"}:
        messages.append(f"{label}: publication_urgency.level invalid")
    if not _compat_module._item_specific_narrative(urgency.get("action_required")):
        messages.append(f"{label}: publication_urgency.action_required must be item-specific")
    if "decision_deadline" not in urgency:
        messages.append(f"{label}: publication_urgency missing decision_deadline")


def _validate_earnings_fields(item, label, messages):
    earnings = item.get("earnings_deep_dive_required")
    if not isinstance(earnings, bool):
        messages.append(f"{label}: earnings_deep_dive_required must be boolean")
        return
    availability_fields = (
        "earnings_release_available",
        "ir_deck_available",
        "call_or_transcript_expected",
    )
    if earnings:
        for field in availability_fields:
            if item.get(field) not in {"yes", "no", "unknown"}:
                messages.append(f"{label}: {field} invalid for earnings candidate")
        if item.get("qna_status") != "not_checked_stage_a":
            messages.append(f"{label}: earnings candidate qna_status must be not_checked_stage_a")
        if item.get("prior_period_comparison_required") is not True:
            messages.append(f"{label}: earnings candidate prior_period_comparison_required must be true")
    else:
        for field in availability_fields:
            if item.get(field) != "not_applicable":
                messages.append(f"{label}: non-earnings {field} must be not_applicable")
        if item.get("qna_status") != "not_applicable":
            messages.append(f"{label}: non-earnings qna_status must be not_applicable")
        if item.get("prior_period_comparison_required") is not False:
            messages.append(f"{label}: non-earnings prior_period_comparison_required must be false")
    if not isinstance(item.get("earnings_rescue_questions"), list):
        messages.append(f"{label}: earnings_rescue_questions must be an array")


def _validate_full_v3_candidate(item, label, messages, strict=False):
    _validate_gate_objects(item, label, messages)
    _validate_decision_score(item, label, messages)
    _validate_publication_urgency(item, label, messages)

    lenses = item.get("structural_value_lenses")
    if not isinstance(lenses, list) or (strict and not lenses):
        messages.append(
            f"{label}: structural_value_lenses must be {'non-empty ' if strict else ''}array"
        )

    for field in _FULL_ITEM_PRESENCE_FIELDS:
        if field not in item:
            messages.append(f"{label}: missing Prompt 0.1S field {field}")

    if "denominator_gap" in item and not isinstance(item.get("denominator_gap"), bool):
        messages.append(f"{label}: denominator_gap must be boolean")
    if "denominator_used" in item and not isinstance(item.get("denominator_used"), str):
        messages.append(f"{label}: denominator_used must be string")
    if "baseline_follow_up_relation" in item and not isinstance(
        item.get("baseline_follow_up_relation"), str
    ):
        messages.append(f"{label}: baseline_follow_up_relation must be string")
    if "portfolio_coverage_contribution" in item and not isinstance(
        item.get("portfolio_coverage_contribution"), list
    ):
        messages.append(f"{label}: portfolio_coverage_contribution must be an array")

    anti_bias = item.get("anti_bias_check")
    if isinstance(anti_bias, dict):
        for field in _ANTI_BIAS_FIELDS:
            if anti_bias.get(field) is not False:
                messages.append(f"{label}: anti_bias_check.{field} must be false")

    rescue_required = item.get("structural_rescue_required")
    if "structural_rescue_required" in item and not isinstance(rescue_required, bool):
        messages.append(f"{label}: structural_rescue_required must be boolean")
    if rescue_required is True and not _compat_module._item_specific_narrative(
        item.get("structural_rescue_question")
    ):
        messages.append(f"{label}: structural_rescue_question required when rescue is true")
    if item.get("search_before_delete_status") not in (None, "applied"):
        messages.append(f"{label}: search_before_delete_status must be applied")

    _validate_earnings_fields(item, label, messages)

    classes = item.get("anchor_classes")
    lenses = item.get("structural_value_lenses")
    tech_applicable = (
        isinstance(classes, list) and "technology_commercialization_anchor" in classes
    ) or (
        isinstance(lenses, list) and "technology_transition_commercialization" in lenses
    )
    if tech_applicable:
        for field in (
            "technology_validation_stage",
            "technology_score_cap_applied",
            "technology_validation_gap",
        ):
            if field not in item:
                messages.append(f"{label}: technology candidate missing {field}")


def _summary_field(data, field):
    if field in data:
        return True, data.get(field)
    summary = data.get("summary")
    if isinstance(summary, dict) and field in summary:
        return True, summary.get(field)
    return False, None


def _validate_full_stage_a_summary(data, messages):
    exact_fields = {
        "structural_selector_policy_version": _CANONICAL_STRUCTURAL_SELECTOR_POLICY_VERSION,
        "structural_selector_policy_file": _CANONICAL_STRUCTURAL_SELECTOR_POLICY_FILE,
        "core_industrial_weight_total": 70,
    }
    true_fields = (
        "credibility_cardability_value_urgency_separated",
        "industry_first_weighting_applied",
        "multi_anchor_class_model_applied",
        "mandatory_structural_lenses_applied",
        "search_before_delete_applied",
    )
    for field, expected in exact_fields.items():
        present, value = _summary_field(data, field)
        if not present or value != expected:
            messages.append(f"full Stage A summary {field} must be {expected!r}")

    present, policy_sha = _summary_field(data, "structural_selector_policy_sha")
    if not present or not isinstance(policy_sha, str) or not policy_sha.strip():
        messages.append("full Stage A summary structural_selector_policy_sha must be populated")

    for field in true_fields:
        present, value = _summary_field(data, field)
        if not present or value is not True:
            messages.append(f"full Stage A summary {field} must be true")

    for field in _FULL_SUMMARY_DICT_FIELDS:
        present, value = _summary_field(data, field)
        if not present or not isinstance(value, dict):
            messages.append(f"full Stage A summary {field} must be an object")

    for field in _FULL_SUMMARY_ARRAY_FIELDS:
        present, value = _summary_field(data, field)
        if not present or not isinstance(value, list):
            messages.append(f"full Stage A summary {field} must be an array")

    for field in _FULL_SUMMARY_PASS_FIELDS:
        present, value = _summary_field(data, field)
        if not present or value != "PASS":
            messages.append(f"full Stage A summary {field} must be PASS")


def _validate_full_stage_a_artifact(data, messages):
    for index, spec in enumerate(_compat_module.stage_a_specs(data)):
        label = spec.get("spec_id") or f"strict_passed_spec[{index}]"
        _validate_full_v3_candidate(spec, label, messages, strict=True)

    for pool in _REVIEW_POOLS_FOR_V3_COMPLETENESS:
        for index, item in enumerate(_compat_module.as_list(data.get(pool))):
            if not isinstance(item, dict):
                continue
            label = (
                item.get("review_pool_item_id")
                or item.get("story_id")
                or f"{pool}[{index}]"
            )
            _validate_full_v3_candidate(item, label, messages, strict=False)

    _validate_full_stage_a_summary(data, messages)


def check_stage_a(data):
    """Run legacy lineage checks, then Prompt 0.1S full-artifact completeness."""
    stream = io.StringIO()
    with redirect_stdout(stream):
        result = _prior_check_stage_a(data)
    legacy_output = stream.getvalue()
    if result != 0 or not _is_full_stage_a_artifact(data):
        print(legacy_output, end="")
        return result

    messages = []
    _validate_full_stage_a_artifact(data, messages)
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

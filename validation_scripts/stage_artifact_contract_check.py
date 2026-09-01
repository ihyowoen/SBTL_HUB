#!/usr/bin/env python3
"""Stage-exit schema contract checker for lineage, dates, source audit and Related."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Direct execution (`python validation_scripts/stage_artifact_contract_check.py`)
# starts with validation_scripts/ rather than the repository root on sys.path.
# Add the root before absolute package imports so the documented 0.7/0.8 CLI
# works exactly like module/unittest execution.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from validation_scripts.stage_a_v4_contract import validate_stage_a_v4_spec
from validation_scripts.stage_a_v4_hardening import validate_stage_a_v4_hardening

STAGE_TOP_LEVEL = {
    "A": [
        "stage_a_validity_status", "artifact_consistency_status", "csv_schema_status",
        "review_pool_partition_status", "strict_pass_gate_metadata_status",
        "baseline_duplicate_screen_status",
    ],
    "B": [
        "lineage_integrity_status", "stage_a_validity_guard_applied",
        "strict_gate_metadata_preserved", "execution_anchor_metadata_preserved",
        "superseded_lineage_mixed", "manual_integrated_rule_mixed",
        "previous_run_output_mixed",
    ],
    "C": [
        "strict_gate_acceptance_guard_applied", "accepted_pool_lineage_status",
    ],
    "0.4": ["lineage_guard"],
    "0.5": ["lineage_integrity_status"],
    "0.6": ["upstream_lineage_integrity", "lineage_and_anchor_guard"],
    "0.7": ["lineage_and_anchor_guard"],
    "0.8": ["github_main_sync_gate", "lineage_merge_gate"],
}

# Presence is not enough for a production stage exit. These are the positive
# values required when an artifact is used to authorize a downstream formal
# operation. A batch carrying a blocked/false guard cannot be counted merely
# because its top-level `status` marker says PASS.
STAGE_TOP_LEVEL_EXPECTED = {
    "A": {
        "stage_a_validity_status": "PASS",
        "artifact_consistency_status": "PASS",
        "csv_schema_status": "PASS",
        "review_pool_partition_status": "PASS",
        "strict_pass_gate_metadata_status": "PASS",
        "baseline_duplicate_screen_status": "PASS",
    },
    "B": {
        "lineage_integrity_status": "PASS",
        "stage_a_validity_guard_applied": True,
        "strict_gate_metadata_preserved": True,
        "execution_anchor_metadata_preserved": True,
        "superseded_lineage_mixed": False,
        "manual_integrated_rule_mixed": False,
        "previous_run_output_mixed": False,
    },
    "C": {
        "strict_gate_acceptance_guard_applied": True,
        "accepted_pool_lineage_status": "PASS",
    },
    "0.4": {"lineage_guard": "PASS"},
    "0.5": {"lineage_integrity_status": "PASS"},
    "0.6": {
        "upstream_lineage_integrity": "PASS",
        "lineage_and_anchor_guard": "PASS",
    },
    "0.7": {"lineage_and_anchor_guard": "PASS"},
}

# A declared stage is authoritative. In particular, repair/revise artifacts such
# as 0.2R/0.3R may not masquerade as the re-established ordinary B/C exits just
# because they happen to carry a similarly named bucket.
DECLARED_STAGE_ALIASES = {
    "A": {"a", "stage_a", "0.1"},
    "B": {"b", "stage_b", "0.2"},
    "C": {"c", "stage_c", "0.3"},
    "0.4": {"0.4"},
    "0.5": {"0.5"},
    "0.6": {"0.6"},
    "0.7": {"0.7"},
    "0.8": {"0.8"},
}

BUCKETS = {
    "A": ["strict_passed_spec"],
    "B": ["draft_cards", "draft_card"],
    "C": ["accepted_fact_safe", "revise_required", "rejected"],
    "0.4": ["addable_merge_safe"],
    "0.5": ["evidence_complete_and_source_claim_covered"],
    "0.6": ["content_enriched_and_language_polished"],
    "0.7": ["publish_ready"],
    "0.8": ["github_merge_ready"],
}

PROMPT_04_ROUTE_PASS_BUCKETS = (
    "addable_merge_safe_new_unrelated",
    "addable_merge_safe_distinct_follow_up",
    "addable_merge_safe_program_lineage",
)
PROMPT_04_OUTCOMES = set(PROMPT_04_ROUTE_PASS_BUCKETS)

ITEM_REQUIRED = {
    "A": [
        "spec_id", "strict_pass_gate", "execution_anchor_type", "baseline_relation",
        "related_prepass", "date_role", "selection_policy_version", "selection_route",
        "execution_credibility_gate", "independent_cardability_gate", "anchor_classes",
        "decision_news_value_score", "decision_value_breakdown",
        "decision_value_classification", "publication_urgency",
        "systemic_scale_denominator", "denominator_gap", "prior_state",
        "new_verified_fact", "changed_judgment", "uncertainty_resolved",
        "remaining_uncertainty", "incremental_information",
        "baseline_expectation_changed", "decision_relevance",
        "evidence_needed_for_stage_b", "next_confirmation_points",
        "structural_non_execution_reason", "why_execution_event_not_required",
        "technology_evidence_level", "policy_stage", "novelty_cap_basis",
    ],
    "B": ["source_spec_id", "fact_sources", "related_evidence_review", "date_role"],
    "C": ["source_spec_id", "fact_sources", "related_lineage", "date_role"],
    "0.4": ["source_spec_id", "event_fingerprint", "related_lineage", "addability_outcome"],
    "0.5": [
        "source_spec_id", "source_diversity_status", "source_discovery_ledger",
        "related_lineage", "date_role",
    ],
    "0.6": [
        "source_spec_id", "content_enriched", "language_terminology_polished",
        "related_lineage", "date_role", "source_diversity_status",
    ],
    "0.7": [
        "source_spec_id", "final_qc_gates", "related_lineage",
        "source_diversity_status",
    ],
    "0.8": [
        "id", "source_spec_id", "related_lineage", "date_role",
        "source_diversity_status", "merge_prep",
    ],
}


def item_marker(item):
    identifier = item.get("id") or item.get("source_spec_id") or item.get("spec_id")
    if identifier:
        return ("id", str(identifier))
    return ("value", json.dumps(item, ensure_ascii=False, sort_keys=True))


def collect_items(payload, stage):
    items = []
    seen = set()
    for bucket in BUCKETS.get(stage, []):
        value = payload.get(bucket)
        if isinstance(value, dict):
            candidates = [value]
        elif isinstance(value, list):
            candidates = [item for item in value if isinstance(item, dict)]
        else:
            candidates = []
        for item in candidates:
            marker = item_marker(item)
            if marker in seen:
                continue
            seen.add(marker)
            items.append(item)
    return items


def bucket_item_count(payload, bucket):
    value = payload.get(bucket)
    if isinstance(value, dict):
        return 1
    if isinstance(value, list):
        return sum(1 for item in value if isinstance(item, dict))
    return 0


def _pass_marker(value):
    if value == "PASS" or value is True:
        return True
    if isinstance(value, dict):
        return value.get("status") == "PASS"
    return False


def _top_level_gate_finding(stage, field, value):
    expected = STAGE_TOP_LEVEL_EXPECTED.get(stage, {}).get(field)
    if expected is not None:
        if expected == "PASS":
            if _pass_marker(value):
                return None
        elif value == expected:
            return None
        return {
            "scope": "top_level",
            "field": field,
            "expected": expected,
            "actual": value,
            "message": "stage-specific production gate must carry its passing value",
        }

    if stage == "0.8" and field == "github_main_sync_gate":
        if isinstance(value, dict) and value.get("status") == "PASS" \
                and value.get("baseline_locked") is True \
                and value.get("main_unchanged_since_locked_preflight") is True \
                and value.get("silent_rebase_performed") is False:
            return None
        if value == "PASS":
            return None
        return {
            "scope": "top_level",
            "field": field,
            "expected": "PASS with baseline_locked/main_unchanged true and silent_rebase false",
            "actual": value,
            "message": "0.8 github/main synchronization gate is not passing",
        }

    if stage == "0.8" and field == "lineage_merge_gate":
        if isinstance(value, dict) \
                and value.get("final_qc_lineage_passed") is True \
                and value.get("anchor_path_lineage_passed") is True \
                and value.get("github_ready_allowed") is True \
                and value.get("anchor_path_hold_count") == 0:
            return None
        if value == "PASS":
            return None
        return {
            "scope": "top_level",
            "field": field,
            "expected": "passing lineage merge gate with zero holds",
            "actual": value,
            "message": "0.8 lineage merge gate is not passing",
        }
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=sorted(STAGE_TOP_LEVEL))
    parser.add_argument("input")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        print("input must be a JSON object", file=sys.stderr)
        return 2

    findings = []
    declared_stage = payload.get("stage")
    if declared_stage is not None:
        if not isinstance(declared_stage, str) or declared_stage.strip().lower() not in DECLARED_STAGE_ALIASES[args.stage]:
            findings.append({
                "scope": "top_level",
                "field": "stage",
                "expected": sorted(DECLARED_STAGE_ALIASES[args.stage]),
                "actual": declared_stage,
                "message": "declared repair/revise or mismatched stage cannot substitute for the requested ordinary stage exit",
            })

    for field in STAGE_TOP_LEVEL[args.stage]:
        if field not in payload:
            findings.append({"scope": "top_level", "field": field})
            continue
        gate_finding = _top_level_gate_finding(args.stage, field, payload[field])
        if gate_finding:
            findings.append(gate_finding)

    items = collect_items(payload, args.stage)
    if args.stage in {"A", "0.5", "0.6", "0.7", "0.8"} and not items:
        findings.append({"scope": "top_level", "field": f"non_empty_{BUCKETS[args.stage][0]}"})

    if args.stage == "0.4":
        route_specific_count = sum(bucket_item_count(payload, bucket) for bucket in PROMPT_04_ROUTE_PASS_BUCKETS)
        if route_specific_count and not items:
            findings.append({
                "scope": "top_level",
                "field": "addable_merge_safe",
                "message": "route-specific passing buckets cannot substitute for addable_merge_safe[]",
            })

    for index, item in enumerate(items):
        item_id = item.get("id") or item.get("source_spec_id") or item.get("spec_id")
        for field in ITEM_REQUIRED.get(args.stage, []):
            if field not in item:
                findings.append({"scope": item_id, "field": field})
        if args.stage == "A":
            v4_messages: list[str] = []
            validate_stage_a_v4_spec(item, index, v4_messages, require_contract=True)
            validate_stage_a_v4_hardening(item, index, v4_messages, require_contract=True)
            for message in v4_messages:
                findings.append({
                    "scope": item_id,
                    "contract": "stage_a_v4",
                    "message": message,
                })
        if args.stage == "0.4" and item.get("addability_outcome") not in PROMPT_04_OUTCOMES:
            findings.append({
                "scope": item_id,
                "field": "addability_outcome",
                "message": "must be a validator-bound addable_merge_safe route",
            })

    result = {
        "status": "PASS" if not findings else "BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT",
        "stage": args.stage,
        "item_count": len(items),
        "missing_count": len(findings),
        "findings": findings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())

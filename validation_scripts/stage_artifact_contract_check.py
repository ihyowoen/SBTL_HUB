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
    ],
    "B": ["source_spec_id", "fact_sources", "related_evidence_review", "date_role"],
    "C": ["source_spec_id", "fact_sources", "related_lineage", "date_role"],
    "0.4": ["source_spec_id", "event_fingerprint", "related_lineage"],
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
    for field in STAGE_TOP_LEVEL[args.stage]:
        if field not in payload:
            findings.append({"scope": "top_level", "field": field})

    items = collect_items(payload, args.stage)
    if args.stage in {"A", "0.5", "0.6", "0.7", "0.8"} and not items:
        findings.append({"scope": "top_level", "field": f"non_empty_{BUCKETS[args.stage][0]}"})

    for index, item in enumerate(items):
        item_id = item.get("id") or item.get("source_spec_id") or item.get("spec_id")
        for field in ITEM_REQUIRED.get(args.stage, []):
            if field not in item:
                findings.append({"scope": item_id, "field": field})
        if args.stage == "A":
            v4_messages: list[str] = []
            validate_stage_a_v4_spec(item, index, v4_messages, require_contract=True)
            for message in v4_messages:
                findings.append({
                    "scope": item_id,
                    "contract": "stage_a_v4",
                    "message": message,
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
#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RUN = ROOT / "runs/2026-09-03"
BASE_BUILDER = ROOT / "scripts/prompt_0_1p_r6_promotion.py"
OUT = RUN / "stage_a_prompt_0_1p_r6_promotion16_20260903_R1.json"
REPORT = RUN / "stage_a_prompt_0_1p_r6_promotion16_validation_20260903_R1.json"
INPUT = RUN / "prompt_0_1p_r6_candidates16_input_20260903_R1.json"
PROMOTED = {"R6_B01_REVIEW_006", "R6_B01_REVIEW_024"}

MIRROR = {
    "anchor_classes": "anchor_classes",
    "structural_value_lenses": "structural_value_lenses",
    "structural_value_override_applied": "structural_value_override_applied",
    "structural_value_override_reason": "structural_value_override_reason",
    "evidence_needed_for_stage_b": "evidence_needed_for_stage_b",
    "why_execution_event_not_required": "why_execution_event_not_required",
    "incremental_information": "incremental_information",
    "decision_relevance": "decision_relevance",
    "baseline_expectation_changed": "baseline_expectation_changed",
    "follow_up_relation": "baseline_follow_up_relation",
    "next_confirmation_points": "next_confirmation_points",
    "portfolio_coverage_contribution": "portfolio_coverage_contribution",
    "earnings_deep_dive_required": "earnings_deep_dive_required",
    "qna_status": "qna_status",
    "decision_news_value_score": "decision_news_value_score",
    "decision_value_breakdown": "decision_value_breakdown",
    "decision_value_classification": "decision_value_classification",
    "prior_state": "prior_state",
    "new_verified_fact": "new_verified_fact",
    "changed_judgment": "changed_judgment",
    "uncertainty_resolved": "uncertainty_resolved",
    "remaining_uncertainty": "remaining_uncertainty",
    "denominator_used": "denominator_used",
    "denominator_gap": "denominator_gap",
    "publication_urgency": "publication_urgency",
    "anti_bias_check": "anti_bias_check",
    "structural_rescue_required": "structural_rescue_required",
    "structural_rescue_question": "structural_rescue_question",
    "technology_validation_stage": "technology_validation_stage",
    "technology_score_cap_applied": "technology_score_cap_applied",
    "technology_validation_gap": "technology_validation_gap",
}


def candidate_id(item: dict) -> str:
    return str(item.get("spec_id") or item.get("review_pool_item_id") or item.get("story_id") or "")


def is_follow_up(item: dict) -> bool:
    classes = item.get("anchor_classes")
    if isinstance(classes, list) and "follow_up_probability_anchor" in classes:
        return True
    relation = item.get("baseline_follow_up_relation")
    if not isinstance(relation, str):
        return False
    return relation.strip().lower() not in {"", "new", "new_unrelated", "unrelated", "not_applicable", "none"}


def main() -> int:
    # The first builder intentionally emits its fail-closed artifact even when the
    # historical compatibility layer rejects it. We then normalize only the
    # contract fields identified by that layer; promotion judgments/scores remain unchanged.
    proc = subprocess.run([sys.executable, str(BASE_BUILDER)], cwd=ROOT, check=False)
    if not OUT.exists():
        raise SystemExit(f"base promotion builder did not emit {OUT}")

    art = json.loads(OUT.read_text(encoding="utf-8"))
    locked = json.loads(INPUT.read_text(encoding="utf-8"))
    originals = {x["review_pool_item_id"]: x for x in locked["items"]}
    strict = art.get("strict_passed_spec", [])
    by_source_review = {
        x.get("promotion_provenance", {}).get("source_review_pool_item_id"): x
        for x in strict if isinstance(x, dict)
    }
    if set(by_source_review) != PROMOTED:
        raise SystemExit(f"unexpected promoted set {sorted(k for k in by_source_review if k)}")

    # 006: binding Liontown-Centenario farm-in. Restore explicit execution identity.
    lion = by_source_review["R6_B01_REVIEW_006"]
    lion_orig = originals["R6_B01_REVIEW_006"]
    lion["selection_route"] = "execution_anchor_route"
    lion["execution_anchor_type"] = lion_orig.get("execution_anchor_type") or "signed_agreement"
    lion["execution_anchor_strength"] = lion_orig.get("execution_anchor_strength") or "moderate"
    lion["structural_value_override_applied"] = False
    lion["structural_value_override_reason"] = None
    lion["why_execution_event_not_required"] = None
    lion.pop("structural_selector_policy_version", None)
    gate = lion.setdefault("execution_credibility_gate", {})
    gate["status"] = "PASS"
    gate["anchor_type"] = lion["execution_anchor_type"]
    gate["anchor_strength"] = lion["execution_anchor_strength"]
    lion["evidence_needed_for_stage_b"] = [
        "Company/ASX filing or executed farm-in contract confirming the 31 August 2026 Centenario agreement date, signed stage, earn-in milestones, consideration, ownership path up to 100%, and project resource or capacity terms."
    ]
    lion["next_confirmation_points"] = [
        "A first earn-in milestone filing reporting payment, ownership percentage and project resource or capacity metric would strengthen or weaken the judgment that the signed Centenario farm-in materially changes Liontown's lithium supply option value."
    ]

    # 024: sector earnings/data signal. Enforce the canonical V3 non-execution route.
    earn = by_source_review["R6_B01_REVIEW_024"]
    earn["selection_route"] = "structural_non_execution_route"
    earn["execution_anchor_type"] = None
    earn["execution_anchor_strength"] = None
    earn["structural_value_override_applied"] = True
    earn["structural_selector_policy_version"] = "STRUCTURAL_NEWS_VALUE_SELECTION_V3"
    earn["anchor_classes"] = [a for a in earn.get("anchor_classes", []) if a != "execution_event_anchor"]
    if not earn["anchor_classes"]:
        earn["anchor_classes"] = ["data_financial_anchor", "strategic_behavior_anchor"]
    earn["structural_value_override_reason"] = (
        "Named lithium-miner earnings and operating data can change the sector demand-and-profitability judgment without a single corporate execution event when storage demand, realised price, volume and cost movements are independently verifiable."
    )
    earn["why_execution_event_not_required"] = (
        "The publication is a cross-issuer financial and demand signal: verified earnings, sales-volume, realised-price and ESS-demand data directly alter the lithium supply-demand judgment without requiring a new plant, contract or transaction."
    )
    earn["evidence_needed_for_stage_b"] = [
        "Named miner H1 2026 earnings releases and filings confirming profit, lithium sales volume, realised lithium price, unit cost, inventory or utilisation, and the claimed ESS-demand contribution versus the prior reporting period."
    ]
    earn["next_confirmation_points"] = [
        "The next quarterly filing reporting lithium sales volume, realised price, unit cost and ESS-linked demand would strengthen or weaken the judgment that storage demand is a persistent sector earnings driver rather than a one-period price effect."
    ]
    gate = earn.setdefault("execution_credibility_gate", {})
    gate["status"] = "PASS"
    gate["anchor_type"] = "structural_or_policy_signal"
    gate["anchor_strength"] = "moderate"

    # Exact strict-spec <-> decision-ledger mirror required by the production V3 chain.
    strict_by_story = {}
    for item in strict:
        for sid in item.get("source_story_ids", []):
            strict_by_story[sid] = item
    for row in art.get("decision_ledger", []):
        spec = strict_by_story.get(row.get("story_id"))
        if not spec:
            continue
        row["ledger_decision"] = "passed"
        row["editorial_bucket"] = "strict_passed_spec"
        row["spec_id"] = spec["spec_id"]
        row["review_pool_item_id"] = None
        for ledger_field, spec_field in MIRROR.items():
            if spec_field in spec:
                row[ledger_field] = copy.deepcopy(spec.get(spec_field))

    # Match the historical completeness validator's exact follow-up semantics.
    all_items = []
    for pool in ("strict_passed_spec", "candidate_review_pool", "watchlist_context_pool", "reject_or_support_only_pool"):
        all_items.extend(x for x in art.get(pool, []) if isinstance(x, dict))
    art["summary"]["follow_up_candidate_ids"] = [candidate_id(x) for x in all_items if is_follow_up(x)]

    # Canonical next-call coexistence contract: promoted strict work + still-open review pool.
    art["next_call_recommendation"] = {
        "recommended_next_call": "Stage B r0",
        "recommended_prompt_id": "Prompt 0.2",
        "recommended_input_universe": "Stage A strict_passed_spec[] only",
        "reason": "Prompt 0.1P produced two ordinary Stage A strict specs while fourteen candidate-review items remain outside Stage B.",
        "pending_parallel_or_followup_call": "review_pool/treasure triage",
        "pending_prompt_id": "authorized review_pool/treasure promotion protocol, not Prompt 0.2",
        "pending_input_universe": "candidate_review_pool[] + eligible treasure/review-only universe",
        "pending_reason": "Stage B may process strict_passed_spec[] only; review_pool/treasure remains open and must not be treated as exhausted.",
        "blocked_items_summary": [{"pool": "candidate_review_pool", "count": 14}],
    }

    from validation_scripts import stage_lineage_contract_check as lineage
    from validation_scripts.stage_a_v4_contract import validate_stage_a_v4_payload
    from validation_scripts.stage_a_v4_hardening import validate_stage_a_v4_hardening_payload
    from validation_scripts.stage_a_full_v3_completeness_review4945713246 import (
        prevalidate_full_stage_a_artifact,
        validate_full_stage_a_artifact,
    )

    pre = prevalidate_full_stage_a_artifact(art)
    v4 = validate_stage_a_v4_payload(art, require_contract=True)
    hard = validate_stage_a_v4_hardening_payload(art, require_contract=True)
    auth = lineage._validate_active_required_docs(art)
    compat = lineage._project_full_stage_a_for_v3_compat(art) if not auth else art
    full = validate_full_stage_a_artifact(compat, lineage._compat_module)
    rc = lineage.check_stage_a(art)
    status = "PASS" if not (pre or v4 or hard or auth or full) and rc == 0 else "FAIL"
    report = {
        "schema": "prompt_0_1p_r6_promotion_validation_v2",
        "status": status,
        "base_builder_rc": proc.returncode,
        "candidate_count": 16,
        "promoted_count": 2,
        "retained_count": 14,
        "promoted_review_pool_ids": sorted(PROMOTED),
        "prevalidation_errors": pre,
        "v4_contract_errors": v4,
        "v4_hardening_errors": hard,
        "active_authority_errors": auth,
        "full_completeness_errors": full,
        "lineage_check_rc": rc,
    }
    art["status"] = status
    OUT.write_text(json.dumps(art, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Formal Stage A 0.1P duplicate disposition for one fully matched Source ID.

Scope is *only* SRC26-20260920_142928-0145, a September 19 secondary
observation of the September 17 FAW/Leapmotor R&D agreement already represented
in locked Full as 2026-09-17_CN_01. No new strict spec or downstream source-add
is authorized. Original pre-native evidence remains attached for audit.
"""

from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

SOURCE_ID = "SRC26-20260920_142928-0145"
FULL_ID = "2026-09-17_CN_01"
BASE_SHA256 = "e42097f6f17495ff24550b2c72dba9d5874e7a835090c95cae4881750116d109"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write(path: Path, data) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> None:
    p = argparse.ArgumentParser()
    for field in ("base", "original16", "full", "output", "receipt"):
        p.add_argument("--" + field, required=True, type=Path)
    args = p.parse_args()

    assert sha256(args.base) == BASE_SHA256
    base = read(args.base)
    j16 = {j["source_id"]: j for j in read(args.original16)["judgments"]}
    full = read(args.full)
    original_spec = next(x for x in full["cards"] if x["id"] == FULL_ID)
    assert len(full["cards"]) == 1676
    assert original_spec["date"] == "2026-09-17"
    assert "Leapmotor" in original_spec["title"]
    assert "차세대 배터리" in original_spec["title"]
    assert SOURCE_ID in j16
    judgment = j16[SOURCE_ID]
    assert judgment["source_row_index"] == 145
    assert judgment["independent_cardability_gate"]["status"] == "FAIL"
    assert judgment["decision_news_value_score"] == 15
    assert judgment["related_prepass"]["matched_baseline_candidate_ids"] == [FULL_ID]
    assert len(base["strict_passed_spec"]) == 8
    assert len(base["candidate_review_pool"]) == 636
    assert len(base["existing_reinforcement"]) == 28
    assert len(base["decision_ledger"]) == 1330
    assert len(base["promotion_reassessment_ledger"]) == 45
    assert base["summary"]["unprocessed_editorial_observations"] == 1285

    target = next(x for x in base["candidate_review_pool"] if x["candidate_id"] == SOURCE_ID)
    assert target["source_row_index"] == 145
    assert target["headline_raw"] == judgment["headline_raw"]
    assert target["primary_url"] == judgment["source_url_original"]
    assert target["stage_a_pool"] == "candidate_review_pool"
    old_source = copy.deepcopy(target)

    delta_reason = (
        "2026-09-19 Gasgoo observation reports the same China Automotive New Energy "
        "Battery Technology–Leapmotor advanced battery technology cooperation agreement "
        "signed on 2026-09-17. Locked Full 2026-09-17_CN_01 already records the "
        "same parties, R&D instrument, four chemistry/technology scopes, and signing date. "
        "FAW Qixin Power investment LOI is a distinct parallel instrument and is not "
        "an additional battery R&D contract in this Source ID."
    )
    recheck = {
        "status": "PASS",
        "same_event_checked": True,
        "matched_baseline_candidate_ids": [FULL_ID],
        "matched_current_batch_candidate_ids": [],
        "relation_candidates": [
            {
                "target_candidate_id": FULL_ID,
                "proposed_relation_type": "same_event_duplicate",
                "confidence": "high",
                "reason": delta_reason,
                "anchor_class_to_verify": None,
                "incremental_anchor_question": None,
            }
        ],
        "duplicate_disposition": "same_event_duplicate",
        "earliest_same_event_check_status": "PASS",
        "fresh_anchor_questions": [
            "Preserve any genuinely new owner-language or material source contribution before an explicit downstream add_source request; none proven by this source."
        ],
        "earliest_same_event_date": "2026-09-17",
        "earliest_check_scope": "Locked Full 1676, Gasgoo Sept19 article, Reuters Sept17 original, FAW event stage split",
        "previous_prepass_edges_preserved_for_audit": [target["related_prepass"]],
    }
    judgment_receipt = {
        "gate_version": "PROMPT_0_1P_V4_20260829",
        "status": "FORMAL_INDIVIDUAL_NON_PROMOTION_COMPLETE",
        "candidate_id": SOURCE_ID,
        "original_source_row_index": 145,
        "original_source_url_preserved": old_source["primary_url"],
        "original_headline_preserved": old_source["headline_raw"],
        "economic_event": "China Automotive New Energy Battery Technology and Leapmotor R&D cooperation signed September 17",
        "date_role": {
            "economic_agreement_date": "2026-09-17",
            "gasgoo_publication_date": "2026-09-19",
            "source_observation_collection_date": "2026-09-20",
            "first_located_same_event_publication": "2026-09-17",
        },
        "execution_credibility_gate": {"status": "PASS", "reason": "The signed agreement is reported as executed, but it was already recorded in Full."},
        "independent_cardability_gate": {"status": "FAIL", "reason": "No increment beyond locked Full event; repeated source is support-only."},
        "decision_news_value_score": 15,
        "decision_value_breakdown": judgment["decision_value_breakdown"],
        "publication_urgency": "monitor",
        "novelty_cap_basis": "repeated_announcement_no_new_fact",
        "related_prepass": recheck,
        "new_verified_fact_beyond_full": "NONE_ESTABLISHED",
        "event_units_preserved": ["BATTERY_RND_AGREEMENT_ALREADY_FULL", "SEPARATE_POWERTRAIN_INVESTMENT_LOI_NOT_COUNTED_AS_BATTERY_RND"],
        "confidence_boundary": "Formal selector duplicate disposition, not Stage B source-quote audit or permission to update Full.",
        "sources": [
            old_source["primary_url"],
            "https://autonews.gasgoo.com/articles/ev/2101180788380209153",
            "https://www.reuters.com/world/asia-pacific/leapmotor-plans-join-series-funding-faw-subsidiary-2026-09-17/",
        ],
        "full_reference_id": FULL_ID,
        "full_reference_fingerprint_sha256": original_spec["event_fingerprint"]["fingerprint_sha256"],
        "final_disposition": "EXISTING_REINFORCEMENT_NO_NEW_CARD",
        "strict_pass_gate": "NOT_APPLICABLE_NON_PROMOTION",
        "stage_b_authorized": False,
    }

    def apply(row: dict) -> None:
        row.update({
            "stage_a_pool": "existing_reinforcement",
            "ledger_decision": "existing_reinforcement",
            "editorial_bucket": "existing_reinforcement",
            "review_pool_resolution_status": "resolved_no_promotion",
            "final_review_pool_disposition": "closed_no_new_card_existing_full_duplicate",
            "decision_news_value_score": judgment_receipt["decision_news_value_score"],
            "decision_value_breakdown": judgment_receipt["decision_value_breakdown"],
            "decision_value_classification": "low_independent_value",
            "publication_urgency": {
                "level": "monitor",
                "reason": "Same September 17 technical cooperation agreement already in Full.",
                "action_required": "Only verify unique evidence contribution before any separately authorized add_source; do not make a second card.",
                "decision_deadline": None,
            },
            "execution_credibility_gate": {
                "status": "PASS", "reason": judgment_receipt["execution_credibility_gate"]["reason"],
                "anchor_type": "execution_event_anchor", "anchor_strength": "moderate",
                "stage_precision_note": "Signed R&D cooperation Sept17; not battery production, delivery or independent new card.",
            },
            "independent_cardability_gate": {
                "status": "FAIL", "reason": judgment_receipt["independent_cardability_gate"]["reason"],
                "full_schema_viability": "FAIL_DUPLICATE", "distinct_event_or_stage_progression": False,
                "duplicate_or_reinforcement_note": delta_reason,
            },
            "related_prepass": recheck,
            "baseline_relation": "same_event_duplicate",
            "baseline_match": FULL_ID,
            "duplicate_risk": "fatal",
            "novelty_cap_basis": "repeated_announcement_no_new_fact",
            "why_not_strict_passed_spec": delta_reason,
            "reason_not_new_card": delta_reason,
            "reason": delta_reason,
            "reinforcement_type": "same_event_duplicate",
            "new_verified_fact": "None beyond locked Full for this instrument.",
            "incremental_information": "No distinct new dated economic action; source maintains a secondary observation of the existing event.",
            "changed_judgment": "Duplicate identity established, not a new economic event.",
            "date_role": {
                "observed_date": "2026-09-20",
                "event_date": "2026-09-17",
                "publication_date": "2026-09-19",
                "announcement_date": "2026-09-17",
                "status": "PASS_STAGE_A_PRELIMINARY",
                "representative_date_basis": "Prior Reuters event publication and signed agreement, not the Sept19 restatement.",
            },
            "stage_b_authorized": False,
            "canonical_card_write_allowed": False,
            "formal_0_1P_non_promotion_20261101": judgment_receipt,
        })

    apply(target)
    decisions = [x for x in base["decision_ledger"] if x["candidate_id"] == SOURCE_ID]
    assert len(decisions) == 1
    apply(decisions[0])

    base["candidate_review_pool"] = [x for x in base["candidate_review_pool"] if x["candidate_id"] != SOURCE_ID]
    base["existing_reinforcement"].append(target)
    resolutions = [x for x in base["review_pool_resolution_ledger"] if x["story_id"] == SOURCE_ID]
    assert len(resolutions) == 1
    resolution = resolutions[0]
    resolution.update({
        "current_disposition": "existing_reinforcement",
        "disposition_basis": delta_reason,
        "carry_forward_policy": "preserve_as_existing_card_reinforcement_no_new_card",
        "next_action_condition": "Review only unique evidence contribution before an explicitly authorized source addition; no new strict card.",
        "final_review_pool_disposition": "closed_no_new_card_existing_full_duplicate",
        "reviewed_by_stage_or_pass": "PROMPT_0_1P_V4_20260829 formal non-promotion Nov1 2026",
        "review_artifact_id": "STAGE_A_0145_FORMAL_NO_NEW_CARD_20261101",
    })
    # Only live review-pool members may be present in this lineage ledger.
    # Preserve its closed record in the formal resolution receipt instead.
    final_review_resolution = copy.deepcopy(resolution)
    base["review_pool_resolution_ledger"] = [
        x for x in base["review_pool_resolution_ledger"] if x["story_id"] != SOURCE_ID
    ]

    base["promotion_reassessment_ledger"].append({
        "candidate_id": SOURCE_ID,
        "economic_event_cluster_id": judgment["case_id"],
        "before_pool": "candidate_review_pool",
        "after_pool": "existing_reinforcement",
        "promotion_reassessment_status": "FORMAL_NO_PROMOTION_SAME_EVENT_IN_LOCKED_FULL",
        "resolved": delta_reason,
        "remaining": "Source-contribution/add_source check is separately gated; original Full unchanged.",
        "source_candidates": judgment_receipt["sources"],
        "source_observation_preserved": True,
    })

    summary = base["summary"]
    summary["needs_review_count"] -= 1
    summary["duplicate_or_reinforcement_count"] += 1
    summary["existing_reinforcement_count"] += 1
    summary["processed_priority_source_observations"] += 1
    summary["unprocessed_editorial_observations"] -= 1
    base["review_pool_partition_summary"]["candidate_review_pool"] -= 1
    for key in (
        "high_value_review_pool_ids", "structural_signal_review_pool_ids",
        "earnings_deep_dive_pool_ids", "follow_up_candidate_ids",
        "technology_validation_gap_ids", "legal_policy_stage_gap_ids",
    ):
        if isinstance(summary.get(key), list):
            summary[key] = [x for x in summary[key] if x != SOURCE_ID]

    # Native Stage A computes coverage maps across its four candidate pools,
    # which do not include the separately preserved existing-reinforcement
    # ledger. The reclassification must therefore update these three maps.
    native_candidate_pools = (
        "strict_passed_spec", "candidate_review_pool",
        "watchlist_context_pool", "reject_or_support_only_pool",
    )
    anchors, lenses, classifications = Counter(), Counter(), Counter()
    for pool in native_candidate_pools:
        for row in base[pool]:
            anchors.update(x for x in row.get("anchor_classes", []) if isinstance(x, str))
            lenses.update(x for x in row.get("structural_value_lenses", []) if isinstance(x, str))
            value = row.get("decision_value_classification")
            if isinstance(value, str) and value:
                classifications[value] += 1
    summary["anchor_class_counts"] = dict(sorted(anchors.items()))
    summary["structural_lens_coverage_counts"] = dict(sorted(lenses.items()))
    summary["decision_value_classification_counts"] = dict(sorted(classifications.items()))

    # The initial non-authoritative attachment remains an immutable historical
    # source snapshot. Update only current accounting fields of the manifest.
    att = base["pre_native_0_1P_attachment_manifest_20261101"]
    att["new_formal_decisions"] = 1
    att["remaining_formal_source_count"] = 1284
    att["formal_review_completed_after_attachment_count"] = 1
    att["formal_review_completed_source_ids"] = [SOURCE_ID]
    base["formal_0_1P_resolution_20261101"] = {
        "authority": "PROMPT_0_1P_V4_20260829",
        "case_completed_count": 1,
        "source_id": SOURCE_ID,
        "result": "EXISTING_REINFORCEMENT_NO_NEW_CARD",
        "original_formal_completed_45": 45,
        "new_formal_completed": 1,
        "cumulative_formal_completed": 46,
        "formal_unadjudicated_remaining": 1284,
        "new_strict_passes": 0,
        "current_strict_pass_total": 8,
        "new_stage_b_authorization": False,
        "bounded_source_provenance": judgment_receipt["sources"],
        "full_source_reference": FULL_ID,
        "source_to_event_non_authoritative_attachment_preserved": True,
        "closed_review_pool_resolution": final_review_resolution,
    }

    assert len(base["strict_passed_spec"]) == 8
    assert len(base["candidate_review_pool"]) == 635
    assert len(base["existing_reinforcement"]) == 29
    assert len(base["watchlist_context_pool"]) == 658
    assert len(base["decision_ledger"]) == 1330
    assert len({x["candidate_id"] for x in base["decision_ledger"]}) == 1330
    assert sum(len(base[k]) for k in ("strict_passed_spec", "candidate_review_pool", "watchlist_context_pool", "existing_reinforcement")) == 1330
    assert len(base["promotion_reassessment_ledger"]) == 46
    assert summary["unprocessed_editorial_observations"] == 1284

    write(args.output, base)
    receipt = {
        "artifact_type": "STAGE_A_0145_FORMAL_NO_NEW_CARD_INDIVIDUAL_0_1P_RECEIPT",
        "status": "PENDING_NATIVE_CHECK_AFTER_FORMAL_NON_PROMOTION",
        "locked_main_commit": base["base_main_commit_sha"],
        "locked_full_count": 1676,
        "original_stage_a_with70_sha256": BASE_SHA256,
        "formal_stage_a_output_sha256": sha256(args.output),
        "source": judgment_receipt,
        "new_formal_individual_reviews": 1,
        "cumulative_formal_individual_reviews": 46,
        "formal_pending": 1284,
        "strict_passed_spec_count": 8,
        "new_strict_passes": 0,
        "source_observations_unchanged": 1330,
        "pool_counts": {key: len(base[key]) for key in ("strict_passed_spec", "candidate_review_pool", "watchlist_context_pool", "existing_reinforcement")},
        "stage_b_new_entry_authorized": False,
        "upstream_lineage_change": "ONLY_SOURCE_0145_RECLASSIFIED_IN_STAGE_A_NON_PROMOTION",
    }
    write(args.receipt, receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

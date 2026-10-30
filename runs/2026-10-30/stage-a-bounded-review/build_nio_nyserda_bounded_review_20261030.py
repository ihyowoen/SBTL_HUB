#!/usr/bin/env python3
"""Create a read-only-input, create-only Stage A 0.1P evidence/decision supplement.

This is NOT the complete Stage A machine artifact. The two active native validators
require all 1,330 source identities and a valid upstream 0.0D/0.0C PASS envelope.
Do not treat this supplement as authorization to enter Stage B.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROMPT_REL = "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md"
SOURCE_SHA256 = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"
FULL_GIT_BLOB = "07a91714e56be2a8bfad10ab63822f0c5cb3f06e"

NIO_IDS = [
    "SRC26-20260928_160143-0003",
    "SRC26-20260928_160143-0004",
    "SRC26-20260928_160143-0216",
    "WK26-VOL03-013",
]
NY_IDS = ["SRC26-20260926_120143-0199"]
SCORES = [
    "market_structure_competition",
    "supply_demand_price_utilisation",
    "technology_performance_safety",
    "cashflow_asset_value",
    "law_policy_market_access",
    "systemic_scale",
    "persistence_irreversibility",
    "decision_urgency_actionability",
]
MAX = [25, 25, 20, 10, 10, 5, 3, 2]
ASSETS = [
    {"name": "Eastwater Energy Storage", "county": "Monroe", "mw": 100, "hours": 4},
    {"name": "Holtsville Energy Storage", "county": "Suffolk", "mw": 110, "hours": 4},
    {"name": "KCE NY 37", "county": "Suffolk", "mw": 150, "hours": 4, "site": "Manorville"},
    {"name": "KCE NY 5", "county": "Ulster", "mw": 94, "hours": 4, "site": "New Paltz"},
    {"name": "Blue Spruce Storage", "county": "Bronx", "mw": 133, "hours": 4},
    {"name": "Palladium Storage", "county": "Bronx", "mw": 123, "hours": 4},
    {"name": "Lighthouse Energy Storage", "county": "Chautauqua", "mw": 140, "hours": 8},
    {"name": "Zenobe Burns", "county": "Allegany", "mw": 100, "hours": 4},
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unchanged_write(path, data):
    if path.exists():
        raise FileExistsError(f"CREATE_ONLY_TARGET_EXISTS: {path}")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-ledger", type=Path, required=True)
    parser.add_argument("--full", type=Path, default=ROOT / "data/cards.full.json")
    args = parser.parse_args()
    assert digest(args.source_ledger) == SOURCE_SHA256, "source ledger baseline moved"
    full_bytes = args.full.read_bytes()
    full_blob = hashlib.sha1(b"blob " + str(len(full_bytes)).encode() + b"\x00" + full_bytes).hexdigest()
    assert full_blob == FULL_GIT_BLOB, "Full baseline moved"
    full_data = json.loads(full_bytes)
    cards = full_data["cards"]
    assert len(cards) == 1676 and full_data["total"] == 1676
    full_ids = {c.get("id") for c in cards}
    for card_id in ["R15_02", "2026-04-22_US_02", "2026-04-24_KR_03", "GL05", "2026-08-12_CN_01", "R4_12", "R8_02", "2026-04-27_CN_10"]:
        assert card_id in full_ids, f"missing expected baseline comparison {card_id}"
    with args.source_ledger.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    all_ids = [r["candidate_id"] for r in rows]
    assert len(rows) == 1330 and len(all_ids) == len(set(all_ids)), "original universe not unique 1,330"
    selected_ids = NIO_IDS + NY_IDS
    assert len(set(selected_ids)) == 5
    lookup = {r["candidate_id"]: r for r in rows}
    assert set(selected_ids).issubset(lookup)
    assert all(lookup[k]["stage_a_pool"] == "candidate_review_pool" for k in selected_ids)
    assert all(lookup[k]["decision_news_value_score"] == "64" for k in selected_ids)
    assert all(not lookup[k]["economic_event_cluster_id"] for k in selected_ids)
    assert sum(1 for r in rows if r["economic_event_cluster_id"]) == 45
    assert sum(1 for r in rows if not r["economic_event_cluster_id"]) == 1285
    # Current 1,330-headline lexical cross-check, not a semantic exhaustiveness proof.
    import re
    nio_rx = re.compile(r"(?=.*(?:nio|蔚来|니오))(?=.*(?:geely|吉利|지리|길리))", re.I)
    ny_rx = re.compile(r"nyserda|(?:new york|뉴욕).{0,70}(?:950\s*mw|storage|ess|배터리)|(950\s*mw).{0,70}(?:storage|battery|ESS)", re.I)
    candidates_nio = {r["candidate_id"] for r in rows if nio_rx.search(r["headline_raw"] + " " + r["primary_url"])}
    candidates_ny = {r["candidate_id"] for r in rows if ny_rx.search(r["headline_raw"] + " " + r["primary_url"])}
    assert candidates_nio == set(NIO_IDS) and candidates_ny == set(NY_IDS), "title/URL duplicate search changed; re-review manually"

    def metadata(ids):
        return [
            {"candidate_id": k, "source_row_index": int(lookup[k]["source_row_index"]),
             "original_title": lookup[k]["headline_raw"], "original_url": lookup[k]["primary_url"],
             "original_pool": lookup[k]["stage_a_pool"],
             "original_assessment_status": lookup[k]["assessment_status"],
             "original_metadata_score": int(lookup[k]["decision_news_value_score"]),
             "original_observed_date": json.loads(lookup[k]["date_role"]).get("observed_date") or None}
            for k in ids
        ]

    cases = [
        {
            "case_id": "NIO_GEELY_20260927_DUAL_EQUITY",
            "case_status": "BOUNDED_ITEM_FOUR_JUDGMENTS_DOCUMENTED_FORMAL_STAGE_A_HOLD",
            "original_source_rows": metadata(NIO_IDS),
            "source_count": 4,
            "representative_source_id": "WK26-VOL03-013",
            "event_cluster_identity": "Two legally distinct reciprocal conditional capital subscriptions in one 2026-09-27 announced agreement package; one editorial event cluster, not four cards or completed closings.",
            "economic_actions": [
                {"unit_id": "NIO_POWER_SUBSCRIPTION", "actor": "Geely subsidiary", "asset": "NIO Energy Investment (Hubei) / NIO Power", "action": "signed conditional share subscription", "conditional_stake_pct": 30.0, "post_closing_possible_floor_pct": 20.0, "consideration": "100% Yiyi Internet Technology equity plus RMB640m cash", "post_money_valuation_rmb_billion": 16.0, "completion_status": "NOT_VERIFIED_CLOSED", "future_optional_top_up": "Separate potential further RMB640m investment for 34% only if option exercised"},
                {"unit_id": "HAOHAN_SUBSCRIPTION", "actor": "NIO China", "asset": "Geely Zhejiang Haohan Energy Technology", "action": "separate signed conditional cash share subscription", "conditional_stake_pct": 10.0, "cash_consideration": "amount not in issuer release", "use_of_funds": "Haohan to buy certain charging assets from NIO", "completion_status": "NOT_VERIFIED_CLOSED"}
            ],
            "execution_credibility_gate": {"status": "PASS", "anchor_type": "execution_event_anchor", "anchor_strength": "signed_conditional_definitive_agreements", "qualified_act": "signed agreements confirmed; closing and subsequent network/vehicle roll-out not confirmed"},
            "independent_cardability_gate": {"status": "PASS", "scope": "one combined ownership-structure announcement", "full_schema_viability": "POSSIBLE_WITH_STAGE_B_EVIDENCE", "reason": "Capital ownership step is new relative to Geely/NIO 2023 cooperation and distinct from Full swap-station/charging cards; only one representative event cluster."},
            "decision_value": {"prior_metadata_score": 64, "manual_reassessed_score": 56, "decision_value_breakdown": dict(zip(SCORES, [23, 18, 0, 9, 1, 2, 2, 1])), "classification": "material_industry_signal_55_69", "scoring_reason": "Signed cross-ownership raises structural competition and potential future capacity sharing; network integration and future cashflow are conditional, not delivered output. No evidenced new technology performance or enacted policy change.", "systemic_scale_denominator": None, "denominator_gap": "No independently defensible ratio of affected exchange/charge capacity to total relevant addressable infrastructure; 16bn RMB post-money valuation is not a coverage denominator.", "technology_evidence_level": "not_applicable", "policy_stage": None, "novelty_cap_basis": "none"},
            "publication_urgency": {"status": "near_term", "reason": "Close/clearance, milestone equity adjustment and network implementation are upcoming checkpoints; 2026-09-27 agreement announcement is not fresh as of 2026-10-30."},
            "selection_route": "execution_anchor_route",
            "anchor_classes": ["execution_event_anchor", "strategic_behavior_anchor"],
            "date_role": {"representative_date": "2026-09-27", "date_basis": "NIO issuer release dated 2026-09-27 announcing entry into signed definitive agreements", "event_type": "public_announcement_of_signed_conditional_agreements", "underlying_agreement_signature_time": "NOT_INDEPENDENTLY_EXACTLY_KNOWN", "closing_date": None, "geely_counterpart_release_date": "2026-09-28"},
            "before_after": {"prior_state": "Existing 2023 commercial cooperation; NIO/Geely charging and swap operations separate, no verified reciprocal stakes in the Full baseline.", "new_verified_fact": "Conditional reciprocal capital subscriptions agreed; NIO Power 30% proposed Geely stake and Haohan 10% proposed NIO stake.", "changed_judgment": "Moves from industry cooperation to conditional capital integration, but not completed asset-transfer/network integration.", "uncertainty_resolved": "Parties, two instruments, proposed stakes, RMB640m cash component, RMB16bn post-money scope, and announcement date.", "remaining_uncertainty": "Regulatory clearance, definitive close, exact Haohan cash price/asset list, Yiyi valuation, option exercise, actual joint network implementation.", "incremental_information": "New binding-stage ownership terms versus 2023 business cooperation; prior cards concern other assets/counterparties.", "baseline_expectation_changed": True, "decision_relevance": "Cross-platform battery swapping/charging ownership and future capital allocation; do not assume battery demand contracted or realized."},
            "related_prepass": {"status": "PASS_BOUNDED_SOURCE_IDENTITY_NOT_NATIVE_STRICT", "same_event_source_ids": NIO_IDS, "same_event_checked_in_full_1676": True, "earliest_same_event_announcement": "2026-09-27", "same_event_older_full_card_found": False, "lexical_candidate_batch_check": "FOUR_SOURCE_ID_MATCHES_ONLY_NON_SEMANTIC", "baseline_comparisons": [
                {"card_id": "2026-08-12_CN_01", "relation": "new_unrelated_event", "reason": "Wuhan 36-station handover, not Geely equity subscriptions"},
                {"card_id": "GL05", "relation": "new_unrelated_event", "reason": "NIO-BYD charging collaboration, different counterparty"},
                {"card_id": "R8_02", "relation": "new_unrelated_event", "reason": "Geely technology launch, different instrument"},
                {"card_id": "R4_12", "relation": "new_unrelated_event", "reason": "Industry discussion of swapping versus charging"},
                {"card_id": "2026-04-27_CN_10", "relation": "new_unrelated_event", "reason": "Geely 'Haohan' vehicle hybrid SiC product is NOT corporate Haohan Energy charging equity"}
            ], "unresolved_scope": "Semantic review of every other pending 1,280 Source ID and full Stage 0.0C event universe remains incomplete; no formal PASS."},
            "original_headline_corrections": ["'Geely has bought 30%' and 'NIO sells' imply closed deal; issuer states closing conditional.", "'RMB16bn' is approximate post-money NIO Power valuation, not cash proceeds.", "NIO 10% Haohan transaction is a separate subscription, not the same 30% stake.", "Future 34% requires an unexercised RMB640m option; 20% is conditional downside floor, not base deal."],
            "source_owner_evidence": [
                {"source_owner": "NIO Inc. investor relations", "role": "issuer_primary_for_both_transactions", "url": "https://ir.nio.com/news-releases/news-release-details/nio-announces-definitive-agreements-strategic-transaction-geely", "locator": "2026-09-27 release, paragraphs on stake, conditions, valuation, option and Haohan subscription"},
                {"source_owner": "Geely Holding Group", "role": "counterparty_first_party_independent_owner", "url": "https://newsroom.geely.com/geely-holding-group-nio-cooperation-battery-swapping-charging", "locator": "2026-09-28 announcement, background 2023 and both proposed stakes"}
            ],
            "stage_b_evidence_needed": ["Confirm any regulatory/transaction closing after 2026-09-27; never imply closed without it.", "Separate valuation, transferred Yiyi interest, initial cash and unexercised option; identify undisclosed Haohan cash price.", "Check 2023 partnership as predecessor before assigning Related; distinguish legal change from planned technical rollout.", "Independently support market consequence with subsequent issuer filings, not announcement ambition alone."]
        },
        {
            "case_id": "NYSERDA_BULK_BESS_AWARDS_20260923",
            "case_status": "BOUNDED_ITEM_FOUR_JUDGMENTS_DOCUMENTED_FORMAL_STAGE_A_HOLD",
            "original_source_rows": metadata(NY_IDS),
            "source_count": 1,
            "representative_source_id": NY_IDS[0],
            "event_cluster_identity": "One NYSERDA inaugural 2025 ISC solicitation result announced on 2026-09-23: 8 executed project incentive contracts. Eight project assets preserved separately; NOT eight automatic editorial cards.",
            "economic_actions": [{"unit_id": f"PROJECT_{i + 1:02d}", **a, "derived_mwh": a["mw"] * a["hours"], "action": "index_storage_credit_contract_awarded", "operational_status": "NOT_COD"} for i, a in enumerate(ASSETS)],
            "portfolio_controls": {"contracted_project_count": 8, "total_mw": 950, "derived_mwh_not_official_portfolio_total": sum(a["mw"] * a["hours"] for a in ASSETS), "award_project_duration_min_h": 4, "award_project_duration_max_h": 8, "issuing_program": "NYSERDA 2025 Index Storage Credit solicitation", "expected_ess_only_private_investment_usd": "more_than_1.6_billion_forecast", "combined_storage_plus_13_renewables_usd": "more_than_3.7_billion_forecast_NOT_ESS_ONLY", "ess_only_projected_jobs": "over_500", "combined_21_projected_jobs": "over_1000", "bids_project_count": 46, "bids_mw_approx": 6000, "state_2030_storage_goal_mw": 6000, "aggregate_contract_payments": "not_yet_started_before_operational_COD"},
            "execution_credibility_gate": {"status": "PASS", "anchor_type": "execution_event_anchor", "anchor_strength": "agency_confirms_eight_executed_incentive_contracts", "qualified_act": "contract award/signed incentive contracts; not energized ESS, COD or subsidy disbursement"},
            "independent_cardability_gate": {"status": "PASS", "scope": "one program award decision with eight distinct project assets", "full_schema_viability": "POSSIBLE_WITH_STAGE_B_EVIDENCE", "reason": "950MW signed portfolio awards change development economics; none is KCE NY6 or a 2023 operating event. Project-level eight separate cards not justified automatically."},
            "decision_value": {"prior_metadata_score": 64, "manual_reassessed_score": 66, "decision_value_breakdown": dict(zip(SCORES, [19, 23, 0, 9, 8, 3, 3, 1])), "classification": "material_industry_signal_55_69", "scoring_reason": "Eight executed program contracts materially improve incentive-supported storage pipeline, not realized supply; 950MW / publicly stated 6GW 2030 goal supports a nonzero systemic denominator.", "systemic_scale_denominator": {"amount_mw": 6000, "basis": "New York 2030 storage target", "ratio_contract_mw_to_state_goal": 0.15833333333333333, "ratio_qualified": "contracted_project_pipeline_vs_future_policy_goal_not_existing_installed_share"}, "denominator_gap": None, "technology_evidence_level": "not_applicable", "policy_stage": None, "novelty_cap_basis": "none"},
            "publication_urgency": {"status": "monitor", "reason": "Contract award announced in September; COD/permits and payment conditions stretch to 2030 and need tracking, not imminent operation."},
            "selection_route": "execution_anchor_route",
            "anchor_classes": ["execution_event_anchor", "data_financial_anchor"],
            "date_role": {"representative_date": "2026-09-23", "date_basis": "NYSERDA dated first public announcement of awards", "event_type": "public_contract_award_announcement", "underlying_individual_contract_execution_dates": "NOT_IDENTIFIED", "expected_COD": "no_later_than_2030_target_not_verified"},
            "before_after": {"prior_state": "New York 6GW 2030 ESS policy and earlier installed KCE NY6 project; first 2025 ISC competition not previously published as an eight-project contracted list in Full.", "new_verified_fact": "Eight named signed 4–8h ESS contracts, 950MW; forecast $1.6bn+ ESS-only private investment, none operational by award.", "changed_judgment": "Competitive storage procurement moved from solicitation/goal to contracted incentives, with milestones and future risks.", "uncertainty_resolved": "Eight project names/counties/capacities/durations, signed credit status, dollar-scope split, NY5/NY37 site differentiation.", "remaining_uncertainty": "Individual contract execution dates, exact per-MW incentive economics and owner-specific financing, permits/interconnection/COD, actual jobs/investment, progress of other six developers.", "incremental_information": "NYSERDA program award portfolio is a different instrument, eight assets, and economic stage from prior operating NY6 and corporate KCE capital process.", "baseline_expectation_changed": True, "decision_relevance": "Supportable future 4–8h Li-ion storage project pipeline and ratepayer credit exposure; neither installed MW nor actual ESS equipment orders proven."},
            "related_prepass": {"status": "PASS_BOUNDED_SOURCE_IDENTITY_NOT_NATIVE_STRICT", "same_event_source_ids": NY_IDS, "same_event_checked_in_full_1676": True, "earliest_same_event_announcement": "2026-09-23", "same_event_older_full_card_found": False, "lexical_candidate_batch_check": "ONE_NYSERDA_ESS_SOURCE_ID_MATCH_ONLY_NON_SEMANTIC", "baseline_comparisons": [
                {"card_id": "R15_02", "relation": "new_unrelated_event", "reason": "March 2026 Full item explicitly describes KCE NY6 20MW/45.6MWh operating since 2023, not KCE NY5 (94MW New Paltz) or KCE NY37 (150MW Manorville) 2026 incentive awards."},
                {"card_id": "2026-04-22_US_02", "relation": "new_unrelated_event", "reason": "SK/Key Capture Energy corporate financing exploration, not project-level incentive contract award"},
                {"card_id": "2026-04-24_KR_03", "relation": "new_unrelated_event", "reason": "SK/KCE capital options not NYSERDA executed award contracts"}
            ], "unresolved_scope": "Full-scale semantic sweep and final 0.0C/Stage A lineage validation remain pending; one NYSERDA primary portfolio owner does not imply final source-diversity PASS."},
            "site_identity": {"KCE_NY_6": {"operating_card_id": "R15_02", "site": "Blasdell, Erie County, near Buffalo", "mw": 20, "mwh": 45.6, "reported_actual_open_year": 2023, "source_url": "https://www.theguru.co.kr/news/article.html?no=99949", "full_card_date": "2026-03-31", "baseline_date_qc_flag": "2023 asset opening re-reported in 2026; potential stale-first-event problem in Full; do not change Full without approval"}, "KCE_NY_5": {"site": "New Paltz, Ulster County", "bid_mw": 94, "bid_hours": 4, "interconnection_queue": "967", "proposed_in_service_date": "2030-02-01"}, "KCE_NY_37": {"site": "Manorville, Suffolk County", "contracted_mw": 150, "duration_hours": 4, "future_planned_construction": 2028, "future_planned_COD": 2030}},
            "original_headline_corrections": ["Selected/contracted 950MW is not installed 950MW or guarantee of operation.", "ESS-only forecast private investment is over $1.6bn, not the $3.7bn ESS+13 renewables combined figure.", "NYSERDA payments start only after COD plus permits and local approvals.", "KCE NY6 (operating since 2023), NY5 and NY37 are different project IDs/assets.", "NYSERDA 2025 solicitation is the program name; announcement is 2026-09-23."],
            "source_owner_evidence": [
                {"source_owner": "NYSERDA", "role": "single_primary_public_authority_for_portfolio", "url": "https://www.nyserda.ny.gov/About/Newsroom/2026-Announcements/2026-09-23-NYSERDA-Awards-Eight-Bulk-Energy-Storage-Projects-13-LSR-Projects", "locator": "2026-09-23 release, eight awards/950MW/payment delay/13 renewables combined scope"},
                {"source_owner": "NYSERDA", "role": "same_owner_fact_sheet_not_independent_corroboration", "url": "https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Energy-Storage/Bulk-Energy-Storage-Factsheet.pdf", "locator": "September 2026 two-page fact sheet: 8 names, MW, duration, $1.6bn ESS-only, 500+ jobs"},
                {"source_owner": "Key Capture Energy", "role": "independent_owner_for_two_of_eight_assets_only", "url": "https://keycaptureenergy.com/kceny37/", "locator": "KCE NY37 site in Manorville; confirms operating NY6 separately"},
                {"source_owner": "NYSERDA / Key Capture Energy public bidder submission", "role": "project_identity_for_KCE_NY5_not_whole_portfolio", "url": "https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Energy-Storage/Bulk-Storage-Incentives/KCE-NY-5_Att_B_Public_Project_Summary.pdf", "locator": "KCE NY5 94MW/4h New Paltz, intended COD 2030, queue 967"},
                {"source_owner": "The Guru", "role": "existing_Full_R15_02_original_article_not_2026_new_execution", "url": "https://www.theguru.co.kr/news/article.html?no=99949", "locator": "2026-03-31 article identifies NY6 operating from 2023 at Blasdell"}
            ],
            "stage_b_evidence_needed": ["Confirm contract execution dates and incentive instrument economics if asserted; agency statement is enough for contract existence but not for undisclosed prices.", "Maintain separate eight project asset entries; check each developer permit, interconnection and COD evidence before operational statements.", "Get additional independent owners for rest of portfolio or record single-primary-authority exception explicitly downstream.", "Correctly separate $1.6bn ESS-only projected investment from $3.7bn combined ESS+13 renewable estimate.", "Flag R15_02 historical date problem in separate authorized Full QC, without mutating Full or Related now."]
        }
    ]

    for case in cases:
        scores = case["decision_value"]["decision_value_breakdown"]
        assert list(scores) == SCORES
        assert all(isinstance(scores[k], int) and 0 <= scores[k] <= upper for k, upper in zip(SCORES, MAX))
        assert sum(scores.values()) == case["decision_value"]["manual_reassessed_score"]
        assert scores["technology_performance_safety"] == 0
        assert scores["systemic_scale"] <= 2 or case["decision_value"]["systemic_scale_denominator"] is not None
        assert case["execution_credibility_gate"]["status"] == "PASS"
        assert case["independent_cardability_gate"]["status"] == "PASS"
        assert case["case_status"].endswith("FORMAL_STAGE_A_HOLD")

    artifact = {
        "artifact_type": "STAGE_A_0_1P_BOUNDED_ITEM_RESEARCH_COMPANION_NOT_MACHINE_PASS",
        "created_date_kst": "2026-10-30",
        "source_prompt_file": PROMPT_REL,
        "source_prompt_version": "STAGE_A_INTEGRATED_SELECTOR_V4_20260901",
        "promotion_prompt": "docs/llm_prompts/v1/14_PROMPT_0_1P_Review_Pool_Promotion.md",
        "run_scope": "Two pre-existing unresolved case packages / five original Source IDs; no new Round; no provisional strict_passed_spec emitted",
        "gate_status": "HOLD_NATIVE_STAGE_A_NOT_RUN",
        "stage_transition_authorized": False,
        "baseline": {"original_source_rows": 1330, "original_sha256": SOURCE_SHA256, "full_cards": 1676, "full_git_blob": FULL_GIT_BLOB, "formal_prior_0_1P_reviewed_ids": 45, "formal_unadjudicated_source_ids_before": 1285, "formal_unadjudicated_source_ids_after": 1285, "bounded_newly_researched_original_ids": 5, "completely_unresearched_for_four_judgment_ids_remaining_at_most": 1280, "no_loss_original_row_or_id": True, "review_pool_status_mutated": False},
        "stage_a_item_judgment_status": "MANUAL_EVIDENCE_BOUNDED_FOR_TWO_EVENTS_NOT_VALIDATED_PROMOTION",
        "full_source_universe_warning": "Do not build a two-event pseudo Stage A PASS or backfill untouched 1,285 lines with fabricated decisions; native Stage A requires all 1,330 accounted with valid upstream 0.0D/0.0C and current validators.",
        "cases": cases,
        "source_row_disposition_delta": [{"candidate_id": s["candidate_id"], "parent_case_id": case["case_id"], "source_role": "representative" if s["candidate_id"] == case["representative_source_id"] else "same_event_support_observation", "original_pool_preserved": "candidate_review_pool", "bounded_four_judgments": "documented_at_case_level", "formal_0_1P_status": "HOLD_NOT_IN_VALIDATED_STRICT_BUCKET", "semantic_dedup_applied_to_source_id": False} for case in cases for s in case["original_source_rows"]],
        "native_validation": {"stage_artifact_contract_check_A": "NOT_EXECUTED_INCOMPLETE_TOP_LEVEL_STAGE_A", "stage_lineage_contract_check_stage_a": "NOT_EXECUTED_INCOMPLETE_UPSTREAM_UNIVERSE", "not_represented_as_pass": True},
        "change_impact": {"github_main": "unchanged", "full_lean_related": "unchanged", "existing_7_drafts": "preserved", "PR_386": "unchanged", "production": "unchanged", "revolution_master_downstream": "unchanged"},
        "next_single_bottleneck": "Resume evidence-bound four-judgment screening across unassessed Source IDs beyond these five, including other >=60 review candidates and nontraditional WATCH; complete upstream full-universe Stage A/native envelope before promotions."
    }
    original_id_set = set(all_ids)
    assert len(artifact["source_row_disposition_delta"]) == 5
    assert {r["candidate_id"] for r in artifact["source_row_disposition_delta"]} == set(selected_ids)
    assert set(selected_ids) <= original_id_set
    assert sum(a["mw"] for a in ASSETS) == 950
    assert sum(a["mw"] * a["hours"] for a in ASSETS) == 4360
    out_path = HERE / "STAGE_A_NIO_NYSERDA_BOUNDED_0_1P_REVIEW_20261030.json"
    data = json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    unchanged_write(out_path, data)
    receipt = {
        "status": "PASS_BOUNDED_ARTIFACT_QC_NOT_NATIVE_STAGE_A_PASS",
        "scope": "original 1,330 read-only; four NIO/one NYSERDA source IDs; two event packages; 10 underlying units",
        "baseline_source_sha256": digest(args.source_ledger),
        "full_git_blob": full_blob,
        "baseline_full_count": len(cards),
        "original_source_count": len(rows),
        "original_source_unique_count": len(original_id_set),
        "original_blank_cluster_count": sum(1 for r in rows if not r["economic_event_cluster_id"]),
        "new_0_1P_source_bounded_review_count": len(selected_ids),
        "all_source_ids_preserved_unchanged": True,
        "output_source_id_delta_equals_input_selected_ids": True,
        "original_pool_unchanged": True,
        "case_count": len(cases),
        "economic_units_count": sum(len(c["economic_actions"]) for c in cases),
        "ess_contracted_mw_check": sum(a["mw"] for a in ASSETS),
        "ess_derived_mwh_check": sum(a["mw"] * a["hours"] for a in ASSETS),
        "manual_scores_math_and_caps": "PASS",
        "current_batch_title_url_lexical_matches": {"NIO_Geely": sorted(candidates_nio), "NYSERDA_ESS": sorted(candidates_ny)},
        "cross_batch_semantic_exhaustiveness": "NOT_PROVEN",
        "native_stage_a_contract": "NOT_EXECUTED",
        "native_stage_a_lineage": "NOT_EXECUTED",
        "formal_stage_a_promotion_count": 0,
        "formal_stage_a_unadjudicated_count": 1285,
        "new_artifact_sha256": hashlib.sha256(data.encode("utf-8")).hexdigest()
    }
    unchanged_write(HERE / "STAGE_A_NIO_NYSERDA_BOUNDED_REVIEW_QC_20261030.json", json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

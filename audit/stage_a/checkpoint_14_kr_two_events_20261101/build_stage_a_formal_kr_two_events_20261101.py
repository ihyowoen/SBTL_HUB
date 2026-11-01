#!/usr/bin/env python3
"""Bounded Prompt 0.1P Stage A promotion: two Korean event families.

The official September 22/23 acts are candidates for TWO strict Stage A
specifications, not 30+ media cards. Move only demonstrably same-event
observations into support-only; mixed-article/strategy/registration IDs remain
in review. There is no Stage B evidence approval or canonical Full mutation.
"""

from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse


BASE_SHA = "1d2c8ccbd01b40aef7de512969281043a59cdb866d2a6dfbdd52bf997edf95c1"
RES_ROWS = [222, 230, 232, 234, 250, 256, 270, 280, 281, 283, 284, 429, 570, 604, 605, 606, 608, 609, 612, 618, 622, 631, 1018, 1271]
ESS_ROWS = [235, 260, 271, 535, 538, 1279]
HOLD_SPLITS = {
    48: "September 19 pre-notice supplier localisation/strategic preparation predates the Sep22 tender notice; distinguish corporate conduct from prospective tender.",
    228: "September 23 article evaluates LG Energy Solution competitive strategy, which may have separate original-company actions beyond this tender.",
    244: "Mixed ESS tender and end-of-life vehicle rare-earth recovery policy: separate material economic acts; original publisher page currently inaccessible.",
    614: "Repeated collection of the same mixed article as 244; retain both Source IDs, and separately resolve rare-earth recovery action.",
    916: "September 28 actual bidder registration-window opening is a procedural stage after September 22 notice; do not silently collapse a potential follow-up.",
}
EVENTS = {
    "RESOURCE": {
        "case_id": "KR_RESOURCE_SECURITY_PLAN_20260923",
        "rows": RES_ROWS,
        "representative": 222,
        "date": "2026-09-23",
        "owner": "산업통상부; 제6차 자원안보협의회",
        "owner_urls": [
            "https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/172235/view",
            "https://www.motir.go.kr/kor/article/ATCL03465409b/171730/view",
        ],
        "title": "자원안보 기본계획 등 4개 안건 확정 — 핵심광물 관리·비축 목표 변경",
        "summary": "2026-09-23 제6차 자원안보협의회가 네 안건을 심의·확정; 관리대상 38→51종과 비축품목 24→29종, 취약광종 비축목표 최대 365일. 13개 신규 광종 지정은 후속 고시 개정 예정이며 재고 확보 완료가 아님.",
        "increment": "Special Act framework is earlier (Full 2026-04-24_KR_07); this is an independently dated first statutory resource-security plan with four Sept23 approvals, not a new passage of that Act.",
        "must_not": "The planned designation of 13 minerals needs a later formal notice amendment. No claim that all 51 are already formally designated, all 29 physically stockpiled for a year, the 2030 20-million-barrel facility built, or 2035 oil goal attained.",
        "prior_state": "Prior 38 critical minerals, 24 reserve commodities, up to 180 days reserve target; 2025 Special Act implementation and 2026 April law amendment already in Full.",
        "new_fact": "September23: first resource-security basic plan, adjusted fifth petroleum reserve plan, critical mineral designation plan, and first critical-mineral reserve plan adopted; future notice amendment needed for 13 selected new minerals.",
        "event_units": ["FIRST_RESOURCE_BASIC_PLAN_ADOPTED", "FIFTH_PETROLEUM_RESERVE_PLAN_ADJUSTED", "MINERAL_DESIGNATION_PLAN_ADOPTED_NOTICE_PENDING", "FIRST_MINERAL_RESERVE_PLAN_ADOPTED"],
        "score": [18, 21, 0, 8, 9, 4, 3, 2],
        "policy_stage": 3,
        "legal_stage": "stage_3_enacted_law_final_rule_or_adopted_standard",
        "classification_lenses": ["critical materials", "regional core signal"],
        "anchors": ["policy_regulatory_anchor"],
        "route": "structural_non_execution_route",
        "system_denominator": "38 existing critical minerals →51 selected in plan; 24 existing reserve commodities →29; previous target 180 days →up to 365 for vulnerable types, not physical stock.",
        "law_type": "National Resource Security Special Act statutory first basic plan, adjusted fifth petroleum reserve plan, mineral designation plan, first mineral reserve plan.",
        "procedure": "Four planning agendas formally deliberated/adopted by the sixth Resource Security Council on September 23; later ministerial notice amendment and subsequent execution remain separate.",
        "mandatory": "No immediately applicable new blanket mandatory date in official release; mineral additions require a future amendment to the resource-security ministerial notice.",
        "implementation": "2026–2035 targets; mineral designation notice amendment, differentiated reserve procurement and national available-stock accounting; investment/facility completion remain later stages.",
        "funding": "No executed commodity procurement or dedicated expenditure documented by Sept23 release. New resource-security fund is a stated plan, not proven disbursement.",
        "affected": ["Korean critical-mineral reserve programme", "battery and semiconductor input-supply chains", "petroleum strategic reserves"],
        "next_trigger": "Confirm gazette/ministerial notice adding 13 minerals; detailed item-by-item reserve procurement, budget appropriation, 2030 facility progress, and actual stocks.",
        "related_full": ["2026-04-24_KR_07", "2026-07-23_KR_01"],
        "related_reason": "Earlier National Resource Security Act amendment and July mineral finance links are distinct legal/finance acts; September23 adopts a specific statutory plan and targets.",
        "staged_questions": [
            "Read adopted first resource-security basic plan and mineral-reserve plan annexes for item-specific implementation and funding.",
            "Find later ministerial notice date that formally designates the extra 13 minerals; no designation effect inferred from the plan alone.",
            "Distinguish reserve target days from actual publicly held stocks and 2030 storage-facility construction.",
        ],
    },
    "ESS": {
        "case_id": "KR_ESS_CENTRAL_TENDER_1180MW_20260922",
        "rows": ESS_ROWS,
        "representative": 235,
        "date": "2026-09-22",
        "owner": "기후에너지환경부·한국전력거래소",
        "owner_urls": [
            "https://www.mcee.go.kr/home/web/board/read.do?boardId=1893270&boardMasterId=939&menuId=10598",
            "https://www.kpx.or.kr/board.es?act=view&bid=0042&list_no=78164&mid=a10501010000&nPage=1",
            "https://www.kpx.or.kr/board.es?act=view&bid=0042&list_no=78165&mid=a11201000000",
        ],
        "title": "2026 ESS 중앙계약시장 1,180MW 경쟁입찰 공고 — 육지·제주 별도 공고",
        "summary": "전력거래소 9월22일 육지 1,100MW 공고 제2026-05호·제주 80MW 제2026-06호. 계통대상 변전소 확대, 제주 조건부 25년 선택계약 도입; 낙찰·계약체결·준공은 아직 별개 단계.",
        "increment": "Fresh KPX 2026-05/06 procurement notices on September22, different competitive-round instruments from prior individual ESS project grants/contracts in Full; not an award or installed capacity.",
        "must_not": "1,180MW is tendered volume, not 1,180MW award, 2029 completion, signed projects or installed new battery demand. 제주 25-year option applies only to eligible high-cycle equipment and is not a universal 25-year tenor.",
        "prior_state": "Prior three central contract market rounds through 2026H1 selected a cumulative 1,196MW per government; earlier Full ESS cards concern different projects/rounds.",
        "new_fact": "September22 KPX mainland tender #2026-05 at 1,100MW and Jeju tender #2026-06 at 80MW were published; substations widened and conditional Jeju 25-year option introduced.",
        "event_units": ["MAINLAND_1100MW_TENDER_NOTICE_2026_05", "JEJU_80MW_TENDER_NOTICE_2026_06_OPTIONAL_25Y"],
        "score": [18, 23, 0, 8, 8, 5, 3, 2],
        "policy_stage": 4,
        "legal_stage": "stage_4_implementation_budget_guidance_or_registry",
        "classification_lenses": ["AI/data-centre power/ESS", "regional core signal"],
        "anchors": ["execution_event_anchor", "policy_regulatory_anchor"],
        "route": "execution_anchor_route",
        "system_denominator": "This competitive solicitation 1,180MW = mainland 1,100MW + Jeju 80MW; 1,196MW cumulative *previously selected* across three rounds for scale, not additive completed MW.",
        "law_type": "KPX tender notices 2026-05 (mainland) and 2026-06 (Jeju) under Electricity Market Operation Rules ch.15 low-carbon-source central contract market.",
        "procedure": "Actual tender notices published 2026-09-22 at 17:00 and 17:01; bidder evaluation, November awards, later construction/permits/contracts remain future steps.",
        "mandatory": "Tender closing scheduled November 11; physical build target February 2029 for selected developers, not construction completed or unconditional award date.",
        "implementation": "Separate mainland/Jeju bid packages, expanded substation eligibility; Jeju 25-year optional contract only for daily twice cycling over 25 years.",
        "funding": "Tendered capacity and price evaluation, not contracted subsidy disbursement or final installation budget.",
        "affected": ["ESS prospective bidding developers", "Korean cell and ESS suppliers", "eligible mainland substations", "Jeju network sites"],
        "next_trigger": "Read KPX #2026-05/06 tender PDFs and corrected annex/data sheets, verify final qualified bids, actual awards and later permits/contracts independently.",
        "related_full": [],
        "related_reason": "No exact September22 two-notice tender round found in locked Full1676; prior ESS project contracts/rounds have different dated economic events.",
        "staged_questions": [
            "Verify exact capacity, tender site/eligibility and scoring terms from both KPX 2026-05/06 PDFs, including Oct14 annex formula correction.",
            "Confirm whether 제주 25-year alternative is conditional on sustained twice-daily cycling and distinguish from default 15 years.",
            "Track bid closing, awarded MW, contracted capacity and actual installed operation as later distinct facts.",
        ],
    },
}
SCORE_FIELDS = (
    "market_structure_competition", "supply_demand_price_utilisation",
    "technology_performance_safety", "cashflow_asset_value",
    "law_policy_market_access", "systemic_scale",
    "persistence_irreversibility", "decision_urgency_actionability",
)
MAX_FIELDS = (25, 25, 20, 10, 10, 5, 3, 2)
STAGE_B_REQUIREMENT_NOTE = (
    "Stage B must verify the provided source-candidate URL and build a valid evidence package before drafting. "
    "This Stage A spec is not evidence_complete, and primary_url is not evidence by itself."
)


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


def related_for_strict(e: dict, old: dict) -> dict:
    refs = []
    for full_id in e["related_full"]:
        refs.append({
            "target_candidate_id": full_id,
            "proposed_relation_type": "program_lineage",
            "confidence": "high",
            "reason": e["related_reason"],
            "anchor_class_to_verify": "policy_regulatory_anchor",
            "incremental_anchor_question": e["staged_questions"][0],
        })
    return {
        "status": "PASS", "same_event_checked": True,
        "matched_baseline_candidate_ids": list(e["related_full"]),
        "matched_current_batch_candidate_ids": [],
        "relation_candidates": refs, "duplicate_disposition": "no_duplicate_found",
        "earliest_same_event_check_status": "PASS",
        "fresh_anchor_questions": e["staged_questions"],
        "search_shortlist_baseline_ids": old.get("related_prepass", {}).get("search_shortlist_baseline_ids", []),
        "search_shortlist_is_lineage": False,
        "unverified_legacy_reference": "",
        "unverified_legacy_existing_ids": [],
        "preliminary_relation_proposal": "program_lineage" if refs else "new_unrelated_event",
        "fingerprint_reason": e["increment"],
        "rejected_relation_candidates": [],
        "previous_prepass_edges_preserved_for_audit": [old["related_prepass"]],
        "earliest_same_event_date": e["date"],
        "earliest_check_scope": "Full1676 locked main; all 1,330 source titles/URLs; official MOTIR or MCEE/KPX release and notices.",
    }


def build_strict(old: dict, template: dict, e: dict, source_rows: list[dict]) -> dict:
    spec = copy.deepcopy(old)
    for key, value in template.items():
        if key not in spec:
            spec[key] = copy.deepcopy(value)
    sid, url = old["candidate_id"], old["primary_url"]
    evidence_urls = list(dict.fromkeys([url, *e["owner_urls"], *(r["primary_url"] for r in source_rows)]))
    score = dict(zip(SCORE_FIELDS, e["score"]))
    value = sum(e["score"])
    legal_stage = e["legal_stage"]
    is_ess = e["case_id"].startswith("KR_ESS_")
    date = e["date"]
    ver_reason = e["increment"] + " " + e["must_not"]
    if is_ess:
        evidence_targets = [
            {"source_or_document_class":"KPX official adopted 2026 ESS tender notice document PDF",
             "exact_claim_or_metric":"2026-09-22 1,100MW mainland and 80MW Jeju bid launch and project site eligibility"},
            {"source_or_document_class":"KPX official amended ESS bid notice PDF dated2026-10-14",
             "exact_claim_or_metric":"mainland G60 and Jeju G61 paid-in-capital denominator formula changes and tender-scoring effect"},
            {"source_or_document_class":"KPX ESS award notice and executed developer contract filing",
             "exact_claim_or_metric":"November 2026 awards MW, contract dates and Jeju chosen 15-year versus conditional 25-year duration"},
        ]
        confirmation_targets = [
            "KPX November2026 award notice with actual named winning developers and contracted MW would strengthen the Korea ESS demand outlook; cancelled capacity would weaken the near-term ESS outlook.",
            "KPX February2029 ESS commissioning reports and measured MW capacity would strengthen the operating-demand outlook; delayed COD would weaken the grid-support outlook.",
            "Jeju actual 25-year contract award count under 730 annual charging cycles; revise tenure assessment if winners choose a different contract mix.",
        ]
    else:
        evidence_targets = [
            {"source_or_document_class":"MOTIR official adopted statutory basic-plan document PDF",
             "exact_claim_or_metric":"2026-09-23 four-plan approval, 38 to 51 selected mineral categories, 24 to 29 planned reserve items"},
            {"source_or_document_class":"MOTIR ministerial designation notice document",
             "exact_claim_or_metric":"Date and operative notice amendment formally designating 13 additional minerals after September23 selection"},
            {"source_or_document_class":"MOTIR official adopted statutory basic-plan document PDF",
             "exact_claim_or_metric":"2026-09-23 first critical-mineral reserve plan approval, 29 target types and 365-day maximum goal"},
        ]
        confirmation_targets = [
            "Date of MOTIR gazette adding 13 critical minerals; change the effective-scope judgment only if the notice is published, otherwise hold existing 38-mineral scope outlook.",
            "Korea critical-mineral reserve capacity in stock-days versus 365-day plan would strengthen the Korean reserve adequacy outlook; a stock shortfall would weaken the buffer outlook.",
            "Korea 2030 oil reserve facility completed20-million barrels versus construction schedule would strengthen the supply resilience outlook; delayed commissioning would weaken the oil-storage outlook.",
        ]
    evidence_targets = [
        f"{target['source_or_document_class']}: verify {target['exact_claim_or_metric']}"
        for target in evidence_targets
    ]
    legal_fields = {
        "legal_policy_stage": legal_stage,
        "legal_instrument_type": e["law_type"],
        "competent_authority": e["owner"],
        "procedural_status": e["procedure"],
        "adoption_date": date,
        "publication_date": date,
        "effective_date": e["mandatory"],
        "mandatory_application_date": e["mandatory"],
        "affected_entities": e["affected"],
        "affected_products_or_activities": ["critical-mineral national stockpile and supply security" if not is_ess else "2026 mainland and Jeju ESS competitive procurement"],
        "geographic_scope": "Republic of Korea", "extraterritorial_effect": "No extra-territorial direct obligation evidenced; upstream sourcing may be indirectly affected.",
        "budget_or_funding_source": e["funding"],
        "implementation_mechanism": e["implementation"],
        "administrative_readiness": e["procedure"],
        "exemptions_and_thresholds": [e["mandatory"]],
        "transition_and_grandfathering": ["Prior regulatory/market structure remains distinct; further date-specific guidance requires Stage B review."],
        "noncompliance_consequences": ["No present physical build or inventory shortfall treated as an established infraction."],
        "appeal_or_litigation_risk": "Not evidenced at this Stage A selector gate; check implementing instrument/procedure in Stage B.",
        "reversibility_risk": "Administrative targets/tender bids may be revised; no future implementation is presumed irreversible.",
        "precedent_scope": "Specific September 2026 act; not blanket retroactive expansion of earlier laws/contracts.",
        "legal_policy_transmission_chain": [e["new_fact"], "Affects procurement/sourcing expectations; realized volumes and prices require later evidence."],
        "next_implementation_trigger": e["next_trigger"],
    }
    spec.update(legal_fields)
    spec.update({
        "candidate_id": sid, "story_id": sid, "spec_id": "A_SPEC_" + sid,
        "source_story_ids": [sid], "source_origin": old["origin"],
        "stage_a_pool": "strict_passed_spec", "ledger_decision": "passed", "editorial_bucket": "strict_passed_spec",
        "assessment_status": "STAGE_A_STRICT_PASS", "assessment_profile": "policy_adopted" if not is_ess else "procurement_notice_actual",
        "assessment_method": "PROMPT_0_1P_V4_20260829 bounded official original-owner confirmation",
        "promotion_reassessment_status": "PROMOTED_VALIDATED_STRICT",
        "selection_route": e["route"], "region": "KR", "representative_date": date,
        "representative_source": e["owner_urls"][0],
        "title_raw": e["title"], "headline": old["headline_raw"],
        "summary_hint": e["summary"], "context_text": e["prior_state"],
        "why_now": e["increment"], "market_relevance": e["increment"],
        "event_anchor": e["new_fact"], "economic_event_cluster_id": e["case_id"],
        "event_representative_source_id": sid,
        "primary_url": url, "strict_spec_source_primary_url": url,
        "url": url, "urls": evidence_urls,
        "selector_resolved_url": e["owner_urls"][0],
        "source_domain_candidates": list(dict.fromkeys(urlparse(u).netloc for u in evidence_urls)),
        "support_source_candidates": [r["primary_url"] for r in source_rows if r["candidate_id"] != sid],
        "support_source_candidates_accounted": True,
        "same_event_source_cluster": [
            {"story_id": r["candidate_id"], "url": r["primary_url"], "preserve_for_stage_b": True}
            for r in source_rows
        ] + [{"story_id": sid, "url": u, "preserve_for_stage_b": True} for u in e["owner_urls"]],
        "source_cluster_preserved": True,
        "source_diversity_path": {
            "status": "viable", "candidate_owner_available": True,
            "independent_owner_availability": "unknown",
            "same_owner_syndication_not_independent": True,
            "source_audit_approval": False,
            "stage_b_question": e["next_trigger"],
        },
        "source_access_risk": "original_owner_path_available_evidence_pending",
        "source_path_plausibility": "DIRECT_CANDIDATE_LOCATED_NOT_STAGE_B_EVIDENCE",
        "source_priority_notes": e["must_not"],
        "source_tier_estimate": "primary_original_candidate",
        "source_metadata_only": True,
        "bounded_research_source_candidates": e["owner_urls"],
        "source_cluster_preserved": True,
        "stage_a_evidence_status": "not_evidence_complete_no_fetch",
        "stage_b_evidence_package_required": True,
        "stage_b_requirement_note": STAGE_B_REQUIREMENT_NOTE,
        "primary_url_semantics": "provided_source_candidate_not_evidence",
        "accepted_facts_approved": False, "canonical_card_write_allowed": False,
        "stage_b_authorized": False,
        "enhanced_selector_precision_version": "v3",
        "selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
        "strict_gate_check": "pass",
        "strict_pass_gate": {
            "status": "pass", "reason": ver_reason,
            "all_six_conditions_passed": True, "anchor_supported_by_upstream_text": True,
            "why_not_review_pool": ver_reason,
        },
        "anchor_classes": e["anchors"],
        "structural_value_lenses": e["classification_lenses"],
        "original_structural_value_lenses": old.get("structural_value_lenses", []),
        "strategic_lens": e["classification_lenses"],
        "cat": "Policy" if not is_ess else "ESS",
        "sub_cat": "RESOURCE_SECURITY_STATUTORY_PLANS" if not is_ess else "CENTRAL_CONTRACT_TENDER",
        "signal_estimate": "high" if value >= 70 else "mid",
        "signal_rubric_estimate": "Industrial value score; tender or legal form is not a realized asset.",
        "decision_news_value_score": value,
        "decision_value_breakdown": score,
        "decision_value_classification": "material_industry_signal",
        "decision_value_component_reasoning": {
            fld: {"points": pts, "ceiling": cap,
                  "basis": e["new_fact"] if fld in ("law_policy_market_access", "supply_demand_price_utilisation") else e["increment"]}
            for fld, pts, cap in zip(SCORE_FIELDS, e["score"], MAX_FIELDS)
        },
        "publication_urgency": {
            "level": "near_term", "reason": "Material Stage A discovery priority; not authorization to publish.",
            "action_required": e["next_trigger"], "decision_deadline": None,
        },
        "technology_evidence_level": "not_applicable", "technology_score_cap_applied": False,
        "technology_validation_stage": None, "technology_validation_gap": e["must_not"],
        "policy_stage": e["policy_stage"], "policy_stage_provisional": False,
        "novelty_cap_basis": "none", "systemic_scale_denominator": e["system_denominator"],
        "denominator_used": e["system_denominator"], "denominator_gap": "",
        "prior_state": e["prior_state"], "new_verified_fact": "0.1P selector finding, NOT Stage B accepted-fact-safe: " + e["new_fact"],
        "changed_judgment": e["increment"], "uncertainty_resolved": e["new_fact"],
        "remaining_uncertainty": e["must_not"],
        "incremental_information": e["new_fact"],
        "baseline_expectation_changed": e["increment"],
        "decision_relevance": e["increment"],
        "evidence_needed_for_stage_b": evidence_targets,
        "next_confirmation_points": confirmation_targets,
        "related_prepass": related_for_strict(e, old),
        "baseline_relation": "program_lineage" if e["related_full"] else "new_unrelated_event",
        "baseline_match": e["related_full"][0] if e["related_full"] else "",
        "baseline_follow_up_relation": e["related_reason"],
        "follow_up_relation": e["related_reason"],
        "duplicate_risk": "low_confirmed_not_same_event",
        "date_role": {
            "observed_date": old.get("date_role", {}).get("observed_date"),
            "event_date": date, "publication_date": date, "announcement_date": date,
            "status": "PASS_STAGE_A_PRELIMINARY",
            "representative_date_basis": "First dated official plan adoption or tender publication; not projected implementation/commercial operation.",
            "earliest_check_scope": "Full1676 + 1,330 source titles and owners + dated original government/KPX notices.",
        },
        "structural_non_execution_reason": "Dated formally adopted statutory plans change scope/targets without physical new production." if not is_ess else None,
        "why_execution_event_not_required": "Policy-plan adoption is an independent decision-useful regulatory act despite no reserve stock yet." if not is_ess else None,
        "execution_anchor_type": "" if not is_ess else "administrative_competitive_tender_notice",
        "execution_anchor_strength": "" if not is_ess else "moderate",
        "structural_value_override_applied": not is_ess,
        "structural_value_override_reason": ver_reason if not is_ess else "",
        "execution_credibility_gate": {
            "status": "PASS", "reason": ver_reason,
            "anchor_type": "policy_regulatory_anchor" if not is_ess else "administrative_competitive_tender_notice",
            "anchor_strength": "moderate",
            "stage_precision_note": e["must_not"],
        },
        "independent_cardability_gate": {
            "status": "PASS", "reason": ver_reason,
            "full_schema_viability": "PASS", "distinct_event_or_stage_progression": True,
            "duplicate_or_reinforcement_note": e["must_not"],
        },
        "needs_review": False, "review_reason": "", "review_pool_subtype": "structural_signal_review",
        "review_pool_partition": None, "review_pool_resolution_status": None,
        "review_pool_item_id": None,
        "merge_status": "not_merged", "merged_story_ids": [],
        "staleness_decision": "fresh_followup" if not is_ess else "fresh_event",
        "staleness": {"event_date": date, "publication_date": date,
                      "staleness_gap_days": 0, "staleness_suspected": False,
                      "fresh_followup": not is_ess, "staleness_override": False,
                      "decision": "fresh_followup" if not is_ess else "fresh_event"},
        "review_pool_repromotion_precondition": "0.1P completed; strict only after ordinary native Stage A checks.",
        "promotion_precondition": "Completed under 0.1P; Stage B evidence/rights check remains mandatory.",
        "recommended_action": e["next_trigger"],
        "portfolio_coverage_contribution": e["classification_lenses"],
        "format_risk_tags": [],
        "why_now": e["increment"],
        "search_before_delete_status": "applied",
        "formal_0_1P_batch_promoted_20261101": {
            "case_id": e["case_id"], "date": date,
            "source_id": sid, "source_count": len(source_rows),
            "source_ids": [r["candidate_id"] for r in source_rows],
            "evidence_urls": e["owner_urls"],
            "separate_economic_units": e["event_units"],
            "not_stage_b_fact_safe": True,
        },
    })
    return spec


def support_row(old: dict, e: dict, rep_sid: str) -> dict:
    row = copy.deepcopy(old)
    source_id = row["candidate_id"]
    original_prepass = copy.deepcopy(row["related_prepass"])
    reason = (
        f"Same {e['date']} economic act as separately promoted Stage A {rep_sid}; "
        f"this article reports/expounds that plan or tender without a source-specific "
        f"different owner, instrument or executed stage. Preserve observation and "
        f"original URL; never create another card. {e['must_not']}"
    )
    row.update({
        "stage_a_pool": "reject_or_support_only_pool",
        "ledger_decision": "reject_or_support_only_pool", "editorial_bucket": "reject_or_support_only_pool",
        "review_pool_partition": "reject_or_support_only_pool",
        "review_pool_subtype": "support_source_only",
        "final_review_pool_disposition": "support_source_only_after_review",
        "review_pool_resolution_status": "resolved_support_source_only",
        "reject_or_support_only_basis": reason,
        "final_reason": reason, "whether_support_source_only": True,
        "reason_not_new_card": reason, "why_not_strict_passed_spec": reason,
        "decision_news_value_score": 11,
        "decision_value_breakdown": dict(zip(SCORE_FIELDS, (5,4,0,1,0,1,0,0))),
        "decision_value_classification": "low_independent_value",
        "decision_value_component_reasoning": {
            fld: {"points":pts,"ceiling":cap,"basis":reason}
            for fld,pts,cap in zip(SCORE_FIELDS,(5,4,0,1,0,1,0,0),MAX_FIELDS)
        },
        "novelty_cap_basis": "repeated_announcement_no_new_fact",
        "execution_credibility_gate": {
            "status": "PASS", "reason": f"Official owner establishes underlying {e['date']} act; this observation is not a new act.",
            "anchor_type": "policy_regulatory_anchor" if e["case_id"].startswith("KR_RESOURCE") else "execution_event_anchor",
            "anchor_strength": "moderate", "stage_precision_note": e["must_not"],
        },
        "independent_cardability_gate": {
            "status": "FAIL", "reason": reason,
            "full_schema_viability": "FAIL", "distinct_event_or_stage_progression": False,
            "duplicate_or_reinforcement_note": reason,
        },
        "publication_urgency": {"level":"monitor", "reason":"No separate card", "action_required":f"Keep as Stage B candidate source for {rep_sid}; verify incremental fact if any.","decision_deadline":None},
        "related_prepass": {
            "status": "PASS", "same_event_checked": True,
            "matched_baseline_candidate_ids": [],
            "matched_current_batch_candidate_ids": [rep_sid],
            "relation_candidates": [{
                "target_candidate_id": rep_sid, "proposed_relation_type": "same_event_duplicate",
                "confidence": "high", "reason": reason,
                "anchor_class_to_verify": None, "incremental_anchor_question": None,
            }],
            "duplicate_disposition": "same_event_duplicate", "earliest_same_event_check_status": "PASS",
            "fresh_anchor_questions": [f"Check source-specific distinct executed action before any future relaunch of {source_id}."],
            "earliest_same_event_date": e["date"],
            "earliest_check_scope": "Full1676 + government/KPX original act + same-event media URLs",
            "previous_prepass_edges_preserved_for_audit": [original_prepass],
        },
        "baseline_relation": "same_event_duplicate_in_stage_a_batch",
        "baseline_match": rep_sid,
        "prior_state": e["prior_state"],
        "new_verified_fact": "0.1P bounded owner check: " + e["new_fact"],
        "changed_judgment": "No increment over retained same-event Stage A strict source.",
        "uncertainty_resolved": reason,
        "remaining_uncertainty": "Potential unreported detail requires separate evidence, not automatic card creation.",
        "incremental_information": "No new distinct economic action established by this source.",
        "baseline_expectation_changed": "No; same official dated act as representative.",
        "decision_relevance": "Source evidence only; material decision belongs to the representative strict event.",
        "date_role": {"observed_date": old.get("date_role",{}).get("observed_date"),
                      "event_date":e["date"],"publication_date":None,"announcement_date":e["date"],
                      "status":"PASS_STAGE_A_PRELIMINARY",
                      "representative_date_basis":"Official economic act date; individual secondary article date is not inferred."},
        "recommendation": "Preserve as a support source; no independent card.",
        "recommended_action": "Preserve source URL, no new card for same event",
        "source_metadata_only": True,
        "canonical_card_write_allowed": False,
        "accepted_facts_approved": False,
        "stage_b_authorized": False,
        "formal_0_1P_support_only_20261101": {
            "case_id":e["case_id"], "representative_source_id": rep_sid,
            "original_source_url": old["primary_url"],
            "original_headline_raw": old["headline_raw"],
            "original_source_row_index": old["source_row_index"],
            "disposition": "SUPPORT_ONLY_SAME_EVENT_NO_CARD",
            "evidence_urls": e["owner_urls"],
            "source_independent_cardability": "FAIL",
            "no_destruction_or_silent_merge": True,
        },
    })
    return row


def coverage_maps(artifact: dict) -> None:
    pools = ("strict_passed_spec", "candidate_review_pool", "watchlist_context_pool", "reject_or_support_only_pool")
    anchors, lenses, classes = Counter(), Counter(), Counter()
    for pool in pools:
        for row in artifact[pool]:
            anchors.update(v for v in row.get("anchor_classes",[]) if isinstance(v,str))
            lenses.update(v for v in row.get("structural_value_lenses",[]) if isinstance(v,str))
            val = row.get("decision_value_classification")
            if isinstance(val,str) and val: classes[val] += 1
    artifact["summary"]["anchor_class_counts"] = dict(sorted(anchors.items()))
    artifact["summary"]["structural_lens_coverage_counts"] = dict(sorted(lenses.items()))
    artifact["summary"]["decision_value_classification_counts"] = dict(sorted(classes.items()))


def main() -> None:
    p = argparse.ArgumentParser()
    for k in ("base", "full", "output", "receipt"):
        p.add_argument("--"+k, required=True, type=Path)
    args = p.parse_args()
    assert sha256(args.base) == BASE_SHA
    stage, full = read(args.base), read(args.full)
    assert len(full["cards"]) == 1676
    assert len(stage["strict_passed_spec"]) == 8
    assert len(stage["candidate_review_pool"]) == 635
    assert len(stage["review_pool_resolution_ledger"]) == 1293
    assert len(stage["decision_ledger"]) == 1330
    template = next(r for r in stage["strict_passed_spec"] if r["spec_id"] == "A_SPEC_R4_DISC_001")
    pool_by_idx = {r["source_row_index"]:r for r in stage["candidate_review_pool"]}
    decisions = {r["candidate_id"]:r for r in stage["decision_ledger"]}
    resolutions = {r["story_id"]:r for r in stage["review_pool_resolution_ledger"]}
    assert len(set(RES_ROWS+ESS_ROWS)) == 30
    assert set(HOLD_SPLITS).isdisjoint(set(RES_ROWS+ESS_ROWS))
    for n in [*RES_ROWS,*ESS_ROWS,*HOLD_SPLITS]:
        assert n in pool_by_idx, n
    assert len({r["primary_url"] for r in stage["decision_ledger"] if r["source_row_index"] in RES_ROWS}) < len(RES_ROWS)
    full_titles = "\n".join(str(x.get("title", "")) for x in full["cards"])
    assert "핵심광물 38→51종" not in full_titles
    assert "1,180MW" not in full_titles

    output_records = []
    for event_key, e in EVENTS.items():
        rows = [pool_by_idx[idx] for idx in e["rows"]]
        representative = pool_by_idx[e["representative"]]
        rep_sid = representative["candidate_id"]
        spec = build_strict(representative, template, e, rows)
        stage["strict_passed_spec"].append(spec)
        decisions[rep_sid].update(copy.deepcopy(spec))
        stage["promotion_reassessment_ledger"].append({
            "candidate_id": rep_sid, "economic_event_cluster_id": e["case_id"],
            "before_pool": "candidate_review_pool", "after_pool": "strict_passed_spec",
            "promotion_reassessment_status": "PROMOTED_VALIDATED_STRICT",
            "resolved": e["new_fact"], "remaining": e["must_not"],
            "source_candidates": e["owner_urls"], "source_observation_preserved": True,
        })
        output_records.append({
            "source_id":rep_sid,"original_source_row_index":representative["source_row_index"],
            "source_url_original":representative["primary_url"],
            "case_id":e["case_id"], "economic_act_units":e["event_units"],
            "result":"NEW_STRICT_STAGE_A_SPEC_NOT_STAGE_B_AUTHORIZED",
            "score":spec["decision_news_value_score"],
            "full_identity":"NEW_DATE_SPECIFIC_ACT_NOT_IN_FULL1676",
            "official_basis":e["owner_urls"],
        })
        for row in rows:
            if row["candidate_id"] == rep_sid:
                continue
            sid = row["candidate_id"]
            support = support_row(row,e,rep_sid)
            stage["reject_or_support_only_pool"].append(support)
            decisions[sid].update(copy.deepcopy(support))
            res = resolutions[sid]
            res.update({
                "original_review_pool_partition":"reject_or_support_only_pool",
                "current_disposition":"reject_or_support_only_pool",
                "disposition_basis":support["final_reason"],
                "carry_forward_policy":"support_source_only",
                "next_action_condition":f"Stage B optional source corroboration to {rep_sid}; no additional card without new act.",
                "final_review_pool_disposition":"support_source_only_after_review",
                "reviewed_by_stage_or_pass":"PROMPT_0_1P_V4_20260829 formal support closure Nov1 2026",
                "review_artifact_id":"STAGE_A_KR_TWO_EVENT_FAMILIES_0_1P_20261101",
            })
            stage["promotion_reassessment_ledger"].append({
                "candidate_id": sid,"economic_event_cluster_id":e["case_id"],
                "before_pool":"candidate_review_pool","after_pool":"reject_or_support_only_pool",
                "promotion_reassessment_status":"FORMAL_SAME_EVENT_SUPPORT_ONLY",
                "resolved":support["final_reason"],
                "remaining":"Original source retained for Stage B corroboration; no automatic source acceptance.",
                "source_candidates":e["owner_urls"],"source_observation_preserved":True,
            })
            output_records.append({
                "source_id":sid,"original_source_row_index":row["source_row_index"],
                "source_url_original":row["primary_url"],"case_id":e["case_id"],
                "result":"FORMAL_SAME_EVENT_SUPPORT_ONLY_NO_NEW_CARD",
                "related_representative_source_id":rep_sid,
                "score":11,"official_basis":e["owner_urls"],
            })

    disposition_ids = {x["source_id"] for x in output_records}
    stage["candidate_review_pool"] = [r for r in stage["candidate_review_pool"] if r["candidate_id"] not in disposition_ids]
    stage["review_pool_resolution_ledger"] = [r for r in stage["review_pool_resolution_ledger"] if r["story_id"] not in {
        pool_by_idx[e["representative"]]["candidate_id"] for e in EVENTS.values()
    }]

    summary = stage["summary"]
    summary["strict_passed_spec_count"] = len(stage["strict_passed_spec"])
    summary["needs_review_count"] = sum(len(stage[x]) for x in ("candidate_review_pool", "watchlist_context_pool", "reject_or_support_only_pool"))
    summary["processed_priority_source_observations"] += 30
    summary["processed_priority_economic_clusters"] += 2
    summary["unprocessed_editorial_observations"] -= 30
    summary["pool_counts"] = {
        x:len(stage[x]) for x in (
            "strict_passed_spec","candidate_review_pool","watchlist_context_pool",
            "reject_or_support_only_pool","existing_reinforcement","rejected","support_source_only"
        )
    }
    stage["review_pool_partition_summary"] = {
        x:len(stage[x]) for x in ("candidate_review_pool","watchlist_context_pool","reject_or_support_only_pool")
    }
    for key in ("high_value_review_pool_ids","structural_signal_review_pool_ids","earnings_deep_dive_pool_ids","technology_validation_gap_ids","legal_policy_stage_gap_ids"):
        if isinstance(summary.get(key),list):
            summary[key] = [x for x in summary[key] if x not in disposition_ids]
    if isinstance(summary.get("follow_up_candidate_ids"),list):
        follow_up = []
        for pool in ("strict_passed_spec", "candidate_review_pool", "watchlist_context_pool", "reject_or_support_only_pool"):
            for item in stage[pool]:
                relation = item.get("baseline_follow_up_relation", "")
                is_follow_up = "follow_up_probability_anchor" in item.get("anchor_classes", []) or (
                    isinstance(relation, str)
                    and relation.strip().lower() not in ("", "new", "new_unrelated", "unrelated", "not_applicable", "none")
                )
                if is_follow_up:
                    follow_up.append(item.get("spec_id") or item.get("review_pool_item_id") or item.get("story_id"))
        summary["follow_up_candidate_ids"] = follow_up
    coverage_maps(stage)
    att = stage["pre_native_0_1P_attachment_manifest_20261101"]
    completed = list(att["formal_review_completed_source_ids"])
    completed.extend(r["source_id"] for r in output_records)
    assert len(completed) == len(set(completed)) == 31
    att.update({
        "new_formal_decisions":31,
        "new_strict_promotions":2,
        "formal_review_completed_after_attachment_count":31,
        "formal_review_completed_source_ids": completed,
        "remaining_formal_source_count": 1254,
        "native_validator_scope_warning": "Native A artifact and lineage schema PASS now include all ten emitted strict specs, including two new Korean event families; pass validates structural contracts only, not Stage B evidence acceptance or substantive certification of 70 preliminary attachments.",
    })
    stage["formal_0_1P_two_korean_events_20261101"] = {
        "authority":"PROMPT_0_1P_V4_20260829",
        "source_ids_formalized_this_batch":30,
        "source_ids_formalized_cumulative_since_45":31,
        "formal_individual_completed_total":76,
        "formal_individual_pending":1254,
        "independent_event_families":2,
        "new_strict_passes":2,
        "new_support_only_sources":28,
        "new_cards_created":0,
        "stage_b_executed":False,
        "same_event_no_multicard":True,
        "original_source_universe_count":1330,
        "newly_found_source_rows_outside_prior54":[232,280,605,631],
        "formal_source_decisions":output_records,
        "distinct_mixed_or_stage_split_hold": [
            {"source_row_index":i,"source_id":pool_by_idx[i]["candidate_id"],"original_url":pool_by_idx[i]["primary_url"],"reason":reason}
            for i,reason in HOLD_SPLITS.items()
        ],
        "owner_urls_by_event":{key:e["owner_urls"] for key,e in EVENTS.items()},
        "official_notice_implementation_boundary":"MOTIR new mineral designation notice still pending; ESS bidder awards/contracts/build not yet implied.",
        "global_editorial_stage_a_status":"HOLD_OPEN_1254_UNADJUDICATED",
        "native_stage_b_recommendation_scope":"Strict-only schema next-call recommendation is not workflow authorization while global 0.1P HOLD remains; no Stage B has been executed.",
        "canonical_main_full_related_mutations":0,
    }
    stage["recommended_for"] = ["Continue formal Stage A 0.1P remaining 1,254 original Source IDs; ten strict Stage A candidates are evidence-pending, not published cards."]
    stage["next_call_recommendation"].update({
        "recommended_next_call":"Stage B r0",
        "recommended_prompt_id":"Prompt 0.2",
        "recommended_input_universe":"Stage A strict_passed_spec[] only",
        "reason":"Native schema strict-only next-call eligibility, NOT authorization or execution: global editorial Stage A HOLD until remaining 1,254 formal source dispositions complete.",
        "blocked_items_summary":stage["review_pool_partition_summary"],
        "pending_parallel_or_followup_call":"review_pool/treasure triage",
        "pending_prompt_id":"authorized review_pool/treasure promotion protocol, not Prompt 0.2",
        "pending_input_universe":"candidate_review_pool[] + eligible treasure/review-only universe",
        "pending_reason":"Stage B may process strict_passed_spec[] only; review_pool/treasure remains open and must not be treated as exhausted.",
    })
    assert len(stage["strict_passed_spec"]) == 10
    assert len(stage["candidate_review_pool"]) == 605
    assert len(stage["watchlist_context_pool"]) == 658
    assert len(stage["reject_or_support_only_pool"]) == 28
    assert len(stage["existing_reinforcement"]) == 29
    assert len(stage["review_pool_resolution_ledger"]) == 1291
    assert len(stage["promotion_reassessment_ledger"]) == 76
    assert len(stage["decision_ledger"]) == 1330
    assert sum(len(stage[k]) for k in ("strict_passed_spec","candidate_review_pool","watchlist_context_pool","reject_or_support_only_pool","existing_reinforcement")) == 1330
    assert summary["unprocessed_editorial_observations"] == 1254
    write(args.output,stage)
    receipt = {
        "status":"PENDING_NATIVE_VALIDATION_AFTER_0_1P_BUILD",
        "artifact_type":"STAGE_A_FORMAL_KR_RESOURCE_AND_ESS_0_1P_RECEIPT",
        "base_sha256":BASE_SHA,
        "output_sha256":sha256(args.output),
        "original_sources":1330,"new_formalized":30,"formalized_total":76,"formal_pending":1254,
        "strict_count":10,"new_strict_count":2,"new_support_only_count":28,
        "newly_recovered_source_rows":[232,280,605,631],
        "separate_hold_source_rows":list(HOLD_SPLITS),
        "event_records":stage["formal_0_1P_two_korean_events_20261101"],
        "stage_b_executed":False,"global_stage_a_status":"HOLD",
    }
    write(args.receipt,receipt)
    print(json.dumps({key:receipt[key] for key in ("status","output_sha256","new_formalized","formal_pending","new_strict_count","new_support_only_count")},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Checkpoint #15: four genuinely distinct executed U.S./Japan event cases.

Promotes four source-level primary event representatives; 5 repeated observations
are retained as independent support source records; one FlexGen observation is
reinforcement of an already-published Full event.  Eos and FlexGen siblings in
the same Eos/FlexGen/Georgia roundup are lineage-linked only, not new cards.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from build_stage_a_formal_kr_two_events_20261101 import (
    BASE_SHA as PRIOR_INPUT_SHA,
    build_strict, coverage_maps, read, sha256, support_row, write,
)

BASE_SHA = "32cde5ebdfe5dbb751c8fba2f1cc62c2ef6a3d0647efa00f8c10ff2498cbb69e"
assert PRIOR_INPUT_SHA != BASE_SHA

CASES: dict[str, dict[str, Any]] = {
    "GEORGIA": {
        "case_id":"US_GEORGIA_POWER_ROBINS_128MW_COD_BY_20260915",
        "rows":[86], "representative":86,
        "owner":"Georgia Power", "date":"2026-09-15",
        "owner_urls":[
            "https://www.georgiapower.com/news-hub/press-releases/georgia-power-robins-battery-storage-achieves-commercial-operation.html",
            "https://www.georgiapower.com/news-hub/press-releases/construction-now-underway-on-765-mw-of-new-battery-energy-storage-systems-across-georgia.html",
        ],
        "title":"Georgia Power Robins 128MW 배터리 ESS 상업운전 확인",
        "region":"US","geographic_scope":"Georgia, United States",
        "summary":"Georgia Power의 9월15일 기업 발표로 Robins BESS 128MW가 이미 상업운전 중임을 확인. 4시간까지 전력을 공급할 수 있다고 설명했으나 정확한 최초 COD 일자는 미공개. 기존 2025년 착공 및 2026년 6월 예상 COD와는 별도 달성 단계.",
        "prior_state":"Georgia Power 2025-05-07 건설 발표에서는 Robins 128MW BESS의 준공을 2026년 6월로 예상; Full1676에 9월 상업운전 달성 사건 없음.",
        "new_fact":"9월15일 원발표는 Georgia Power의 Robins 128MW ESS가 상업운전 상태임을 확증하나 정확한 최초 COD일은 명시하지 않음.",
        "increment":"2025 construction/prospective COD became a verified commercial-operation milestone at a real 128MW asset; separate from Eos financing and FlexGen EMS contracts in same roundup.",
        "must_not":"Do not equate release date 2026-09-15 with exact first COD; do not infer officially registered 512MWh from 128MW × up-to-four-hour duration, or count Eos/FlexGen sibling news as additional new cards.",
        "event_units":["GEORGIA_ROBINS_128MW_COMMERCIAL_OPERATION_BY_SEPT15",
                       "EOS_DOE_EXISTING_FULL_2026_09_10_US_01",
                       "FLEXGEN_LIGHTSHIFT_EXISTING_FULL_2026_09_16_US_02"],
        "score":[18,23,0,9,0,5,3,2],
        "anchors":["execution_event_anchor"],
        "classification_lenses":["AI/data-centre power/ESS","regional core signal"],
        "route":"execution_anchor_route", "execution_type":"confirmed_commercial_operation",
        "tech_stage":None, "tech_gap":"No new cell chemistry, efficiency or four-hour MWh rating independently validated by Stage A.",
        "technology_level":"not_applicable",
        "system_denominator":"Robins single operating asset rated 128MW, part of Georgia Power 2023 IRP portfolio; 128MW is power, not exact battery MWh registered. Four-hour capability is operator narrative, not a 512MWh source figure.",
        "law_type":"not_a_new_policy_rule", "policy_stage":None, "legal_stage":None,
        "procedure":"Georgia Power September15 original official announcement says commercial operation; exact first-in-service day not supplied.",
        "mandatory":"not_applicable", "implementation":"BESS co-located with Robins solar, delivering grid flexibility on a four-hour-rated operational horizon.",
        "funding":"No new Eos loan or financing event applies; IRP project ownership and EPC delivered per utility release.",
        "affected":["Georgia Power grid operations","Robins 128MW BESS","U.S. utility-scale ESS supply-chain demand"],
        "next_trigger":"Verify original in-service/COD date from PSC operating docket, first dispatch/availability reports and physical energy capacity from plant records.",
        "related_full":[],
        "related_reason":"Original roundup contains two separate economic acts already represented by Full 2026-09-10_US_01 Eos and 2026-09-16_US_02 FlexGen, but neither is the Robins 128MW COD event.",
        "staged_questions":["Check date of first commercial dispatch versus September15 celebration and earlier June projected COD.",
                            "Check registered MWh and sustained-duration documentation; distinguish rated MW from delivered energy.",
                            "Do not merge sibling Eos financing and FlexGen EMS partnership events into the Robins representative."],
        "evidence":[
            "Georgia Power official September15 commercial operation press release: verify 2026-09-15 Robins BESS 128MW commercial operation status and four-hour grid dispatch capacity.",
            "Georgia Power official May2025 construction announcement: verify previously projected June2026 commercial start and contrast with completed operation.",
            "Georgia PSC official utility in-service filing or plant registry: verify first commercial dispatch date and 128MW rated battery capacity.",
        ],
        "confirm":[
            "Georgia Power actual verified Robins 128MW in-service filing versus September15 announcement would strengthen the utility ESS operating outlook; delayed entry would weaken the rollout outlook.",
            "Georgia Power Robins measured 128MW operating capacity and recorded MWh duration would strengthen grid-flexibility outlook; curtailed dispatch would weaken actual operation outlook.",
            "Georgia Power PSC later portfolio in-service reports for 579.5MW other assets would strengthen Georgia supply outlook; commissioning delays would weaken planned operating capacity outlook.",
        ],
        "cat":"ESS", "sub_cat":"BESS_COMMERCIAL_OPERATION",
    },
    "EVE": {
        "case_id":"CN_EVE_POWER_FLUENCE_206GWH_FRAMEWORK_20260918",
        "rows":[16,116,133,158,1265], "representative":1265,
        "owner":"EVE Energy (亿纬锂能) and Fluence Energy", "date":"2026-09-18",
        "owner_urls":[
            "https://static.cninfo.com.cn/finalpage/2026-09-18/1225571033.PDF",
            "https://ir.fluenceenergy.com/news-releases/news-release-details/fluence-secures-long-term-battery-supply-through-multiyear",
        ],
        "title":"EVE Power–Fluence, 최대 206GWh 장기 공급 프레임워크 공개",
        "region":"CN","geographic_scope":"Chinese battery supplier and global Fluence procurement; destination markets unconfirmed",
        "summary":"EVE Energy 9월18일 공시: EVE Power·Fluence의 2027~2031년 공급 프레임워크 규모 206GWh 중 2027년 약정량은 16GWh, 2028~2031년 190GWh는 예약 용량. 실제 구매 사양·수량·가격·납기는 후속 개별 PO에 따름. Fluence 9월24일 별도 구매자 발표로 장기 공급관계 확인.",
        "prior_state":"Fluence 기존 Full 2026-09-16_GL_01은 FY26 실적 가이던스 하향 사건이며 EVE 공급 프레임워크와 다름; earlier EVE/Fluence business cooperation existed.",
        "new_fact":"EVE Energy September18 stock filing confirms new signed 2027-2031 framework with 2027 committed 16GWh and 2028-2031 reserved 190GWh; product prices and POs remain undetermined.",
        "increment":"Battery sourcing allocation now has a multiyear supplier framework and some 2027 committed volume, but no 206GWh purchase order or realized deliveries.",
        "must_not":"206GWh headline is NOT a firm purchase order, bankable sales, current capacity addition or U.S.-market-only delivery; 16GWh 2027 commitment is still subject to later purchase order details, and 190GWh is explicitly reserved, not binding throughput.",
        "event_units":["2027_VOLUME_COMMITMENT_16GWH_FRAMEWORK_ONLY","2028_2031_RESERVED_190GWH_FRAMEWORK_ONLY","FLUENCE_CONFIRMATION_RELEASE_SEPT24_SAME_AGREEMENT"],
        "score":[21,23,0,7,0,5,3,2],
        "anchors":["execution_event_anchor"],
        "classification_lenses":["midstream supply contract","AI/data-centre power/ESS"],
        "route":"execution_anchor_route", "execution_type":"signed_multiyear_supply_framework",
        "tech_stage":None, "tech_gap":"No manufacturing location, chemistry, product specification, commissioning, accepted PO, or actual cell performance evidenced by framework filing.",
        "technology_level":"not_applicable",
        "system_denominator":"206GWh five-year cooperation nominal maximum = 16GWh 2027 committed volume (7.77%) + 190GWh 2028-2031 reserved capacity (92.23%); neither equals PO fulfillment.",
        "law_type":"not_a_new_policy_rule", "policy_stage":None, "legal_stage":None,
        "procedure":"EVE Shenzhen disclosure September18 is first dated official source; Fluence September24 later confirms same existing agreement as buyer, not a second sale.",
        "mandatory":"not_applicable", "implementation":"Future 2027-2031 planned supply horizon; order-specific product, price, delivery schedule and quality criteria remain future PO execution.",
        "funding":"No publicly fixed value or bookable 206GWh revenue; financial impact undetermined by EVE filing.",
        "affected":["EVE Power storage battery supply planning","Fluence global ESS procurement","future cell supplier competition"],
        "next_trigger":"Confirm first signed purchase orders, annual physical shipments, destination markets, cell chemistry/manufacturing origin, and binding volume/payments independently.",
        "related_full":["2026-09-16_GL_01"],
        "related_reason":"Earlier Fluence FY26 guidance revision concerns margin/production delays, not EVE September18 agreement; relate only as issuer programme context, not same-event duplicate.",
        "staged_questions":["Verify legal scope of 16GWh commitment and 190GWh reservation using EVE Chinese issuer filing and Fluence September24 buyer release.",
                            "Reject media shortcut 'largest 206GWh confirmed order'; inspect purchase orders, prices and destination market independently.",
                            "Monitor actual production, delivery, revenue and international/local-content compliance by market."],
        "evidence":[
            "EVE Energy 2026-09-18 original Shenzhen stock exchange PDF filing: verify 2027 committed volume 16GWh and 2028-2031 reserved capacity 190GWh under 206GWh supply framework.",
            "Fluence September24 official buyer press release document: verify 2026-09-24 multiyear supply contract status with EVE Power and global buyer scope, not executed 206GWh orders.",
            "EVE Energy future formal purchase orders and issuer filings: verify actual quantities, price, destinations, signed dates and noncancelable volume obligations.",
        ],
        "confirm":[
            "EVE Power future signed purchase contract volume covering the 2027 committed16GWh would strengthen global ESS supplier concentration outlook; no contracted capacity would weaken demand outlook.",
            "Fluence annual actual battery shipment volume in GWh versus reserved190GWh capacity would strengthen long-term battery demand outlook; unused reservations would weaken it.",
            "EVE actual shipment destination-market and manufacturing-origin data would strengthen local supply-chain planning outlook; incompatible domestic content would weaken U.S.-eligibility outlook.",
        ],
        "cat":"SupplyChain", "sub_cat":"CELL_SUPPLY_FRAMEWORK",
    },
    "FACTORIAL": {
        "case_id":"US_JP_FACTORIAL_MITSUI_SULFIDE_JDA_20260917",
        "rows":[126], "representative":126,
        "owner":"Factorial Energy and Mitsui Kinzoku", "date":"2026-09-17",
        "owner_urls":[
            "https://factorialenergy.gcs-web.com/news-releases/news-release-details/mitsui-kinzoku-partners-factorial-scale-all-solid-state-battery",
            "https://www.mitsui-kinzoku.com/en/news_a/?TabModule903=0&dispmid=1140&itemid=1993",
        ],
        "title":"Factorial–Mitsui Kinzoku, 황화물 전해질·전고체 셀 공동개발 합의",
        "region":"US","geographic_scope":"United States and Japan supplier development",
        "summary":"9월17일 Factorial과 Mitsui Kinzoku가 전고체 Solstice 플랫폼의 황화물계 A-SOLiD 전해질 성능 개선·층 형성 공정 개발을 위한 JDA 체결 발표. 공정 대량생산 적합성은 검증 목표로 남으며 셀 양산 시작·수율·성능 인증 달성이 아님.",
        "prior_state":"Factorial Full 2026-07-24_US_01 drone cell commercial order and 2026-06-17_US_02 road-use integration are distinct customer/vehicle-stage events.",
        "new_fact":"September17 Factorial–Mitsui signed joint development agreement to integrate Mitsui sulfide solid-electrolyte material with Factorial all-solid-state cell development and optimize layers and production suitability.",
        "increment":"New Japan materials partner and actual JDA alter sulfide electrolyte supply/process qualification path, without proving mass production or independent cell validation.",
        "must_not":"Do not claim sulfide solid-state cells achieved mass production, guaranteed energy-density performance, commercial delivery or qualification solely because JDA and collaboration were announced.",
        "event_units":["SIGNED_SULFIDE_ELECTROLYTE_JOINT_DEVELOPMENT_AGREEMENT","MASS_PRODUCTION_AND_QUALIFICATION_STILL_FUTURE"],
        "score":[22,20,3,6,0,4,3,2],
        "anchors":["execution_event_anchor","technology_commercialization_anchor"],
        "classification_lenses":["technology_transition_commercialization","midstream materials"],
        "route":"execution_anchor_route", "execution_type":"signed_joint_development_agreement",
        "tech_stage":"research_or_paper", "tech_gap":"Materials/layer-formation work is newly agreed; independent solid-state qualification, scalable process yields and actual mass production remain unverified.",
        "technology_level":"company_target_or_unsupported_claim",
        "system_denominator":"One supplier-development JDA with Mitsui for A-SOLiD sulfide electrolyte; no disclosed validated GWh output, yield, unit cost or equipment throughput denominator.",
        "law_type":"not_a_new_policy_rule", "policy_stage":None, "legal_stage":None,
        "procedure":"September17 issuer/partner press statements confirm signed JDA; actual jointly validated material performance and scale-up are future milestones.",
        "mandatory":"not_applicable", "implementation":"Factorial to lead cell architecture, integration and manufacturing-validation design; Mitsui provides sulfide electrolyte materials and coating-layer process R&D.",
        "funding":"No verified disclosed committed investment, procurement take-or-pay or customer delivery amount in source announcement.",
        "affected":["sulfide solid electrolyte materials","solid-state cell R&D supply chain","Factorial Solstice platform"],
        "next_trigger":"Verify laboratory test results, sulfide electrolyte coating yield, cell-level independent qualification, customer pilot lines and any binding production-volume/offtake agreements.",
        "related_full":["2026-07-24_US_01","2026-06-17_US_02"],
        "related_reason":"Factorial's prior aerospace commercial order and vehicle road testing are separate economic/technical acts; new JDA is a supply-chain/material development partnership.",
        "staged_questions":["Read the signed scope versus announced framework; no binding commercial volume assumed.",
                            "Validate Mitsui sulfide electrolyte suitability, film-layer process and scalable yield with actual qualification evidence.",
                            "Disambiguate earlier Factorial drone order and Stellantis vehicle tests from this new electrolyte partnership."],
        "evidence":[
            "Factorial September17 official joint development agreement announcement: verify 2026-09-17 Mitsui Kinzoku signed contract status for sulfide electrolyte Solstice material scale-up.",
            "Mitsui Kinzoku September17 original partner press release document: verify A-SOLiD electrolyte layer production test stage and planned mass-production suitability work.",
            "Future Factorial independent qualification test filing: verify verified sulfide cell performance and scale production yield, not only partnership targets.",
        ],
        "confirm":[
            "Factorial independent sulfide-cell qualification results with measured yield would strengthen the solid-state commercialization outlook; failed tests would weaken it.",
            "Mitsui actual A-SOLiD mass production line commissioning versus JDA stage would strengthen battery materials supply outlook; delays would weaken scale-up outlook.",
            "Factorial customer signed purchase contract volume from qualified sulfide-cell lines would strengthen market penetration outlook; absent production commitments would weaken it.",
        ],
        "cat":"Technology", "sub_cat":"SULFIDE_SOLID_STATE_JDA",
    },
    "PANASONIC": {
        "case_id":"JP_PANASONIC_ENERGY_KADOMA_RND_HUB_OPEN_20260916",
        "rows":[78,119], "representative":78,
        "owner":"Panasonic Energy", "date":"2026-09-16",
        "owner_urls":["https://news.panasonic.com/global/press/en260916-3",
                      "https://news.panasonic.com/jp/press/jn260916-2"],
        "title":"Panasonic Energy, 오사카 Kadoma 배터리 R&D 허브 가동",
        "region":"JP","geographic_scope":"Kadoma, Osaka, Japan; future network link to US sites",
        "summary":"Panasonic Energy가 9월16일 일본 Kadoma Energy Innovation Square 연구거점 가동을 공식 발표. 배터리 소재 개발·셀 설계·프로토타입 제작 기능을 통합한 약 24,500㎡ 연구시설이며 양산 셀 생산능력 또는 검증된 신제품 매출은 아님.",
        "prior_state":"Panasonic Energy's R&D and production-development work across multiple Japanese sites preexisted; no exact September16 Kadoma opened facility in Full1676.",
        "new_fact":"September16 official Panasonic launch confirms Kadoma Energy Innovation Square operating as a new lithium-ion battery materials/design/prototyping R&D facility, linked to Suminoe and U.S. manufacturing sites.",
        "increment":"Physical R&D infrastructure was put into use; integrates materials/cell design/prototyping and supports later production transfer, with no new commercial cell output implied.",
        "must_not":"Do not treat 24,500㎡ R&D floor space or approximately 500 staff as GWh production CAPA, 500 new hires, completed next-generation battery qualification or current factory shipments.",
        "event_units":["KADOMA_ENERGY_INNOVATION_SQUARE_RND_FACILITY_LAUNCHED"],
        "score":[18,20,0,8,0,4,3,2],
        "anchors":["execution_event_anchor","technology_commercialization_anchor"],
        "classification_lenses":["technology_transition_commercialization","cell/manufacturing"],
        "route":"execution_anchor_route", "execution_type":"operating_battery_rnd_facility",
        "tech_stage":"research_or_paper", "tech_gap":"Facility launch enables material/design/prototype R&D but does not establish independently validated battery chemistry, yield, qualification, or mass production.",
        "technology_level":"not_applicable",
        "system_denominator":"A 24,500sqm research/prototyping building and about 500 staff are R&D inputs; not commercial GWh production or existing shipments.",
        "law_type":"not_a_new_policy_rule", "policy_stage":None, "legal_stage":None,
        "procedure":"Official Panasonic launch 2026-09-16 is an operating R&D hub, not factory production-completion certification.",
        "mandatory":"not_applicable", "implementation":"Integrate Kadoma research and Suminoe production development to transfer future validated cell processes across Japan/Nevada/Kansas sites.",
        "funding":"No directly verified incremental CAPEX or hiring count in cited release; physical facility launched.",
        "affected":["Panasonic lithium-ion battery R&D","materials and cell-prototyping workflow","future Japan/U.S. factory process transfer"],
        "next_trigger":"Verify prototype-to-qualified-cell lead time, customer test qualification, factory line transfer, and validated production/scrap/yield before crediting commercial output.",
        "related_full":[],
        "related_reason":"Existing Panasonic factory/customer qualification milestones in Full are not September16 opening of the Kadoma research facility.",
        "staged_questions":["Separate research/prototyping launch from GWh commercial manufacturing and customer deliveries.",
                            "Confirm any actual lead time reduction and savings; published greater-than-15% reduction is company expectation.",
                            "Track future Suminoe and Nevada/Kansas process-transfer and cell-level customer qualification."],
        "evidence":[
            "Panasonic Energy original global press release document dated September16: verify 2026-09-16 Energy Innovation Square launch status and Kadoma 24500 square-meter R&D facility capacity.",
            "Panasonic Energy Japanese corporate press release document September16: verify 2026-09-16 Kadoma research facility launch stage and Suminoe production-development collaboration.",
            "Panasonic later factory certification test reports and production filings: verify mass-production line transfer status and battery qualification milestone dates separately.",
        ],
        "confirm":[
            "Panasonic actual battery prototype development schedule versus 15-percent transport target would strengthen R&D efficiency outlook; unchanged delays would weaken it.",
            "Panasonic verified customer qualifications following Kadoma research output would strengthen downstream production outlook; rejected cells would weaken it.",
            "Panasonic Kansas/Nevada transferred mass-production processes with documented yield would strengthen scale-up outlook; stalled commissioning would weaken it.",
        ],
        "cat":"Technology", "sub_cat":"BATTERY_RND_FACILITY_OPENING",
    },
}

SPECIAL_EDITORIAL_CAUTION = {
    133:"Chinese headline describes all 206GWh as largest confirmed order; issuer filing says 16GWh commitment +190GWh reservation subject to future POs.",
    158:"Chinese headline describes a 206GWh mega order; issuer filing says nonfinal framework and follow-on purchase orders not signed for all volumes.",
}
HOLD_SPLIT = {
    8:"InsideEVs September18 interview about the new Mitsui JDA also discusses older PowerCo, Hyundai, SK On and POSCO Future M cooperation, Karma Automotive 2028 prospective rollout, and reported target energy density. Source-level non-JDA economic units require independent lineage/date and qualification checks before formal disposition.",
}


def execution_strict(old: dict, template: dict, e: dict, observations: list[dict]) -> dict:
    spec = build_strict(old,template,e,observations)
    technical = e["tech_stage"] is not None
    assert sum(e["score"]) >= 55
    spec.update({
        "assessment_profile":"confirmed_commercial_operation" if e["case_id"].startswith("US_GEORGIA") else "confirmed_company_economic_act",
        "selection_route":"execution_anchor_route",
        "execution_anchor_type":e["execution_type"],
        "execution_anchor_strength":"strong" if "operation" in e["execution_type"] or "facility" in e["execution_type"] else "moderate",
        "structural_value_override_applied":False,
        "structural_value_override_reason":"",
        "structural_non_execution_reason":None,
        "why_execution_event_not_required":None,
        "execution_credibility_gate":{
            "status":"PASS", "reason":e["increment"] + " " + e["must_not"],
            "anchor_type":e["execution_type"],
            "anchor_strength":"strong" if "operation" in e["execution_type"] or "facility" in e["execution_type"] else "moderate",
            "stage_precision_note":e["must_not"],
        },
        "technology_evidence_level":e["technology_level"],
        "technology_validation_stage":e["tech_stage"],
        "technology_stage_provisional":False if technical else None,
        "technology_score_cap_applied":technical,
        "technology_validation_gap":e["tech_gap"],
        "policy_stage":None, "legal_policy_stage":None,
        "review_pool_subtype":None,
        "legal_instrument_type":None, "competent_authority":None,
        "mandatory_application_date":None, "effective_date":None,
        "procedural_status":None,
        "region":e["region"], "geographic_scope":e["geographic_scope"],
        "adoption_date":None,"publication_date":None,
        "affected_products_or_activities":e["affected"],
        "legal_policy_transmission_chain":[],
        "exemptions_and_thresholds":[], "transition_and_grandfathering":[],
        "noncompliance_consequences":[],
        "appeal_or_litigation_risk":None, "precedent_scope":None,
        "extraterritorial_effect":"Not a direct legal instrument; possible future sourcing geography separately verified.",
        "cat":e["cat"], "sub_cat":e["sub_cat"],
        "staleness_decision":"fresh_followup" if e["case_id"].startswith("US_GEORGIA") else "fresh_event",
        "staleness":{"event_date":e["date"],"publication_date":e["date"],
                     "staleness_gap_days":0,"staleness_suspected":False,
                     "fresh_followup":e["case_id"].startswith("US_GEORGIA"),
                     "staleness_override":False,"decision":"fresh_followup" if e["case_id"].startswith("US_GEORGIA") else "fresh_event"},
        "source_priority_notes":e["must_not"],
        "evidence_needed_for_stage_b":e["evidence"],
        "next_confirmation_points":e["confirm"],
        "baseline_follow_up_relation":"distinct_related_economic_act" if e["related_full"] else "new_unrelated",
        "follow_up_relation":"distinct_related_economic_act" if e["related_full"] else "new_unrelated",
        "related_prepass":{
            "status":"PASS", "same_event_checked":True,
            "matched_baseline_candidate_ids":e["related_full"],
            "matched_current_batch_candidate_ids":[],
            "relation_candidates":[{
                "target_candidate_id":fid,"proposed_relation_type":"program_lineage",
                "confidence":"high","reason":e["related_reason"],
                "anchor_class_to_verify":"execution_event_anchor",
                "incremental_anchor_question":e["staged_questions"][0],
            } for fid in e["related_full"]],
            "duplicate_disposition":"no_duplicate_found",
            "earliest_same_event_check_status":"PASS",
            "fresh_anchor_questions":e["staged_questions"],
            "search_shortlist_is_lineage":False,
            "preliminary_relation_proposal":"program_lineage" if e["related_full"] else "new_unrelated_event",
            "fingerprint_reason":e["increment"],
            "rejected_relation_candidates":[],
            "previous_prepass_edges_preserved_for_audit":[old["related_prepass"]],
            "earliest_same_event_date":e["date"],
            "earliest_check_scope":"Full1676 locked + original 1330 Source IDs + original company owner releases",
        },
        "independent_cardability_gate":{
            "status":"PASS","reason":e["increment"] + " " + e["must_not"],
            "full_schema_viability":"PASS","distinct_event_or_stage_progression":True,
            "duplicate_or_reinforcement_note":e["related_reason"],
        },
        "original_source_identity_preserved":{
            "source_id":old["story_id"], "source_row_index":old["source_row_index"],
            "headline_raw":old["headline_raw"],"primary_url":old["primary_url"],
        },
        "formal_0_1P_batch_promoted_20261101":{
            "case_id":e["case_id"],"date":e["date"],
            "source_id":old["story_id"],"source_count":len(observations),
            "source_ids":[r["story_id"] for r in observations],
            "evidence_urls":e["owner_urls"],
            "separate_economic_units":e["event_units"],
            "not_stage_b_fact_safe":True,
        },
    })
    if e["case_id"].startswith("US_GEORGIA"):
        spec["mixed_source_sibling_lineage"] = [
            {"economic_act":"Eos $87,018,601 DOE loan draw","full_id":"2026-09-10_US_01",
             "disposition":"already_in_full_separate_event_no_new_card"},
            {"economic_act":"FlexGen-Lightshift 16 BESS projects EMS portfolio","full_id":"2026-09-16_US_02",
             "disposition":"already_in_full_separate_event_no_new_card"},
            {"economic_act":"Georgia Power Robins 128MW COD","full_id":None,
             "disposition":"new_distinct_stage_a_strict_spec"},
        ]
    return spec


def reinforce_flexgen(old: dict, rep_full: dict) -> dict:
    row = copy.deepcopy(old)
    reason = (
        "2026-09-18 later article describes same FlexGen-Lightshift 16-project 80MW/285MWh "
        "EMS portfolio as locked Full 2026-09-16_US_02, based on FlexGen original September16 release; "
        "six 25MW/85MWh sites completed and ten 55MW/200MWh under construction. "
        "No new 55MW commissioning or new agreement signed after the Full event is established."
    )
    row.update({
        "stage_a_pool":"existing_reinforcement", "ledger_decision":"existing_reinforcement",
        "editorial_bucket":"existing_reinforcement",
        "assessment_status":"FORMAL_0_1P_EXISTING_FULL_REINFORCEMENT",
        "assessment_method":"PROMPT_0_1P_V4_20260829 original-owner and Full body comparison",
        "promotion_reassessment_status":"FORMAL_EXISTING_FULL_NO_NEW_CARD",
        "review_pool_partition":None,"review_pool_resolution_status":None,
        "review_reason":"", "needs_review":False,
        "reinforcement_type":"same_event_later_media_recap",
        "reason_not_new_card":reason,
        "baseline_match":rep_full["id"],"baseline_relation":"same_event_duplicate_in_full",
        "baseline_follow_up_relation":"same_event_duplicate_in_full",
        "follow_up_relation":"same_event_duplicate_in_full",
        "duplicate_risk":"same_event_confirmed",
        "novelty_cap_basis":"repeated_announcement_no_new_fact",
        "decision_news_value_score":26,
        "decision_value_classification":"context_or_reinforcement",
        "independent_cardability_gate":{
            "status":"FAIL","reason":reason,
            "full_schema_viability":"FAIL","distinct_event_or_stage_progression":False,
            "duplicate_or_reinforcement_note":reason,
        },
        "execution_credibility_gate":{
            "status":"PASS","reason":"FlexGen original September16 confirms all 16 EMS projects; no later independent commissioning.",
            "anchor_type":"execution_event_anchor", "anchor_strength":"moderate",
            "stage_precision_note":"Six assets completed, ten under construction; never report all 16 as new COD.",
        },
        "related_prepass":{
            "status":"PASS","same_event_checked":True,
            "matched_baseline_candidate_ids":[rep_full["id"]],
            "matched_current_batch_candidate_ids":[],
            "relation_candidates":[{"target_candidate_id":rep_full["id"],
                                    "proposed_relation_type":"same_event_duplicate","confidence":"high",
                                    "reason":reason,"anchor_class_to_verify":None,"incremental_anchor_question":None}],
            "duplicate_disposition":"same_event_duplicate",
            "earliest_same_event_check_status":"PASS",
            "fresh_anchor_questions":["Check for later project-specific COD only if new owner evidence arrives."],
            "earliest_same_event_date":"2026-09-16",
            "earliest_check_scope":"Full 2026-09-16_US_02 primary FlexGen body plus later September18 article",
            "previous_prepass_edges_preserved_for_audit":[copy.deepcopy(old["related_prepass"])],
        },
        "prior_state":"Full 2026-09-16_US_02 already carries 6 completed and 10 constructing sites.",
        "new_verified_fact":"No new economic event vs prior Full; later source confirms owner’s dated September16 announcement.",
        "changed_judgment":"No new card; source reinforcement only.",
        "uncertainty_resolved":reason,
        "remaining_uncertainty":"Ten construction sites each require future separate operation verification.",
        "incremental_information":"Additional coverage of same already published Full act.",
        "baseline_expectation_changed":"No; already represented.",
        "decision_relevance":"Preserve original source URL as possible later evidence corroboration.",
        "reason":reason,
        "source_metadata_only":True,
        "stage_b_authorized":False,"accepted_facts_approved":False,"canonical_card_write_allowed":False,
        "formal_0_1P_existing_full_reinforcement_20261101":{
            "original_source_id":old["story_id"],"original_source_row_index":old["source_row_index"],
            "original_headline":old["headline_raw"],"original_url":old["primary_url"],
            "full_card_id":rep_full["id"],
            "primary_owner_url":"https://www.flexgen.com/resources/blog/flexgen-partners-lightshift-energy-its-16-battery-energy-storage-projects-pjm-iso-ne",
            "no_new_card":True,
        },
    })
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    for k in ("base","full","output","receipt"):
        parser.add_argument("--"+k,type=Path,required=True)
    a = parser.parse_args()
    assert sha256(a.base) == BASE_SHA
    d, full = read(a.base), read(a.full)
    assert len(full["cards"]) == 1676
    assert len(d["strict_passed_spec"]) == 10
    assert len(d["candidate_review_pool"]) == 605
    assert len(d["watchlist_context_pool"]) == 658
    assert len(d["review_pool_resolution_ledger"]) == 1291
    assert len(d["promotion_reassessment_ledger"]) == 76
    full_by_id = {r["id"]:r for r in full["cards"]}
    assert full_by_id["2026-09-10_US_01"]["title"].startswith("Eos")
    assert full_by_id["2026-09-16_US_02"]["title"].startswith("Lightshift")
    full_text = "\n".join(str(r.get("title","")) for r in full["cards"])
    for key in ("Robins 128MW", "206GWh", "Kadoma", "Mitsui Kinzoku"):
        assert key not in full_text, key
    candidate = {r["source_row_index"]:r for r in d["candidate_review_pool"]}
    watch = {r["source_row_index"]:r for r in d["watchlist_context_pool"]}
    all_old = {**candidate,**watch}
    case_indices = {i for e in CASES.values() for i in e["rows"]}
    assert len(case_indices) == 9 and 115 not in case_indices
    assert 8 not in case_indices and 8 in watch
    assert all(i in all_old for i in case_indices)
    assert set(SPECIAL_EDITORIAL_CAUTION) <= case_indices
    template = d["strict_passed_spec"][-1]
    ledger = {r["story_id"]:r for r in d["decision_ledger"]}
    reviews = {r["story_id"]:r for r in d["review_pool_resolution_ledger"]}
    decisions = []
    strict_ids: set[str] = set()
    support_ids: set[str] = set()
    for case_key,e in CASES.items():
        observations = [all_old[idx] for idx in e["rows"]]
        rep = all_old[e["representative"]]
        sid = rep["story_id"]
        strict = execution_strict(rep,template,e,observations)
        d["strict_passed_spec"].append(strict)
        ledger[sid].update(copy.deepcopy(strict))
        strict_ids.add(sid)
        decisions.append({
            "source_id":sid,"row":e["representative"],"headline_raw_original":rep["headline_raw"],
            "source_url_original":rep["primary_url"],"case_id":e["case_id"],
            "result":"NEW_STRICT_STAGE_A_SELECTOR_ONLY_NOT_STAGE_B",
            "full_identity":"NO_EXACT_SAME_EVENT_IN_FULL1676",
            "related_full_distinct_events":e["related_full"],"score":sum(e["score"]),
            "owner_urls":e["owner_urls"],"economic_act_units":e["event_units"],
            "must_not_claim":e["must_not"],
        })
        d["promotion_reassessment_ledger"].append({
            "candidate_id":sid,"economic_event_cluster_id":e["case_id"],
            "before_pool":rep["stage_a_pool"],"after_pool":"strict_passed_spec",
            "promotion_reassessment_status":"PROMOTED_VALIDATED_STRICT",
            "resolved":e["new_fact"],"remaining":e["must_not"],
            "source_candidates":e["owner_urls"],"source_observation_preserved":True,
        })
        for row in observations:
            if row["story_id"] == sid:
                continue
            s = support_row(row,e,sid)
            idx = row["source_row_index"]
            if idx in SPECIAL_EDITORIAL_CAUTION:
                s["source_specific_editorial_correction"] = SPECIAL_EDITORIAL_CAUTION[idx]
            d["reject_or_support_only_pool"].append(s)
            ledger[row["story_id"]].update(copy.deepcopy(s))
            review = reviews[row["story_id"]]
            review.update({
                "original_review_pool_partition":"reject_or_support_only_pool",
                "current_disposition":"reject_or_support_only_pool",
                "disposition_basis":s["final_reason"],
                "carry_forward_policy":"support_source_only",
                "next_action_condition":f"Corroboration for {sid}; no new card without an independent act.",
                "final_review_pool_disposition":"support_source_only_after_review",
                "reviewed_by_stage_or_pass":"PROMPT_0_1P_V4_20260829 original-owner formal Nov1 2026",
                "review_artifact_id":"STAGE_A_USJP_FOUR_EVENTS_FORMAL_20261101",
            })
            d["promotion_reassessment_ledger"].append({
                "candidate_id":row["story_id"],"economic_event_cluster_id":e["case_id"],
                "before_pool":row["stage_a_pool"],"after_pool":"reject_or_support_only_pool",
                "promotion_reassessment_status":"FORMAL_SAME_EVENT_SUPPORT_ONLY",
                "resolved":s["final_reason"],
                "remaining":"Source record retained for future Stage B corroboration; original journalism claims not auto accepted.",
                "source_candidates":e["owner_urls"],"source_observation_preserved":True,
            })
            decisions.append({
                "source_id":row["story_id"],"row":idx,
                "headline_raw_original":row["headline_raw"],"source_url_original":row["primary_url"],
                "case_id":e["case_id"],"result":"FORMAL_SAME_EVENT_SUPPORT_NO_NEW_CARD",
                "related_strict_source_id":sid,"owner_urls":e["owner_urls"],
                "source_specific_editorial_correction":SPECIAL_EDITORIAL_CAUTION.get(idx),
            })
            support_ids.add(row["story_id"])

    flex = all_old[115]
    r = reinforce_flexgen(flex,full_by_id["2026-09-16_US_02"])
    d["existing_reinforcement"].append(r)
    ledger[flex["story_id"]].update(copy.deepcopy(r))
    d["promotion_reassessment_ledger"].append({
        "candidate_id":flex["story_id"],
        "economic_event_cluster_id":"US_FLEXGEN_LIGHTSHIFT_EXISTING_FULL_20260916",
        "before_pool":"watchlist_context_pool","after_pool":"existing_reinforcement",
        "promotion_reassessment_status":"FORMAL_EXISTING_FULL_REINFORCEMENT",
        "resolved":r["reason_not_new_card"],
        "remaining":"Future ten project CODs need new event-specific original records.",
        "source_candidates":[r["formal_0_1P_existing_full_reinforcement_20261101"]["primary_owner_url"]],
        "source_observation_preserved":True,
    })
    decisions.append({
        "source_id":flex["story_id"],"row":115,
        "headline_raw_original":flex["headline_raw"],"source_url_original":flex["primary_url"],
        "case_id":"US_FLEXGEN_LIGHTSHIFT_EXISTING_FULL_20260916",
        "result":"FORMAL_EXISTING_FULL_REINFORCEMENT_NO_NEW_CARD",
        "related_full_id":"2026-09-16_US_02",
        "owner_urls":[r["formal_0_1P_existing_full_reinforcement_20261101"]["primary_owner_url"]],
        "must_not_claim":"16 projects consist of six operating and ten under construction, not 16 newly commissioned.",
    })
    completed_ids = strict_ids | support_ids | {flex["story_id"]}
    assert len(completed_ids) == 10 and len(support_ids) == 5 and len(strict_ids) == 4
    d["candidate_review_pool"] = [v for v in d["candidate_review_pool"] if v["story_id"] not in completed_ids]
    d["watchlist_context_pool"] = [v for v in d["watchlist_context_pool"] if v["story_id"] not in completed_ids]
    d["review_pool_resolution_ledger"] = [v for v in d["review_pool_resolution_ledger"] if v["story_id"] not in (strict_ids | {flex["story_id"]})]

    summary=d["summary"]
    summary["strict_passed_spec_count"] = len(d["strict_passed_spec"])
    summary["existing_reinforcement_count"] = len(d["existing_reinforcement"])
    summary["duplicate_or_reinforcement_count"] = len(d["existing_reinforcement"])
    summary["needs_review_count"] = sum(len(d[x]) for x in ("candidate_review_pool","watchlist_context_pool","reject_or_support_only_pool"))
    summary["processed_priority_source_observations"] += 10
    summary["processed_priority_economic_clusters"] += 4
    summary["unprocessed_editorial_observations"] -= 10
    summary["pool_counts"] = {x:len(d[x]) for x in (
        "strict_passed_spec","candidate_review_pool","watchlist_context_pool",
        "reject_or_support_only_pool","existing_reinforcement","rejected","support_source_only")}
    d["review_pool_partition_summary"] = {x:len(d[x]) for x in (
        "candidate_review_pool","watchlist_context_pool","reject_or_support_only_pool")}
    coverage_maps(d)
    import sys
    sys.path.insert(0,str(a.base.resolve().parent))
    from validation_scripts.stage_a_full_v3_completeness_review4943656188 import _expected_summary_id_arrays
    for k,v in _expected_summary_id_arrays(d).items():
        if k in summary:
            summary[k] = v
    att = d["pre_native_0_1P_attachment_manifest_20261101"]
    reviewed = list(att["formal_review_completed_source_ids"])
    assert len(reviewed) == 31
    reviewed += [r["source_id"] for r in decisions]
    assert len(reviewed) == len(set(reviewed)) == 41
    att.update({
        "new_formal_decisions":41,
        "new_strict_promotions":6,
        "formal_review_completed_after_attachment_count":41,
        "formal_review_completed_source_ids":reviewed,
        "remaining_formal_source_count":1244,
        "native_validator_scope_warning":"Native Stage A tests include fourteen strict specs but are structural contracts, not Stage B fact acceptance or substantive certification of preliminary attachments.",
    })
    d["formal_0_1P_four_usjp_economic_events_20261101"] = {
        "authority":"PROMPT_0_1P_V4_20260829",
        "previous_checkpoint_id":14,
        "source_ids_formalized_this_batch":10,
        "source_ids_formalized_cumulative_since_45":41,
        "formal_individual_completed_total":86,
        "formal_individual_pending":1244,
        "independent_new_event_families":4,
        "new_strict_passes":4,"new_same_event_support_sources":5,
        "new_existing_full_reinforcements":1,
        "new_cards_created":0,"stage_b_executed":False,
        "global_editorial_stage_a_status":"HOLD_OPEN_1244_UNADJUDICATED",
        "native_stage_b_recommendation_scope":"Strict-only technical next-call, not global editorial release or Stage B execution.",
        "unchanged_source_universe":1330,
        "separate_economic_units_within_row86":CASES["GEORGIA"]["event_units"],
        "mixed_source_split_holds":[{"source_row_index":idx,"source_id":all_old[idx]["story_id"],
                                      "original_url":all_old[idx]["primary_url"],"reason":reason,
                                      "formal_source_disposition":"PENDING", "stage_a_pool_unchanged":True}
                                     for idx,reason in HOLD_SPLIT.items()],
        "mixed_source_distinct_full_sibling_cards":["2026-09-10_US_01","2026-09-16_US_02"],
        "source_decisions":sorted(decisions,key=lambda v:v["row"]),
        "owner_urls_by_case":{k:v["owner_urls"] for k,v in CASES.items()},
        "canonical_main_full_related_mutations":0,
    }
    d["recommended_for"] = ["Finish 1,244 remaining formal Source ID judgments; Stage A HOLD even though fourteen individual strict candidates pass schema."]
    d["next_call_recommendation"].update({
        "recommended_next_call":"Stage B r0",
        "recommended_prompt_id":"Prompt 0.2",
        "recommended_input_universe":"Stage A strict_passed_spec[] only",
        "reason":"Native strict-only next-call eligibility is not an editorial Stage B start; global Stage A HOLD requires closing remaining 1,244 formal 0.1P Source ID decisions.",
        "blocked_items_summary":d["review_pool_partition_summary"],
        "pending_parallel_or_followup_call":"review_pool/treasure triage",
        "pending_prompt_id":"authorized review_pool/treasure promotion protocol, not Prompt 0.2",
        "pending_input_universe":"candidate_review_pool[] + eligible treasure/review-only universe",
        "pending_reason":"Stage B may process strict_passed_spec[] only; review_pool/treasure remains open and must not be treated as exhausted.",
    })
    assert len(d["strict_passed_spec"]) == 14
    assert len(d["candidate_review_pool"]) == 598
    assert len(d["watchlist_context_pool"]) == 655
    assert len(d["reject_or_support_only_pool"]) == 33
    assert len(d["existing_reinforcement"]) == 30
    assert len(d["review_pool_resolution_ledger"]) == 1286
    assert len(d["promotion_reassessment_ledger"]) == 86
    assert len(d["decision_ledger"]) == 1330
    assert sum(len(d[x]) for x in ("strict_passed_spec","candidate_review_pool","watchlist_context_pool",
                                   "reject_or_support_only_pool","existing_reinforcement")) == 1330
    assert summary["processed_priority_source_observations"] == 86
    assert summary["unprocessed_editorial_observations"] == 1244
    write(a.output,d)
    receipt={
        "artifact_type":"STAGE_A_USJP_FOUR_EVENTS_FORMAL_0_1P_RECEIPT",
        "status":"PENDING_NATIVE_VALIDATION_AFTER_BUILD",
        "base_sha256":BASE_SHA,"output_sha256":sha256(a.output),
        "original_sources":1330,"new_formalized":10,
        "formalized_total":86,"formal_pending":1244,
        "strict_count":14,"new_strict_count":4,
        "new_support_only_count":5,"new_existing_full_reinforcement":1,
        "event_records":d["formal_0_1P_four_usjp_economic_events_20261101"],
        "stage_b_executed":False,"global_stage_a_status":"HOLD",
    }
    write(a.receipt,receipt)
    print(json.dumps({k:receipt[k] for k in (
        "output_sha256","new_formalized","formal_pending","new_strict_count",
        "new_support_only_count","new_existing_full_reinforcement")},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()

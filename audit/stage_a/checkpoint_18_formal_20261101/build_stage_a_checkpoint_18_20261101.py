#!/usr/bin/env python3
"""CP18: independently formalize six previously pending Source IDs.

Source/act grain matters: two independent events were hidden in mixed ESS news;
the previously announced ESS tender registration is a dated procedural follow-up,
not a second 1,180 MW tender. All authoritative 0.1P and Stage B boundaries stay.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from build_stage_a_checkpoint_16_remaining_cases_20261101 import formal_watch
from build_stage_a_formal_kr_two_events_20261101 import coverage_maps, read, sha256, support_row, write
from build_stage_a_formal_usjp_four_events_20261101 import execution_strict

BASE_SHA = "d36893b263dfed269388d40680a7896ebee0b68127619cded66baeb951084fef"
BASE_FORMAL = 99

EVENTS = {
    "SKON_LNF": {
        "case_id":"KR_SKON_LNF_LFP_CATHODE_SUPPLY_CONTRACT_20260917",
        "rows":[48,228],"representative":48,"date":"2026-09-17",
        "owner":"SK On / L&F (contract issuer and counterparty)",
        "owner_urls":[
            "https://askinno.com/archives/171570",
            "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20260917800658",
            "https://www.newswire.co.kr/newsRead.php?no=1042886",
        ],
        "title":"SK온–엘앤에프, ESS용 LFP 양극재 1,617억 원 중장기 공급계약",
        "region":"KR","geographic_scope":"Korea SK On Seosan; prospective SK On Georgia US cell lines",
        "summary":"SK온·엘앤에프 9월17일 ESS용 LFP 양극재 중장기 공급계약. 회사 발표는 약 1,600억원, 엘앤에프 단일판매 공시에는 1,617억 3,306만원(USD118.2m, 계약상 최소구매 수량·기준 판가). 계약 기한은 2028년12월31일이며 2031년까지 연장할 수 있는 옵션은 아직 행사되지 않았다. 서산·조지아 현장 투입·실제 납품 완료/수익 인식은 후속확인.",
        "prior_state":"SK On's ESS strategy and earlier contracted cathode supply were discussed, but this L&F/SK On September17 USD118.2m bilateral minimum-purchase agreement was a separate named signed supplier contract. Existing locked Full 2026-09-22_KR_01 involves a different supplier, POSCO Future M.",
        "new_fact":"September17 L&F formally reported a signed USD118.2m (KRW161,733,060,000 at notice rate) ESS LFP cathode supply-and-purchase agreement with SK On and designated affiliates through 2028-12-31; SK On's dated owner newsroom confirms signing and planned Korea/US manufacturing use.",
        "increment":"A contracted domestic LFP cathode input supply obligation is a direct Korean/non-Chinese materials commercialization and downstream ESS supply-chain milestone, independent of the September22 market procurement notice and separate POSCO Future M/SK On supplier contract.",
        "must_not":"KRW161,733,060,000 is notice-rate value of 3-year minimum purchase units at recent raw-material-linked prices, not cash received, annual revenue, final physical deliveries or nonadjustable order book. No advance payment. Optional 2029-2031 extension is not exercised. Seosan 3GWh line conversion and US Georgia ESS application are plans, not new completed factories or tender wins. The September19 news forecast about a 560MW tender was superseded by September22 actual 1,180MW notice.",
        "event_units":["SEP17_SIGNED_LNF_SKON_LFP_CATHODE_SUPPLY_PURCHASE_CONTRACT",
                       "THREE_YEAR_MINIMUM_PURCHASE_BASE_KRW161_733_060_000",
                       "POTENTIAL_THREE_YEAR_EXTENSION_NOT_EXERCISED",
                       "PROSPECTIVE_SEOSAN_GEORGIA_CELL_APPLICATION_NO_COD"],
        "score":[17,20,0,9,3,4,3,2],
        "anchors":["execution_event_anchor"],
        "classification_lenses":["materials_midstream","ESS supply-chain non-China sourcing","capital_allocation_cashflow"],
        "route":"execution_anchor_route","execution_type":"executed_lfp_cathode_supply_purchase_contract",
        "tech_stage":None,"technology_level":"not_applicable",
        "tech_gap":"No independent high-density LFP cathode chemistry performance, actual batch qualifications, mass shipment records or installed ESS acceptance yet.",
        "system_denominator":"Contract USD118,200,000 = KRW161,733,060,000 at September17 KRW1368.30/USD; 7.51% of L&F 2025 consolidated revenue KRW2,154,938,965,103. 2026-09-17 to 2028-12-31, not three fully elapsed calendar years.",
        "affected":["L&F LFP cathode commercialization","SK On Seosan and Georgia ESS cell sourcing", "Korean non-Chinese LFP component supply chains"],
        "procedure":"Named SK On/L&F contract September17; DART receipt 20260917800658 (primary portal URL; direct portal rendering blocked in current web tool), cross-checked with SK On original newsroom and L&F issuer-distributed news release.",
        "implementation":"Minimum purchase quantities across SK On designated domestic/international production; unit value subject to feedstock pricing, actual delivery schedules and later settlement.",
        "funding":"Private commercial supplier contract, no verified upfront payment; not 2026 ESS central-market awarded capacity.",
        "next_trigger":"Official DART/KRX full filing readback and amended terms, 2026-28 L&F quarterly shipped cathode volumes/revenue, SK On Seosan/Georgia line conversion and specific ESS tender award separately.",
        "related_full":[],
        "related_reason":"Distinct from Full 2026-09-22_KR_01 POSCO Future M/SK On cathode supply; also distinct from KR_ESS_CENTRAL_TENDER_1180MW_20260922 procurement notice.",
        "staged_questions":["Check SK On-L&F actual September17 bilateral contract vs later SK On-POSCO Future M contract and government ESS procurement.",
                            "Check DART 20260917800658 number-based minimum-purchase value and variable pricing, not revenue booked.",
                            "Confirm actual LFP shipment/qualification and no unverified 2026 commercial production."],
        "evidence":[
            {"source_or_document_class":"SK On first-party September17 press release", "exact_claim_or_metric":"2026-09-17 signed SK On–L&F LFP cathode supply-and-purchase contract with approximate KRW160bn contract price and prospective Seosan/Georgia manufacturing destinations."},
            {"source_or_document_class":"L&F September17 corporate disclosure DART receipt 20260917800658", "exact_claim_or_metric":"Minimum purchase reference KRW161,733,060,000, 7.51% of 2025 sales, contract end 2028-12-31, variable prices and unexercised extension; direct original DART portal readback required before Stage B."},
            {"source_or_document_class":"SK On and L&F original shipment invoices and production batch records", "exact_claim_or_metric":"First actual cathode tonne deliveries, acceptance, invoicing, revenue recognition and Seosan/Georgia source traceability."},
        ],
        "confirm":[
            {"measurable_event_or_metric":"First invoiced LFP cathode tonnes and identified SK On Seosan ESS cell batch usage through 2028-12-31", "interpretation_effect":"Verified shipped tonnage would strengthen operating-flow interpretation; absence would weaken it."},
            {"measurable_event_or_metric":"DART filing amendment and realized raw-material-index price adjustment against disclosed KRW161,733,060,000", "interpretation_effect":"Confirmed original filing would strengthen contract-value confidence; contradictory amendments would weaken the stated value interpretation."},
            {"measurable_event_or_metric":"KPX public award decision and named SK On battery sourcing under distinct ESS tenders", "interpretation_effect":"Confirmed award would strengthen downstream demand linkage; missing award would invalidate any asserted tender win."},
        ],
        "cat":"Materials","sub_cat":"LFP_CATHODE_SIGNED_SUPPLY_CONTRACT",
        "legal_stage":None,"policy_stage":None,"law_type":"Bilateral commercial LFP cathode supply-and-purchase agreement, not a regulation",
        "mandatory":"Contractual period 2026-09-17 through 2028-12-31; optional extension separate",
    },
    "RE_MAGNET": {
        "case_id":"KR_EOL_EV_HEV_MOTOR_RE_MAGNET_PILOT_MOU_20260922",
        "rows":[244,614],"representative":244,"date":"2026-09-22",
        "owner":"Ministry of Climate, Energy and Environment, Korea Environment Corporation, Hyundai Motor, car dismantlers association",
        "owner_urls":[
            "https://admin.korea.kr/briefing/pressReleaseView.do?newsId=156782918",
            "https://www.korea.kr/news/policyNewsView.do?newsId=148972528",
            "https://ev.or.kr/nportal/board/generalView.do?ARTC_ID=25752&boardType=report",
        ],
        "title":"정부·현대차, 폐차 모터 희토자석 회수·실증 시범사업 업무협약",
        "region":"KR","geographic_scope":"South Korea end-of-life EV and HEV motor recycling chain",
        "summary":"기후부·한국환경공단·현대차·폐차협회가 9월22일 폐차 구동모터 희토 영구자석 회수체계 시범사업 업무협약을 체결. 일반 폐차의 회수·유통 지원과 현대차 시험차 해체·회수 실증 두 트랙. 연간 약 1만4천대·최대 15톤은 정부가 밝힌 예상 시범 처리량이며 실제 회수실적이나 상용 재활용률이 아님.",
        "prior_state":"Korean recycling practices typically recovered steel, copper or aluminum from end-of-life vehicle motors without an established national permanent-magnet separation network; earlier May2026 magnet recovery pilot concerned discarded computers, not this vehicle-motor MoU.",
        "new_fact":"September22 ministry/Hyundai/K-eco/dismantler association pilot agreement concluded to organize EOL motor collection/trading and separate Hyundai engineering test-car dismantling and magnet-material recovery trials, with prospective capacity from 14,000 cars and up to 15 tonnes/year magnets.",
        "increment":"A named cross-industry signed recycling-pilot governance and industrial procurement/routing arrangement creates a concrete initial Korean rare-earth magnet circular supply-chain pathway separate from ESS central-market procurement and September23 critical-mineral statutory planning.",
        "must_not":"14,000 end-of-life vehicles and 15 metric tonnes are expected annual pilot potential, NOT magnets recovered, sold, certified metal yield or current plant nameplate; test-car recovery validation is planned, not proven. MoU does not establish binding nationwide collection law or completed recycler award. Separate from 1,180MW ESS tender and the September23 resource-security four plans.",
        "event_units":["SEP22_SIGNED_GOV_HYUNDAI_Dismantler_RE_MAGNET_PILOT_MOU",
                       "PLANNED_ELV_COLLECTION_AND_DISTRIBUTION_TRACK",
                       "PLANNED_HYUNDAI_TEST_CAR_DISMANTLING_RECYCLING_VALIDATION",
                       "FOURTEEN_THOUSAND_VEHICLE_FIFTEEN_TON_TARGET_NOT_REALIZED"],
        "score":[16,17,5,6,8,4,2,2],
        "anchors":["execution_event_anchor"],
        "classification_lenses":["circular_recycling","upstream_critical_minerals","industrial_partner_pilot"],
        "route":"execution_anchor_route","execution_type":"signed_eol_motor_rare_earth_magnet_pilot_mou",
        "tech_stage":"pilot","technology_level":"pilot_precommercial",
        "tech_gap":"Physical magnet separation performance, actual scrap supplier selection, recovery yields and composition are not demonstrated.",
        "system_denominator":"Ministry prospective annual throughput 14,000 EOL EV/HEV drive motors; up to 15 metric tonnes of recovered permanent magnets; estimated motor content ~0.75-1.5kg by vehicle. None realized as of 2026-09-22.",
        "affected":["End-of-life EV/HEV dismantlers","Korea Environment Corporation recycler sourcing","Hyundai test-vehicle recycling","Korean rare-earth magnet circular-materials security"],
        "procedure":"Official ministry September22 MoU announcement and ministry September23 after-signing confirmation. Two independently distinguishable workflows under one interparty project.",
        "implementation":"K-eco to support recyclers' bidding/reporting, dismantlers to gather motor feedstock, Hyundai to provide motor magnet location and removal methods; test vehicles use sandbox experimental process.",
        "funding":"MoU and proposed pilot support; no substantiated public budget, recycler procurement amount, private investment or operating recovery revenue.",
        "next_trigger":"Signed MoU and pilot design annex, recycler award, actual EV/HEV motor tonnes processed and measured magnet kilogram purity recovery, sandbox performance and adopted recycling standards.",
        "related_full":[],
        "related_reason":"Not same act as earlier May e-waste hard-disk magnet recycling pilot, September22 ESS procurement or September23 critical-mineral plan adoption.",
        "staged_questions":["Confirm September22 post-signature ministry notice versus pre-scheduled agreement and 9/23 summary, no new policy regulation in force.",
                            "Distinguish 14k vehicles/15t projected annual recovery from actual measured recovery.",
                            "Verify separately when recycler supply contracts or sandbox trials actually commence."],
        "evidence":[
            {"source_or_document_class":"Ministry September22 first-party official press release", "exact_claim_or_metric":"Signed 2026-09-22 MOU, two pilot tracks, estimated 14,000 end-of-life vehicles and potential 15 metric tonnes per year, not realized yield."},
            {"source_or_document_class":"Ministry September23 official government after-signing notice", "exact_claim_or_metric":"September22 executed signature date and distinct participants; no verified recovered permanent-magnet tonnage."},
            {"source_or_document_class":"Korea Environment Corporation original procurement award, Hyundai test-car motor logs and pilot assay reports", "exact_claim_or_metric":"Recycler name and award date, motor units and kilograms collected, magnet kilograms separated and purity/yield measured."},
        ],
        "confirm":[
            {"measurable_event_or_metric":"K-eco recycler procurement award plus independently counted EV/HEV motor collection tonnes", "interpretation_effect":"Verified award and volumes would strengthen executed pilot status; no award would weaken implementation claims."},
            {"measurable_event_or_metric":"Actual permanent-magnet recovered tonnes and assay purity compared with prospective 15 metric tonnes per year", "interpretation_effect":"Measured recovery would strengthen circular supply-chain evidence; zero recovery would invalidate achieved-yield statements."},
            {"measurable_event_or_metric":"Published ministry rule amendment with effective date and compulsory motor magnet collection metric", "interpretation_effect":"Binding amendment would confirm regulatory change; no publication would invalidate mandatory nationwide collection inference."},
        ],
        "cat":"Circular","sub_cat":"RARE_EARTH_MAGNET_EV_MOTOR_RECYCLING_PILOT",
        "legal_stage":None,"policy_stage":None,
        "law_type":"Government-industry pilot memorandum of understanding, not a final binding recycling mandate",
        "mandatory":"Signed pilot MoU dated 2026-09-22; no national mandatory start date",
    },
}

FACTORIAL = {
    "case_id":"US_JP_FACTORIAL_MITSUI_SULFIDE_JDA_20260917",
    "date":"2026-09-17",
    "must_not":"Mitsui JDA is already a retained separate 0.1P strict act. Karma partnership dates to 2026-02-05 and official Kaveya scheduled late2027 vs subsequent interview 2028; not a new September order or achieved car delivery. Robotics/aircraft claims are market outlook, not signed September contracts.",
    "owner_urls":["https://www.globenewswire.com/news-release/2026/09/17/3363848/0/en/mitsui-kinzoku-partners-with-factorial-to-scale-all-solid-state-battery-manufacturing.html",
                  "https://ir.factorialenergy.com/news-releases/news-release-details/karma-automotive-and-factorial-announce-first-solid-state"],
    "prior_state":"September17 Mitsui sulfide-electrolyte JDA is formally represented by original source row126; February5 Karma agreement pre-dates this September interview.",
    "new_fact":"InsideEVs interview repeated the Mitsui owner JDA, referenced earlier SK On/PowerCo ties and older Karma plans; no independently signed additional September production order was demonstrated.",
}

KPX_REGISTER = {
    "case_id":"KR_ESS_CENTRAL_TENDER_REGISTRATION_WINDOW_20260928",
    "rows":[916],"date":"2026-09-28",
    "owner_urls":["https://www.kpx.or.kr/board.es?act=view&bid=0042&list_no=78164&mid=a11201000000",
                  "https://www.kpx.or.kr/boardDownload.es?bid=0042&list_no=78164&seq=1"],
    "status":"FORMAL_WATCH_PREANNOUNCED_REGISTRATION_STAGE_NO_NEW_AWARD",
    "why":"KPX official September22 34-page tender PDF page3 already set bidder registration for September28 09:00 through October2 15:00; the September28 news reports commencement of a scheduled procedural phase, not new 1,180MW capacity, bid completion, selected operator, contracted capacity, or ESS COD. Separate registration lifecycle is preserved from the September22 announcement; no independent change to awarded market output established.",
    "future":"KPX proof of actual bidder registrations, proposal submission by November11 15:00 and later November award decision, signed project agreements and COD; evaluate any amended original KPX schedule separately.",
}

EXTRA_EDGES = {
    48:[{"event":"KR_SKON_LNF_LFP_CATHODE_SUPPLY_CONTRACT_20260917","role":"signed_supply_contract_supporting_article"},
        {"event":"KR_ESS_CENTRAL_TENDER_1180MW_20260922","role":"preannouncement_forecast_only_not_official_notice","warning":"September19 560MW estimate contradicted September22 confirmed 1180MW announcement."}],
    228:[{"event":"KR_SKON_LNF_LFP_CATHODE_SUPPLY_CONTRACT_20260917","role":"older_signed_sourcing_event_in_later_market_report"},
         {"event":"KR_ESS_CENTRAL_TENDER_1180MW_20260922","role":"separate_government_tender_announcement"},
         {"event":"LGES_DOMESTIC_LFP_SUPPLY_CHAIN_STRATEGY_UNAWARDED","role":"future_strategy_no_vendor_contract_or_award_verified"}],
    244:[{"event":"KR_EOL_EV_HEV_MOTOR_RE_MAGNET_PILOT_MOU_20260922","role":"independent_mou_event"},
         {"event":"KR_ESS_CENTRAL_TENDER_1180MW_20260922","role":"separate_policy_news_in_same_article"}],
    614:[{"event":"KR_EOL_EV_HEV_MOTOR_RE_MAGNET_PILOT_MOU_20260922","role":"same_article_duplicate_source_observation"},
         {"event":"KR_ESS_CENTRAL_TENDER_1180MW_20260922","role":"same_article_separate_tender_claim"}],
    8:[{"event":"US_JP_FACTORIAL_MITSUI_SULFIDE_JDA_20260917","role":"same_JDA_interview_source"},
       {"event":"FACTORIAL_KARMA_20260205","role":"earlier_partner_deal_mentioned_in_interview","warning":"Owner original named late2027 Kaveya vs interview 2028 date; not a new September order."}],
    916:[{"event":"KR_ESS_CENTRAL_TENDER_REGISTRATION_WINDOW_20260928","role":"preannounced_procedural_followup_watch"},
         {"event":"KR_ESS_CENTRAL_TENDER_1180MW_20260922","role":"parent_tender_notice_no_additional_1180MW"}],
}


def main() -> None:
    ap=argparse.ArgumentParser()
    for field in ("base","full","output","receipt"):
        ap.add_argument("--"+field,required=True,type=Path)
    a=ap.parse_args()
    assert sha256(a.base)==BASE_SHA
    d,full=read(a.base),read(a.full)
    assert len(full["cards"])==1676 and len(d["decision_ledger"])==1330
    assert len(d["promotion_reassessment_ledger"])==BASE_FORMAL
    assert len(d["strict_passed_spec"])==18 and len(d["candidate_review_pool"])==586
    assert len(d["watchlist_context_pool"])==660 and len(d["reject_or_support_only_pool"])==36
    old={r["source_row_index"]:r for r in d["decision_ledger"]}
    cand={r["source_row_index"]:r for r in d["candidate_review_pool"]}
    watches={r["source_row_index"]:r for r in d["watchlist_context_pool"]}
    assert set(EXTRA_EDGES)=={8,48,228,244,614,916}
    assert set(EXTRA_EDGES)-{8}<=set(cand) and 8 in watches
    ledger={r["story_id"]:r for r in d["decision_ledger"]}
    review={r["story_id"]:r for r in d["review_pool_resolution_ledger"]}
    template=d["strict_passed_spec"][-1]
    decisions=[]
    promoted,support,watch=set(),set(),set()
    strict_specs=[]

    def attach(row:dict,idx:int,classification:str) -> None:
        row["formal_0_1P_cp18_source_to_economic_act_edges_20261101"]=copy.deepcopy(EXTRA_EDGES[idx])
        row["cp18_source_identity_preserved"]={
            "story_id":old[idx]["story_id"],"source_row_index":idx,
            "headline_raw":old[idx]["headline_raw"],"primary_url":old[idx]["primary_url"],
        }
        decisions.append({"row":idx,"source_id":old[idx]["story_id"],
                          "result":classification,"economic_act_edges":EXTRA_EDGES[idx],
                          "source_url":old[idx]["primary_url"]})

    def formal_entry(idx:int,event_id:str,before:str,after:str,status:str,resolved:str,remaining:str,owner_urls:list[str]) -> None:
        d["promotion_reassessment_ledger"].append({
            "candidate_id":old[idx]["story_id"],"economic_event_cluster_id":event_id,
            "before_pool":before,"after_pool":after,
            "promotion_reassessment_status":status,
            "resolved":resolved,"remaining":remaining,
            "source_candidates":owner_urls,"source_observation_preserved":True,
        })

    def update_review(idx:int, after:str, reason:str, trigger:str) -> None:
        ent=review[old[idx]["story_id"]]
        ent.update({
            "original_review_pool_partition":after,"current_disposition":after,
            "disposition_basis":reason,
            "carry_forward_policy":"support_source_only" if after=="reject_or_support_only_pool" else "carry_forward_to_watchlist",
            "next_action_condition":trigger,
            "final_review_pool_disposition":"support_source_only_after_review" if after=="reject_or_support_only_pool" else "watchlist_only_after_review",
            "reviewed_by_stage_or_pass":"PROMPT_0_1P_V4_20260829 owner first CP18",
            "review_artifact_id":"STAGE_A_CHECKPOINT_18_FORMAL_20261101",
        })

    for e in EVENTS.values():
        obs=[old[i] for i in e["rows"]]
        rep=old[e["representative"]]
        # Native Stage A v4 requires string arrays even though lineage's semantic
        # validator can also understand structured pairs. Preserve both the
        # source/document class and the measurable interpretation in each string.
        native_event=copy.deepcopy(e)
        native_event["evidence"]=[
            "Official contract or filing document — "+v["source_or_document_class"]+
            ": verify exact target "+v["exact_claim_or_metric"]
            for v in e["evidence"]
        ]
        native_event["confirm"]=[
            "Confirmation metric — "+v["measurable_event_or_metric"]+
            "; interpretation: "+v["interpretation_effect"]
            for v in e["confirm"]
        ]
        s=execution_strict(rep,template,native_event,obs)
        s.update({
            "headline":e["title"],"title_raw":e["title"],
            "assessment_method":"PROMPT_0_1P_V4_20260829 owner release + official original stage + Full1676 contrast",
            "publication_date":e["date"],"representative_date":e["date"],
            "date_role":{
                **s["date_role"],"event_date":e["date"],"announcement_date":e["date"],
                "publication_date":e["date"],
                "representative_date_basis":"Owner September original economic act, NOT news article publish/ingest date.",
            },
            "formal_0_1P_cp18_strict_event_20261101":{
                "case_id":e["case_id"],"original_representative_source_row":rep["source_row_index"],
                "owner_urls":e["owner_urls"],"stage_b_fact_adoption":False,
                "new_economic_event":True,"not_canonical_card_write":True,
            },
        })
        assert not s["stage_b_authorized"] and not s["accepted_facts_approved"]
        d["strict_passed_spec"].append(s)
        strict_specs.append(s)
        ledger[rep["story_id"]].update(copy.deepcopy(s))
        attach(ledger[rep["story_id"]],rep["source_row_index"],"FORMAL_STRICT_EVENT_SELECTOR_ONLY")
        promoted.add(rep["story_id"])
        formal_entry(rep["source_row_index"],e["case_id"],rep["stage_a_pool"],"strict_passed_spec",
                     "PROMOTED_VALIDATED_STRICT",e["new_fact"],e["must_not"],e["owner_urls"])
        for idx in e["rows"]:
            if idx==e["representative"]:
                continue
            r=old[idx]
            su=support_row(r,e,rep["story_id"])
            su["new_verified_fact"]="Supports a different signed event contained within a mixed ESS article: "+e["new_fact"]
            su["remaining_uncertainty"]="Verify all article sibling event IDs separately; "+e["must_not"]
            if idx==614:
                su["same_exact_article_url_duplicate_of"] = old[244]["story_id"]
                su["mixed_article_primary_economic_act_count_minimum"] = 2
            ledger[r["story_id"]].update(copy.deepcopy(su))
            d["reject_or_support_only_pool"].append(su)
            attach(ledger[r["story_id"]],idx,"FORMAL_SUPPORT_ONLY_MIXED_EVENT_SOURCE")
            support.add(r["story_id"])
            update_review(idx,"reject_or_support_only_pool",su["final_reason"],"New independent signed stage or verified fulfillment required to reopen.")
            formal_entry(idx,e["case_id"],r["stage_a_pool"],"reject_or_support_only_pool",
                         "FORMAL_SAME_EVENT_SUPPORT_ONLY",su["final_reason"],e["must_not"],e["owner_urls"])

    idx=8
    old8=old[idx]
    existing=old[126]["story_id"]
    assert any(x["candidate_id"]==existing and x["after_pool"]=="strict_passed_spec" for x in d["promotion_reassessment_ledger"])
    s8=support_row(old8,FACTORIAL,existing)
    s8["new_verified_fact"]="September17 Factorial and Mitsui JDA confirmed in first-party release; Karma collaboration first announced February5, so no independent September Karma agreement or car delivery."
    s8["remaining_uncertainty"]="Karma planned vehicle date differs between owner February5 (late2027 Kaveya) and September interview (2028); avoid false new September launch."
    s8["factorial_owner_prior_agreement_date"]="2026-02-05"
    ledger[old8["story_id"]].update(copy.deepcopy(s8))
    d["reject_or_support_only_pool"].append(s8)
    attach(ledger[old8["story_id"]],idx,"FORMAL_SUPPORT_EXISTING_FACTORIAL_JDA_HISTORICAL_KARMA_DISTINCT")
    support.add(old8["story_id"])
    update_review(idx,"reject_or_support_only_pool",s8["final_reason"],"Reopen only for a new dated signed OEM order or proven product delivery.")
    formal_entry(idx,FACTORIAL["case_id"],old8["stage_a_pool"],"reject_or_support_only_pool",
                 "FORMAL_EXISTING_STRICT_SAME_JDA_SUPPORT_SOURCE",s8["new_verified_fact"],
                 s8["remaining_uncertainty"],FACTORIAL["owner_urls"])

    idx=916
    row=old[idx]
    w=formal_watch(row,KPX_REGISTER,[row],row["story_id"])
    w.update({
        "lineage_parent_stage_a_economic_cluster":"KR_ESS_CENTRAL_TENDER_1180MW_20260922",
        "policy_procedure_stage":"bidder_registration_window_open_as_preannounced_in_original_tender_PDF",
        "actual_registration_quantity_verified":False,
        "not_second_tender_announcement":True,
    })
    ledger[row["story_id"]].update(copy.deepcopy(w))
    d["watchlist_context_pool"].append(w)
    attach(ledger[row["story_id"]],idx,"FORMAL_WATCH_PROCEDURAL_FOLLOWUP_NO_NEW_AWARD")
    watch.add(row["story_id"])
    update_review(idx,"watchlist_context_pool",KPX_REGISTER["why"],KPX_REGISTER["future"])
    formal_entry(idx,KPX_REGISTER["case_id"],row["stage_a_pool"],"watchlist_context_pool",
                 KPX_REGISTER["status"],KPX_REGISTER["why"],KPX_REGISTER["future"],KPX_REGISTER["owner_urls"])

    completed=promoted|support|watch
    assert len(promoted)==2 and len(support)==3 and len(watch)==1 and len(completed)==6
    d["candidate_review_pool"]=[r for r in d["candidate_review_pool"] if r["story_id"] not in completed]
    d["watchlist_context_pool"]=[r for r in d["watchlist_context_pool"] if r["story_id"] not in completed]
    # Append the sole newly formalized watch *after* removing any completed watch IDs.
    d["watchlist_context_pool"].append(w)
    d["review_pool_resolution_ledger"]=[r for r in d["review_pool_resolution_ledger"] if r["story_id"] not in promoted]
    expected={"strict_passed_spec":20,"candidate_review_pool":581,
              "watchlist_context_pool":660,"reject_or_support_only_pool":39,
              "existing_reinforcement":30,"review_pool_resolution_ledger":1280,
              "promotion_reassessment_ledger":105}
    assert all(len(d[k])==n for k,n in expected.items()),{k:len(d[k]) for k in expected}
    assert sum(len(d[k]) for k in ("strict_passed_spec","candidate_review_pool","watchlist_context_pool",
                "reject_or_support_only_pool","existing_reinforcement"))==1330
    ids=[r["story_id"] for r in d["decision_ledger"]]
    assert len(ids)==len(set(ids))==1330
    assert len({r["candidate_id"] for r in d["promotion_reassessment_ledger"]})==105
    assert all(not r.get("stage_b_authorized") and not r.get("accepted_facts_approved") and not r.get("canonical_card_write_allowed") for r in strict_specs)

    summ=d["summary"]
    summ["strict_passed_spec_count"]=20
    summ["existing_reinforcement_count"]=30
    summ["duplicate_or_reinforcement_count"]=30
    summ["needs_review_count"]=1280
    summ["processed_priority_source_observations"]=105
    summ["processed_priority_economic_clusters"]+=2
    summ["unprocessed_editorial_observations"]=1225
    summ["pool_counts"]={k:len(d[k]) for k in (
        "strict_passed_spec","candidate_review_pool","watchlist_context_pool",
        "reject_or_support_only_pool","existing_reinforcement","rejected","support_source_only")}
    d["review_pool_partition_summary"]={k:len(d[k]) for k in (
        "candidate_review_pool","watchlist_context_pool","reject_or_support_only_pool")}
    coverage_maps(d)
    import sys
    sys.path.insert(0,str(a.base.resolve().parent))
    from validation_scripts.stage_a_full_v3_completeness_review4943656188 import _expected_summary_id_arrays
    for k,v in _expected_summary_id_arrays(d).items():
        if k in summ:
            summ[k]=v
    att=d["pre_native_0_1P_attachment_manifest_20261101"]
    prior=att["formal_review_completed_source_ids"]
    now=[r["source_id"] for r in sorted(decisions,key=lambda r:r["row"])]
    assert len(prior)==54 and len(set(prior))==54 and set(now).isdisjoint(prior)
    att.update({
        "new_formal_decisions":60,"new_strict_promotions":12,
        "formal_review_completed_after_attachment_count":60,
        "formal_review_completed_source_ids":prior+now,
        "remaining_formal_source_count":1225,
        "native_validator_scope_warning":"Native contracts cover 20 strict specs but cannot authorize global Stage B: 1225 original Source IDs still lack individual formal Stage A dispositions.",
    })
    original54=read(Path(__file__).with_name("PRE_NATIVE_54_20261031.json"))
    those54={i for e in original54["case_definitions"] for i in e["source_row_indices"]}
    decided_index={r["source_row_index"] for r in d["decision_ledger"]
                   if r["story_id"] in set(att["formal_review_completed_source_ids"])}
    assert len(those54)==54 and those54.issubset(decided_index),sorted(those54-decided_index)
    d["formal_0_1P_cp18_completed_original54_20261101"]={
        "authority":"PROMPT_0_1P_V4_20260829",
        "base_cp16_sha256":BASE_SHA,
        "source_ids_formally_resolved_this_batch":6,
        "new_strict_event_count":2,"new_support_source_count":3,"new_watch_count":1,
        "cumulative_formal_individual_count":105,"remaining_unadjudicated_source_count":1225,
        "pre_native_original54_source_ids_fully_resolved":True,
        "related_mixed_source_row228_formally_resolved":True,
        "cp17_error_corrigendum":{
            "description":"The earlier CP17 article URL key incorrectly treated bbsSeq=443 as document identity and ignored docSeq; DAPA rows1297/1309 are separate administrative notices.",
            "corrected_source_review_units":1130,"corrected_duplicate_observation_reduction":101,
            "source_observations_preserved":1231,"no_formal_merge_of_dapa_rows":True,
        },
        "case_results":sorted(decisions,key=lambda r:r["row"]),
        "owner_primary_urls_by_case":{e["case_id"]:e["owner_urls"] for e in EVENTS.values()},
        "no_extra_cards_for_registration_or_factorial":True,
        "new_published_cards":0,"stage_b_executed":False,
        "global_stage_a_status":"HOLD_OPEN_1225_UNADJUDICATED",
        "canonical_main_full_related_mutations":0,
    }
    d["recommended_for"]=["Finish 1225 outstanding formal Source ID owner-first economic-act dispositions. Stage A HOLD despite 20 strict selectors."]
    d["next_call_recommendation"].update({
        "recommended_next_call":"Stage B r0","recommended_prompt_id":"Prompt 0.2",
        "recommended_input_universe":"Stage A strict_passed_spec[] only",
        "reason":"Native strict-only next-call eligibility is not Stage B global editorial authorization; 1225 source-level judgments still open.",
        "blocked_items_summary":d["review_pool_partition_summary"],
        "pending_parallel_or_followup_call":"review_pool/treasure triage",
        "pending_input_universe":"candidate_review_pool[] + eligible treasure/review-only universe",
    })
    write(a.output,d)
    receipt={
        "artifact_type":"STAGE_A_CP18_COMPLETE_PRENATIVE54_AND_RELATED_20261101",
        "status":"PENDING_NATIVE_AND_INDEPENDENT_QC",
        "base_sha256":BASE_SHA,"output_sha256":sha256(a.output),
        "base_formal_ids":99,"new_formal_ids":6,"formal_total":105,
        "formal_pending":1225,"new_strict":2,"new_support":3,"new_watch":1,
        "strict_total":20,"original54_completed":True,
        "cp17_url_correction":d["formal_0_1P_cp18_completed_original54_20261101"]["cp17_error_corrigendum"],
        "source_decisions":sorted(decisions,key=lambda r:r["row"]),
        "no_stage_b":True,"global_stage_a_status":"HOLD","no_main_full_related_write":True,
    }
    write(a.receipt,receipt)
    print(json.dumps({k:receipt[k] for k in (
        "output_sha256","new_formal_ids","formal_total","formal_pending",
        "new_strict","new_support","new_watch","strict_total","original54_completed")},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()

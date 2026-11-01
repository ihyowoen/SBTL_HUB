#!/usr/bin/env python3
"""Stage A checkpoint #16: resolve seven first-owner economic case groups, 13 source IDs.

Formal means a completed Stage A source disposition, NOT publication or Stage B evidence
approval.  Repeated articles are preserved as source observations of one economic act.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from build_stage_a_formal_kr_two_events_20261101 import (
    build_strict, coverage_maps, read, sha256, support_row, write,
)
from build_stage_a_formal_usjp_four_events_20261101 import execution_strict

BASE_SHA = "8bd11020fea3c8874837fa2a30b5bab619e0174a7e92b43661d5c5b225a230c6"
BASE_COUNT = 86

CASES = {
    "ESVOLTA": dict(
        case_id="US_GOOGLE_ESVOLTA_GRANULAR_CERT_STORAGE_PILOT_20260917",
        rows=[19,123,468], representative=19, date="2026-09-17",
        owner="Quintrace, esVolta, LevelTen Energy; Google as pilot sponsor/buyer",
        owner_urls=[
            "https://www.esvolta.com/post/battery-storage-shift-pilot-demonstrates-how-hourly-renewable-certificates-can-power-the-next-phase",
            "https://www.quintrace.com/press-releases/battery-storage-shift-pilot",
        ],
        title="Google 후원 esVolta ESS 시간별 환경증서 실증 — 3개월 9.2GWh 운영 구간",
        region="US", geographic_scope="United States, Anole and Burksol battery assets",
        summary="esVolta·Quintrace·LevelTen의 9월17일 결과: Google이 후원하고 시간별 환경속성 이전을 계약한 3개월 파일럿. 운영 중인 Anole 240MW/480MWh, Burksol 100MW/200MWh에서 정해진 시간대의 충·방전 합계 9.2GWh를 제시. 독립적 시장 표준 확정이나 실제 수익금 공개는 아님.",
        prior_state="Existing 340MW/680MWh esVolta assets were already operating; annual renewable matching and evolving GHG Protocol accounting were not a certified universal storage-credit settlement method.",
        new_fact="September17 owners disclosed an executed Google-sponsored three-month storage-shift certificate demonstration with two identified operating BESS projects; combined window charging/discharging 9.2GWh and hourly tracking were reported.",
        increment="A named contractual dispatch/attribute-tracking pilot with reported field operation changes the battery environmental-attribute commercial validation stage; not merely a hypothetical certificate structure.",
        must_not="9.2GWh is the reported combined charge/discharge window activity, not independently proven net certified renewable MWh or payments; no generally binding SBTi/GHG Protocol standard, traded market volume, Google ownership of battery sites, or new 340MW commissioning.",
        event_units=["GOOGLE_SPONSORED_STORAGE_SHIFT_PILOT_CONTRACTS","TWO_EXISTING_BESS_REPORT_9_2GWH_WINDOW_DISPATCH","HOURLY_GRANULAR_CERTIFICATE_TRACKING_DEMONSTRATION"],
        score=[16,18,8,7,0,3,2,1], anchors=["execution_event_anchor","technology_commercialization_anchor"],
        classification_lenses=["AI/data-centre power/ESS","technology_transition_commercialization"],
        route="execution_anchor_route", execution_type="completed_operating_storage_certificate_field_pilot",
        tech_stage="field_demonstration", technology_level="pilot_precommercial",
        tech_gap="No independent EnergyTag auditor report, GHG Protocol adoption, independently audited certificate totals or realized operator revenue disclosed.",
        system_denominator="Two existing BESS facilities: Anole 240MW/480MWh plus Burksol 100MW/200MWh = 340MW/680MWh; 9.2GWh reported three-month window charging/discharging activity, not new storage capacity or separately certified delivered net energy.",
        affected=["esVolta existing Anole and Burksol battery assets","Google hourly clean-power attribute matching","Quintrace and LevelTen granular-certificate tracking services"],
        procedure="Commercial pilot results and contracted time-shifted environmental attributes reported in September17 issuer statements; certificates and payment amounts not independently evidenced.",
        implementation="Google specified charge/discharge windows; Quintrace matched hourly attributes and losses; LevelTen administered registry accounts; independently replicable third-party settlement remains to verify.",
        funding="Google sponsored the pilot and contracted for defined environmental-attribute time windows; cash consideration, operator earnings and take-or-pay were undisclosed.",
        next_trigger="Obtain executed anonymized pilot contract, EnergyTag/registry independent attestation, retired certificate MWh, actual payment and adopter beyond Google.",
        evidence=[
            "esVolta original official September17 pilot result press release: verify 2026-09-17 Anole 240MW/480MWh and Burksol 100MW/200MWh installed capacity plus reported 9.2GWh charge/discharge window volume during a 3-month pilot.",
            "Quintrace original September17 partner pilot press release: verify signed Google certificate contract status, timestamp/loss tracking methodology and reported pilot window volume 9.2GWh distinct from net clean credited MWh.",
            "LevelTen registry retirement report or Google executed attribute contract: verify actual paid certificate quantity, financial settlement date and duplicate-claim controls.",
        ],
        confirm=[
            "Google signed hourly storage environmental-attribute contract and metered 9.2GWh activity confirmed by independent registry would strengthen ESS carbon-accounting revenue outlook; rejected credits would weaken it.",
            "Quintrace independently retired hourly certificate MWh net of battery losses and actual payment evidence would strengthen recurring storage revenue outlook; nonpayment would weaken it.",
            "GHG Protocol or SBTi eventual finalized storage-hourly accounting rule and corporate adoption counts would strengthen standardized demand outlook; rejected methodology would weaken it.",
        ],
        cat="ESS", sub_cat="GRANULAR_CERT_STORAGE_FIELD_PILOT",
    ),
    "OFGEM": dict(
        case_id="UK_OFGEM_CMP470_OTCF_MINDED_TO_CONSULT_20260917",
        rows=[122,138], representative=122, date="2026-09-17",
        owner="Great Britain Office of Gas and Electricity Markets (Ofgem)",
        owner_urls=[
            "https://www.ofgem.gov.uk/consultation/connection-and-use-system-code-cusc-cmp470-introducing-oversubscribed-technologies-commitment-fee-otcf",
            "https://www.ofgem.gov.uk/press-release/ofgem-moves-free-grid-capacity-tackling-excess-battery-projects",
        ],
        title="영국 Ofgem, ESS 접속대기열 CMP470 보증금 도입안 협의 — 결정 대기",
        region="UK", geographic_scope="Great Britain electricity transmission connection queue",
        summary="Ofgem이 9월17일 CMP470 초과접속기술 Commitment Fee 협의 시작. 초기 £3,000/MW에서 최대 £25,000/MW 제안, BESS 운영·대기열 합산 약 90GW 대비 2035년 필요 전망 29GW. 10월2일 종료 뒤 현재 'Closed (awaiting decision)'이며 어떤 수수료도 이 자료만으로 시행된 것은 아님.",
        prior_state="CMP470 industry modification proposed March2026 and queued BESS oversubscription was recognized; no final Ofgem approval of OTCF had occurred by September17.",
        new_fact="Ofgem published a formal minded-to-approve CMP470 consultation September17, presenting indicative £3,000-£25,000 per MW commitment security tied to technology oversubscription and seeking comments until October2.",
        increment="The official regulator moved CMP470 from industry proposal to explicit minded-to public consultation with quantified potential BESS capital/security exposure; final code adoption still pending.",
        must_not="Do not claim £3,000/MW or £25,000/MW fee is already levied, approved, collected, universally applies, or that 90GW are all queued/unbuilt. Around 90GW includes about 83GW shortlisted and 7GW already operational; 29GW is a 2035 need projection.",
        event_units=["CMP470_OF_GEM_MINDED_TO_APPROVE_CONSULTATION","DRAFT_BESS_SECURITY_3000_TO_25000_GBP_PER_MW","FINAL_CUSC_RULE_AND_NESO_ACTIVATION_PENDING"],
        score=[16,19,0,5,7,3,2,2], anchors=["policy_regulatory_anchor"],
        classification_lenses=["policy_regulatory_anchor","AI/data-centre power/ESS"],
        route="structural_non_execution_route", policy_stage=1,
        legal_stage="stage_1_roadmap_consultation_or_draft_standard",
        law_type="CUSC CMP470 proposed Oversubscribed Technologies Commitment Fee code modification, Ofgem minded-to consultation; not an adopted final CUSC rule",
        procedure="Ofgem formal consultation opened 2026-09-17, closed 2026-10-02, website still Closed (awaiting decision) on November1; final decision pending.",
        mandatory="No operative mandatory fee date; draft £3,000/MW lower and £25,000/MW upper security contingent on approval and oversubscription triggers.",
        implementation="If finalized, NESO would monitor technology oversubscription and administer new/modified securities; original proposal begins when oversubscription >50% of target and stops when <25%.",
        funding="Proposed developer-held financial commitments / cash collateral / letters of credit, not government budget or realized fee payments.",
        affected=["Great Britain BESS grid connection applicants","NESO connection queue","network consumers and developers' securities"],
        system_denominator="Ofgem 83GW BESS prioritized in queue + 7GW operational ≈90GW combined; national projected need 29GW by 2035; proposed securities £3,000-£25,000/MW if finally implemented.",
        next_trigger="Check Ofgem final CMP470 decision, definitive code text, fee bands and triggering dates; verify NESO security requests and any grid-queue attrition only after operation.",
        related_full=[],related_reason="No same dated CMP470 minded-to consultation in locked Full1676; earlier general GB grid-connection reforms are separate programme context.",
        staged_questions=["Confirm final Ofgem consultation status not implementation.","Read final CMP470 and WACMs for co-location exemptions and trigger levels.","Count real BESS projects affected only after NESO actual security notices."],
        evidence=[
            "Ofgem official original CMP470 consultation document and attached minded-to PDF dated2026-09-17: verify policy consultation status Closed awaiting decision after formal close date 2026-10-02.",
            "Ofgem official original September17 press release document: verify proposed financial security price from £3,000 per MW to £25,000 per MW and BESS capacity 83GW queued plus 7GW operating against 29GW 2035 forecast.",
            "Ofgem eventual final CMP470 approval decision and NESO official CUSC implementation notice: verify operative effective date, trigger thresholds and actual commitment security per MW.",
        ],
        confirm=[
            "Ofgem final CMP470 decision adopting proposed £3,000-£25,000/MW developer security would strengthen GB BESS queue-discipline outlook; rejection would weaken the expected policy transmission outlook.",
            "NESO actual CMP470 activation date and per-MW collateral required for projects above 50-percent oversubscription threshold would strengthen the capital-cost outlook; exemptions would narrow that outlook.",
            "NESO monthly BESS queue capacity count declining from 83GW shortlisted after CMP470 activation would strengthen GB grid connection reform outlook; unchanged 83GW would weaken that outlook.",
        ],
        cat="Policy",sub_cat="UK_BESS_GRID_CONNECT_QUEUE_CONSULT",
    ),
    "CANADA": dict(
        case_id="CA_CITT_CHINA_PV_DUTY_ORDER_RESCINDED_20260917",
        rows=[173],representative=173,date="2026-09-17",
        owner="Canadian International Trade Tribunal (CITT) and Canada Border Services Agency (CBSA)",
        owner_urls=[
            "https://www.canada.ca/en/international-trade-tribunal/news/2026/09/tribunal-terminates-expiry-reviewphotovoltaic-modules-and-laminates-from-china.html",
            "https://www.cbsa-asfc.gc.ca/sima-lmsi/er-rre/sml2026/sml2026-xo-eng.html",
        ],
        title="캐나다 CITT, 중국산 태양광 모듈·라미네이트 무역구제 명령 취소",
        region="CA", geographic_scope="Canada customs importation of certain Chinese-origin/export photovoltaic modules and laminates",
        summary="캐나다 CITT가 9월17일 중국산 특정 태양광 모듈·라미네이트 대상 2021년 명령을 취소. CBSA는 해당 제품의 반덤핑·상계관세 신규 통관 부과를 중단하고, 적격 2026년3월25일 이후 통관분은 자동환급 예정. 배터리셀·ESS 완제품 관세 철회가 아님.",
        prior_state="CITT March2021 solar-modules order in force; CBSA July2026 made separate determination that dumping/subsidization would likely continue, but final CITT order disposition followed later.",
        new_fact="CITT September17 terminated solar-modules expiry review and formally rescinded March2021 order, resulting in CBSA non-collection for covered new released goods and eligible refunds from March25 2026 under CBSA notice.",
        increment="A final tribunal order changes actual solar-component customs liability and import economics, a direct clean-energy supply-chain access event; indirect solar-plus-storage integration must not be represented as an ESS battery tariff change.",
        must_not="Do not extend this PV-specific rescission to lithium battery cells, inverters or complete ESS; do not claim all Canadian import tariffs disappeared, pre-March25 releases qualify for refunds or retroactive repayment was already fully disbursed.",
        event_units=["SEPT17_FINAL_CITT_RESCISSION_OF_PV_ORDER","CBSA_NO_NEW_PV_AD_CVD_LIABILITY","ELIGIBLE_PV_RELEASES_SINCE_MARCH25_REFUND_RULE"],
        score=[17,20,0,7,10,4,3,2],anchors=["policy_regulatory_anchor"],
        classification_lenses=["policy_regulatory_anchor","PV/storage adjacent supply chain"],
        route="structural_non_execution_route",policy_stage=5,
        legal_stage="stage_3_enacted_law_final_rule_or_adopted_standard",
        law_type="CITT formal Special Import Measures Act Section 76.03 order rescission, PV modules and laminates from China; CBSA enforcement/eligible refund notice",
        procedure="CITT September17 final rescission; CBSA September17 notice stops duties on new covered releases and provides automatic eligible refunds to March25 2026 onward goods.",
        mandatory="2026-09-17 final order and duty cessation; CBSA eligible-refund release-date floor 2026-03-25, not retroactive to earlier goods.",
        implementation="CBSA import release classification and automatic refund of eligible duties; product definitions/exclusions under SIMA SML measures, with earlier released goods still subject to past assessment.",
        funding="Customs duty non-collection and potential automatic refund to covered Canadian importers; no quantified fiscal total or battery incentive.",
        affected=["Canadian importers of defined Chinese photovoltaic modules and laminates","Canadian PV sourcing and downstream solar-plus-storage developers indirectly","CBSA customs duties for specified PV goods"],
        system_denominator="Defined Chinese PV modules and laminates only; eligible releases on or after 2026-03-25; no MW/market share or duty repayment total established.",
        next_trigger="Read CITT original Sept17 order, CBSA SIMA SML definitive tariff classification and importer refund implementation; measure actual affected PV volume and separate any ESS battery import policies.",
        related_full=[],related_reason="No same final CITT September17 Chinese photovoltaic anti-dumping/countervailing order rescission in locked Full1676.",
        staged_questions=["Check exact covered PV product definitions and exclusions, not battery cells.","Confirm eligible March25 2026 release floor and actual CBSA refund credits.","Estimate any solar-storage cost pass-through only from importer/project evidence."],
        evidence=[
            "Canadian International Trade Tribunal original 2026-09-17 expiry-review rescission decision: verify photovoltaic modules and laminates from China, 2021 order, and precise effective rescission date.",
            "Canada Border Services Agency official 2026-09-17 SML expiry-of-order notice: verify PV duty cessation effective date and automatic refund eligibility status for covered releases since March25 2026.",
            "CBSA customs refund remittance report or importer filings: verify actual returned duties, commodity scope and payment date independent of announced refund rule.",
        ],
        confirm=[
            "CBSA finalized 2026 Chinese photovoltaic duty price at zero would strengthen Canada PV cost outlook; higher duties would weaken outlook.",
            "CBSA actual 2026 PV duty refund volume in CAD would strengthen importer outlook; no refunds would weaken outlook.",
            "Canadian hybrid solar-BESS project signed module procurement cost reductions linked to the PV duty change would strengthen downstream hybrid economics outlook; unchanged battery tariffs mean no direct ESS cell benefit.",
        ],
        cat="Policy",sub_cat="CANADA_PV_TRADE_RESCISSION",
    ),
    "HIRASOL": dict(
        case_id="JP_HIRASOL_IZUMIZAKI_NEGAPOSI_MARKET_PREQUAL_20260916",
        rows=[79],representative=79,date="2026-09-16",
        owner="Hirasol Energy (ヒラソル・エナジー)",
        owner_urls=["https://prtimes.jp/main/html/rd/p/000000027.000085634.html"],
        title="Hirasol Izumizaki ESS, 네가포지 조정력 입찰 3,800kW 사전심사 통과",
        region="JP",geographic_scope="Izumizaki Village, Fukushima, Tohoku area, Japan",
        summary="Hirasol 9월16일 기업 원발표: 7월21일 계통연계된 정격 1,900kW Izumizaki ESS가 네가포지 충·방전 복합 운용 사전심사 통과. 4개 조정력 상품 및 복합응찰 가능 입찰상한 3,800kW 승인. 정격 설비증설·실제 입찰량·낙찰·현금수익 아님.",
        prior_state="Izumizaki battery already physically connected July21 with rated output 1,900kW; prequalification for combined negative/positive balancing market was not previously established.",
        new_fact="September16 operator disclosure reports acceptance of actual balancing-market prequalification for 3,800kW bid upper bound across four overlapping products at a single already operating 1,900kW BESS.",
        increment="An existing ESS obtains new market bid eligibility via J-EMS control and negative/positive balancing, a real monetization-access milestone independent of physical capacity or new construction.",
        must_not="3,800kW is a maximum approved adjustable bidding capability, not doubled battery nameplate 1,900kW, guaranteed continuous offered MW, four additive product volumes, actual contracted award, market earnings, or new September COD.",
        event_units=["EXISTING_1900KW_ESS_MARKET_PREQUALIFICATION_PASS","FOUR_OVERLAPPING_BALANCING_PRODUCTS_3800KW_COMBINED_BID_CAP"],
        score=[16,18,5,7,3,3,2,1],anchors=["execution_event_anchor"],
        classification_lenses=["AI/data-centre power/ESS","Japan grid ancillary-services monetization"],
        route="execution_anchor_route",execution_type="verified_bess_balancing_market_bid_eligibility",
        tech_stage="qualification",technology_level="independent_test_or_customer_qualification",
        tech_gap="No independent TSO prequalification record, winning bids, continuous 3.8MW physical export validation or net balancing revenue reported.",
        system_denominator="One previously connected 1,900kW nameplate BESS; 3,800kW market bid-ceiling via net charging reduction + discharge, four product categories overlap and are not additive.",
        affected=["Hirasol Izumizaki 1.9MW BESS","Japanese balancing market registration","J-EMS aggregator dispatch eligibility"],
        procedure="9월16일 기업원발표는 시장 사전심사 결과, 7월21일 계통연계가 물리적 연결 사건으로 선행; 실제 시장입찰/낙찰은 후속.",
        implementation="Hirasol J-EMS cloud and edge control allows charge interruption plus discharge bids for four distinct but overlapping balancing-market product types.",
        funding="No verified incremental revenue, settlement, capex increase or awarded market contract value at the prequalification stage.",
        next_trigger="Verify Tohoku grid operator/OCCCTO formal prequalification entry, first actual bids/awards and revenue settlement by time block.",
        evidence=[
            "Hirasol Energy original 2026-09-16 company press release document: verify Izumizaki battery July21 grid connection date and 1,900kW physical capacity versus 3,800kW market prequalification bid capacity.",
            "Japanese OCCTO or grid operator official prequalification registration notice: verify approval status for four overlapping product classes and nonadditive 3,800kW capacity ceiling for Izumizaki ESS.",
            "Japanese balancing market official auction and settlement reports: verify actual Izumizaki awarded kW volume per period and realized cash revenue distinct from approval eligibility.",
        ],
        confirm=[
            "OCCTO official accepted Izumizaki 3,800kW balancing bid ceiling for four overlapping products would strengthen existing-ESS flexibility utilization outlook; lower approved limits would weaken it.",
            "Hirasol actual awarded ancillary-service kW and paid settlement under J-EMS would strengthen Japanese ESS monetization outlook; zero awards would weaken the conversion outlook.",
            "Other Japanese BESS operators verified negative-positive prequalification approvals with measured kW volumes would strengthen scalability outlook; isolated one-site outcomes would limit it.",
        ],
        cat="ESS",sub_cat="JAPAN_BALANCING_MARKET_PREQUALIFICATION",
    ),
}

WATCH_CASES = {
    "FLOW": dict(case_id="AU_FLOW_POWER_BENNETTS_STAGE2_PROPOSAL_20260918",rows=[120],date="2026-09-18",
        owner_urls=["https://flowpower.com.au/flow-power-celebrates-bennetts-creek-battery-construction-milestone/",
                    "https://flowpower.com.au/flow-power-reaches-financial-close-on-bennetts-creek-battery-energy-storage-system/",
                    "https://flowpower.com.au/bennetts-creek-battery-roadworks/",
                    "https://flowpower.com.au/bennetts-creek-battery/"],
        status="FORMAL_WATCH_SPLIT_OLD_CONSTRUCTION_V_NEW_PRE_PERMIT_PROPOSAL",
        why="September14 was a ceremony at an already-started 100MW/223MWh construction site (Flow Power May14 already said work commenced; Dec2025 financial close); Sept18 also announced up-to-300MW/1.2GWh Stage2 only at preliminary environmental/planning phase. Live company project page currently says 100MW/233MWh versus dated Sept18 223MWh: unresolved owner version difference.",
        future="Stage2 development approval application filed/approved, new financial close or signed EPC, Stage1 final authoritative engineering MWh, actual 2028 COD."),
    "LG": dict(case_id="KR_LG_AI_DATACENTER_TURBO_CHILLER_LAUNCH_20260920",rows=[176,177,178,179],date="2026-09-20",
        owner_urls=["https://www.lge.co.kr/story/newsroom/236187"],
        status="FORMAL_WATCH_ADJACENT_PRODUCT_SAME_LAUNCH_FOUR_MEDIA_OBSERVATIONS",
        why="LG stated the turbo chiller was released on September20; owner newsroom posted September21. Four original media articles describe one AI-data-centre cooling appliance release, not ESS procurement. Manufacturer's conditional around-30% annual chiller electricity saving compares water versus refrigerant free cooling; no independently measured site PUE, battery dispatch, sales booking or new datacentre BESS.",
        future="Independent operating annual cooling kWh validation and signed data-centre deployments materially linking battery or grid demand."),
    "TOPCON": dict(case_id="CN_OPIS_TOPCON_PV_CELL_PRICE_WEEKLY_20260915",rows=[172],date="2026-09-15",
        owner_urls=["https://pv-magazine-usa.com/2026/09/18/china-topcon-solar-cell-prices-fall-for-third-week-as-export-buying-fades-and-wafer-costs-ease/"],
        status="FORMAL_WATCH_SOLAR_CELL_PRICE_SNAPSHOT_NOT_BATTERY_CELL",
        why="PV magazine reports OPIS September15 solar TOPCon photovoltaic cell price M10 FOB $0.0469/W and 210R $0.0458/W. This is a time-specific proprietary PV price assessment, not a lithium-ion ESS battery-cell USD/Wh benchmark, independently verified shipment price or new corporate economic act.",
        future="Official OPIS comparable period-by-period methodology and demonstrated separate ESS/PV hybrid procurement price pass-through."),
}


def strict_case(old:dict, template:dict, e:dict, observations:list[dict]) -> dict:
    e={
        "legal_stage":None,"policy_stage":None,
        "law_type":"Not a new legal policy instrument", "mandatory":"No legal application date",
        "related_full":[],
        "related_reason":"No exact same dated economic act represented in locked Full1676.",
        "staged_questions":[
            "Confirm dated original first-party event versus earlier Full1676 and source observations.",
            "Separate physical execution, market access, proposal and later realization stages.",
            "Confirm issuer claims independently during Stage B evidence collection.",
        ],
        **e,
    }
    if e["route"] == "execution_anchor_route":
        s=execution_strict(old,template,e,observations)
    else:
        s=build_strict(old,template,e,observations)
        s.update({
            "assessment_profile":"regulator_consultation_only" if e["policy_stage"]==1 else "final_pv_customs_rescission",
            "region":e["region"],"geographic_scope":e["geographic_scope"],
            "affected_entities":e["affected"],"affected_products_or_activities":e["affected"],
            "legal_policy_transmission_chain":[e["new_fact"],e["must_not"]],
            "extraterritorial_effect":"GB grid connection conditions only" if e["region"]=="UK" else "Chinese-origin/export PV goods imported to Canada; battery imports not covered",
            "source_priority_notes":e["must_not"],"technology_validation_gap":"No technology performance claim adjudicated by this policy act.",
            "evidence_needed_for_stage_b":e["evidence"],"next_confirmation_points":e["confirm"],
            "cat":e["cat"],"sub_cat":e["sub_cat"],
            "assessment_method":"PROMPT_0_1P_V4_20260829 original regulator/CBSA check and Full1676 identity",
            "review_pool_subtype":None,
            "staleness_decision":"fresh_event",
            "staleness":{"event_date":e["date"],"publication_date":e["date"],"staleness_gap_days":0,
                         "staleness_suspected":False,"fresh_followup":False,"staleness_override":False,"decision":"fresh_event"},
            "baseline_follow_up_relation":"new_unrelated","follow_up_relation":"new_unrelated",
            "publication_date":e["date"],"adoption_date":None if e["policy_stage"]==1 else e["date"],
            "legal_policy_stage":e["legal_stage"],"policy_stage":e["policy_stage"],
            "policy_stage_provisional":False,
            "structural_non_execution_reason":"Official regulator consultation is a time-bounded draft decision, not a fee in force." if e["policy_stage"]==1 else "Final tribunal PV customs order is material without battery asset construction.",
            "why_execution_event_not_required":"Independent legal process and potential BESS developer cost exposure; enforceability remains pending." if e["policy_stage"]==1 else "A final PV-specific trade remedy cessation materially changes import access without requiring a physical battery asset milestone.",
            "structural_value_override_applied":True,
            "structural_value_override_reason":e["increment"]+" "+e["must_not"],
            "execution_anchor_type":"","execution_anchor_strength":"",
            "execution_credibility_gate":{"status":"PASS","reason":e["new_fact"],"anchor_type":"policy_regulatory_anchor","anchor_strength":"strong" if e["policy_stage"]==5 else "moderate","stage_precision_note":e["must_not"]},
            "source_diversity_path":{
                "status":"viable","candidate_owner_available":True,"independent_owner_availability":"unknown",
                "same_owner_syndication_not_independent":True,"source_audit_approval":False,
                "stage_b_question":e["next_trigger"],
            },
        })
    s.update({
        "formal_0_1P_remaining_cases_20261101":{
            "case_id":e["case_id"],"source_ids":[x["story_id"] for x in observations],
            "event_units":e["event_units"],"owner_urls":e["owner_urls"],
            "stage_b_evidence_required":True,"not_a_published_article":True,
        },
        "original_source_identity_preserved":{"source_id":old["story_id"],"source_row_index":old["source_row_index"],
                                              "headline_raw":old["headline_raw"],"primary_url":old["primary_url"]},
        "formal_0_1P_batch_promoted_20261101":{
            "case_id":e["case_id"],"date":e["date"],"source_id":old["story_id"],
            "source_count":len(observations),"source_ids":[x["story_id"] for x in observations],
            "evidence_urls":e["owner_urls"],"separate_economic_units":e["event_units"],
            "not_stage_b_fact_safe":True,
        },
    })
    if e["region"]=="UK":
        s["decision_value_classification"]="standard_monitoring"
        s["exemptions_and_thresholds"]=["Proposal: fee begins above 50% oversubscription, stops below 25%; alternative code mods and co-location exceptions remain undecided."]
        s["procedural_status"]="Closed (awaiting decision) on 2026-11-01; consultation closed 2026-10-02, no final modification approval."
        s["adoption_date"]="NOT_ADOPTED — Ofgem CMP470 decision pending after 2026-10-02 consultation close"
        s["mandatory_application_date"]="NOT_APPLICABLE — no mandatory OTCF until final CMP470 code approval and activation"
        s["effective_date"]="NOT_EFFECTIVE — 2026-11-01 status Closed (awaiting decision)"
    if e["region"]=="CA":
        s["transition_and_grandfathering"]=["Goods released before 2026-03-25 are not eligible for the order-rescission refund; earlier assessments continue."]
        s["mandatory_application_date"]="2026-09-17 (order rescission and cessation for covered new releases)"
        s["effective_date"]="2026-09-17; CBSA refund release eligibility starts 2026-03-25"
    if e["region"]=="US":
        s["assessment_profile"]="actual_storage_field_demonstration_not_standard_adoption"
        s["publication_date"]="2026-09-17"
    if e["region"]=="JP":
        s["assessment_profile"]="actual_balancing_market_prequalification_not_earnings"
        s["publication_date"]="2026-09-16"
    assert s["stage_b_authorized"] is False and s["canonical_card_write_allowed"] is False
    return s


def formal_watch(old:dict,e:dict,obs:list[dict],rep_sid:str)->dict:
    row=copy.deepcopy(old)
    sid=old["story_id"]
    row.update({
        "stage_a_pool":"watchlist_context_pool","ledger_decision":"watchlist_context_pool",
        "editorial_bucket":"watchlist_context_pool","assessment_status":"FORMAL_0_1P_WATCH_CONTEXT_NO_CARD",
        "assessment_method":"PROMPT_0_1P_V4_20260829 owner-first event identity/stage check",
        "review_pool_partition":"watchlist_context_pool","review_pool_subtype":"general_candidate",
        "review_pool_resolution_status":"reviewed_watch_context","final_review_pool_disposition":"watchlist_only_after_review",
        "promotion_reassessment_status":"FORMAL_WATCH_NO_CARD",
        "needs_review":False,"review_reason":e["why"],"why_context_only":e["why"],
        "future_trigger_to_reopen":e["future"],"recommended_monitoring_action":e["future"],
        "reason_not_new_card":e["why"],"why_not_strict_passed_spec":e["why"],
        "final_reason":e["why"],"economic_event_cluster_id":e["case_id"],
        "event_representative_source_id":rep_sid,
        "same_event_source_cluster":[{"source_id":r["story_id"],"url":r["primary_url"],"preserved":True} for r in obs],
        "prior_state":"Original dated owner history and Full1676 checked; no independent strict event with verified executed impact established.",
        "new_verified_fact":"0.1P owner bounded check: "+e["why"],
        "changed_judgment":"Formal watch context, not a new card or Stage B accepted evidence.",
        "incremental_information":e["why"],"remaining_uncertainty":e["future"],
        "source_priority_notes":e["why"],"source_metadata_only":True,
        "independent_cardability_gate":{"status":"FAIL","reason":e["why"],"full_schema_viability":"FAIL",
                                        "distinct_event_or_stage_progression":False,"duplicate_or_reinforcement_note":e["why"]},
        "canonical_card_write_allowed":False,"accepted_facts_approved":False,"stage_b_authorized":False,
        "formal_0_1P_watch_context_20261101":{
            "case_id":e["case_id"],"original_row":old["source_row_index"],
            "original_source_id":sid,"original_url":old["primary_url"],
            "owner_urls":e["owner_urls"],"event_date":e["date"],
            "source_observations_in_group":len(obs),"watch_reason":e["why"],"future_trigger":e["future"],
            "no_new_card":True,"stage_b_evidence_authorized":False,
        },
    })
    if sid!=rep_sid:
        row["same_event_source_observation_role"]="duplicate_media_observation_of_watch_only_economic_act"
        row["baseline_match"]=rep_sid
        row["baseline_relation"]="same_event_watch_context_observation"
    return row


def main():
    p=argparse.ArgumentParser()
    for k in ("base","full","output","receipt"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    assert sha256(a.base)==BASE_SHA
    d,full=read(a.base),read(a.full)
    assert len(full["cards"])==1676 and len(d["decision_ledger"])==1330
    assert len(d["strict_passed_spec"])==14 and len(d["candidate_review_pool"])==598
    assert len(d["watchlist_context_pool"])==655 and len(d["review_pool_resolution_ledger"])==1286
    assert len(d["promotion_reassessment_ledger"])==86
    old_by_index={r["source_row_index"]:r for pool in (
        "candidate_review_pool","watchlist_context_pool") for r in d[pool]}
    expected={19,123,468,122,138,173,79,120,176,177,178,179,172}
    assert set(old_by_index).issuperset(expected) and 8 in old_by_index
    assert {idx for e in [*CASES.values(),*WATCH_CASES.values()] for idx in e["rows"]}==expected
    assert 79 in {r["source_row_index"] for r in d["watchlist_context_pool"]}
    for phrase in ("Quintrace","CMP470","Bennetts Creek","泉崎", "CITT"):
        assert not any(phrase.casefold() in str(c.get("title","")).casefold() for c in full["cards"]),phrase
    template=d["strict_passed_spec"][-1]
    ledger={r["story_id"]:r for r in d["decision_ledger"]}
    reviews={r["story_id"]:r for r in d["review_pool_resolution_ledger"]}
    strict_ids,support_ids,watch_ids=set(),set(),set()
    new_watch_rows=[]
    decisions=[]
    for e in CASES.values():
        obs=[old_by_index[i] for i in e["rows"]]
        rep=old_by_index[e["representative"]]
        sid=rep["story_id"]
        s=strict_case(rep,template,e,obs)
        d["strict_passed_spec"].append(s)
        ledger[sid].update(copy.deepcopy(s))
        strict_ids.add(sid)
        decisions.append({"row":rep["source_row_index"],"source_id":sid,"case_id":e["case_id"],
            "result":"FORMAL_STRICT_SELECTOR_ONLY_NOT_STAGE_B","original_headline":rep["headline_raw"],
            "original_url":rep["primary_url"],"owner_urls":e["owner_urls"],"score":sum(e["score"]),
            "event_units":e["event_units"],"must_not_claim":e["must_not"]})
        d["promotion_reassessment_ledger"].append({
            "candidate_id":sid,"economic_event_cluster_id":e["case_id"],
            "before_pool":rep["stage_a_pool"],"after_pool":"strict_passed_spec",
            "promotion_reassessment_status":"PROMOTED_VALIDATED_STRICT",
            "resolved":e["new_fact"],"remaining":e["must_not"],
            "source_candidates":e["owner_urls"],"source_observation_preserved":True})
        for r in obs:
            if r["story_id"]==sid:
                continue
            su=support_row(r,e,sid)
            su["execution_credibility_gate"]["anchor_type"]=(
                "policy_regulatory_anchor" if e["route"]=="structural_non_execution_route" else "execution_event_anchor")
            su["formal_0_1P_support_only_20261101"]["representative_source_id"]=sid
            su["formal_0_1P_support_only_20261101"]["support_role"]="one_economic_event_multiple_independent_source_ids"
            d["reject_or_support_only_pool"].append(su)
            ledger[r["story_id"]].update(copy.deepcopy(su))
            rev=reviews[r["story_id"]]
            rev.update({"original_review_pool_partition":"reject_or_support_only_pool",
                "current_disposition":"reject_or_support_only_pool","disposition_basis":su["final_reason"],
                "carry_forward_policy":"support_source_only",
                "next_action_condition":"Future separate economic stage only; retain URL for corroboration.",
                "final_review_pool_disposition":"support_source_only_after_review",
                "reviewed_by_stage_or_pass":"PROMPT_0_1P_V4_20260829 owner-first formal Nov1 2026",
                "review_artifact_id":"STAGE_A_CHECKPOINT_16_FORMAL_20261101"})
            d["promotion_reassessment_ledger"].append({
                "candidate_id":r["story_id"],"economic_event_cluster_id":e["case_id"],
                "before_pool":r["stage_a_pool"],"after_pool":"reject_or_support_only_pool",
                "promotion_reassessment_status":"FORMAL_SAME_EVENT_SUPPORT_ONLY",
                "resolved":su["final_reason"],"remaining":e["must_not"],
                "source_candidates":e["owner_urls"],"source_observation_preserved":True})
            support_ids.add(r["story_id"])
            decisions.append({"row":r["source_row_index"],"source_id":r["story_id"],"case_id":e["case_id"],
                "result":"FORMAL_SUPPORT_SAME_EVENT_NO_EXTRA_CARD","representative_source_id":sid,
                "original_headline":r["headline_raw"],"original_url":r["primary_url"],"owner_urls":e["owner_urls"]})
    for e in WATCH_CASES.values():
        obs=[old_by_index[i] for i in e["rows"]]
        sid=obs[0]["story_id"]
        for r in obs:
            w=formal_watch(r,e,obs,sid)
            new_watch_rows.append(w)
            ledger[r["story_id"]].update(copy.deepcopy(w))
            rev=reviews[r["story_id"]]
            rev.update({"original_review_pool_partition":"watchlist_context_pool",
                "current_disposition":"watchlist_context_pool","disposition_basis":e["why"],
                "carry_forward_policy":"carry_forward_to_watchlist",
                "next_action_condition":e["future"],
                "final_review_pool_disposition":"watchlist_only_after_review",
                "reviewed_by_stage_or_pass":"PROMPT_0_1P_V4_20260829 owner-first formal Nov1 2026",
                "review_artifact_id":"STAGE_A_CHECKPOINT_16_FORMAL_20261101"})
            d["promotion_reassessment_ledger"].append({
                "candidate_id":r["story_id"],"economic_event_cluster_id":e["case_id"],
                "before_pool":r["stage_a_pool"],"after_pool":"watchlist_context_pool",
                "promotion_reassessment_status":e["status"],"resolved":e["why"],
                "remaining":e["future"],"source_candidates":e["owner_urls"],
                "source_observation_preserved":True})
            watch_ids.add(r["story_id"])
            decisions.append({"row":r["source_row_index"],"source_id":r["story_id"],
                "case_id":e["case_id"],"result":"FORMAL_WATCH_CONTEXT_NO_NEW_CARD",
                "representative_source_id":sid,"original_headline":r["headline_raw"],
                "original_url":r["primary_url"],"owner_urls":e["owner_urls"],
                "reason":e["why"],"future_trigger":e["future"]})
    completed=strict_ids|support_ids|watch_ids
    assert len(strict_ids)==4 and len(support_ids)==3 and len(watch_ids)==6 and len(completed)==13
    d["candidate_review_pool"]=[r for r in d["candidate_review_pool"] if r["story_id"] not in completed]
    d["watchlist_context_pool"]=[r for r in d["watchlist_context_pool"] if r["story_id"] not in completed]+new_watch_rows
    d["review_pool_resolution_ledger"]=[r for r in d["review_pool_resolution_ledger"] if r["story_id"] not in strict_ids]
    assert len(d["strict_passed_spec"])==18
    assert len(d["candidate_review_pool"])==586
    assert len(d["watchlist_context_pool"])==660
    assert len(d["reject_or_support_only_pool"])==36
    assert len(d["existing_reinforcement"])==30
    assert len(d["review_pool_resolution_ledger"])==1282
    assert len(d["promotion_reassessment_ledger"])==99
    assert sum(len(d[k]) for k in ("strict_passed_spec","candidate_review_pool","watchlist_context_pool",
                                   "reject_or_support_only_pool","existing_reinforcement"))==1330
    summ=d["summary"]
    summ["strict_passed_spec_count"]=18
    summ["existing_reinforcement_count"]=30
    summ["duplicate_or_reinforcement_count"]=30
    summ["needs_review_count"]=1282
    summ["processed_priority_source_observations"]=99
    summ["processed_priority_economic_clusters"]+=4
    summ["unprocessed_editorial_observations"]=1231
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
        if k in summ:summ[k]=v
    att=d["pre_native_0_1P_attachment_manifest_20261101"]
    reviewed=att["formal_review_completed_source_ids"]+[x["source_id"] for x in sorted(decisions,key=lambda r:r["row"])]
    assert len(reviewed)==len(set(reviewed))==54
    att.update({"new_formal_decisions":54,"new_strict_promotions":10,
        "formal_review_completed_after_attachment_count":54,
        "formal_review_completed_source_ids":reviewed,
        "remaining_formal_source_count":1231,
        "native_validator_scope_warning":"Native contracts cover eighteen strict specs but do not certify Stage B evidence or authorize global release; 1,231 formal Source IDs pending."})
    pre_native_54=read(Path(__file__).with_name("PRE_NATIVE_54_20261031.json"))
    remaining54=[r for e in pre_native_54["case_definitions"] for r in e["source_row_indices"]
                 if r not in {x["source_row_index"] for x in d["decision_ledger"] if x["story_id"] in reviewed}]
    assert set(remaining54)=={8,48,244,614,916},(remaining54,len(reviewed))
    d["formal_0_1P_remaining_pre_native_cases_20261101"]={
        "authority":"PROMPT_0_1P_V4_20260829","previous_checkpoint_id":15,
        "source_ids_formalized_this_batch":13,"formal_individual_completed_total":99,
        "formal_individual_pending":1231,"source_ids_formalized_cumulative_since_45":54,
        "source_ids_from_original54_formally_decided":49,
        "source_rows_original54_remaining_unresolved":[8,48,244,614,916],
        "related_outside54_mixed_or_procedural_source_row228_pending":True,
        "source_row8_mixed_Factorial_interview_preserved_unchanged":True,
        "case_groups_this_batch":7,
        "strict_case_groups":4,"watch_case_groups":3,
        "source_disposition_counts":{"strict":4,"support_only":3,"watch_context":6},
        "source_decisions":sorted(decisions,key=lambda r:r["row"]),
        "owner_urls_by_case":{e["case_id"]:e["owner_urls"] for e in [*CASES.values(),*WATCH_CASES.values()]},
        "flow_power_announcement_vs_live_capacity_disagreement":{"dated_release_MWh":223,"live_site_MWh":233,
            "resolution":"HOLD_MWH_ENGINEERING_SPEC_CHECK","no_new_September_construction":True},
        "ofgem_final_status":"CONSULTATION_CLOSED_AWAITING_DECISION_NO_APPROVED_FEE",
        "canada_product_scope":"PV_MODULES_AND_LAMINATES_ONLY_NOT_BATTERY_ESS",
        "hirasol_bidding_vs_nameplate":"3800KW_BID_ELIGIBILITY_NOT_1900KW_PHYSICAL_UPGRADE",
        "esvolta_energy_accounting":"9_2GWH_CHARGE_DISCHARGE_WINDOW_ACTIVITY_NOT_NET_CERTIFIED_CREDIT_VOLUME_OR_REVENUE",
        "new_cards_created":0,"stage_b_executed":False,
        "global_editorial_stage_a_status":"HOLD_OPEN_1231_UNADJUDICATED",
        "native_stage_b_recommendation_scope":"Strict-only technical next-call, not global editorial release or Stage B execution.",
        "canonical_main_full_related_mutations":0,
    }
    d["recommended_for"]=["Finish 1,231 remaining formal Source ID judgments including mixed row8; Stage A HOLD despite 18 individual strict specs passing schema."]
    d["next_call_recommendation"].update({
        "recommended_next_call":"Stage B r0","recommended_prompt_id":"Prompt 0.2",
        "recommended_input_universe":"Stage A strict_passed_spec[] only",
        "reason":"Native strict-only next-call eligibility is not permission to start Stage B: 1,231 source-level editorial judgments pending.",
        "blocked_items_summary":d["review_pool_partition_summary"],
        "pending_parallel_or_followup_call":"review_pool/treasure triage",
        "pending_prompt_id":"authorized review_pool/treasure promotion protocol, not Prompt 0.2",
        "pending_input_universe":"candidate_review_pool[] + eligible treasure/review-only universe",
        "pending_reason":"Stage B may process strict_passed_spec[] only; review_pool/treasure remains open and must not be treated as exhausted.",
    })
    write(a.output,d)
    receipt={
        "artifact_type":"STAGE_A_CHECKPOINT_16_REMAINING_PRENATIVE_CASES_FORMAL_0_1P_RECEIPT",
        "status":"PENDING_NATIVE_VALIDATION_AFTER_BUILD",
        "base_sha256":BASE_SHA,"output_sha256":sha256(a.output),
        "original_sources":1330,"new_formalized":13,"formalized_total":99,"formal_pending":1231,
        "strict_count":18,"new_strict_count":4,"new_support_only_count":3,
        "new_watch_context_count":6,"case_groups":7,
        "remaining_unadjudicated_source_rows_from_pre_native_54":[8,48,244,614,916],
        "event_records":d["formal_0_1P_remaining_pre_native_cases_20261101"],
        "stage_b_executed":False,"global_stage_a_status":"HOLD",
    }
    write(a.receipt,receipt)
    print(json.dumps({k:receipt[k] for k in (
        "output_sha256","new_formalized","formalized_total","formal_pending","new_strict_count",
        "new_support_only_count","new_watch_context_count")},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()

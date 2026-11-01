#!/usr/bin/env python3
"""Stage A CP19: owner-backed economic-event/lifecycle adjudication.

The 1,330 original Source IDs are immutable.  Repeated media references remain
separate observations; only documented economic acts are selected as new strict
events.  This does not authorize Stage B, canonical cards, or publications.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from build_stage_a_checkpoint_16_remaining_cases_20261101 import formal_watch, strict_case
from build_stage_a_formal_kr_two_events_20261101 import coverage_maps, read, sha256, support_row, write
from build_stage_a_formal_usjp_four_events_20261101 import execution_strict

BASE_SHA = "4b9039f9f045e92ae5485ddab4ab0ab40bb19da8fdf59bb02c6c0b5adba44b66"
FULL_SHA = "d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9"


def case(*, cid, rows, rep, date, title, owner, urls, region, stage, fact, guard,
         impact, score, evidence, confirm, actions, prior, denominator,
         affected, category, subtype, related=(), mechanism="", budget="",
         legal_stage=None, law_type=None, mandatory=None, tech_stage=None):
    policy = legal_stage is not None
    return {
        "case_id":cid,"rows":rows,"representative":rep,"date":date,"title":title,
        "owner":owner,"owner_urls":urls,"region":region,
        "geographic_scope":{"KR":"Republic of Korea","US":"United States","UK":"United Kingdom","EU":"European Union"}[region],
        "summary":fact+" "+guard,"prior_state":prior,"new_fact":fact,
        "increment":impact,"must_not":guard,"event_units":actions,"score":score,
        "anchors":["policy_regulatory_anchor"] if policy else ["execution_event_anchor"],
        "classification_lenses":["policy_regulatory_anchor","market_structure"] if policy else
             (["technology_transition_commercialization","systemic_scale"] if tech_stage else ["capital_allocation_cashflow","materials_midstream"]),
        "route":"structural_non_execution_route" if policy else "execution_anchor_route",
        "execution_type":stage if not policy else None,
        "tech_stage":tech_stage,"technology_level":"material_failure_evidence" if tech_stage else "not_applicable",
        "tech_gap":"Future root-cause, total affected product population and actual mitigation completion require separate original reports." if tech_stage else "Not a claim of validated cell chemistry performance or mass production.",
        "system_denominator":denominator,"affected":affected,
        "procedure":mechanism or fact,
        "implementation":mechanism or "Implementation beyond the announced date requires original owner follow-up.",
        "funding":budget or "No direct disbursement established by this announcement alone.",
        "next_trigger":"; ".join(confirm),
        "related_full":list(related),
        "related_reason":"Related historical facts and/or partners in locked Full are distinct economic acts, not the same newly dated legal stage or execution event.",
        "staged_questions":["Identify signed/approved original stage independently of article headline.",
                            "Check whether any future funding, plant operation or contract is an actual later action.",
                            "Cross-check same-event duplicates against Full 1676 and Stage A formal IDs."],
        "evidence":evidence,"confirm":confirm,"cat":category,"sub_cat":subtype,
        "legal_stage":legal_stage,
        "policy_stage":{ "stage_1_roadmap_consultation_or_draft_standard":1,
                         "stage_2_bill_or_proposed_rule":2,
                         "stage_4_implementation_budget_guidance_or_registry":4}.get(legal_stage),
        "law_type":law_type or "Original corporate/technical announcement; not a new binding legal instrument",
        "mandatory":mandatory or "No new mandatory legal application date established",
    }


EVENTS = [
    case(cid="KR_BATTERY_SODIUM_ASSB_TECHNOLOGY_ROADMAP_20260922",
         rows=[1277,226,302],rep=1277,date="2026-09-22",region="KR",
         owner="Korea Ministry of Trade, Industry and Resources (MOTIR)",
         urls=["https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/172230/view"],
         title="산업부, 나트륨·전고체 중심 배터리 산업기술 로드맵 확정·발표",
         stage="strategy_roadmap_adopted_not_disbursed",legal_stage="stage_1_roadmap_consultation_or_draft_standard",
         law_type="Nonbinding 2026 battery technology industrial R&D roadmap, not enacted tax-credit legislation",
         mandatory="No enforceable industry deadline; roadmap targets 2027-2031 require budget, standards and approvals",
         fact="MOTIR original September22 roadmap designates sodium-ion and all-solid-state as future technology priorities; proposes about KRW400bn new government R&D programs 2027-2031 and industry intent for KRW8tn R&D/facilities 2026-2030.",
         guard="2027-2031 R&D is a new-program proposal, not appropriated, awarded or disbursed cash. KRW8tn is private intent, not executed CAPEX. Sodium 160Wh/kg 2027 and 220Wh/kg 2030, and 400Wh/kg ASSB 2028 are technology targets, not independently achieved performance. Tax credit and common standards are future policy proposals, not effective rules.",
         impact="Official technology strategy change affects chemistry selection, upstream sodium hard-carbon materials and ASSB innovation; the future public/private commitments have not yet become cashflows.",
         score=[16,18,0,5,5,3,2,1],
         actions=["SEP22_ADOPTED_BATTERY_INDUSTRY_TECHNOLOGY_ROADMAP", "PLANNED_GOV_RND_KRW400BN_NOT_SPENT", "PLANNED_PRIVATE_KRW8TN_NOT_SPENT", "SODIUM_ASSB_TECH_TARGETS_NOT_REALIZED"],
         prior="Prior industry strategies emphasized high-nickel cells; separate September23 critical-mineral security four plans, and later signed SK On/L&F cathode contract are different acts.",
         denominator="Government planned approximately KRW400bn new R&D 2027-2031; industry intended KRW8tn 2026-2030; no actual grant/capex disbursement proven.",
         affected=["Korean sodium-ion and all-solid-state R&D", "Material and cell makers", "Industrial battery standards and proposed production tax incentives"],
         category="Policy",subtype="NONBINDING_SODIUM_ASSB_RND_ROADMAP",
         evidence=["MOTIR official September22 battery industrial roadmap document: verify KRW400bn planned new R&D programs 2027-2031 and KRW8tn proposed industry investment 2026-2030.",
                   "MOTIR original R&D program budget and standardized-test notice: verify 2027 sodium cell 160Wh/kg and 2028 all-solid-state 400Wh/kg as targets not test results."],
         confirm=["MOTIR 2027 R&D award notice naming actual funded project amounts would strengthen execution outlook; failure to award would weaken investment conversion outlook.",
                  "Certified sodium-ion 220Wh/kg 2030 cell test result and audited private KRW8tn CAPEX spending would strengthen roadmap realization outlook; missing results would weaken commercialization outlook."]),

    case(cid="KR_JEONNAM_BATTERY_RAW_MATERIALS_NATIONAL_SPECIAL_ZONE_DESIGNATION_20260930",
         rows=[1244],rep=1244,date="2026-09-30",region="KR",owner="Korean National Advanced Strategic Industry Committee and MOTIR",
         urls=["https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/172252/view"],
         title="전남 광양·여수·순천, 이차전지 기초원료 국가첨단전략산업 특화단지 신규 지정",
         stage="actual_zone_designation",legal_stage="stage_4_implementation_budget_guidance_or_registry",
         law_type="Administrative designation of National Advanced Strategic Industry specialized zone under existing law, not a new law",
         mandatory="Administrative committee designation on September30; exact gazette legal-effective date pending separate verification",
         fact="The 9th National Advanced Strategic Industry Committee on September30 newly designated Jeonnam Gwangyang–Yeosu–Suncheon for battery basic raw-material industrial specialization; company leaders plan approximately KRW5,372.4bn lithium refining and associated investment by 2036.",
         guard="The KRW5.3724tn is intended private investment through 2036, not money already invested, contracted or construction begun. The same meeting also designated robotics Daegu/Gyeongbuk and defense Changwon, separate sectoral decisions; do not multiply battery site counts. The image-sensor strategic-technology designation amendment requires future legislative completion.",
         impact="Realized administrative battery-material zone designation changes location-specific industrial support expectations while actual lithium-refining CAPEX and capacity remain contingent.",
         score=[18,18,0,9,8,4,3,2],
         actions=["SEP30_JEONNAM_BATTERY_RAW_MATERIALS_ZONE_DESIGNATED", "PLANNED_LITHIUM_REFINERY_CAPEX_KRW5_3724TN_BY2036_NOT_SPENT", "OTHER_SECTOR_ROBOT_AND_DEFENSE_ZONES_DISTINCT"],
         prior="Earlier April2026 regional applications for component and materials specialization were proposals; the September30 government committee action is an actual new administrative designation, not factory COD.",
         denominator="KRW5,372,400,000,000 announced for sector leaders' plans by 2036; distinct from broader three-sector KRW12,987.7bn planned by 2042.",
         affected=["Jeonnam Gwangyang Yeosu Suncheon lithium refining", "Korean upstream battery precursor/basic raw-material industrial suppliers"],
         category="Materials",subtype="ADMINISTRATIVE_BATTERY_MATERIAL_SPECIAL_ZONE",
         related=["2026-04-28_KR_04"],
         evidence=["MOTIR September30 official 9th committee notice: verify Jeonnam Gwangyang Yeosu Suncheon designated zone and private KRW5,372.4bn planned investment through 2036.",
                   "MOTIR official gazette designation document and permitted projects: verify original administrative notice date, site boundaries and actual lithium refining CAPEX committed."],
         confirm=["Final MOTIR specialized-zone gazette effective date and geographically defined legal boundaries would strengthen regulatory certainty outlook; a contrary gazette would weaken it.",
                  "Named private refinery building permit and documented 2036 cumulative project disbursement against KRW5.3724tn would strengthen capacity outlook; cancellations would weaken it."]),

    case(cid="UK_TESLA_POWERWALL2_FIRE_RISK_REPLACEMENT_OFFICIAL_20260928",
         rows=[1255],rep=1255,date="2026-09-28",region="UK",owner="UK Office for Product Safety and Standards (OPSS)",
         urls=["https://www.gov.uk/product-safety-alerts-reports-recalls/product-safety-report-tesla-powerwall-2-2609-0219"],
         title="영국 OPSS, Tesla Powerwall 2 일부 제품 화재 위험·무상교체 프로그램 공표",
         stage="safety_replacement_programme_initiated",tech_stage="material_recall_defect_fire_warranty_or_operating_failure",
         fact="UK OPSS published safety report 2609-0219 on September28: third-party-manufactured cells in affected Powerwall 2 units may develop excessive lithium plating, casing cracks, short-circuit and thermal runaway; Tesla initiated free replacement, and remotely discharged most affected units pending replacement.",
         guard="The affected unit count and specific cell maker are not established. The UK measure is a product safety report with modification/replacement program, not a proven fleet-wide Powerwall recall, not confirmation every unit burned, and not completed replacements. UK regulatory report describes non-compliance with the 2016 Electrical Equipment Safety Regulations for affected products.",
         impact="A newly documented grid-storage field safety failure mechanism and operating mitigation changes warranty/insurance and cell quality risk estimates.",
         score=[18,19,16,9,8,4,3,2],
         actions=["SEP28_UK_OPSS_POWERWALL2_DEFECT_REPORT", "TESLA_ACTUAL_REMOTE_DISCHARGE_AND_FREE_REPLACEMENT_PROGRAM_INITIATED", "UNIDENTIFIED_THIRD_PARTY_CELL_MAKER_NOT_ATTRIBUTED"],
         prior="Earlier residential Tesla storage product commercial offerings are unrelated; no same UK OPSS 2609-0219 safety event existed in locked Full.",
         denominator="Unknown affected device count; OPSS safety notification 2609-0219, published 2026-09-28.",
         affected=["UK Tesla Powerwall 2 owners", "Residential and light commercial ESS cell safety and installer replacements"],
         category="ESS",subtype="FIELD_SAFETY_CELL_DEFECT_REPLACEMENT",
         evidence=["UK OPSS official Product Safety Report 2609-0219: verify 2026-09-28 product report, lithium plating/casing fracture/thermal runaway mechanism and free modification programme.",
                   "Tesla original replacement-programme service document and UK installer reports: verify exact affected Powerwall2 unit count, discharged units and completed replacements."],
         confirm=["Tesla service records measuring completed replacement unit volume for UK report 2609-0219 would strengthen remedial progress outlook; unknown counts would weaken completion outlook.",
                  "Official cell supplier investigation naming third-party batch and demonstrated root-cause test result would strengthen risk localization outlook; no finding would weaken attribution outlook."]),

    case(cid="US_DOE_SPARK_31_TRANSMISSION_PROJECTS_20260924",
         rows=[1267],rep=1267,date="2026-09-24",region="US",owner="United States Department of Energy Office of Electricity",
         urls=["https://www.energy.gov/articles/energy-department-announces-speed-power-investments-across-26-states-lower-electricity"],
         title="미 DOE SPARK, 26개 주 31개 전력망 개선 프로젝트 지원 대상 선정 의향",
         stage="federal_preaward_selected_projects_intent_not_cash_disbursement",
         fact="DOE Office of Electricity announced September24 intention to fund 31 selected SPARK grid-modernization projects across 26 states, with projected US$5.25bn total investment: US$1.9bn DOE federal funding and US$3.35bn recipient cost share. Targets include reconductoring over 1,500 miles, grid-enhancing equipment on nearly 21,000 miles and over 23GW prospective capacity release.",
         guard="Selected/intended assistance is not paid-out US$5.25bn federal subsidy; DOE share is US$1.9bn and recipient share US$3.35bn. Target line miles and >23GW are prospective grid capacity, not completed BESS installations or new battery orders.",
         impact="A dated federal project-selection intention with identified transmission scope materially affects potential energy-grid constraints, indirectly ESS interconnection conditions.",
         score=[17,19,0,8,10,5,3,2],
         actions=["SEP24_DOE_SPARK_31_PROJECT_PREAWARD_SELECTION_26_STATES", "PLANNED_TOTAL_USD5_25BN_SPLIT_DOE1_9BN_RECIPIENT3_35BN", "PROSPECTIVE_23GW_GRID_HEADROOM_NOT_INSTALLED_BESS"],
         prior="US grid investments and ESS project contracts in Full are different programs; this September24 announcement concerns transmission grid upgrades rather than ESS developer awards.",
         denominator="31 projects in 26 US states; planned total US$5.25bn = federal1.9bn + recipient3.35bn; >23GW available grid capacity projected.",
         affected=["US high-capacity transmission operators", "Grid connection capacity and downstream ESS/AI power infrastructure"],
         category="Power",subtype="GRID_MODERNIZATION_SELECTED_PREAWARD",
         evidence=["DOE September24 official SPARK announcement document: verify 31 projects, 26 states, 1.9bn federal and 3.35bn recipient cost share, >23GW grid capacity estimate.",
                   "DOE official cooperative grant agreement and beneficiary construction document: verify actual award obligation date, federal disbursement and completed 1,500 reconductored line miles."],
         confirm=["DOE signed SPARK grant award notice listing obligated US$1.9bn federal amounts would strengthen funding execution outlook; cancelled awards would weaken it.",
                  "Utility completion report measuring >23GW grid availability and 1,500 installed reconductored miles would strengthen capacity transmission outlook; noncompletion would weaken it."]),

    case(cid="US_NTH_CYCLE_GLENCOR​E_BINDING_FEEDSTOCK_OFFTAKE_TERM_SHEET_20260922".replace("\u200b",""),
         rows=[1280,349],rep=1280,date="2026-09-22",region="US",owner="Nth Cycle and Glencore; Nth Cycle original press release filed by Kensington with US SEC",
         urls=["https://www.sec.gov/Archives/edgar/data/2102713/000119312526397915/d159150d425.htm"],
         title="Nth Cycle–Glencore, Project SHIELD 원료·산출물 공급구매 구속력 텀시트 체결",
         stage="executed_binding_term_sheet_definitive_agreement_not_yet_signed",
         fact="Nth Cycle's original September22 SEC-filed release confirms a binding term sheet with Glencore for Project SHIELD, discussing all projected black mass feedstock and off-take of refined MHP and battery-grade lithium carbonate; ten-year offtake value over US$1bn is a forecast-price estimate. Parties target definitive supply/offtake agreements by end-2026.",
         guard="Ten-year >US$1bn is projected contract value based on Q2 2026 forecast prices, not cash collected, guaranteed realized revenue or a completed final off-take. Glencore site assessment and international OYSTER expansion are possibilities. Prior Trafigura US$1.1bn conditional arrangement in locked Full R3_07 is distinct, and US DOE US$100m selected grant is not another newly received grant here.",
         impact="A binding early-stage supply/offtake arrangement makes material progress toward recycling feedstock and final-product marketability without claiming an operating plant or definitive contract.",
         score=[18,19,0,8,9,4,3,2],
         actions=["SEP22_NTH_GLENC​ORE_BINDING_TERM_SHEET".replace("\u200b",""), "PROJECT_SHIELD_PLANNED_100PCT_FEEDSTOCK_AND_OFFTAKE_NOT_DELIVERED", "TEN_YEAR_USD1BN_FORECAST_VALUE_NOT_BOOKED_REVENUE", "DEC2026_TARGET_FINAL_CONTRACT_NOT_SIGNED"],
         prior="Locked Full R3_07 describes a separate Nth Cycle–Trafigura conditional term arrangement; 2026 September Glencore is a new counterparty.",
         denominator="10-year preliminary offtake projected >USD1bn based on Q2-2026 assumptions, not fixed booked revenue or delivered tonnage.",
         affected=["Nth Cycle Project SHIELD recycling", "Glencore US black mass feedstock and battery material marketing", "US MHP and lithium carbonate circular supply chain"],
         category="Circular",subtype="BINDING_FEEDSTOCK_OFFTAKE_TERM_SHEET",
         related=["R3_07"],
         evidence=["SEC September22 Kensington Rule425 company filing document: verify Nth Cycle-Glencore binding term sheet, >USD1bn forecast 10-year value and end-2026 target definitive agreement.",
                   "SEC original definitive contract filing and Project SHIELD shipping documents: verify actual 100% feedstock/offtake minimum volumes, contract effective date and realized lithium/MHP batches."],
         confirm=["Nth Cycle and Glencore definitive 2026 offtake contract filing with purchased tonnes and prices would strengthen bankability outlook; no final agreement would weaken it.",
                  "Project SHIELD first MHP and lithium carbonate commercial shipment volume and audited revenue would strengthen realized market-flow outlook; absence would weaken it."]),

    case(cid="US_MOSS_LANDING_SEP18_CLEANUP_REIGNITION_1300_MODULES_20260918",
         rows=[1294],rep=1294,date="2026-09-18",region="US",owner="United States Environmental Protection Agency, Moss Landing cleanup response",
         urls=["https://www.epa.gov/ca/moss-landing-vistra-battery-fire-updates"],
         title="EPA, Moss Landing 해체 중 잔존 배터리 1,300모듈 재발화 공식 기록",
         stage="actual_ESS_thermal_failure_during_postfire_cleanup",tech_stage="material_recall_defect_fire_warranty_or_operating_failure",
         fact="US EPA response timeline confirms approximately 06:00 September18 a new fire in previously damaged battery remnants of the Moss Landing 300 building during cleanup; approximately 1,300 modules estimated burned, with temporary nearby shelter-in-place and no reported injuries. Fire subsided around 10:00.",
         guard="This is September2026 partial reignition during January2025 fire remediation, not a new 2026 commercial operating BESS fire or 56,000 additional modules; 56,000 is the old January2025 comparison. The 1,300 September figure is EPA estimate, not complete measured demolition tonnage. Not evidence the cleaned facility resumed operation.",
         impact="An independently dated second safety failure during decommissioning changes hazard/remediation, insurance and recycling risk beyond the September8 cleanup progress already represented in Full.",
         score=[17,18,0,8,9,4,3,2],
         actions=["SEP18_MOSS_LANDING_300_CLEANUP_REIGNITION", "EST_1300_MODULES_BURNED_NEW_EVENT", "SHELTER_IN_PLACE_THEN_RELEASE_NO_INJURIES_REPORTED"],
         prior="Full 2026-09-08_US_02 documents EPA cleanup progress, while January2025 initial battery warehouse fire is a separate historic baseline.",
         denominator="EPA estimate 1,300 burned modules on September18 compared with roughly 56,000 initial January2025 fire modules; no new 2026 COD.",
         affected=["Moss Landing 300 damaged building demolition", "ESS fire decommissioning and recycling safety", "Vistra and local emergency authorities"],
         category="ESS",subtype="POSTFIRE_CLEANUP_REIGNITION",
         related=["2026-09-08_US_02"],
         evidence=["US EPA official response timeline September18: verify 06:00 reignition, estimated 1,300 additional burned modules, 10:00 fire end and no injuries reported.",
                   "EPA original sampling and decommissioning safety report: verify post-September18 safe demolition dates, recovered/burned module counts and incident cause."],
         confirm=["EPA final September18 incident investigation reporting exact 1300 modules volume and fire cause would strengthen ESS hazard outlook; unknown cause would weaken the safety outlook.",
                  "Vistra/EPA completed decommissioning report with verified cleanup volume in tonnes and final closure date would strengthen remediation timeline outlook; a postponed schedule would weaken the timeline outlook."]),

    case(cid="EU_G_TBT_N_EU1242_INDUSTRIAL_BATTERY_PERFORMANCE_DRAFT_20261005",
         rows=[1324],rep=1324,date="2026-10-05",region="EU",owner="European Commission / WTO TBT notification system",
         urls=["https://technical-barriers-trade.ec.europa.eu/en/notification/40734"],
         title="EU, 산업용 배터리 내구·효율 및 배터리여권 기술요건 위임규정 초안 WTO 통보",
         stage="notified_draft_delegated_regulation_not_adopted",legal_stage="stage_2_bill_or_proposed_rule",
         law_type="Proposed Commission Delegated Regulation to supplement/amend Regulation EU 2023/1542; WTO TBT G/TBT/N/EU/1242",
         mandatory="No mandatory application date or legal force established; WTO comment deadline 2026-12-04",
         fact="European Commission WTO TBT G/TBT/N/EU/1242 arrived October5, 2026; proposed delegated regulation sets future electrochemical performance/durability minimums for rechargeable industrial batteries, second-life battery measurements, residential ESS round-trip efficiency, stationary ESS safety/SoH and battery passport QR/unique identifier parameters; comments through December4.",
         guard="Notification and draft annex are not a final adopted regulation, not currently enforced new minimum thresholds, and do not automatically apply residential ESS efficiency tests to every industrial battery. Battery passport technical parameters and second-life tests are distinct parts of the same draft.",
         impact="A precise regulatory proposal with measurable cycle-life, fade and efficiency parameters directly changes future ESS/battery compliance-design risk without implying it is in force.",
         score=[17,17,0,8,8,3,3,2],
         actions=["OCT05_EU_WTO_TBT_BATTERY_DELEGATED_DRAFT_NOTIFICATION", "DEC04_COMMENT_DEADLINE_NOT_ADOPTION", "MULTI_SUBJECT_PERFORMANCE_SAFETY_PASSPORT_PROPOSALS_NO_CURRENT_DUTY"],
         prior="EU Battery Regulation 2023/1542 is already the baseline law; this 2026 proposed delegated act is a separate rulemaking stage and is not an enactment of a new regulation.",
         denominator="WTO notification 40734; symbol G/TBT/N/EU/1242; formal comment deadline 2026-12-04, not entry into force.",
         affected=["Rechargeable industrial batteries", "Residential and stationary ESS", "Second-life battery suppliers", "EU battery passport technical-compliance chain"],
         category="Policy",subtype="EU_INDUSTRIAL_BATTERY_DELEGATED_DRAFT",
         evidence=["European Commission official October05 WTO TBT document notification 40734: verify G/TBT/N/EU/1242, residential ESS round-trip efficiency and industrial battery fade/lifetime proposed scope.",
                   "European Commission official adopted Delegated Regulation or withdrawn draft document: verify December04 comment deadline, final numbered standard parameters and legal effective dates."],
         confirm=["European Commission final delegated regulation publication and formal entry-into-force date would strengthen binding-compliance outlook; withdrawal would weaken it.",
                  "Final battery passport technical standards and measured capacity fade/round-trip efficiency threshold values would strengthen actionable product-design outlook; delay would weaken it."]),

    case(cid="US_EXIM_VAULTCO_GLENC​ORE_MERCURIA_2X500M_PARTNER_COMMITMENTS_20260923".replace("\u200b",""),
         rows=[700,709,851,852],rep=700,date="2026-09-23",region="US",owner="Glencore, Mercuria, EXIM-backed VaultCo initiative",
         urls=["https://www.glencore.com/media-and-insights/news/glencore-partners-with-us-exim-bank-to-build-strategic-minerals-reserve-fund",
               "https://mercuria.com/mercuria-commits-500-million-to-vaultco-u-s-critical-mineral-stockpile-in-partnership-with-the-u-s-export-import-bank/",
               "https://www.exim.gov/news/fact-sheet/project-vault"],
         title="미 VaultCo 비축망, Glencore·Mercuria 각각 5억달러 공급참여 약정",
         stage="two_signed_partner_critical_minerals_reserve_commitments_not_inventory_delivery",
         fact="On September23 Glencore and Mercuria separately announced participation in EXIM-backed VaultCo/Project Vault US strategic critical-mineral reserve, each a US$500m commitment to critical-mineral procurement and stockpiling partnerships; EXIM's up-to-US$10bn loan facility had been approved February2, not newly awarded September23.",
         guard="US$500m commitments from two separate commodity traders are not proof US$1bn cash has already been drawn, US$1bn minerals already purchased/delivered or a new September government US$10bn loan. Project Vault partner entry is distinct from Nth Cycle/Glencore Project SHIELD binding term sheet (September22) despite common Glencore name. Stockpile size, mineral list, funding draws, price support and release terms need further evidence.",
         impact="Separate commercial sourcing commitments by two traders make material organizational progress toward a previously approved US strategic mineral reserve, with distinct actor-level economic acts kept under one policy-event family.",
         score=[18,20,0,8,10,4,3,2],
         actions=["SEP23_GLENC​ORE_USD500M_VAULTCO_FOUNDING_PARTNER".replace("\u200b",""),
                  "SEP23_MERCURIA_USD500M_VAULTCO_ANCHOR_COMMITMENT", "FEB02_OLD_EXIM_LOAN_APPROVAL_UP_TO_USD10BN_NOT_NEW", "NO_VERIFIED_INVENTORY_STOCKPILE_DELIVERY"],
         prior="Project Vault announced and EXIM approved up to USD10bn loan in February2026; September2026 trader partner sourcing commitments are fresh follow-up acts, not re-approval of federal authority.",
         denominator="US$500m Glencore announcement + US$500m Mercuria announcement = US$1bn separate commitments, with no actual spent/drawn amount confirmed.",
         affected=["US industrial critical-mineral reserve", "Glencore minerals marketing", "Mercuria minerals sourcing", "US OEM supply security"],
         category="Upstream",subtype="STRATEGIC_RESERVE_PRIVATE_COMMITMENTS",
         evidence=["Glencore official September23 partner release document: verify USD500m critical-minerals commitment and first VaultCo participant selection without claiming completed delivery.",
                   "Mercuria original September23 company document and EXIM February02 official loan notice: verify separate USD500m Mercuria commitment and prior existing up-to-USD10bn financing authority."],
         confirm=["EXIM and VaultCo signed inventory purchase contract with paid USD500m partner tranche and actual mineral tonnage would strengthen reserve implementation outlook; undrawn commitments would weaken it.",
                  "Published VaultCo balance sheet stockpile purchase volume and release-price rules would strengthen reserve operational outlook; absent stock would weaken it."]),

    case(cid="US_HR9340_HOUSE_RATEPAYER_PROTECTION_ACT_PASSED_20260916",
         rows=[1200],rep=1200,date="2026-09-16",region="US",owner="US House Energy and Commerce Committee",
         urls=["https://energycommerce.house.gov/posts/ratepayer-protection-act-passes-house-with-strong-bipartisan-support"],
         title="미 하원, 데이터센터 100MW 이상 전력비 부담 심의법안 H.R.9340 통과",
         stage="House_bill_passed_not_enacted",legal_stage="stage_2_bill_or_proposed_rule",
         law_type="H.R. 9340 Ratepayer Protection Act, passed US House only; not a federal statute in force",
         mandatory="No current mandatory data-center rate allocation deadline; Senate, Presidential action and state PUC process not verified",
         fact="US House of Representatives passed H.R.9340 Ratepayer Protection Act on September16 by 417-3; it would require state public utility commissions to consider large-load standards for data centres drawing more than 100MW to bear incremental grid service costs.",
         guard="House passage does not enact law. It asks state commissions to consider cost-allocation strategies, not automatically imposes 100MW federal tariffs or forces every data center to buy BESS. Senate/Presidential enactment and state-specific tariffs require separate future facts.",
         impact="A concrete federal legislative advancement influences future grid-cost allocation expectations for AI centers, flexible load, power projects and ESS economics without present legal force.",
         score=[16,18,0,7,8,3,2,2],
         actions=["SEP16_HR9340_PASSED_HOUSE_417_TO_3", "PROPOSED_STATE_PUC_100MW_COST_ALLOCATION_CONSIDERATION", "NO_ENACTMENT_OR_TARIFF_YET"],
         prior="State PUC data-center large-load cost policies exist separately; this federal bill is not a final national tariff or battery-specific procurement rule.",
         denominator="417 voting yes, 3 no; proposed electricity load 100MW threshold, not 100MW of BESS procured.",
         affected=["US data centers >100MW proposed utility load standard", "State public utility commissions", "Grid interconnection/ESS economic signals"],
         category="Policy",subtype="HOUSE_PASSED_LARGE_LOAD_COST_ALLOCATION_BILL",
         evidence=["US House Energy and Commerce September16 official House-passage notice document: verify H.R.9340 417-3 vote and proposed >100MW incremental grid-cost PUC consideration.",
                   "US Congress original legislative status and published final statute or state rate-case order: verify 2026 House passage versus any enacted rule or tariff effective date."],
         confirm=["US Senate passage plus President signed H.R.9340 with effective date would strengthen nationwide policy likelihood outlook; stalled bill would weaken it.",
                  "State utility commission final >100MW data-center incremental cost tariff decision would strengthen observed ratepayer protection outlook; unchanged tariffs would weaken it."]),

    case(cid="US_PHMSA_5800_1_BATTERY_THERMAL_RUNAWAY_UAS_REPORT_FORM_DRAFT_20260921",
         rows=[425],rep=425,date="2026-09-21",region="US",owner="US Pipeline and Hazardous Materials Safety Administration",
         urls=["https://www.federalregister.gov/documents/2026/09/21/2026-19276/hazardous-materials-information-collection-activities",
               "https://www.phmsa.dot.gov/regulations/federal-register-documents/2026-19276"],
         title="미 PHMSA, 리튬전지 열폭주·드론 사고정보 추가 신고서 개편안 의견수렴",
         stage="proposed_incident_form_information_collection_revision",legal_stage="stage_1_roadmap_consultation_or_draft_standard",
         law_type="Notice/request for public comments on proposed revision to DOT Form 5800.1, OMB 2137-0039; not a final transport regulation",
         mandatory="Current Form 5800.1 remains mandatory under existing regulation; proposed revision not applicable until OMB approval after 2026-12-21 comment deadline",
         fact="PHMSA September21 Federal Register notice proposed amendments to hazardous-material transport incident report DOT Form 5800.1; draft adds explicit lithium-ion thermal-runaway indicators, accident circumstances and questions about UAS transportation, with comments due December21 and subsequent OMB approval needed.",
         guard="This is an information-collection and incident-reporting form proposal, not a new UL cell safety certification, not a changed battery carriage permission and not an approved mandatory revised form. Existing HMR incident-reporting obligations continue pending OMB action.",
         impact="Proposed discrete thermal-runaway and UAS incident fields could improve future transport safety traceability for battery manufacturers and defense-drone cargo supply without currently changing certification approvals.",
         score=[16,17,0,5,6,3,2,2],
         actions=["SEP21_PHMSA_DOT5800_1_REVISED_FORM_COMMENT_REQUEST", "PROPOSED_THERMAL_RUNAWAY_AND_UAS_REPORT_FIELDS_NOT_EFFECTIVE", "DEC21_COMMENTS_AND_FUTURE_OMB_APPROVAL_REQUIRED"],
         prior="Under 49 CFR 171.16 current incident report Form 5800.1 already applies to reportable hazardous-material transportation incidents; this action only proposes data-field changes.",
         denominator="Federal Register document 2026-19276; comment deadline 2026-12-21; current OMB control 2137-0039 remains effective.",
         affected=["Lithium-ion battery transport accident reporting", "UAS dangerous-goods incident data", "Hazmat filers and regulators"],
         category="Policy",subtype="DRAFT_BATTERY_UAS_HAZMAT_INCIDENT_REPORTING",
         evidence=["PHMSA official September21 Federal Register notice 2026-19276: verify draft DOT 5800.1 thermal runaway questions and proposed UAS incident tracking fields with December21 comment deadline.",
                   "PHMSA and OMB official revised information collection approval document: verify final Form 5800.1 fields, effective date and data reporting obligation."],
         confirm=["OMB final approval and PHMSA publication of revised DOT5800.1 effective date would strengthen future battery-incident data quality outlook; failed approval would weaken it.",
                  "Final Form5800.1 battery thermal-runaway metric and UAS incident response volume would strengthen measured safety exposure outlook; missing fields would weaken it."]),
]

WATCHES = [
  {"rows":[1299],"case_id":"CA_ELECTRA_WMC_FIVE_YEAR_NONBINDING_TERM_SHEET_20261013",
   "date":"2026-10-13","owner_urls":["https://www.sec.gov/Archives/edgar/data/1907184/000117184326006595/exh_991.htm"],
   "why":"SEC issuer exhibit confirms October13 Electra–WMC five-year term sheet for refinery cobalt working capital, exclusive marketing and future equity possibility; explicitly nonbinding beyond limited ancillary clauses, subject to due diligence, definite financing contracts, creditor approvals and refinery commissioning. No cash facility or capital injection is proven signed/received; prior Electra–Glencore cobalt agreement is distinct.",
   "future":"Electra/WMC executed definitive loan/offtake/equity agreements, committed amounts, drawdown dates, collateral terms, actual cobalt sulfate sale volumes and refinery first production."},
  {"rows":[1236],"case_id":"KR_2026_SEP_BATTERY_EXPORT_720M_YOY14PCT_OFFICIAL_METRIC_20261001",
   "date":"2026-10-01","owner_urls":["https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/172254/view"],
   "why":"MOTIR official October1 release records September 2026 secondary-battery exports USD720m, +14.0% year-on-year, fifth consecutive rising month and improvement in both quantity and unit price. Preserve as a verified protected aggregate metric, not a company contract or factory COD; full denominator and later revisions require materiality context.",
   "future":"MOTIR monthly revised commodity export dataset by quantity, USD value and price; subsequent monthly confirmation that price-volume growth persists or reverses."},
  {"rows":[423],"case_id":"US_OSHA_TUVSUD_UL2580_UL2743_PRELIM_NRTL_20260921",
   "date":"2026-09-21","owner_urls":["https://www.federalregister.gov/documents/2026/09/21/2026-19268/tuv-sud-america-inc-application-for-expansion-of-recognition"],
   "why":"OSHA September21 published a preliminary favorable finding on TÜV SÜD America NRTL expansion to UL 2580 (EV batteries) and UL 2743 (portable power packs); agency explicitly states no interim/temporary approval, and October6 comment deadline. Not an expansion of UL1642 cell certification, not a granted final NRTL scope or an SBTL film certification.",
   "future":"OSHA separate final grant/denial Federal Register notice confirming UL2580 and UL2743 under TUVAM NRTL authorization, exact effective date and accredited laboratory scope."},
]

REJECTS = [
  {"rows":[855,1133],"case_id":"EU_DEMOCRATIC_RESILIENCE_FIMI_TRAINING_NOT_BATTERY_20260925",
   "date":"2026-09-25","owner_urls":["https://commission.europa.eu/news-and-media/news/train-trainers-programme-successfully-delivered-its-first-edition-2026-09-25_en"],
   "why":"EC Directorate-General for Communication September25 original article is a September7–11 course for officials on foreign information manipulation and psychological defence; no EV, ESS, battery materials, industrial policy instrument, energy price or industrial sourcing action appears. Two captures of the same official article are off-scope, not two battery events."},
]


def main() -> None:
    p=argparse.ArgumentParser()
    for k in ("base","full","output","receipt"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    assert sha256(a.base)==BASE_SHA and sha256(a.full)==FULL_SHA
    d,full=read(a.base),read(a.full)
    assert len(full["cards"])==1676 and len(d["decision_ledger"])==1330
    assert len(d["promotion_reassessment_ledger"])==105 and len(d["strict_passed_spec"])==20
    assert {k:len(d[k]) for k in ("candidate_review_pool","watchlist_context_pool","reject_or_support_only_pool") }=={
        "candidate_review_pool":581,"watchlist_context_pool":660,"reject_or_support_only_pool":39}
    old={r["source_row_index"]:r for r in d["decision_ledger"]}
    target={i for e in EVENTS for i in e["rows"]} | {i for w in WATCHES for i in w["rows"]} | {i for r in REJECTS for i in r["rows"]}
    assert len(target)==21 and target=={226,302,1277,1244,1255,1267,349,1280,1294,1324,700,709,851,852,1200,425,423,1299,1236,855,1133}
    old_formal={r["candidate_id"] for r in d["promotion_reassessment_ledger"]}
    assert not ({old[i]["story_id"] for i in target}&old_formal)
    ledger={r["story_id"]:r for r in d["decision_ledger"]}
    review={r["story_id"]:r for r in d["review_pool_resolution_ledger"]}
    template=d["strict_passed_spec"][-1]
    promoted,supported,watched,rejected=set(),set(),set(),set()
    results=[]

    def formal_entry(idx:int,e:dict,status:str,to:str,resolved:str):
        o=old[idx]
        d["promotion_reassessment_ledger"].append({
            "candidate_id":o["story_id"],"economic_event_cluster_id":e["case_id"],
            "before_pool":o["stage_a_pool"],"after_pool":to,
            "promotion_reassessment_status":status,"resolved":resolved,
            "remaining":e.get("must_not",e.get("future",e.get("why",""))),
            "source_candidates":e["owner_urls"],"source_observation_preserved":True,
        })

    def update_review(idx:int,pool:str,reason:str,next_trigger:str,disposition:str,policy:str):
        sid=old[idx]["story_id"]
        if pool=="strict_passed_spec":return
        row=review[sid]
        row.update({
            "original_review_pool_partition":pool,"current_disposition":pool,
            "disposition_basis":reason,"carry_forward_policy":policy,
            "next_action_condition":next_trigger,"final_review_pool_disposition":disposition,
            "reviewed_by_stage_or_pass":"PROMPT_0_1P_V4_20260829 first-party CP19",
            "review_artifact_id":"STAGE_A_CHECKPOINT_19_FORMAL_20261101",
        })

    def attach(idx:int,e:dict,classification:str,extra:list[dict]|None=None):
        sid=old[idx]["story_id"]
        edges=[{"event":u,"role":"distinct_child_or_stage_preserved"} for u in e.get("event_units",[e["case_id"]])]
        edges+=extra or []
        ledger[sid]["formal_0_1P_cp19_source_to_economic_act_edges_20261101"]=edges
        ledger[sid]["cp19_source_identity_preserved"]={
            "story_id":sid,"source_row_index":idx,"headline_raw":old[idx]["headline_raw"],
            "primary_url":old[idx]["primary_url"]}
        results.append({"row":idx,"source_id":sid,"result":classification,
                        "event_family":e["case_id"],"source_url":old[idx]["primary_url"],
                        "first_party_owner_urls":e["owner_urls"],"economic_act_edges":edges})

    for e in EVENTS:
        source_rows=[old[i] for i in e["rows"]]
        rep=old[e["representative"]]
        if e["route"]=="execution_anchor_route":
            spec=execution_strict(rep,template,e,source_rows)
        else:
            spec=strict_case(rep,template,e,source_rows)
            spec.update({
                "assessment_profile":"validated_early_policy_stage" if e["policy_stage"]<=2 else "administrative_designation_actual",
                "procedural_status":e["procedure"],
                "legal_policy_stage":e["legal_stage"],
                "effective_date":e["mandatory"],
                "mandatory_application_date":e["mandatory"],
                "structural_non_execution_reason":e["increment"]+" "+e["must_not"],
                "why_execution_event_not_required":"An independently published structural legal or industrial roadmap stage changes supply-chain conditions without requiring present plant operation.",
                "extraterritorial_effect":"Rules or policy apply in named region only; overseas sourcing effect remains an inference.",
            })
            if e["policy_stage"]<=2:
                spec["adoption_date"]="NOT_ADOPTED — formally published procedural stage only, no final binding rule"
                spec["procedural_status"]=e["procedure"]+" No final regulation has been adopted by this act."
                spec["publication_date"]=e["date"]
        spec.update({
            "headline":e["title"],"title_raw":e["title"],
            "representative_date":e["date"],"publication_date":e["date"],
            "date_role":{**spec["date_role"],"event_date":e["date"],"announcement_date":e["date"],
                         "representative_date_basis":"Dated owner original stage; no inference from collector date."},
            "assessment_method":"PROMPT_0_1P_V4_20260829 original owner, locked Full1676 and event-act audit CP19",
            "formal_0_1P_cp19_strict_event_20261101":{
                "case_id":e["case_id"],"representative_source_row":e["representative"],
                "owner_urls":e["owner_urls"],"new_independent_economic_event":True,
                "subacts":e["event_units"],"stage_b_fact_adoption":False,"canonical_card_write":False,
            },
        })
        score_total=sum(e["score"])
        spec["decision_value_classification"]=("high_decision_value" if score_total>=70 else
             "material_industry_signal" if score_total>=55 else
             "standard_monitoring" if score_total>=40 else "low_independent_value")
        spec["evidence_needed_for_stage_b"]=[
            item+" Official document to verify original announcement date "+e["date"]+" and stated status."
            for item in e["evidence"]
        ]
        assert spec["stage_b_authorized"] is False and spec["accepted_facts_approved"] is False
        d["strict_passed_spec"].append(spec)
        ledger[rep["story_id"]].update(copy.deepcopy(spec))
        attach(e["representative"],e,"FORMAL_STRICT_EVENT_SELECTOR_ONLY")
        promoted.add(rep["story_id"])
        formal_entry(e["representative"],e,"PROMOTED_VALIDATED_STRICT","strict_passed_spec",e["new_fact"])
        for i in e["rows"]:
            if i==e["representative"]:continue
            r=old[i]
            sup=support_row(r,e,rep["story_id"])
            sup["new_verified_fact"]="Same economic event, no independently dated second contract/action: "+e["new_fact"]
            if i==349:
                sup["headline_original_overstates_stage"]= "Report says 10-year $1bn 'offtake deal'; original SEC says binding term sheet and future definitive agreement."
            ledger[r["story_id"]].update(copy.deepcopy(sup))
            d["reject_or_support_only_pool"].append(sup)
            attach(i,e,"FORMAL_SUPPORT_ONLY_SAME_OWNER_ECONOMIC_ACT")
            supported.add(r["story_id"])
            update_review(i,"reject_or_support_only_pool",sup["final_reason"],
                          "New dated owner contract or fulfilled milestone only",
                          "support_source_only_after_review","support_source_only")
            formal_entry(i,e,"FORMAL_SAME_EVENT_SUPPORT_ONLY","reject_or_support_only_pool",sup["final_reason"])

    for e in WATCHES:
        idx=e["rows"][0]
        o=old[idx]
        w=formal_watch(o,e,[o],o["story_id"])
        if idx==1236:
            w["protected_support_metric"]={"month":"2026-09","usd_millions":720,"yoy_pct":14.0,
                "volume_and_unit_price_both_improved":True,"consecutive_growing_months":5,
                "source":"MOTIR original October1 2026 export report"}
        ledger[o["story_id"]].update(copy.deepcopy(w))
        d["watchlist_context_pool"].append(w)
        attach(idx,e,"FORMAL_WATCH_ORIGINAL_STAGE_OR_PROTECTED_METRIC")
        watched.add(o["story_id"])
        update_review(idx,"watchlist_context_pool",e["why"],e["future"],
                      "watchlist_only_after_review","carry_forward_to_watchlist")
        formal_entry(idx,e,"FORMAL_WATCH_NO_CARD","watchlist_context_pool",e["why"])

    for e in REJECTS:
        for idx in e["rows"]:
            o=old[idx]
            row=copy.deepcopy(o)
            row.update({
                "stage_a_pool":"reject_or_support_only_pool", "ledger_decision":"reject_or_support_only_pool",
                "editorial_bucket":"reject_or_support_only_pool", "review_pool_partition":"reject_or_support_only_pool",
                "review_pool_subtype":"out_of_scope_verified_original", "review_pool_resolution_status":"closed_not_cardable",
                "assessment_status":"FORMAL_0_1P_REJECT_OUT_OF_SCOPE_ORIGINAL_OWNER",
                "assessment_method":"PROMPT_0_1P_V4_20260829 original publisher body inspection",
                "promotion_reassessment_status":"FORMAL_REJECT_OUT_OF_INDUSTRY_SCOPE",
                "final_review_pool_disposition":"not_cardable_after_review",
                "reject_or_support_only_basis":e["why"],"final_reason":e["why"],
                "whether_support_source_only":False,"reason_not_new_card":e["why"],
                "why_not_strict_passed_spec":e["why"],"independent_cardability_gate":{
                    "status":"FAIL","reason":e["why"],"full_schema_viability":"FAIL",
                    "distinct_event_or_stage_progression":False,"duplicate_or_reinforcement_note":"Same off-industry EC training source for both observations."},
                "new_verified_fact":e["why"],"remaining_uncertainty":"No industry-specific battery or ESS act appears in EC original.",
                "economic_event_cluster_id":e["case_id"],
                "canonical_card_write_allowed":False,"accepted_facts_approved":False,"stage_b_authorized":False,
                "formal_0_1P_cp19_off_topic_rejection_20261101":{
                    "owner_urls":e["owner_urls"],"document_publication_date":e["date"],
                    "no_source_deletion":True,"source_original_preserved":True,"not_battery_scope":True},
            })
            ledger[o["story_id"]].update(copy.deepcopy(row))
            d["reject_or_support_only_pool"].append(row)
            attach(idx,e,"FORMAL_REJECT_OUT_OF_SCOPE_NO_CARD")
            rejected.add(o["story_id"])
            update_review(idx,"reject_or_support_only_pool",e["why"],"Closed unless primary original has materially revised battery-related content.",
                          "not_cardable_after_review","closed_not_cardable")
            formal_entry(idx,e,"FORMAL_REJECT_OUT_OF_SCOPE","reject_or_support_only_pool",e["why"])

    closed=promoted|supported|watched|rejected
    assert len(closed)==len(target)==21
    assert len(promoted)==10 and len(supported)==6 and len(watched)==3 and len(rejected)==2
    d["candidate_review_pool"]=[r for r in d["candidate_review_pool"] if r["story_id"] not in closed]
    d["watchlist_context_pool"]=[r for r in d["watchlist_context_pool"] if r["story_id"] not in closed]
    d["watchlist_context_pool"] += [ledger[old[e["rows"][0]]["story_id"]] for e in WATCHES]
    d["review_pool_resolution_ledger"]=[r for r in d["review_pool_resolution_ledger"] if r["story_id"] not in promoted]
    expected={"strict_passed_spec":30,"candidate_review_pool":563,"watchlist_context_pool":660,
              "reject_or_support_only_pool":47,"existing_reinforcement":30,
              "review_pool_resolution_ledger":1270,"promotion_reassessment_ledger":126}
    assert all(len(d[k])==n for k,n in expected.items()),{k:len(d[k]) for k in expected}
    assert sum(len(d[k]) for k in ("strict_passed_spec","candidate_review_pool",
                                      "watchlist_context_pool","reject_or_support_only_pool","existing_reinforcement"))==1330
    assert len({r["story_id"] for r in d["decision_ledger"]})==1330
    assert len({r["candidate_id"] for r in d["promotion_reassessment_ledger"]})==126
    s=d["summary"]
    s.update({"strict_passed_spec_count":30,"existing_reinforcement_count":30,"duplicate_or_reinforcement_count":30,
              "needs_review_count":1270,"processed_priority_source_observations":126,
              "processed_priority_economic_clusters":s["processed_priority_economic_clusters"]+10,
              "unprocessed_editorial_observations":1204})
    s["pool_counts"]={k:len(d[k]) for k in ("strict_passed_spec","candidate_review_pool","watchlist_context_pool",
                                            "reject_or_support_only_pool","existing_reinforcement","rejected","support_source_only")}
    d["review_pool_partition_summary"]={k:len(d[k]) for k in ("candidate_review_pool","watchlist_context_pool","reject_or_support_only_pool")}
    coverage_maps(d)
    import sys
    sys.path.insert(0,str(a.full.resolve().parent.parent))
    from validation_scripts.stage_a_full_v3_completeness_review4943656188 import _expected_summary_id_arrays
    for k,v in _expected_summary_id_arrays(d).items():
        if k in s:s[k]=v
    att=d["pre_native_0_1P_attachment_manifest_20261101"]
    previous=att["formal_review_completed_source_ids"]
    now=[r["source_id"] for r in sorted(results,key=lambda x:x["row"])]
    assert len(previous)==60 and len(set(previous))==60 and len(now)==21 and not (set(previous)&set(now))
    att.update({"new_formal_decisions":81,"new_strict_promotions":22,
                "formal_review_completed_after_attachment_count":81,
                "formal_review_completed_source_ids":previous+now,
                "remaining_formal_source_count":1204,
                "native_validator_scope_warning":"Native strict and lineage contracts pass on decided items only; 1204 Source IDs still need formal event-level disposition before global Stage B clearance."})
    d["formal_0_1P_cp19_owner_document_batch_20261101"]={
        "authority":"PROMPT_0_1P_V4_20260829","base_cp18_sha256":BASE_SHA,
        "new_formal_source_ids":21,"new_strict_economic_event_families":10,
        "same_event_support_source_ids":6,"watch_or_protected_metric_source_ids":3,
        "owner_verified_off_industry_reject_source_ids":2,
        "formal_total":126,"pending_total":1204,
        "strict_total":30,"source_ids_preserved_total":1330,
        "source_to_economic_act_edges":sorted(results,key=lambda x:x["row"]),
        "case_index":{e["case_id"]:{"source_rows":e["rows"],"representative_row":e["representative"],
            "event_date":e["date"],"owner_urls":e["owner_urls"],"economic_subacts":e["event_units"],
            "stage_guard":e["must_not"]} for e in EVENTS},
        "protected_support_not_silently_dropped":True,
        "two_actor_vaultco_commitments_kept_distinct":True,
        "global_stage_a_status":"HOLD_OPEN_1204_UNADJUDICATED",
        "stage_b_executed":False,"new_published_cards":0,"canonical_main_full_related_mutations":0,
    }
    d["recommended_for"]=["Finish 1204 pending formal Source ID judgments; protect event-level substages and preserve all original IDs. Global Stage A HOLD."]
    d["next_call_recommendation"].update({
        "pending_parallel_or_followup_call":"review_pool/treasure triage",
        "pending_input_universe":"candidate_review_pool[] + eligible treasure/review-only universe",
        "reason":"Stage B strict-only eligibility is not global Stage A editorial approval while 1204 Source IDs lack formal dispositions.",
        "blocked_items_summary":d["review_pool_partition_summary"],
    })
    write(a.output,d)
    receipt={"status":"PENDING_NATIVE_AND_INDEPENDENT_QC",
             "artifact_type":"STAGE_A_CP19_OWNER_PRIMARY_DOCUMENT_BATCH_FORMAL",
             "base_sha256":BASE_SHA,"output_sha256":sha256(a.output),"locked_full_sha256":FULL_SHA,
             "new_formal":21,"new_strict":10,"new_support":6,"new_watch":3,"new_reject":2,
             "cumulative_formal":126,"remaining":1204,"cumulative_strict":30,
             "source_decisions":sorted(results,key=lambda x:x["row"]),
             "no_stage_b":True,"global_status":"HOLD","no_main_full_related_mutation":True}
    write(a.receipt,receipt)
    print(json.dumps({k:receipt[k] for k in ("output_sha256","new_formal","new_strict","new_support",
                "new_watch","new_reject","cumulative_formal","remaining","cumulative_strict")},indent=2))


if __name__=="__main__":main()

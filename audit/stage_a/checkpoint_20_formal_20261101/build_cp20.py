#!/usr/bin/env python3
"""CP20: original-owner backed event/action split, read-only CP19 baseline.

27 previously unadjudicated Source IDs: 12 independent event representatives,
14 one-event support observations and 1 existing Full-event reinforcement.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from build_stage_a_checkpoint_19_20261101 import case
from build_stage_a_formal_kr_two_events_20261101 import coverage_maps, read, sha256, support_row, write
from build_stage_a_formal_usjp_four_events_20261101 import execution_strict

BASE_SHA="bf30369c00bd528b4ab32c628a388b48a56471ac5e8f34fd22631bcb8eaead7d"
FULL_SHA="d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9"

# Facts in this mapping are source-level judgments, not Stage B accepted facts.
# A detailed Stage B primary-document package is still required before any card.
FACTS=[
 dict(cid="CN_NIO_GEELY_RECIPROCAL_POWER_EQUITY_DEFINITIVE_AGREEMENTS_20260927",
      rows=[869,870,1082,1263],rep=1263,date="2026-09-27",region="CN",scope="China",
      title="NIO·Geely, 배터리 스왑·충전 사업 교차지분 거래 최종계약 체결",
      owner="NIO Inc. investor relations",urls=["https://ir.nio.com/news-releases/news-release-details/nio-announces-definitive-agreements-strategic-transaction-geely"],
      stage="signed_conditional_definitive_equity_transaction_not_closed",
      fact="On September27 NIO signed definitive agreements under which Geely will contribute Yiyi Chongqing's entire equity and RMB640m cash to NIO Power for an initial 30% equity interest, post-money NIO Power valuation around RMB16bn; NIO China also agrees to take 10% of Geely Haohan Energy, and Geely has an option for a further RMB640m cash infusion within specified terms.",
      guard="All equity transactions are subject to regulatory approval/closing conditions, not completed purchases or actual cash contribution. Geely's 30% stake may ratchet down to 20% on milestones; 34% is conditional on separately exercising the option. Future Geely vehicle battery-swap compatibility is preliminary, not an approved launched fleet.",
      impact="Cross-ownership and charging/swapping infrastructure economics could shift across two rival Chinese auto groups, but signed agreements have not transferred equity.",
      score=[22,20,0,10,8,5,3,2],
      acts=["SIGNED_GEELY_IN_KIND_YIYI_PLUS_RMB640M_FOR_INITIAL_30PCT_NIO_POWER_CONDITIONAL",
            "SIGNED_NIO_CHINA_10PCT_HAOHAN_EQUITY_SWAP_CONDITIONAL",
            "OPTIONAL_SECOND_RMB640M_GEELEY_CASH_FOR_34PCT_NOT_EXERCISED",
            "GEELY_SWAP_COMPATIBLE_FUTURE_VEHICLES_PRELIMINARY_ONLY"],
      prior="Past NIO station openings and Geely electric-vehicle charging partnerships are distinct; no 2026 Sep27 reciprocal equity transaction exists in locked Full.",
      metric="Sep27 RMB640m initial cash plus full Yiyi equity, conditional 30% NIO Power and 10% Haohan, RMB16bn post-money valuation; prospective option second RMB640m",
      denom="Initial proposed equity: Geely 30.0%, NIO China 63.6%, Wuhan Guangchuang 6.4%; all subject to completion; potential Geely ratchet as low as 20%.",
      affected=["NIO Power battery swapping network","Geely commercial swap Yiyi unit","Geely Haohan charging infrastructure"],cat="Downstream",sub="SIGNED_CONDITIONAL_CROSS_EQUITY_SWAP_NETWORK"),

 dict(cid="AU_GLOBAL_LITHIUM_TITAN_BINDING_SCHEME_AUD333M_20260922",
      rows=[337,338,342,343,683],rep=683,date="2026-09-22",region="AU",scope="Australia and UAE lithium refining supply chain",
      title="Global Lithium–Titan, 호주 Manna 리튬자산 3.33억 호주달러 조건부 인수약정",
      owner="Global Lithium Resources ASX:GL1 original signed SID announcement",urls=["https://newswire.iguana2.com/2fee0049d633f441/announcements/gl1.asx/6A1344840/GL1_Global_Lithium_enters_into_binding_SID_with_Titan.pdf"],
      stage="binding_scheme_implementation_deed_not_acquisition_close",
      fact="Global Lithium filed September22 binding Scheme Implementation Deed with Titan Australia Mining (Titan Lithium Group) for proposed 100% cash acquisition at A$1.15 per share, approximately A$333m fully diluted equity value; separate up-to-A$120m four-tranche bridge facility supports Manna development pending scheme.",
      guard="An entered binding SID is not a completed takeover or paid A$333m. Shareholder 75%-by-votes, court, Australian FIRB/ACCC and independent expert conditions remain, with late-December meeting and target January2027 implementation. A$120m bridge is an up-to facility, not evidenced full drawdown; Manna plant not yet producing or feeding UAE refinery.",
      impact="A binding proposed change of ownership plus conditional project bridge facility could shift control of an Australian lithium asset into a UAE integrated supply chain.",
      score=[22,19,0,10,8,4,3,2],
      acts=["SEP22_SIGNED_BINDING_AUD333M_GLOBAL_LITHIUM_TITAN_SCHEME_NOT_CLOSED",
            "UP_TO_AUD120M_BRIDGE_FACILITY_FOUR_TRANCHES_NOT_FULLY_DRAWN",
            "COURT_SHAREHOLDER_FIRB_ACCC_APPROVALS_PENDING"],
      prior="Titan Mining US graphite developments in locked Full are a distinct US company; no exact Titan Lithium/Global Lithium Australia transaction in Full.",
      metric="A$333m scheme enterprise/equity consideration A$1.15 per share; up to A$120m bridge; 2027 planned completion date",
      denom="277.5m issued shares plus options/rights to estimate A$333m fully diluted equity; bridge up to A$120m of conditional funding.",
      affected=["Global Lithium Manna lithium project","Titan Lithium UAE refining integration","Australian lithium mining investment"],cat="Upstream",sub="BINDING_SCHEME_IMPLEMENTATION_DEED_NOT_CLOSED"),

 dict(cid="SA_GOTION_6GWH_THREE_SITE_BESS_ORDER_20260911",
      rows=[497],rep=497,date="2026-09-11",region="SA",scope="Saudi Arabia",
      title="Gotion, 사우디 3개 대형 ESS 현장 6GWh 공급 수주 발표",
      owner="Gotion High-tech official corporate news",urls=["https://www.gotion.com.cn/newsInfo/979"],
      stage="company_confirmed_BESS_supply_order_not_completed_delivery",
      fact="Gotion High-tech official September11 statement says it won a 6GWh BESS system supply order covering three major battery storage stations in Saudi Arabia's first large BESS project batch, with site construction under way.",
      guard="Six GWh represents company-announced awarded storage-supply volume, not six GWh shipped, installed, commissioned or collected as revenue; no named offtake price or final operation date is proven in release. Do not merge with prior 2GW/8GWh 15-year Saudi tolling award as if Gotion were that developer.",
      impact="A material China-to-Saudi LFP/BESS supply placement tests a new regional grid-storage supply chain, distinct from storage-services contracts.",
      score=[20,22,0,9,6,5,3,2],acts=["SEP11_GOTION_SAUDI_THREE_SITE_BESS_6GWH_AWARDED_SUPPLY","CONSTRUCTION_STARTED_NOT_GOTION_DELIVERY_OR_COD"],
      prior="Locked Full August20 Saudi 2GW/8GWh storage service contracts concerned developers, not Gotion's battery supply order.",
      metric="6GWh Gotion battery storage solutions to three Saudi stations, company release 2026-09-11",
      denom="Three Saudi ESS stations, aggregate 6GWh announced Gotion system order; exact project line MW and realized GWh unreported.",
      affected=["Saudi utility BESS","Gotion system supply","Chinese battery exports to Middle East"],cat="ESS",sub="SIGNED_SUPPLY_ORDER_NOT_SHIPPED"),

 dict(cid="FI_SUNGROW_DELTA_600MWH_FRAMEWORK_EXECUTION_TWO_PROJECTS_20260924",
      rows=[728,1068],rep=728,date="2026-09-24",region="FI",scope="Finland",
      title="Sungrow–Delta Capacity, 핀란드 2개 ESS 총 600MWh 공급 단계 확정",
      owner="Sungrow Europe official press release",urls=["https://www.sungrowpower.com/eu/en/delta-karppio-akkuone"],
      stage="actual_two_project_delivery_allocation_under_prior_framework",
      fact="Sungrow on September24 confirmed two Finland projects totaling 250MW/600MWh, Kärppiö in Teuva and AKKU One in Lapinlahti, supplied under an earlier 1GWh framework signed at Intersolar; the company describes the original 1GWh framework as fulfilled at this date, while sites are construction-stage.",
      guard="600MWh is specified project allocation/supply agreement fulfillment, not an additional 1GWh new framework on September24, and not 600MWh operating. 2027 commissioning remains scheduled. Karppio and AKKU One are separate assets; do not sum their 600MWh twice with the separate AKKU One construction-stage observation.",
      impact="Named project delivery obligations under a framework give a more concrete supplier-order stage while asset operation remains later.",
      score=[19,20,0,9,7,4,3,2],acts=["SEP24_600MWH_COMBINED_DELIVERY_ALLOCATION_KARPPIO_AND_AKKU_ONE","PREEXISTING_1GWH_FRAMEWORK_REPORTED_FULFILLED_NOT_NEW_1GWH","FINLAND_250MW_600MWH_2027_COD_NOT_YET"],
      prior="Prior 1GWh framework at Intersolar, and September17 AKKU One construction milestone, are distinct economic stages for the same named assets.",
      metric="250MW/600MWh two Finland assets, pre-existing 1GWh framework fulfillment and 2027 scheduled COD",
      denom="Two named 125MW/300MWh batteries; 600MWh aggregate project energy, not a new 1GWh system order.",
      affected=["Sungrow BESS delivery","Delta Capacity Kärppiö and AKKU One","Finland power flexibility"],cat="ESS",sub="FRAMEWORK_SPECIFIC_DELIVERY_ALLOCATION"),

 dict(cid="FI_AKKU_ONE_COVENERGO_DELTA_125MW_300MWH_CONSTRUCTION_START_20260917",
      rows=[367],rep=367,date="2026-09-17",region="FI",scope="Finland",
      title="Covenergo–Delta Capacity, 핀란드 AKKU One 125MW·300MWh 착공",
      owner="Delta Capacity/Covenergo official project statement",urls=["https://www.deltacapacity.com/post/covenergo-and-delta-capacity-partner-on-125-mw---300-mwh-akku-one-bess-project-in-lapinlahti-finlan"],
      stage="physical_BESS_construction_under_way_not_COD",
      fact="Delta Capacity and Covenergo September17 owner announcement confirms site construction underway for AKKU One 125MW/300MWh BESS in Lapinlahti; Covenergo majority ownership, acquired ready-to-build from Helios Nordic Energy, with Q4 2027 target commissioning.",
      guard="Construction start is not battery delivery or COD. This 300MWh is a component of Sungrow's separately announced September24 two-site 600MWh supply allocation; it is not another 300MWh demand uplift on top of that aggregate and not the later Oct financial close or partial tolling action.",
      impact="Physical construction crosses a real ESS execution stage for Finnish grid flexibility without duplicating supplier purchase volume.",
      score=[18,19,0,9,7,4,3,2],acts=["SEP17_AKKU_ONE_125MW_300MWH_CONSTRUCTION_STARTED","Q4_2027_TARGET_COD_NOT_ACTUAL_OPERATION","ALREADY_COUNTED_WITHIN_SUNGROW_DELTA_600MWH_SUPPLY_NOT_EXTRA_MWH"],
      prior="Ready-to-build asset acquisition and 1GWh Sungrow supplier framework predated the September17 owner construction-start confirmation.",
      metric="AKKU One 125MW/300MWh physical construction underway September17, target Q4 2027 commissioning",
      denom="AKKU One individual asset 125MW/300MWh; subset of future two Finland plants totaling 600MWh.",
      affected=["AKKU One BESS construction","Covenergo owner and Delta Capacity project management","Finnish grid"],cat="ESS",sub="PHYSICAL_BESS_CONSTRUCTION_NOT_COD"),

 dict(cid="GL_CATL_KUEHNE_NAGEL_BATTERY_LOGISTICS_SWAP_MOU_20260918",
      rows=[865,1156],rep=865,date="2026-09-18",region="GL",scope="Europe transport flows and China logistics pilot",
      title="CATL–Kuehne+Nagel, 배터리 물류·운송 전동화·교환식 중형트럭 MOU 체결",
      owner="CATL official corporate news",urls=["https://www.catl.com/en/news/7012.html"],
      stage="signed_strategic_logistics_MOU_pilots_future",
      fact="CATL September18 confirms signed Memorandum of Understanding with Kuehne+Nagel for battery logistics and European transport-flow electrification; a Qiji heavy-truck battery-swap pilot is envisaged in China and recycling/aftersales/charging/ESS sites are possible cooperation fields.",
      guard="Signing a logistics MoU is not commercial delivery, signed battery orders, launched Qiji swapping pilot or already commissioned logistics-site BESS. This is a different counterparty and September18 stage from CATL–DHL September14 European Green Freight Corridors MoU.",
      impact="A global logistics provider's battery transport and electrification framework may alter cross-border supply-chain design, but named pilots have not yet been executed.",
      score=[18,18,0,6,7,4,3,2],acts=["SEP18_CATL_KUEHNE_NAGEL_SIGNED_LOGISTICS_MOU","QJIJI_TRUCK_BATTERY_SWAP_PILOT_FUTURE_ONLY","POTENTIAL_LOGISTICS_SITE_ESS_NO_INSTALLED_VOLUME"],
      prior="CATL-DHL Europe freight corridor signing on September14 has different counterparty and scope; this Kuehne+Nagel event is separate.",
      metric="September18 CATL-Kuehne+Nagel MoU signature, proposed Europe electrified flows and future China Qiji pilot",
      denom="No disclosed contracted GWh or delivered electrified truck count; Scope3 and logistics network are strategic coverage.",
      affected=["CATL global battery freight","Kuehne+Nagel logistics","Qiji truck swapping pilot"],cat="Power",sub="SIGNED_LOGISTICS_ELECTRIFICATION_MOU"),

 dict(cid="EU_CATL_DHL_GREEN_FREIGHT_CORRIDOR_MOU_20260914",
      rows=[165],rep=165,date="2026-09-14",region="EU",scope="European Union freight corridors",
      title="CATL–DHL, 유럽 전기화물·충전·교환망 세부 MOU 체결",
      owner="CATL official corporate news",urls=["https://www.catl.com/en/news/6999.html"],
      stage="signed_Europe_focused_MOU_not_physical_corridor_deployment",
      fact="CATL and DHL Group signed a September14 European Green Freight Corridors-specific MoU to explore large commercial EV corridors, fleet charging, ESS systems, mobile power and swap pilots, narrowing their earlier September2024 global cooperation into region-specific possibilities.",
      guard="The 2026 Europe MoU is a specific signed follow-on framework, not a completed freight corridor, guaranteed truck order or constructed energy-storage site; 2024 global MoU was the prior state, and September18 Kuehne+Nagel deal is a separate partner.",
      impact="A logistics-scale European vehicle/charging sourcing framework may affect battery demand options but no current deployed MW/GWh can be inferred.",
      score=[18,18,0,6,7,4,3,2],acts=["SEP14_CATL_DHL_EUROPE_GREEN_CORRIDOR_SIGNED_MOU","2024_GLOBAL_DHL_MOU_PRIOR_BASELINE","EV_CHARGING_ESS_SWAP_PILOTS_NOT_DEPLOYED"],
      prior="CATL-DHL global cooperation MoU signed September2024; region-specific Sep2026 framework is a new stage with new scope.",
      metric="September14 signed Europe-specific CATL-DHL MoU, corridor/charging/swapping scope",
      denom="No announced new battery order volume or built corridor station count.",
      affected=["DHL Europe road freight","CATL commercial vehicle batteries","Potential ESS charging corridor"],cat="Power",sub="SIGNED_EU_FREIGHT_ELECTRIFICATION_MOU"),

 dict(cid="AU_CANADIAN_SOLAR_ESTORAGE_OX2_MUSWELLBROOK_200MWH_SUPPLY_20261006",
      rows=[1167],rep=1167,date="2026-10-06",region="AU",scope="New South Wales Australia",
      title="Canadian Solar e-STORAGE, OX2 Muswellbrook 100MW·200MWh ESS 공급·시운전 계약",
      owner="Canadian Solar investor relations release",urls=["https://investors.canadiansolar.com/news-releases/news-release-details/e-storage-supply-and-commission-100-mw200-mwh-battery-storage"],
      stage="signed_BESS_supply_commissioning_LTSA_not_delivery",
      fact="Canadian Solar October6 confirms e-STORAGE signed a supply and commissioning agreement for OX2's 100MW/200MWh Muswellbrook Solar Farm and Battery project in NSW Australia, also backed by a 20-year long-term service agreement.",
      guard="Signed hardware/EMS/PCS/LTSA arrangement is not shipments, installation or COD; deliveries expected Q3 2027 and COD targeted Q3 2028. Do not count 20-year LTSA as already earned service fees or added separate battery capacity.",
      impact="A named Australian 200MWh hybrid ESS order with proprietary EMS and long-term servicing advances a real future battery supply pipeline.",
      score=[19,20,0,9,7,4,3,2],acts=["OCT06_OX2_MUSWELLBROOK_100MW_200MWH_SIGNED_SUPPLY","SIGNED_20_YEAR_LTSA_DISTINCT_SERVICE_CHILD","Q3_2027_SHIPMENT_Q3_2028_COD_PLANNED_ONLY"],
      prior="Canadian Solar's earlier Australia and data-center BESS contracts in Full are different sites; OX2 Muswellbrook is a new named project.",
      metric="100MW/200MWh OX2 Muswellbrook signed supply/commissioning 2026-10-06, 20-year LTSA; expected 2027 shipment",
      denom="One 100MW/200MWh battery paired with OX2 solar at Muswellbrook NSW.",
      affected=["e-STORAGE SolBank/EMS deliveries","OX2 Muswellbrook","NSW former coal-mine energy transition"],cat="ESS",sub="SIGNED_SUPPLY_COMMISSIONING_AND_LTSA"),

 dict(cid="US_JUPITER_POWER_CLOSED_1P4BN_TEN_BESS_FOUR_FINANCING_TRANSACTIONS_DISCLOSED_20260916",
      rows=[97],rep=97,date="2026-09-16",region="US",scope="United States Texas and Michigan",
      title="Jupiter Power, 10개 ESS 36GWh 아닌 3.6GWh 프로젝트 금융 14억달러 종결 사실 공개",
      owner="Jupiter Power original company financing release",urls=["https://jupiterpower.io/jupiter-power-secures-1-4-billion-in-project-financing-for-ten-utility-scale-battery-energy-storage-projects/"],
      stage="retrospective_disclosure_four_closed_financings_April_to_July",
      fact="Jupiter Power September16 owner disclosure states four separate financing transactions totaling US$1.4bn for ten Texas/Michigan BESS projects totaling 1,500MW/3,600MWh, with individual financings actually closed between April and July2026, not on September16.",
      guard="Source headline's 3.8GWh is inconsistent with original company 3.6GWh, which controls. Financing closed in earlier months; September16 is disclosure date. The deal total includes secured project debt, tax equity bridge and private placement, not $1.4bn new federal subsidy, not fully disbursed operating cash or 10 new CODs.",
      impact="A first-party disclosure of substantial already-closed multi-project financing reduces funding uncertainty for US grid-scale BESS without establishing newly commissioned GWh.",
      score=[20,21,0,10,7,5,3,2],acts=["SEP16_JUPITER_DISCLOSED_1P4BN_FOUR_FINANCINGS_CLOSED_APR_JUL","TEN_PROJECTS_1500MW_3600MWH_NOT_3800MWH","CLOSED_FINANCE_NOT_10_COD_OR_SUBSIDY"],
      prior="Four closed transactions occurred Apr–Jul2026; first public consolidated company disclosure September16, no exact same ten-project financing in Full.",
      metric="US$1.4bn four financing closings Apr-Jul 2026, 10 BESS totaling 1500MW/3600MWh (not news 3.8GWh)",
      denom="10 Texas/Michigan projects, 1,500MW/3,600MWh original owner figure; 4 separate financings.",
      affected=["Jupiter Power US BESS development","Project-finance lenders and tax equity","US battery capacity financing"],cat="ESS",sub="FIRST_DISCLOSED_PRIOR_FINANCING_CLOSE"),

 dict(cid="EU_EVE_IAA_COMMERCIAL_VEHICLE_30GWH_STRATEGIC_COOP_ORDER_20260919",
      rows=[146],rep=146,date="2026-09-19",region="EU",scope="Germany IAA commercial-vehicle partnerships/global",
      title="EVE Energy, IAA서 상용차 배터리 30GWh 초과 전략협력 계약 발표",
      owner="EVE Energy original manufacturer exhibition announcement",urls=["https://www.evebattery.com/en/news-1900"],
      stage="signed_multiple_strategic_cooperation_agreements_not_guaranteed_deliveries",
      fact="EVE Energy's September29 retrospective owner release identifies on-site IAA transportation agreements by September19 with BMZ, Janus Electric, Morris Commercial, Sunswap, WEG and other participants and states aggregate strategic cooperation orders exceeding 30GWh.",
      guard="Owner calls these strategic cooperation orders and on-site agreements; no counterparty-level firm purchase order quantities, conditions, delivery schedule, revenue or 30GWh new installed capacity verified. Its AI Battery and LMX performance are supplier claims not independent tests.",
      impact="Multiple named commercial-vehicle partners signed strategic frameworks indicating important EV-cell demand options without proven binding volume execution.",
      score=[20,21,0,9,7,5,3,2],acts=["SEP19_IAA_EVE_MULTI_PARTNER_STRATEGIC_COOP_AGREEMENTS","COMPANY_AGGREGATE_ABOVE_30GWH_COOP_ORDERS_UNVERIFIED_FIRM_POs","SEP29_FOLLOWUP_PRESS_RELEASE_DATE_NOT_NEW_ORDER_DATE"],
      prior="Earlier 206GWh EVE-Fluence storage framework is a separate segment and partner; IAA vehicle deal group is not Fluence.",
      metric="EVE original named partners and claimed >30GWh on-site strategic cooperation orders at IAA Sep19, original release Sep29",
      denom="Company-level aggregate >30GWh strategic cooperation orders with multiple partners, firm purchased volume per buyer unknown.",
      affected=["EVE commercial vehicle battery cells","BMZ/Janus Electric/Morris Commercial/Sunswap/WEG cooperation","European truck and bus OEM battery sourcing"],cat="Cell",sub="SIGNED_STRATEGIC_COOP_AGREEMENTS_NOT_FIRM_DELIVERIES"),

 dict(cid="EU_VW_POWERCO_GOTION_THREE_CONDITIONAL_LFP_JVS_AND_5P3_STAKE_20260928",
      rows=[1259],rep=1259,date="2026-09-28",region="EU",scope="Spain Slovakia Morocco LFP supply chain and Germany China equity",
      title="Volkswagen·PowerCo–Gotion, 3개 LFP 합작사업 합의·Gotion 지분 5.3% 매각 계약",
      owner="Volkswagen Group original press release",urls=["https://www.volkswagen-group.com/en/press-releases/volkswagen-group-powerco-and-gotion-deepen-strategic-partnership-20710"],
      stage="signed_proposed_three_JV_framework_and_separate_conditional_equity_sale",
      fact="Volkswagen September28 confirms PowerCo–Gotion agreement to establish three industrial JVs: Valencia Spain LFP cell PowerCo51%, Šurany Slovakia LFP cell Gotion51%, Kenitra Morocco LFP cathode Gotion51%. PowerCo expected EUR470m contribution to two sites and Gotion EUR1.1bn to Valencia through 2030; VW subsidiary separately signed definitive agreements to sell 5.3% Gotion equity.",
      guard="Three JVs are intended under agreements but not confirmed legally formed, closed, transferred or commissioned. EUR470m and EUR1.1bn are agreed prospective contributions, not already spent; 5.3% Gotion equity sale needs approvals and is not completed. Do not treat all sites as inside EU: Kenitra is Morocco. No realized LFP GWh yet.",
      impact="A signed regional multi-country LFP cell and cathode local-sourcing framework with separate conditional equity divestiture could materially reshape PowerCo's European supply chain.",
      score=[23,22,0,10,9,5,3,2],acts=["SEP28_PLANNED_VALENCIA_POWERCO_51PCT_LFP_JV","SEP28_PLANNED_SURANY_GOTION_51PCT_LFP_JV","SEP28_PLANNED_KENITRA_MOROCCO_GOTION_51PCT_CAM_JV","PROSPECTIVE_EUR470M_POWERCO_PLUS_EUR1P1BN_GOTION_CONTRIBUTIONS","SEPARATE_SIGNED_5P3PCT_VW_GOTION_EQUITY_SALE_NOT_CLOSED"],
      prior="VW and Gotion supplied cells under a 2020-era partnership; three regional 2026 JV agreements and stake sale are new, separately conditional economic acts.",
      metric="Three intended JV sites and majority 51% ownership map; proposed EUR470m/EUR1.1bn contributions by 2030; 5.3% VW Gotion share sale agreement",
      denom="Three intended LFP joint ventures at Valencia, Šurany and Kenitra, not three operating plants; two separate contingent investment counterparties.",
      affected=["PowerCo Europe LFP cells","Gotion cell production","Morocco LFP cathode materials","VW investment stake in Gotion"],cat="Materials",sub="CONDITIONAL_THREE_LFP_JV_AND_STAKE_SALE_AGREEMENTS"),

 dict(cid="CN_GEELY_AI_2250KW_SMART_CHARGING_AND_20PCT_RESTORATION_CLAIMS_20260923",
      rows=[498,741,772,784,812,881],rep=772,date="2026-09-23",region="CN",scope="China vehicle charging technology",
      title="Geely, AI 기반 2,250kW 충전 플랫폼 발표…수명 개선 20%는 자체 주장",
      owner="Geely Auto Group official news release",urls=["https://www.geelyautogroup.com/en/media/202609231/","https://newsroom.geely.com/geely-auto-group-ultra-fast-ai-powered-geely-smart-charging"],
      stage="public_product_technology_unveil_no_independent_performance_validation",
      fact="Geely September23 officially unveiled fifth-generation Smart Charging station capable of company-claimed up to 2,250kW peak, Xingrui PowerMind AI battery temperature management and new Ultra Short Blade Battery; Geely claims fast charging 10-70% in 4m30s and 20% cycle-life improvement from pulse restoration technology.",
      guard="Unveiling a technology is an actual announcement, not certification, proven nationwide deployment or independent performance test. Peak 2,250kW, 20% life extension, 12C charging and 4m30s claims are Geely self-reported; no third-party cycle test protocol, product mass-production volume or field deployment is demonstrated.",
      impact="A meaningful high-power charging product claim/architecture shifts competitive technology questions despite limited independent validation.",
      score=[19,18,4,8,7,4,3,2],acts=["SEP23_GEELY_PUBLIC_AI_SMART_CHARGING_PLATFORM_AND_2250KW_PEAK_CLAIM","GEELY_PULSE_RESTORATION_20PCT_CYCLE_LIFE_COMPANY_CLAIM_NOT_VALIDATED","ULTRA_SHORT_BLADE_6C_AND_10_TO70PCT_4M30S_SELF_REPORTED_TEST_NOT_CERTIFIED"],
      prior="Earlier Geely 1500kW charger in Full R8_02 March23 is a previous product generation; this September23 2250kW/AI/pulse-restoration announcement adds new capabilities but remains company performance claim.",
      metric="September23 2026 official Geely 2250kW peak station, 20% pulse restoration cycle-life claim, 4m30s 10-70% charging and 6C blade product",
      denom="Single manufacturer-declared station technology; installation count, independent battery-cycle sample size and certified use-case energy not disclosed.",
      affected=["Geely EV battery charging ecosystem","Charging-station storage/power hardware","Battery pulse-restoration cycle-life technology"],cat="Technology",sub="UNVALIDATED_SUPPLIER_CHARGER_LIFE_CLAIMS",tech_stage="concept_or_target",tech_level="company_target_or_unsupported_claim"),
]

# One already-covered company original has no new event beyond locked Full1676.
FULL_REINFORCEMENTS=[
  {"row":1184,"full_id":"2026-09-06_CN_03","event_id":"CN_CATL_COPPER_FOIL_PARTNERSHIP_SEP06_ALREADY_IN_FULL",
   "owner_url":"https://www.catl.com/en/news/6993.html",
   "reason":"Original CATL Sep06 strategic agreements with Taijin and Shenzhen Huike involve copper foil equipment procurement, 400kt planned capacity, cost-plus price model and shared R&D, all already covered by locked Full 2026-09-06_CN_03. Weekly row1184 is an explanatory repeat of same September6 economic act; no new signed implementation, commissioning, paid CAPEX or purchase guarantee evidenced."}
]

GEO_EVENT_ROLE={
    498:["GEELY_PULSE_RESTORATION_20PCT_CYCLE_LIFE_COMPANY_CLAIM_NOT_VALIDATED"],
    881:["GEELY_PULSE_RESTORATION_20PCT_CYCLE_LIFE_COMPANY_CLAIM_NOT_VALIDATED"],
    741:["SEP23_GEELY_PUBLIC_AI_SMART_CHARGING_PLATFORM_AND_2250KW_PEAK_CLAIM"],
    812:["SEP23_GEELY_PUBLIC_AI_SMART_CHARGING_PLATFORM_AND_2250KW_PEAK_CLAIM"],
    772:["SEP23_GEELY_PUBLIC_AI_SMART_CHARGING_PLATFORM_AND_2250KW_PEAK_CLAIM"],
    784:["SEP23_GEELY_PUBLIC_AI_SMART_CHARGING_PLATFORM_AND_2250KW_PEAK_CLAIM"],
}
NIO_ROLE={
    869:["SIGNED_GEELY_IN_KIND_YIYI_PLUS_RMB640M_FOR_INITIAL_30PCT_NIO_POWER_CONDITIONAL"],
    1082:["GEELY_SWAP_COMPATIBLE_FUTURE_VEHICLES_PRELIMINARY_ONLY"],
    870:["SIGNED_GEELY_IN_KIND_YIYI_PLUS_RMB640M_FOR_INITIAL_30PCT_NIO_POWER_CONDITIONAL",
         "SIGNED_NIO_CHINA_10PCT_HAOHAN_EQUITY_SWAP_CONDITIONAL"],
}

def make_event(f:dict)->dict:
    # CP19's factory accepts a small region enum; the original owner region is
    # then overwritten with the actual jurisdiction for this worldwide batch.
    e=case(cid=f["cid"],rows=f["rows"],rep=f["rep"],date=f["date"],
        title=f["title"],owner=f["owner"],urls=f["urls"],region="EU" if f["region"] in ("EU","FI") else "US",
        stage=f["stage"],fact=f["fact"],guard=f["guard"],impact=f["impact"],
        score=f["score"],
        evidence=[
            f'{f["owner"]} original {f["date"]} company release official document: verify {f["metric"]}. Official document to verify original announcement date {f["date"]} and stated status.',
            f'{f["owner"]} original executed agreement or project commissioning document: verify final actual closing date, delivery volume, or cash-funding milestone for {f["metric"]}. Official document to verify original announcement date {f["date"]} and stated status.',
        ],
        confirm=[
            f'Company official contract filing or dated completion decision reporting actual {f["metric"]} would strengthen the {f["cat"]} execution outlook; confirmed cancellation would weaken the {f["cat"]} execution outlook.',
            f'Independent owner operation report with verified delivery volume, cash paid and milestone date for {f["metric"]} would strengthen project-realization outlook; missed project schedule would weaken that outlook.',
        ],
        actions=f["acts"],prior=f["prior"],denominator=f["denom"],affected=f["affected"],
        category=f["cat"],subtype=f["sub"],
        related=f.get("related",()),
        mechanism=f["fact"],budget="No cash outlay or physical installation established beyond the explicitly stated completed stage.",
        tech_stage=f.get("tech_stage"))
    e["region"]=f["region"]
    e["geographic_scope"]=f["scope"]
    if f.get("tech_level"):
        e["technology_level"]=f["tech_level"]
        e["tech_gap"]="Supplier claims await independent full-load 2,250kW field performance and 20% battery cycle-life test protocol; no certified broad deployment proven."
    return e

def main()->None:
    p=argparse.ArgumentParser()
    for k in ("base","full","output","receipt"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    assert sha256(a.base)==BASE_SHA and sha256(a.full)==FULL_SHA
    d,full=read(a.base),read(a.full)
    assert len(full["cards"])==1676 and len(d["decision_ledger"])==1330
    assert len(d["promotion_reassessment_ledger"])==126 and len(d["strict_passed_spec"])==30
    assert {k:len(d[k]) for k in ("candidate_review_pool","watchlist_context_pool","reject_or_support_only_pool","existing_reinforcement")}=={
        "candidate_review_pool":563,"watchlist_context_pool":660,"reject_or_support_only_pool":47,"existing_reinforcement":30}
    events=[make_event(f) for f in FACTS]
    targets={i for e in events for i in e["rows"]}|{x["row"] for x in FULL_REINFORCEMENTS}
    assert len(events)==12 and len(targets)==27
    assert targets=={97,146,165,337,338,342,343,367,497,498,683,728,741,772,784,812,865,869,870,881,1068,1082,1156,1167,1184,1259,1263}
    old={r["source_row_index"]:r for r in d["decision_ledger"]}
    previous={r["candidate_id"] for r in d["promotion_reassessment_ledger"]}
    assert not ({old[i]["story_id"] for i in targets}&previous)
    for i in targets:
        assert old[i]["stage_a_pool"] in ("candidate_review_pool","watchlist_context_pool"),(i,old[i]["stage_a_pool"])
    ledger={r["story_id"]:r for r in d["decision_ledger"]}
    review={r["story_id"]:r for r in d["review_pool_resolution_ledger"]}
    template=d["strict_passed_spec"][-1]
    new_strict,new_support,new_reinforcement=set(),set(),set()
    edges=[]

    def formal(idx:int,eid:str,status:str,pool:str,reason:str,owners:list[str])->None:
        r=old[idx]
        d["promotion_reassessment_ledger"].append({
            "candidate_id":r["story_id"],"economic_event_cluster_id":eid,
            "before_pool":r["stage_a_pool"],"after_pool":pool,
            "promotion_reassessment_status":status,"resolved":reason,
            "remaining":"Stage B owner documents required; no canonical card or publication authorized.",
            "source_candidates":owners,"source_observation_preserved":True,
        })

    def tag(idx:int,eid:str,units:list[str],action:str,owners:list[str])->None:
        r=old[idx]
        sid=r["story_id"]
        sub=[{"event":u,"role":"stage_specific_separate_economic_act_preserved"} for u in units]
        ledger[sid]["formal_0_1P_cp20_source_to_economic_act_edges_20261101"]=sub
        ledger[sid]["cp20_source_identity_preserved"]={
            "story_id":sid,"source_row_index":idx,"headline_raw":r["headline_raw"],"primary_url":r["primary_url"]}
        edges.append({"row":idx,"source_id":sid,"result":action,
                      "economic_event_cluster_id":eid,"original_source_url":r["primary_url"],
                      "first_party_owner_urls":owners,"economic_act_edges":sub})

    def update_review(idx:int,to:str,why:str,next_action:str,carry:str,disposition:str)->None:
        r=old[idx]
        r0=review[r["story_id"]]
        r0.update({"original_review_pool_partition":r["stage_a_pool"],
            "current_disposition":to,"disposition_basis":why,"next_action_condition":next_action,
            "final_review_pool_disposition":disposition,"carry_forward_policy":carry,
            "reviewed_by_stage_or_pass":"PROMPT_0_1P_V4_20260829 owner primary CP20",
            "review_artifact_id":"STAGE_A_CHECKPOINT_20_FORMAL_20261101"})

    for e in events:
        source_rows=[old[i] for i in e["rows"]]
        idx=e["representative"]
        rep=old[idx]
        spec=execution_strict(rep,template,e,source_rows)
        points=sum(e["score"])
        spec.update({
            "decision_value_classification":"high_decision_value" if points>=70 else "material_industry_signal",
            "headline":e["title"],"title_raw":e["title"],
            "representative_date":e["date"],"publication_date":e["date"],
            "date_role":{**spec["date_role"],"event_date":e["date"],"announcement_date":e["date"],
                "representative_date_basis":"Owner original first economic-action date, distinguished from later disclosure and commissioning."},
            "assessment_method":"PROMPT_0_1P_V4_20260829 owner primary document and Full1676 identity audit CP20",
            "evidence_needed_for_stage_b":e["evidence"],
            "next_confirmation_points":e["confirm"],
            "formal_0_1P_cp20_strict_event_20261101":{
                "case_id":e["case_id"],"representative_source_row":idx,
                "source_row_indices":e["rows"],"owner_urls":e["owner_urls"],
                "economic_subacts":e["event_units"],"independently_cardable_stage":True,
                "no_extra_card_for_support":True,"stage_b_fact_adoption":False,
                "canonical_card_write":False,
            },
        })
        if "FI_SUNGROW" in e["case_id"] or "FI_AKKU_ONE" in e["case_id"]:
            spec["within_batch_related_economic_event_families"]= [
                "FI_SUNGROW_DELTA_600MWH_FRAMEWORK_EXECUTION_TWO_PROJECTS_20260924",
                "FI_AKKU_ONE_COVENERGO_DELTA_125MW_300MWH_CONSTRUCTION_START_20260917"]
            spec["no_double_count_finland_300mwh"]="AKKU One 300MWh is a subset of 600MWh combined supply in two-site contract; construction and supply are distinct milestone actions, not additive contracted GWh."
        if idx==97:
            spec["source_headline_metric_correction"]={"unreliable_media_gwh":3.8,
               "original_company_gwh":3.6,"original_company_mwh":3600,
               "disclosure_date":"2026-09-16","actual_financing_close_window":"2026-04..2026-07"}
        if "GEELY_AI" in e["case_id"]:
            spec["supplier_performance_claim_guard"]={"performance_cited_not_independent":True,
                "2250kw_peak_company_claim":True,"20pct_life_gain_unverified":True,
                "mass_deployment_not_proven":True}
        assert spec["stage_b_authorized"] is False and spec["canonical_card_write_allowed"] is False
        d["strict_passed_spec"].append(spec)
        ledger[rep["story_id"]].update(copy.deepcopy(spec))
        tag(idx,e["case_id"],e["event_units"],"FORMAL_STRICT_EVENT_SELECTOR_ONLY",e["owner_urls"])
        new_strict.add(rep["story_id"])
        formal(idx,e["case_id"],"PROMOTED_VALIDATED_STRICT","strict_passed_spec",e["new_fact"],e["owner_urls"])
        for i in e["rows"]:
            if i==idx:continue
            r=old[i]
            sup=support_row(r,e,rep["story_id"])
            sup["new_verified_fact"]="Source supports same economic event, not second new award or financing: "+e["new_fact"]
            sup["source_headline_vs_owner_status_guard"]=e["must_not"]
            ledger[r["story_id"]].update(copy.deepcopy(sup))
            d["reject_or_support_only_pool"].append(sup)
            units=(GEO_EVENT_ROLE.get(i) or NIO_ROLE.get(i) or [e["event_units"][0]])
            tag(i,e["case_id"],units,"FORMAL_SUPPORT_ONLY_SAME_EVENT_NO_SECOND_CARD",e["owner_urls"])
            new_support.add(r["story_id"])
            update_review(i,"reject_or_support_only_pool",sup["final_reason"],
                "A separately dated signed contract or actual operation milestone would reopen.",
                "support_source_only","support_source_only_after_review")
            formal(i,e["case_id"],"FORMAL_SAME_EVENT_SUPPORT_ONLY","reject_or_support_only_pool",sup["final_reason"],e["owner_urls"])

    full_by_id={r["id"]:r for r in full["cards"]}
    for e in FULL_REINFORCEMENTS:
        idx=e["row"]
        o=old[idx]
        full_row=full_by_id[e["full_id"]]
        assert "동박" in full_row["title"] and "cost-plus" in full_row["fact"]
        r=copy.deepcopy(o)
        r.update({
            "stage_a_pool":"existing_reinforcement","ledger_decision":"existing_reinforcement",
            "editorial_bucket":"existing_reinforcement","assessment_status":"FORMAL_0_1P_EXISTING_FULL_REINFORCEMENT",
            "assessment_method":"PROMPT_0_1P_V4_20260829 original CATL text and locked Full body same-event comparison",
            "promotion_reassessment_status":"FORMAL_EXISTING_FULL_NO_NEW_CARD",
            "review_pool_partition":None,"review_pool_resolution_status":None,
            "review_pool_subtype":None,"review_reason":"","needs_review":False,
            "reinforcement_type":"exact_same_signed_strategic_copper_foil_cooperation",
            "reason_not_new_card":e["reason"],"baseline_match":e["full_id"],
            "baseline_relation":"same_event_duplicate_in_full",
            "baseline_follow_up_relation":"same_event_duplicate_in_full",
            "follow_up_relation":"same_event_duplicate_in_full","duplicate_risk":"same_event_confirmed",
            "novelty_cap_basis":"repeated_announcement_no_new_fact",
            "decision_news_value_score":26,"decision_value_classification":"context_or_reinforcement",
            "independent_cardability_gate":{"status":"FAIL","reason":e["reason"],
                "full_schema_viability":"FAIL","distinct_event_or_stage_progression":False,
                "duplicate_or_reinforcement_note":e["reason"]},
            "new_verified_fact":e["reason"],"remaining_uncertainty":"Actual future capacity buildout is not proven by this repeated partnership announcement.",
            "economic_event_cluster_id":e["event_id"],"canonical_card_write_allowed":False,
            "accepted_facts_approved":False,"stage_b_authorized":False,
            "formal_0_1P_cp20_existing_full_20261101":{
                "owner_original":e["owner_url"],"matched_full_id":e["full_id"],
                "matched_full_title":full_row["title"],"same_event_not_new_card":True,
                "source_observation_retained":True},
        })
        ledger[o["story_id"]].update(copy.deepcopy(r))
        d["existing_reinforcement"].append(r)
        new_reinforcement.add(o["story_id"])
        tag(idx,e["event_id"],["SEP06_ALREADY_REPRESENTED_CATL_COPPER_FOIL_AGREEMENT"],
            "FORMAL_REINFORCEMENT_LOCKED_FULL_NO_NEW_CARD",[e["owner_url"]])
        formal(idx,e["event_id"],"FORMAL_EXISTING_FULL_NO_NEW_CARD","existing_reinforcement",e["reason"],[e["owner_url"]])

    closed=new_strict|new_support|new_reinforcement
    assert len(closed)==len(targets)==27
    assert (len(new_strict),len(new_support),len(new_reinforcement))==(12,14,1)
    for k in ("candidate_review_pool","watchlist_context_pool"):
        d[k]=[r for r in d[k] if r["story_id"] not in closed]
    d["review_pool_resolution_ledger"]=[r for r in d["review_pool_resolution_ledger"]
            if r["story_id"] not in (new_strict|new_reinforcement)]
    expected={"strict_passed_spec":42,"candidate_review_pool":538,"watchlist_context_pool":658,
              "reject_or_support_only_pool":61,"existing_reinforcement":31,
              "review_pool_resolution_ledger":1257,"promotion_reassessment_ledger":153}
    assert all(len(d[k])==n for k,n in expected.items()),{k:len(d[k]) for k in expected}
    assert sum(len(d[k]) for k in ("strict_passed_spec","candidate_review_pool",
           "watchlist_context_pool","reject_or_support_only_pool","existing_reinforcement"))==1330
    assert len({r["story_id"] for r in d["decision_ledger"]})==1330
    assert len({r["candidate_id"] for r in d["promotion_reassessment_ledger"]})==153
    s=d["summary"]
    s.update({"strict_passed_spec_count":42,"existing_reinforcement_count":31,
              "duplicate_or_reinforcement_count":31,"needs_review_count":1257,
              "processed_priority_source_observations":153,
              "processed_priority_economic_clusters":s["processed_priority_economic_clusters"]+12,
              "unprocessed_editorial_observations":1177})
    s["pool_counts"]={k:len(d[k]) for k in ("strict_passed_spec","candidate_review_pool",
         "watchlist_context_pool","reject_or_support_only_pool","existing_reinforcement","rejected","support_source_only")}
    d["review_pool_partition_summary"]={k:len(d[k]) for k in ("candidate_review_pool",
        "watchlist_context_pool","reject_or_support_only_pool")}
    coverage_maps(d)
    sys.path.insert(0,str(a.full.resolve().parent.parent))
    from validation_scripts.stage_a_full_v3_completeness_review4943656188 import _expected_summary_id_arrays
    for k,v in _expected_summary_id_arrays(d).items():
        if k in s:s[k]=v
    att=d["pre_native_0_1P_attachment_manifest_20261101"]
    previous=att["formal_review_completed_source_ids"]
    now=[e["source_id"] for e in sorted(edges,key=lambda x:x["row"])]
    assert len(previous)==81 and len(set(previous))==81 and len(now)==27 and not (set(previous)&set(now))
    att.update({"new_formal_decisions":108,"new_strict_promotions":34,
                "formal_review_completed_after_attachment_count":108,
                "formal_review_completed_source_ids":previous+now,
                "remaining_formal_source_count":1177,
                "native_validator_scope_warning":"Native contracts validate decided items, not 1177 pending Stage A Source IDs; global Stage A HOLD."})
    d["formal_0_1P_cp20_first_party_event_act_batch_20261101"]={
        "authority":"PROMPT_0_1P_V4_20260829","cp19_baseline_sha256":BASE_SHA,
        "source_ids_preserved_total":1330,"new_formal_source_ids":27,
        "new_independent_event_representatives":12,"new_same_event_support":14,
        "new_existing_full_reinforcement":1,"formal_total":153,"pending_total":1177,
        "strict_total":42,"source_to_economic_act_edges":sorted(edges,key=lambda x:x["row"]),
        "case_index":{e["case_id"]:{"representative_row":e["representative"],
                 "source_rows":e["rows"],"owner_urls":e["owner_urls"],
                 "economic_subacts":e["event_units"],"stage_guard":e["must_not"]} for e in events},
        "finland_300mwh_not_double_counted":True,
        "jupiter_original_3600mwh_replaces_3800mwh_media":True,
        "vw_three_jvs_and_separate_stake_sale_conditional":True,
        "geely_supplier_20pct_claim_not_independently_validated":True,
        "stage_b_executed":False,"new_published_cards":0,
        "canonical_main_full_related_mutations":0,
        "global_stage_a_status":"HOLD_OPEN_1177_UNADJUDICATED"}
    d["recommended_for"]=["Finish 1177 pending formal Source ID decisions by event family; Stage A global HOLD; no Stage B or canonical card write."]
    d["next_call_recommendation"].update({
        "pending_parallel_or_followup_call":"review_pool/treasure triage",
        "pending_input_universe":"candidate_review_pool[] + eligible treasure/review-only universe",
        "reason":"Native strict selectors pass within decided rows; 1177 raw Source IDs await formal disposition.",
        "blocked_items_summary":d["review_pool_partition_summary"]})
    temp_output=a.output.with_name(a.output.name+".building")
    write(temp_output,d)
    completed_readback=read(temp_output)
    assert len(completed_readback["decision_ledger"])==1330
    assert len(completed_readback["strict_passed_spec"])==42
    temp_output.replace(a.output)
    receipt={"status":"PENDING_NATIVE_AND_INDEPENDENT_QC",
       "artifact_type":"STAGE_A_CP20_FIRST_PARTY_27_ID_BATCH",
       "base_cp19_sha256":BASE_SHA,"locked_full_sha256":FULL_SHA,
       "output_sha256":sha256(a.output),"new_formal":27,
       "new_strict":12,"new_support":14,"new_existing_full_reinforcement":1,
       "cumulative_formal":153,"remaining":1177,"cumulative_strict":42,
       "source_decisions":sorted(edges,key=lambda x:x["row"]),
       "no_stage_b":True,"global_status":"HOLD","no_main_full_related_mutation":True}
    write(a.receipt,receipt)
    print(json.dumps({k:receipt[k] for k in ("output_sha256","new_formal","new_strict",
        "new_support","new_existing_full_reinforcement","cumulative_formal","remaining","cumulative_strict")},indent=2))

if __name__=="__main__":
    main()


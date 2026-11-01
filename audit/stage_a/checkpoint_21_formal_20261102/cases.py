"""Manually adjudicated CP21 cases; automated retrieval never makes decisions."""
from pathlib import Path
import sys, importlib.util
ROOT=Path(__file__).resolve().parents[1]/'native'
for p in (ROOT/'audit/stage_a').iterdir():
 if p.is_dir():sys.path.insert(0,str(p))
spec=importlib.util.spec_from_file_location('cp19',ROOT/'audit/stage_a/checkpoint_19_formal_20261101/build_cp19.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def event(cid,rows,rep,date,title,owner,url,region,fact,guard,impact,score,actions,prior,denom,related=()):
 e=m.case(cid=cid,rows=rows,rep=rep,date=date,title=title,owner=owner,urls=[url],region='US',stage='owner_confirmed_economic_act',fact=fact,guard=guard,impact=impact,score=score,evidence=['Original dated owner release and instrument/production records.', 'Verify amount, conditions, date and prior coverage before any Stage B adoption.'],confirm=['Subsequent realized production, utilization, signed implementation or drawdown, independently dated.'],actions=actions,prior=prior,denominator=denom,affected=['Battery and energy storage supply chain'],category='ESS',subtype=cid,related=related)
 e['region']=region;e['geographic_scope']={'HU':'Hungary / Europe','CN':'China','US':'United States','KR':'Korea / United States','CA':'Canada'}[region]
 return e
EVENTS=[
 event('HU_CATL_DEBRECEN_TWO_CELL_LINES_TRIAL_20260922',[1278,758,791,814,1149],1278,'2026-09-22','CATL, 데브레첸 셀 공장 첫 2개 라인 시험가동','CATL','https://www.catl.com/en/news/7000.html','HU',
 'CATL reports trial operation of the first two cell lines on September 22 after permit preconditions; module production has run since autumn 2024.',
 'Trial setup and validation are not series production. Planned final 100GWh is not commissioned capacity or output; 537,000 modules are historical module output, not new cells. Environmental compliance is CATL attribution, not independent certification.',
 'A new local cell-manufacturing stage changes European supply-chain readiness separately from module assembly and earlier permitting.',[20,20,0,8,4,2,3,2],
 ['TWO_CELL_LINES_TRIAL_SEP22_NOT_SERIES','AUGUST_OCCUPANCY_PERMIT_PRIOR_STAGE','MODULE_PRODUCTION_SINCE_2024_NOT_NEW_CELL_OUTPUT'],
 'Full contains Hungarian environmental oversight but no same Debrecen September22 cell-trial act; all Full1676 and prior Strict42 searched.', 'Two lines; final site plan 100GWh, no realized cell GWh or market denominator.', ['2026-07-06_KR_05']),
 event('US_FORM_ENERGY_270M_CREDIT_CLOSE_20260921',[1290],1290,'2026-09-21','Form Energy, 2.7억달러 신용약정 종결 발표','Form Energy via GlobeNewswire','https://www.globenewswire.com/news-release/2026/09/21/3365616/0/en/form-energy-announces-closing-of-270m-credit-facility.html','US',
 'Form Energy announces closing of a $270m revolving and 45X tax-credit advance facility for manufacturing scale-up and working capital.',
 'A closed facility is not $270m fully drawn or a government grant. Accordion up to $1bn is conditional future credit, not current funded debt. August $750m Series G is separate prior equity. 100-hour duration is product design, not realized fleet delivery.',
 'Manufacturing liquidity and tax-credit monetization change scale-up funding independently of the historical Crusoe supply agreement.',[20,20,0,10,3,2,3,2],
 ['270M_REVOLVER_PLUS_TAX_CREDIT_ADVANCE_FACILITY_CLOSED','UP_TO_1BN_ACCORDION_NOT_DRAWN','AUGUST_750M_EQUITY_PRIOR_DISTINCT_NOT_NEW_SEP21_EQUITY'],
 'Full has Form-Crusoe supply and LDES context; no same September21 credit facility.', '$270m current facility; up to $1bn accordion; no debt utilization denominator.', ['R9_01']),
 event('CN_PYLONTECH_588_601AH_MASS_PRODUCTION_20260921',[1287],1287,'2026-09-21','Pylontech, 588Ah·601Ah ESS 셀 양산 개시 발표','Pylontech via PRNewswire','https://www.prnewswire.com/news-releases/pylontech-starts-mass-production-of-588ah-and-601ah-lfp-cells-for-ess-302886245.html','CN',
 'September22 release states mass production started September21 at Hefei for 588Ah and 601Ah LFP cells, with over 100MWh already produced according to Pylontech.',
 'Production-stage company report is distinct from independent performance validation. 12,000 cycles, 96.5% efficiency and 425.8Wh/L remain supplier claims. PyOcean6.25/8MWh integration is not completed project delivery. Prior Yangzhou/Ningxia project capacities are not new September production.',
 'Moves previously launched large-cell system architecture into reported cell manufacturing, a distinct execution stage.',[18,22,4,6,0,2,3,2],
 ['HEFEI_588AH_601AH_CELL_MASS_PRODUCTION_SEP21','OVER_100MWH_OUTPUT_COMPANY_REPORTED','PYOCEAN_PROJECT_DELIVERY_FUTURE'],
 'Full June11 8MWh system launch is related product development; not the September21 cell production milestone.', 'Over100MWh company output; annual capacity and yield not established.', ['2026-06-11_EU_07']),
 event('KR_US_LGES_B2U_PRIORITY_BATTERY_REPURPOSING_20260922',[581,1126],581,'2026-09-22','LG에너지솔루션·B2U, 재사용 ESS 우선 배터리 공급 협력','LG Energy Solution','https://news.lgensol.com/company-news/press-releases/5260','KR',
 'LGES September22 dateline announces strategic agreement giving B2U priority access to battery capacity and exploring U.S. grid-scale repurposed-battery storage.',
 'Newsroom page is dated September24 but release dateline is September22. Priority access is not quantified binding purchase, installed GWh, revenue or new recycling plant. GWh ambition is unquantified future scope.',
 'Supplier access and second-life commercialization rights change separately from B2U prior Texas operation and Waymo battery supply.',[22,20,0,7,0,2,3,2],
 ['PRIORITY_BATTERY_ACCESS_STRATEGIC_AGREEMENT','REPURPOSING_BEFORE_RECYCLING_FUTURE_US_BESS','SEPT24_PAGE_DATE_NOT_AGREEMENT_DATE'],
 'Full September9 Texas28MWh operating project and June4 Waymo collaboration concern different counterparties/actions.', 'No committed supply volume, contract value or realized GWh.', ['2026-09-09_US_01','2026-06-04_US_01']),
 event('CA_MARATHON_CONDITIONAL_11M_LOAN_20260918',[91],91,'2026-09-18','Invest Ontario, Marathon 처리시설 최대 1,100만 캐나다달러 조건부 융자 지원','Invest Ontario','https://www.investontario.ca/press-release/invest-ontario-supports-construction-generation-minings-marathon-copper-palladium-processing-facility','CA',
 'Invest Ontario announces up to C$11m conditional CMPF loan support for Generation Mining Marathon copper-palladium processing facility.',
 'Conditional support is not loan disbursement, financial close, construction completion or mineral production. C$410m processing facility is part of C$992m total project, not additive investments. Job and production estimates are forward-looking.',
 'Specific project financing support changes a construction-ready critical-mineral asset funding path without implying mine operation.',[18,18,0,9,8,2,3,2],
 ['UP_TO_CAD11M_CONDITIONAL_PROCESSING_LOAN','CAD410M_PROCESSING_SUBSET_OF_CAD992M_PROJECT','PERMITTED_CONSTRUCTION_READY_NOT_OPERATING'],
 'No same Marathon funding act found in Full1676 or prior formal153.', 'C$11m conditional support / C$410m processing component / C$992m whole project; all C$.')
]
# Every topic retains a separate source/document identity and its historical metrics.
WEBINARS=[
 ([74,458],'2026-09-19','container_scale','1,000–1,300kWh/container teaching example; not new delivered capacity.'),
 ([75,459],'2026-09-19','land_connection','March2026 reported queue 191m kW, contract applications35m kW, connected0.84m kW: different stages, not summed; government source not verified.'),
 ([76,460],'2026-09-18','fire_safety','Historical Arizona2019 and other fire examples; not new September2026 incidents or new safety certification.'),
 ([77,461],'2026-09-18','c_rate','C-rate/power/energy examples; auction figures and historical plants remain context; do not convert power into newly installed energy.'),
 ([326],'2026-09-22','cashflow','Historical model assumptions include 5,000yen/kW/year O&M and 1% yearly degradation; not guaranteed realized returns.'),
 ([327],'2026-09-22','irr','6.8万円/kWh is a 2024 cost illustration; negative base-case IRR range is model dependent and omits some revenue streams.'),
 ([641,1030],'2026-09-25','capex','2024 cost5.4+1.4=6.8万円/kWh; not a new current quotation or new subsidy decision.'),
 ([646,1031],'2026-09-25','vpp','VPP/ERAB explanation and examples; not actual aggregate resource enrollment or dispatch.'),
 ([648],'2026-09-24','solar_colocation','Historical PV generation/curtailment examples; no new commissioned co-located storage.'),
 ([649],'2026-09-24','utilization','2024 balancing-market examples, 60% modeled acceptance; not current realized profitability.'),
 ([1027],'2026-09-27','om_cost','O&M5000yen/kW/year and other historical model assumptions; not owner realized operating costs.'),
 ([1028],'2026-09-26','second_life','2018 HEV143万 = 1.43 million vehicles, not current battery recovery; 2021 Chitose example is historical.')
]
WATCHES=[]
def watch(rows,date,cid,why,future,actions,urls=None):
 WATCHES.append(dict(rows=rows,date=date,case_id=cid,why=why,future=future,event_units=actions,owner_urls=urls))
for rows,date,topic,metrics in WEBINARS:
 watch(rows,date,'JP_JAPAN_BRANDING_WEBINAR_'+topic.upper(),
 'Publisher Japan Branding announces a planned free online educational webinar. Topic: '+topic+'. '+metrics+' Educational summary is retained; no new decision-changing industrial deployment, contract or legal act established. Organizer biography mentioning Mongolia70MW/400MWh is a separate unverified plan, not silently merged into this webinar.',
 'Reopen for a newly dated primary industry dataset, actual project contract/deployment, or verified rule change; seminar attendance alone is not industrial execution.', ['WEBINAR_ANNOUNCEMENT_'+topic.upper(),'HISTORICAL_DATA_CONTEXT_NOT_NEW_ECONOMIC_ACT'])
watch([730,1070],'2026-09-25','NL_PAPENDAL_ENECO_315KW_OPERATION',
 'Eneco confirms Papendal iwell315kW battery in operation; energy/flexibility-market availability offsets leasing for first three years. Preserve the operating milestone and lease-access model. One-site case has no realized savings, dispatch, duration or generalizable adoption evidence; WATCH, not discarded.',
 'Verify realized dispatch/net lease economics, MWh and independent replication before reassessing wider industrial significance.',
 ['315KW_BATTERY_OPERATION_CONFIRMED','THREE_YEAR_LEASE_COST_OFFSET_FOR_MARKET_ACCESS','59_CHARGERS_PRIOR_YEAR_STAGE_NOT_NEW_BATTERY_MWH'])
watch([647,1032],'2026-09-25','JP_WATT_TUNE_REVENUE_SHARE_TARIFF',
 'Owner release publishes aggregation fee8% of contract-defined revenue plus300,000yen/year before tax across nine areas excluding Okinawa. Commercial price signal retained. 21x49.9kW/100kWh is illustrative aggregation, not enrolled capacity or approved market entry.',
 'Executed owner contracts, qualification, actual area-specific dispatch and net realized margins; retain price terms for competitor comparison.',
 ['PUBLIC_SERVICE_TARIFF_8PCT_PLUS_300K_YEN','AREA_SPECIFIC_AGGREGATION_DESIGN_NOT_MARKET_ADMISSION'])
watch([651],'2026-09-24','JP_NATURE_TESLA_SMART_CHARGE_SERVICE',
 'Nature launches RemoE/E2 Tesla surplus-solar control subscription300yen/month with first month free. This is paid software service availability, not new cell production or verified nationwide adoption. Tesla charging does not provide V2H; one Tesla only; beta savings are anecdotal.',
 'Measured adoption, independent savings distribution or wider OEM deployment.', ['SMART_CHARGING_SUBSCRIPTION_AVAILABLE','BATTERY_EV_PRIORITY_CONTROL_NOT_V2H'])
watch([1127],'2026-09-24','JP_OBIHIRO_NISSAN_MOBISAVI_WARRANTY_ANNOUNCED',
 'Dealer and MobiSavi announce EV LIFE+ starting October1, combined manufacturer/dealer capacity cover to earlier of11years/160,000km. Preserve residual-value and risk-transfer signal. This is regional dealer warranty design, not Nissan-wide warranty or verified cell longevity.',
 'Executed warranty terms, threshold, claims/reserve economics and measured adoption.', ['SEP24_ANNOUNCEMENT_OCT1_SERVICE_START','DEALER_EXTENSION_NOT_OEM_CELL_LIFE_VALIDATION'])
watch([1325],'2026-10-16','JP_FANTASISTA_NAGAHAMA_CONSTRUCTION',
 'Fantasista release confirms October16 groundworks start at Nagahama through fb3/NC MAX WORLD after October14 construction announcement. Local second-site stage preserved; no capacity or financial scale in this release supports broader industrial materiality.',
 'Original specifications, capex/offtake/market admission and commissioning records; March2027 completion and April2027 operation are future plans.', ['OCT16_CONSTRUCTION_START','OCT14_ANNOUNCEMENT_PRIOR_STAGE','APRIL2027_OPERATION_FUTURE'])
watch([1165],'2026-10-13','JP_MARUBENI_SUNVILLAGE_FOUR_MARKET_ENTRY',
 'Owner release reports four SunVillage sites completed balancing-market entry during September2026 following October2025 announcement; Marubeni supplies aggregation. Preserve actual market-access stage.179MW is operator total order book, not these four-site capacity.',
 'Verify individual admission dates, outputs and realized revenue; confirm site denominator before materiality reassessment.', ['FOUR_SITES_MARKET_ENTRY_SEPTEMBER','OCT13_RETROSPECTIVE_ANNOUNCEMENT','179MW_OPERATOR_ORDERBOOK_NOT_FOUR_SITE_TOTAL'])
watch([253,617],'2026-09-22','CA_NEXTSTAR_STORAGE_MILESTONE_AWARD',
 'NextStar received September22 Energy Storage Canada award following Windsor opening. PageSeptember23 is later than ceremony. Award alone adds no new production stage; C$5bn invested/1300staff and target2500 retained as company context, not a new factory commissioning or ESS shipment.',
 'A separately dated production/customer/shipments milestone; do not promote the award based on factory-scale background.', ['SEP22_AWARD','WINDSOR_OPENING_PRIOR_STAGE','EMPLOYMENT_TARGET_NOT_ACTUAL_ADDITIONAL_OUTPUT'])
SUPPORT_EXISTING=[dict(rows=[769,1139,778,1138],rep=772,case_id='CN_GEELY_AI_SMART_CHARGING_20260923',date='2026-09-23',owner_urls=['https://www.geelyautogroup.com/en/media/202609231/'],prior_state='CP20 row772 selected September23 Geely announcement.',new_fact='The same September23 Geely AI charging/PowerMind product announcement, explained by September24 commentary.',must_not='2,250kW and20% lifetime gain remain company claims. 2027 network targets are future, not completed rollout. Preserve battery/robot subclaims for separate review; no new contract or measured deployment in these commentaries.',event_units=['SEP23_AI_CHARGING_ANNOUNCEMENT','POWERMIND_TEMPERATURE_CONTROL_COMPANY_CLAIM','FUTURE_NETWORK_TARGET_NOT_EXECUTION'])]
# Robot/product-specific material remains pending rather than over-merged.

#!/usr/bin/env python3
"""R29 governed review candidate: September EV demand/exports cross-definition.
Temporary branch bootstrap. Self-deletes before publication PR; no main write.
Three independent data owners: Benchmark, CADA CPCA unit, China MIIT/CAAM.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, subprocess
ROOT = Path(__file__).resolve().parents[1]
BASE = "6851fdbe4a25b30b7204d07708a1238123c14910"
BLOB = "1af792e2e80516e1ec1d7d9660c150b312168b21"
DEST = "direct-adds/2026-10-17-global-ev-regional-divergence"
ID = "2026-10-16_GL_01"
BENCH = "https://source.benchmarkminerals.com/article/global-ev-sales-reach-2-15-million-units-in-september-2026"
CADA = "https://www.cada.cn/Trends/info_91_10580.html"
MIIT = "https://www.miit.gov.cn/gxsj/tjfx/zbgy/qc/art/2026/art_8a878aeeb8a34a5b88975c5bbe94f7bf.html"
def git(*args):
    return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
assert git("merge-base","HEAD",BASE)==BASE,"Wrong original main baseline"
assert git("rev-parse",BASE+":data/cards.full.json")==BLOB,"Locked full blob mismatch"
assert git("hash-object","data/cards.full.json")==BLOB,"Do not reapply to changed full"
assert git("rev-parse",BASE+":public/data/cards.json")=="41b51ca4fa4e4f40a92c18577ea0655483295be1","Lean baseline shifted"
fullpath=ROOT/"data/cards.full.json"
leanpath=ROOT/"public/data/cards.json"
full=json.loads(fullpath.read_text(encoding="utf-8"))
lean=json.loads(leanpath.read_text(encoding="utf-8"))
assert full["total"]==lean["total"]==len(full["cards"])==len(lean["cards"])==1674
ids={c["id"] for c in full["cards"]}
assert ID not in ids and len(ids)==1674
old_cards=copy.deepcopy(full["cards"])
source_urls={u for c in full["cards"] for u in c.get("urls",[])}
for url in (BENCH,CADA,MIIT):
    assert url not in source_urls,("Already cited by historical card",url)
for c in full["cards"]:
    text=(c.get("title","")+" "+c.get("fact","")).lower()
    if c["date"]>="2026-10-12" and "9월" in text and ("ev" in text or "전기차" in text):
        raise AssertionError("Possible new-event semantic collision "+c["id"])
checked=datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
def source(name,url,published,claim,quote,fields,origin,kind="body_quote_verified"):
    return {
      "source_name":name,"source_owner":name,"source_url":url,"source_published_date":published,
      "visible_quote_date":published,"claim":claim,"source_quote":quote,
      "source_quote_status":kind,"evidence_role":"primary_event_evidence",
      "source_origin_type":origin,"supports":fields,"fetch_method":"retrieved_search_index_body_text",
      "checked_at":checked,"source_url_canonical_complete":True,
      "resolved_article_matches_quote":True}
facts=[
 source("Benchmark Mineral Intelligence",BENCH,"2026-10-16",
 "2026년 9월 글로벌 EV 215만대, 전월 대비 +17%, 전년 대비 -2%; 1~9월 1,550만대 +3%.",
 "2.15 million electric vehicles (EVs) were sold globally in September 2026",
 ["title","sub","gate","fact","implication"],"first_party_market_data"),
 source("Benchmark Mineral Intelligence",BENCH,"2026-10-16",
 "유럽 EV 9월 역대 최대 약 60만대, 전년 대비 +39%.",
 "Sales were up 39% year-on-year",
 ["title","sub","fact","implication"],"first_party_market_data"),
 source("Benchmark Mineral Intelligence",BENCH,"2026-10-16",
 "북미 EV 판매 9월 전년 대비 -44%; 2025년 9월 미국 EV 세액공제 종료 직전 구매 집중이라는 기저효과.",
 "North America’s sales fell 44% year-on-year",
 ["title","gate","fact","implication"],"first_party_market_data"),
 source("중국 자동차유통협회 승용차시장정보연석분회",CADA,"2026-10-12",
 "중국 9월 승용 NEV 내수 소매 108.4만대, 전년 대비 -16.7%. 1~9월 -12.8%.",
 "9月新能源乘用车市场零售108.4万辆，同比下降16.7%",
 ["title","sub","gate","fact","implication"],"first_party_passenger_market_data"),
 source("중국 자동차유통협회 승용차시장정보연석분회",CADA,"2026-10-12",
 "승용 NEV 9월 수출 55.8만대, 전년 대비 +163.5%; 전체 승용차 수출 중 60.8%.",
 "9月新能源乘用车厂商出口55.8万辆，同比增长163.5%",
 ["title","sub","gate","fact","implication"],"first_party_passenger_market_data"),
 source("중국 공업정보화부 (CAAM 기반 통계)",MIIT,"2026-10-12",
 "9월 중국 전체 자동차 범위의 NEV 판매 182.3만대, 전년 대비 +13.6%로 승용 소매 통계와 집계 기준이 다름.",
 "新能源汽车产销分别完成181.4万辆和182.3万辆，同比分别增长12.2%和13.6%",
 ["gate","fact","implication"],"official_ministry_statistics")
]
card={
 "id":ID,"region":"GL","date":"2026-10-16","cat":"Market Structure",
 "sub_cat":"EV 수요·도매/소매·수출","signal":"high",
 "title":"세계 EV 9월 −2%…중국 내수 −16.7%·수출 +163.5%, 집계별 양극화",
 "sub":"Benchmark 집계의 9월 세계 EV 판매는 215만 대(전년 대비 −2%, 전월 대비 +17%)다. 유럽은 +39%로 역대 최대였지만 북미는 −44%였고, 중국 승용 NEV 내수 소매는 −16.7%였다.",
 "gate":"중국 승용 NEV 수출 55.8만 대(+163.5%)와 전체 NEV 판매 182.3만 대(+13.6%)는 내수 소매 108.4만 대(−16.7%)와 서로 다른 집계다. 수출·도매·소매·차종 범위를 동일한 지표로 더하거나 차감하면 수요를 오독한다.",
 "fact":"Benchmark Mineral Intelligence가 10월 16일 발표한 2026년 9월 글로벌 EV 판매는 215만 대, 전년 대비 −2%·전월 대비 +17%이며 1~9월 누계는 1,550만 대(+3%)다. 유럽 9월 판매는 약 60만 대(+39%), 북미는 −44%였다. 중국 승용차시장정보연석분회의 9월 승용 NEV 내수 소매는 108.4만 대(−16.7%), 승용 NEV 수출은 55.8만 대(+163.5%)이고 수출 내 NEV 비중은 60.8%다. 한편 중국 공업정보화부의 전체 NEV 판매(상업용 포함·출하 기준)는 182.3만 대(+13.6%)다. 북미 −44%에는 2025년 9월 미국 구매세액공제 종료 직전 판매 급증의 높은 비교기준이 있다. 중국 전체 NEV 출하 증가를 국내 승용차 소비 회복으로 해석하거나 북미 비교연도 효과를 신규 수요급락으로 단정하면 안 된다.",
 "implication":["내수 시장 약세에도 중국 제조사의 해외 출하 비중이 커지면서 셀·소재·부품 수요를 판단할 때 중국 내수 소매와 생산·도매·수출을 분리해야 한다. 유럽의 강세와 북미 기저효과 역시 한 방향의 세계 EV 수요로 합산해 판단하기 어렵다. 다음 확인은 10월 소매·출하·수출 추이 및 실제 완성차·셀 재고와 가격·마진이다."],
 "urls":[BENCH,CADA,MIIT],"fact_sources":facts,
 "source_diversity_status":"INDEPENDENT_THREE_DATA_OWNERS_DISTINCT_SCOPES",
 "source_diversity_measure":{"unique_source_owners":3,"distinct_source_urls":3,"first_party_primary":3,
 "sampling_caveat":"Benchmark global EV and Chinese industry retail/exports and ministry all-NEV shipments are non-interchangeable populations."},
 "source_discovery_ledger":[
  {"source_url":BENCH,"source_owner":"Benchmark Mineral Intelligence","outcome":"used_in_fact_sources","unique_contribution":"Global / Europe / North America 9월 EV 판매 YoY/MoM·발표일"},
  {"source_url":CADA,"source_owner":"중국 승용차시장정보연석분회","outcome":"used_in_fact_sources","unique_contribution":"중국 국내 승용 NEV 소매/수출/수출구조"},
  {"source_url":MIIT,"source_owner":"중국 공업정보화부","outcome":"used_in_fact_sources","unique_contribution":"중국 상업용 포함 NEV 판매 182.3만대와 통계모집단 차이"}],
 "date_role":{"status":"PUBLICATION_DATE_EVIDENCE_REVIEWED","event_date":"2026-10-16",
 "representative_date":"2026-10-16","role":"latest_global_monthly_market_assessment_published",
 "reference_data_period":"2026-09","publication_dates":["2026-10-12","2026-10-16"],
 "source_publication_dates":["2026-10-12","2026-10-16"],"earliest_same_event_date_checked":True,
 "event_date_source_url":BENCH,"event_date_source_quote":"16th October 2026",
 "representative_date_reason":"16 October is the publication date of new global cross-region monthly assessment; underlying September data are not an October sales event."},
 "event_fingerprint":{"actor":"Benchmark data / CADA CPCA / MIIT","asset_or_policy":"September 2026 EV retail/export and global market regional divergence","location":"Global/China/Europe/North America","event_type":"monthly_market_data_release","event_date":"2026-10-16","source_url_cluster":[BENCH,CADA,MIIT]},
 "related":[],"related_lineage":{"status":"INDEPENDENT_EVENT_REVIEWED","relation_type":"new_unrelated_event",
 "related_ids":[],"same_event_checked":True,"earliest_same_event_date_checked":True,
 "reason":"September global monthly sales report published Oct16 differs in scope/date from previous July-August and battery shipment statistics; no production Related edge until governed lifecycle."}
}
# Do not convert data assessments to realized company customer orders.
assert "ESS 수주" not in card["fact"] and not card["related"]
assert sum(s["source_owner"]==facts[0]["source_owner"] for s in facts)==3
assert len({s["source_url"] for s in facts})==3
for c in (full,lean):
    index=next((i for i,x in enumerate(c["cards"]) if x["date"]<card["date"]),len(c["cards"]))
    c["cards"].insert(index,copy.deepcopy(card))
    c["total"]=1675;c["updated"]=checked
assert [r["id"] for r in full["cards"]]==[r["id"] for r in lean["cards"]]
breakdown={"market_structure_competition":20,"supply_demand_price_utilisation":25,
"technology_performance_safety":0,"cashflow_asset_value":3,"law_policy_market_access":0,
"systemic_scale":5,"persistence_irreversibility":3,"decision_urgency_actionability":2}
assert sum(breakdown.values())==58
attestation={
 "id":ID,"execution_credibility_gate":"PASS","independent_cardability_gate":"PASS",
 "anchor_classes":["data_financial_anchor","strategic_behavior_anchor"],"selection_route":"structural_non_execution_route",
 "decision_news_value_score":58,"decision_value_breakdown":breakdown,"decision_value_classification":"material_industry_signal",
 "publication_urgency":"near_term","technology_evidence_level":"not_applicable","policy_stage":None,
 "novelty_cap_basis":"none","systemic_scale_denominator":"Benchmark 2026년 9월 세계 EV 215만 대; 중국 승용 NEV 소매 108.4만 대·수출 55.8만 대; 각 분모는 별도 지표로만 사용",
 "denominator_gap":None,
 "prior_state":"Benchmark의 2026년 8월 세계 EV 판매 증가율은 전년 대비 +2%였고 중국 내수 감소율은 −11%였다. 세계 지표만 보면 지역별 역학이 상쇄될 수 있었다.",
 "new_verified_fact":"9월 세계 EV 판매 215만대(전년 대비 −2%, 전월 대비 +17%). 유럽 +39%, 북미 −44%, 중국 승용 NEV 국내 소매 −16.7%/수출 +163.5%, MIIT 전체 NEV 판매 +13.6%는 서로 다른 통계모집단이다.",
 "changed_judgment":"글로벌 성장률 한 숫자로 중국 셀·소재 수요 회복을 판단하는 것은 부적절하다. 내수 EV 소매 위축과 수출 채널 확대, 유럽 성장·북미 기저효과를 분리해 해석해야 한다.",
 "evidence_review_summary":"Deep Summary 여섯 차원 개별 QC(정식 Prompt 0.6 단계 PASS 주장 아님): ① 과거=8월 세계 YoY +2%, 중국 YoY −11%; ② 변화=9월 세계 −2%, 유럽 +39%, 북미 −44%; ③ 수치=세계 215만대/중국 승용 NEV 소매 108.4만 −16.7%·수출 55.8만 +163.5%/중국 MIIT 전체 NEV 판매 182.3만 +13.6%; ④ 경계=승용 내수 소매/승용 수출/전체 NEV 출하/글로벌 Benchmark가 서로 다른 분모이고 북미는 전년 구매세액공제 종료 직전의 높은 기저; ⑤ 경로=해외수출 비중 증가·판매 지역 변화→셀·소재 조달·가격구조 판단; ⑥ 재확인=10월 각 통계·재고·가동률·수출가격·분기 영업이익. Benchmark original article 2026-10-16, CADA CPCA 2026-10-12, MIIT 2026-10-12 indexed body paragraphs with exact short quotations, dates and support fields checked; independent owners and differing scopes preserved. No original site direct-HTTP receipt; fetch_method explicitly records web-indexed article text, not fabricated full file read. Structural value score B25 = observed sales & trade flows, A20 = separate growth shift in export channel geography/share (NEV exports as 60.8% of all passenger exports, 21pp rise), D3 = bounded possible supplier economics (not proven margin); no duplicate credit for a policy announcement. A formal Stage C→0.6 evidence chain is not claimed and must not be fabricated.",
 "next_confirmation_points":["10월 중국 NEV 승용 내수 소매·전체 도매판매·승용 수출의 각각의 성장률과 분모 재확인","유럽과 북미 10월의 계절성·2025년 미국 구매세액공제 만료 기저효과 제거 후 실수요 확인","배터리 셀·파우치필름 소재 업체의 지역별 실제 출하·ASP·재고·마진 변동과 연계 여부 확인"],
 "inclusion_decision":"standard_include","owner_override_reason":None,
 "structural_non_execution_reason":"실제 지역별 신차 판매·승용 수출·도매 출하의 검증된 수치가 상충되는 수요 해석을 교정하는 사건이다. 물리적 투자/계약 발표 없이도 독립적인 구조 정보가 있다.",
 "why_execution_event_not_required":"산업 수급 및 수출시장 채널 구성을 바꾸는 월간 실적 데이터이므로 개별 프로젝트 착공 사건은 가치 판단의 선결 조건이 아니다."
}
mani={"schema":"manual_direct_add_v2","status":"PASS",
"direct_add_id":"R29_20261017_INDEPENDENT_EV_DEMAND_EXPORT_DIVERGENCE",
"review_mode":"already_reviewed_bounded_direct_add","formal_full_run_claimed":False,
"base_main_commit_sha":BASE,"base_full_blob_sha":BLOB,"expected_before":1674,"expected_after":1675,
"output_updated":checked,"operations":{"add":[ID],"update":[],"id_migration":[]},
"editorial_attestation":{"policy_version":"EMBEDDED_NEWS_VALUE_SELECTION_V4","additions":[attestation],"updates":[]}}
def serial(d,compact=False,trail=True):
    return json.dumps(d,ensure_ascii=False,indent=None if compact else 2,separators=(",",":") if compact else None)+("\n" if trail else "")
fullpath.write_text(serial(full),encoding="utf8")
leanpath.write_text(serial(lean,True,False),encoding="utf8")
# Canonical LEAN projection authoritative; full is never rewritten by exporter.
subprocess.run(["node","scripts/lean_cards.mjs"],cwd=ROOT,check=True)
subprocess.run(["node","scripts/lean_cards.mjs","--check"],cwd=ROOT,check=True)
path=ROOT/DEST/"direct-add.json"
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(serial(mani),encoding="utf8")
for p in [fullpath,leanpath,path]:
    print("R29_STAGED",p.relative_to(ROOT),len(p.read_bytes()),hashlib.sha256(p.read_bytes()).hexdigest())
print("R29_NEW_CARD",ID,"58 POINTS",len(full["cards"]),len(lean["cards"]))

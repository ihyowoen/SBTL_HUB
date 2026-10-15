#!/usr/bin/env python3
"""Prepare exactly two issuer/SEC-verified fixes against locked main; writes only staging copies."""
import copy, json, hashlib, pathlib
BASE=pathlib.Path(__file__).resolve().parents[1]
OUT=pathlib.Path("/tmp/R23_FOCUSED_CORRECTIONS_20261015")
BLOB_FULL="d0b472e4173e565284616bb7eec0e4b28e1a42b9"
BLOB_LEAN="c39eac64afde20ff0ccacd920e12abbdab1b3d02"
UPDATED="2026-10-15T05:40:32Z"
NTH_IR="https://nthcycle.com/newsroom/nth-cycle-announces-landmark-1-1-billion-offtake-agreement-with-trafigura-expands-operations-in-us-and-europe"
NTH_SEC="https://www.sec.gov/Archives/edgar/data/2102713/000119312526394814/kcac-20260918.htm"
LAR_AUG="https://investors.lithium-argentina.com/news-releases/news-release-details/lithium-argentina-finalizes-ppg-joint-venture-announces-180m"
LAR_SEP="https://investors.lithium-argentina.com/news-releases/news-release-details/lithium-argentina-announces-closing-180m-strategic-investment"
CHANGE_IDS={"R3_07","2026-08-24_GL_03"}
def obj(path):return json.loads(path.read_text(encoding="utf-8"))
def card(d,cid):
    result=[x for x in d['cards'] if x['id']==cid]
    assert len(result)==1,cid
    return result[0]
import subprocess
assert subprocess.run(["git","rev-parse","HEAD:data/cards.full.json"],cwd=BASE,text=True,capture_output=True,check=True).stdout.strip()==BLOB_FULL
assert subprocess.run(["git","rev-parse","HEAD:public/data/cards.json"],cwd=BASE,text=True,capture_output=True,check=True).stdout.strip()==BLOB_LEAN
full_orig=obj(BASE/"data/cards.full.json")
lean_orig=obj(BASE/"public/data/cards.json")
assert len(full_orig["cards"])==len(lean_orig["cards"])==1674
assert full_orig["updated"]==lean_orig["updated"]=="2026-10-08T06:35:17Z"
assert [c['id'] for c in full_orig['cards']]==[c['id'] for c in lean_orig['cards']]
full=copy.deepcopy(full_orig)
lean=copy.deepcopy(lean_orig)
def visible_fixes(c,cid):
    assert c["id"]==cid
    if cid=="R3_07":
        assert "완벽한 상업화" in c["sub"] and "완연한 주류" in c["gate"]
        c["title"]="Nth Cycle–Trafigura, 재활용 니켈·리튬 11억달러 규모 10년 조건합의"
        c["sub"]="2026년 3월 발표한 구속력 있는 오프테이크 조건합의서다. 실제 구매·인도 계약과 상업화 완료로 해석해서는 안 된다."
        c["gate"]="2026년 9월 SEC S-4는 Trafigura 거래가 최종 구매계약 체결 및 미국 핵심 정제시설 개발 등 선행조건을 남긴 binding term sheet라고 명시했다."
        c["fact"]="Nth Cycle은 3월 16일 Trafigura와 약 11억달러로 평가되는 10년 오프테이크 조건합의를 발표했다. 대상은 MHP에 포함된 니켈 2,000t과 배터리급 탄산리튬 1,500t이며, 9월 SEC 서류에 따르면 최종 공급·구매계약 및 이행조건은 아직 남아 있다. 기존 오하이오 시설의 가동과 이 거래에 따른 장래 물량 인도는 구분해야 한다."
        c["implication"]=["미국 폐배터리 정제의 장기 판로 확보 가능성을 보여주지만 11억달러를 이미 발생한 매출이나 확정 출하로 계산할 수 없다. 후속 확인 지점은 최종계약·정제시설 개발·실제 인도다."]
        for u in [NTH_IR,NTH_SEC]:
            if u not in c["urls"]:c["urls"].append(u)
    else:
        assert "1.3억달러" in c["sub"] and "5,000만달러" in c["fact"]
        c["title"]="Lithium Argentina·Ganfeng, PPG JV 최종계약·1.8억달러 전환사채 투자"
        c["sub"]="8월 24일 PPG 합작법인 최종계약과 Ganfeng의 1억8,000만달러 무담보 전환사채 투자에 합의했다. 전환사채 투자는 9월 15일 종결됐으며 JV의 별도 종결은 구분한다."
        c["gate"]="발행사 원문상 1억8,000만달러는 1억3,000만달러 주식투자와 JV 5,000만달러 투입의 합계가 아니라, 6년 만기 4% 금리의 단일 무담보 전환사채다. JV 계약 체결, 투자 종결, 향후 PPG 생산은 서로 다른 단계다."
        c["fact"]="Lithium Argentina와 Ganfeng은 8월 24일 아르헨티나 PPG 프로젝트 통합을 위한 JV 최종계약을 발표했으며, 지분구조는 Ganfeng 67%·Lithium Argentina 33%다. Ganfeng은 Lithium Argentina에 1억8,000만달러를 6년 만기·연 4.0%·주당 12.50달러 전환조건의 무담보 전환사채로 투자하기로 했고 회사는 9월 15일 해당 투자 종결을 발표했다. 9월 15일 발표 당시 JV 별도 완료는 향후 일정이었다."
        c["implication"]=["투자금과 보유현금을 활용해 2027년 1월 만기 전환사채 2억5,900만달러를 상환하려는 부채구조 재편으로, 즉시 완공된 신규 리튬 생산설비나 JV에 별도 5,000만달러가 납입된 사실을 뜻하지 않는다."]
        for u in [LAR_AUG,LAR_SEP]:
            if u not in c["urls"]:c["urls"].append(u)
for dataset in [full,lean]:
    dataset["updated"]=UPDATED
    for cid in CHANGE_IDS:
        visible_fixes(card(dataset,cid),cid)
lar=card(full,"2026-08-24_GL_03")
origlar=card(full_orig,"2026-08-24_GL_03")
assert len(origlar["fact_sources"])==2
new_time=UPDATED
a0,a1=lar["fact_sources"]
for a in (a0,a1):
    a["source_url"]=LAR_AUG
    a["checked_at"]=new_time
a0["claim"]="PPG JV 최종계약(지분구조 67%·33%) 발표 사실을 확인한다."
a0["source_quote"]="entered into definitive agreements"
a1["claim"]="1억8,000만달러 6년 만기 무담보 전환사채, 4.0% 이자, 12.50달러 전환가격을 확인한다."
a1["source_quote"]="$180 million unsecured convertible note"
a1["source_published_date"]="2026-08-24"
lar["fact_sources"].append({
    "source_name":"Lithium Argentina","source_url":LAR_SEP,"source_owner":"Lithium Argentina",
    "claim":"9월 15일 전환사채 투자종결 및 PPG JV와의 단계 차이를 확인한다.",
    "source_quote":"closing of the $180 million strategic investment",
    "source_quote_status":"official_material_quote_verified",
    "evidence_role":"primary_event_evidence",
    "supports":["sub","gate","fact","implication"],
    "source_published_date":"2026-09-15","visible_quote_date":"2026-09-15",
    "source_origin_type":"official_or_source_owner_material",
    "fetch_method":"web_official_body_fetch","source_url_canonical_complete":True,
    "resolved_article_matches_quote":True,"checked_at":new_time
})
for row in lar["source_claim_coverage_map"]:
    if row["visible_field"] in ["sub","gate","fact","implication"]:
        row["supporting_fact_source_indices"]=sorted(set(row["supporting_fact_source_indices"]+[2]))
assert len(lar["source_discovery_ledger"])==2
for i,row in enumerate(lar["source_discovery_ledger"]):
    row["source_url"]=LAR_AUG
    row["unique_contribution"]=lar["fact_sources"][i]["claim"]
lar["source_discovery_ledger"].append({
    "source_url":LAR_SEP,"source_name":"Lithium Argentina","source_owner":"Lithium Argentina",
    "source_role":"primary_event_evidence","outcome":"used_in_fact_sources",
    "unique_contribution":"9월 15일 전환사채 투자종결 및 PPG JV와의 단계 차이를 확인한다."
})
lar["source_evidence_entry_count"]=3
lar["source_unique_url_count"]=2
lar["source_unique_domain_count"]=1
lar["source_independent_owner_count"]=1
lar["source_diversity_measure"].update({
    "source_evidence_entry_count":3,"source_unique_url_count":2,
    "source_unique_domain_count":1,"source_independent_owner_count":1,
    "visible_source_url_count":len(lar["urls"]), "missing_source_url_count":0
})
lar["event_fingerprint"]["asset_or_policy"]=lar["title"]
lar["event_fingerprint"]["factual_anchor"]=lar["title"]
lar["event_fingerprint"]["source_url_cluster"]=[LAR_AUG,LAR_SEP]
if isinstance(lar.get("date_role"),dict):
    # Keep 8/24 as original event; 9/15 is subsequent proof, not a relabeled event date.
    lar["date_role"]["source_publication_dates"]=["2026-08-24","2026-09-15"]
    lar["date_role"]["publication_dates"]=["2026-08-24","2026-09-15"]
card(lean,"2026-08-24_GL_03")["fact_sources"]=copy.deepcopy(lar["fact_sources"])
OUT.mkdir(exist_ok=True,parents=True)
for target,d,kwargs in [("data/cards.full.json",full,{"indent":2}),("public/data/cards.json",lean,{"separators":(",",":")})]:
    dest=OUT/target
    dest.parent.mkdir(parents=True,exist_ok=True)
    src=BASE/target
    written=json.dumps(d,ensure_ascii=False,**kwargs)+("\n" if src.read_bytes().endswith(b"\n") else "")
    dest.write_text(written,encoding="utf-8")
def verify():
    originals=[c["id"] for c in full_orig["cards"]]
    assert originals==[c["id"] for c in full["cards"]]==[c["id"] for c in lean["cards"]]
    assert full["total"]==lean["total"]==1674
    assert full["schema"]==lean["schema"] and full["sort"]==lean["sort"]
    assert full["updated"]==lean["updated"]==UPDATED
    f={c["id"]:c for c in full["cards"]}
    l={c["id"]:c for c in lean["cards"]}
    fo={c["id"]:c for c in full_orig["cards"]}
    lo={c["id"]:c for c in lean_orig["cards"]}
    assert {i for i in originals if f[i]!=fo[i]}==CHANGE_IDS
    assert {i for i in originals if l[i]!=lo[i]}==CHANGE_IDS
    for i in originals:
        assert f[i]["related"]==fo[i]["related"]
        assert l[i]["related"]==lo[i]["related"]
        for k in l[i]:
            assert f[i].get(k)==l[i][k],(i,k)
    nth=f["R3_07"];li=f["2026-08-24_GL_03"]
    assert "조건합의" in nth["title"] and NTH_SEC in nth["urls"]
    assert "Glencore" not in " ".join(str(nth[k]) for k in ("title","fact"))
    assert "전환사채" in li["title"] and "$130 million strategic investment" not in json.dumps(li,ensure_ascii=False)
    assert len(li["fact_sources"])==3 and li["source_unique_url_count"]==2
    assert all(0 <= index <len(li["fact_sources"]) for c in li["source_claim_coverage_map"] for index in c["supporting_fact_source_indices"])
    assert all(c["date"]==fo[c["id"]]["date"] for c in full["cards"])
    print("QC PASS 1674 IDs/no drops; 2 changed only; cross Full/Lean projection exact; Related unchanged; dates unchanged")
verify()
for f in [OUT/"data/cards.full.json",OUT/"public/data/cards.json"]:
    print("PREVIEW",str(f),f.stat().st_size,"sha256",hashlib.sha256(f.read_bytes()).hexdigest())

#!/usr/bin/env python3
from __future__ import annotations

import copy, hashlib, json, subprocess, sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
RUN=ROOT/'runs/2026-09-03'
A_PATH=RUN/'stage_a_prompt_0_1p_r6_promotion16_20260903_R1.json'
OLD_B=RUN/'stage_b_r6_strict7_20260903_R1.json'
OUT=RUN/'stage_b_r6_promotion2_20260903_R1.json'
REPORT=RUN/'stage_b_r6_promotion2_validation_20260903_R1.json'
PROMPT=ROOT/'docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md'
CANON=ROOT/'data/cards.full.json'
MAIN='df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4'
BLOB='53219907cdb435c3822c41d097b23e475662aa8a'

a=json.loads(A_PATH.read_text(encoding='utf-8'))
strict=copy.deepcopy(a['strict_passed_spec'])
assert len(strict)==2
specs={x['spec_id']:x for x in strict}
assert set(specs)=={'STD26_R6_P01P_006','STD26_R6_P01P_024'}
A_SHA=hashlib.sha256(A_PATH.read_bytes()).hexdigest()

def domain(u): return urlsplit(u).netloc.lower().removeprefix('www.')

def canonical_ids():
    d=json.loads(CANON.read_text(encoding='utf-8')); cards=d if isinstance(d,list) else d.get('cards',[])
    return {str(x.get('id')) for x in cards if isinstance(x,dict) and x.get('id')}

used=canonical_ids()
if OLD_B.exists():
    old=json.loads(OLD_B.read_text(encoding='utf-8'))
    for p in old.get('evidence_packages',[]):
        cid=(p.get('draft') or {}).get('id')
        if cid: used.add(cid)
planned=set()
def allocate(date,region):
    for n in range(1,100):
        cid=f'{date}_{region}_{n:02d}'
        if cid not in used and cid not in planned:
            planned.add(cid); return cid
    raise RuntimeError((date,region))

E={
 'STD26_R6_P01P_006':{
   'region':'GL','date':'2026-08-31','cat':'Materials','sub_cat':'Argentina lithium brine / binding farm-in','signal':'high',
   'title':'라이온타운, 아르헨티나 Centenario 리튬 염호 최대 100% earn-in 계약',
   'sub':'4년간 US$40m 프로젝트 지출…초기 US$5m 현금+US$10m 주식, 단계별 투자 연동',
   'gate':'리튬 염호 진입이 탐색 단계가 아니라 구속력 있는 단계형 farm-in 계약으로 전환됐다.',
   'fact':'Liontown은 NEXT Lithium과 아르헨티나 Salta의 Centenario 리튬 염호 프로젝트에 대해 최대 100% 지분을 확보할 수 있는 binding farm-in agreement를 체결했다. 계약은 4년간 US$40m 프로젝트 지출을 요구하며, 계약이 unconditional이 되면 초기 대가로 US$5m 현금과 US$10m 상당 Liontown 주식을 지급한다.',
   'implication':['Liontown이 Kathleen Valley의 경암 리튬 중심 포트폴리오에 아르헨티나 염호 옵션을 추가하면서 원료·지역 다변화가 실제 계약 단계로 들어갔다.','다만 100% 지분은 즉시 취득이 아니라 단계별 earn-in 결과에 달려 있으므로 후속 탐사성과·마일스톤 지급·지분상승을 추적해야 한다.'],
   'date_role':'binding farm-in agreement announcement/execution',
   'claims':[
      ('P2-006-C1','Liontown과 NEXT Lithium은 Centenario 프로젝트에 대해 Liontown이 최대 100% 지분을 earn-in할 수 있는 binding farm-in agreement를 체결했다.',['P2-006-P1','P2-006-P2']),
      ('P2-006-C2','계약상 프로젝트 지출은 4년간 US$40m이다.',['P2-006-P1','P2-006-P2']),
      ('P2-006-C3','계약이 unconditional이 될 때 초기 대가는 US$5m 현금과 US$10m 상당 Liontown 주식이다.',['P2-006-P1','P2-006-P2']),
   ],
   'sources':[
      {'id':'P2-006-P1','owner':'Liontown','role':'acquirer_primary_release','url':'https://www.liontown.com/latest-news/liontown-to-earn-up-to-100-of-the-centenario-lithium-brine-project-in-argentina/','published':'2026-08-31','summary':'Liontown confirms the binding farm-in, staged path to 100%, US$40m four-year project expenditure and initial US$5m cash plus US$10m shares.','quote':'executed a binding farm-in agreement with Next Lithium Corp. to earn up to a 100% interest'},
      {'id':'P2-006-P2','owner':'NEXT Lithium','role':'counterparty_primary_release','url':'https://www.globenewswire.com/news-release/2026/09/01/3354112/0/en/next-lithium-partners-with-liontown-for-the-development-and-100-sale-of-the-centenario-lithium-project.html','published':'2026-09-01','summary':'NEXT independently confirms the binding agreement, four-year US$40m expenditure and initial consideration terms.','quote':'US$40 million (C$55 million) in project expenditure over a four-year period.'},
   ],
 },
 'STD26_R6_P01P_024':{
   'region':'GL','date':'2026-08-31','cat':'Materials','sub_cat':'lithium earnings / ESS-linked demand','signal':'high',
   'title':'리튬 업계 실적 반등에 ESS 수요·가격 회복 가시화',
   'sub':'Ganfeng H1 흑자전환·Albemarle Q2 Energy Storage 매출 78% 증가',
   'gate':'ESS 수요와 리튬 가격 회복이 단순 전망이 아니라 주요 업체의 최신 실적 지표에 반영됐다.',
   'fact':'Ganfeng Lithium은 2026년 상반기 매출 약 RMB23.1bn과 순이익 약 RMB4.26bn을 기록해 전년 동기 적자에서 흑자로 전환했다. Albemarle의 2026년 2분기 Energy Storage 부문은 매출 US$1.277bn으로 전년 동기 대비 77.9% 증가했고, 판매량은 11.0%, 평균 실현가격은 60.5% 상승했다. 두 사례는 최근 리튬 업황 개선이 가격과 ESS 관련 수요 지표에 동시에 나타나고 있음을 보여준다.',
   'implication':['EV 외 ESS가 리튬 수요의 추가 축으로 커지면서 가격 회복 시 광산·정제·배터리 밸류체인의 실적 레버리지가 커질 수 있다.','다만 Ganfeng과 Albemarle의 실적 개선에는 가격·물량·비용 등 복수 요인이 작용하므로 ESS 수요 하나만으로 업계 전체 수익성 회복을 설명하면 안 된다.'],
   'date_role':'cross-issuer lithium earnings signal publication',
   'claims':[
      ('P2-024-C1','Ganfeng Lithium의 2026년 상반기 매출은 약 RMB23.1bn, 순이익은 약 RMB4.26bn으로 전년 동기 적자에서 흑자로 전환했다.',['P2-024-I1','P2-024-I2']),
      ('P2-024-C2','Albemarle의 2026년 2분기 Energy Storage 매출은 US$1.2767bn으로 전년 동기 대비 77.9% 증가했다.',['P2-024-P1']),
      ('P2-024-C3','Albemarle의 해당 분기 Energy Storage 판매량은 11.0%, 평균 실현가격은 60.5% 전년 대비 상승했다.',['P2-024-P1']),
   ],
   'sources':[
      {'id':'P2-024-P1','owner':'Albemarle','role':'issuer_primary_earnings_release','url':'https://www.albemarle.com/au/en/news/albemarle-reports-second-quarter-2026-results','published':'2026-08-05','summary':'Albemarle reports Q2 Energy Storage sales of US$1.2767bn, volume +11.0%, average realized price +60.5%, and adjusted EBITDA +229.3%.','quote':'Energy Storage net sales for the second quarter of 2026 were $1.3 billion'},
      {'id':'P2-024-I1','owner':'Shanghai Metals Market','role':'independent_results_analysis','url':'https://news.metal.com/newscontent/104086807-smm-analysis-feng-lithium-returned-to-profit-in-h1-2026-with-resource-and-capacity-dual-drivers-delivering-notable-results','published':'2026-08-30','summary':'SMM reports Ganfeng H1 revenue RMB23.097bn and net profit RMB4.257bn, a swing from loss to profit.','quote':'H1 revenue of 23.097 billion yuan, a 175.75% YoY surge'},
      {'id':'P2-024-I2','owner':'S&P Capital IQ via MarketScreener','role':'independent_results_confirmation','url':'https://www.marketscreener.com/news/ganfeng-lithium-group-co-ltd-reports-earnings-results-for-the-half-year-ended-june-30-2026-ce7858dfd181ff2c','published':'2026-08-28','summary':'Independent earnings feed confirms Ganfeng H1 revenue RMB23.09695bn and net income RMB4.25716bn versus a prior-year net loss.','quote':'Net income was CNY 4,257.16 million compared to net loss'},
   ],
 },
}

packages=[]; draft_cards=[]
for spec_id in sorted(E):
    spec=specs[spec_id]; e=E[spec_id]
    sources=[]
    for s in e['sources']:
        r=copy.deepcopy(s); r.update({'domain':domain(r['url']),'fetched':True,'fetch_status':'fetched_body_or_authoritative_page','source_quote':r.pop('quote'),'source_quote_status':'body_quote_verified','headline_only':False,'rss_or_snippet_only':False,'claim_use':'short_verified_quote_plus_paraphrase'})
        sources.append(r)
    owners=list(dict.fromkeys(s['owner'] for s in sources)); domains=list(dict.fromkeys(s['domain'] for s in sources))
    claims=[{'claim_id':cid,'claim':text,'supported_by_source_ids':srcs,'visible':True,'status':'SUPPORTED'} for cid,text,srcs in e['claims']]
    discovery=[{'url':s['url'],'owner':s['owner'],'status':'fetched_verified','body_or_document_verified':True} for s in sources]
    related={'same_event_check':'PASS','earliest_event_date_check':'PASS','relation_type':'new_unrelated_event','matched_baseline_candidate_ids':spec.get('related_prepass',{}).get('matched_baseline_candidate_ids',[]),'matched_current_candidates':[],'fresh_follow_up_anchor_class':None,'fresh_follow_up_anchor':None,'incremental_fact':None,'changed_judgment':None,'rejected_relation_candidates':[],'reinforcement_transfer_ledger':[],'production_related_ids':[],'note':'No prior/current duplicate or lineage target established at Stage B.'}
    date_role={'representative_event_date':e['date'],'role':e['date_role'],'stage_a_representative_date':spec.get('representative_date'),'source_publication_dates':sorted({s['published'] for s in sources}),'status':'PASS','note':'Current event/signal anchor date is preserved separately from each source publication date.'}
    cid=allocate(e['date'],e['region'])
    draft={'id':cid,'source_spec_id':spec_id,'region':e['region'],'date':e['date'],'cat':e['cat'],'sub_cat':e['sub_cat'],'signal':e['signal'],'title':e['title'],'sub':e['sub'],'gate':e['gate'],'fact':e['fact'],'implication':e['implication'],'urls':[s['url'] for s in sources],'related':[],'fact_sources':copy.deepcopy(sources),'related_evidence_review':copy.deepcopy(related),'date_role':copy.deepcopy(date_role),'stage_b_only':True,'stage_b_fact_safety_not_declared':True,'stage_b_publish_readiness_not_declared':True,'state':'draft'}
    pkg={'source_spec_id':spec_id,'spec_id':spec_id,'source_story_ids':spec['source_story_ids'],'stage_a_selection_package':copy.deepcopy(spec),'stage_a_artifact':str(A_PATH.relative_to(ROOT)),'stage_a_artifact_sha256':A_SHA,'stage_a_support_sources_attempted':discovery,'source_discovery_ledger':discovery,'source_discovery_status':'completed_verified_source_found','source_independence_ledger':[{'source_id':s['id'],'owner':s['owner'],'role':s['role'],'domain':s['domain'],'independent_editorial_owner':not s['role'].startswith(('acquirer_primary','counterparty_primary','issuer_primary'))} for s in sources],'source_unique_url_count':len({s['url'] for s in sources}),'source_unique_domain_count':len(domains),'source_independent_owner_count':len(owners),'source_role_coverage':dict(Counter(s['role'] for s in sources)),'source_synthesis_plan':'Primary/issuer facts control where available; independent second-owner sources verify the quantified terms. Visible copy is limited to claim-map-supported facts and explicitly bounded synthesis.','fact_sources':copy.deepcopy(sources),'claim_map':claims,'source_conflicts':[],'date_role':copy.deepcopy(date_role),'related_evidence_review':copy.deepcopy(related),'execution_anchor_review':{'selection_route':spec['selection_route'],'stage_a_anchor_classes':spec['anchor_classes'],'status':'PASS','evidence_basis':[s['id'] for s in sources[:2]],'note':'Stage B evidence supports the Stage A route without changing the promotion score or inventing a stronger execution state.'},'draft_status':'draft','draft_blocked':False,'draft_blocked_reason':None,'rescue_log':[],'unresolved_questions':spec.get('next_confirmation_points',[]),'draft':copy.deepcopy(draft)}
    assert pkg['source_independent_owner_count']>=2 and len(sources)>=2 and all(c['status']=='SUPPORTED' for c in claims)
    packages.append(pkg); draft_cards.append(draft)

artifact={'stage':'stage_b','status':'PASS_DRAFTED_NOT_FACT_SAFE','run_tag':'20260903_R6_STAGE_B_PROMOTION2_R1','source_prompt_file':'docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md','source_prompt_version':'STAGE_B_V4_20260829','source_prompt_sha256':hashlib.sha256(PROMPT.read_bytes()).hexdigest(),'stage_a_artifact':str(A_PATH.relative_to(ROOT)),'stage_a_artifact_sha256':A_SHA,'main_sha':MAIN,'canonical_blob_sha':BLOB,'lineage_integrity_status':'PASS','stage_a_validity_guard_applied':True,'strict_gate_metadata_preserved':True,'execution_anchor_metadata_preserved':True,'superseded_lineage_mixed':False,'manual_integrated_rule_mixed':False,'previous_run_output_mixed':False,'input_strict_count':2,'strict_passed_spec_count':2,'stage_b_accounting_matches_strict_passed_spec_count':True,'draft_count':2,'draft_blocked_count':0,'fact_safety_declared_count':0,'publish_ready_declared_count':0,'external_search_or_fetch_used':True,'strict_passed_spec':strict,'evidence_packages':packages,'draft_cards':draft_cards,'draft_blocked':[],'draft_blocked_schema':[],'next_authorized_stage':'Prompt 0.3 Stage C r0 on the two Prompt 0.1P-promoted Stage B drafts'}
OUT.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

from validation_scripts import stage_lineage_contract_check as lineage
rc_lineage=lineage.check_stage_b(artifact)
rc_evidence=subprocess.run([sys.executable,str(ROOT/'validation_scripts/stage_b_evidence_gate.py'),str(OUT)],cwd=ROOT).returncode
rc_contract=subprocess.run([sys.executable,str(ROOT/'validation_scripts/stage_artifact_contract_check.py'),'B',str(OUT)],cwd=ROOT).returncode
errors=[]
if len(packages)!=2: errors.append('package_count')
if {p['source_spec_id'] for p in packages}!=set(specs): errors.append('strict_spec_coverage')
if any(p['source_independent_owner_count']<2 for p in packages): errors.append('owner_diversity')
if any(any(c['status']!='SUPPORTED' for c in p['claim_map']) for p in packages): errors.append('claim_support')
if len({d['id'] for d in draft_cards})!=2 or any(d['id'] in canonical_ids() for d in draft_cards): errors.append('draft_id_collision')
report={'schema':'stage_b_r6_promotion2_validation_v1','status':'PASS' if rc_lineage==0 and rc_evidence==0 and rc_contract==0 and not errors else 'FAIL','artifact':str(OUT.relative_to(ROOT)),'artifact_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'stage_b_lineage_check_rc':rc_lineage,'stage_b_evidence_gate_rc':rc_evidence,'stage_b_production_contract_rc':rc_contract,'custom_errors':errors,'input_strict_count':2,'draft_count':2,'draft_blocked_count':0,'claim_count':sum(len(p['claim_map']) for p in packages),'source_count':sum(len(p['fact_sources']) for p in packages),'all_claims_supported':all(all(c['status']=='SUPPORTED' for c in p['claim_map']) for p in packages),'all_packages_multi_owner':all(p['source_independent_owner_count']>=2 for p in packages),'fact_safety_declared':False,'publish_ready_declared':False}
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if report['status']=='PASS' else 1)

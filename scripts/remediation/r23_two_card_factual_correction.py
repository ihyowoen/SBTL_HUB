#!/usr/bin/env python3
"""R23: Stage an immutable, source-checked TWO-card correction into /tmp only.
This script never writes production Full or Lean; a separate branch-scoped CI job
must approve the exact two-file preview output before committing proposed changes.
Do not treat this factual correction as a 0.0C or Stage A release authorization.
"""
from pathlib import Path
import copy,json,hashlib,collections
ROOT=Path(__file__).resolve().parents[1]; OUT=Path('/tmp/r23_hotfix_preview');OUT.mkdir(exist_ok=True)
full_path=ROOT/'data/cards.full.json'
lean_path=ROOT/'public/data/cards.json'
assert hashlib.sha256(full_path.read_bytes()).hexdigest() == '15e202db02664e682890f1402d745ec71b2739274debc5c948e9567fa73582a1', 'SOURCE_BASE_FULL_CHANGED'
assert hashlib.sha256(lean_path.read_bytes()).hexdigest() == 'eef99e504a7b525be85c74a9e7d92091ed277257c9408a298c358c0afd61da18', 'SOURCE_BASE_LEAN_CHANGED'
full=json.loads(full_path.read_text());lean=json.loads(lean_path.read_text())
assert len(full['cards'])==len(lean['cards'])==1674
ids=['R3_07','2026-08-24_GL_03']
orig_full=copy.deepcopy(full);orig_lean=copy.deepcopy(lean)
O8="https://investors.lithium-argentina.com/news-releases/news-release-details/lithium-argentina-finalizes-ppg-joint-venture-announces-180m"
O9="https://investors.lithium-argentina.com/news-releases/news-release-details/lithium-argentina-announces-closing-180m-strategic-investment"
N3="https://nthcycle.com/newsroom/nth-cycle-announces-landmark-1-1-billion-offtake-agreement-with-trafigura-expands-operations-in-us-and-europe"
SEC="https://www.sec.gov/Archives/edgar/data/2102713/000119312526394814/kcac-20260918.htm"
def change(card):
  if card['id']=='R3_07':
    card['title']="Nth Cycle–Trafigura, 재활용 니켈·리튬 11억달러 규모 조건합의"
    card['sub']="2026년 3월 발표한 10년 오프테이크는 구속력 있는 조건합의서다. 본계약 체결과 실제 인도는 별도 조건으로 남아 있다."
    card['gate']="회사 발표는 예상 거래가치를 약 11억달러로 제시했지만, 9월 SEC 문서는 Trafigura 조건합의가 최종 구매계약 체결과 선행조건 충족을 필요로 한다고 명시한다."
    card['fact']="Nth Cycle은 2026년 3월 16일 Trafigura와 재활용 MHP 내 니켈 2,000t 및 탄산리튬 1,500t의 장기 구매를 위한 구속력 있는 조건합의서를 발표했다. 약 11억달러는 장기 거래의 추정가치다. SEC 공개자료에 따르면 최종 원료구매계약 체결과 미국 정제 프로젝트 개발 등 조건이 남아 있으며, 계약 물량이 이미 인도·매출화됐다는 근거는 아니다."
    card['implication']=["폐배터리 정제 기술의 잠재적 구매 수요를 보여주는 신호지만, 예상 계약가치가 곧 확정 매출이나 상업생산 실적을 의미하지 않는다. 실제 공급 능력·원료 확보·본계약 이행이 관건이다."]
    card['urls']=list(dict.fromkeys(card['urls']+[N3,SEC]))
  elif card['id']=='2026-08-24_GL_03':
    card['title']="Lithium Argentina–Ganfeng, PPG JV 최종계약·1.8억달러 전환사채 합의"
    card['sub']="8월 24일 PPG JV 지분 67:33 최종계약과 1.8억달러 무담보 전환사채 투자합의를 발표했다. 투자 자금은 9월 15일 종결됐으며 JV 종결은 별도다."
    card['gate']="공식 8월 24일 발표의 투자수단은 6년 만기 연 4% 무담보 전환사채다. 기존 1.3억달러 신용공여와 JV에 5,000만달러를 투입하는 구조로 설명하는 것은 잘못이다."
    card['fact']="Lithium Argentina와 Ganfeng은 8월 24일 Pozuelos-Pastos Grandes(PPG) 공동개발 JV 최종계약(지분 Ganfeng 67%·Lithium Argentina 33%)과 Ganfeng의 1.8억달러 무담보 전환사채 인수합의를 발표했다. 전환사채는 6년 만기·연 4% 이자·주당 12.50달러 전환 조건이다. 회사는 9월 15일 해당 투자의 실제 종결을 발표했다. PPG JV의 법적 종결 및 광산 가동과는 구분한다."
    card['implication']=["9월 투자종결로 기존 2027년 1월 만기 전환사채 2.59억달러를 재조달할 재원이 확보됐다. 신규 광산 생산이나 PPG JV의 종결을 확인한 것은 아니다.","JV 최종계약, 전환사채 투자종결, 장래 생산능력은 단계가 달라 각각 추적해야 한다."]
    card['urls']=[O8,O9]
    card['fact_sources'][0]['source_url']=O8
    card['fact_sources'][0]['claim']="8월 24일 PPG JV 최종계약(지분 67:33)과 별도의 1.8억달러 전환사채 투자합의를 발표했다."
    card['fact_sources'][0]['supports']=['title','sub','gate','fact','implication']
    card['fact_sources'][1]['source_url']=O9
    card['fact_sources'][1]['claim']="9월 15일 Ganfeng의 1.8억달러 6년 만기 무담보 전환사채 투자종결을 회사가 발표했다."
    card['fact_sources'][1]['source_quote']="closing of the $180 million strategic investment"
    card['fact_sources'][1]['source_published_date']='2026-09-15'
    card['fact_sources'][1]['visible_quote_date']='2026-09-15'
    card['fact_sources'][1]['supports']=['sub','gate','fact','implication']
    if 'source_discovery_ledger' in card:
      card['source_discovery_ledger'][0]['source_url']=O8
      card['source_discovery_ledger'][0]['unique_contribution']=card['fact_sources'][0]['claim']
      card['source_discovery_ledger'][1]['source_url']=O9
      card['source_discovery_ledger'][1]['unique_contribution']=card['fact_sources'][1]['claim']
    if 'source_unique_url_count' in card:
      card['source_unique_url_count']=2
      card['source_unique_domain_count']=1
    if 'event_fingerprint' in card:
      card['event_fingerprint']['asset_or_policy']=card['title']
      card['event_fingerprint']['factual_anchor']=card['title']
      card['event_fingerprint']['source_url_cluster']=[O8,O9]
    if 'writer_notes' in card:
      card['writer_notes']="2026-10-15 source-backed factual repair: 2026-08-24 investment was USD180m convertible note (not USD130m equity plus USD50m JV); 2026-09-15 closing is follow-up, not PPG JV completion."
    # Historical Stage B/C & baseline QC are immutable run evidence; do not rewrite or claim revalidation pass.
for d in [full,lean]:
  for c in d['cards']:
    if c.get('id') in ids:change(c)
  assert [x['id'] for x in d['cards']]==[x['id'] for x in orig_full['cards']]
  assert len(d['cards'])==1674
f=(OUT/'cards.full.json'); l=(OUT/'cards.json')
f.write_text(json.dumps(full,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
l.write_text(json.dumps(lean,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
for p,d,orig in [(f,full,orig_full),(l,lean,orig_lean)]:
  changed=[]
  for x,y in zip(d['cards'],orig['cards']):
    if x!=y:changed.append(x['id'])
  assert set(changed)==set(ids),changed
  assert len({x['id'] for x in d['cards']})==1674
  print(p,'size',p.stat().st_size,'sha256',hashlib.sha256(p.read_bytes()).hexdigest(),'changed_cards',changed)
for id in ids:
 a=next(c for c in full['cards'] if c['id']==id)
 b=next(c for c in lean['cards'] if c['id']==id)
 assert all(a.get(k)==v for k,v in b.items()),id
 assert all(u.startswith('https://') for u in a['urls'])
 print('CARD_PAIRED_FULL_LEAN',id,'TITLE',a['title'])
assert f.read_bytes()!=full_path.read_bytes()
assert l.read_bytes()!=lean_path.read_bytes()
assert hashlib.sha256(f.read_bytes()).hexdigest() == '09ebf08385b1bfe0cfa5816ec49f93d23f0016dfe83f1fc37b9da164157bedbb', 'FULL_PREVIEW_SHA_MISMATCH'
assert hashlib.sha256(l.read_bytes()).hexdigest() == 'df7b0c056554958fe4f75b96352d596b99d5b3b0ac52099c00a34e89044ea6ac', 'LEAN_PREVIEW_SHA_MISMATCH'
print('HOTFIX_DRY_RUN_PASS_CHANGED_EXACTLY_TWO')


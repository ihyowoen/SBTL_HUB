#!/usr/bin/env python3
"""Independent CP20->CP21 audit. Does not import builder or case definitions."""
import json,hashlib,subprocess,sys,collections
from pathlib import Path
BASE=Path('work/cp20/STAGE_A_CP20_FORMAL_20261101.json');NEW=Path('work/cp21/STAGE_A_CP21_FORMAL_20261102.json');FULL=Path('work/native/data/cards.full.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
assert sha(BASE)=='b0b06dae8fd3ac19950772479ba087e0c8b661f3388899b9bbd370f789cd21c1'
assert sha(FULL)=='d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9'
b=read(BASE);n=read(NEW);receipt=read(NEW.with_name('STAGE_A_CP21_RECEIPT_20261102.json'))
STRICT={1278,1290,1287,581,91}
SUPPORT={758,791,814,1149,1126,769,1139,778,1138}
WATCH={74,458,75,459,76,460,77,461,326,327,641,1030,646,1031,648,649,1027,1028,730,1070,647,1032,651,1127,1325,1165,253,617}
TARGET=STRICT|SUPPORT|WATCH
assert len(TARGET)==42
assert n['promotion_reassessment_ledger'][:153]==b['promotion_reassessment_ledger']
assert n['strict_passed_spec'][:42]==b['strict_passed_spec']
assert len(n['decision_ledger'])==len(b['decision_ledger'])==1330
identity=('source_row_index','story_id','candidate_id','headline_raw','primary_url','origin')
changed=set();primary_hashes={};source_docs={}
for i,(o,r) in enumerate(zip(b['decision_ledger'],n['decision_ledger'])):
 assert i==r['source_row_index']; assert all(o.get(k)==r.get(k) for k in identity),(i,'source identity changed')
 if o!=r:
  changed.add(i);tag=r['formal_0_1P_cp21_source_to_economic_act_edges_20261102']
  assert tag['row']==i and tag['source_id']==r['story_id'] and tag['human_adjudicated'] is True
  assert tag['economic_act_edges'] and tag['first_party_owner_urls']
  for ev in tag['primary_retrieval']:
   key=hashlib.sha256(ev['url'].encode()).hexdigest()[:16];p=Path('work/evidence')/(key+'.raw')
   assert ev['status']==200 and sha(p)==ev['sha256']
   text=(Path('work/evidence')/(key+'.txt')).read_text()
   assert len(text)>500 and not text.strip().startswith('Just a moment')
   primary_hashes[ev['url']]=ev['sha256'];source_docs[ev['url']]=text
  for flag in ('stage_b_authorized','accepted_facts_approved','canonical_card_write_allowed'):assert r[flag] is False
assert changed==TARGET,changed^TARGET
pools=('strict_passed_spec','candidate_review_pool','watchlist_context_pool','reject_or_support_only_pool','existing_reinforcement')
partition={}
for p in pools:
 for r in n[p]:
  sid=r['story_id'];assert sid not in partition,(p,sid);partition[sid]=p
assert set(partition)=={r['story_id'] for r in b['decision_ledger']}
for ids,p in ((STRICT,pools[0]),(SUPPORT,pools[3]),(WATCH,pools[2])):
 for i in ids:assert partition[n['decision_ledger'][i]['story_id']]==p
prior_formal={r['candidate_id'] for r in b['promotion_reassessment_ledger']}
assert len(prior_formal)==153
for r in b['decision_ledger']:
 if r['candidate_id'] in prior_formal:assert r==n['decision_ledger'][r['source_row_index']]
assert len(n['promotion_reassessment_ledger'])==195
assert len({r['candidate_id'] for r in n['promotion_reassessment_ledger']})==195
assert len(n['strict_passed_spec'])==47
assert len(n['review_pool_resolution_ledger'])==1252
assert n['summary']['processed_priority_source_observations']==195
assert n['summary']['unprocessed_editorial_observations']==1135
assert receipt['output_sha256']==sha(NEW)
assert receipt['cumulative_formal']==195 and receipt['remaining']==1135
# Evidence-content checks independently specified from original-body reading.
checks={1278:['two production lines','trial','100 GWH'],1290:['$270 million','revolving credit','accordion'],1287:['September 21','100MWh','12,000'],581:['September 22, 2026','priority access','repurpos'],91:['$11 million','conditional loan','$410 million','$992 million']}
for i,phrases in checks.items():
 tag=n['decision_ledger'][i]['formal_0_1P_cp21_source_to_economic_act_edges_20261102'];body=' '.join(source_docs[u] for u in tag['first_party_owner_urls'])
 for phrase in phrases:assert phrase.casefold() in body.casefold(),(i,phrase)
# Semantic guards: capacity stage, credit/funding stage, data age and support scope.
r=n['decision_ledger']
assert 'not series production' in r[1278]['remaining_uncertainty']
assert 'not $270m fully drawn' in r[1290]['remaining_uncertainty']
assert 'not loan disbursement' in r[91]['remaining_uncertainty']
assert r[1287]['technology_evidence_level']=='company_target_or_unsupported_claim'
assert r[1287]['decision_value_breakdown']['technology_performance_safety']<=4
assert r[1287]['date_role']['event_date']=='2026-09-21' and r[1287]['date_role']['publication_date']=='2026-09-22'
assert r[581]['date_role']['event_date']=='2026-09-22' and r[581]['date_role']['publication_date']=='2026-09-24'
assert all(r[i]['baseline_match']==r[772]['story_id'] for i in (769,778,1138,1139))
assert r[772]==b['decision_ledger'][772]
assert all(r[i]==b['decision_ledger'][i] for i in (781,1147,797,1151,504,887,510,893,82,94)),'Overmerged blocked, mixed or distinct subact sources'
assert '191m kW' in r[75]['protected_source_context'] and '0.84m kW' in r[75]['protected_source_context']
assert '1.43 million' in r[1028]['protected_source_context']
assert '300,000yen/year' in r[647]['protected_source_context'] and 'not enrolled capacity' in r[647]['protected_source_context']
assert '315kW' in r[730]['protected_source_context'] and 'first three years' in r[730]['protected_source_context']
assert '179MW is operator total order book' in r[1165]['protected_source_context']
batch=n['formal_0_1P_cp21_owner_body_batch_20261102'];assert batch['stage_b_executed'] is False and batch['canonical_main_full_related_mutations']==0 and batch['new_published_cards']==0
assert batch['global_stage_a_status']=='HOLD_OPEN_1135_UNADJUDICATED'
# Rerun actual native validators; do not trust a builder receipt.
native={}
for label,args in {'artifact':['A'],'lineage':['stage_a']}.items():
 script='stage_artifact_contract_check.py' if label=='artifact' else 'stage_lineage_contract_check.py'
 p=subprocess.run([sys.executable,'work/native/validation_scripts/'+script,*args,str(NEW)],capture_output=True,text=True)
 assert p.returncode==0 and 'PASS' in p.stdout and 'BLOCKED' not in p.stdout,(label,p.stdout,p.stderr)
 Path('work/cp21/native_'+label+'.txt').write_text(p.stdout)
 native[label]={'returncode':p.returncode,'stdout':p.stdout.strip()}
result={'independent_qc':'PASS','method':'Standalone verifier; no builder/case import; separately specified source-content and anti-overmerge checks. Not a second human or agent review.','verified_source_ids':1330,'previous_formal_unchanged':153,'previous_strict_unchanged':42,'exact_changed_rows':sorted(TARGET),'new_strict':5,'new_support':9,'new_watch':28,'cumulative_formal':195,'cumulative_strict':47,'pending_formal':1135,'original_body_documents_verified':len(primary_hashes),'native_contracts':native,'hashes':{'cp20':sha(BASE),'cp21':sha(NEW),'full1676':sha(FULL)},'global_stage_a':'HOLD','stage_b_executed':False,'canonical_main_full_related_mutations':0,'scope_limit':'42 manually adjudicated Source IDs only. HTTP success for remaining source retrievals is not formal completion.'}
NEW.with_name('STAGE_A_CP21_INDEPENDENT_QC_20261102.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))

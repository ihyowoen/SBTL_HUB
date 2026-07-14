#!/usr/bin/env python3
"""Prompt 0.5 source-diversity checker.

Claim-specific fact_sources rows may reuse a canonical article. Row reuse is
informational; fake diversity means declared unique-source counts or PASS status
do not match unique URLs / independent owners.
"""
import json,re,sys
from urllib.parse import urlparse
PASS={'PASS_MULTI_SOURCE','PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION'}
HOLD={'HOLD_NEEDS_SOURCE_AUGMENTATION','FAIL_SOURCE_DIVERSITY'}
ALLOWED=PASS|HOLD
COMPLETE={'accepted','accepted_fact_safe','accepted_fact_safe_with_warnings','evidence_complete_and_source_claim_covered'}
BUCKETS=('addable_merge_safe','cards','draft_cards','qc_cards','payload','accepted','accepted_fact_safe','accepted_fact_safe_with_warnings','evidence_complete_and_source_claim_covered','addable_hold_source_gap','addable_hold_claim_gap','needs_source_augmentation','evidence_qc_rejected','source_claim_gap','single_source_exception_review','deferred_review_pool','review_pool_deferred')
OWNER_FIELDS=('independent_owner','owner','source_owner','publisher_owner','canonical_owner','parent_owner','probable_editorial_owner','editorial_owner')
LANDING=re.compile(r'^/?$|^/(index|home|main)\.?\w*/?$',re.I)
CORR=re.compile(r'safety|recall|리콜|점유율|market\s*share|시장\s*점유|ranking|순위|1위|최대|최초|world.?first|업계\s*최',re.I)
OFFICIAL_HINTS=('.gov','.go.kr','sec.gov','/ir','ir.','investor','.go.jp','europa.eu','.go.uk')
OFFICIAL_TERMS=('official','regulatory','regulator','filing','sec_filing','court','original_dataset','original_data','contracting_party','project_owner','source_owner','research_institution','company_primary','primary_announcement','government','ministry','agency','issuer_release','press_release_owner')
MEDIA_TERMS=('media','news_article','media_article','trade_press','wire','syndication')

def load(p):
    with open(p,encoding='utf-8') as f:return json.load(f)
def host(u):
    if not isinstance(u,str):return ''
    h=urlparse(u).netloc.lower();return h[4:] if h.startswith('www.') else h
def landing(u):
    if not isinstance(u,str) or not u:return True
    try:p=urlparse(u.strip())
    except Exception:return True
    return not p.scheme or not p.netloc or bool(LANDING.match((p.path or '').strip()) and not p.query)
def official_url(u):
    return isinstance(u,str) and any(x in urlparse(u).netloc.lower() or x in u.lower() for x in OFFICIAL_HINTS)
def integer(o,*keys):
    if not isinstance(o,dict):return None
    for k in keys:
        v=o.get(k)
        if isinstance(v,int) and not isinstance(v,bool):return v
    return None
def ledger_owner_count(c):
    rows=c.get('source_independence_ledger') if isinstance(c,dict) else None
    if not isinstance(rows,list):return None
    owners=set();anonymous=0
    for r in rows:
        if not isinstance(r,dict) or r.get('is_independent') is False or r.get('independent') is False:continue
        found=False
        for k in OWNER_FIELDS:
            if r.get(k):owners.add(str(r[k]).strip().lower());found=True;break
        if not found and (r.get('is_independent') is True or r.get('independent') is True):anonymous+=1
    return (len(owners), anonymous) if owners or anonymous else None
def owner_count(c,hosts):
    declared=integer(c,'source_independent_owner_count','independent_owner_count')
    if declared is None:
        declared=integer(c.get('source_diversity_measure'),'source_independent_owner_count','independent_owner_count')
    ledger=ledger_owner_count(c)
    if ledger is not None:
        ledger_named, ledger_anonymous=ledger
        if ledger_named:return ledger_named
        if declared is None:return ledger_anonymous
    if declared is not None:return declared
    return len(hosts)
def metadata(s):
    keys=('source_type','source_kind','source_origin_type','source_role','publisher_type','origin_type','official_source_type','source_category')
    return ' '.join(str(s.get(k,'')).lower() for k in keys if isinstance(s,dict))
def primary(s):
    if not isinstance(s,dict):return False
    if s.get('is_official') is True or s.get('official_source') is True or s.get('is_primary_source') is True:return True
    role=str(s.get('evidence_role') or '').lower()
    if role in {'official_material_evidence','official_source','primary_source','regulatory_filing','original_dataset'}:return True
    blob=metadata(s)
    if any(t in blob for t in MEDIA_TERMS) and not any(t in blob for t in OFFICIAL_TERMS):return False
    return any(t in blob for t in OFFICIAL_TERMS)
def visible(s):
    if not isinstance(s,dict) or s.get('supporting_context_only_not_visible_claim_support') is True:return False
    if s.get('evidence_role') in {'primary_event_evidence','secondary_event_evidence'}:return True
    return isinstance(s.get('supports'),list) and any(x in s['supports'] for x in ('title','sub','gate','fact','implication'))
def exception(c,vs):
    e=c.get('single_source_exception')
    return c.get('source_diversity_status')=='PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION' and isinstance(e,dict) and e.get('allowed') is True and bool(e.get('reason')) and any(primary(s) for s in vs)
def cards(data):
    if isinstance(data,list):return data
    out=[];seen=set()
    if not isinstance(data,dict):return out
    for b in BUCKETS:
        for r in data.get(b,[]) if isinstance(data.get(b),list) else []:
            if not isinstance(r,dict):continue
            m=r.get('id') or r.get('card_id') or r.get('source_spec_id') or r.get('spec_id') or id(r)
            if m in seen:continue
            seen.add(m);x=dict(r);x['__qc_bucket']=b;out.append(x)
    return out

def main():
    if len(sys.argv)!=2:print('usage: evidence_qc_v8_check.py <evidence_qc_output.json>');return 2
    rows=cards(load(sys.argv[1]));names=('landing_page','fake_diversity','weak_corroboration','url_desync','invalid_source_diversity_status','missing_source_discovery_ledger');flags={n:[] for n in names};reuse=[]
    for c in rows:
        cid=c.get('id') or c.get('card_id') or c.get('source_spec_id') or c.get('spec_id') or '<no-id>';bucket=c.get('__qc_bucket');status=c.get('source_diversity_status');fs=c.get('fact_sources') or [];urls=c.get('urls') or []
        source_urls=[s.get('source_url') for s in fs if isinstance(s,dict) and s.get('source_url')];vs=[s for s in fs if visible(s)];vu=[s.get('source_url') for s in vs if s.get('source_url')];unique=len(set(source_urls));visible_unique=len(set(vu));owners=owner_count(c,{host(u) for u in vu if host(u)});ledger=c.get('source_discovery_ledger') or c.get('source_discovery_ledger_ref') or c.get('source_discovery_ledger_reference')
        if status not in ALLOWED:flags['invalid_source_diversity_status'].append((cid,f'missing/invalid source_diversity_status={status}'))
        if bucket in COMPLETE and status in HOLD:flags['invalid_source_diversity_status'].append((cid,f'{status} may not appear in complete bucket {bucket}'))
        if status=='PASS_MULTI_SOURCE':
            if visible_unique<2:flags['invalid_source_diversity_status'].append((cid,f'PASS_MULTI_SOURCE requires >=2 visible source URLs, got {visible_unique}'))
            if owners<2:flags['invalid_source_diversity_status'].append((cid,f'PASS_MULTI_SOURCE requires >=2 independent source owners, got {owners}'))
        if status=='PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION' and not exception(c,vs):flags['invalid_source_diversity_status'].append((cid,'single-source pass exception invalid'))
        if status=='PASS_SINGLE_SOURCE':flags['invalid_source_diversity_status'].append((cid,'PASS_SINGLE_SOURCE is not allowed'))
        for u in source_urls:
            if landing(u):flags['landing_page'].append((cid,u))
        declared_urls=integer(c,'source_unique_url_count','distinct_source_urls');declared_entries=integer(c,'source_evidence_entry_count')
        if declared_urls is not None and declared_urls!=unique:flags['fake_diversity'].append((cid,f'declared source_unique_url_count={declared_urls}, actual={unique}'))
        if declared_entries is not None and declared_entries!=len(fs):flags['fake_diversity'].append((cid,f'declared source_evidence_entry_count={declared_entries}, actual={len(fs)}'))
        if fs and unique<len(fs):reuse.append((cid,f'{len(fs)} claim rows / {unique} canonical URLs'))
        if status in PASS and not ledger:flags['missing_source_discovery_ledger'].append((cid,f'{status} requires source_discovery_ledger/ref'))
        blob=' '.join(str(c.get(k,'')) for k in ('title','sub','gate','fact'));needs=str(c.get('signal','')).lower() in {'top','high'} or bool(CORR.search(blob))
        if needs and owners<2 and not any(official_url(u) for u in set(vu)) and not exception(c,vs):flags['weak_corroboration'].append((cid,f'{owners} independent source owner, no official/primary exception'))
        for u in vu:
            if u not in set(urls):flags['url_desync'].append((cid,u))
    total=sum(len(v) for v in flags.values());print('=== Evidence QC mechanical check ===');print(f'cards checked: {len(rows)}')
    for n in names:
        print(f'  {n}: {len(flags[n])}')
        for cid,d in flags[n][:30]:print(f'      - {cid}: {d}')
        if len(flags[n])>30:print(f'      ... (+{len(flags[n])-30} more)')
    print(f'  claim_row_url_reuse_info: {len(reuse)}')
    for cid,d in reuse[:10]:print(f'      - {cid}: {d}')
    if len(reuse)>10:print(f'      ... (+{len(reuse)-10} more)')
    if total:print(f'RESULT: {total} flag(s) - Evidence QC is NOT pass. Do NOT fabricate sources.');return 1
    print('RESULT: PASS - no evidence QC flags.');return 0
if __name__=='__main__':sys.exit(main())

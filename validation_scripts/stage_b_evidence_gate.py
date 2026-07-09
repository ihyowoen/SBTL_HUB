#!/usr/bin/env python3
"""
R3C_P01 + FIX-004 - Stage B evidence gate.

This gate validates the evidence-before-draft rule without treating a legitimate
`draft_blocked` as a failed `draft_card`.

Rules:
- Every emitted draft_card must have a valid evidence_package with >=1 fetched
  body-level, official-material, or document-level core event source.
- A draft_blocked item does not need a valid evidence_package, but must have a
  populated rescue/source-discovery ledger and blocked/final reason.
- A strict_passed_spec may not disappear silently: every strict spec must map to
  either draft_card or draft_blocked.
"""
import json, re, sys
from urllib.parse import urlparse

LANDING_RE = re.compile(r'^/?$|^/(index|home|main)\.?\w*/?$', re.I)
OK_QUOTE_STATUS = {'body_quote_verified','official_material_quote_verified','document_quote_verified'}
SOURCE_DISCOVERY_LEDGER_KEYS = [
    'source_discovery_ledger',
    'official_source_search_ledger',
    'cited_primary_search_ledger',
    'alternate_source_search_ledger',
]
FORBIDDEN_STAGE_B_TRUE_FLAGS = [
    'accepted_fact_safe',
    'addable_merge_safe',
    'evidence_complete',
    'source_claim_covered',
    'content_enriched',
    'language_terminology_polished',
    'publish_ready',
    'github_merge_ready',
]

def is_landing_page(url):
    if not url or not isinstance(url, str): return True
    try: p=urlparse(url.strip())
    except Exception: return True
    path=(p.path or '').strip()
    return (not p.scheme or not p.netloc) or (LANDING_RE.match(path) and not p.query)

def get(d,*keys,default=None):
    for k in keys:
        if isinstance(d,dict) and k in d and d[k] is not None: return d[k]
    return default

def key(x):
    return get(x,'source_spec_id','spec_id','id','story_id','key',default='<unknown>')

def listify(x):
    if isinstance(x,list): return x
    if isinstance(x,dict): return list(x.values())
    return []

def evidence_ok(ep, row=None, root=None):
    if not isinstance(ep,dict): return False, ['missing evidence_package']
    issues=[]
    srcs=[]
    for k in ['sources','fetched_sources','body_sources','fact_source_candidates','fact_sources']:
        v=ep.get(k)
        if isinstance(v,list): srcs += v
    if not srcs: issues.append('no source list in evidence_package')
    discovery_rows = []
    for scope in (ep, row, root):
        if not isinstance(scope, dict):
            continue
        for k in SOURCE_DISCOVERY_LEDGER_KEYS:
            if isinstance(scope.get(k), list):
                discovery_rows += scope.get(k)
    discovery_disabled = (
        ep.get('external_source_discovery_disabled_by_user') is True
        or (isinstance(row, dict) and row.get('external_source_discovery_disabled_by_user') is True)
        or (isinstance(root, dict) and root.get('external_source_discovery_disabled_by_user') is True)
    )
    if not discovery_rows and not discovery_disabled:
        issues.append('missing source_discovery/official/cited/alternate search ledger')
    status = ep.get('source_discovery_status') or ((row or {}).get('source_discovery_status') if isinstance(row, dict) else None)
    if status in (None, '', 'not_checked'):
        issues.append('missing source_discovery_status')
    good=0
    good_urls=set()
    for s in srcs:
        if not isinstance(s,dict): continue
        u=s.get('source_url') or s.get('url')
        fetched=bool(s.get('fetched') or s.get('fetched_at') or s.get('checked_at') or s.get('body') or s.get('body_text') or s.get('source_quote'))
        quote_status=s.get('source_quote_status') or s.get('quote_status')
        quote=bool(s.get('source_quote') or s.get('quote'))
        if fetched and quote and (quote_status in OK_QUOTE_STATUS or s.get('evidence_role')=='primary_event_evidence') and not is_landing_page(u):
            good += 1
            good_urls.add(u)
    if good < 1: issues.append('no fetched body/official/document-level core source with quote')
    if len(good_urls) <= 1:
        exc = ep.get('single_source_exception') or ((row or {}).get('single_source_exception') if isinstance(row, dict) else None)
        if not isinstance(exc, dict) or exc.get('allowed') is not True or not exc.get('reason'):
            issues.append('single-source evidence package missing explicit single_source_exception.allowed/reason')
    return (len(issues)==0), issues

def blocked_ok(b):
    ledgers=[]
    for k in ['source_discovery_ledger','fetch_attempt_ledger','fetch_ledger','rescue_attempt_log','official_source_search_ledger','alternate_source_search_ledger','cited_primary_search_ledger']:
        v=b.get(k)
        if isinstance(v,list): ledgers += v
    rescue=b.get('rescue_attempted') is True or len(ledgers)>0
    reason=(
        b.get('final_hold_or_reject_reason')
        or b.get('blocked_reason')
        or b.get('blocked_source_reason')
        or b.get('draft_blocked_reason')
        or b.get('reason')
    )
    status_ok = b.get('source_discovery_status') in ('completed_no_verified_source', 'incomplete', 'completed_verified_source_found')
    return bool(rescue and ledgers and reason and status_ok), {'rescue':rescue,'ledger_count':len(ledgers),'reason':bool(reason),'source_discovery_status':b.get('source_discovery_status')}

def forbidden_state_flags(row):
    found = []
    if not isinstance(row, dict):
        return found
    for field in FORBIDDEN_STAGE_B_TRUE_FLAGS:
        if row.get(field) is True:
            found.append(field)
        if row.get('state') == field:
            found.append('state=' + field)
    return found

def main():
    if len(sys.argv)<2:
        print('usage: stage_b_evidence_gate.py <stage_b_output.json>'); return 2
    data=json.load(open(sys.argv[1],encoding='utf-8'))
    strict=listify(get(data,'strict_passed_spec','strict_passed_specs',default=[]))
    cards=listify(get(data,'draft_cards','cards','revised_draft_cards',default=[]))
    blocked=listify(get(data,'draft_blocked','blocked_specs',default=[]))
    ep_raw=get(data,'evidence_packages','evidence_package',default=[])
    ep_index={}
    if isinstance(ep_raw,dict): ep_index.update(ep_raw)
    for ep in listify(ep_raw):
        if isinstance(ep,dict): ep_index[key(ep)]=ep
    problems=[]; warnings=[]; card_keys=set(); blocked_keys=set()
    for c in cards:
        ck=key(c); card_keys.add(ck)
        bad_flags = forbidden_state_flags(c)
        if bad_flags:
            problems.append(f'draft_card {ck}: Stage B must not set downstream state flags {bad_flags}')
        if c.get('stage_a_strict_pass_gate_missing') is True:
            problems.append(f'draft_card {ck}: stage_a_strict_pass_gate_missing true is invalid in v13')
        ep=ep_index.get(ck) or c.get('evidence_package')
        ok,issues=evidence_ok(ep, c, data)
        if not ok: problems.append(f'draft_card {ck}: '+ '; '.join(issues))
    for b in blocked:
        bk=key(b); blocked_keys.add(bk)
        bad_flags = forbidden_state_flags(b)
        if bad_flags:
            problems.append(f'draft_blocked {bk}: Stage B must not set downstream state flags {bad_flags}')
        if b.get('stage_a_strict_pass_gate_missing') is True:
            problems.append(f'draft_blocked {bk}: stage_a_strict_pass_gate_missing true is invalid in v13')
        ok,info=blocked_ok(b)
        if not ok: problems.append(f'draft_blocked {bk}: missing rescue/source-discovery ledger or final reason {info}')
    strict_keys={key(s) for s in strict}
    missing=strict_keys - card_keys - blocked_keys
    if missing: problems.append('strict specs silently missing from draft_cards/draft_blocked: '+', '.join(sorted(missing)))
    print('=== Stage B evidence gate FIX-004 ===')
    print(f'strict_passed_spec : {len(strict)}')
    print(f'draft_cards        : {len(cards)}')
    print(f'draft_blocked      : {len(blocked)}')
    print(f'problems           : {len(problems)}')
    if problems:
        for p in problems[:100]: print('-',p)
        print('RESULT: BLOCKED_STAGE_B_EVIDENCE_OR_BLOCKED_LEDGER_INVALID')
        return 1
    print('RESULT: PASS_STAGE_B_EVIDENCE_GATE')
    return 0
if __name__=='__main__': sys.exit(main())

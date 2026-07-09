#!/usr/bin/env python3
"""
Stage lineage contract conformance check.

Usage:
  python validation_scripts/stage_lineage_contract_check.py stage_a <stage_a_results.json>
  python validation_scripts/stage_lineage_contract_check.py stage_b <stage_b_results.json>
  python validation_scripts/stage_lineage_contract_check.py stage_c <stage_c_results.json>
"""
import json, sys

A_FIELDS = [
    'spec_id','source_story_ids','strict_pass_gate','enhanced_selector_precision_version',
    'selector_policy_version','strict_gate_check','format_risk_tags','execution_anchor_type',
    'execution_anchor_strength','baseline_relation','duplicate_risk','staleness_decision',
    'source_access_risk','stage_a_evidence_status','stage_b_evidence_package_required',
    'primary_url_semantics'
]
B_FIELDS = [
    'lineage_integrity_status','stage_a_validity_guard_applied',
    'strict_gate_metadata_preserved','execution_anchor_metadata_preserved',
    'superseded_lineage_mixed','manual_integrated_rule_mixed','previous_run_output_mixed'
]
C_ITEM_FIELDS = [
    'id',
    'spec_id',
    'source_story_ids',
    'stage_b_lineage',
    'strict_gate_acceptance_guard_applied',
    'accepted_pool_lineage_status',
]
REVIEW_POOLS = [
    'candidate_review_pool',
    'watchlist_context_pool',
    'reject_or_support_only_pool',
    'review_pool',
]
HARD_REJECT_BASES = {
    'out_of_scope',
    'consumer_noise',
    'local_noise',
    'duplicate_without_incremental_value',
    'stale_without_fresh_angle',
    'source_broken_unrecoverable',
    'generic_keyword_only',
    'not_sbtl_lane',
}
STAGE_C_FORBIDDEN_TRUE_FLAGS = [
    'addable_merge_safe',
    'evidence_complete',
    'source_claim_covered',
    'content_enriched',
    'language_terminology_polished',
    'publish_ready',
    'github_merge_ready',
]
ACCEPTED_STAGE_C_POOLS = {'accepted_fact_safe', 'accepted_fact_safe_with_warnings'}


def load(path):
    with open(path, encoding='utf-8') as f: return json.load(f)


def fail(msgs):
    print('RESULT: BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT')
    for m in msgs[:100]: print('-', m)
    if len(msgs)>100: print(f'... +{len(msgs)-100} more')
    return 1


def item_key(item):
    if not isinstance(item, dict):
        return ''
    for key in ['review_pool_item_id', 'story_id', 'spec_id', 'id']:
        value = item.get(key)
        if value:
            return str(value)
    grouped = item.get('grouped_story_ids') or item.get('source_story_ids')
    if isinstance(grouped, list) and grouped:
        return '|'.join(str(x) for x in grouped if x)
    return ''


def missing_or_empty(item, field):
    return field not in item or item.get(field) in (None, '', [])


def check_stage_a(data):
    specs = data.get('strict_passed_spec') or data.get('strict_passed_specs') or []
    msgs=[]
    for i,s in enumerate(specs):
        sid=s.get('spec_id', f'idx_{i}')
        for f in A_FIELDS:
            if f not in s or s.get(f) in (None,''):
                msgs.append(f'{sid}: missing {f}')
        sg=s.get('strict_pass_gate') or {}
        if not isinstance(sg, dict):
            msgs.append(f'{sid}: strict_pass_gate not object')
        else:
            for f in ['status','reason','all_six_conditions_passed']:
                if f not in sg:
                    msgs.append(f'{sid}: strict_pass_gate missing {f}')
        if s.get('stage_a_evidence_status') not in (None,'not_evidence_complete_no_fetch'):
            msgs.append(f'{sid}: invalid stage_a_evidence_status={s.get("stage_a_evidence_status")}')
        if s.get('primary_url_semantics') not in (None,'provided_source_candidate_not_evidence'):
            msgs.append(f'{sid}: invalid primary_url_semantics={s.get("primary_url_semantics")}')
    if 'review_pool_partition_summary' not in data:
        msgs.append('top-level missing review_pool_partition_summary')

    review_items = []
    for pool in REVIEW_POOLS:
        rows = data.get(pool)
        if isinstance(rows, list):
            review_items.extend((pool, row) for row in rows if isinstance(row, dict))

    if review_items:
        if data.get('review_pool_carry_forward_ledger_status') != 'PASS':
            msgs.append('top-level review_pool_carry_forward_ledger_status must be PASS when review pools exist')
        ledger = data.get('review_pool_resolution_ledger')
        if not isinstance(ledger, list) or not ledger:
            msgs.append('top-level review_pool_resolution_ledger[] missing or empty while review pools exist')
            ledger_keys = set()
        else:
            ledger_keys = {item_key(row) for row in ledger if isinstance(row, dict)}

        for pool, row in review_items:
            key = item_key(row)
            if not key:
                msgs.append(f'{pool}: item missing review_pool_item_id/story_id/spec_id')
            elif key not in ledger_keys:
                msgs.append(f'{pool} {key}: missing review_pool_resolution_ledger row')
            if pool in ('candidate_review_pool', 'review_pool'):
                for field in ['promotion_precondition', 'bounded_review_question', 'recommended_next_action']:
                    if not row.get(field):
                        msgs.append(f'{pool} {key or "unknown"}: missing {field}')

    rejected = data.get('rejected') if isinstance(data.get('rejected'), list) else []
    for row in rejected:
        if not isinstance(row, dict):
            continue
        key = item_key(row) or 'unknown'
        basis = row.get('hard_reject_basis')
        if basis not in HARD_REJECT_BASES:
            msgs.append(f'rejected {key}: invalid/missing hard_reject_basis')
        if row.get('hard_reject_confidence') != 'high':
            msgs.append(f'rejected {key}: hard_reject_confidence must be high')
        if row.get('hard_reject_positive_test_passed') is not True:
            msgs.append(f'rejected {key}: hard_reject_positive_test_passed must be true')
        if row.get('hard_reject_anti_overclosure_check') != 'PASS':
            msgs.append(f'rejected {key}: hard_reject_anti_overclosure_check must be PASS')
        if not row.get('why_not_review_pool'):
            msgs.append(f'rejected {key}: missing why_not_review_pool')

    if data.get('strict_passed_via_p_013_count') not in (None, 0):
        msgs.append('strict_passed_via_p_013_count must be 0; P_013 auto-promotion is deprecated')
    return fail(msgs) if msgs else (print('RESULT: PASS_STAGE_A_SCHEMA_CONTRACT'),0)[1]


def check_stage_b(data):
    msgs=[]
    expected_values = {
        'lineage_integrity_status': 'PASS',
        'stage_a_validity_guard_applied': True,
        'strict_gate_metadata_preserved': True,
        'execution_anchor_metadata_preserved': True,
        'superseded_lineage_mixed': False,
        'manual_integrated_rule_mixed': False,
        'previous_run_output_mixed': False,
    }
    for f in B_FIELDS:
        if f not in data:
            msgs.append(f'top-level missing {f}')
            continue
        actual = data.get(f)
        expected = expected_values.get(f)
        if actual != expected:
            msgs.append(f'top-level {f} must be {expected!r}, got {actual!r}')
    return fail(msgs) if msgs else (print('RESULT: PASS_STAGE_B_SCHEMA_CONTRACT'),0)[1]


def check_stage_c(data):
    pools=[]
    for name in ['accepted_fact_safe','revise_required','rejected','support_source_only','deferred_review_pool','accepted_fact_safe_with_warnings']:
        v=data.get(name)
        if isinstance(v, list): pools += [(name,x) for x in v]
    msgs=[]
    for pool,item in pools:
        cid=item.get('id')
        if not cid:
            msgs.append(f'{pool}: item missing id for spec/story {item.get("spec_id") or item.get("source_story_ids")}')
        for field in C_ITEM_FIELDS:
            if missing_or_empty(item, field):
                msgs.append(f'{pool} {cid or "unknown"}: missing {field}')
        if pool in ACCEPTED_STAGE_C_POOLS:
            if item.get('strict_gate_acceptance_guard_applied') is not True:
                msgs.append(f'{pool} {cid or "unknown"}: strict_gate_acceptance_guard_applied must be true')
            if item.get('accepted_pool_lineage_status') != 'PASS':
                msgs.append(f'{pool} {cid or "unknown"}: accepted_pool_lineage_status must be PASS')
            if item.get('state') != 'accepted_fact_safe':
                msgs.append(f'{pool} {cid or "unknown"}: state must be accepted_fact_safe')
            if item.get('stage_c_only') is not True:
                msgs.append(f'{pool} {cid or "unknown"}: stage_c_only must be true')
            for flag in STAGE_C_FORBIDDEN_TRUE_FLAGS:
                if item.get(flag) is True:
                    msgs.append(f'{pool} {cid or "unknown"}: Stage C must not set downstream flag {flag}=true')
                if item.get('state') == flag:
                    msgs.append(f'{pool} {cid or "unknown"}: Stage C must not use downstream state {flag}')
    return fail(msgs) if msgs else (print('RESULT: PASS_STAGE_C_SCHEMA_CONTRACT'),0)[1]


def main():
    if len(sys.argv)!=3:
        print(__doc__); return 2
    stage,path=sys.argv[1],sys.argv[2]
    data=load(path)
    if stage=='stage_a': return check_stage_a(data)
    if stage=='stage_b': return check_stage_b(data)
    if stage=='stage_c': return check_stage_c(data)
    print('unknown stage'); return 2
if __name__=='__main__': sys.exit(main())

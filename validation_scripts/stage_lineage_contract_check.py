#!/usr/bin/env python3
"""
Stage lineage contract conformance check.

Usage:
  python validation_scripts/stage_lineage_contract_check.py stage_a <stage_a_results.json>
  python validation_scripts/stage_lineage_contract_check.py stage_b <stage_b_results.json>
  python validation_scripts/stage_lineage_contract_check.py stage_c <stage_c_results.json>
"""
import json
import sys

A_FIELDS = [
    'spec_id', 'source_story_ids', 'strict_pass_gate',
    'enhanced_selector_precision_version', 'selector_policy_version',
    'strict_gate_check', 'format_risk_tags', 'execution_anchor_type',
    'execution_anchor_strength', 'baseline_relation', 'duplicate_risk',
    'staleness_decision', 'source_access_risk', 'stage_a_evidence_status',
    'stage_b_evidence_package_required', 'primary_url_semantics'
]
B_EXPECTED_VALUES = {
    'lineage_integrity_status': 'PASS',
    'stage_a_validity_guard_applied': True,
    'strict_gate_metadata_preserved': True,
    'execution_anchor_metadata_preserved': True,
    'superseded_lineage_mixed': False,
    'manual_integrated_rule_mixed': False,
    'previous_run_output_mixed': False,
}
B_SOURCE_DIVERSITY_FIELDS = [
    'stage_a_support_sources_attempted',
    'source_independence_ledger',
    'source_unique_url_count',
    'source_unique_domain_count',
    'source_independent_owner_count',
    'source_role_coverage',
    'source_synthesis_plan',
]
B_SOURCE_DIVERSITY_INTEGER_FIELDS = {
    'source_unique_url_count',
    'source_unique_domain_count',
    'source_independent_owner_count',
}
C_ITEM_FIELDS = [
    'id', 'spec_id', 'source_story_ids', 'stage_b_lineage',
    'strict_gate_acceptance_guard_applied', 'accepted_pool_lineage_status'
]
C_SOURCE_DIVERSITY_FIELDS = [
    'source_diversity_status',
    'source_diversity_measure',
    'source_diversity_roles',
    'source_synthesis_applied',
    'source_synthesis_fields',
    'source_synthesis_audit',
    'single_source_exception',
    'source_published_date',
    'visible_quote_date',
]
REVIEW_POOLS = [
    'candidate_review_pool', 'watchlist_context_pool',
    'reject_or_support_only_pool', 'review_pool'
]
HARD_REJECT_BASES = {
    'out_of_scope', 'consumer_noise', 'local_noise',
    'duplicate_without_incremental_value', 'stale_without_fresh_angle',
    'source_broken_unrecoverable', 'generic_keyword_only', 'not_sbtl_lane'
}
ACCEPTED_STAGE_C_POOLS = {'accepted_fact_safe', 'accepted_fact_safe_with_warnings'}
STAGE_C_FORBIDDEN_TRUE_FLAGS = {
    'addable_merge_safe', 'evidence_complete', 'source_claim_covered',
    'content_enriched', 'language_terminology_polished', 'publish_ready',
    'github_merge_ready'
}


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def fail(messages):
    print('RESULT: BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT')
    for message in messages[:100]:
        print('-', message)
    if len(messages) > 100:
        print(f'... +{len(messages) - 100} more')
    return 1


def missing_or_empty(obj, field):
    return field not in obj or obj.get(field) in (None, '', [])


def item_key(item):
    if not isinstance(item, dict):
        return ''
    for key in ('review_pool_item_id', 'source_spec_id', 'story_id', 'spec_id', 'id'):
        value = item.get(key)
        if value:
            return str(value)
    grouped = item.get('grouped_story_ids') or item.get('source_story_ids')
    if isinstance(grouped, list) and grouped:
        return '|'.join(str(x) for x in grouped if x)
    return ''


def as_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    return []


def evidence_packages(data):
    raw = data.get('evidence_packages') or data.get('evidence_package') or []
    return [row for row in as_list(raw) if isinstance(row, dict)]


def has_review_items(data):
    for pool in REVIEW_POOLS:
        rows = data.get(pool)
        if isinstance(rows, list) and rows:
            return True
    return False


def validate_source_diversity_field(scope, field, label, messages):
    if field not in scope:
        messages.append(f'{label}: missing source-diversity lineage field {field}')
        return
    value = scope.get(field)
    if field == 'stage_a_support_sources_attempted':
        if not isinstance(value, (list, bool)):
            messages.append(f'{label}: {field} must be a support-attempt ledger array or boolean compatibility flag')
    elif field in B_SOURCE_DIVERSITY_INTEGER_FIELDS and not isinstance(value, int):
        messages.append(f'{label}: {field} must be integer')
    elif field not in B_SOURCE_DIVERSITY_INTEGER_FIELDS and value in (None, '', [], {}):
        messages.append(f'{label}: {field} must be populated')


def has_any_source_diversity_field(scope):
    return isinstance(scope, dict) and any(field in scope for field in B_SOURCE_DIVERSITY_FIELDS)


def check_stage_a(data):
    messages = []
    specs = data.get('strict_passed_spec') or data.get('strict_passed_specs') or []
    for index, spec in enumerate(specs):
        spec_id = spec.get('spec_id', f'idx_{index}')
        for field in A_FIELDS:
            if field == 'format_risk_tags':
                if field not in spec or spec.get(field) is None:
                    messages.append(f'{spec_id}: missing {field}')
                elif not isinstance(spec.get(field), list):
                    messages.append(f'{spec_id}: format_risk_tags must be a list, including [] when no tags apply')
            elif missing_or_empty(spec, field):
                messages.append(f'{spec_id}: missing {field}')
        gate = spec.get('strict_pass_gate') or {}
        if not isinstance(gate, dict):
            messages.append(f'{spec_id}: strict_pass_gate not object')
        else:
            for field in ('status', 'reason', 'all_six_conditions_passed'):
                if field not in gate:
                    messages.append(f'{spec_id}: strict_pass_gate missing {field}')
            if gate.get('status') != 'pass':
                messages.append(f'{spec_id}: strict_pass_gate.status must be pass for strict_passed_spec[]')
            if gate.get('all_six_conditions_passed') is not True:
                messages.append(f'{spec_id}: strict_pass_gate.all_six_conditions_passed must be true for strict_passed_spec[]')
            if not gate.get('reason'):
                messages.append(f'{spec_id}: strict_pass_gate.reason must be populated')
        if spec.get('stage_a_evidence_status') not in (None, 'not_evidence_complete_no_fetch'):
            messages.append(f'{spec_id}: invalid stage_a_evidence_status={spec.get("stage_a_evidence_status")}')
        if spec.get('primary_url_semantics') not in (None, 'provided_source_candidate_not_evidence'):
            messages.append(f'{spec_id}: invalid primary_url_semantics={spec.get("primary_url_semantics")}')

    if has_review_items(data):
        if 'review_pool_partition_summary' not in data:
            messages.append('top-level missing review_pool_partition_summary when review pools exist')
        if data.get('review_pool_carry_forward_ledger_status') != 'PASS':
            messages.append('top-level review_pool_carry_forward_ledger_status must be PASS when review pools exist')
        ledger = data.get('review_pool_resolution_ledger')
        ledger_keys = {item_key(row) for row in ledger} if isinstance(ledger, list) else set()
        if not ledger_keys:
            messages.append('top-level review_pool_resolution_ledger[] missing or empty while review pools exist')
        for pool in REVIEW_POOLS:
            for row in data.get(pool, []) if isinstance(data.get(pool), list) else []:
                key = item_key(row)
                if not key:
                    messages.append(f'{pool}: item missing review_pool_item_id/story_id/spec_id')
                elif key not in ledger_keys:
                    messages.append(f'{pool} {key}: missing review_pool_resolution_ledger row')
                if pool in ('candidate_review_pool', 'review_pool'):
                    for field in ('promotion_precondition', 'bounded_review_question', 'recommended_next_action'):
                        if not row.get(field):
                            messages.append(f'{pool} {key or "unknown"}: missing {field}')

    for row in data.get('rejected', []) if isinstance(data.get('rejected'), list) else []:
        key = item_key(row) or 'unknown'
        if row.get('hard_reject_basis') not in HARD_REJECT_BASES:
            messages.append(f'rejected {key}: invalid/missing hard_reject_basis')
        if row.get('hard_reject_confidence') != 'high':
            messages.append(f'rejected {key}: hard_reject_confidence must be high')
        if row.get('hard_reject_positive_test_passed') is not True:
            messages.append(f'rejected {key}: hard_reject_positive_test_passed must be true')
        if row.get('hard_reject_anti_overclosure_check') != 'PASS':
            messages.append(f'rejected {key}: hard_reject_anti_overclosure_check must be PASS')
        if not row.get('why_not_review_pool'):
            messages.append(f'rejected {key}: missing why_not_review_pool')

    if data.get('strict_passed_via_p_013_count') not in (None, 0):
        messages.append('strict_passed_via_p_013_count must be 0; P_013 auto-promotion is deprecated')
    return fail(messages) if messages else (print('RESULT: PASS_STAGE_A_SCHEMA_CONTRACT'), 0)[1]


def check_stage_b(data):
    messages = []
    for field, expected in B_EXPECTED_VALUES.items():
        if field not in data:
            messages.append(f'top-level missing {field}')
        elif data.get(field) != expected:
            messages.append(f'top-level {field} must be {expected!r}, got {data.get(field)!r}')

    packages = evidence_packages(data)
    if packages:
        for index, package in enumerate(packages):
            label = f'evidence_package[{item_key(package) or index}]'
            for field in B_SOURCE_DIVERSITY_FIELDS:
                validate_source_diversity_field(package, field, label, messages)
    elif has_any_source_diversity_field(data):
        for field in B_SOURCE_DIVERSITY_FIELDS:
            validate_source_diversity_field(data, field, 'top-level', messages)
    else:
        for field in B_SOURCE_DIVERSITY_FIELDS:
            messages.append(f'top-level/evidence_packages missing source-diversity lineage field {field}')

    return fail(messages) if messages else (print('RESULT: PASS_STAGE_B_SCHEMA_CONTRACT'), 0)[1]


def check_stage_c(data):
    messages = []
    pools = []
    for pool in ('accepted_fact_safe', 'accepted_fact_safe_with_warnings', 'revise_required', 'rejected', 'support_source_only', 'deferred_review_pool'):
        rows = data.get(pool)
        if isinstance(rows, list):
            pools.extend((pool, row) for row in rows if isinstance(row, dict))

    for pool, item in pools:
        card_id = item.get('id') or 'unknown'
        for field in C_ITEM_FIELDS:
            if missing_or_empty(item, field):
                messages.append(f'{pool} {card_id}: missing {field}')
        for field in C_SOURCE_DIVERSITY_FIELDS:
            if missing_or_empty(item, field):
                messages.append(f'{pool} {card_id}: missing source-diversity lineage field {field}')
        if pool in ACCEPTED_STAGE_C_POOLS:
            if item.get('strict_gate_acceptance_guard_applied') is not True:
                messages.append(f'{pool} {card_id}: strict_gate_acceptance_guard_applied must be true')
            if item.get('accepted_pool_lineage_status') != 'PASS':
                messages.append(f'{pool} {card_id}: accepted_pool_lineage_status must be PASS')
            if item.get('state') != 'accepted_fact_safe':
                messages.append(f'{pool} {card_id}: state must be accepted_fact_safe')
            if item.get('stage_c_only') is not True:
                messages.append(f'{pool} {card_id}: stage_c_only must be true')
            for flag in STAGE_C_FORBIDDEN_TRUE_FLAGS:
                if item.get(flag) is True:
                    messages.append(f'{pool} {card_id}: Stage C must not set downstream flag {flag}=true')
                if item.get('state') == flag:
                    messages.append(f'{pool} {card_id}: Stage C must not use downstream state {flag}')
    return fail(messages) if messages else (print('RESULT: PASS_STAGE_C_SCHEMA_CONTRACT'), 0)[1]


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    stage, path = sys.argv[1], sys.argv[2]
    data = load(path)
    if stage == 'stage_a':
        return check_stage_a(data)
    if stage == 'stage_b':
        return check_stage_b(data)
    if stage == 'stage_c':
        return check_stage_c(data)
    print('unknown stage')
    return 2


if __name__ == '__main__':
    sys.exit(main())

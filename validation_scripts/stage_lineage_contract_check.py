#!/usr/bin/env python3
"""Contract-driven Stage A/B/C lineage validator.

Usage:
  python validation_scripts/stage_lineage_contract_check.py stage_a <stage_a.json>
  python validation_scripts/stage_lineage_contract_check.py stage_b <stage_b.json>
  python validation_scripts/stage_lineage_contract_check.py stage_c <stage_c.json>
"""
import json
import sys

STAGE_A_REQUIRED = [
    'spec_id', 'source_story_ids', 'strict_pass_gate',
    'enhanced_selector_precision_version', 'selector_policy_version',
    'strict_gate_check', 'format_risk_tags', 'execution_anchor_type',
    'execution_anchor_strength', 'baseline_relation', 'duplicate_risk',
    'staleness_decision', 'source_access_risk', 'stage_a_evidence_status',
    'stage_b_evidence_package_required', 'primary_url_semantics',
]
STAGE_A_SOURCE_DIVERSITY_REQUIRED = [
    'same_event_source_cluster', 'support_source_candidates',
    'source_domain_candidates', 'source_diversity_path', 'source_cluster_preserved',
]
STAGE_A_PRESENCE_ONLY = {'format_risk_tags', 'support_source_candidates', 'source_domain_candidates'}
STAGE_A_GATE_REQUIRED = ['status', 'reason', 'all_six_conditions_passed']
STAGE_A_ALLOWED_STAGE_EVIDENCE_STATUS = {'not_evidence_complete_no_fetch'}
STAGE_A_ALLOWED_PRIMARY_URL_SEMANTICS = {'provided_source_candidate_not_evidence'}
STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH = {'strong', 'moderate'}

STAGE_B_EXPECTED_TOP_LEVEL = {
    'lineage_integrity_status': 'PASS',
    'stage_a_validity_guard_applied': True,
    'strict_gate_metadata_preserved': True,
    'execution_anchor_metadata_preserved': True,
    'superseded_lineage_mixed': False,
    'manual_integrated_rule_mixed': False,
    'previous_run_output_mixed': False,
}
STAGE_B_SOURCE_DIVERSITY_REQUIRED = [
    'stage_a_support_sources_attempted',
    'source_independence_ledger',
    'source_unique_url_count',
    'source_unique_domain_count',
    'source_independent_owner_count',
    'source_role_coverage',
    'source_synthesis_plan',
]
STAGE_B_INTEGER_FIELDS = {'source_unique_url_count', 'source_unique_domain_count', 'source_independent_owner_count'}

STAGE_C_BASE_REQUIRED = [
    'id', 'spec_id', 'source_story_ids', 'stage_b_lineage',
    'strict_gate_acceptance_guard_applied', 'accepted_pool_lineage_status',
]
STAGE_C_SOURCE_DIVERSITY_REQUIRED = [
    'source_diversity_status', 'source_diversity_measure',
    'source_diversity_roles', 'source_synthesis_applied',
    'source_synthesis_fields', 'source_synthesis_audit',
    'single_source_exception', 'source_published_date', 'visible_quote_date',
]
STAGE_C_ACCEPTED_POOLS = {'accepted_fact_safe', 'accepted_fact_safe_with_warnings'}
STAGE_C_POOLS = [
    'accepted_fact_safe', 'accepted_fact_safe_with_warnings', 'revise_required',
    'rejected', 'support_source_only', 'deferred_review_pool', 'review_pool_deferred',
]
STAGE_C_FORBIDDEN_TRUE_FLAGS = {
    'addable_merge_safe', 'evidence_complete', 'source_claim_covered',
    'content_enriched', 'language_terminology_polished', 'publish_ready',
    'github_merge_ready',
}

REVIEW_POOLS = ['candidate_review_pool', 'watchlist_context_pool', 'reject_or_support_only_pool', 'review_pool']
HARD_REJECT_BASES = {
    'out_of_scope', 'consumer_noise', 'local_noise', 'duplicate_without_incremental_value',
    'stale_without_fresh_angle', 'source_broken_unrecoverable', 'generic_keyword_only',
    'not_sbtl_lane',
}


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def as_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    return []


def item_key(item):
    if not isinstance(item, dict):
        return ''
    for key in ('review_pool_item_id', 'source_spec_id', 'story_id', 'spec_id', 'id'):
        if item.get(key):
            return str(item[key])
    grouped = item.get('grouped_story_ids') or item.get('source_story_ids')
    if isinstance(grouped, list) and grouped:
        return '|'.join(str(x) for x in grouped if x)
    return ''


def missing_presence(obj, field):
    return not isinstance(obj, dict) or field not in obj


def missing_nonempty(obj, field):
    return missing_presence(obj, field) or obj.get(field) in (None, '', [], {})


def fail(messages):
    print('RESULT: BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT')
    for message in messages[:120]:
        print('-', message)
    if len(messages) > 120:
        print(f'... +{len(messages) - 120} more')
    return 1


def stage_a_specs(data):
    return as_list(data.get('strict_passed_spec') or data.get('strict_passed_specs') or [])


def validate_stage_a_source_diversity(spec, spec_id, messages):
    for field in STAGE_A_SOURCE_DIVERSITY_REQUIRED:
        if field in STAGE_A_PRESENCE_ONLY:
            if missing_presence(spec, field):
                messages.append(f'{spec_id}: missing source-diversity lineage field {field}')
        elif missing_nonempty(spec, field):
            messages.append(f'{spec_id}: missing source-diversity lineage field {field}')

    path = spec.get('source_diversity_path')
    if not isinstance(path, dict) or not path.get('status'):
        messages.append(f'{spec_id}: source_diversity_path.status is required')

    if spec.get('source_cluster_preserved') is not True:
        messages.append(f'{spec_id}: source_cluster_preserved must be true for strict_passed_spec')


def validate_stage_a_spec(spec, index, messages):
    spec_id = spec.get('spec_id', f'idx_{index}') if isinstance(spec, dict) else f'idx_{index}'
    if not isinstance(spec, dict):
        messages.append(f'{spec_id}: spec row is not object')
        return

    for field in STAGE_A_REQUIRED:
        missing = missing_presence(spec, field) if field in STAGE_A_PRESENCE_ONLY else missing_nonempty(spec, field)
        if missing:
            messages.append(f'{spec_id}: missing {field}')

    validate_stage_a_source_diversity(spec, spec_id, messages)

    gate = spec.get('strict_pass_gate')
    if not isinstance(gate, dict):
        messages.append(f'{spec_id}: strict_pass_gate not object')
        return
    for field in STAGE_A_GATE_REQUIRED:
        if field not in gate:
            messages.append(f'{spec_id}: strict_pass_gate missing {field}')
    if gate.get('status') != 'pass':
        messages.append(f'{spec_id}: strict_pass_gate.status must be pass')
    if gate.get('all_six_conditions_passed') is not True:
        messages.append(f'{spec_id}: strict_pass_gate.all_six_conditions_passed must be true')

    if spec.get('stage_a_evidence_status') not in STAGE_A_ALLOWED_STAGE_EVIDENCE_STATUS:
        messages.append(f'{spec_id}: invalid stage_a_evidence_status={spec.get("stage_a_evidence_status")}')
    if spec.get('primary_url_semantics') not in STAGE_A_ALLOWED_PRIMARY_URL_SEMANTICS:
        messages.append(f'{spec_id}: invalid primary_url_semantics={spec.get("primary_url_semantics")}')
    if spec.get('execution_anchor_strength') not in STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH:
        messages.append(f'{spec_id}: execution_anchor_strength must be strong or moderate for strict_passed_spec')


def has_review_items(data):
    return any(isinstance(data.get(pool), list) and data.get(pool) for pool in REVIEW_POOLS)


def validate_review_pools(data, messages):
    if not has_review_items(data):
        return
    if 'review_pool_partition_summary' not in data:
        messages.append('top-level missing review_pool_partition_summary when review pools exist')
    if data.get('review_pool_carry_forward_ledger_status') != 'PASS':
        messages.append('review_pool_carry_forward_ledger_status must be PASS when review pools exist')
    ledger = data.get('review_pool_resolution_ledger')
    ledger_keys = {item_key(row) for row in ledger} if isinstance(ledger, list) else set()
    if not ledger_keys:
        messages.append('review_pool_resolution_ledger[] missing or empty when review pools exist')
    for pool in REVIEW_POOLS:
        for row in as_list(data.get(pool)):
            key = item_key(row)
            if not key:
                messages.append(f'{pool}: item missing review_pool_item_id/story_id/spec_id')
            elif key not in ledger_keys:
                messages.append(f'{pool} {key}: missing review_pool_resolution_ledger row')
            if pool in ('candidate_review_pool', 'review_pool'):
                for field in ('promotion_precondition', 'bounded_review_question', 'recommended_next_action'):
                    if missing_nonempty(row, field):
                        messages.append(f'{pool} {key or "unknown"}: missing {field}')


def check_stage_a(data):
    messages = []
    for index, spec in enumerate(stage_a_specs(data)):
        validate_stage_a_spec(spec, index, messages)
    validate_review_pools(data, messages)
    for row in as_list(data.get('rejected')):
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
    if messages:
        return fail(messages)
    print('RESULT: PASS_STAGE_A_SCHEMA_CONTRACT')
    return 0


def evidence_packages(data):
    raw = data.get('evidence_packages') or data.get('evidence_package') or []
    return [row for row in as_list(raw) if isinstance(row, dict)]


def has_any_source_diversity_field(scope):
    return isinstance(scope, dict) and any(field in scope for field in STAGE_B_SOURCE_DIVERSITY_REQUIRED)


def validate_stage_b_source_diversity(scope, label, messages):
    for field in STAGE_B_SOURCE_DIVERSITY_REQUIRED:
        if field not in scope:
            messages.append(f'{label}: missing source-diversity lineage field {field}')
            continue
        value = scope.get(field)
        if field in STAGE_B_INTEGER_FIELDS:
            if not isinstance(value, int):
                messages.append(f'{label}: {field} must be integer')
        elif field == 'stage_a_support_sources_attempted':
            if not isinstance(value, (list, bool)):
                messages.append(f'{label}: {field} must be ledger array or boolean compatibility flag')
        elif value in (None, '', [], {}):
            messages.append(f'{label}: {field} must be populated')


def check_stage_b(data):
    messages = []
    for field, expected in STAGE_B_EXPECTED_TOP_LEVEL.items():
        if field not in data:
            messages.append(f'top-level missing {field}')
        elif data.get(field) != expected:
            messages.append(f'top-level {field} must be {expected!r}, got {data.get(field)!r}')

    packages = evidence_packages(data)
    if has_any_source_diversity_field(data):
        validate_stage_b_source_diversity(data, 'top-level', messages)
    elif packages:
        for index, package in enumerate(packages):
            validate_stage_b_source_diversity(package, f'evidence_package[{item_key(package) or index}]', messages)
    else:
        for field in STAGE_B_SOURCE_DIVERSITY_REQUIRED:
            messages.append(f'top-level/evidence_packages missing source-diversity lineage field {field}')

    if messages:
        return fail(messages)
    print('RESULT: PASS_STAGE_B_SCHEMA_CONTRACT')
    return 0


def iter_stage_c_items(data):
    for pool in STAGE_C_POOLS:
        for row in as_list(data.get(pool)):
            if isinstance(row, dict):
                yield pool, row


def check_stage_c(data):
    messages = []
    for pool, item in iter_stage_c_items(data):
        card_id = item.get('id') or 'unknown'
        for field in STAGE_C_BASE_REQUIRED:
            if missing_nonempty(item, field):
                messages.append(f'{pool} {card_id}: missing {field}')
        for field in STAGE_C_SOURCE_DIVERSITY_REQUIRED:
            if missing_presence(item, field):
                messages.append(f'{pool} {card_id}: missing source-diversity lineage field {field}')
        if pool in STAGE_C_ACCEPTED_POOLS:
            if item.get('strict_gate_acceptance_guard_applied') is not True:
                messages.append(f'{pool} {card_id}: strict_gate_acceptance_guard_applied must be true')
            if item.get('accepted_pool_lineage_status') != 'PASS':
                messages.append(f'{pool} {card_id}: accepted_pool_lineage_status must be PASS')
            if item.get('state') != 'accepted_fact_safe':
                messages.append(f'{pool} {card_id}: state must be accepted_fact_safe')
            if item.get('stage_c_only') is not True:
                messages.append(f'{pool} {card_id}: stage_c_only must be true')
            for flag in STAGE_C_FORBIDDEN_TRUE_FLAGS:
                if item.get(flag) is True or item.get('state') == flag:
                    messages.append(f'{pool} {card_id}: Stage C must not set downstream flag/state {flag}')
    if messages:
        return fail(messages)
    print('RESULT: PASS_STAGE_C_SCHEMA_CONTRACT')
    return 0


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

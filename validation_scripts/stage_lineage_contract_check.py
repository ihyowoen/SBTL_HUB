#!/usr/bin/env python3
"""Contract-driven Stage A/B/C lineage validator.

Usage:
  python validation_scripts/stage_lineage_contract_check.py stage_a <stage_a.json>
  python validation_scripts/stage_lineage_contract_check.py stage_b <stage_b.json>
  python validation_scripts/stage_lineage_contract_check.py stage_c <stage_c.json>
"""
import json
import re
import sys
import unicodedata

STAGE_A_REQUIRED = [
    'spec_id', 'source_story_ids', 'strict_pass_gate',
    'enhanced_selector_precision_version', 'selector_policy_version',
    'strict_gate_check', 'format_risk_tags', 'baseline_relation', 'duplicate_risk',
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
STAGE_A_NON_EXECUTION_ANCHOR_CLASSES = {
    'policy_regulatory_anchor',
    'data_financial_anchor',
    'strategic_behavior_anchor',
    'technology_commercialization_anchor',
    'follow_up_probability_anchor',
}
STAGE_A_V3_OVERRIDE_REQUIRED = [
    'structural_value_override_reason',
    'anchor_classes',
    'incremental_information',
    'decision_relevance',
    'baseline_expectation_changed',
    'evidence_needed_for_stage_b',
    'next_confirmation_points',
    'why_execution_event_not_required',
    'prior_state',
    'new_verified_fact',
    'changed_judgment',
    'uncertainty_resolved',
    'remaining_uncertainty',
]
STAGE_A_V3_NARRATIVE_FIELDS = (
    'structural_value_override_reason',
    'incremental_information',
    'decision_relevance',
    'baseline_expectation_changed',
    'why_execution_event_not_required',
    'prior_state',
    'new_verified_fact',
    'changed_judgment',
    'uncertainty_resolved',
    'remaining_uncertainty',
)
STAGE_A_GENERIC_OVERRIDE_FRAGMENTS = (
    'official source',
    'company material',
    'media report',
    'additional confirmation',
    'more evidence',
    'further evidence',
    'more data',
    'additional data',
    'further confirmation',
    'needs confirmation',
    'confirmation needed',
    'to be confirmed',
    'tbd',
    'unknown',
)
STAGE_A_PLACEHOLDER_NARRATIVE_PHRASES = {
    'not provided', 'not available', 'not specified', 'not applicable',
    'no information', 'no details', 'no data', 'none provided',
    'placeholder', 'dummy text', 'n/a', 'na', 'nil', 'none',
    '미제공', '정보 없음', '자료 없음', '해당 없음', '확인 불가',
}
STAGE_A_PLACEHOLDER_NARRATIVE_TOKENS = {
    'not', 'provided', 'available', 'specified', 'applicable', 'disclosed',
    'known', 'no', 'information', 'details', 'data', 'none', 'placeholder',
    'dummy', 'text', 'n/a', 'na', 'nil', 'yet', 'unavailable', 'undisclosed',
    'missing', 'unknown', 'currently', 'still', 'presently', 'current',
    'present', 'at', 'as', 'of', 'now', 'this', 'time', 'remains', 'remaining',
    'undetermined', 'unconfirmed', 'unverified', 'unclear', 'pending',
    '미제공', '미공개', '비공개', '정보', '자료', '내용', '없음', '해당',
    '확인', '불가', '아직', '현재', '여전히', '미정', '미확인', '불명',
}
STAGE_A_PLACEHOLDER_NARRATIVE_PATTERNS = (
    r'\b(?:not|no|none)\s+(?:yet\s+)?(?:provided|available|specified|applicable|disclosed|known)\b',
    r'\b(?:information|details|data)\s+(?:is\s+)?(?:not\s+)?(?:available|unavailable|missing|unknown|undisclosed)\b',
    r'\b(?:unavailable|undisclosed|unknown)\s+(?:information|details|data)\b',
)
STAGE_A_EXACT_TARGET_TERMS = (
    'revenue', 'sales', 'ebitda', 'ebit', 'profit', 'margin', 'cost',
    'price', 'volume', 'capacity', 'utilisation', 'utilization', 'yield',
    'throughput', 'capex', 'opex', 'deadline', 'date', 'stage', 'status',
    'probability', 'adoption', 'approval', 'production', 'shipment',
    '매출', '영업이익', '이익', '마진', '원가', '가격', '물량', '용량',
    '가동률', '수율', '투자', '기한', '날짜', '단계', '상태', '확률',
    '채택', '승인', '생산', '출하',
)
STAGE_A_INTERPRETATION_EFFECT_TERMS = (
    'confirm', 'strengthen', 'support', 'weaken', 'invalidate', 'reject',
    'revise', 'change', 'raise', 'lower', 'increase', 'decrease', 'hold',
    '확인', '강화', '지지', '약화', '무효', '기각', '수정', '변경',
    '상향', '하향', '증가', '감소', '유지',
)
STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS = (
    'official', 'filing', 'rule', 'regulation', 'guidance', 'order', 'notice',
    'document', 'dataset', 'statistics', 'transcript', 'technical test',
    'test result', 'independent report', 'audit', 'contract', 'permit',
    'court decision', 'legislation', 'earnings release', 'prepared remarks',
    '공식', '공시', '규정', '지침', '명령', '고시', '문서', '데이터셋',
    '통계', '회의록', '시험', '시험결과', '보고서', '감사', '계약',
    '허가', '판결', '법률', '실적발표', '준비발언',
)
STAGE_A_CONFIRMATION_EVENT_TERMS = (
    'publication', 'filing', 'guidance', 'approval', 'decision', 'contract',
    'award', 'permit', 'launch', 'production', 'shipment', 'qualification',
    'test result', 'effective date', 'deadline', 'schedule', 'capacity',
    'volume', 'price', 'cost', 'margin', 'utilisation', 'utilization',
    'adoption rate', 'threshold', 'probability', 'metric',
)

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


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _normalized_text(value):
    return value.strip().lower() if isinstance(value, str) else ''


def _contains_generic_fragment(value):
    text = _normalized_text(value)
    return any(fragment in text for fragment in STAGE_A_GENERIC_OVERRIDE_FRAGMENTS)


def _strip_unicode_edge_punctuation(value):
    text = unicodedata.normalize('NFKC', _normalized_text(value)).strip()
    while text:
        before = text
        while text and (
            text[0].isspace()
            or unicodedata.category(text[0]).startswith(('P', 'S'))
        ):
            text = text[1:].lstrip()
        while text and (
            text[-1].isspace()
            or unicodedata.category(text[-1]).startswith(('P', 'S'))
        ):
            text = text[:-1].rstrip()
        if text == before:
            break
    return text


def _contains_generic_target_fragment(value):
    # Normalize Unicode punctuation and paired quote/bracket wrappers so
    # placeholder-only variants such as “more evidence”… or more evidence。
    # cannot bypass complete-pattern matching.
    text = _strip_unicode_edge_punctuation(value)
    text = ' '.join(text.replace(':', ' ').replace(';', ' ').split())
    if not text:
        return True
    # Match generic evidence scaffolds as complete placeholder semantics, not
    # substrings inside concrete claims such as "additional data center capacity".
    patterns = (
        r'(?:more|further) evidence(?: (?:on|for|needed|required)\b.*)?',
        r'more data(?: (?:on|for|needed|required)\b.*)?',
        r'additional data(?: (?:on|for|needed|required|to confirm)\b.*)?',
        r'(?:additional|further) confirmation(?: (?:on|for|needed|required)\b.*)?',
        r'(?:needs confirmation|confirmation needed|to be confirmed|tbd)',
        r'(?:official source|company material|media report)(?:s)?(?: for confirmation)?',
    )
    return any(re.fullmatch(pattern, text) for pattern in patterns)


def _specific_string(value):
    text = _normalized_text(value)
    return bool(text) and len(text.split()) >= 4 and not _contains_generic_fragment(text)


def _placeholder_only_text(value):
    text = _strip_unicode_edge_punctuation(value)
    if not text:
        return True
    if text in STAGE_A_PLACEHOLDER_NARRATIVE_PHRASES:
        return True
    normalized = ''.join(
        ' ' if (
            char.isspace()
            or unicodedata.category(char).startswith(('P', 'S'))
        ) else char
        for char in text
    )
    normalized = ' '.join(normalized.split())
    if normalized in STAGE_A_PLACEHOLDER_NARRATIVE_PHRASES:
        return True
    if any(re.fullmatch(pattern, normalized) for pattern in STAGE_A_PLACEHOLDER_NARRATIVE_PATTERNS):
        return True
    tokens = normalized.split()
    if bool(tokens) and len(tokens) <= 5 and all(
        token in STAGE_A_PLACEHOLDER_NARRATIVE_TOKENS for token in tokens
    ):
        return True
    korean_absence = ('없음', '미제공', '미공개', '비공개', '불가')
    korean_subject = ('정보', '자료', '내용', '세부', '사항')
    return (
        len(tokens) <= 5
        and any(marker in normalized for marker in korean_absence)
        and any(subject in normalized for subject in korean_subject)
    )


def _item_specific_narrative(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    # Narrative fields may legitimately describe residual unknowns or pending
    # confirmation. Reject placeholder-only semantics, not contextual words
    # such as "unknown" inside an otherwise item-specific explanation.
    return len(text) >= 8 and not _placeholder_only_text(text)


def _structured_component(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    return len(text) >= 2 and not _placeholder_only_text(text)


def _structured_source_class(value):
    return (
        _structured_component(value)
        and not _contains_generic_fragment(value)
        and _has_any_term(value, STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS)
    )


def _structured_exact_target(value):
    if not _structured_component(value) or _contains_generic_target_fragment(value):
        return False
    text = _normalized_text(value)
    tokens = [token for token in text.replace('/', ' ').replace(':', ' ').split() if token]
    has_named_target = len(tokens) >= 2 and any(
        re.search(r'[a-z가-힣]', token) for token in tokens
    )
    is_explicit_date = bool(re.fullmatch(
        r'(?:19|20|21)\d{2}(?:[-/.](?:0?[1-9]|1[0-2])(?:[-/.](?:0?[1-9]|[12]\d|3[01]))?|년(?:\s*(?:0?[1-9]|1[0-2])월(?:\s*(?:0?[1-9]|[12]\d|3[01])일)?)?)?',
        text,
    ))
    has_qualified_numeric_target = (
        any(char.isdigit() for char in text)
        and any(re.search(r'[a-z가-힣]', token) for token in tokens)
        and (has_named_target or _has_any_term(value, STAGE_A_EXACT_TARGET_TERMS))
    )
    return (
        is_explicit_date
        or has_qualified_numeric_target
        or has_named_target
        or _has_any_term(value, STAGE_A_EXACT_TARGET_TERMS)
    )


def _structured_interpretation_effect(value):
    return (
        _structured_component(value)
        and not _contains_generic_fragment(value)
        and _has_any_term(value, STAGE_A_INTERPRETATION_EFFECT_TERMS)
    )


def _term_pattern(term):
    escaped = re.escape(term)
    if term in STAGE_A_INTERPRETATION_EFFECT_TERMS and not re.search(r'[가-힣]', term):
        irregular = {
            'hold': r'(?:hold|holds|holding|held)',
        }
        if term in irregular:
            body = irregular[term]
        elif term.endswith('e'):
            stem = re.escape(term[:-1])
            body = rf'(?:{escaped}|{stem}es|{stem}ed|{stem}ing)'
        else:
            body = rf'(?:{escaped}|{escaped}s|{escaped}es|{escaped}ed|{escaped}ing)'
        return rf'(?<![\w]){body}(?![\w])'
    if re.search(r'[가-힣]', term):
        # Korean source-class terms commonly appear inside compounds such as
        # 공시자료. Preserve the left boundary so 비공식 does not satisfy 공식.
        return rf'(?<![\w]){escaped}'
    # Accept ordinary English inflections such as filing/filings while keeping
    # full left/right boundaries so unofficial does not satisfy official.
    return rf'(?<![\w]){escaped}(?:s|es)?(?![\w])'


def _matching_terms(value, terms):
    text = _normalized_text(value)
    return [
        term for term in sorted(terms, key=len, reverse=True)
        if re.search(_term_pattern(term), text)
    ]


def _has_any_term(value, terms):
    return bool(_matching_terms(value, terms))


def _valid_evidence_target(value):
    if isinstance(value, dict):
        source_class = value.get('source_or_document_class') or value.get('source_class')
        exact_target = value.get('exact_claim_or_metric') or value.get('verification_target')
        return _structured_source_class(source_class) and _structured_exact_target(exact_target)

    text = _normalized_text(value)
    if not text or _placeholder_only_text(text) or _contains_generic_target_fragment(text):
        return False
    matched_source_terms = _matching_terms(text, STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS)
    if not matched_source_terms:
        return False

    target_text = text
    for term in matched_source_terms:
        target_text = re.sub(_term_pattern(term), ' ', target_text)
    target_tokens = [token for token in target_text.replace('/', ' ').replace(':', ' ').split() if token]
    has_exact_metric_or_date = any(any(char.isdigit() for char in token) for token in target_tokens)
    has_named_target = len(target_tokens) >= 2
    has_exact_metric_term = _has_any_term(target_text, STAGE_A_EXACT_TARGET_TERMS)
    return has_exact_metric_or_date or has_named_target or has_exact_metric_term


def _valid_confirmation_point(value):
    if isinstance(value, dict):
        measurable = value.get('measurable_event_or_metric') or value.get('confirmation_event')
        interpretation_effect = value.get('interpretation_effect') or value.get('confirm_weaken_invalidate')
        return _structured_exact_target(measurable) and _structured_interpretation_effect(interpretation_effect)
    text = _normalized_text(value)
    return (
        bool(text)
        and len(text.split()) >= 4
        and not _placeholder_only_text(text)
        and not _contains_generic_target_fragment(text)
        and _has_any_term(text, STAGE_A_CONFIRMATION_EVENT_TERMS)
    )


def validate_stage_a_v3_override(spec, spec_id, messages):
    if spec.get('structural_value_override_applied') is not True:
        return False

    valid = True
    for field in STAGE_A_V3_OVERRIDE_REQUIRED:
        if missing_nonempty(spec, field):
            messages.append(f'{spec_id}: incomplete V3 override package missing {field}')
            valid = False

    for field in STAGE_A_V3_NARRATIVE_FIELDS:
        if not _item_specific_narrative(spec.get(field)):
            messages.append(f'{spec_id}: {field} must be item-specific narrative text')
            valid = False

    classes = spec.get('anchor_classes')
    if not isinstance(classes, list) or not classes:
        messages.append(f'{spec_id}: anchor_classes must be a non-empty array for v3_non_execution')
        valid = False
    else:
        invalid_classes = [
            value for value in classes
            if not isinstance(value, str)
            or value not in STAGE_A_NON_EXECUTION_ANCHOR_CLASSES
        ]
        if invalid_classes:
            messages.append(f'{spec_id}: invalid non-execution anchor_classes={invalid_classes}')
            valid = False

    evidence_targets = spec.get('evidence_needed_for_stage_b')
    if not isinstance(evidence_targets, list) or not evidence_targets:
        valid = False
    elif any(not _valid_evidence_target(value) for value in evidence_targets):
        messages.append(
            f'{spec_id}: evidence_needed_for_stage_b entries must identify both '
            'a source/document class and an exact claim, metric, stage, or date'
        )
        valid = False

    confirmation_points = spec.get('next_confirmation_points')
    if not isinstance(confirmation_points, list) or not confirmation_points:
        valid = False
    elif any(not _valid_confirmation_point(value) for value in confirmation_points):
        messages.append(
            f'{spec_id}: next_confirmation_points entries must identify measurable '
            'events or metrics, not generic confirmation requests'
        )
        valid = False

    return valid


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
    format_risk_tags = spec.get('format_risk_tags')
    if not isinstance(format_risk_tags, list):
        messages.append(f'{spec_id}: format_risk_tags must be an array')
        has_format_risk = False
    else:
        invalid_format_risk_tags = [
            value for value in format_risk_tags
            if not isinstance(value, str) or not value.strip()
        ]
        if invalid_format_risk_tags:
            messages.append(f'{spec_id}: format_risk_tags must contain non-empty strings')
        normalized_format_risk_tags = [
            value.strip().lower() for value in format_risk_tags
            if isinstance(value, str) and value.strip()
        ]
        has_format_risk = normalized_format_risk_tags not in ([], ['none'])
    execution_type = spec.get('execution_anchor_type')
    execution_strength = spec.get('execution_anchor_strength')
    execution_core_complete = (
        _nonempty_string(execution_type)
        and execution_strength in STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH
    )
    override_marker = spec.get('structural_value_override_applied')
    residual_override_fields = [
        field for field in STAGE_A_V3_OVERRIDE_REQUIRED
        if spec.get(field) not in (None, '', [], {})
    ]
    execution_path_complete = (
        execution_core_complete
        and override_marker is False
        and not residual_override_fields
    )

    if has_format_risk:
        override_path_complete = validate_stage_a_v3_override(spec, spec_id, messages)
        if execution_core_complete and override_marker is not False:
            messages.append(
                f'{spec_id}: execution route requires structural_value_override_applied=false'
            )
        if execution_core_complete and residual_override_fields:
            messages.append(
                f'{spec_id}: execution route must leave override-only fields empty; '
                f'found {residual_override_fields}'
            )
        if execution_path_complete == override_path_complete or (
            execution_core_complete and override_path_complete
        ):
            messages.append(
                f'{spec_id}: format-risk strict_passed_spec requires exactly one complete '
                'execution or v3_non_execution path'
            )
        if (execution_type or execution_strength) and not execution_core_complete:
            messages.append(f'{spec_id}: partial/invalid execution path metadata for format-risk strict_passed_spec')
    else:
        if not _nonempty_string(execution_type):
            messages.append(f'{spec_id}: missing execution_anchor_type')
        if execution_strength not in STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH:
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

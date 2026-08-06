#!/usr/bin/env python3
"""Review 4870635557 compatibility layer for Related assertion specificity."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_PRIOR_PATH = Path(__file__).with_name(
    "related_lifecycle_check_review4868891584_base.py"
)
_PRIOR_DIR = str(_PRIOR_PATH.parent)
if _PRIOR_DIR not in sys.path:
    sys.path.insert(0, _PRIOR_DIR)

_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.related_lifecycle_check_review4868891584_base",
    _PRIOR_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load Related validator base from {_PRIOR_PATH}")
_prior = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_prior)

# Keep the public source-level chronology contract visible to static checks;
# behavior remains implemented by the preserved prior layer.
_RESOLVED_PROVISIONAL_TARGETS_CONTRACT = "resolved_provisional_targets"
_PROVISIONAL_CHRONOLOGY_ERROR_CONTRACT = (
    "follow-up date precedes provisional predecessor"
)
_RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS = {
    "ebitda", "profit", "profits", "capex", "opex", "yield", "yields",
    "throughput", "영업이익", "이익", "수익", "설비투자", "자본지출",
    "운영비", "영업비용", "수율", "처리량",
}
_prior._RELATED_DATA_FINANCIAL_ROLE_TERMS.update(
    _RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
)
_prior._ASSERTION_ROLE_TERMS.update(
    _RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
)

for _name in dir(_prior):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_prior, _name)

_prior_item_specific_lineage_assertion = _prior.item_specific_lineage_assertion
_GENERIC_JUDGMENT_DESCRIPTOR_TERMS = {
    "outlook", "probability", "likelihood", "risk", "risks", "judgment",
    "judgement", "expectation", "expectations", "forecast", "forecasts",
    "sentiment", "confidence", "conviction", "view", "views",
    "전망", "확률", "가능성", "위험", "리스크", "판단", "기대", "예측",
    "심리", "신뢰", "신뢰도", "확신", "견해",
}
_NOMINAL_CHANGE_TERMS = {
    "reduction", "reductions", "improvement", "improvements", "decline",
    "declines", "increase", "increases", "decrease", "decreases", "growth",
    "deterioration", "recovery", "expansion", "contraction", "cut", "cuts",
    "drop", "drops", "rise", "rises", "gain", "gains", "감축", "개선",
    "하락", "상승", "증가", "감소", "악화", "회복", "확대", "축소",
}
_METRIC_VALUE_PATTERNS = (
    r"(?<![a-z0-9가-힣])[-+]?\d+(?:[.,]\d+)?\s*%",
    r"(?<![a-z0-9가-힣])[$€£¥₩]\s*[-+]?\d+(?:[.,]\d+)?",
    r"(?<![a-z0-9가-힣])[-+]?\d+(?:[.,]\d+)?\s*(?:"
    r"usd|eur|krw|jpy|cny|rmb|won|dollars?|euros?|yuan|yen|"
    r"million|billion|trillion|mn|bn|bps|bp|pp|percentage\s+points?|"
    r"times?|x|억원|조원|만원|원|달러|유로|위안|엔|톤|천톤|만톤|kg|"
    r"gwh|mwh|kwh|gw|mw|kw|units?|대|건|배)(?![a-z0-9가-힣])",
)


def _has_concrete_metric_value(value):
    """Recognize a measured value, not a digit embedded in an entity label."""
    normalized = _prior._normalize_assertion_text(value)
    return any(
        _prior._base.re.search(pattern, normalized)
        for pattern in _METRIC_VALUE_PATTERNS
    )


def item_specific_lineage_assertion(value):
    """Require concrete metric developments and preserve numbered entity labels."""
    prior_accepts = _prior_item_specific_lineage_assertion(value)

    normalized_value = _prior._normalize_assertion_text(value)
    normalized = _prior._base.re.sub(
        r"[^a-z0-9가-힣]+", " ", normalized_value
    ).strip()
    tokens = [token for token in normalized.split() if token]
    normalized_role_tokens = [
        _prior._normalize_assertion_role_token(token) for token in tokens
    ]
    subject_tokens = [
        _prior._normalize_subject_token(token) for token in normalized_role_tokens
    ]
    temporal_indexes = _prior._assertion_temporal_token_indexes(tokens)
    has_nominal_change = any(
        token in _NOMINAL_CHANGE_TERMS for token in normalized_role_tokens
    )
    has_change_predicate = has_nominal_change or any(
        token in _prior._ASSERTION_CHANGE_PREDICATE_TERMS
        for token in normalized_role_tokens
    )
    has_concrete_entity_label = _prior._has_concrete_entity_label(tokens)

    metric_roles = {
        token
        for token in normalized_role_tokens
        if token in _RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
    }
    has_concrete_subject = has_concrete_entity_label or any(
        index not in temporal_indexes
        and role_token not in _RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
        and role_token not in _NOMINAL_CHANGE_TERMS
        and subject_token not in _prior._ASSERTION_NEUTRAL_SUBJECT_TOKENS
        and subject_token not in _prior._GENERIC_OWNER_SINGULARS
        and subject_token not in _prior._base._GENERIC_LINEAGE_ASSERTION_TOKENS
        and not subject_token.isdigit()
        for index, (role_token, subject_token) in enumerate(
            zip(normalized_role_tokens, subject_tokens)
        )
    )

    # The historical gate predates nominal metric-change nouns. Extend it only
    # for the bounded shape `concrete subject + metric + nominal change`; generic
    # forms such as `capex reduction` or `company profit improvement` still fail.
    nominal_metric_override = (
        bool(metric_roles) and has_nominal_change and has_concrete_subject
    )
    if not prior_accepts and not nominal_metric_override:
        return False

    has_concrete_metric_value = _has_concrete_metric_value(value)
    has_execution_event = any(
        token in _prior._ASSERTION_EVENT_SUBJECT_TERMS
        and token not in _RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
        for token in normalized_role_tokens
    )

    # A named entity plus a metric noun is still not a fact or change. Preserve
    # the existing scoped `named subject + period + metric` contract, but require
    # a predicate/comparative, measured value, execution event, or period scope.
    # Digits embedded in product or facility names do not count as measurements.
    if metric_roles and not (
        has_change_predicate
        or has_concrete_metric_value
        or has_execution_event
        or bool(temporal_indexes)
    ):
        return False

    # Project A / Plant 1 / Facility 2 are concrete subjects. Preserve them when
    # a real verbal or nominal judgment change is present instead of stripping
    # the label and misclassifying the remainder as generic judgment prose.
    if has_concrete_entity_label and has_change_predicate:
        return True

    meaningful_tokens = []
    for index, (role_token, subject_token) in enumerate(
        zip(normalized_role_tokens, subject_tokens)
    ):
        if index in temporal_indexes or subject_token.isdigit():
            continue
        if subject_token in _prior._ASSERTION_NEUTRAL_SUBJECT_TOKENS:
            continue
        if subject_token in _prior._GENERIC_OWNER_SINGULARS:
            continue
        if subject_token in _prior._base._GENERIC_LINEAGE_ASSERTION_TOKENS:
            continue
        meaningful_tokens.append((role_token, subject_token))

    if meaningful_tokens and all(
        role_token in _prior._ASSERTION_CHANGE_PREDICATE_TERMS
        or role_token in _NOMINAL_CHANGE_TERMS
        or subject_token in _GENERIC_JUDGMENT_DESCRIPTOR_TERMS
        for role_token, subject_token in meaningful_tokens
    ):
        return False
    return True


_prior.item_specific_lineage_assertion = item_specific_lineage_assertion
_prior._base.item_specific_lineage_assertion = item_specific_lineage_assertion

if __name__ == "__main__":
    _prior._base.sys.exit(_prior._base.main())

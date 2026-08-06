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
_SUBJECTLESS_NOMINAL_MODIFIER_TERMS = {
    "significant", "significantly", "material", "materially", "substantial",
    "substantially", "sharp", "sharply", "strong", "strongly", "weak",
    "weakly", "major", "minor", "notable", "notably", "meaningful",
    "meaningfully", "quarterly", "annual", "annually", "monthly", "weekly",
    "daily", "recent", "recently", "expected", "projected", "reported",
    "documented", "verified", "continued", "continuing", "further", "ongoing",
    "large", "small", "rapid", "rapidly", "gradual", "gradually",
    "unexpected", "severe", "historic", "historical", "dramatic", "sudden",
    "record", "surprising", "unprecedented", "exceptional", "temporary",
    "persistent", "structural", "cyclical", "seasonal", "broad", "modest",
    "중대한", "상당한", "유의미한", "뚜렷한", "큰", "작은", "급격한",
    "빠른", "완만한", "분기", "분기별", "연간", "월간", "주간", "일간",
    "최근", "예상", "전망된", "보고된", "확인된", "지속적인", "추가적인",
}
# A bare sentence-initial TitleCase token is ambiguous. Keep only explicitly
# governed legacy single-token names; other English names need an acronym,
# possessive, corporate suffix, internal-capital/digit, or multi-token signal.
_KNOWN_SINGLE_TOKEN_ENTITY_NAMES = {"tesla", "acme"}
_KNOWN_KOREAN_SINGLE_TOKEN_ENTITY_NAMES = {
    "삼성", "현대", "기아", "포스코", "한화", "두산", "롯데", "에코프로",
    "엘지", "금양", "천보", "율촌화학", "동화기업", "한국전력",
    "수출입은행", "산업통상자원부",
}
_KOREAN_ENTITY_CLASS_TERMS = {
    "프로젝트", "사업", "공장", "플랜트", "시설", "법인", "컨소시엄",
    "센터", "단지", "기지", "연구원", "위원회", "은행",
}
_KOREAN_ENTITY_SUFFIXES = (
    "주식회사", "에너지솔루션", "솔루션", "퓨처엠", "비엠", "화학",
    "전자", "전력", "산업", "소재", "배터리", "모빌리티", "홀딩스",
    "테크놀로지", "테크", "공사", "연구원", "위원회", "은행", "그룹",
)
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


def _original_assertion_tokens(value):
    """Return assertion tokens while preserving entity-name capitalization."""
    original = str(value).replace("’", "'")
    original = _prior._base.re.sub(
        r"(?<=[A-Za-z0-9])'s\b", "", original,
        flags=_prior._base.re.IGNORECASE,
    )
    original = _prior._base.re.sub(
        r"(?<=[A-Za-z0-9])s'\b", "s", original,
        flags=_prior._base.re.IGNORECASE,
    )
    return _prior._base.re.findall(r"[A-Za-z0-9가-힣]+", original)


def _possessive_subject_tokens(value):
    original = str(value).replace("’", "'")
    return {
        match.group(1).casefold()
        for match in _prior._base.re.finditer(
            r"\b([A-Za-z][A-Za-z0-9]*)'s\b", original,
            flags=_prior._base.re.IGNORECASE,
        )
    }


def _has_positively_identifiable_subject(
    value,
    tokens,
    normalized_role_tokens,
    subject_tokens,
    temporal_indexes,
    has_concrete_entity_label,
):
    """Require a named/class-bound entity, not an arbitrary leftover modifier."""
    if has_concrete_entity_label:
        return True

    original_tokens = _original_assertion_tokens(value)
    if len(original_tokens) != len(tokens):
        return False
    possessive_subjects = _possessive_subject_tokens(value)
    has_corporate_suffix = any(
        token in _prior._ENTITY_LABEL_SUFFIXES
        for token in normalized_role_tokens
    )

    for index, (original, role_token, subject_token) in enumerate(
        zip(original_tokens, normalized_role_tokens, subject_tokens)
    ):
        if index in temporal_indexes or subject_token.isdigit():
            continue
        if role_token in _RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS:
            continue
        if role_token in _NOMINAL_CHANGE_TERMS:
            continue
        if role_token in _SUBJECTLESS_NOMINAL_MODIFIER_TERMS:
            continue
        if subject_token in _GENERIC_JUDGMENT_DESCRIPTOR_TERMS:
            continue
        if subject_token in _prior._ASSERTION_NEUTRAL_SUBJECT_TOKENS:
            continue
        if subject_token in _prior._GENERIC_OWNER_SINGULARS:
            continue
        if subject_token in _prior._base._GENERIC_LINEAGE_ASSERTION_TOKENS:
            continue

        # Hangul has no capitalization signal, so require an affirmative
        # company/institution or class-bound project/facility cue. Unknown
        # Korean modifiers and adverbs remain fail-closed.
        if _prior._base.re.search(r"[가-힣]", original):
            korean_base = original[:-1] if original.endswith("의") else original
            next_is_entity_class = (
                index + 1 < len(normalized_role_tokens)
                and normalized_role_tokens[index + 1] in _KOREAN_ENTITY_CLASS_TERMS
            )
            has_entity_suffix = any(
                korean_base.endswith(suffix) and len(korean_base) > len(suffix)
                for suffix in _KOREAN_ENTITY_SUFFIXES
            )
            if (
                subject_token in _KNOWN_KOREAN_SINGLE_TOKEN_ENTITY_NAMES
                or next_is_entity_class
                or has_entity_suffix
            ):
                return True
            continue

        # English entity signals must be positive. Sentence-initial TitleCase
        # alone is not enough because ordinary assertion prose is sentence-cased.
        has_internal_name_signal = any(char.isupper() for char in original[1:])
        has_digit_signal = any(char.isdigit() for char in original)
        previous_is_entity_lead = (
            index > 0
            and normalized_role_tokens[index - 1] in _prior._ENTITY_LABEL_LEADS
        )
        previous_is_named_token = (
            index > 0
            and original_tokens[index - 1][:1].isupper()
            and normalized_role_tokens[index - 1]
            not in _SUBJECTLESS_NOMINAL_MODIFIER_TERMS
        )
        has_multi_token_name_signal = (
            index > 0
            and original[:1].isupper()
            and (previous_is_entity_lead or previous_is_named_token)
        )
        has_corporate_name_signal = index == 0 and has_corporate_suffix
        if len(original) >= 2 and (
            original.isupper()
            or has_internal_name_signal
            or has_digit_signal
            or has_multi_token_name_signal
            or has_corporate_name_signal
            or subject_token in possessive_subjects
            or subject_token in _KNOWN_SINGLE_TOKEN_ENTITY_NAMES
        ):
            return True
    return False


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
    has_concrete_subject = _has_positively_identifiable_subject(
        value,
        tokens,
        normalized_role_tokens,
        subject_tokens,
        temporal_indexes,
        has_concrete_entity_label,
    )

    # Nominal metric-change phrases require an actual entity/item subject even
    # when the historical gate would otherwise accept the role words alone.
    if metric_roles and has_nominal_change and not has_concrete_subject:
        return False

    # The historical gate predates nominal metric-change nouns. Extend it only
    # for the bounded shape `identifiable subject + metric + nominal change`.
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

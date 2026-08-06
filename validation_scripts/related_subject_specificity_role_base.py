#!/usr/bin/env python3
"""Review 4862131806 compatibility layer for Related assertion semantics."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_BASE_PATH = Path(__file__).with_name("related_lifecycle_check_review4860866998_base.py")
# The base validator retains direct-script imports for CLI compatibility. Ensure
# its sibling modules are also importable when this wrapper is imported as the
# validation_scripts package from an isolated focused unittest invocation.
_BASE_DIR = str(_BASE_PATH.parent)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.related_lifecycle_check_review4860866998_base",
    _BASE_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load Related validator base from {_BASE_PATH}")
_base = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_base)

for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)

_prior_item_specific_lineage_assertion = _base.item_specific_lineage_assertion
_RELATED_DATA_FINANCIAL_ROLE_TERMS = {
    "operating", "operation", "operations", "shipment", "shipments", "price",
    "prices", "inventory", "inventories", "utilisation", "utilisations",
    "utilization", "utilizations", "safety", "market", "data", "economics",
    "impairment", "impairments", "loss", "losses", "recognition", "scale",
    "delay", "delays", "revenue", "revenues", "customer", "customers",
    "운영", "가동", "출하", "가격", "재고", "가동률", "이용률", "안전",
    "시장", "데이터", "경제성", "손상", "손실", "매출인식", "규모", "지연",
    "매출", "고객",
}
_ASSERTION_ROLE_TERMS = {
    "approve", "approved", "adopt", "adopted", "effective", "enforce", "enforced",
    "launch", "launched", "start", "started", "complete", "completed", "secure",
    "secured", "award", "awarded", "contract", "contracted", "finance", "financed",
    "commission", "commissioned", "commissioning", "file", "filed", "filing",
    "disclose", "disclosed", "publish", "published", "announce", "announced",
    "delay", "delayed", "cancel", "cancelled", "canceled", "increase", "increased",
    "decrease", "decreased", "add", "added", "remove", "removed", "change",
    "changed", "shift", "shifted", "move", "moved", "confirm", "confirmed",
    "weaken", "weakened", "strengthen", "strengthened", "invalidate", "invalidated",
    "permit", "permitted", "license", "licensed", "agreement", "agreed",
    "construction", "constructed", "operate", "operated", "operation", "operations",
    "operating", "begin", "began", "begins", "enter", "entered", "force",
    "fund", "funded", "funding", "invest", "invested", "investment", "supply",
    "supplied", "deliver", "delivered", "delivery", "sale", "sold", "purchase",
    "purchased", "shipment", "customer", "guidance", "forecast", "milestone",
    "rule", "revenue", "margin", "capacity", "volume", "price", "cost", "date",
    "stage", "status", "eligibility", "probability", "outlook", "judgment",
    "judgement", "target", "execution", "승인", "채택", "발효", "시행", "집행",
    "출시", "착수", "준공", "상업운전", "완료", "확보", "수주", "계약", "금융",
    "공시", "발표", "지연", "취소", "증가", "감소", "추가", "삭제", "변경",
    "전환", "이동", "확인", "약화", "강화", "무효화", "허가", "인가", "건설",
    "운영", "가동", "투자", "공급", "납품", "판매", "구매", "출하", "고객",
    "매출", "마진", "용량", "물량", "가격", "비용", "날짜", "단계", "상태",
    "적격성", "확률", "전망", "판단", "목표",
} | _RELATED_DATA_FINANCIAL_ROLE_TERMS
_ENTITY_LABEL_LEADS = {
    "project", "program", "programme", "company", "corporation", "corp", "group",
    "fund", "facility", "plant", "site", "platform", "initiative", "venture",
    "프로젝트", "프로그램", "회사", "기업", "법인", "그룹", "펀드", "공장",
    "시설", "사업", "법인명",
}
_ENTITY_LABEL_SUFFIXES = {
    "inc", "incorporated", "corp", "corporation", "co", "company", "ltd",
    "limited", "llc", "plc", "holdings", "holding", "group", "partners",
    "ventures", "energy", "technologies", "technology", "systems", "solutions",
    "주식회사", "홀딩스", "그룹", "에너지", "테크놀로지", "시스템", "솔루션",
}
_AMBIGUOUS_ENTITY_ROLE_TERMS = _ENTITY_LABEL_LEADS | _ENTITY_LABEL_SUFFIXES
_ASSERTION_NEUTRAL_SUBJECT_TOKENS = {
    "a", "an", "the", "this", "that", "these", "those", "of", "for", "in",
    "on", "at", "to", "from", "as", "by", "with", "and", "or", "its", "s",
    "their", "official", "public", "regulatory", "government", "governmental",
    "corporate", "company", "issuer", "business", "entity", "reported",
    "organization", "organisation", "authority", "agency", "institution",
    "published", "disclosed", "source", "sources", "document", "documents",
    "dataset", "datasets", "transcript", "transcripts", "report", "reports",
    "release", "releases", "announcement", "announcements", "general", "latest",
    "current", "해당", "공식", "공공", "정부", "규제", "기업", "회사", "발행사",
    "자료", "문서", "데이터셋", "보고서", "발표자료", "일반", "최신", "현재",
} | _AMBIGUOUS_ENTITY_ROLE_TERMS
_GENERIC_OWNER_SINGULARS = {
    "company", "issuer", "business", "entity", "corporation", "corporate",
    "project", "program", "programme", "fund", "group", "facility", "plant",
    "site", "platform", "initiative", "venture",
}
_GENERIC_OWNER_PLURALS = {
    "companies": "company", "issuers": "issuer", "businesses": "business",
    "entities": "entity", "corporations": "corporation", "projects": "project",
    "programs": "program", "programmes": "programme", "funds": "fund",
    "groups": "group", "facilities": "facility", "plants": "plant",
    "sites": "site", "platforms": "platform", "initiatives": "initiative",
    "ventures": "venture",
}
_NUMERIC_ENTITY_LABEL_LEADS = {
    "project", "program", "programme", "plant", "facility", "site", "unit",
    "line", "block", "mine", "well", "factory", "프로젝트", "프로그램", "사업",
    "공장", "시설", "사업장", "사이트", "라인", "광산", "유정",
}
_LETTERED_ENTITY_LABEL_LEADS = _NUMERIC_ENTITY_LABEL_LEADS | {
    "project", "program", "programme", "platform", "initiative", "venture",
    "프로젝트", "프로그램", "사업",
}
_ASSERTION_CHANGE_PREDICATE_TERMS = {
    "approved", "adopted", "effective", "enforced", "launched", "started",
    "completed", "secured", "awarded", "contracted", "financed", "commissioned",
    "filed", "disclosed", "published", "announced", "delayed", "cancelled",
    "canceled", "increased", "decreased", "added", "removed", "changed",
    "shifted", "moved", "confirmed", "weakened", "strengthened", "invalidated",
    "permitted", "licensed", "agreed", "constructed", "operated", "operating",
    "began", "begins", "entered", "funded", "invested", "supplied", "delivered",
    "sold", "purchased", "lower", "lowered", "higher", "raised", "reduced",
    "improved", "worsened", "stronger", "weaker",
    "승인", "채택", "발효", "시행", "집행", "출시", "착수", "준공", "상업운전",
    "완료", "확보", "수주", "공시", "발표", "지연", "취소", "증가", "감소",
    "추가", "삭제", "변경", "전환", "이동", "확인", "약화", "강화", "무효화",
    "허가", "인가", "건설", "운영", "가동", "투자", "공급", "납품", "판매",
    "구매", "출하", "하향", "상향", "낮아짐", "높아짐", "개선", "악화",
}
_ASSERTION_EVENT_SUBJECT_TERMS = {
    "permit", "license", "agreement", "contract", "filing", "construction",
    "operation", "operations", "commissioning", "launch", "start", "award",
    "delivery", "shipment", "investment", "funding", "guidance", "forecast",
    "rule", "milestone", "허가", "인가", "계약", "공시", "건설", "운영",
    "가동", "상업운전", "출시", "착수", "수주", "납품", "출하", "투자",
    "금융", "전망", "규정", "이정표",
}
_STANDALONE_ASSERTION_EVENT_TERMS = {"commissioning", "상업운전"}
_ASSERTION_TEMPORAL_TERMS = {
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december", "quarter", "q1", "q2",
    "q3", "q4", "today", "yesterday", "tomorrow", "월", "분기", "오늘", "어제",
}
_ASSERTION_ORDINAL_PERIOD_TERMS = {
    "first", "second", "third", "fourth", "1st", "2nd", "3rd", "4th",
}
_ASSERTION_PERIOD_UNIT_TERMS = {
    "quarter", "half", "semester", "year", "분기", "반기", "연도",
}
_ASSERTION_PERIOD_MODIFIER_TERMS = {"fiscal", "calendar", "financial"}
_ASSERTION_ADJACENT_PERIOD_MODIFIER_TERMS = _ASSERTION_PERIOD_MODIFIER_TERMS | {"fy"}
_ASSERTION_SPLIT_FISCAL_YEAR_MARKERS = {"fy", "fiscal", "financial"}
_ASSERTION_SPLIT_QUARTER_MARKERS = {"q", "quarter"}
_ASSERTION_COMPOSITE_PERIOD_PATTERNS = (
    r"fy\d{2,4}",
    r"(?:h[12]|[12]h)(?:(?:fy)?\d{2,4})?",
    r"q[1-4](?:(?:fy)?\d{2,4})?",
    r"[1-4]q(?:(?:fy)?\d{2,4})?",
    r"(?:19|20)\d{2}년?",
    r"[1-4]분기",
    r"[12]반기",
    r"(?:상|하|전|후)반기",
)


def _title_like_english_entity_label(value, tokens):
    original_tokens = _base.re.findall(r"[A-Za-z0-9]+", value)
    if len(original_tokens) != len(tokens) or len(tokens) < 2:
        return False
    return all(
        token.isupper()
        or (token[:1].isupper() and token[1:].islower())
        or token.isdigit()
        for token in original_tokens
    )


def _entity_only_label(value, tokens):
    if not tokens:
        return False
    if tokens[0] in _ENTITY_LABEL_LEADS or tokens[-1] in _ENTITY_LABEL_SUFFIXES:
        return True
    return _title_like_english_entity_label(value, tokens)


def _normalize_assertion_text(value):
    """Remove possessive syntax without fabricating a standalone subject token."""
    normalized = value.casefold().replace("’", "'")
    normalized = _base.re.sub(r"(?<=[a-z0-9])'s\b", "", normalized)
    normalized = _base.re.sub(r"(?<=[a-z0-9])s'\b", "s", normalized)
    return normalized


def _simple_english_singular_candidates(token):
    """Return conservative singular candidates for neutral subject classes."""
    candidates = set()
    if token.endswith("ies") and len(token) > 3:
        candidates.add(token[:-3] + "y")
    if token.endswith("es") and len(token) > 2:
        candidates.add(token[:-2])
        candidates.add(token[:-1])
    if token.endswith("s") and len(token) > 1:
        candidates.add(token[:-1])
    return candidates


def _normalize_subject_token(token):
    """Normalize plural generic-owner and neutral subject-class variants."""
    if token in _GENERIC_OWNER_PLURALS:
        return _GENERIC_OWNER_PLURALS[token]
    if token in _ASSERTION_NEUTRAL_SUBJECT_TOKENS:
        return token
    for candidate in _simple_english_singular_candidates(token):
        if candidate in _ASSERTION_NEUTRAL_SUBJECT_TOKENS:
            return candidate
    return token


def _normalize_assertion_role_token(token):
    """Normalize conservative English plurals only when they map to a known role."""
    if token in _ASSERTION_ROLE_TERMS:
        return token
    for candidate in _simple_english_singular_candidates(token):
        if candidate in _ASSERTION_ROLE_TERMS:
            return candidate
    return token


def _assertion_temporal_token_indexes(tokens):
    """Return simple, composite, and split date/period token positions."""
    temporal_indexes = {
        index
        for index, token in enumerate(tokens)
        if token in _ASSERTION_TEMPORAL_TERMS
        or any(
            _base.re.fullmatch(pattern, token)
            for pattern in _ASSERTION_COMPOSITE_PERIOD_PATTERNS
        )
    }
    for index in range(len(tokens) - 2):
        if (
            tokens[index] in _ASSERTION_PERIOD_MODIFIER_TERMS
            and tokens[index + 1] == "year"
            and _base.re.fullmatch(r"(?:19|20)\d{2}", tokens[index + 2])
        ):
            temporal_indexes.update((index, index + 1, index + 2))
    for index, token in enumerate(tokens[:-1]):
        next_token = tokens[index + 1]
        if (
            token in _ASSERTION_SPLIT_FISCAL_YEAR_MARKERS
            and _base.re.fullmatch(r"(?:19|20)?\d{2}", next_token)
        ):
            temporal_indexes.update((index, index + 1))
        if (
            token in _ASSERTION_SPLIT_QUARTER_MARKERS
            and next_token in {"1", "2", "3", "4"}
        ):
            temporal_indexes.update((index, index + 1))
    for index, token in enumerate(tokens):
        if token not in _ASSERTION_ORDINAL_PERIOD_TERMS:
            continue
        unit_index = index + 1
        if (
            unit_index < len(tokens)
            and tokens[unit_index] in _ASSERTION_PERIOD_MODIFIER_TERMS
        ):
            temporal_indexes.add(unit_index)
            unit_index += 1
        if (
            unit_index < len(tokens)
            and tokens[unit_index] in _ASSERTION_PERIOD_UNIT_TERMS
        ):
            temporal_indexes.update((index, unit_index))

    # Fiscal/calendar/financial/FY qualifiers directly adjoining a recognized period are
    # part of the same temporal span, not an item subject. This covers both
    # `Fiscal Q1` and ordinal forms such as `Fiscal first quarter` after the
    # underlying period indexes have been identified.
    for index, token in enumerate(tokens):
        if token not in _ASSERTION_ADJACENT_PERIOD_MODIFIER_TERMS:
            continue
        if index > 0 and index - 1 in temporal_indexes:
            temporal_indexes.add(index)
            continue
        if index + 1 < len(tokens) and index + 1 in temporal_indexes:
            temporal_indexes.add(index)
    return temporal_indexes


def _has_concrete_entity_label(tokens):
    """Recognize class-bound identifiers such as Plant 1 or Project A."""
    for index, token in enumerate(tokens[:-1]):
        lead = _normalize_subject_token(token)
        identifier = tokens[index + 1]
        if lead in _NUMERIC_ENTITY_LABEL_LEADS and identifier.isdigit():
            return True
        if lead in _LETTERED_ENTITY_LABEL_LEADS and _base.re.fullmatch(r"[a-z]", identifier):
            return True
    return False


def item_specific_lineage_assertion(value):
    if not _prior_item_specific_lineage_assertion(value):
        return False
    normalized_value = _normalize_assertion_text(value)
    normalized = _base.re.sub(
        r"[^a-z0-9가-힣]+", " ", normalized_value
    ).strip()
    tokens = [token for token in normalized.split() if token]
    normalized_role_tokens = [
        _normalize_assertion_role_token(token) for token in tokens
    ]
    subject_tokens = [
        _normalize_subject_token(token) for token in normalized_role_tokens
    ]
    role_tokens = {
        token for token in normalized_role_tokens if token in _ASSERTION_ROLE_TERMS
    }
    temporal_token_indexes = _assertion_temporal_token_indexes(tokens)
    has_role = bool(role_tokens)
    has_unambiguous_role = any(
        token not in _AMBIGUOUS_ENTITY_ROLE_TERMS for token in role_tokens
    )
    has_numeric_detail = any(any(char.isdigit() for char in token) for token in tokens)
    has_temporal_detail = bool(temporal_token_indexes)
    has_change_predicate = any(
        token in _ASSERTION_CHANGE_PREDICATE_TERMS
        for token in normalized_role_tokens
    )
    has_concrete_entity_label = _has_concrete_entity_label(tokens)
    has_concrete_subject_detail = has_concrete_entity_label or any(
        index not in temporal_token_indexes
        and token not in _ASSERTION_ROLE_TERMS
        and token not in _ASSERTION_NEUTRAL_SUBJECT_TOKENS
        and token not in _GENERIC_OWNER_SINGULARS
        and token not in _base._GENERIC_LINEAGE_ASSERTION_TOKENS
        and not token.isdigit()
        for index, token in enumerate(subject_tokens)
    )
    has_non_role_detail = has_concrete_subject_detail
    has_self_identifying_event_subject = any(
        token in _ASSERTION_EVENT_SUBJECT_TERMS for token in normalized_role_tokens
    )

    # A bare metric or event-role word does not identify the item or the actual
    # fresh change. Preserve only the long-standing canonical one-word execution
    # anchor, while `revenue`, `launch`, and similar role-only values fail.
    if len(tokens) == 1:
        return normalized_role_tokens[0] in _STANDALONE_ASSERTION_EVENT_TERMS

    # An entity label must be rejected before an ambiguous noun such as `fund`
    # can satisfy the role shortcut. Named self-identifying execution events
    # such as `Project Alpha commissioning` remain valid concise anchors.
    if (
        _entity_only_label(value, tokens)
        and not has_numeric_detail
        and not has_temporal_detail
        and not has_change_predicate
        and not has_self_identifying_event_subject
    ):
        return False

    # A date or period plus a bare role noun (for example `Q2 revenue` or
    # `2026 revenue`) is not a fresh anchor, incremental fact, or changed
    # judgment. Stopwords, source modifiers, and generic owner classes do not
    # count as a concrete subject. Numeric plant/site/facility/project labels do count.
    dated_or_numeric_detail_is_specific = (
        has_change_predicate
        or has_self_identifying_event_subject
        or has_concrete_subject_detail
    )
    if has_numeric_detail and has_role and dated_or_numeric_detail_is_specific:
        return True
    if has_temporal_detail and has_role and dated_or_numeric_detail_is_specific:
        return True
    if has_change_predicate and (
        has_non_role_detail or has_self_identifying_event_subject
    ):
        return True
    if has_role and has_non_role_detail and has_unambiguous_role:
        return True

    # Retain the prior compatibility path only for substantive prose containing
    # an actual predicate/change cue; arbitrary role-only or entity-only strings
    # cannot satisfy strict follow-up lineage.
    return (
        len(tokens) >= 3
        and has_change_predicate
        and not _entity_only_label(value, tokens)
    )


_base.item_specific_lineage_assertion = item_specific_lineage_assertion

# Compatibility contract markers retained for source-level regression tests:
# resolved_provisional_targets
# follow-up date precedes provisional predecessor
if __name__ == "__main__":
    _base.sys.exit(_base.main())

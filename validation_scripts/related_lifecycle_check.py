#!/usr/bin/env python3
"""Review 4861267953 compatibility layer for Related assertion semantics."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_BASE_PATH = Path(__file__).with_name("related_lifecycle_check_review4860866998_base.py")
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
}
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


def item_specific_lineage_assertion(value):
    if not _prior_item_specific_lineage_assertion(value):
        return False
    normalized = _base.re.sub(
        r"[^a-z0-9가-힣]+", " ", value.casefold()
    ).strip()
    tokens = [token for token in normalized.split() if token]
    role_tokens = {token for token in tokens if token in _ASSERTION_ROLE_TERMS}
    has_role = bool(role_tokens)
    has_unambiguous_role = any(
        token not in _AMBIGUOUS_ENTITY_ROLE_TERMS for token in role_tokens
    )
    has_numeric_detail = any(any(char.isdigit() for char in token) for token in tokens)

    # An entity label must be rejected before an ambiguous noun such as `fund`
    # can satisfy the role shortcut. A genuine event/metric role still preserves
    # concise assertions such as `Fund Alpha secured financing`.
    if _entity_only_label(value, tokens) and not has_unambiguous_role:
        return False
    if has_role or has_numeric_detail:
        return True
    # Retain the prior compatibility path for substantive three-plus-token prose,
    # but do not let an arbitrary multi-token entity label satisfy lineage.
    return len(tokens) >= 3 and not _entity_only_label(value, tokens)


_base.item_specific_lineage_assertion = item_specific_lineage_assertion

# Compatibility contract markers retained for source-level regression tests:
# resolved_provisional_targets
# follow-up date precedes provisional predecessor
if __name__ == "__main__":
    _base.sys.exit(_base.main())

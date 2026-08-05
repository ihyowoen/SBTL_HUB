#!/usr/bin/env python3
"""Review 4860866998 compatibility layer for Related assertion semantics."""
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

_ASSERTION_ROLE_TERMS = {
    "approve", "approved", "adopt", "adopted", "effective", "enforce", "enforced",
    "launch", "launched", "start", "started", "complete", "completed", "secure",
    "secured", "award", "awarded", "contract", "contracted", "finance", "financed",
    "file", "filed", "disclose", "disclosed", "publish", "published", "announce",
    "announced", "delay", "delayed", "cancel", "cancelled", "canceled", "increase",
    "increased", "decrease", "decreased", "add", "added", "remove", "removed",
    "change", "changed", "shift", "shifted", "move", "moved", "confirm", "confirmed",
    "weaken", "weakened", "strengthen", "strengthened", "invalidate", "invalidated",
    "revenue", "margin", "capacity", "volume", "price", "cost", "date", "stage",
    "status", "eligibility", "probability", "outlook", "judgment", "judgement",
    "승인", "채택", "발효", "시행", "집행", "출시", "착수", "완료", "확보",
    "수주", "계약", "금융", "공시", "발표", "지연", "취소", "증가", "감소",
    "추가", "삭제", "변경", "전환", "이동", "확인", "약화", "강화", "무효화",
    "매출", "마진", "용량", "물량", "가격", "비용", "날짜", "단계", "상태",
    "적격성", "확률", "전망", "판단",
}


def item_specific_lineage_assertion(value):
    if not _base.item_specific_lineage_assertion(value):
        return False
    normalized = _base.re.sub(
        r"[^a-z0-9가-힣]+", " ", value.casefold()
    ).strip()
    tokens = [token for token in normalized.split() if token]
    has_role = any(token in _ASSERTION_ROLE_TERMS for token in tokens)
    has_numeric_detail = any(any(char.isdigit() for char in token) for token in tokens)
    return has_role or has_numeric_detail


_base.item_specific_lineage_assertion = item_specific_lineage_assertion

if __name__ == "__main__":
    _base.main()

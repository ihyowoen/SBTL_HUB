#!/usr/bin/env python3
"""Review 4861267953 compatibility layer for exact-target specificity."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_BASE_PATH = Path(__file__).with_name("stage_lineage_contract_check_review4860866998_base.py")
_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.stage_lineage_contract_check_review4860866998_base",
    _BASE_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load validator base from {_BASE_PATH}")
_base_layer = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_base_layer)

for _name in dir(_base_layer):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base_layer, _name)

_prior_structured_exact_target = _base_layer._structured_exact_target
_GENERIC_TARGET_MODIFIER_TOKENS = {
    "official", "unofficial", "company", "corporate", "business", "issuer",
    "group", "firm", "enterprise", "organization", "organisation", "project",
    "program", "programme", "reported", "published", "public", "private",
    "current", "latest", "new", "additional", "relevant", "specific",
    "formal", "final", "preliminary", "estimated", "expected", "planned",
    "회사", "기업", "법인", "사업", "프로젝트", "프로그램", "공식", "비공식",
    "현재", "최신", "신규", "추가", "관련", "구체", "최종", "예비", "예상",
}


def _is_substantive_predicate_role_token(token):
    """Treat every supported predicate inflection as role vocabulary."""
    return _base_layer._semantic._has_substantive_target_predicate(token)


def _structured_exact_target(value):
    if not _prior_structured_exact_target(value):
        return False
    text = _base_layer._base._normalized_text(value)
    tokens = _base_layer._base.re.findall(r"[a-z0-9가-힣]+", text)
    role_tokens = set()
    for term in (
        tuple(_base_layer._base.STAGE_A_EXACT_TARGET_TERMS)
        + tuple(_base_layer._base.STAGE_A_CONFIRMATION_EVENT_TERMS)
        + tuple(_base_layer._base.STAGE_A_SUBSTANTIVE_TARGET_PREDICATE_TERMS)
        + tuple(_base_layer._base.STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS)
    ):
        role_tokens.update(
            _base_layer._base.re.findall(
                r"[a-z0-9가-힣]+", _base_layer._base._normalized_text(term)
            )
        )
    neutral_tokens = role_tokens | _GENERIC_TARGET_MODIFIER_TOKENS | {
        "and", "or", "the", "a", "an", "of", "for", "to", "in", "on",
        "at", "by", "from", "with", "was", "were", "is", "are", "be",
        "been", "being", "및", "또는", "의", "에", "에서", "대한",
    }
    has_named_subject = any(
        token not in neutral_tokens
        and not token.isdigit()
        and not _is_substantive_predicate_role_token(token)
        for token in tokens
    )
    has_number = any(char.isdigit() for char in text)
    return has_named_subject or has_number


_base_layer._structured_exact_target = _structured_exact_target
if hasattr(_base_layer, "_semantic"):
    _base_layer._semantic._structured_exact_target = _structured_exact_target
if hasattr(_base_layer, "_base"):
    _base_layer._base._structured_exact_target = _structured_exact_target

if __name__ == "__main__":
    _base_layer._base.sys.exit(_base_layer._base.main())

#!/usr/bin/env python3
"""Review 4861791404 compatibility layer for exact-target specificity."""
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
    "source", "entity", "government", "governmental", "regulatory",
    "authority", "agency", "institution",
    "group", "firm", "enterprise", "organization", "organisation", "project",
    "program", "programme", "reported", "published", "public", "private",
    "current", "latest", "new", "additional", "relevant", "specific",
    "formal", "final", "preliminary", "estimated", "expected", "planned",
    "회사", "기업", "법인", "사업", "프로젝트", "프로그램", "공식", "비공식",
    "출처", "정부", "정부기관", "규제기관", "기관", "당국", "조직",
    "현재", "최신", "신규", "추가", "관련", "구체", "최종", "예비", "예상",
}
_SOURCE_CLASS_ROLE_TOKENS = set()
for _term in _base_layer._base.STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS:
    _SOURCE_CLASS_ROLE_TOKENS.update(
        _base_layer._base.re.findall(
            r"[a-z0-9가-힣]+", _base_layer._base._normalized_text(_term)
        )
    )


def _normalize_possessive_subject_text(value):
    """Remove English possessive morphology without dropping the owner name."""
    if not isinstance(value, str):
        return value
    # `company's` tokenizes as `company`, `s`; the suffix must not become a
    # fabricated named subject. Curly apostrophes and plural possessives are
    # normalized as well, while `Project Alpha's` retains `Project Alpha`.
    normalized = _base_layer._base.re.sub(
        r"(?<=[a-z0-9])(?:['’]s)\b",
        "",
        value,
        flags=_base_layer._base.re.IGNORECASE,
    )
    return _base_layer._base.re.sub(
        r"(?<=s)['’](?=\s|$)",
        "",
        normalized,
        flags=_base_layer._base.re.IGNORECASE,
    )


def _simple_english_singular_candidates(token):
    """Return conservative singular candidates for role-vocabulary matching."""
    candidates = set()
    if token.endswith("ies") and len(token) > 3:
        candidates.add(token[:-3] + "y")
    if token.endswith("es") and len(token) > 2:
        candidates.add(token[:-2])
        candidates.add(token[:-1])
    if token.endswith("s") and len(token) > 1:
        candidates.add(token[:-1])
    return candidates


def _is_substantive_predicate_role_token(token):
    """Treat every supported predicate inflection as role vocabulary."""
    return _base_layer._semantic._has_substantive_target_predicate(token)


def _is_simple_plural_role_token(token, role_tokens):
    """Neutralize conservative English plurals of metric/event role nouns."""
    if token in role_tokens:
        return True
    return any(
        candidate in role_tokens
        for candidate in _simple_english_singular_candidates(token)
    )


def _is_source_class_role_token(token):
    """Treat simple English plural source/document nouns as role vocabulary."""
    return _is_simple_plural_role_token(token, _SOURCE_CLASS_ROLE_TOKENS)


def _is_generic_target_modifier_token(token):
    """Neutralize singular and simple-plural generic owner/modifier classes."""
    return _is_simple_plural_role_token(token, _GENERIC_TARGET_MODIFIER_TOKENS)


def _structured_exact_target(value):
    value = _normalize_possessive_subject_text(value)
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
    neutral_tokens = role_tokens | {
        "and", "or", "the", "a", "an", "of", "for", "to", "in", "on",
        "at", "by", "from", "with", "was", "were", "is", "are", "be",
        "been", "being", "및", "또는", "의", "에", "에서", "대한",
    }
    has_named_subject = any(
        token not in neutral_tokens
        and not _is_simple_plural_role_token(token, role_tokens)
        and not _is_generic_target_modifier_token(token)
        and not _is_source_class_role_token(token)
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

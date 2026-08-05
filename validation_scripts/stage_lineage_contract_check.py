#!/usr/bin/env python3
"""Review 4869087245 compatibility layer for causal and exact-target semantics."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_PRIOR_PATH = Path(__file__).with_name(
    "stage_lineage_contract_check_review4868891584_base.py"
)
_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.stage_lineage_contract_check_review4868891584_base",
    _PRIOR_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load validator base from {_PRIOR_PATH}")
_prior = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_prior)

for _name in dir(_prior):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_prior, _name)

_prior_has_bound_interpretation_effect = _prior._has_bound_interpretation_effect
_ENGLISH_CAUSAL_CLAUSE_PATTERN = (
    r"\b(?:because|since|after|before|when|once|whenever)\b|"
    r"(?<!long )\bas\b(?!\s+(?:of|long\s+as)\b)"
)
_KOREAN_CAUSAL_SUFFIX_PATTERN = (
    r"(?:때문에|이므로|므로|이후에|이후|이전에|전에|할 때|했을 때)"
)
_CAUSAL_CLAUSE_PATTERN = (
    rf"(?:{_ENGLISH_CAUSAL_CLAUSE_PATTERN}|{_KOREAN_CAUSAL_SUFFIX_PATTERN})"
)
_TEMPORAL_NOUN_MODIFIER_AUXILIARY_PATTERN = (
    r"(?:would|will|can|could|may|might|must|shall|should|is|are|was|were|"
    r"has|have|had)"
)


def _is_temporal_noun_modifier(text, marker):
    """Treat after/before as modifiers when they qualify a noun, not a clause."""
    marker_text = marker.group(0).lower()
    if marker_text not in {"after", "before"}:
        return False

    remainder = text[marker.end():]
    if remainder.startswith("-"):
        return True

    # Examples: "the filing after review would strengthen ..." and
    # "the filing before publication may weaken ...".  The temporal phrase
    # modifies the preceding noun, while the modal/auxiliary starts the main
    # predicate.  A true dependent clause instead carries its own predicate
    # (for example, "after the outlook improved").
    return bool(
        _prior._base_layer._base.re.match(
            rf"\s+(?:the\s+)?[a-z0-9가-힣-]+"
            rf"(?:\s+[a-z0-9가-힣-]+){{0,3}}\s+"
            rf"{_TEMPORAL_NOUN_MODIFIER_AUXILIARY_PATTERN}\b",
            remainder,
        )
    )


def _next_causal_clause_marker(text):
    for marker in _prior._base_layer._base.re.finditer(
        _CAUSAL_CLAUSE_PATTERN, text
    ):
        if _is_temporal_noun_modifier(text, marker):
            continue
        return marker
    return None


def _independent_clause_for_causal(text):
    """Return only the independent clause, never a causal/temporal dependent suffix."""
    current = text.strip()
    for _ in range(16):
        marker = _next_causal_clause_marker(current)
        if marker is None:
            return current.strip()

        prefix = current[:marker.start()].strip(" ,;")
        remainder = current[marker.end():]
        marker_is_korean_suffix = bool(
            _prior._base_layer._base.re.fullmatch(
                _KOREAN_CAUSAL_SUFFIX_PATTERN,
                marker.group(0),
            )
        )

        # Korean causal/temporal markers are normally suffixes attached to the
        # dependent clause, so the following text is the independent clause.
        if marker_is_korean_suffix:
            current = _prior._base_layer._base.re.sub(
                r"^\s*[,;]?\s*", "", remainder
            ).strip()
            if not current:
                return ""
            continue

        # A leading English subordinator introduces a dependent clause. Keep
        # only the comma/semicolon-delimited main clause that follows it.
        if not prefix:
            separator = _prior._base_layer._base.re.search(r"[,;]\s*", remainder)
            if separator is None:
                return ""
            current = remainder[separator.end():].strip()
            continue

        # For a medial English subordinator, the prefix is the independent
        # clause. The suffix must not be re-evaluated as a standalone effect.
        return prefix

    return ""


def _has_bound_interpretation_effect(value):
    text = _prior._base_layer._base._normalized_text(value)
    if not text:
        return False
    preserve_parentheticals = getattr(
        _prior, "_preserve_parenthetical_subject_modifiers", None
    )
    if preserve_parentheticals is not None:
        text = preserve_parentheticals(text)
    independent_clause = _independent_clause_for_causal(text)
    return bool(
        independent_clause
        and _prior_has_bound_interpretation_effect(independent_clause)
    )


_prior._has_bound_interpretation_effect = _has_bound_interpretation_effect
_prior._base_layer._has_bound_interpretation_effect = _has_bound_interpretation_effect
if hasattr(_prior._base_layer, "_semantic"):
    _prior._base_layer._semantic._has_bound_interpretation_effect = (
        _has_bound_interpretation_effect
    )
if hasattr(_prior._base_layer, "_base"):
    _prior._base_layer._base._has_bound_interpretation_effect = (
        _has_bound_interpretation_effect
    )

_prior_structured_exact_target = _prior._structured_exact_target
_PERIOD_QUALIFIER_TOKEN_PATTERN = (
    r"(?:q[1-4]|[1-4]q|fy\d{2,4}|(?:19|20)\d{2}년?|h[12]|[12]h)"
)
_NUMBERED_EXACT_TARGET_CLASSES = set(
    getattr(
        _prior,
        "_LETTERED_EXACT_TARGET_CLASSES",
        {
            "project", "program", "programme", "plant", "facility", "site",
            "unit", "프로젝트", "프로그램", "공장", "시설", "사업장", "호기",
        },
    )
)


def _is_period_qualifier_token(token):
    return bool(
        _prior._base_layer._base.re.fullmatch(
            _PERIOD_QUALIFIER_TOKEN_PATTERN, token
        )
    )


def _has_numbered_exact_target_subject(tokens):
    """Recognize a class-bound numeric identifier, not an unbound period/amount."""
    return any(
        tokens[index] in _NUMBERED_EXACT_TARGET_CLASSES
        and tokens[index + 1].isdigit()
        for index in range(len(tokens) - 1)
    )


def _structured_exact_target(value):
    """Require a concrete named/item subject; dates and numbers only qualify it."""
    value = _prior._normalize_possessive_subject_text(value)
    text = _prior._base_layer._base._normalized_text(value)
    tokens = _prior._base_layer._base.re.findall(r"[a-z0-9가-힣]+", text)
    role_tokens = set()
    for term in (
        tuple(_prior._base_layer._base.STAGE_A_EXACT_TARGET_TERMS)
        + tuple(_prior._base_layer._base.STAGE_A_CONFIRMATION_EVENT_TERMS)
        + tuple(_prior._base_layer._base.STAGE_A_SUBSTANTIVE_TARGET_PREDICATE_TERMS)
        + tuple(_prior._base_layer._base.STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS)
    ):
        role_tokens.update(
            _prior._base_layer._base.re.findall(
                r"[a-z0-9가-힣]+",
                _prior._base_layer._base._normalized_text(term),
            )
        )
    normalized_prior_value = " ".join(
        _prior._normalize_supported_role_token(token, role_tokens)
        for token in tokens
    )
    if not _prior_structured_exact_target(normalized_prior_value):
        return False

    neutral_tokens = role_tokens | {
        "and", "or", "the", "a", "an", "of", "for", "to", "in", "on",
        "at", "by", "from", "with", "was", "were", "is", "are", "be",
        "been", "being", "및", "또는", "의", "에", "에서", "대한",
    }
    has_named_subject = any(
        token not in neutral_tokens
        and not _prior._is_simple_plural_role_token(token, role_tokens)
        and not _prior._is_generic_target_modifier_token(token)
        and not _prior._is_source_class_role_token(token)
        and not token.isdigit()
        and not _is_period_qualifier_token(token)
        and not (len(token) == 1 and token.isalpha())
        and not _prior._is_substantive_predicate_role_token(token)
        for token in tokens
    )
    has_lettered_subject = _prior._has_lettered_exact_target_subject(tokens)
    has_numbered_subject = _has_numbered_exact_target_subject(tokens)
    return has_named_subject or has_lettered_subject or has_numbered_subject


_prior._structured_exact_target = _structured_exact_target
_prior._base_layer._structured_exact_target = _structured_exact_target
if hasattr(_prior._base_layer, "_semantic"):
    _prior._base_layer._semantic._structured_exact_target = _structured_exact_target
if hasattr(_prior._base_layer, "_base"):
    _prior._base_layer._base._structured_exact_target = _structured_exact_target

if __name__ == "__main__":
    _prior._base_layer._base.sys.exit(_prior._base_layer._base.main())

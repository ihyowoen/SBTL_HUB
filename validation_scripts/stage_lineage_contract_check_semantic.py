#!/usr/bin/env python3
"""Compatibility entry point with semantic confirmation-effect binding."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_BASE_PATH = Path(__file__).with_name("stage_lineage_contract_check_base.py")
_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.stage_lineage_contract_check_base", _BASE_PATH
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load validator base from {_BASE_PATH}")
_base = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_base)

_base.STAGE_A_AMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS = (
    "confirm", "support", "확인", "지지",
)
_base.STAGE_A_UNAMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS = tuple(
    term for term in _base.STAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS
    if term not in _base.STAGE_A_AMBIGUOUS_DIRECT_INTERPRETATION_EFFECT_TERMS
)
_base.STAGE_A_INTERPRETATION_OBJECT_TERMS = (
    "interpretation", "thesis", "outlook", "judgment", "judgement",
    "expectation", "assessment", "probability", "conviction", "conclusion",
    "view", "forecast", "adoption", "eligibility", "timeline", "scenario",
    "case", "risk",
    "해석", "논지", "전망", "판단", "기대", "평가", "확률", "확신",
    "결론", "견해", "예측", "채택", "적격성", "일정", "시나리오",
    "가정", "위험",
)
_base.STAGE_A_OVERLOADED_INTERPRETATION_OBJECT_TERMS = {
    "adoption", "채택",
}
_base.STAGE_A_INTERPRETATION_METRIC_QUALIFIERS = {
    "rate", "rates", "share", "shares", "ratio", "ratios", "percentage",
    "percent", "pct", "volume", "count", "number", "level", "growth",
    "율", "비율", "점유율", "백분율", "물량", "건수", "수치", "수준", "증가율",
}
_base.STAGE_A_EFFECT_AUXILIARY_TERMS = {
    "would", "will", "could", "can", "may", "might", "should", "must",
    "do", "does", "did", "to", "is", "are", "was", "were", "be", "been",
    "being",
}
_base.STAGE_A_EFFECT_BRIDGE_BLOCKERS = {
    "and", "or", "but", "then", "while", "whereas", "although", "however",
    "by", "to", "at", "from", "versus", "vs", "per", "percent", "pct",
    "mw", "mwh", "gw", "gwh", "units", "unit", "tons", "tonnes",
    "그리고", "또는", "하지만", "그러나", "반면", "대비", "에서", "까지",
}
_base.STAGE_A_EFFECT_FIRST_MEASUREMENT_ATTACHMENT_TERMS = {
    "under", "within", "amid", "during", "according", "against", "alongside",
    "beneath", "inside", "in", "아래", "하에서", "중", "내", "가운데",
}
_base.STAGE_A_EFFECT_BRIDGE_PREDICATE_BLOCKERS = {
    "say", "says", "said", "report", "reports", "reported", "reporting",
    "show", "shows", "showed", "shown", "indicate", "indicates", "indicated",
    "state", "states", "stated", "note", "notes", "noted", "describe",
    "describes", "described", "record", "records", "recorded", "find",
    "finds", "found", "disclose", "discloses", "disclosed", "announce",
    "announces", "announced", "publish", "publishes", "published",
    "말한다", "말했다", "보고", "보고했다", "공시", "공시했다", "발표",
    "발표했다", "기재", "기재했다", "나타낸다", "보여준다",
}
_base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS = {
    "report", "document", "filing", "release", "disclosure", "announcement",
    "data", "result", "results", "metric", "measurement", "event",
    "capacity", "production", "output", "volume", "revenue", "sales", "margin",
    "price", "cost", "shipment", "shipments", "order", "orders", "customer",
    "rate", "rates", "share", "shares", "ratio", "ratios", "percentage",
    "percent", "pct", "count", "number", "level", "growth",
    "보고서", "문서", "공시", "자료", "결과", "지표", "측정", "사건",
    "용량", "생산", "생산량", "물량", "매출", "마진", "가격",
    "비용", "출하", "주문", "고객", "율", "비율", "점유율", "백분율",
    "건수", "수치", "수준", "증가율",
}
# Keep every measurement guard and the auxiliary direct-effect fallback aligned
# with the complete exact-metric vocabulary accepted elsewhere by the validator.
_base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS = set(
    _base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS
) | set(_base.STAGE_A_EXACT_TARGET_TERMS)
_base.STAGE_A_EFFECT_FIRST_MEASUREMENT_SUBJECT_TERMS = (
    _base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS
)
_base.STAGE_A_INTERPRETATION_OBJECT_QUALIFIER_TERMS = {
    "for", "of", "regarding", "concerning", "about", "on", "around",
    "toward", "towards", "대한", "관련", "관한",
}
_base.STAGE_A_SUBSTANTIVE_TARGET_PREDICATE_TERMS = (
    "increase", "decrease", "change", "hold", "raise", "lower",
    "launch", "approve", "qualify", "complete", "delay", "cancel",
    "secure", "award", "publish", "file", "disclose", "remain", "unknown",
    "증가", "감소", "변경", "유지", "상향", "하향", "출시", "승인",
    "완료", "지연", "취소", "확보", "수주", "공시", "미확인",
)


def _effect_tokens(clause):
    all_terms = (
        _base.STAGE_A_INTERPRETATION_EFFECT_TERMS
        + _base.STAGE_A_INTERPRETATION_OBJECT_TERMS
    )
    prepared = clause
    for term in sorted(set(all_terms), key=len, reverse=True):
        prepared = _base.re.sub(
            _base._term_pattern(term),
            lambda match: f" {match.group(0)} ",
            prepared,
        )
    return _base.re.findall(r"[a-z0-9가-힣]+", prepared)


def _substantive_target_pattern(term):
    """Match ordinary predicate inflections without reopening substrings."""
    if _base.re.search(r"[가-힣]", term):
        return _base._term_pattern(term)

    irregular = {
        "hold": ("hold", "holds", "holding", "held"),
        "cancel": (
            "cancel", "cancels", "canceled", "cancelled",
            "canceling", "cancelling",
        ),
        "unknown": ("unknown",),
    }
    if term in irregular:
        forms = irregular[term]
    elif term.endswith("e"):
        stem = term[:-1]
        forms = (term, f"{stem}es", f"{stem}ed", f"{stem}ing")
    elif term.endswith("y") and len(term) > 1:
        stem = term[:-1]
        if term[-2] not in "aeiou":
            forms = (term, f"{stem}ies", f"{stem}ied", f"{term}ing")
        else:
            forms = (term, f"{term}s", f"{term}ed", f"{term}ing")
    else:
        plural = f"{term}es" if term.endswith(("s", "x", "z", "ch", "sh", "o")) else f"{term}s"
        forms = (term, plural, f"{term}ed", f"{term}ing")

    body = "|".join(
        _base.re.escape(form) for form in sorted(set(forms), key=len, reverse=True)
    )
    return rf"(?<![\w])(?:{body})(?![\w])"


def _has_substantive_target_predicate(value):
    text = _base._normalized_text(value)
    return any(
        _base.re.search(_substantive_target_pattern(term), text)
        for term in _base.STAGE_A_SUBSTANTIVE_TARGET_PREDICATE_TERMS
    )


def _structured_exact_target(value):
    """Require a claim, metric, event, stage, or date—not a bare entity name."""
    if (
        not _base._structured_component(value)
        or _base._contains_generic_target_fragment(value)
    ):
        return False

    text = _base._normalized_text(value)
    tokens = [
        token
        for token in text.replace("/", " ").replace(":", " ").split()
        if token
    ]
    is_explicit_date = bool(_base.re.fullmatch(
        r"(?:19|20|21)\d{2}(?:[-/.](?:0?[1-9]|1[0-2])"
        r"(?:[-/.](?:0?[1-9]|[12]\d|3[01]))?|년"
        r"(?:\s*(?:0?[1-9]|1[0-2])월"
        r"(?:\s*(?:0?[1-9]|[12]\d|3[01])일)?)?)?",
        text,
    ))
    has_alpha = any(_base.re.search(r"[a-z가-힣]", token) for token in tokens)
    has_exact_role = _base._has_any_term(
        value, _base.STAGE_A_EXACT_TARGET_TERMS
    )
    has_event_role = _base._has_any_term(
        value, _base.STAGE_A_CONFIRMATION_EVENT_TERMS
    )
    has_predicate_role = _has_substantive_target_predicate(value)
    has_qualified_numeric_target = (
        any(char.isdigit() for char in text)
        and has_alpha
        and (has_exact_role or has_event_role or has_predicate_role)
    )
    return (
        is_explicit_date
        or has_qualified_numeric_target
        or has_exact_role
        or has_event_role
        or has_predicate_role
    )


def _valid_evidence_target(value):
    """Require a source class plus a substantive exact target."""
    if isinstance(value, dict):
        source_class = (
            value.get("source_or_document_class")
            or value.get("source_class")
        )
        exact_target = (
            value.get("exact_claim_or_metric")
            or value.get("verification_target")
        )
        return (
            _base._structured_source_class(source_class)
            and _structured_exact_target(exact_target)
        )

    text = _base._normalized_text(value)
    if (
        not text
        or _base._placeholder_only_text(text)
        or _base._contains_generic_target_fragment(text)
    ):
        return False
    matched_source_terms = _base._matching_terms(
        text, _base.STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS
    )
    if not matched_source_terms:
        return False

    target_text = text
    for term in matched_source_terms:
        target_text = _base.re.sub(_base._term_pattern(term), " ", target_text)
    return _structured_exact_target(target_text)


def _effect_bridge_is_semantic(tokens, effect_index, object_index):
    start, end = sorted((effect_index, object_index))
    bridge = tokens[start + 1:end]
    if len(bridge) > 6:
        return False
    if any(any(char.isdigit() for char in token) for token in bridge):
        return False
    if any(token in _base.STAGE_A_EFFECT_BRIDGE_BLOCKERS for token in bridge):
        return False
    if any(token in _base.STAGE_A_EFFECT_BRIDGE_PREDICATE_BLOCKERS for token in bridge):
        return False
    # When the interpretation object appears before the effect, reject a bridge
    # that crosses a separate reported event or measurement noun. Measurement
    # nouns that follow an explicit object qualifier (for/of/regarding/...) are
    # part of the interpretation object itself, so "outlook for capacity would
    # weaken" remains valid while "outlook report says capacity increased" is
    # still blocked.
    if object_index < effect_index:
        measurement_positions = [
            index for index, token in enumerate(bridge)
            if token in _base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS
        ]
        if measurement_positions:
            qualifier_positions = [
                index for index, token in enumerate(bridge)
                if token in _base.STAGE_A_INTERPRETATION_OBJECT_QUALIFIER_TERMS
            ]
            measurement_terms_are_object_qualifiers = bool(qualifier_positions) and all(
                any(qualifier_index < measurement_index for qualifier_index in qualifier_positions)
                for measurement_index in measurement_positions
            )
            if not measurement_terms_are_object_qualifiers:
                return False
    # When any interpretation effect appears first, a preceding measurement
    # subject plus a relational attachment to a later interpretation object
    # describes the measured event, not a change to that interpretation. This
    # applies to directional and direct effects alike: "capacity increased under
    # the outlook" and "production was weakened under the outlook" must fail.
    # The clause has already been split on punctuation and adversative
    # conjunctions, so scan the complete preceding subject region rather than a
    # fixed local window; ordinary facility/location modifiers must not push the
    # measurement noun out of view. Direct transitive effects remain available
    # through their normal path because they do not use a relational attachment.
    if effect_index < object_index and _base._has_any_term(
        tokens[effect_index],
        _base.STAGE_A_INTERPRETATION_EFFECT_TERMS,
    ):
        subject_context = tokens[:effect_index]
        has_measurement_subject = any(
            token in _base.STAGE_A_EFFECT_FIRST_MEASUREMENT_SUBJECT_TERMS
            for token in subject_context
        )
        has_relational_attachment = any(
            token in _base.STAGE_A_EFFECT_FIRST_MEASUREMENT_ATTACHMENT_TERMS
            for token in bridge
        )
        if has_measurement_subject and has_relational_attachment:
            return False
    return True


def _object_position_is_interpretive(tokens, index):
    """Exclude overloaded object terms when they form a measured metric."""
    token = tokens[index]
    if token not in _base.STAGE_A_OVERLOADED_INTERPRETATION_OBJECT_TERMS:
        return True

    neighbors = tokens[max(0, index - 1):index] + tokens[index + 1:index + 3]
    if any(
        neighbor in _base.STAGE_A_INTERPRETATION_METRIC_QUALIFIERS
        for neighbor in neighbors
    ):
        return False

    # An explicit semantic qualifier such as adoption probability/outlook keeps
    # the overloaded term interpretive even if the probability is quantified.
    semantic_qualifiers = set(_base.STAGE_A_INTERPRETATION_OBJECT_TERMS) - set(
        _base.STAGE_A_OVERLOADED_INTERPRETATION_OBJECT_TERMS
    )
    if any(neighbor in semantic_qualifiers for neighbor in neighbors):
        return True

    # Directional movement plus a numeric/metric qualifier makes adoption a
    # measured outcome regardless of whether the movement appears before or
    # after the overloaded object (for example, "10% increase in adoption" or
    # "adoption increased by 10%"). Inspect every directional endpoint allowed
    # by the six-token semantic bridge, plus the two-token measurement modifier
    # immediately outside that endpoint (for example, "10 percent increase").
    directional_positions = [
        candidate_index
        for candidate_index in range(
            max(0, index - 7), min(len(tokens), index + 8)
        )
        if _base._has_any_term(
            tokens[candidate_index],
            _base.STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS,
        )
    ]
    for directional_index in directional_positions:
        context_start = max(0, min(index, directional_index) - 2)
        context_end = min(len(tokens), max(index, directional_index) + 3)
        measurement_context = tokens[context_start:context_end]
        has_measurement = any(
            any(char.isdigit() for char in candidate)
            for candidate in measurement_context
        ) or any(
            candidate in _base.STAGE_A_INTERPRETATION_METRIC_QUALIFIERS
            for candidate in measurement_context
        )
        if has_measurement:
            return False
    return True


def _has_verbal_effect_cue(clause, term):
    pattern = _base._term_pattern(term)
    for match in _base.re.finditer(pattern, clause):
        prefix_tokens = _base.re.findall(r"[a-z0-9가-힣]+", clause[:match.start()])[-3:]
        if any(token in _base.STAGE_A_EFFECT_AUXILIARY_TERMS for token in prefix_tokens):
            return True
    return False


def _has_measurement_context(tokens):
    return any(
        token in _base.STAGE_A_EFFECT_BRIDGE_EVENT_MEASUREMENT_BLOCKERS
        for token in tokens
    ) or any(any(char.isdigit() for char in token) for token in tokens)


def _preserve_parenthetical_subject_modifiers(text):
    """Keep comma-delimited parenthetical modifiers with their subject."""
    parenthetical_leads = {
        "in", "at", "within", "from", "under", "inside", "amid", "during",
        "with", "without", "after", "before", "near", "across", "throughout",
        "located", "based", "on", "by",
        "에서", "내", "안", "아래", "중", "동안", "근처", "기반",
    }
    lead_pattern = "|".join(
        _base.re.escape(term)
        for term in sorted(parenthetical_leads, key=len, reverse=True)
    )

    def replace(match):
        modifier = match.group(1).strip()
        tokens = _effect_tokens(modifier)
        if not tokens or tokens[0] not in parenthetical_leads:
            return match.group(0)
        has_effect_or_object = any(
            _base._has_any_term(
                token,
                _base.STAGE_A_INTERPRETATION_EFFECT_TERMS
                + _base.STAGE_A_INTERPRETATION_OBJECT_TERMS,
            )
            for token in tokens
        )
        if has_effect_or_object:
            return match.group(0)
        return f" {modifier} "

    # Match only a comma whose following token is a known parenthetical lead.
    # This prevents an introductory comma from being paired with a later
    # subject-boundary comma.
    pattern = rf",\s*((?:{lead_pattern})(?![\w])[^,;\n.]*?)\s*,"
    return _base.re.sub(pattern, replace, text)


def _has_bound_interpretation_effect(value):
    """Require semantic or grammatical interpretation-effect binding."""
    text = _base._normalized_text(value)
    if not text:
        return False

    prepared_text = _preserve_parenthetical_subject_modifiers(text)
    clauses = _base.re.split(
        r"[.;,\n]+|\b(?:but|while|whereas|although|however)\b|(?:하지만|그러나|반면)",
        prepared_text,
    )
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        tokens = _effect_tokens(clause)
        object_positions = [
            index for index, token in enumerate(tokens)
            if _base._has_any_term(
                token, _base.STAGE_A_INTERPRETATION_OBJECT_TERMS
            )
            and _object_position_is_interpretive(tokens, index)
        ]
        effect_positions = [
            (index, token)
            for index, token in enumerate(tokens)
            if _base._has_any_term(token, _base.STAGE_A_INTERPRETATION_EFFECT_TERMS)
        ]
        measurement_context = _has_measurement_context(tokens)
        for effect_index, effect_token in effect_positions:
            matched_directional = _base._matching_terms(
                effect_token, _base.STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS
            )
            matched_direct = _base._matching_terms(
                effect_token, _base.STAGE_A_DIRECT_INTERPRETATION_EFFECT_TERMS
            )
            if any(
                _effect_bridge_is_semantic(tokens, effect_index, object_index)
                for object_index in object_positions
            ):
                return True
            if matched_directional:
                continue
            for direct_term in matched_direct:
                # Inflection alone is not semantic evidence. An unbound direct
                # effect needs an auxiliary verbal cue and must not merely
                # describe a measured event such as "capacity weakened by 10%".
                if _has_verbal_effect_cue(clause, direct_term) and not measurement_context:
                    return True
    return False


def _structured_interpretation_effect(value):
    return (
        _base._structured_component(value)
        and not _base._contains_generic_target_fragment(value)
        and _has_bound_interpretation_effect(value)
    )


_base._effect_tokens = _effect_tokens
_base._substantive_target_pattern = _substantive_target_pattern
_base._has_substantive_target_predicate = _has_substantive_target_predicate
_base._structured_exact_target = _structured_exact_target
_base._valid_evidence_target = _valid_evidence_target
_base._effect_bridge_is_semantic = _effect_bridge_is_semantic
_base._object_position_is_interpretive = _object_position_is_interpretive
_base._has_verbal_effect_cue = _has_verbal_effect_cue
_base._has_measurement_context = _has_measurement_context
_base._preserve_parenthetical_subject_modifiers = _preserve_parenthetical_subject_modifiers
_base._has_bound_interpretation_effect = _has_bound_interpretation_effect
_base._structured_interpretation_effect = _structured_interpretation_effect

for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)

if __name__ == "__main__":
    _base.sys.exit(_base.main())
"""Bounded quantity/state observations shared by Prompt 0.6 entrypoints.

This is not an entailment engine. Numeric spans retain operators and Korean
money scale. State observations retain the reason for non-realization. Unknown
Korean state syntax does not acquire realized strength by falling through.
Evidence authority and entity/metric/argument binding remain caller contracts.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

QUANT_SIGNAL_RE = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(?P<bound><=|>=|≤|≥|<|>|≈|~)?\s*"
    r"(?:(?P<currency_code_prefix>USD|EUR|GBP|KRW|CNY|RMB|JPY|AUD|CAD|CHF|HKD|SGD)\s+)?"
    r"(?P<sign>[+−﹣－＋-])?\s*"
    r"(?P<currency>[$€£¥₩]?)"
    r"(?P<number>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+,\d+|\d+(?:\.\d+)?)"
    r"(?:\s*(?P<korean_magnitude>백만|천|만|억|조)?\s*(?P<korean_currency>달러|유로|위안|원|엔))?"
    r"(?:\s*(?P<magnitude>thousand|million|billion|trillion|mn|bn|tn|k|m|b)\b)?"
    r"(?:\s*(?P<currency_code_suffix>USD|EUR|GBP|KRW|CNY|RMB|JPY|AUD|CAD|CHF|HKD|SGD)\b)?"
    r"(?:\s*(?P<unit>%|x|mw|gw|gwh|mwh|kwh|tpa|kt|mt|sqm|m²|km|tons?|tonnes?))?"
    r"(?:\s+(?P<generic_unit>"
    r"(?!(?:and|or|but|yet|for|from|to|at|in|on|by|with|because|while|whereas|per|previously|currently|planned|approved|started|delayed|completed|commercial|subject|target|project|plant|facility|capacity|investment|production)\b)"
    r"[A-Za-z][A-Za-z0-9²³_-]{0,31}"
    r"(?:\s+(?!(?:and|or|but|yet|for|from|to|at|in|on|by|with|because|while|whereas|per|previously|currently|planned|approved|started|delayed|completed|commercial|subject|target|project|plant|facility|capacity|investment|production)\b)"
    r"[A-Za-z][A-Za-z0-9²³_-]{0,31}){0,3}"
    r"))?"
    r"(?:(?P<unit_separator>\s+per\s+|\s*/\s*)"
    r"(?P<unit_denominator>"
    r"[A-Za-z][A-Za-z0-9²³_-]{0,31}"
    r"(?:\s+(?!(?:and|or|but|yet|for|from|to|at|in|on|by|with|because|while|whereas|previously|currently|planned|approved|started|delayed|completed|commercial|subject|target|project|plant|facility|capacity|investment|production)\b)"
    r"[A-Za-z][A-Za-z0-9²³_-]{0,31}){0,3}"
    r"))?"
    r"(?![A-Za-z0-9])",
    re.IGNORECASE,
)


def _canonical_numeric_text(raw):
    value=raw
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?",value):
        value=value.replace(",","")
    elif "," in value and "." not in value:
        value=value.replace(",",".")
    whole,sep,fraction=value.partition(".")
    whole=whole.lstrip("0") or "0"
    if sep:
        fraction=fraction.rstrip("0")
        value=whole+(("." + fraction) if fraction else "")
    else:
        value=whole
    return value or "0"


MAGNITUDE_CANONICAL = {
    "thousand":"k", "k":"k",
    "million":"m", "mn":"m", "m":"m",
    "billion":"bn", "bn":"bn", "b":"bn",
    "trillion":"tn", "tn":"tn",
}


SIGN_CANONICAL = {"−": "-", "﹣": "-", "－": "-", "＋": "+"}
KOREAN_SCALE = {"": 0, "천": 3, "만": 4, "백만": 6, "억": 8, "조": 12}
KOREAN_CURRENCY = {"원": "krw", "달러": "dollar_unspecified", "유로": "eur", "위안": "cny", "엔": "jpy"}
# A bare Korean "dollar" is not necessarily USD. Preserve that ambiguity.


def _shift_decimal(number: str, places: int) -> str:
    """Exact power-of-ten shift without float or Decimal context rounding."""
    whole, _, fraction = number.partition(".")
    digits = whole + fraction
    point = len(whole) + places
    if point >= len(digits):
        return _canonical_numeric_text(digits + "0" * (point - len(digits)))
    return _canonical_numeric_text(digits[:point] + "." + digits[point:])


@dataclass(frozen=True)
class QuantityObservation:
    start: int
    end: int
    raw: str
    bound: str
    sign: str
    number: str
    currency_symbol: str
    magnitude: str
    currency_code: str
    unit: str
    denominator: str

    @property
    def identity(self):
        return (self.bound, self.sign, self.number, self.currency_symbol,
                self.magnitude, self.currency_code, self.unit, self.denominator)

    @property
    def signal(self):
        unit = self.unit
        if self.denominator:
            unit = (unit or "1") + "/" + self.denominator
        suffix = " ".join(x for x in (self.magnitude, self.currency_code, unit) if x)
        return (f"{self.bound}{self.sign}{self.currency_symbol}{self.number}"
                + (" " + suffix if suffix else ""))


def quantity_from_match(match) -> QuantityObservation:
    groups = match.groupdict()
    get = lambda key: groups.get(key) or ""
    bound = {"≤": "<=", "≥": ">=", "≈": "~"}.get(get("bound"), get("bound"))
    sign = SIGN_CANONICAL.get(get("sign"), get("sign"))
    number = _canonical_numeric_text(get("number"))
    currency = get("currency").lower()
    prefix, suffix = get("currency_code_prefix").lower(), get("currency_code_suffix").lower()
    currency_code = prefix + "/" + suffix if prefix and suffix and prefix != suffix else prefix or suffix
    raw_magnitude = get("magnitude")
    unit = get("unit").lower()
    generic = get("generic_unit").lower()
    denominator = get("unit_denominator").lower()
    bridge = (match.string[match.end("number"):match.start("magnitude")]
              if raw_magnitude and match.start("magnitude") >= 0 else "")
    metre = (raw_magnitude == "m" and bool(re.search(r"\s", bridge))
             and not any((currency, prefix, suffix, unit, generic, denominator)))
    magnitude = "" if metre else MAGNITUDE_CANONICAL.get(raw_magnitude.lower(), "")
    if generic in {"and", "or", "but", "yet", "for", "from", "to", "at", "in", "on", "by", "with",
                   "because", "while", "whereas", "previously", "currently", "planned", "approved",
                   "started", "delayed", "completed", "commercial", "subject", "target"}:
        generic = ""
    unit = "meter" if metre else unit or generic
    if get("korean_currency"):
        # Scale is part of the amount, not an ignorable trailing word.
        number = _shift_decimal(number, KOREAN_SCALE[get("korean_magnitude")])
        korean_code = KOREAN_CURRENCY[get("korean_currency")]
        currency_code = (currency_code + "/" + korean_code
                         if currency_code and currency_code != korean_code else korean_code)
    return QuantityObservation(match.start(), match.end(), match.group(0), bound, sign,
                               number, currency, magnitude, currency_code, unit, denominator)


def quantitative_signal_from_match(match):
    return quantity_from_match(match).signal


# A conservative whole-expression detector. Compound Korean money is currently
# explicitly unsupported rather than split into unrelated numbers or truncated.
_KOREAN_MONEY_EXPRESSION = re.compile(
    r"(?<![0-9])(?:[+−﹣－＋-]\s*)?[0-9][0-9,.]*"
    r"(?:\s*(?:백만|천|만|억|조)\s*(?:[0-9][0-9,.]*)?)*"
    r"\s*(?:달러|유로|위안|원|엔)"
)


def unsupported_quantity_spans(text):
    spans = []
    for match in _KOREAN_MONEY_EXPRESSION.finditer(text):
        whole = match.group(0)
        parsed = QUANT_SIGNAL_RE.fullmatch(whole)
        if parsed is None or not parsed.groupdict().get("korean_currency"):
            spans.append((match.start(), match.end(), whole))
    return tuple(spans)


def quantitative_observations(text):
    unsupported = unsupported_quantity_spans(text)
    return tuple(quantity_from_match(match) for match in QUANT_SIGNAL_RE.finditer(text)
                 if not any(match.start() < end and match.end() > start
                            for start, end, _ in unsupported))


def quantitative_signals(text):
    # Never let an unsupported evidence expression authorize an inner number.
    return tuple(observation.signal for observation in quantitative_observations(text))

NON_REALIZED_CHANGED_STATE_PREFIX_RE = re.compile(
    r"(?:"
    r"\b(?:not|never|without)\b(?:\s+\w+){0,3}\s*$"
    r"|\bno\s+(?:current\s+)?(?:\w+\s+){0,2}$"
    r"|\b(?:is|are|was|were|has|have|had|do|does|did|will|would|can|could)\s+not(?:\s+\w+){0,2}\s*$"
    r"|\b(?:plan(?:ned)?|target(?:ed)?|propos(?:ed|al)|schedul(?:ed|ing))\b(?:\s+\w+){0,2}\s*$"
    r"|n['’]t(?:\s+\w+){0,2}\s*$"
    r")",
    re.IGNORECASE,
)


TENTATIVE_CHANGED_STATE_PREFIX_RE = re.compile(
    r"(?:"
    r"\b(?:may|might|could|possibly|potentially|likely\s+to|expected\s+to)\b(?:\s+\w+){0,3}\s*$"
    r"|\bsubject\s+to\b(?:\s+\w+){0,3}\s*$"
    r")",
    re.IGNORECASE,
)


NON_REALIZED_CHANGED_STATE_SUFFIX_RE = re.compile(
    r"^\s*(?:"
    r"(?:has|have|had|is|are|was|were|will|would|can|could)?\s*(?:not|never|n['’]t)\b"
    r"|not\s+yet\b"
    r"|(?:is|are|remains?|remain)\s+(?:planned|targeted|expected|scheduled)\b"
    r")",
    re.IGNORECASE,
)


CLAUSE_BOUNDARY_RE = re.compile(
    r"[.;:!?]|\b(?:but|yet|however|although|though|whereas)\b",
    re.IGNORECASE,
)


COORDINATING_NEW_SUBJECT_RE = re.compile(
    r"(?i:\b(?:and|or)\s+)"
    r"(?:(?i:it|they|he|she|we|you|this|that|these|those)\b"
    r"|(?i:the|a|an)\s+(?:[A-Za-z][A-Za-z0-9&._-]*\s+){0,2}[A-Za-z][A-Za-z0-9&._-]*\b"
    r"|[A-Z][A-Za-z0-9&._-]{1,}\b"
    r"|[a-z][A-Za-z0-9&._-]{1,}\s+(?="
    r"(?i:is|are|was|were|has|have|had|will|shall|may|might|could|"
    r"start(?:ed|ing)?|begin|began|begun|commence(?:d)?|approve(?:d)?|"
    r"delay(?:ed)?|complete(?:d)?|resume(?:d)?|restart(?:ed)?|"
    r"suspend(?:ed)?|cancel(?:led|ed)?|sign(?:ed)?|launch(?:ed)?|ship(?:ped|ping)?)\b"
    r"))"
)


CLAUSE_NEGATION_RE = re.compile(
    r"\b(?:not|never|without|neither|nor)\b|n['’]t\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class StateObservation:
    start: int
    end: int
    raw: str
    strength: int
    classification: str
    reason: str


def _state_observation(match, strength, classification, reason):
    return StateObservation(match.start(), match.end(), match.group(0), strength, classification, reason)


def _independent_context(text, match):
    # An and/or conjunct ends local negation, but does not end a surrounding
    # if/then condition. Sentence/contrast boundaries do end that condition.
    boundaries = []
    for boundary in CLAUSE_BOUNDARY_RE.finditer(text):
        if boundary.group(0) == ".":
            before, after = text[:boundary.start()], text[boundary.end():]
            if before[-1:].isdigit() and after[:1].isdigit():
                continue
            # A dotted initialism is not an independent assertion boundary.
            if (re.search(r"(?:\b[A-Za-z]\.){2,}$", text[:boundary.end()])
                    or (re.search(r"\b[A-Za-z]$", before) and re.match(r"[A-Za-z]\.", after))):
                continue
        boundaries.append(boundary)
    left = max((b.end() for b in boundaries if b.end() <= match.start()), default=0)
    right = min((b.start() for b in boundaries if b.start() >= match.end()), default=len(text))
    return text[left:match.start()], text[match.end():right]


_CONDITIONAL_EN = re.compile(
    r"\b(?:if|unless|whether|assuming|provided\s+that|providing\s+that|in\s+the\s+event\s+that)\b",
    re.IGNORECASE,
)
_KOREAN_NEXT_SUBJECT = re.compile(r"(?:[가-힣](?:고|며|는데)|,)\s+(?P<subject>(?:[가-힣]{2,}|[A-Z][A-Za-z0-9_-]+)(?:은|는|이|가))\s+")
_KOREAN_CONTRAST = re.compile(r"(?:지만|반면|그러나|하지만|그런데)\s*")


def _korean_state_observation(text, match, prefix, suffix):
    # This branch handles only Korean state markers. English grammar remains
    # separate; Hangul elsewhere in an English clause cannot flip its modality.
    boundaries = list(_KOREAN_CONTRAST.finditer(prefix))
    if boundaries:
        prefix = prefix[boundaries[-1].end():]
    contrast = _KOREAN_CONTRAST.search(suffix)
    if contrast:
        suffix = suffix[:contrast.start()]
    next_subject = _KOREAN_NEXT_SUBJECT.search(suffix)
    if next_subject:
        suffix = suffix[:next_subject.start("subject")]
    # Only the local predicate determines negation/condition; later independent
    # subjects are outside this occurrence's suffix scope.
    if (re.search(r"(?:안|못)\s*$|(?:미|비)$", prefix)
            or re.search(r"(?:지\s*(?:않|못)|\b아니|(?:적|바)\s*(?:이\s*)?없)", suffix)):
        return _state_observation(match, 0, "negated", "korean_local_negation")
    if (re.search(r"(?:만약|경우에만)\s*[^.;!?]*$", prefix)
            or re.search(r"^(?:[가-힣]*?(?:다면|되면|하면|될\s*경우|된\s*경우)|\s*(?:조건|여부))", suffix)):
        return _state_observation(match, 0, "conditional", "korean_conditional_predicate")
    if re.search(r"(?:예정|계획|목표|전망|예상|기대|추진|검토|해야|하여야|필요)", suffix):
        return _state_observation(match, 0, "prospective", "korean_not_realized")
    if re.search(r"(?:가능성|가능|[될할]\s*수\s*있)", suffix):
        return _state_observation(match, 1, "tentative", "korean_possibility")
    if re.search(r"(?:예정|내년|향후|앞으로)\s*$", prefix):
        return _state_observation(match, 0, "prospective", "korean_future_context")
    if re.match(r"^(?:했|됐|하였|되었|한다|된다|중|\s*(?:완료|확정|개시|시작|중))", suffix):
        # Approval-in-progress is not an approval already granted.
        if match.group(0) == "승인" and re.match(r"^\s*중", suffix):
            return _state_observation(match, 0, "pending", "approval_in_progress")
        return _state_observation(match, 2, "realized", "korean_asserted_predicate")
    if re.match(r"^(?:을|를)\s*(?:받았|마쳤|완료했|시작했)", suffix):
        return _state_observation(match, 2, "realized", "korean_completed_object")
    if re.search(r"(?:중|완료)$", match.group(0)):
        return _state_observation(match, 2, "realized", "korean_asserted_marker")
    return _state_observation(match, 0, "unsupported", "korean_state_syntax_unresolved")


def state_observation(text, match):
    """Return an explicit observation, never infer realization for unknown Korean syntax."""
    if match is None or not isinstance(text, str):
        raise ValueError("state observation requires text and a marker match")
    local_prefix, local_suffix = _independent_context(text, match)
    if re.search(r"[가-힣]", match.group(0)):
        return _korean_state_observation(text, match, local_prefix, local_suffix)
    if re.search(r"\bto\s+(?:be\s+)?$", local_prefix, re.IGNORECASE):
        return _state_observation(match, 0, "prospective", "english_infinitive")
    if _CONDITIONAL_EN.search(local_prefix) or _CONDITIONAL_EN.search(local_suffix):
        return _state_observation(match, 0, "conditional", "english_conditional_scope")
    prefix=text[max(0,match.start()-96):match.start()]
    suffix=text[match.end():min(len(text),match.end()+64)]
    clause_prefix=text[:match.start()]
    boundaries=list(CLAUSE_BOUNDARY_RE.finditer(clause_prefix))
    coordinate_boundaries=list(COORDINATING_NEW_SUBJECT_RE.finditer(clause_prefix))
    all_boundaries=boundaries+coordinate_boundaries
    if all_boundaries:
        clause_prefix=clause_prefix[max(item.end() for item in all_boundaries):]
    if re.match(
        r"(?:commercial\s+production|production|construction)\b",
        match.group(0),re.IGNORECASE,
    ):
        noun_subject_conjunction=re.search(
            r"\b(?:and|or)\s+$",clause_prefix,re.IGNORECASE
        )
        if noun_subject_conjunction:
            clause_prefix=clause_prefix[noun_subject_conjunction.end():]
    if re.match(
        r"(?:start(?:ed|ing)?|begin|began|begun|commence(?:d)?|approve(?:d)?|"
        r"delay(?:ed)?|complete(?:d)?|resume(?:d)?|restart(?:ed)?|"
        r"suspend(?:ed)?|cancel(?:led|ed)?|sign(?:ed)?|launch(?:ed)?|"
        r"ship(?:ped|ping)?)\b",
        match.group(0),re.IGNORECASE,
    ):
        trailing_subject_conjunction=re.search(
            r"\b(?:and|or)\s+"
            r"(?:(?:the|a|an)\s+)?[A-Za-z][A-Za-z0-9&._-]{1,}"
            r"(?:\s+(?:is|are|was|were|has|have|had|will|shall|may|might|could))?"
            r"\s+$",
            clause_prefix,re.IGNORECASE,
        )
        if trailing_subject_conjunction:
            clause_prefix=clause_prefix[trailing_subject_conjunction.end():]
    clause_prefix=re.sub(r"\bnot\s+only\b","",clause_prefix,flags=re.IGNORECASE)
    if CLAUSE_NEGATION_RE.search(clause_prefix):
        return _state_observation(match, 0, "non_realized", "english_negation_or_prospective")
    if NON_REALIZED_CHANGED_STATE_PREFIX_RE.search(prefix):
        return _state_observation(match, 0, "non_realized", "english_negation_or_prospective")
    if NON_REALIZED_CHANGED_STATE_SUFFIX_RE.search(suffix):
        return _state_observation(match, 0, "non_realized", "english_negation_or_prospective")
    if re.search(
        r"\b(?:risk|chance|possibility|prospect|threat)\s+(?:of|for)\s+(?:being\s+)?$"
        r"|\bpotential\s+(?:for|of)\s+(?:being\s+)?$",
        prefix,re.IGNORECASE,
    ):
        return _state_observation(match, 0, "non_realized", "english_negation_or_prospective")
    if re.search(
        r"\b(?:must)\s+"
        r"(?:(?:be|have|been|being)\s+){0,3}$"
        r"|\b(?:needs?|needed)\s+to\s+(?:(?:be|have|been|being)\s+){0,3}$"
        r"|\b(?:is|are|was|were|be|been)\s+required\s+to\s+"
        r"(?:(?:be|have|been|being)\s+){0,3}$",
        prefix,re.IGNORECASE,
    ):
        return _state_observation(match, 0, "non_realized", "english_negation_or_prospective")
    if re.search(
        r"\b(?:would|should|can)\s+"
        r"(?:(?:(?:not\s+)?(?:be|have|been|being)|"
        r"[A-Za-z][A-Za-z-]*ly|eventually|probably|possibly|likely|"
        r"soon|later|ultimately|still)\s+){0,6}$",
        prefix,re.IGNORECASE,
    ) or re.search(r"\b(?:would|should|can)\s*$",prefix,re.IGNORECASE):
        return _state_observation(match, 0, "non_realized", "english_negation_or_prospective")
    if re.search(
        r"\b(?:is|are|was|were|be|been)\s+"
        r"(?:going\s+to|set\s+to|due\s+to)\s+"
        r"(?:(?:be|have|been|being)\s+){0,3}$",
        prefix,re.IGNORECASE,
    ):
        return _state_observation(match, 0, "non_realized", "english_negation_or_prospective")
    if re.search(
        r"\b(?:will|shall)\s+"
        r"(?:(?:(?:not\s+)?(?:be|have|been|being)|"
        r"[A-Za-z][A-Za-z-]*ly|eventually|probably|possibly|likely|"
        r"soon|later|ultimately|still)\s+){0,6}$",
        prefix,re.IGNORECASE,
    ) or re.search(r"\b(?:will|shall)\s*$",prefix,re.IGNORECASE):
        return _state_observation(match, 0, "non_realized", "english_negation_or_prospective")
    if TENTATIVE_CHANGED_STATE_PREFIX_RE.search(prefix):
        return _state_observation(match, 1, "tentative", "english_possibility")
    return _state_observation(match, 2, "realized", "english_asserted_marker")



def changed_state_match_strength(text, match):
    return state_observation(text, match).strength

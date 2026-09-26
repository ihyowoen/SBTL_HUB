"""Bounded quantity/state observations shared by Prompt 0.6 entrypoints.

This is not an entailment engine. Numeric spans retain operators and Korean
money scale. State observations retain the reason for non-realization. Unknown
Korean state syntax does not acquire realized strength by falling through.
Evidence authority and entity/metric/argument binding remain caller contracts.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Share the suffix boundary between extraction and whole-expression coverage;
# case particles such as '5억의' must not erase the scale on either path.
_KOREAN_QUANTITY_END = (
    r"(?=$|[^가-힣0-9]|이다|이며|이고|이었|였|으로|에서|까지|부터|보다|정도|규모|수준|[이가을를은는의에도과와])"
)

QUANT_SIGNAL_RE = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(?P<bound><=|>=|≤|≥|<|>|≈|~)?\s*"
    r"(?:(?P<currency_code_prefix>USD|EUR|GBP|KRW|CNY|RMB|JPY|AUD|CAD|CHF|HKD|SGD)\s+)?"
    r"(?P<sign>[+−﹣－＋-])?\s*"
    r"(?:(?P<country_dollar_prefix>A|C)\$\s*|(?P<currency>[$€£¥₩]?))"
    r"(?P<number>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+,\d+|\d+(?:\.\d+)?)"
    r"(?:\s*(?P<korean_magnitude>백만|십|백|천|만|억|조)"
    r"(?=달러|유로|위안|원|엔|" + _KOREAN_QUANTITY_END + r"))?"
    r"(?:\s*(?P<korean_currency>달러|유로|위안|원|엔))?"
    r"(?:\s*(?P<magnitude>thousand|million|billion|trillion|mn|bn|tn|k|m|b)\b)?"
    r"(?:\s*(?P<currency_code_suffix>USD|EUR|GBP|KRW|CNY|RMB|JPY|AUD|CAD|CHF|HKD|SGD)\b)?"
    r"(?:\s*(?P<unit>%|x|gwh|mwh|kwh|gw|mw|tpa|kt|mt|sqm|m²|km|tonnes?|tons?|t)(?![A-Za-z0-9]))?"
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

TEMPORAL_EN_YEAR_QUARTER_VALUE = (
    r"(?:19|20|21)\d{2}(?:\s+(?:q[1-4]|(?:first|second|third|fourth)\s+quarter))?"
    r"|(?:the\s+)?(?:q[1-4]|(?:first|second|third|fourth)\s+quarter)"
    r"(?:\s+(?:of\s+)?(?:19|20|21)\d{2})?"
)
TEMPORAL_EN_MONTH_VALUE = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"(?:\s+(?:19|20|21)\d{2})?"
)
TEMPORAL_EN_MONTH_RANGE_VALUE = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"(?:\s+(?:19|20|21)\d{2})?"
    r"\s+(?:to|through)\s+"
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"(?:\s+(?:19|20|21)\d{2})?"
)
TEMPORAL_EN_PERIOD_VALUE = (
    r"(?:" + TEMPORAL_EN_YEAR_QUARTER_VALUE + r"|" + TEMPORAL_EN_MONTH_VALUE + r")"
)
TEMPORAL_PERIOD_SPAN_RE = re.compile(
    r"(?:"
    r"\b(?:in|during|by|on|since|through|until|as\s+of)\s+"
    r"(?P<en_period>" + TEMPORAL_EN_PERIOD_VALUE + r")\b"
    r"|\bfor\s+(?P<en_for_period>" + TEMPORAL_EN_YEAR_QUARTER_VALUE + r")\b"
    r"|\bfrom\s+(?P<en_month_range>" + TEMPORAL_EN_MONTH_RANGE_VALUE + r")\b"
    r"|\bfrom\s+(?P<en_from_period>"
    r"(?:" + TEMPORAL_EN_YEAR_QUARTER_VALUE
    + r"|(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
      r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
      r"\s+(?:19|20|21)\d{2})"
    r")\b"
    r"|(?P<ko_period>"
    r"(?:19|20|21)\d{2}\s*년(?:도)?\s*[1-4]\s*분기"
    r"|[1-4]\s*분기(?:\s*(?:19|20|21)\d{2}\s*년)?"
    r"|(?:19|20|21)\d{2}\s*년(?:도|에|부터|까지)?"
    r"))",
    re.IGNORECASE,
)

_MONTH_ALIASES = {
    "jan":"january","feb":"february","mar":"march","apr":"april",
    "jun":"june","jul":"july","aug":"august","sep":"september","sept":"september",
    "oct":"october","nov":"november","dec":"december",
}
_QUARTER_ORDINALS = {"first":"1","second":"2","third":"3","fourth":"4"}


def canonical_temporal_period(raw):
    value=re.sub(r"\s+"," ",str(raw or "").strip()).casefold()
    value=re.sub(r"^the\s+","",value)
    if not value:
        return ""
    korean_year=re.fullmatch(
        r"(?P<year>(?:19|20|21)\d{2})\s*년(?P<suffix>도|에|부터|까지)?",
        value,
    )
    if korean_year:
        suffix=korean_year.group("suffix") or ""
        if suffix == "에":
            suffix=""
        return f"{korean_year.group('year')}년{suffix}"
    month_range=re.fullmatch(
        r"(?P<start>jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        r"(?:\s+(?P<start_year>(?:19|20|21)\d{2}))?"
        r"\s+(?:to|through)\s+"
        r"(?P<end>jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        r"(?:\s+(?P<end_year>(?:19|20|21)\d{2}))?",
        value,
    )
    if month_range:
        start=_MONTH_ALIASES.get(month_range.group("start"),month_range.group("start"))
        end=_MONTH_ALIASES.get(month_range.group("end"),month_range.group("end"))
        start_year=month_range.group("start_year") or ""
        end_year=month_range.group("end_year") or ""
        if bool(start_year) ^ bool(end_year):
            shared_year=start_year or end_year
            start_year=start_year or shared_year
            end_year=end_year or shared_year
        left=start + (f" {start_year}" if start_year else "")
        right=end + (f" {end_year}" if end_year else "")
        return f"{left}-to-{right}"
    korean_quarter=re.fullmatch(
        r"(?:(?P<year1>(?:19|20|21)\d{2})\s*년(?:도)?\s*)?"
        r"(?P<quarter>[1-4])\s*분기"
        r"(?:\s*(?P<year2>(?:19|20|21)\d{2})\s*년)?",
        value,
    )
    if korean_quarter:
        year=korean_quarter.group("year1") or korean_quarter.group("year2") or ""
        return f"{year} q{korean_quarter.group('quarter')}".strip()
    english_quarter=re.fullmatch(
        r"(?:(?P<year1>(?:19|20|21)\d{2})\s+)?"
        r"(?:q(?P<qnum>[1-4])|(?P<ordinal>first|second|third|fourth)\s+quarter)"
        r"(?:\s+(?:of\s+)?(?P<year2>(?:19|20|21)\d{2}))?",
        value,
    )
    if english_quarter:
        quarter=english_quarter.group("qnum") or _QUARTER_ORDINALS[english_quarter.group("ordinal")]
        year=english_quarter.group("year1") or english_quarter.group("year2") or ""
        return f"{year} q{quarter}".strip()
    parts=value.split(" ",1)
    head=_MONTH_ALIASES.get(parts[0],parts[0])
    return head + ((" " + parts[1]) if len(parts)>1 else "")


def _period_group_value(match):
    groups=match.groupdict()
    return (
        groups.get("en_period")
        or groups.get("en_for_period")
        or groups.get("en_month_range")
        or groups.get("en_from_period")
        or groups.get("ko_period")
        or ""
    )


def temporal_period_spans(text):
    if not isinstance(text, str):
        return ()
    return tuple((match.start(), match.end(), match.group(0))
                 for match in TEMPORAL_PERIOD_SPAN_RE.finditer(text))


_BOUNDARY_TEMPORAL_OPERATOR_RE = re.compile(
    r"^(?P<operator>since|until|by|through|as\s+of)\b",
    re.IGNORECASE,
)


def _canonical_temporal_observation(match):
    period=canonical_temporal_period(_period_group_value(match))
    operator=_BOUNDARY_TEMPORAL_OPERATOR_RE.match(match.group(0).strip())
    if operator is None:
        return period
    canonical_operator=re.sub(
        r"\s+"," ",operator.group("operator").casefold()
    )
    return f"{canonical_operator}:{period}"


def temporal_period_observations(text):
    if not isinstance(text, str):
        return ()
    return tuple(
        (match.start(), match.end(), _canonical_temporal_observation(match))
        for match in TEMPORAL_PERIOD_SPAN_RE.finditer(text)
    )


def _overlaps_any_span(start, end, spans):
    return any(start < span_end and end > span_start
               for span_start, span_end, _ in spans)



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
KOREAN_SCALE = {"": 0, "십": 1, "백": 2, "천": 3, "만": 4, "백만": 6, "억": 8, "조": 12}
KOREAN_CURRENCY = {"원": "krw", "달러": "dollar_unspecified", "유로": "eur", "위안": "cny", "엔": "jpy"}
COUNTRY_DOLLAR_PREFIX = {"a": "aud", "c": "cad"}
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
    country_dollar = COUNTRY_DOLLAR_PREFIX.get(get("country_dollar_prefix").lower(), "")
    codes = []
    for code in (prefix, suffix, country_dollar):
        if code and code not in codes:
            codes.append(code)
    currency_code = "/".join(codes)
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
    # A scale is meaningful even when currency is unstated. Do not infer KRW.
    if (get("korean_magnitude") == "조" and not get("korean_currency")
            and re.search(r"(?:^|[^가-힣])제\s*$", match.string[:match.start("number")])):
        # 제5조 is an ordinal article, not a five-trillion amount.
        unit = "조항"
    elif get("korean_magnitude"):
        number = _shift_decimal(number, KOREAN_SCALE[get("korean_magnitude")])
    if get("korean_currency"):
        korean_code = KOREAN_CURRENCY[get("korean_currency")]
        currency_code = (currency_code + "/" + korean_code
                         if currency_code and currency_code != korean_code else korean_code)
    return QuantityObservation(match.start(), match.end(), match.group(0), bound, sign,
                               number, currency, magnitude, currency_code, unit, denominator)


def quantitative_signal_from_match(match):
    return quantity_from_match(match).signal


# Match the *whole* expression before exposing numeric tokens. Composition
# (e.g. 6십억원 or 1조 2000억) is still outside this bounded grammar. The
# detector includes bare scales so missing currency cannot hide a partial parse.
_KOREAN_MONEY_EXPRESSION = re.compile(
    r"(?<![0-9])(?:[+−﹣－＋-]\s*)?[0-9][0-9,.]*"
    r"(?:(?:\s*(?:백만|십|백|천|만|억|조)\s*(?:[0-9][0-9,.]*)?)+"
    r"(?:\s*(?:달러|유로|위안|원|엔))?|\s*(?:달러|유로|위안|원|엔))"
    r"(?![A-Za-z0-9])" + _KOREAN_QUANTITY_END
)


def unsupported_quantity_spans(text):
    spans = []
    for match in _KOREAN_MONEY_EXPRESSION.finditer(text):
        whole = match.group(0)
        parsed = QUANT_SIGNAL_RE.fullmatch(whole)
        if parsed is None or not (parsed.groupdict().get("korean_currency")
                                 or parsed.groupdict().get("korean_magnitude")):
            spans.append((match.start(), match.end(), whole))
    return tuple(spans)


def quantitative_observations(text):
    unsupported = unsupported_quantity_spans(text)
    temporal = temporal_period_spans(text)
    return tuple(
        quantity_from_match(match)
        for match in QUANT_SIGNAL_RE.finditer(text)
        if not _overlaps_any_span(match.start(), match.end(), unsupported)
        and not _overlaps_any_span(match.start(), match.end(), temporal)
    )


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
    r"\b(?:if|unless|assuming|provided\s+that|providing\s+that|in\s+the\s+event\s+that)\b",
    re.IGNORECASE,
)
_KOREAN_NEXT_SUBJECT = re.compile(r"(?:[가-힣](?:고|며|는데)|,)\s+(?P<subject>(?:[가-힣]{2,}|[A-Z][A-Za-z0-9_-]+)(?:은|는|이|가))\s+")
_KOREAN_CONTRAST = re.compile(r"(?:지만|반면|그러나|하지만|그런데)\s*")
# Only explicit predicate constructions gain realized strength. An unsupported
# form still has its own observation; it is not silently promoted to an event.
_KOREAN_COMPLETED_OBJECT = re.compile(r"^[을를]\s*(?:받았|마쳤|완료했|시작했)")
_KOREAN_ENTERED_EVENT = re.compile(r"^에\s*(?:들어갔|돌입했)")
_KOREAN_CONDITIONAL_SUFFIX = re.compile(
    r"^(?:[가-힣\s]*?(?:다면|되면|하면|으면|될\s*경우|된\s*경우)(?=$|\s|[.,;!?])"
    r"|\s*(?:조건|여부))"
)
_KOREAN_INTERRUPTED_EVENT = re.compile(r"^(?:[을를]\s*)?\s*(?:중단|중지)")
_KOREAN_FUTURE_CONTEXT = re.compile(r"(?:내년|향후|앞으로|오는\s*(?:[0-9]+년|[0-9]+월))")
_KOREAN_DATED_CONTEXT = re.compile(r"[0-9]{4}년(?:도|에|부터|까지)?")
_KOREAN_NONPAST_PREDICATE = re.compile(r"^(?:한다|된다|[을를]\s*(?:시작한다|개시한다))")
_KOREAN_ONGOING_SUFFIX = r"중(?=$|[^가-힣]|이다|이며|이고|인|에|으로)"



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
    if (re.search(r"(?<![가-힣])(?:안|못)\s*$|(?:미|비)$", prefix)
            or re.search(r"(?:지\s*(?:않|못)|\b아니|(?:적|바)\s*(?:이\s*)?없)", suffix)):
        return _state_observation(match, 0, "negated", "korean_local_negation")
    if (re.search(r"(?:만약|경우에만)\s*[^.;!?]*$", prefix)
            or _KOREAN_CONDITIONAL_SUFFIX.search(suffix)):
        return _state_observation(match, 0, "conditional", "korean_conditional_predicate")
    if re.search(r"(?:예정|계획|목표|전망|예상|기대|추진|검토|해야|하여야|필요)", suffix):
        return _state_observation(match, 0, "prospective", "korean_not_realized")
    if re.search(r"(?:가능성|가능|[될할]\s*수\s*있)", suffix):
        return _state_observation(match, 1, "tentative", "korean_possibility")
    if _KOREAN_INTERRUPTED_EVENT.match(suffix):
        # '가동 중단됐다' asserts a suspension, not running. The suspension
        # marker has its own observation and can still supply realized density.
        return _state_observation(match, 0, "interrupted", "korean_interrupted_event")
    if (re.search(r"예정\s*$", prefix)
            or ((_KOREAN_FUTURE_CONTEXT.search(prefix) or _KOREAN_DATED_CONTEXT.search(prefix))
                and _KOREAN_NONPAST_PREDICATE.match(suffix))):
        # Dates for the project being approved do not undo a past approval;
        # only a dated/future nonpast predicate is treated as prospective here.
        return _state_observation(match, 0, "prospective", "korean_future_context")
    if re.match(r"^(?:했|됐|하였|되었|한다|된다|\s*(?:완료|확정|개시|시작|"
                + _KOREAN_ONGOING_SUFFIX + r"))", suffix):
        # Approval-in-progress is not an approval already granted.
        if match.group(0) == "승인" and re.match(r"^\s*중", suffix):
            return _state_observation(match, 0, "pending", "approval_in_progress")
        return _state_observation(match, 2, "realized", "korean_asserted_predicate")
    if _KOREAN_COMPLETED_OBJECT.match(suffix):
        return _state_observation(match, 2, "realized", "korean_completed_object")
    if _KOREAN_ENTERED_EVENT.match(suffix):
        return _state_observation(match, 2, "realized", "korean_entered_event")
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
    # 'whether X was approved' queries X. A later 'and will decide whether ...'
    # does not make an already asserted approval conditional. True if/unless
    # conditions can be preposed or postposed and keep their enclosing scope.
    # A postposed condition belongs only to this state until a coordinated
    # explicit subject starts a new clause. Keep preposed conditions in the
    # prefix so "If Alpha is approved and Beta is approved" remains scoped.
    conditional_suffix = local_suffix
    coordinated_subject = COORDINATING_NEW_SUBJECT_RE.search(conditional_suffix)
    if coordinated_subject:
        conditional_suffix = conditional_suffix[:coordinated_subject.start()]

    conditional_prefix = local_prefix
    prefix_subjects = list(COORDINATING_NEW_SUBJECT_RE.finditer(conditional_prefix))
    # A genuinely preposed condition scopes all of its coordinated conjuncts
    # ("If Alpha ... and Beta ..."). Otherwise, once a later explicit subject
    # begins, a postposed condition from the earlier conjunct must not leak
    # into that later subject.
    preposed_condition = re.match(
        r"^\s*(?:(?:previously|earlier|initially|historically|currently|"
        r"meanwhile|today|now|then|at\s+present|at\s+the\s+time)\s*,\s*"
        r"|(?:in|during|as\s+of|by)\s+"
        r"(?:" + TEMPORAL_EN_PERIOD_VALUE + r")"
        r"\s*,\s*"
        r"|for\s+(?:" + TEMPORAL_EN_YEAR_QUARTER_VALUE + r")\s*,\s*)*"
        r"(?:if|unless|assuming|provided\s+that|providing\s+that|"
        r"in\s+the\s+event\s+that|whether)\b",
        conditional_prefix,re.IGNORECASE,
    )
    if prefix_subjects and not preposed_condition:
        conditional_prefix = conditional_prefix[prefix_subjects[-1].end():]

    if (_CONDITIONAL_EN.search(conditional_prefix) or _CONDITIONAL_EN.search(conditional_suffix)
            or re.search(r"\bwhether\b", conditional_prefix, re.IGNORECASE)):
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

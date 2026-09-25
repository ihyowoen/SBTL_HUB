"""Bounded, ordered claim witnesses for Prompt 0.6.

No truth inference, translation, external model, or editorial claim input. These
observations supplement (never replace) quantity, modality, provenance, scope and
operation guards. Unsupported grammar is not evidence of equivalence. Pronoun
binding is deliberately limited to an immediately preceding explicit named topic;
ambiguous new pronoun relations are returned as unresolved, not guessed.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Iterable

from validation_scripts import content_semantic_atoms as atoms


@dataclass(frozen=True)
class Clause:
    start: int
    end: int
    text: str


# Protect decimal numbers and dotted initialisms; do not split 10.5 or U.S.
_INITIALISM_END = re.compile(r'(?:\b[A-Za-z]\.){2,}$')
_ABBREVIATION_END = re.compile(r'\b(?:Mr|Mrs|Ms|Dr|Prof|Corp|Inc|Ltd|Co|vs)\.$', re.I)


def clauses(text: str) -> tuple[Clause, ...]:
    if not isinstance(text, str):
        return ()
    out = []
    begin = 0
    for index, char in enumerate(text):
        terminal = char in ';!?|\n'
        if char == '.':
            prev = text[index - 1] if index else ''
            nxt = text[index + 1] if index + 1 < len(text) else ''
            terminal = not (
                (prev.isdigit() and nxt.isdigit())
                or (prev.isalpha() and nxt.isalpha())
                or _INITIALISM_END.search(text[:index + 1])
                or _ABBREVIATION_END.search(text[:index + 1])
            )
        if terminal:
            left, right = begin, index
            while left < right and text[left].isspace():
                left += 1
            while right > left and text[right - 1].isspace():
                right -= 1
            if left < right:
                out.append(Clause(left, right, text[left:right]))
            begin = index + 1
    if text[begin:].strip():
        left = begin + len(text[begin:]) - len(text[begin:].lstrip())
        out.append(Clause(left, len(text.rstrip()), text[left:].rstrip()))
    return tuple(out)


def exact_clause_set(texts: Iterable[str]) -> frozenset[str]:
    """Literal novelty only: do not discard subjects, periods, polarity or roles."""
    return frozenset(' '.join(c.text.split()).casefold() for text in texts for c in clauses(text))


_WORD = re.compile(r'[A-Za-z가-힣][A-Za-z가-힣0-9&._-]*|[<>≤≥=+−-]|\d+(?:\.\d+)?')


def ordered_terms(text: str) -> tuple[str, ...]:
    """Retain order and prepositions; canonicalize only existing quantity atoms."""
    out = []
    end = 0
    for match in atoms.QUANT_SIGNAL_RE.finditer(text):
        out.extend(x.casefold() for x in _WORD.findall(text[end:match.start()]))
        out.append('quantity:' + atoms.quantity_from_match(match).signal)
        end = match.end()
    out.extend(x.casefold() for x in _WORD.findall(text[end:]))
    return tuple(out)


_KR_SUBJECT = (r'(?P<subject>[가-힣A-Za-z][가-힣A-Za-z0-9&_-]*'
               r'(?:\s+[가-힣A-Za-z][가-힣A-Za-z0-9&_-]*){0,3})(?:은|는|이|가)\s+')
_KR_OBJECT = re.compile(
    r'^' + _KR_SUBJECT + r'(?P<object>.+?)(?:을|를)\s+'
    r'(?P<context>.*?)'
    r'(?P<predicate>[가-힣]{2,}?(?:했다|하였다|한다|된다|됐다|되었다)'
    r'|[가-힣]{2,}?하지\s+(?:않았다|않는다))$'
)

# A finite trailing-quantity form is also an observed relation: the numeric
# suffix must not cause subject/object roles to disappear (original A06).
_KR_TRAILING_QUANTITY = re.compile(
    r'^' + _KR_SUBJECT + r'(?P<object>.+?)(?:을|를)\s+'
    r'(?P<predicate>[가-힣]{2,}?(?:했다|하였다|한다|된다|됐다|되었다)'
    r'|[가-힣]{2,}?하지\s+(?:않았다|않는다))\s+(?P<context>.+)$'
)
_KR_DESCRIPTION = re.compile(
    r'^' + _KR_SUBJECT + r'(?P<attribute>[가-힣]{2,}?)(?:이|가|은|는)\s+'
    r'(?P<polarity>안\s+|그다지\s+)?'
    r'(?P<predicate>높다|낮다|크다|작다|많다|적다|있다|없다|좋다|나쁘다'
    r'|높았다|낮았다|컸다|작았다|많았다|적었다|있었다|없었다)'
    r'(?P<negation>\s*(?:는\s+)?(?:아니다|않다))?$'
)

_KR_COPULAR = re.compile(
    r'^' + _KR_SUBJECT
    + r'(?P<complement>[가-힣]+(?:\s+[가-힣]+){0,4}?)(?P<copula>이다|이었다|였다|아니다)$'
)


def korean_relations(text: str) -> Counter:
    """Subject-object-predicate retains intervening quantities, not a token bag."""
    out = Counter()
    for clause in clauses(text):
        match = _KR_OBJECT.fullmatch(clause.text)
        if match is None:
            trailing = _KR_TRAILING_QUANTITY.fullmatch(clause.text)
            if trailing and atoms.QUANT_SIGNAL_RE.match(trailing['context']):
                match = trailing
        if match:
            subject, predicate, obj = match['subject'].casefold(), match['predicate'], match['object']
            context = ordered_terms(match['context'])
            if not context:
                # Preserve the published three-part helper identity for simple
                # SOV clauses, including its canonical negative stem.
                negated = re.fullmatch(r"(.+?)하지\s+(?:않았다|않는다)", predicate)
                predicate = "neg:" + negated[1] if negated else predicate
                out[(subject, predicate, obj)] += 1
            else:
                out[('relation:kr', subject, predicate, ordered_terms(obj), context)] += 1
        match = _KR_DESCRIPTION.fullmatch(clause.text)
        if match:
            out[('description:kr', match['subject'].casefold(), match['attribute'],
                 ' '.join((match['polarity'] or '').split()), match['predicate'],
                 ' '.join((match['negation'] or '').split()))] += 1
        copular = _KR_COPULAR.fullmatch(clause.text)
        if copular:
            out[('copular:kr', copular['subject'].casefold(),
                 ' '.join(copular['complement'].split()), copular['copula'])] += 1
    return out


def korean_description_tokens(text: str) -> list[str]:
    # Used by the legacy content inventory as well as the ordered relation guard.
    out = []
    for clause in clauses(text):
        match = _KR_DESCRIPTION.fullmatch(clause.text)
        if match:
            out.extend(x for x in (match['subject'], match['attribute'],
                                   match['polarity'], match['predicate'], match['negation']) if x)
        copular = _KR_COPULAR.fullmatch(clause.text)
        if copular:
            out.extend((copular['subject'], copular['complement'], copular['copula']))
    return out


_PROPER = r'[A-Z][A-Za-z0-9&._-]+(?:\s+(?:[A-Z][A-Za-z0-9&._-]+|project|plant|facility|company)){0,3}'
_SUBJECT = (r'(?P<subject>' + _PROPER + r'|(?:[Tt]he|[Aa]n?)\s+[A-Za-z][A-Za-z0-9_-]+'
            r'|[Ii]t|[Tt]hey|[Hh]e|[Ss]he)')
_ACTIONS = (r'sold|sells?|acquired|acquires?|bought|buys?|used|uses?|burned|burns?|burnt'
            r'|supplied|supplies|supply|selected|selects?|recycled|recycles?'
            r'|owned|owns?|employed|employs?|manufactured|manufactures?|exported|exports?|imported|imports?|shipped|ships?|delivered|delivers?')
_EN_ACTION = re.compile(
    r'^' + _SUBJECT + r'\s+'
    r'(?P<aux>(?i:(?:(?:can|could|may|might|will|would|must|should|has|have|had|did|does|do)\s+)?'
    r'(?:not\s+)?))'
    r'(?P<verb>(?i:' + _ACTIONS + r'))\s+(?P<tail>.+)$'
)
_EN_PASSIVE = re.compile(
    r'^(?P<object>.+?)\s+'
    r'(?P<aux>(?i:(?:is|are|was|were|has\s+been|have\s+been|had\s+been)))\s+'
    r'(?P<verb>(?i:sold|acquired|bought|used|burned|burnt|supplied|selected|recycled|owned|employed|manufactured|exported|imported|shipped|delivered))\s+'
    r'by\s+(?P<subject>' + _PROPER + r')(?P<tail>\s+.+)?$'
)
_TOPIC = re.compile(r'^(?P<topic>' + _PROPER + r')\s+(?:project|plant|facility|company)$')
_NEW_ACTION = re.compile(r'\s+(?:and|but|while|whereas)\s+(?=' + _SUBJECT + r'\s+(?i:' + _ACTIONS + r')\b)')
_PRONOUNS = {'it', 'they', 'he', 'she'}


def immediate_pronoun_topic(text: str, position: int) -> str | None:
    """Resolve only an immediately preceding named topic for a pronoun clause."""
    parsed = clauses(text)
    for index, clause in enumerate(parsed):
        if clause.start <= position <= clause.end:
            if not re.match(r'(?i)^(?:it|they|he|she)\b', clause.text):
                return None
            if index == 0:
                return None
            previous = parsed[index - 1]
            if text[previous.end:clause.start].strip() != '.':
                return None
            match = _TOPIC.fullmatch(previous.text)
            return match['topic'].casefold() if match else None
    return None


def english_relations(text: str) -> Counter:
    out = Counter()
    previous = None
    for clause in clauses(text):
        # A topic is used only by the immediately following sentence. It must not
        # cross a semicolon/pipe (used to join independent fields and sources).
        topic = None
        if previous is not None and text[previous.end:clause.start].strip() == '.':
            prev_topic = _TOPIC.fullmatch(previous.text)
            if prev_topic:
                topic = prev_topic['topic'].casefold()
        segments = []
        pos = 0
        for boundary in _NEW_ACTION.finditer(clause.text):
            segments.append(clause.text[pos:boundary.start()])
            pos = boundary.end()
        segments.append(clause.text[pos:])
        for segment in segments:
            match = _EN_ACTION.fullmatch(segment.strip())
            if not match:
                continue
            subject = re.sub(r'^(?:the|a|an)\s+', '', match['subject'].casefold())
            kind = 'relation:en'
            if subject in _PRONOUNS:
                if topic is not None:
                    # Singular named topics cannot resolve the plural pronoun.
                    if subject != 'it':
                        kind = 'relation:unresolved'
                    subject = topic
                else:
                    kind = 'relation:unresolved'
                    # Keeping the explicit context prevents permutation across
                    # otherwise identical, unresolved pronoun strings.
                    subject = (subject, previous.text if previous else '')
            out[(kind, subject, match['aux'].strip().casefold(),
                 match['verb'].casefold(), ordered_terms(match['tail']))] += 1
        passive = _EN_PASSIVE.fullmatch(clause.text.strip())
        if passive:
            out[('relation:en:passive', passive['subject'].casefold(),
                 passive['aux'].strip().casefold(), passive['verb'].casefold(),
                 ordered_terms(passive['object']), ordered_terms(passive['tail'] or ''))] += 1
        previous = clause
    return out


_METRIC_PERIOD_VALUE = (
    r"(?:" + atoms.TEMPORAL_EN_YEAR_QUARTER_VALUE + r"|"
    r"(?:19|20|21)\d{2}\s*년(?:도)?\s*[1-4]\s*분기|"
    r"[1-4]\s*분기(?:\s*(?:19|20|21)\d{2}\s*년)?|"
    r"(?:19|20|21)\d{2}\s*년(?:도)?)"
)
_METRIC = re.compile(
    r'(?<![A-Za-z가-힣])(?P<metric>capacity|output|revenue|profit|sales|investment|cost|margin|'
    r'용량|출력|매출|이익|판매량|투자액|비용|마진)'
    r'(?:은|는|이|가)?\s*'
    r'(?:(?:in|for|during)\s+(?P<post_period>' + _METRIC_PERIOD_VALUE + r')\s*)?'
    r'(?:(?:is|was|are|were|of|at)\s+|[:=]\s*)?$', re.I
)
_PERIOD = re.compile(r'(?<!\w)(?P<period>' + _METRIC_PERIOD_VALUE + r')(?!\w)', re.I)


def _canonical_metric_period(raw: str) -> str:
    return atoms.canonical_temporal_period(raw)


def _mask_periods(text: str) -> str:
    if not isinstance(text, str):
        return text
    chars=list(text)
    for start,end,_ in atoms.temporal_period_spans(text):
        for index in range(start,end):
            chars[index]=' '
    return ''.join(chars)


def english_factual_period_relations(text: str) -> Counter:
    out=Counter()
    for clause in clauses(text):
        segments=[]
        pos=0
        for boundary in _NEW_ACTION.finditer(clause.text):
            segments.append(clause.text[pos:boundary.start()])
            pos=boundary.end()
        segments.append(clause.text[pos:])
        for segment in segments:
            match=_EN_ACTION.fullmatch(segment.strip())
            if not match:
                continue
            periods=atoms.temporal_period_observations(match['tail'])
            if not periods:
                continue
            subject=re.sub(r'^(?:the|a|an)\s+','',match['subject'].casefold())
            if subject in _PRONOUNS:
                continue
            masked_tail=_mask_periods(match['tail'])
            object_terms=ordered_terms(masked_tail)
            for _,_,period in periods:
                out[('relation:en:period', subject, match['aux'].strip().casefold(),
                     match['verb'].casefold(), object_terms, period)] += 1
    return out


_COPULAR_REASON_CLAUSE = re.compile(
    r'\b(?:am|is|are|was|were|be|been|being)\b[^.;!?]{0,120}?'
    r'\b(?:because|since|although|though)\s+(?P<clause>[^.;!?]+)',
    re.I,
)


def copular_subordinate_relations(text: str) -> Counter:
    out=Counter()
    if not isinstance(text,str):
        return out
    for match in _COPULAR_REASON_CLAUSE.finditer(text):
        out.update(english_relations(match['clause'].strip()))
    return out

def metric_quantity_relations(text: str, subjects_for_span: Callable) -> Counter:
    """Explicit entity+metric+period+quantity, not a shared entity-number bag.

    Generic unlabelled numbers stay governed by the existing quantity contract.
    No metric is inferred from the unit or from a different evidence field.
    """
    out = Counter()
    for clause in clauses(text):
        for quantity in atoms.quantitative_observations(clause.text):
            prefix = clause.text[:quantity.start]
            match = _METRIC.search(prefix)
            if not match:
                continue
            metric = match['metric'].casefold()
            subjects = subjects_for_span(text, clause.start + match.start(), clause.start + quantity.end)
            if subjects == ['__generic__']:
                # Bare "Capacity is 10 MW" is not an explicit entity binding.
                continue
            if match.groupdict().get('post_period'):
                period = _canonical_metric_period(match['post_period'])
            else:
                periods = list(_PERIOD.finditer(prefix[:match.start()]))
                period = _canonical_metric_period(periods[-1]['period']) if periods else ''
            for subject in subjects:
                out[('metric:quantity', subject, metric, period, quantity.signal)] += 1
    return out

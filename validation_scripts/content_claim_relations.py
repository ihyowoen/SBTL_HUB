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


def korean_period_relations(text: str) -> Counter:
    """Preserve explicit Korean period identity before temporal masking."""
    out=Counter()
    if not isinstance(text,str):
        return out
    for clause in clauses(text):
        match=_KR_OBJECT.fullmatch(clause.text)
        if match is None:
            trailing=_KR_TRAILING_QUANTITY.fullmatch(clause.text)
            if trailing and atoms.QUANT_SIGNAL_RE.match(trailing['context']):
                match=trailing
        if not match:
            continue
        context=match['context']
        periods=atoms.temporal_period_observations(context)
        if not periods:
            continue
        subject=match['subject'].casefold()
        predicate=match['predicate']
        negated=re.fullmatch(r"(.+?)하지\s+(?:않았다|않는다)",predicate)
        predicate="neg:" + negated[1] if negated else predicate
        obj=ordered_terms(match['object'])
        for _,_,period in periods:
            out[('relation:kr:period',subject,predicate,obj,period)]+=1
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


_PROPER = (r"[A-Z][A-Za-z0-9&._-]+(?:(?:'s|’s)\s+[A-Za-z][A-Za-z0-9&._-]+)?"
           r"(?:\s+(?:[A-Z][A-Za-z0-9&._-]+|project|plant|facility|company)){0,3}")
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
    r"(?:" + atoms.TEMPORAL_EN_PERIOD_VALUE + r"|"
    r"(?:19|20|21)\d{2}\s*년(?:도)?\s*[1-4]\s*분기|"
    r"[1-4]\s*분기(?:\s*(?:19|20|21)\d{2}\s*년)?|"
    r"(?:19|20|21)\d{2}\s*년(?:도)?)"
)
_METRIC = re.compile(
    r'(?<![A-Za-z가-힣])(?P<metric>capacity|output|revenue|profit|sales|investment|cost|margin|'
    r'용량|출력|매출|이익|판매량|투자액|비용|마진)'
    r'(?:은|는|이|가)?\s*'
    r'(?:(?:in|for|during)\s+(?P<post_period>' + _METRIC_PERIOD_VALUE + r')\s*'
    r'|from\s+(?P<post_range>' + atoms.TEMPORAL_EN_MONTH_RANGE_VALUE + r')\s*)?'
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


def _topic_before_clause(text: str, parsed: tuple[Clause, ...], index: int) -> str | None:
    if index <= 0:
        return None
    previous=parsed[index-1]
    current=parsed[index]
    if text[previous.end:current.start].strip() != '.':
        return None
    match=_TOPIC.fullmatch(previous.text)
    return match['topic'].casefold() if match else None


def _resolved_action_subject(raw_subject: str, topic: str | None):
    subject=re.sub(r'^(?:the|a|an)\s+','',raw_subject.casefold())
    if subject not in _PRONOUNS:
        return subject
    if subject == 'it' and topic:
        return topic
    return None


_GENERAL_FINITE = re.compile(
    r'^' + _SUBJECT + r'\s+(?P<body>.+)$'
)
_GENERAL_AUX = {
    'am','is','are','was','were','be','been','being',
    'has','have','had','do','does','did',
    'can','could','may','might','will','would','must','should','shall',
}
_GENERAL_IRREGULAR = {
    'grew','fell','rose','ran','went','came','sank','broke','burst','shut',
    'left','won','lost','drove','flew','stood','sat','lay','led','paid',
}
_GENERAL_STATE_VERBS = {
    'approved','delayed','started','completed','resumed','restarted',
    'suspended','cancelled','canceled','signed','launched','shipped',
    'commenced','began','begun',
}


def _strip_leading_period(text: str):
    value=str(text or '').strip()
    observations=atoms.temporal_period_observations(value)
    for start,end,period in observations:
        if not value[:start].strip():
            remainder=re.sub(r'^\s*,\s*','',value[end:],count=1)
            return remainder.strip(),period
    return value,''


def _normalize_aux_contractions(text: str):
    value=str(text or '')
    value=re.sub(r"\bwon['’]t\b","will not",value,flags=re.I)
    value=re.sub(r"\bcan['’]t\b","can not",value,flags=re.I)
    value=re.sub(
        r"\b(?P<aux>had|has|have|did|does|do|would|could|should|must|"
        r"is|are|was|were|might)n['’]t\b",
        r"\g<aux> not",value,flags=re.I,
    )
    return value


_SUBJECT_PREFIX = re.compile(r'^' + _SUBJECT + r'\s+')


def _strip_subject_preverb_period(text: str):
    value=str(text or '').strip()
    subject_match=_SUBJECT_PREFIX.match(value)
    if not subject_match:
        return value,''
    for start,end,period in atoms.temporal_period_observations(value):
        if start < subject_match.end():
            continue
        if value[subject_match.end():start].strip():
            continue
        masked=(value[:start] + ' ' + value[end:]).strip()
        masked=re.sub(r'\s+',' ',masked)
        return masked,period
    return value,''


def _parse_general_finite(segment: str, topic: str | None):
    match=_GENERAL_FINITE.fullmatch(segment.strip())
    if not match:
        return None
    subject=_resolved_action_subject(match['subject'],topic)
    if subject is None:
        return None
    body=_normalize_aux_contractions(match['body'])
    tokens=list(re.finditer(r"[A-Za-z][A-Za-z-]*",body))
    if not tokens:
        return None
    aux=[]
    index=0
    while index < len(tokens):
        token=tokens[index].group(0).casefold()
        if token in _GENERAL_AUX or token == 'not':
            aux.append(token)
            index+=1
            continue
        break
    if index >= len(tokens):
        return None
    verb_match=tokens[index]
    verb=verb_match.group(0).casefold()
    if not aux and not (
        re.fullmatch(r"[a-z][a-z-]*(?:s|ed|ing)",verb)
        or verb in _GENERAL_IRREGULAR
    ):
        return None
    tail=body[verb_match.end():].strip()
    return subject,' '.join(aux),verb,tail


def _split_coordinated_passives(text: str):
    parts=re.split(r'\s+(?:and|but|while|whereas)\s+',text,flags=re.I)
    if len(parts) <= 1:
        return (text,)
    parsed=[]
    for part in parts:
        remainder,_=_strip_leading_period(part)
        if not _EN_PASSIVE.fullmatch(remainder):
            return (text,)
        parsed.append(part)
    return tuple(parsed)


_COPULAR_COORDINATED_SUBJECT = re.compile(
    r'\s+(?:and|but|while|whereas)\s+'
    r'(?=(?:[A-Z][A-Za-z0-9&._-]*(?:\s+(?:[A-Z][A-Za-z0-9&._-]+|project|plant|facility|company)){0,3}'
    r'|(?:[Tt]he|[Aa]n?)\s+[A-Za-z][A-Za-z0-9_-]+|[Ii]t|[Tt]hey|[Hh]e|[Ss]he)'
    r'(?:\s+(?:(?:in|during|for|by|on|since|through|until|as\s+of)\s+'
    r'(?:' + atoms.TEMPORAL_EN_PERIOD_VALUE + r')'
    r'|from\s+(?:' + atoms.TEMPORAL_EN_MONTH_RANGE_VALUE + r')))?'
    r'\s+(?:is|are|was|were)\b)',
    re.I,
)


def _local_dated_arguments(tail: str):
    """Return object terms bound to each explicit local period in one action tail."""
    periods=atoms.temporal_period_observations(tail)
    if not periods:
        return ()
    out=[]
    previous_end=0
    for start,end,period in periods:
        local=tail[previous_end:start]
        local=re.sub(r'^\s*(?:and|or|,)\s*','',local,flags=re.I)
        local=re.sub(r'\s*(?:and|or|,)\s*$','',local,flags=re.I)
        terms=ordered_terms(local)
        if terms:
            out.append((terms,period))
        previous_end=end
    return tuple(out)


def _finite_coord_token(token: str):
    value=str(token or '').casefold()
    return (
        re.fullmatch(r"(?:" + _ACTIONS + r")",value,re.IGNORECASE) is not None
        or re.fullmatch(r"[a-z][a-z-]*(?:ed|ing)",value) is not None
        or value in _GENERAL_IRREGULAR
    )


def _active_local_dated_pairs(tail: str, initial_verb: str):
    periods=atoms.temporal_period_observations(tail)
    if not periods:
        return ()
    out=[]
    previous_end=0
    current_verb=initial_verb
    for start,end,period in periods:
        raw_local=tail[previous_end:start]
        connector_prefix=re.match(r'^\s*(?:and|or|,)\s+',raw_local,re.I)
        local=re.sub(r'^\s*(?:and|or|,)\s*','',raw_local,flags=re.I).strip()
        local=re.sub(r'\s*(?:and|or|,)\s*$','',local,flags=re.I).strip()
        terms=list(ordered_terms(local))
        if (previous_end or connector_prefix) and terms and _finite_coord_token(terms[0]):
            current_verb=terms.pop(0)
        out.append((current_verb,tuple(terms),period))
        previous_end=end
    return tuple(out)

def _preposed_action_terms(tail: str):
    periods=atoms.temporal_period_observations(tail)
    if not periods:
        return ordered_terms(tail)
    before=tail[:periods[0][0]]
    connectors=list(re.finditer(r"\b(?:and|or)\b",before,flags=re.I))
    if connectors:
        before=before[:connectors[-1].start()]
    return ordered_terms(before.strip(" ,"))


def _passive_local_dated_objects(passive):
    tail=passive['tail'] or ''
    periods=atoms.temporal_period_observations(tail)
    if not periods:
        return ()
    out=[]
    previous_end=0
    base_object=ordered_terms(passive['object'])
    for index,(start,end,period) in enumerate(periods):
        local=tail[previous_end:start]
        local=re.sub(r'^\s*(?:and|or|,)\s*','',local,flags=re.I).strip()
        local=re.sub(r'\s*(?:and|or|,)\s*$','',local,flags=re.I).strip()
        object_terms=ordered_terms(local) if local else ()
        if not object_terms:
            object_terms=base_object
        out.append((object_terms,period))
        previous_end=end
    return tuple(out)


def _emit_active_period_relations(out, segment, topic):
    raw,leading_period=_strip_leading_period(segment)
    subject_period=''
    raw,subject_period=_strip_subject_preverb_period(raw)
    preposed_period=leading_period or subject_period

    match=_EN_ACTION.fullmatch(raw)
    if match:
        subject=_resolved_action_subject(match['subject'],topic)
        if subject is None:
            return
        aux=match['aux'].strip().casefold()
        verb=match['verb'].casefold()
        tail=match['tail']
    else:
        parsed_general=_parse_general_finite(raw,topic)
        if not parsed_general:
            return
        subject,aux,verb,tail=parsed_general
        if verb in _GENERAL_STATE_VERBS:
            return

    local_pairs=_active_local_dated_pairs(tail,verb)
    if local_pairs:
        if preposed_period:
            preposed_terms=_preposed_action_terms(tail)
            out[('relation:en:period',subject,aux,verb,preposed_terms,preposed_period)]+=1
        for local_verb,object_terms,period in local_pairs:
            out[('relation:en:period',subject,aux,local_verb,object_terms,period)]+=1
        return

    if preposed_period:
        object_terms=ordered_terms(tail)
        out[('relation:en:period',subject,aux,verb,object_terms,preposed_period)]+=1


def _emit_passive_period_relation(out, segment):
    raw,leading_period=_strip_leading_period(segment)
    passive=_EN_PASSIVE.fullmatch(raw)
    masked_passive=None

    if passive is None:
        masked_raw=_mask_periods(raw)
        masked_raw=re.sub(r'\s+',' ',masked_raw).strip()
        passive=_EN_PASSIVE.fullmatch(masked_raw)
        if passive is None:
            return
        masked_passive=passive

    subject=passive['subject'].casefold()
    aux=passive['aux'].strip().casefold()
    verb=passive['verb'].casefold()
    base_object=ordered_terms(passive['object'])

    if leading_period:
        out[('relation:en:passive:period',subject,aux,verb,base_object,leading_period)]+=1

    if masked_passive is not None:
        for _,_,period in atoms.temporal_period_observations(raw):
            out[('relation:en:passive:period',subject,aux,verb,base_object,period)]+=1
        return

    local_objects=_passive_local_dated_objects(passive)
    if local_objects:
        for object_terms,period in local_objects:
            out[('relation:en:passive:period',subject,aux,verb,object_terms,period)]+=1

    # Periods before the passive tail (for example object-period-copula or
    # verb-period-agent forms) are not represented by local_objects.
    tail_start=passive.start('tail') if passive.groupdict().get('tail') else len(raw)
    for start,_,period in atoms.temporal_period_observations(raw):
        if start < tail_start:
            cleaned_object=ordered_terms(_mask_periods(passive['object']))
            out[('relation:en:passive:period',subject,aux,verb,
                 cleaned_object or base_object,period)]+=1


def english_factual_period_relations(text: str) -> Counter:
    out=Counter()
    parsed=clauses(text)
    for index,clause in enumerate(parsed):
        topic=_topic_before_clause(text,parsed,index)
        segments=[]
        pos=0
        for boundary in _NEW_ACTION.finditer(clause.text):
            segments.append(clause.text[pos:boundary.start()])
            pos=boundary.end()
        segments.append(clause.text[pos:])
        for segment in segments:
            _emit_active_period_relations(out,segment,topic)
        for passive_segment in _split_coordinated_passives(clause.text):
            _emit_passive_period_relation(out,passive_segment)
    return out


_EN_COPULAR_PERIOD = re.compile(
    r'^' + _SUBJECT + r'\s+(?P<copula>(?i:is|are|was|were))\s+(?P<tail>.+)$'
)
_COPULAR_NEW_SUBJECT_BEFORE_PERIOD = re.compile(
    r'\b(?:and|but|while|whereas)\s+'
    r'(?:[A-Za-z][A-Za-z0-9&._-]*(?:\s+[A-Za-z][A-Za-z0-9&._-]*){0,3}|'
    r'it|they|he|she)\s+(?:is|are|was|were)\b',
    re.I,
)
_COPULAR_SUBJECT_AFTER_PERIOD = re.compile(
    r'^\s*(?:,\s*)?'
    r'(?:[A-Za-z][A-Za-z0-9&._-]*(?:\s+[A-Za-z][A-Za-z0-9&._-]*){0,3}|'
    r'it|they|he|she)\s+(?:is|are|was|were)\b',
    re.I,
)


def _copular_segment_period_relations(segment: str, topic: str | None):
    out=Counter()
    raw,leading_period=_strip_leading_period(segment)
    observations=atoms.temporal_period_observations(raw)
    direct=_EN_COPULAR_PERIOD.fullmatch(raw)

    if direct:
        subject=_resolved_action_subject(direct['subject'],topic)
        if subject is None:
            return out
        observations=atoms.temporal_period_observations(direct['tail'])
        local_pairs=list(_local_dated_arguments(direct['tail']))
        if local_pairs:
            if leading_period:
                first_start=observations[0][0] if observations else len(direct['tail'])
                before_first=direct['tail'][:first_start].strip()
                pieces=re.split(r"\b(?:and|or)\b",before_first,flags=re.I)
                leading_complement=ordered_terms(pieces[0].strip(" ,"))
                if leading_complement:
                    out[('relation:en:copular:period',subject,
                         direct['copula'].casefold(),leading_complement,leading_period)]+=1
                if len(pieces)>1:
                    remainder=ordered_terms(pieces[-1].strip(" ,"))
                    if remainder:
                        local_pairs[0]=(remainder,local_pairs[0][1])
            pair_index=0
            for start,end,period in observations:
                after=direct['tail'][end:]
                if _COPULAR_SUBJECT_AFTER_PERIOD.match(after):
                    # This period is preposed for the following explicit
                    # subject; do not attach it to the current copular subject.
                    continue
                if pair_index < len(local_pairs):
                    complement,pair_period=local_pairs[pair_index]
                    pair_index+=1
                    if pair_period == period:
                        out[('relation:en:copular:period',subject,
                             direct['copula'].casefold(),complement,period)]+=1
            if out:
                return out
            if observations:
                return out
        if leading_period:
            complement=ordered_terms(direct['tail'])
            if complement:
                out[('relation:en:copular:period',subject,
                     direct['copula'].casefold(),complement,leading_period)]+=1
        return out

    all_periods=atoms.temporal_period_observations(raw)
    if leading_period:
        all_periods=((0,0,leading_period),)+all_periods
    if not all_periods:
        return out
    masked=_mask_periods(raw)
    masked=re.sub(r'^\s*,\s*','',masked).strip()
    parsed=_EN_COPULAR_PERIOD.fullmatch(masked)
    if not parsed:
        return out
    subject=_resolved_action_subject(parsed['subject'],topic)
    if subject is None:
        return out
    complement=ordered_terms(parsed['tail'])
    if not complement:
        return out
    seen=set()
    for _,_,period in all_periods:
        if period and period not in seen:
            seen.add(period)
            out[('relation:en:copular:period',subject,
                 parsed['copula'].casefold(),complement,period)]+=1
    return out


def english_copular_period_relations(text: str) -> Counter:
    out=Counter()
    parsed=clauses(text)
    for index,clause in enumerate(parsed):
        topic=_topic_before_clause(text,parsed,index)
        segments=_COPULAR_COORDINATED_SUBJECT.split(clause.text)
        for segment in segments:
            out.update(_copular_segment_period_relations(segment,topic))
    return out


_COPULAR_REASON_CLAUSE = re.compile(
    r'\b(?:am|is|are|was|were|be|been|being)\b[^.;!?]{0,120}?'
    r'\b(?:because|since|although|though)\s+(?P<clause>[^.;!?]+)',
    re.I,
)


_SUBORDINATE_FINITE = re.compile(
    r'^' + _SUBJECT + r'\s+'
    r'(?P<verb>(?i:[A-Za-z][A-Za-z-]{1,}))'
    r'(?:\s+(?P<tail>.*))?$'
)
_SUBORDINATE_AUXILIARIES = {
    'am','is','are','was','were','be','been','being',
    'has','have','had','do','does','did',
    'can','could','may','might','will','would','must','should','shall',
}


def copular_subordinate_relations(text: str) -> Counter:
    out=Counter()
    if not isinstance(text,str):
        return out
    for match in _COPULAR_REASON_CLAUSE.finditer(text):
        clause=match['clause'].strip()
        parsed=english_relations(clause)
        if parsed:
            out.update(parsed)
            continue
        finite=_parse_general_finite(clause,None)
        if not finite:
            continue
        subject,aux,verb,tail=finite
        if aux:
            out[('relation:en:subordinate',subject,aux,verb,ordered_terms(tail))]+=1
        else:
            # Preserve the established key shape for simple finite subordinate
            # clauses; add aux only when it is semantically present.
            out[('relation:en:subordinate',subject,verb,ordered_terms(tail))]+=1
    return out

_COORDINATED_METRIC_PERIOD = re.compile(
    r'(?:^|(?:and|,))\s*(?:in|for|during)\s+'
    r'(?P<period>' + _METRIC_PERIOD_VALUE + r')\s*'
    r'(?:(?:is|was|are|were|of|at)\s+|[:=]\s*)?$',
    re.I,
)


def _period_after_quantity(clause_text: str, quantity_end: int):
    suffix=clause_text[quantity_end:]
    observations=atoms.temporal_period_observations(suffix)
    if not observations:
        return ''
    start,_,period=observations[0]
    if suffix[:start].strip(' ,'):
        return ''
    return period


def metric_quantity_relations(text: str, subjects_for_span: Callable) -> Counter:
    """Explicit entity+metric+period+quantity with bounded coordinated carry."""
    out=Counter()
    for clause in clauses(text):
        context=None
        previous_quantity_end=None
        for quantity in atoms.quantitative_observations(clause.text):
            prefix=clause.text[:quantity.start]
            match=_METRIC.search(prefix)
            period=''
            if match:
                metric=match['metric'].casefold()
                subjects=subjects_for_span(
                    text,clause.start+match.start(),clause.start+quantity.end
                )
                if subjects == ['__generic__']:
                    previous_quantity_end=quantity.end
                    continue
                post_value=(
                    match.groupdict().get('post_period')
                    or match.groupdict().get('post_range')
                )
                if post_value:
                    period=_canonical_metric_period(post_value)
                else:
                    suffix_period=_period_after_quantity(clause.text,quantity.end)
                    if suffix_period:
                        period=suffix_period
                    else:
                        metric_prefix=prefix[:match.start()]
                        observations=atoms.temporal_period_observations(metric_prefix)
                        if observations:
                            period=observations[-1][2]
                        else:
                            prefix_periods=list(_PERIOD.finditer(metric_prefix))
                            period=(
                                _canonical_metric_period(prefix_periods[-1]['period'])
                                if prefix_periods else ''
                            )
                context=(metric,tuple(subjects))
            else:
                carry=_COORDINATED_METRIC_PERIOD.search(prefix)
                if carry and context is not None:
                    metric,subjects=context
                    period=_canonical_metric_period(carry['period'])
                elif context is not None and previous_quantity_end is not None:
                    bridge=clause.text[previous_quantity_end:quantity.start]
                    masked_bridge=_mask_periods(bridge)
                    if not re.fullmatch(r'\s*(?:and|,)\s*',masked_bridge,re.I):
                        previous_quantity_end=quantity.end
                        continue
                    metric,subjects=context
                else:
                    previous_quantity_end=quantity.end
                    continue

            if not period:
                period=_period_after_quantity(clause.text,quantity.end)
            for subject in subjects:
                out[('metric:quantity',subject,metric,period,quantity.signal)]+=1
            previous_quantity_end=quantity.end
    return out

"""Shared, side-effect-free Prompt 0.6 contracts.

This module compares supplied observations; it is NOT a natural-language truth
oracle. Callers retain locked-version, upstream-authority and operation binding.
A local evidence snapshot cannot certify upstream provenance or publication.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Mapping, Sequence

VISIBLE_COPY_FIELDS = ("sub", "gate", "fact", "implication")

DENSITY_DIMENSIONS = (
    "prior_state",
    "changed_state",
    "quantitative_anchor",
    "boundary_or_uncertainty",
    "transmission_path",
    "next_watchpoint",
)

CONTENT_BASELINE_STRATEGY = "nearest_upstream_visible_copy_0.5_0.4_C"

PRESENTATION_HTML_TAG_RE = re.compile(
    r"</?(?:strong|b|em|i|u|mark|span|small|sub|sup)(?:\s+[^<>]*?)?\s*/?>",
    re.IGNORECASE,
)

def _nonempty_text(value):
    return isinstance(value,str) and bool(value.strip())

def _strip_paired_presentation_markup(text):
    # Strip syntactically paired emphasis/code markers only. Literal asterisks
    # such as "2 * 3" and rating symbols such as "A*" remain substantive text.
    if text.strip() in {"**","__","~~","`","*","_"}:
        return ""
    patterns = (
        r"\*\*(?=\S)(.+?)(?<=\S)\*\*",
        r"__(?=\S)(.+?)(?<=\S)__",
        r"`(?=\S)(.+?)(?<=\S)`",
        r"(?<!\w)\*(?=\S)(.+?)(?<=\S)\*(?!\w)",
        r"(?<!\w)_(?=\S)(.+?)(?<=\S)_(?!\w)",
    )
    previous=None
    while previous!=text:
        previous=text
        for pattern in patterns:
            text=re.sub(pattern,r"\1",text,flags=re.DOTALL)
    return text

def _normalize_text(value):
    if not isinstance(value,str):
        return value
    text=value
    text=re.sub(r"\[([^\]]+)\]\([^)]*\)",r"\1",text)
    # Strip only known presentation-formatting tags. Do not use a generic
    # <...> regex because comparison expressions such as "<0.7%" or ">300"
    # are substantive visible copy.
    text=PRESENTATION_HTML_TAG_RE.sub("",text)
    text=re.sub(r"^\s{0,3}#{1,6}\s+","",text)
    # A spaced leading sign/bound is part of a numeric claim, not markup.
    text=re.sub(
        r"^\s*[-+>]\s+(?!\s*(?:[$€£¥₩]?\d|USD\b|EUR\b|GBP\b|KRW\b|CNY\b|RMB\b|JPY\b|AUD\b|CAD\b|CHF\b|HKD\b|SGD\b))",
        "",text,flags=re.IGNORECASE,
    )
    text=_strip_paired_presentation_markup(text)
    return " ".join(text.split())

def _normalized_visible_value(field, value):
    if field in {"sub","gate","fact"}:
        if not _nonempty_text(value):
            return None
        normalized=_normalize_text(value)
        return normalized if _nonempty_text(normalized) else None
    if field=="implication":
        if not isinstance(value,list) or not value or any(not _nonempty_text(x) for x in value):
            return None
        normalized=tuple(_normalize_text(x) for x in value)
        if any(not _nonempty_text(x) for x in normalized):
            return None
        return normalized
    return None

def _visible_value_text(value):
    if value is None:
        return ""
    if isinstance(value,tuple):
        return " | ".join(value)
    return str(value)

def _strength_multiset_covers(required,evidence):
    pool=sorted(evidence)
    for target in sorted(required,reverse=True):
        candidates=[(idx,value) for idx,value in enumerate(pool) if value>=target]
        if not candidates:
            return False
        idx,_=candidates[0]
        pool.pop(idx)
    return True


@dataclass(frozen=True)
class ContractIssue:
    """One shared rule result; entrypoints only render it differently."""

    rule_id: str
    field: str
    expected: object
    actual: object
    message: str

    def as_finding(self, scope: str) -> dict:
        # Preserve established CLI wording without duplicating rule decisions.
        message = {
            "C06.GROUNDING.OCCURRENCES": "dimension is not grounded in the referenced quote/claim evidence; uncovered signal occurrences remain",
            "C06.GROUNDING.MODALITY": "changed-state modality is stronger than the referenced quote/claim evidence",
        }.get(self.rule_id, self.message)
        return {
            "scope": scope, "rule_id": self.rule_id, "field": self.field,
            "expected": self.expected, "actual": self.actual,
            "message": message,
        }


@dataclass(frozen=True)
class ResolvedEvidenceContext:
    """Detached JSON snapshot of evidence already resolved by a trusted caller.

    Its scope is explicit. It does not infer authority from a row's own labels.
    Accessors return detached containers, so mutation cannot change a later
    check's snapshot. JSON payloads contain no caller-owned mutable references.
    """

    scope: str
    _support_json: str
    _texts_json: str
    _packages_json: str

    @classmethod
    def from_maps(cls, *, scope, support, texts, packages):
        if scope not in {"bound_upstream", "local_row"}:
            raise ValueError("unknown content evidence context scope")
        if not all(isinstance(value, dict) for value in (support, texts, packages)):
            raise ValueError("resolved evidence context requires three explicit maps")
        if any(not isinstance(key, str) for values in (support, texts, packages) for key in values):
            raise ValueError("evidence context map keys must be strings")
        normalized_support = {}
        for ref, fields in support.items():
            if not isinstance(fields, (set, frozenset, list, tuple)) or any(
                not isinstance(field, str) or field not in VISIBLE_COPY_FIELDS
                for field in fields
            ):
                raise ValueError("evidence context contains invalid visible field support")
            normalized_support[ref] = sorted(set(fields))
        if any(not isinstance(values, list) or any(not isinstance(value, str) for value in values)
               for values in texts.values()):
            raise ValueError("evidence context requires text arrays")
        if any(not isinstance(values, list) or any(not isinstance(value, dict) for value in values)
               for values in packages.values()):
            raise ValueError("evidence context requires package arrays")
        dump = lambda value: json.dumps(value, sort_keys=True, ensure_ascii=False,
                                        separators=(",", ":"), allow_nan=False)
        return cls(scope, dump(normalized_support), dump(texts), dump(packages))

    def legacy_maps(self):
        """Compatibility adapter, not a second authority resolution."""
        return (
            {ref: set(fields) for ref, fields in json.loads(self._support_json).items()},
            json.loads(self._texts_json),
            json.loads(self._packages_json),
        )

    @property
    def unverified_scopes(self):
        return () if self.scope == "bound_upstream" else (
            "locked_upstream_authority", "actual_visible_copy_delta", "materialized_operation",
        )


def density_policy_issues(density, *, no_change: bool):
    """Shape + density policy only; never certifies declared evidence as true."""
    if not isinstance(no_change, bool):
        raise ValueError("density policy requires an explicit boolean mode")
    prefix = "content_enrichment_audit.density_audit"
    issues = []
    def issue(code, field, expected, actual, message):
        issues.append(ContractIssue(code, field, expected, actual, message))
    if not isinstance(density, dict) or density.get("status") != "PASS":
        issue("C06.DENSITY.STATUS", prefix + ".status", "PASS",
              density.get("status") if isinstance(density, dict) else density,
              "0.6 content_enrichment_audit.density_audit must be structured PASS")
    if not isinstance(density, dict):
        return issues
    dimensions = density.get("dimensions")
    if not isinstance(dimensions, dict) or set(dimensions) != set(DENSITY_DIMENSIONS):
        issue("C06.DENSITY.DIMENSIONS", prefix + ".dimensions", list(DENSITY_DIMENSIONS),
              dimensions, f"0.6 density_audit.dimensions must contain exactly {list(DENSITY_DIMENSIONS)}")
        return issues
    if any(not isinstance(dimensions[name], bool) for name in DENSITY_DIMENSIONS):
        issue("C06.DENSITY.BOOLEANS", prefix + ".dimensions", "exact boolean dimensions",
              dimensions, "0.6 density_audit dimensions must all be booleans")
        return issues
    supported = sum(value is True for value in dimensions.values())
    count = density.get("supported_dimension_count")
    if not isinstance(count, int) or isinstance(count, bool):
        issue("C06.DENSITY.COUNT_TYPE", prefix + ".supported_dimension_count",
              "non-boolean integer", count,
              "0.6 density_audit.supported_dimension_count must be a non-boolean integer")
    elif count != supported:
        issue("C06.DENSITY.COUNT", prefix + ".supported_dimension_count", supported, count,
              f"0.6 density_audit.supported_dimension_count={count} != {supported}")
    if not _nonempty_text(density.get("evidence_notes")):
        issue("C06.DENSITY.NOTES", prefix + ".evidence_notes", "non-empty string",
              density.get("evidence_notes"), "0.6 density_audit.evidence_notes required")
    minimum = 4 if no_change else 1
    if supported < minimum:
        issue("C06.DENSITY.MINIMUM", prefix + ".supported_dimension_count", f">= {minimum}",
              supported,
              f"zero-delta 0.6 requires at least four evidence-supported Deep Summary dimensions; found {supported}"
              if no_change else "changed 0.6 copy requires at least one evidence-supported Deep Summary dimension")
    if no_change and dimensions.get("changed_state") is not True:
        issue("C06.DENSITY.CHANGED_STATE", prefix + ".dimensions.changed_state", True,
              dimensions.get("changed_state"),
              "zero-delta 0.6 requires changed_state=true in the density audit")
    return issues


def grounding_issues(dimension: str, visible_counts: Mapping, evidence_counts: Mapping,
                     visible_strengths: Mapping[str, Sequence[int]],
                     evidence_strengths: Mapping[str, Sequence[int]], *, require_realized: bool):
    """Common occurrence/modality policy over existing extractor observations.

    Callers must explicitly choose realized-state policy. The extractor is still
    the legacy finite signal engine; absence of issues is not full semantic proof.
    """
    if dimension not in DENSITY_DIMENSIONS or not isinstance(require_realized, bool):
        raise ValueError("grounding policy requires a known dimension and boolean mode")
    field = "content_enrichment_audit.density_audit.dimension_evidence." + dimension + ".evidence_refs"
    issues = []
    missing = {
        signal: {"required_occurrences": count, "evidence_occurrences": evidence_counts.get(signal, 0)}
        for signal, count in visible_counts.items() if evidence_counts.get(signal, 0) < count
    }
    if missing:
        issues.append(ContractIssue(
            "C06.GROUNDING.OCCURRENCES", field, "evidence covering every mapped signal occurrence", missing,
            f"{'zero-delta ' if require_realized else ''}0.6 dimension {dimension} is not grounded in referenced upstream source quote/claim evidence "
            f"for every signal occurrence; missing={missing}",
        ))
    if dimension != "changed_state":
        return issues
    gaps = {key: list(required) for key, required in visible_strengths.items()
            if not _strength_multiset_covers(required, evidence_strengths.get(key, []))}
    if gaps:
        issues.append(ContractIssue(
            "C06.GROUNDING.MODALITY", field, "same subject/state at equal-or-stronger modality", gaps,
            "0.6 changed_state subject/modality claims are not grounded in referenced upstream evidence; "
            f"required_current_strengths={gaps}",
        ))
    realized = any(
        any(strength >= 2 for strength in strengths)
        and _strength_multiset_covers([strength for strength in strengths if strength >= 2],
                                     evidence_strengths.get(key, []))
        for key, strengths in visible_strengths.items()
    )
    if require_realized and not realized:
        issues.append(ContractIssue(
            "C06.GROUNDING.REALIZED", field, "at least one evidence-grounded realized state", False,
            "zero-delta 0.6 changed_state requires at least one evidence-grounded realized strength-2 subject/state claim",
        ))
    return issues

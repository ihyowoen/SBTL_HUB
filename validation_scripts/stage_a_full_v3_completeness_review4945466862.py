#!/usr/bin/env python3
"""Stage A hardening for Codex review 4945466862.

This layer preserves the supported public route-only ``check_stage_a`` shape
while keeping real Stage A artifacts fail-closed.  It also closes reverse
ledger-disposition coverage, strict source-URL usability, and explicitly
selected legal-policy stage applicability gaps reported in the follow-up
review of the 4943980352 fixes.
"""
from __future__ import annotations

from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness as _base_contract
from validation_scripts import stage_a_full_v3_completeness_review4943777463 as _historical
from validation_scripts import stage_a_full_v3_completeness_review4943878732 as _previous

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
prevalidate_full_stage_a_artifact = _previous.prevalidate_full_stage_a_artifact

# A single pool is a supported public route-only validation payload, especially
# {"strict_passed_spec": [...]}.  Real Stage A output materializes several
# outcome/accounting pools, while the older strong provenance/accounting
# markers remain unambiguous full-artifact signals.
_STAGE_A_OUTPUT_POOL_KEYS = _previous._STAGE_A_OUTPUT_POOL_KEYS
_CANONICAL_DISPOSITION_POOLS = (
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
    "rejected",
    "existing_reinforcement",
    "support_source_only",
)


def looks_like_full_stage_a_artifact(data: Any) -> bool:
    """Discriminate real/incomplete full output from supported route-only input.

    Historical strong markers are sufficient on their own.  If those markers
    have been stripped, two or more Stage A outcome/accounting pool keys still
    identify a generated Stage A artifact, without converting the longstanding
    single-pool route-contract API into a full-artifact validator.
    """
    if _historical.looks_like_full_stage_a_artifact(data):
        return True
    if not isinstance(data, Mapping):
        return False
    pool_key_count = sum(1 for field in _STAGE_A_OUTPUT_POOL_KEYS if field in data)
    return pool_key_count >= 2


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _story_ids(item: Mapping[str, Any], *, strict: bool = False) -> set[str]:
    result: set[str] = set()
    story_id = item.get("story_id")
    if _nonempty_text(story_id):
        result.add(story_id.strip())
    grouped = item.get("grouped_story_ids")
    if isinstance(grouped, list):
        result.update(value.strip() for value in grouped if _nonempty_text(value))
    if strict:
        source_ids = item.get("source_story_ids")
        if isinstance(source_ids, list):
            result.update(value.strip() for value in source_ids if _nonempty_text(value))
    return result


def _emitted_story_ids(data: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for pool in _CANONICAL_DISPOSITION_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for item in values:
            if isinstance(item, Mapping):
                result.update(_story_ids(item, strict=pool == "strict_passed_spec"))
    return result


def _validate_reverse_ledger_disposition_coverage(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    """Every source-ledger story must appear in exactly one emitted disposition.

    Earlier layers already reject cross-pool duplicate dispositions.  This
    reverse check closes the other direction: a ledger story may not disappear
    from all emitted outcome pools while remaining inside story_count/accounting.
    """
    ledger = data.get("decision_ledger")
    if not isinstance(ledger, list):
        return
    emitted = _emitted_story_ids(data)
    for index, row in enumerate(ledger):
        if not isinstance(row, Mapping):
            continue
        story_id = row.get("story_id")
        if not _nonempty_text(story_id):
            continue
        normalized = story_id.strip()
        if normalized not in emitted:
            messages.append(
                f"decision_ledger[{index}] story {normalized}: no emitted canonical Stage A disposition"
            )


def _validate_strict_source_urls(data: Mapping[str, Any], messages: list[str]) -> None:
    values = data.get("strict_passed_spec")
    if not isinstance(values, list):
        return
    for index, item in enumerate(values):
        if not isinstance(item, Mapping):
            continue
        label = item.get("spec_id") if _nonempty_text(item.get("spec_id")) else f"strict_passed_spec[{index}]"
        primary_url = item.get("primary_url")
        if not _nonempty_text(primary_url):
            messages.append(f"{label}: primary_url must be a non-blank source URL candidate")
        urls = item.get("urls")
        if (
            not isinstance(urls, list)
            or not urls
            or not any(_nonempty_text(value) for value in urls)
        ):
            messages.append(f"{label}: urls must contain at least one non-blank source URL candidate")
        elif any(not _nonempty_text(value) for value in urls):
            messages.append(f"{label}: urls entries must be non-blank strings")


def _legal_policy_inferred_from_anchor_or_lens(item: Mapping[str, Any]) -> bool:
    classes = item.get("anchor_classes")
    lenses = item.get("structural_value_lenses")
    return (
        isinstance(classes, list) and "policy_regulatory_anchor" in classes
    ) or (
        isinstance(lenses, list)
        and any(
            isinstance(value, str) and ("policy" in value or "legal" in value)
            for value in lenses
        )
    )


def _validate_explicit_legal_stage_applicability(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    """A canonical legal stage is itself an applicability declaration."""
    for pool in (
        "strict_passed_spec",
        "candidate_review_pool",
        "watchlist_context_pool",
        "reject_or_support_only_pool",
    ):
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            stage = item.get("legal_policy_stage")
            if stage not in _base_contract.LEGAL_POLICY_STAGES:
                continue
            # The base validator already performs the full legal-policy check
            # when the anchor/lens declares applicability.  Only close the
            # explicit-stage-only bypass here to avoid duplicate diagnostics.
            if _legal_policy_inferred_from_anchor_or_lens(item):
                continue
            label = item.get("spec_id") if _nonempty_text(item.get("spec_id")) else f"{pool}[{index}]"
            for field in _base_contract.LEGAL_POLICY_FIELDS:
                if field not in item:
                    messages.append(f"{label}: legal-policy candidate missing {field}")
                    continue
                value = item.get(field)
                if field in _base_contract.LEGAL_ARRAY_FIELDS:
                    if not isinstance(value, list):
                        messages.append(f"{label}: legal-policy {field} must be an array")
                elif value is None or (isinstance(value, str) and not value.strip()):
                    messages.append(f"{label}: legal-policy {field} must be populated")


def validate_full_stage_a_artifact(
    data: Mapping[str, Any], compat_module: Any
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    _validate_reverse_ledger_disposition_coverage(data, messages)
    _validate_strict_source_urls(data, messages)
    _validate_explicit_legal_stage_applicability(data, messages)
    return messages

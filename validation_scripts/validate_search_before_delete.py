#!/usr/bin/env python3
"""Validate claim-level search-before-delete audit metadata.

Usage:
    python validation_scripts/validate_search_before_delete.py artifact.json

Exit 0: PASS
Exit 1: BLOCKED_SEARCH_BEFORE_DELETE_AUDIT_MISSING or malformed artifact
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

BLOCK_STATUS = "BLOCKED_SEARCH_BEFORE_DELETE_AUDIT_MISSING"

AUDIT_REQUIRED_FIELDS = {
    "claim_gap_id",
    "original_claim",
    "affected_fields",
    "full_existing_source_packet_checked",
    "cited_source_refetch_attempted",
    "official_or_primary_search_attempted",
    "independent_tier1_tier2_search_attempted",
    "search_queries",
    "searched_urls",
    "source_discovery_result",
    "recovered_sources",
    "recovered_quotes",
    "claim_repair_before_deletion_check",
    "final_claim_disposition",
    "final_disposition_reason",
}

SEARCH_RESULTS = {
    "supported_and_restored",
    "supported_and_narrowed",
    "not_found_after_bounded_search",
    "source_access_blocked",
    "source_direction_conflict",
}

FINAL_DISPOSITIONS = {
    "restored",
    "retained",
    "narrowed_after_search",
    "deleted_after_search",
    "controlled_hold",
}

NEGATIVE_OUTCOME_KEYS = {
    "revise_blocked_needs_source_augmentation",
    "revise_blocked_evidence_gap",
    "revise_blocked_scope_change_required",
    "revise_blocked_manual_review",
    "rejected",
    "support_source_only",
    "deferred_review_pool",
    "duplicate_hold",
    "baseline_conflict",
    "review_pool_deferred",
    "mandatory_evidence_rescue",
    "production_hold",
    "needs_source_augmentation",
    "evidence_qc_rejected",
    "addable_hold_source_gap",
    "addable_hold_claim_gap",
    "source_claim_gap",
    "single_source_exception_review",
}


def walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


def looks_like_claim_reduction(record: dict[str, Any]) -> bool:
    action_text = " ".join(
        str(record.get(key, ""))
        for key in (
            "field",
            "action",
            "decision",
            "outcome",
            "state",
            "change_type",
            "final_claim_disposition",
            "notes",
            "reason",
            "stage_c_issue_addressed",
        )
    ).lower()
    english_patterns = (
        r"delete(?:d|s|ing)?",
        r"remove(?:d|s|ing)?",
        r"narrow(?:ed|s|ing)?",
        r"hold(?:s|ing)?",
        r"held",
        r"block(?:ed|s|ing)?",
        r"reject(?:ed|s|ing)?",
        r"defer(?:red|s|ring)?",
        r"support[_-]only",
    )
    if any(
        re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", action_text)
        for pattern in english_patterns
    ):
        return True

    korean_terms = ("축소", "삭제", "제거", "보류", "차단", "기각")
    return any(term in action_text for term in korean_terms)


def looks_like_full_audit(record: dict[str, Any]) -> bool:
    """Return true for claim-gap records that contain audit metadata.

    Negative outcome buckets may use lightweight reference rows that only carry
    ``claim_gap_id``/``claim_gap_ids`` to point at a complete audit elsewhere.
    Those reference rows should be checked for a valid link, not validated as
    full audit objects.
    """
    return "claim_gap_id" in record and any(
        field in record for field in AUDIT_REQUIRED_FIELDS - {"claim_gap_id"}
    )


def validate_audit(audit: Any, path: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(audit, dict):
        return [f"{path}: audit must be an object"]

    missing = sorted(AUDIT_REQUIRED_FIELDS - audit.keys())
    if missing:
        errors.append(f"{path}: missing fields {missing}")
        return errors

    for flag in (
        "full_existing_source_packet_checked",
        "cited_source_refetch_attempted",
        "official_or_primary_search_attempted",
        "independent_tier1_tier2_search_attempted",
    ):
        if audit.get(flag) is not True:
            errors.append(f"{path}.{flag}: must be true")

    if not isinstance(audit.get("search_queries"), list) or not audit["search_queries"]:
        errors.append(f"{path}.search_queries: must be a non-empty list")
    if not isinstance(audit.get("searched_urls"), list):
        errors.append(f"{path}.searched_urls: must be a list")
    if not isinstance(audit.get("affected_fields"), list) or not audit["affected_fields"]:
        errors.append(f"{path}.affected_fields: must be a non-empty list")
    source_discovery_result = audit.get("source_discovery_result")
    if source_discovery_result not in SEARCH_RESULTS:
        errors.append(f"{path}.source_discovery_result: invalid value")
    elif source_discovery_result in {"supported_and_restored", "supported_and_narrowed"}:
        if not isinstance(audit.get("recovered_sources"), list) or not audit["recovered_sources"]:
            errors.append(
                f"{path}.recovered_sources: must be a non-empty list "
                "for supported outcomes"
            )
        if not isinstance(audit.get("recovered_quotes"), list) or not audit["recovered_quotes"]:
            errors.append(
                f"{path}.recovered_quotes: must be a non-empty list "
                "for supported outcomes"
            )
    if audit.get("final_claim_disposition") not in FINAL_DISPOSITIONS:
        errors.append(f"{path}.final_claim_disposition: invalid value")
    if audit.get("claim_repair_before_deletion_check") != "PASS":
        errors.append(f"{path}.claim_repair_before_deletion_check: must be PASS")
    if not str(audit.get("original_claim", "")).strip():
        errors.append(f"{path}.original_claim: must be non-empty")
    if not str(audit.get("final_disposition_reason", "")).strip():
        errors.append(f"{path}.final_disposition_reason: must be non-empty")

    return errors


def validate(data: Any) -> list[str]:
    errors: list[str] = []
    audits: list[tuple[str, Any]] = []

    for path, value in walk(data):
        if isinstance(value, dict) and looks_like_full_audit(value):
            audits.append((path, value))

    for path, audit in audits:
        errors.extend(validate_audit(audit, path))

    audit_ids = {
        str(audit.get("claim_gap_id"))
        for _, audit in audits
        if isinstance(audit, dict) and audit.get("claim_gap_id")
    }

    for path, value in walk(data):
        if not isinstance(value, dict):
            continue

        key_name = path.rsplit(".", 1)[-1].split("[", 1)[0]
        negative_bucket = key_name in NEGATIVE_OUTCOME_KEYS
        reduction = looks_like_claim_reduction(value)
        if not (negative_bucket or reduction):
            continue

        linked = value.get("claim_gap_id") or value.get("claim_gap_ids")
        if isinstance(linked, list):
            linked_ids = {str(item) for item in linked}
        elif linked:
            linked_ids = {str(linked)}
        else:
            linked_ids = set()

        inline = value.get("search_before_delete_audit") or value.get("claim_search_audit")
        if inline:
            inline_items = inline if isinstance(inline, list) else [inline]
            for index, item in enumerate(inline_items):
                errors.extend(validate_audit(item, f"{path}.search_before_delete_audit[{index}]"))
            continue

        if not linked_ids or not linked_ids.issubset(audit_ids):
            errors.append(
                f"{path}: negative/reduction outcome lacks a valid claim-level "
                "search-before-delete audit reference"
            )

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_search_before_delete.py artifact.json", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"INVALID_JSON: {exc}", file=sys.stderr)
        return 1

    errors = validate(data)
    if errors:
        print(BLOCK_STATUS)
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS_SEARCH_BEFORE_DELETE_AUDIT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Prompt 0.5 source-diversity and source-audit checker.

Source-derived counters are recomputed from current fact_sources. Canonical URLs,
hostnames and editorial owners are separate measures.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

from card_audit_utils import (
    canonical_url,
    is_landing_page,
    is_visible_source,
    load_owner_registry,
    select_scoped_cards,
    source_audit_measure,
    usable_sources,
)

PASS = {"PASS_MULTI_SOURCE", "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION"}
HOLD = {"HOLD_NEEDS_SOURCE_AUGMENTATION", "FAIL_SOURCE_DIVERSITY"}
ALLOWED = PASS | HOLD
COMPLETE = {
    "accepted", "accepted_fact_safe", "accepted_fact_safe_with_warnings",
    "evidence_complete_and_source_claim_covered", "publish_ready",
    "github_merge_ready", "production_verified",
}
BUCKETS = (
    "addable_merge_safe", "cards", "draft_cards", "qc_cards", "payload",
    "accepted", "accepted_fact_safe", "accepted_fact_safe_with_warnings",
    "evidence_complete_and_source_claim_covered", "addable_hold_source_gap",
    "addable_hold_claim_gap", "needs_source_augmentation", "evidence_qc_rejected",
    "source_claim_gap", "single_source_exception_review", "deferred_review_pool",
    "review_pool_deferred", "publish_ready", "github_merge_ready",
)
CORR = re.compile(
    r"safety|recall|리콜|점유율|market\s*share|시장\s*점유|ranking|순위|1위|최대|최초|world.?first|업계\s*최",
    re.I,
)
OFFICIAL_TERMS = (
    "official", "regulatory", "regulator", "filing", "sec_filing", "court",
    "original_dataset", "original_data", "contracting_party", "project_owner",
    "source_owner", "research_institution", "company_primary",
    "primary_announcement", "government", "ministry", "agency",
    "issuer_release", "press_release_owner",
)


def load(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def integer(obj: Any, *keys: str):
    if not isinstance(obj, dict):
        return None
    for key in keys:
        value = obj.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def metadata(source: dict[str, Any]) -> str:
    keys = (
        "source_type", "source_kind", "source_origin_type", "source_role",
        "publisher_type", "origin_type", "official_source_type", "source_category",
    )
    return " ".join(str(source.get(key, "")).lower() for key in keys)


def primary(source: dict[str, Any]) -> bool:
    if source.get("is_official") is True or source.get("official_source") is True:
        return True
    if source.get("is_primary_source") is True:
        return True
    if str(source.get("evidence_role", "")).lower() in {
        "official_material_evidence", "official_source", "primary_source",
        "regulatory_filing", "original_dataset", "primary_event_evidence",
    }:
        return True
    return any(term in metadata(source) for term in OFFICIAL_TERMS)


def valid_exception(card: dict[str, Any], visible_sources: list[dict[str, Any]]) -> bool:
    exception = card.get("single_source_exception")
    return (
        card.get("source_diversity_status")
        == "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION"
        and isinstance(exception, dict)
        and exception.get("allowed") is True
        and bool(exception.get("reason"))
        and bool(exception.get("mitigation") or exception.get("scope_limits"))
        and any(primary(source) for source in visible_sources)
    )


def cards(data: Any):
    if isinstance(data, list):
        return data
    output = []
    seen = set()
    if not isinstance(data, dict):
        return output
    for bucket in BUCKETS:
        values = data.get(bucket)
        if not isinstance(values, list):
            continue
        for row in values:
            if not isinstance(row, dict):
                continue
            marker = (
                row.get("id") or row.get("card_id") or row.get("source_spec_id")
                or row.get("spec_id") or id(row)
            )
            if marker in seen:
                continue
            seen.add(marker)
            copied = dict(row)
            copied["__qc_bucket"] = bucket
            output.append(copied)
    return output


def load_ids(path: str | None) -> set[str] | None:
    if path is None:
        return None
    source = Path(path)
    if source.suffix.lower() == ".csv":
        rows = csv.DictReader(source.open(encoding="utf-8-sig"))
        values = set()
        for row in rows:
            value = row.get("assigned_id") or row.get("id") or row.get("card_id")
            if value:
                values.add(str(value))
        return values
    payload = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {str(value) for value in payload}
    if isinstance(payload, dict):
        for key in ("ids", "new_ids", "production_ids"):
            if isinstance(payload.get(key), list):
                return {str(value) for value in payload[key]}
    raise ValueError("ID scope file must be a list, ids[] JSON, or CSV with assigned_id/id/card_id")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument(
        "--owner-registry",
        default="validation_data/source_owner_registry.json",
    )
    parser.add_argument("--json-report")
    parser.add_argument("--id-file", "--new-id-file", dest="id_file")
    args = parser.parse_args()

    registry_path = Path(args.owner_registry)
    registry = load_owner_registry(registry_path if registry_path.exists() else None)
    rows = cards(load(args.input))
    selected_ids = load_ids(args.id_file)
    rows, scope = select_scoped_cards(rows, selected_ids)

    names = (
        "invalid_id_scope", "invalid_source_url", "landing_page",
        "fake_diversity", "weak_corroboration", "url_desync",
        "invalid_source_diversity_status", "missing_source_discovery_ledger",
        "resolution_mismatch",
    )
    flags = {name: [] for name in names}
    for message in scope["errors"]:
        flags["invalid_id_scope"].append(("<id-scope>", message))
    reuse = []

    for card in rows:
        cid = (
            card.get("id") or card.get("card_id") or card.get("source_spec_id")
            or card.get("spec_id") or "<no-id>"
        )
        bucket = card.get("__qc_bucket")
        status = card.get("source_diversity_status")
        sources = usable_sources(card)
        visible_sources = [source for source in sources if is_visible_source(source)]
        measure = source_audit_measure(card, registry)

        if measure["missing_source_url_count"]:
            flags["invalid_source_url"].append(
                (cid, f"{measure['missing_source_url_count']} usable source row(s) lack a durable HTTP(S) URL")
            )
        if measure["missing_visible_source_url_count"]:
            flags["invalid_source_url"].append(
                (cid, f"{measure['missing_visible_source_url_count']} visible source row(s) lack a durable HTTP(S) URL")
            )

        source_urls = [source.get("source_url") for source in sources if source.get("source_url")]
        visible_urls = [
            source.get("source_url") for source in visible_sources if source.get("source_url")
        ]
        ledger = (
            card.get("source_discovery_ledger")
            or card.get("source_discovery_ledger_ref")
            or card.get("source_discovery_ledger_reference")
        )

        if status not in ALLOWED:
            flags["invalid_source_diversity_status"].append(
                (cid, f"missing/invalid source_diversity_status={status}")
            )
        if bucket in COMPLETE and status in HOLD:
            flags["invalid_source_diversity_status"].append(
                (cid, f"{status} may not appear in complete bucket {bucket}")
            )
        if status == "PASS_MULTI_SOURCE":
            if measure["visible_source_url_count"] < 2:
                flags["invalid_source_diversity_status"].append(
                    (cid, "PASS_MULTI_SOURCE requires >=2 visible source URLs")
                )
            if measure["source_independent_owner_count"] < 2:
                flags["invalid_source_diversity_status"].append(
                    (cid, "PASS_MULTI_SOURCE requires >=2 independent owners")
                )
        if (
            status == "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION"
            and not valid_exception(card, visible_sources)
        ):
            flags["invalid_source_diversity_status"].append(
                (cid, "single-source pass exception invalid")
            )
        if status == "PASS_SINGLE_SOURCE":
            flags["invalid_source_diversity_status"].append(
                (cid, "PASS_SINGLE_SOURCE is not allowed")
            )

        for url in source_urls:
            if is_landing_page(str(url)):
                flags["landing_page"].append((cid, url))

        declared = {
            "source_evidence_entry_count": integer(card, "source_evidence_entry_count"),
            "source_unique_url_count": integer(card, "source_unique_url_count", "distinct_source_urls"),
            "source_unique_domain_count": integer(card, "source_unique_domain_count"),
            "source_independent_owner_count": integer(card, "source_independent_owner_count", "independent_owner_count"),
        }
        for field, actual in measure.items():
            if field not in declared:
                continue
            value = declared[field]
            if value is not None and value != actual:
                flags["fake_diversity"].append(
                    (cid, f"declared {field}={value}, actual={actual}")
                )

        if len(sources) > measure["source_unique_url_count"]:
            reuse.append(
                (cid, f"{len(sources)} claim rows / {measure['source_unique_url_count']} canonical URLs")
            )
        if status in PASS and not ledger:
            flags["missing_source_discovery_ledger"].append(
                (cid, f"{status} requires source_discovery_ledger/ref")
            )

        visible_blob = " ".join(str(card.get(key, "")) for key in ("title", "sub", "gate", "fact"))
        needs = str(card.get("signal", "")).lower() in {"top", "high"} or bool(CORR.search(visible_blob))
        if (
            needs
            and measure["source_independent_owner_count"] < 2
            and not valid_exception(card, visible_sources)
        ):
            flags["weak_corroboration"].append(
                (cid, "high/sensitive card lacks independent owner or valid primary exception")
            )

        card_urls = set(card.get("urls") or [])
        for url in visible_urls:
            if url not in card_urls:
                flags["url_desync"].append((cid, url))

        resolution = card.get("source_url_resolution")
        if isinstance(resolution, dict):
            entries = resolution.get("resolution_entries") or []
            resolved_urls = {
                value
                for entry in entries
                if isinstance(entry, dict)
                and (value := canonical_url(str(entry.get("source_url", ""))))
            }
            if resolved_urls != set(measure["canonical_urls"]):
                flags["resolution_mismatch"].append(
                    (cid, "resolution URLs do not equal current fact_sources canonical URLs")
                )
            if resolution.get("supporting_fact_source_count") != len(sources):
                flags["resolution_mismatch"].append(
                    (cid, "supporting_fact_source_count mismatch")
                )

    total = sum(len(values) for values in flags.values())
    report = {
        "id_scope": scope,
        "cards_checked": len(rows),
        "flags": {name: len(flags[name]) for name in names},
        "flag_details": flags,
        "claim_row_url_reuse_info": reuse,
        "total_flags": total,
        "status": "PASS" if total == 0 else "FAIL",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.json_report:
        Path(args.json_report).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())

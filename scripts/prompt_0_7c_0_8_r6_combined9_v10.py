#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V9_PATH = ROOT / "scripts/prompt_0_7c_0_8_r6_combined9_v9.py"
spec = importlib.util.spec_from_file_location("r6_combined9_v9", V9_PATH)
v9 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(v9)

core = v9.core

# The cross-issuer earnings card is intentionally dated to the current source-bound
# Mining.com signal publication, while its Stage-B fact package uses earlier issuer
# filings/releases for the underlying earnings numbers. Preserve that original
# source-bound publication anchor instead of pretending an issuer filing was dated
# 2026-08-31.
DATE_SOURCE_OVERRIDES = {
    "STD26_R6_P01P_024": {
        "event_date": "2026-08-31",
        "url": "https://www.mining.com/web/lithium-miners-post-big-profits-as-battery-storage-demand-surges",
        "evidence": "Lithium miners post big profits as battery storage demand surges - Mining.com",
        "evidence_semantics": "source_bound_headline_from_prompt_0_1p_promotion_ledger",
        "provenance": "runs/2026-09-03/stage_a_prompt_0_1p_r6_promotion16_20260903_R1.json",
    }
}


def _valid_http(value) -> bool:
    return isinstance(value, str) and value.startswith(("http://", "https://"))


def _date_tokens(date_value: str) -> list[str]:
    year, month, day = [int(x) for x in date_value.split("-")]
    month_names = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
    ]
    month_abbr = [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec",
    ]
    full = month_names[month - 1]
    abbr = month_abbr[month - 1]
    return [
        date_value.casefold(),
        f"{year}/{month:02d}/{day:02d}".casefold(),
        f"{year}.{month:02d}.{day:02d}".casefold(),
        f"{full} {day} {year}".casefold(),
        f"{full} {day}, {year}".casefold(),
        f"{abbr} {day} {year}".casefold(),
        f"{abbr}. {day} {year}".casefold(),
        f"{abbr}.{day} {year}".casefold(),
        f"{month}/{day}/{year}".casefold(),
        f"{month}/{day}".casefold(),
        f"{year}년 {month}월 {day}일".casefold(),
        f"{month}월 {day}일".casefold(),
        f"{year}年{month}月{day}日".casefold(),
    ]


def _supports_date(text: str, event_date: str) -> bool:
    folded = text.casefold()
    return any(token in folded for token in _date_tokens(event_date))


def _event_date_evidence(source: dict, sid: str, event_date: str) -> dict:
    override = DATE_SOURCE_OVERRIDES.get(sid)
    if override is not None:
        if override["event_date"] != event_date:
            raise AssertionError(f"{sid}: date-source override no longer matches Stage C event date")
        return copy.deepcopy(override)

    fact_sources = source.get("fact_sources")
    if not isinstance(fact_sources, list) or not fact_sources:
        raise AssertionError(f"{sid}: Stage C fact_sources missing for date evidence")

    ranked = []
    for index, fact_source in enumerate(fact_sources):
        if not isinstance(fact_source, dict):
            continue
        url = fact_source.get("url") or fact_source.get("source_url")
        if not _valid_http(url):
            continue
        published = fact_source.get("published") or fact_source.get("publication_date")
        source_quote = fact_source.get("source_quote")
        quote_verified = (
            isinstance(source_quote, str)
            and source_quote.strip()
            and isinstance(fact_source.get("source_quote_status"), str)
            and "verified" in fact_source["source_quote_status"].casefold()
        )
        summary = fact_source.get("summary")
        summary_ok = isinstance(summary, str) and bool(summary.strip())
        evidence = source_quote.strip() if quote_verified else (summary.strip() if summary_ok else None)
        if not evidence:
            continue

        exact_publication_anchor = published == event_date
        explicit_date_anchor = _supports_date(evidence, event_date)
        if quote_verified and exact_publication_anchor:
            rank = 0
            semantics = "body_quote_verified_on_representative_event_date"
        elif summary_ok and exact_publication_anchor:
            rank = 1
            semantics = "validated_stage_c_source_summary_on_representative_event_date_not_verbatim_quote"
        elif quote_verified and explicit_date_anchor:
            rank = 2
            semantics = "body_quote_verified_with_explicit_event_date"
        elif summary_ok and explicit_date_anchor:
            rank = 3
            semantics = "validated_stage_c_source_summary_with_explicit_event_date_not_verbatim_quote"
        else:
            # Do not silently use a source that neither published on the event date
            # nor explicitly states it. That would convert a shape fix into a new
            # date adjudication.
            continue

        ranked.append((rank, index, {
            "event_date": event_date,
            "url": url,
            "evidence": evidence,
            "evidence_semantics": semantics,
            "source_id": fact_source.get("id"),
            "source_published": published,
            "provenance": "validated_stage_c_fact_sources",
        }))

    if not ranked:
        raise AssertionError(
            f"{sid}: no validated Stage C fact source either published on {event_date} "
            "or explicitly stating that date; date role must be rereviewed, not synthesized"
        )
    ranked.sort(key=lambda value: (value[0], value[1]))
    return ranked[0][2]


def _normalize_date_role(card: dict, source: dict) -> dict:
    sid = card.get("source_spec_id") or card.get("spec_id")
    if not isinstance(sid, str) or not sid:
        raise AssertionError(f"{card.get('id')}: source_spec_id missing")

    source_role = source.get("date_role")
    if not isinstance(source_role, dict) or source_role.get("status") != "PASS":
        raise AssertionError(f"{sid}: validated Stage C date_role PASS package missing")
    source_lineage = source.get("related_lineage")
    if not isinstance(source_lineage, dict) or not v9._pass_marker(source_lineage.get("earliest_date_check")):
        raise AssertionError(f"{sid}: Stage C earliest_date_check not PASS")

    representative = (
        source_role.get("representative_event_date")
        or source_role.get("representative_date")
        or source_role.get("stage_a_representative_date")
    )
    if not isinstance(representative, str) or len(representative) != 10:
        raise AssertionError(f"{sid}: Stage C representative event date missing")
    if card.get("date") != representative:
        raise AssertionError(
            f"{sid}: production card date {card.get('date')} != validated representative date {representative}"
        )

    publications = source_role.get("source_publication_dates") or source_role.get("publication_dates")
    if not isinstance(publications, list) or not publications:
        raise AssertionError(f"{sid}: Stage C source publication dates missing")

    evidence = _event_date_evidence(source, sid, representative)
    role = copy.deepcopy(card.get("date_role") if isinstance(card.get("date_role"), dict) else source_role)
    # Preserve legacy Stage-C fields and add the exact current date-role contract.
    role["representative_date"] = representative
    role["event_date"] = representative
    role["source_publication_dates"] = copy.deepcopy(publications)
    role["publication_dates"] = copy.deepcopy(publications)
    role["earliest_same_event_date_checked"] = True
    role["event_date_source_url"] = evidence["url"]
    role["event_date_source_quote"] = evidence["evidence"]
    role["event_date_source_evidence_semantics"] = evidence["evidence_semantics"]
    if evidence.get("source_id"):
        role["event_date_source_id"] = evidence["source_id"]
    if evidence.get("source_published"):
        role["event_date_source_publication_date"] = evidence["source_published"]
    role["event_date_source_provenance"] = evidence["provenance"]
    role["date_role_contract_projection"] = {
        "status": "PASS",
        "source_stage": "Stage C",
        "source_spec_id": sid,
        "projection_only_no_date_readjudication": True,
        "representative_date_preserved": True,
        "source_publication_dates_preserved": True,
        "earliest_date_pass_preserved": True,
    }
    return role


def build_operations_with_date_contract(final_rows, stage_refs):
    operations = v9.build_operations_with_stage_c_insert_contract(final_rows, stage_refs)
    stage_c = v9._stage_c_by_spec()
    for op in operations.get("insert", []):
        card = op.get("card") if isinstance(op, dict) else None
        if not isinstance(card, dict):
            raise AssertionError("insert card missing")
        sid = card.get("source_spec_id") or card.get("spec_id")
        source = stage_c.get(sid)
        if not isinstance(source, dict):
            raise AssertionError(f"{card.get('id')}: no exact Stage C source for date-role projection")
        card["date_role"] = _normalize_date_role(card, source)
    return operations


def _mirror_insert_date_roles_into_stage_0_7() -> None:
    bridge = core.OUT / "stages/stage-0-7-combined9.json"
    payload = core.load(bridge)
    rows = payload.get("publish_ready")
    if not isinstance(rows, list) or len(rows) != 9:
        raise AssertionError("run-bound Stage 0.7 bridge must contain exact publish_ready[9]")

    # Recompute from the same validated Stage C sources rather than reading the
    # generated card-run, so the bridge remains a transparent stage projection.
    stage_c = v9._stage_c_by_spec()
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise AssertionError("Stage 0.7 publish_ready row must be object")
        sid = row.get("source_spec_id") or row.get("spec_id")
        source = stage_c.get(sid)
        if not isinstance(source, dict):
            raise AssertionError(f"Stage 0.7 row has no exact Stage C source: {sid}")
        row["date_role"] = _normalize_date_role(row, source)
        seen.add(sid)
    if seen != set(stage_c):
        raise AssertionError("Stage 0.7 date-role projection does not cover exact Stage C 9-spec set")
    payload["formal_date_role_contract_projection"] = {
        "status": "PASS",
        "item_count": 9,
        "source_stage_c_artifacts": [core.rel(path) for path in v9.STAGE_C_SOURCES],
        "projection_only_no_date_readjudication": True,
    }
    core.write(bridge, payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = parser.parse_args()

    v9.v5.v4.v3.bind_validated_stage_b_rereview()
    v9.v5.v4.bind_validated_stage_a_relation_rereview()
    core.build_operations = build_operations_with_date_contract

    if args.phase == "prepare":
        core.prepare()
        v9.v5.v4.v3.v2.normalize_document_universe_bridge()
        _mirror_insert_date_roles_into_stage_0_7()
    else:
        core.finalize_audit()


if __name__ == "__main__":
    main()

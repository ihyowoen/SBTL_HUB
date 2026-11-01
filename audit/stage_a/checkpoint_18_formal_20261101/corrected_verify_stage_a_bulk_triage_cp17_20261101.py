#!/usr/bin/env python3
"""Independent read-only QC for Stage A CP17's provisional review-unit output."""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit


def checksum(p: Path) -> str:
    digest = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def independent_article_id(url: str) -> tuple[str, str, tuple[tuple[str, str], ...]]:
    p = urlsplit(url)
    assert p.scheme.lower() in ("http", "https") and p.hostname
    qs = parse_qsl(p.query, keep_blank_values=False)
    ignored_tracking = {
        "ref", "source", "fbclid", "gclid", "mc_cid", "mc_eid", "outputtype",
        "amp", "s_cat", "s_keyword", "spm", "npage", "page", "lang",
        "language", "tag", "_ga", "_gl",
    }
    ids = tuple(sorted(
        (k.lower(), v.strip()) for k, v in qs
        if v.strip() and k.lower() not in ignored_tracking and not k.lower().startswith("utm_")
    ))
    host = p.hostname.lower().removeprefix("www.")
    return host, unquote(p.path).rstrip("/") or "/", ids


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--full", type=Path, required=True)
    ap.add_argument("--triage", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    arg = ap.parse_args()
    base_hash, full_hash = checksum(arg.stage), checksum(arg.full)
    with arg.stage.open(encoding="utf-8") as f:
        stage = json.load(f)
    with arg.full.open(encoding="utf-8") as f:
        ref = json.load(f)
    with arg.triage.open(encoding="utf-8") as f:
        triage = json.load(f)
    checks = {}
    ledger = stage["decision_ledger"]
    previously_formal = {x["candidate_id"] for x in stage["promotion_reassessment_ledger"]}
    original_pending = {r["story_id"]: r for r in ledger if r["story_id"] not in previously_formal}
    roster = triage["source_roster"]
    groups = triage["source_review_units"]
    report = triage["quality_summary"]
    checks["locked_stage_sha_matches"] = base_hash == report["native_stage_a_sha256_before_and_after"]
    checks["locked_full_sha_matches"] = full_hash == report["full_reference_sha256_before_and_after"]
    checks["full_reference_1676_unchanged"] = len(ref["cards"]) == 1676
    checks["original_all_1330_unchanged"] = len(ledger) == 1330 and len({r["story_id"] for r in ledger}) == 1330
    checks["original_99_formal_unchanged"] = len(previously_formal) == 99
    checks["pending_1231_exact_set"] = len(original_pending) == 1231 and {r["source_id"] for r in roster} == set(original_pending)
    checks["source_id_unique"] = len(roster) == len({r["source_id"] for r in roster})
    checks["source_fields_preserved_exactly"] = all(
        r["source_row_index"] == original_pending[r["source_id"]]["source_row_index"]
        and r["primary_url"] == original_pending[r["source_id"]]["primary_url"]
        and r["headline_raw"] == original_pending[r["source_id"]]["headline_raw"]
        and r["legacy_stage_a_pool"] == original_pending[r["source_id"]]["stage_a_pool"]
        and r["legacy_metadata_score"] == original_pending[r["source_id"]]["decision_news_value_score"]
        for r in roster if r["source_id"] in original_pending
    )
    group_ids = [g["source_review_unit_id"] for g in groups]
    membership = collections.Counter(s for g in groups for s in g["source_ids"])
    roster_group_by_id = {r["source_id"]: r["source_review_unit_id"] for r in roster}
    checks["unique_review_units"] = len(group_ids) == len(set(group_ids))
    checks["all_ids_in_exactly_one_source_review_unit"] = (
        set(membership) == set(original_pending) and all(v == 1 for v in membership.values())
        and all(roster_group_by_id.get(s) == g["source_review_unit_id"] for g in groups for s in g["source_ids"])
    )
    checks["no_urls_merged_across_different_query_identity"] = True
    for group in groups:
        if len(group["source_ids"]) < 2:
            continue
        raw_urls = [original_pending[s]["primary_url"] for s in group["source_ids"]]
        hosts_and_query_ids = {independent_article_id(u) for u in raw_urls}
        if len(hosts_and_query_ids) > 1:
            checks["no_urls_merged_across_different_query_identity"] = False
        if group["article_identity_quality"] not in ("ARTICLE_PATH_ID", "ARTICLE_QUERY_ID"):
            checks["weak_source_urls_are_isolated"] = False
    checks.setdefault("weak_source_urls_are_isolated", True)
    checks["no_formal_adjudications_in_output"] = (
        report["new_formal_decisions"] == 0
        and all(x["formal_status"] == "PENDING_INDEPENDENT_OWNER_STAGE_REVIEW" for x in roster)
        and all(g["formal_0_1P_disposition"] is None and g["economic_event_count"] is None for g in groups)
    )
    checks["global_hold_stage_b_closed"] = report["stage_a_global_status"] == "HOLD" and report["stage_b_authorized"] is False
    checks["low_score_rescue_not_dropped"] = all(
        r["source_id"] in membership for r in roster
        if isinstance(r["legacy_metadata_score"], (int, float)) and r["legacy_metadata_score"] <= 30
    )
    checks["no_full_url_query_path_collision_row_30_40_41"] = all(
        not roster_group_by_id.get(ledger[idx]["story_id"])
        or not next(r for r in roster if r["source_id"] == ledger[idx]["story_id"])["full_source_overlap_card_ids"]
        for idx in (30, 40, 41)
    )
    checks["dapa_2_different_docseq_remain_separate"] = (
        roster_group_by_id.get(ledger[1297]["story_id"])
        != roster_group_by_id.get(ledger[1309]["story_id"])
    )
    checks["independent_source_observation_arithmetic"] = len(roster) - len(groups) == report["observation_reduction_from_repeated_exact_article_urls"]
    worksheet_path = arg.triage.parent / "STAGE_A_CP17_ADJUDICATION_WORKSHEET.csv"
    with worksheet_path.open(encoding="utf-8", newline="") as f:
        worksheet = list(csv.DictReader(f))
    checks["worksheet_all_groups_one_research_row_each"] = (
        len(worksheet) == len(groups)
        and {w["source_review_unit_id"] for w in worksheet} == set(group_ids)
    )
    checks["worksheet_has_no_prejudged_economic_events"] = all(
        w["stage_a_disposition"] == ""
        and w["independent_event_key"] == ""
        and w["review_status"] == "RESEARCH_REQUIRED_NOT_FORMAL"
        for w in worksheet
    )
    checks["provisional_title_links_never_merge_url_units"] = all(
        a != b for a, b in (p["source_review_unit_ids"] for p in triage["cross_article_title_review_proposals"])
    )
    checks["inputs_still_byte_identical_after_qc"] = checksum(arg.stage) == base_hash and checksum(arg.full) == full_hash
    qc = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts_independent": {
            "all_source_ids": len(ledger),
            "previous_formal_source_ids": len(previously_formal),
            "pending_source_ids": len(original_pending),
            "source_review_units": len(groups),
            "candidate_cross_url_title_links": len(triage["cross_article_title_review_proposals"]),
        },
        "stage_sha256": base_hash,
        "full_sha256": full_hash,
        "triage_sha256": checksum(arg.triage),
        "interpretation": "Coverage and article-key safety only; not an economic-event or fact audit.",
    }
    arg.out.write_text(json.dumps(qc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(qc, ensure_ascii=False, indent=2))
    if qc["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

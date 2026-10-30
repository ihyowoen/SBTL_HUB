#!/usr/bin/env python3
"""Create-only, non-decisional queue for all 103 review-pool >=60 metadata rows.

This preserves URL query parameters with event identifiers (idxno/no/list_no)
instead of collapsing distinct articles. Exact URL repetition is never an
automatic economic-event duplicate or Stage A reject verdict.
"""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

HERE = Path(__file__).resolve().parent
SOURCE_SHA256 = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"


def canonical_transport_url(url):
    p = urlsplit(url.strip())
    # DO NOT erase publisher identity-bearing query keys like idxno, no, list_no.
    fields = sorted((k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                    if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"})
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path, urlencode(fields), ""))


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--source-ledger", type=Path, required=True)
    a = arg.parse_args()
    assert hashlib.sha256(a.source_ledger.read_bytes()).hexdigest() == SOURCE_SHA256
    with a.source_ledger.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(set(r["candidate_id"] for r in rows)) == 1330
    high = [r for r in rows if r["stage_a_pool"] == "candidate_review_pool"
            and int(r["decision_news_value_score"] or 0) >= 60]
    assert len(high) == 103
    assert sum(r["stage_a_pool"] == "candidate_review_pool" for r in rows) == 636
    assert sum(r["stage_a_pool"] == "watchlist_context_pool" for r in rows) == 658
    watch26 = [r["candidate_id"] for r in rows if r["stage_a_pool"] == "watchlist_context_pool"
               and r["decision_news_value_score"] == "26"]
    assert len(watch26) == 654
    assert sum(r["stage_a_pool"] == "existing_reinforcement" for r in rows) == 28
    assert sum(r["stage_a_pool"] == "strict_passed_spec" for r in rows) == 8
    assert sum(not r["economic_event_cluster_id"] for r in rows) == 1285

    first = json.loads((HERE / "STAGE_A_NIO_NYSERDA_BOUNDED_0_1P_REVIEW_20261030.json").read_text(encoding="utf-8"))
    second = json.loads((HERE / "STAGE_A_THREE_MORE_64_POINT_CANDIDATES_BOUNDED_REVIEW_20261030.json").read_text(encoding="utf-8"))
    researched = {r["candidate_id"] for r in first["source_row_disposition_delta"]}
    researched |= {s for c in second["cases"] for s in c["source_ids"]}
    assert len(researched) == 8
    assert researched <= {r["candidate_id"] for r in high}

    by_url = defaultdict(list)
    for r in high:
        by_url[canonical_transport_url(r["primary_url"])].append(r["candidate_id"])
    repeats = [
        {"url_identity_key": url, "source_ids": ids,
         "disposition": "SAME_URL_OBSERVATION_ONLY_NO_AUTOMATIC_EVENT_MERGE"}
        for url, ids in sorted(by_url.items()) if len(ids) > 1
    ]
    assert len(repeats) == 5
    assert sum(len(g["source_ids"]) for g in repeats) == 10
    # These two are distinct publisher articles: their article identifiers are
    # query keys, and a simplistic split('?')[0] would falsely merge both pairs.
    by_id = {r["candidate_id"]: r for r in high}
    assert canonical_transport_url(by_id["SRC26-20260920_142928-0064"]["primary_url"]) != canonical_transport_url(by_id["SRC26-20260920_142928-0065"]["primary_url"])
    assert canonical_transport_url(by_id["SRC26-20260928_160143-0067"]["primary_url"]) != canonical_transport_url(by_id["SRC26-20260928_160143-0124"]["primary_url"])

    high = sorted(high, key=lambda r: (-int(r["decision_news_value_score"] or 0), int(r["source_row_index"])))
    queue = [
        {
            "candidate_id": r["candidate_id"],
            "original_source_row_index": int(r["source_row_index"]),
            "original_stage_a_pool": r["stage_a_pool"],
            "original_assessment_status": r["assessment_status"],
            "original_metadata_score": int(r["decision_news_value_score"]),
            "headline_raw": r["headline_raw"],
            "primary_url": r["primary_url"],
            "query_aware_identity_url": canonical_transport_url(r["primary_url"]),
            "source_observed_date": json.loads(r["date_role"]).get("observed_date") or None,
            "original_economic_cluster_blank": not bool(r["economic_event_cluster_id"]),
            "bounded_research_today": r["candidate_id"] in researched,
            "formal_0_1P_status": "UNADJUDICATED_1_0P_PENDING_FULL_MACHINE_GATE",
            "screening_instruction": "event identity+owner+stage+Full/Related+four judgments; never auto-promote/reject by metadata score"
        }
        for r in high
    ]
    assert len(queue) == 103 and sum(r["bounded_research_today"] for r in queue) == 8
    artifact = {
        "artifact_type": "STAGE_A_103_SOURCE_METADATA_REVIEW_INVENTORY_NOT_VERDICT",
        "date_kst": "2026-10-30",
        "input_sha256": SOURCE_SHA256,
        "source_universe_count": 1330,
        "original_review_count": 636,
        "original_watch_count": 658,
        "original_duplicate_reinforcement_count": 28,
        "original_strict_count": 8,
        "original_formal_unadjudicated_count": 1285,
        "high_metadata_cohort_threshold": 60,
        "threshold_is_search_order_only_not_news_value_cutoff": True,
        "high_metadata_source_count": 103,
        "score_histogram": {"64": 60, "63": 31, "60": 12},
        "eight_source_bounded_research_completed_current_date": sorted(researched),
        "remaining_high_metadata_source_ids_without_new_bounded_review": 95,
        "watch26_count_preserved_not_excluded": len(watch26),
        "watch26_source_set_sha256": hashlib.sha256("\n".join(watch26).encode()).hexdigest(),
        "warning": "Exact URL duplicates do not prove same economic event; URL keys `idxno`, `no`, `list_no` are event-identifying, and a changing board page may also host new legal actions. Each independent stage advancement requires full 0.1P and native Stage A checks.",
        "repeated_url_source_observation_groups": repeats,
        "known_false_pairs_from_naive_query_stripping": [
            ["SRC26-20260920_142928-0064", "SRC26-20260920_142928-0065"],
            ["SRC26-20260928_160143-0067", "SRC26-20260928_160143-0124"]
        ],
        "queue": queue,
        "native_stage_a_status": "NOT_EXECUTED_INCOMPLETE_1330_EVENT_ADJUDICATION",
        "no_source_id_loss": True
    }
    path = HERE / "STAGE_A_103_SOURCE_HIGH_METADATA_NON_DECISION_INVENTORY_20261030.json"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(artifact, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({k: artifact[k] for k in ["source_universe_count", "original_formal_unadjudicated_count", "high_metadata_source_count", "remaining_high_metadata_source_ids_without_new_bounded_review", "watch26_count_preserved_not_excluded", "score_histogram", "known_false_pairs_from_naive_query_stripping"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build 1,330-ID non-decisional exact-URL evidence graph preserving query IDs.

URL observation equality does not imply economic-event equality or entitlement
to merge/cull. This graph only exposes source-recapture and metadata conflicts.
"""

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from build_103_metadata_review_inventory_20261030 import canonical_transport_url

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-ledger", required=True, type=Path)
    args = p.parse_args()
    assert hashlib.sha256(args.source_ledger.read_bytes()).hexdigest() == SOURCE_SHA
    with args.source_ledger.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1330 and len({r["candidate_id"] for r in rows}) == 1330
    by_url = defaultdict(list)
    for r in rows:
        if r["primary_url"]:
            by_url[canonical_transport_url(r["primary_url"])].append(r)
    repeated = {url: source_rows for url, source_rows in by_url.items() if len(source_rows) > 1}
    assert len(by_url) == 1210
    assert len(repeated) == 112
    assert sum(len(v) for v in repeated.values()) == 226
    assert sum(len(v) - 1 for v in repeated.values()) == 114
    assert sum(len({r["stage_a_pool"] for r in v}) > 1 for v in repeated.values()) == 14
    assert sum(len({r["decision_news_value_score"] for r in v}) > 1 for v in repeated.values()) == 16
    assert sum(not r["primary_url"] for r in rows) == 6

    def group_id(url):
        return "SOURCE_URL_OBSERVATION_" + hashlib.sha256(url.encode()).hexdigest()[:16]

    observation_groups = [
        {
            "source_url_observation_group_id": group_id(url),
            "query_aware_url": url,
            "source_ids": [r["candidate_id"] for r in source_rows],
            "source_count": len(source_rows),
            "source_row_original_pools": [r["stage_a_pool"] for r in source_rows],
            "source_row_original_scores": [int(r["decision_news_value_score"] or 0) for r in source_rows],
            "mixed_original_pool": len({r["stage_a_pool"] for r in source_rows}) > 1,
            "score_disagreement": len({r["decision_news_value_score"] for r in source_rows}) > 1,
            "economic_event_equivalence": "UNVERIFIED_DO_NOT_MERGE",
            "url_revision_warning": "A reused publisher/government URL may reflect revised or later content; date-role and source-body check required before any merge."
        }
        for url, source_rows in sorted(repeated.items())
    ]
    by_url_id = {url: group_id(url) for url in repeated}
    source_map = [
        {
            "candidate_id": r["candidate_id"],
            "original_row_index": int(r["source_row_index"]),
            "original_pool": r["stage_a_pool"],
            "original_metadata_score": int(r["decision_news_value_score"] or 0),
            "original_primary_url": r["primary_url"] or None,
            "url_observation_group_id": by_url_id.get(canonical_transport_url(r["primary_url"])) if r["primary_url"] else None,
            "repeat_group_observation_count": len(by_url[canonical_transport_url(r["primary_url"])]) if r["primary_url"] else 0,
            "original_event_cluster_field": r["economic_event_cluster_id"] or None,
            "economic_event_identity_not_inferred_from_url": True
        }
        for r in rows
    ]
    assert len(source_map) == len({r["candidate_id"] for r in source_map}) == 1330
    assert sum(row["repeat_group_observation_count"] >= 2 for row in source_map) == 226
    asset = {
        "artifact_type": "STAGE_A_ALL_1330_QUERY_AWARE_SOURCE_URL_OBSERVATION_GRAPH_NOT_EVENT_CLUSTERS",
        "date_kst": "2026-10-30",
        "input_source_sha256": SOURCE_SHA,
        "original_source_ids": 1330,
        "nonempty_url_source_rows": 1324,
        "distinct_query_aware_source_urls": len(by_url),
        "singleton_source_url_observations": 1098,
        "repeated_url_groups": len(repeated),
        "source_ids_in_repeated_url_groups": 226,
        "extra_recapture_observations_beyond_one_per_url": 114,
        "mixed_pool_repeated_url_groups": 14,
        "mixed_score_repeated_url_groups": 16,
        "missing_primary_url_in_csv_count": 6,
        "missing_primary_url_source_ids": [r["candidate_id"] for r in rows if not r["primary_url"]],
        "missing_csv_url_caveat": "Some IDs are among prior strict 8 and have supporting URLs elsewhere in Stage artifacts. Empty 1,330-ledger primary_url does not establish no supporting evidence exists; follow exact spec lineage.",
        "URL_canonicalizer_cautions": [
            "Preserve event-identifying query parameters: idxno, no, list_no, article_id, etc.; drop only tracking keys (utm_*, fbclid, gclid).",
            "Do not collapse 14 mixed-pool groups to one pool automatically: same source URL can be WATCH at 26 and review at 44/50/52/57/58/64.",
            "Do not treat URL observation equality as an economic-event cluster. Revisions and changed legal/operating stages require body evidence."
        ],
        "mixed_pool_group_ids": [g["source_url_observation_group_id"] for g in observation_groups if g["mixed_original_pool"]],
        "all_repeat_url_source_groups": observation_groups,
        "all_1330_source_url_observation_assignments": source_map,
        "formal_stage_a_state": "HOLD_1285_ORIGINAL_0_1P_UNADJUDICATED",
        "native_stage_a_validator_status": "NOT_EXECUTED_SOURCE_URL_EQUIVALENCE_IS_NOT_ARTIFACT_PASS",
        "not_a_new_review_round": True,
        "no_source_id_loss": True
    }
    output = HERE / "STAGE_A_1330_SOURCE_URL_OBSERVATION_EQUIVALENCE_20261030.json"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(asset, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({k: asset[k] for k in ["original_source_ids", "nonempty_url_source_rows", "distinct_query_aware_source_urls", "singleton_source_url_observations", "repeated_url_groups", "source_ids_in_repeated_url_groups", "extra_recapture_observations_beyond_one_per_url", "mixed_pool_repeated_url_groups", "mixed_score_repeated_url_groups", "missing_primary_url_in_csv_count"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

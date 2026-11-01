#!/usr/bin/env python3
"""Independent delta QC for the single formal 0.1P Stage A disposition.

Read-only comparison to the locked 70-attachment artifact. This script checks
identity, unchanged non-target judgments, bounded top-level changes, and that
the formal source is resolved as reinforcement without manufacturing a card.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SOURCE_ID = "SRC26-20260920_142928-0145"
BASE_SHA = "e42097f6f17495ff24550b2c72dba9d5874e7a835090c95cae4881750116d109"
FULL_ID = "2026-09-17_CN_01"
POOLS = (
    "strict_passed_spec", "candidate_review_pool", "watchlist_context_pool",
    "existing_reinforcement", "reject_or_support_only_pool",
)
ALLOWED_TOP_LEVEL_DIFFERENCES = {
    "candidate_review_pool", "existing_reinforcement", "decision_ledger",
    "review_pool_resolution_ledger", "promotion_reassessment_ledger",
    "summary", "review_pool_partition_summary",
    "pre_native_0_1P_attachment_manifest_20261101",
    "formal_0_1P_resolution_20261101",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--formal", type=Path, required=True)
    p.add_argument("--full", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    checks = {}

    def check(name: str, condition: bool) -> None:
        checks[name] = "PASS" if condition else "FAIL"

    before, after, full = read(args.base), read(args.formal), read(args.full)
    check("original_sha256_fixed", sha256(args.base) == BASE_SHA)
    changed_keys = {
        key for key in set(before) | set(after) if before.get(key) != after.get(key)
    }
    check("changed_sections_allowlisted", changed_keys <= ALLOWED_TOP_LEVEL_DIFFERENCES)
    check("formal_section_new_only", "formal_0_1P_resolution_20261101" not in before)
    check("locked_full_count", len(full["cards"]) == 1676)
    check("locked_full_has_exact_match", any(x["id"] == FULL_ID for x in full["cards"]))
    check("strict_8_identical", len(after["strict_passed_spec"]) == 8 and before["strict_passed_spec"] == after["strict_passed_spec"])
    check("watch_658_identical", len(after["watchlist_context_pool"]) == 658 and before["watchlist_context_pool"] == after["watchlist_context_pool"])
    check("rejections_identical", before["reject_or_support_only_pool"] == after["reject_or_support_only_pool"])
    check("original_source_count_1330", len(after["decision_ledger"]) == 1330)
    check("original_source_ids_identical", [x["candidate_id"] for x in before["decision_ledger"]] == [x["candidate_id"] for x in after["decision_ledger"]])
    original = {x["candidate_id"]: x for x in before["decision_ledger"]}
    current = {x["candidate_id"]: x for x in after["decision_ledger"]}
    other_ids = set(original) - {SOURCE_ID}
    check("1329_other_decisions_byte_semantically_identical", all(original[sid] == current[sid] for sid in other_ids) and len(other_ids) == 1329)
    check("all_1330_source_urls_identical", all(original[sid]["primary_url"] == current[sid]["primary_url"] for sid in original))
    check("all_1330_headlines_identical", all(original[sid]["headline_raw"] == current[sid]["headline_raw"] for sid in original))
    check("all_1330_row_indexes_identical", all(original[sid]["source_row_index"] == current[sid]["source_row_index"] for sid in original))
    for pool in POOLS:
        before_items = {x["candidate_id"]: x for x in before[pool]}
        after_items = {x["candidate_id"]: x for x in after[pool]}
        check(f"other_pool_members_unchanged__{pool}", all(before_items[sid] == after_items.get(sid) for sid in before_items if sid != SOURCE_ID))
    pool_union = [x["candidate_id"] for pool in POOLS for x in after[pool]]
    check("pool_partition_1330_unique", len(pool_union) == len(set(pool_union)) == 1330)
    check("0145_moved_only_to_reinforcement", SOURCE_ID not in {x["candidate_id"] for x in after["candidate_review_pool"]} and sum(x["candidate_id"] == SOURCE_ID for x in after["existing_reinforcement"]) == 1)
    check("formal_duplicate_target_locked_full", current[SOURCE_ID]["related_prepass"]["matched_baseline_candidate_ids"] == [FULL_ID])
    check("formal_cardability_fail", current[SOURCE_ID]["execution_credibility_gate"]["status"] == "PASS" and current[SOURCE_ID]["independent_cardability_gate"]["status"] == "FAIL")
    check("formal_result_no_new_card", current[SOURCE_ID]["stage_b_authorized"] is False and after["formal_0_1P_resolution_20261101"]["new_strict_passes"] == 0)
    check("live_resolution_ledger_exact_1293", len(after["review_pool_resolution_ledger"]) == 1293 and not any(x["story_id"] == SOURCE_ID for x in after["review_pool_resolution_ledger"]))
    check("prior_1293_resolutions_identical", [x for x in before["review_pool_resolution_ledger"] if x["story_id"] != SOURCE_ID] == after["review_pool_resolution_ledger"])
    check("one_added_reassessment", len(after["promotion_reassessment_ledger"]) == 46 and after["promotion_reassessment_ledger"][:-1] == before["promotion_reassessment_ledger"])
    s = after["summary"]
    check("formal_counts_46_1284", s["processed_priority_source_observations"] == 46 and s["unprocessed_editorial_observations"] == 1284)
    check("pool_counts_8_635_658_29", [len(after[x]) for x in ("strict_passed_spec", "candidate_review_pool", "watchlist_context_pool", "existing_reinforcement")] == [8, 635, 658, 29])
    check("original_pre_native_evidence_preserved", all(current[sid].get("pre_native_0_1P_judgment_attachment_20261101") == original[sid].get("pre_native_0_1P_judgment_attachment_20261101") for sid in original))

    result = {
        "artifact_type": "STAGE_A_FORMAL_0145_INDEPENDENT_DELTA_QC",
        "overall": "PASS" if all(v == "PASS" for v in checks.values()) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
        "original_stage_a_sha256": sha256(args.base),
        "formal_stage_a_sha256": sha256(args.formal),
        "locked_full_sha256": sha256(args.full),
        "scope": "Exactly one formal non-promotion source decision; no strict/new-card authorization.",
        "formal_completed": 46,
        "formal_pending": 1284,
        "global_stage_a_release_status": "HOLD",
    }
    with args.out.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({"overall": result["overall"], "check_count": len(checks), "failed_checks": [k for k, v in checks.items() if v == "FAIL"], "formal_stage_a_sha256": result["formal_stage_a_sha256"]}, indent=2))
    if result["overall"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

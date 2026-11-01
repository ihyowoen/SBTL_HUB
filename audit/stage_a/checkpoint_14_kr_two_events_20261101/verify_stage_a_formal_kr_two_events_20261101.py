#!/usr/bin/env python3
"""Independent, fail-closed delta and native QC for Stage A Korean event batch.

Compares immutable pre-batch 1,330 Source IDs against new 1,330 Source IDs,
checks all thirty exact decisions, and runs the two repository-native contracts.
This verifies accounting and schema only, not Stage B fact acceptance.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

RES_ROWS = {222, 230, 232, 234, 250, 256, 270, 280, 281, 283, 284, 429,
            570, 604, 605, 606, 608, 609, 612, 618, 622, 631, 1018, 1271}
ESS_ROWS = {235, 260, 271, 535, 538, 1279}
REP_ROWS = {222, 235}
HELD_ROWS = {48, 228, 244, 614, 916}
EXTRA_RECOVERED = {232, 280, 605, 631}
REVIEW_POOLS = ("strict_passed_spec", "candidate_review_pool", "watchlist_context_pool",
                "reject_or_support_only_pool")
IDENTITY_KEYS = ("story_id", "candidate_id", "source_row_index", "primary_url", "headline_raw")
ALLOWED_CHANGED_TOP_KEYS = {
    "strict_passed_spec", "candidate_review_pool", "reject_or_support_only_pool",
    "decision_ledger", "review_pool_resolution_ledger", "promotion_reassessment_ledger",
    "summary", "review_pool_partition_summary", "pre_native_0_1P_attachment_manifest_20261101",
    "next_call_recommendation", "recommended_for", "formal_0_1P_two_korean_events_20261101",
}
BASE_HASH = "1d2c8ccbd01b40aef7de512969281043a59cdb866d2a6dfbdd52bf997edf95c1"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as src:
        for blob in iter(lambda: src.read(1048576), b""):
            h.update(blob)
    return h.hexdigest()


def read(path: Path):
    with path.open(encoding="utf-8") as src:
        return json.load(src)


def checked(label: str, condition: bool):
    if not condition:
        raise AssertionError(label)


def main() -> None:
    parser = argparse.ArgumentParser()
    for arg in ("base", "artifact", "receipt", "native_root", "output"):
        parser.add_argument("--" + arg.replace("_", "-"), type=Path, required=True)
    args = parser.parse_args()
    old, new, receipt = read(args.base), read(args.artifact), read(args.receipt)
    checked("immutable source hash", sha(args.base) == BASE_HASH)
    checked("receipt matches output SHA", receipt["output_sha256"] == sha(args.artifact))
    old_ledger, new_ledger = old["decision_ledger"], new["decision_ledger"]
    checked("ledger still 1,330", len(old_ledger) == len(new_ledger) == 1330)
    checked("original order preserved", [r["story_id"] for r in old_ledger] ==
            [r["story_id"] for r in new_ledger])
    before_by_row = {r["source_row_index"]:r for r in old_ledger}
    after_by_row = {r["source_row_index"]:r for r in new_ledger}
    checked("1,330 distinct source row numbers", len(before_by_row) == len(after_by_row) == 1330)
    checked("row universe identical", before_by_row.keys() == after_by_row.keys())
    for index in before_by_row:
        before, after = before_by_row[index], after_by_row[index]
        for k in IDENTITY_KEYS:
            checked(f"original source identity {index}:{k}", before.get(k) == after.get(k))
        if index not in (RES_ROWS | ESS_ROWS):
            checked(f"unrelated ledger entry unchanged {index}", before == after)
    changed_indices = {index for index in before_by_row if before_by_row[index] != after_by_row[index]}
    checked("exact thirty decisions", changed_indices == (RES_ROWS | ESS_ROWS))
    checked("five complex candidate holds untouched", all(
        before_by_row[r] == after_by_row[r] for r in HELD_ROWS))
    checked("four extra Source IDs accounted", EXTRA_RECOVERED.issubset(changed_indices))

    rep_ids = {after_by_row[r]["story_id"] for r in REP_ROWS}
    support_ids = {after_by_row[r]["story_id"] for r in changed_indices - REP_ROWS}
    resource_rep = after_by_row[222]["story_id"]
    ess_rep = after_by_row[235]["story_id"]
    checked("2 strict rep IDs", len(rep_ids) == 2)
    checked("28 support IDs", len(support_ids) == 28)

    checked("2 new spec pool records", len(new["strict_passed_spec"]) == 10 and
            new["strict_passed_spec"][:8] == old["strict_passed_spec"])
    strict_by_id = {r["story_id"]:r for r in new["strict_passed_spec"]}
    checked("strict representatives exact", set(strict_by_id) -
            {r["story_id"] for r in old["strict_passed_spec"]} == rep_ids)
    for idx, case_id, expected_n in (
        (222, "KR_RESOURCE_SECURITY_PLAN_20260923", 24),
        (235, "KR_ESS_CENTRAL_TENDER_1180MW_20260922", 6),
    ):
        sid = after_by_row[idx]["story_id"]
        strict = strict_by_id[sid]
        checked(f"strict event case {idx}", strict["economic_event_cluster_id"] == case_id)
        checked(f"strict source cluster preserved {idx}", len(strict["formal_0_1P_batch_promoted_20261101"]["source_ids"]) == expected_n)
        checked(f"strict not Stage B accepted {idx}", strict["stage_b_authorized"] is False and
                strict["accepted_facts_approved"] is False and strict["canonical_card_write_allowed"] is False)
        checked(f"strict ledger mirror identical {idx}", strict["spec_id"] == after_by_row[idx]["spec_id"])
    checked("asset/legal independent source scores", sum(new["strict_passed_spec"][-2]["decision_value_breakdown"].values())
            == new["strict_passed_spec"][-2]["decision_news_value_score"] and
            sum(new["strict_passed_spec"][-1]["decision_value_breakdown"].values())
            == new["strict_passed_spec"][-1]["decision_news_value_score"])

    checked("support-only first class pool", len(new["reject_or_support_only_pool"]) == 28)
    for row in new["reject_or_support_only_pool"]:
        sid = row["story_id"]
        idx = row["source_row_index"]
        expected_rep = resource_rep if idx in RES_ROWS else ess_rep
        checked(f"support source is exact cluster {idx}", sid in support_ids)
        checked(f"support has original primary URL {idx}", row["primary_url"] == before_by_row[idx]["primary_url"])
        checked(f"support no card {idx}", row["canonical_card_write_allowed"] is False and
                row["whether_support_source_only"] is True)
        checked(f"support related rep {idx}", row["formal_0_1P_support_only_20261101"]["representative_source_id"] == expected_rep)
        checked(f"support ledger mirrors disposition {idx}", after_by_row[idx]["editorial_bucket"] ==
                "reject_or_support_only_pool" and after_by_row[idx]["stage_a_pool"] == "reject_or_support_only_pool")

    before_review = {r["story_id"]:r for r in old["review_pool_resolution_ledger"]}
    after_review = {r["story_id"]:r for r in new["review_pool_resolution_ledger"]}
    checked("two reps leave review ledger", set(before_review) - set(after_review) == rep_ids)
    checked("review count 1291", len(new["review_pool_resolution_ledger"]) == 1291)
    for sid, row in after_review.items():
        if sid not in support_ids:
            checked(f"unchanged review ledger {sid}", before_review[sid] == row)
        else:
            checked(f"support reviewed resolution {sid}", row["current_disposition"] ==
                    "reject_or_support_only_pool")

    old_promo = old["promotion_reassessment_ledger"]
    new_promo = new["promotion_reassessment_ledger"]
    checked("original 46 promotion ledger preserved", len(old_promo) == 46 and new_promo[:46] == old_promo)
    checked("30 exact promotion reassessments", len(new_promo) == 76 and
            {r["candidate_id"] for r in new_promo[46:]} == rep_ids | support_ids)
    checked("existing source candidates and watchlist unchanged", new["watchlist_context_pool"] ==
            old["watchlist_context_pool"] and new["existing_reinforcement"] == old["existing_reinforcement"])
    checked("candidate review count 605", len(new["candidate_review_pool"]) == 605)
    source_pools = (*REVIEW_POOLS, "existing_reinforcement")
    universe = [r["story_id"] for pool in source_pools for r in new[pool]]
    checked("source pool union exactly 1330", len(universe) == len(set(universe)) == 1330 and
            set(universe) == {r["story_id"] for r in new_ledger})
    checked("all pre-native 70 attachment payloads preserved", all(
        old[k] == new[k] for k in old if k.startswith("pre_native_")
        and k != "pre_native_0_1P_attachment_manifest_20261101"))
    old_attach = old["pre_native_0_1P_attachment_manifest_20261101"]
    new_attach = new["pre_native_0_1P_attachment_manifest_20261101"]
    checked("70 source input hashes preserved", old_attach["source_input_sha256"] ==
            new_attach["source_input_sha256"] and new_attach["pre_native_source_count"] == 70)
    checked("31 formalized since attachment", new_attach["new_formal_decisions"] == 31 and
            new_attach["new_strict_promotions"] == 2 and new_attach["remaining_formal_source_count"] == 1254)

    meta = new["formal_0_1P_two_korean_events_20261101"]
    checked("explicit 2 events 30 sources 5 holds", meta["independent_event_families"] == 2 and
            meta["source_ids_formalized_this_batch"] == 30 and meta["new_support_only_sources"] == 28 and
            {x["source_row_index"] for x in meta["distinct_mixed_or_stage_split_hold"]} == HELD_ROWS)
    checked("formalized completed 76 remaining 1254", meta["formal_individual_completed_total"] == 76
            and meta["formal_individual_pending"] == 1254)
    checked("HOLD, not Stage B", meta["global_editorial_stage_a_status"].startswith("HOLD") and
            meta["stage_b_executed"] is False and meta["canonical_main_full_related_mutations"] == 0)
    checked("two distinct economic acts", len({strict_by_id[sid]["economic_event_cluster_id"] for sid in rep_ids}) == 2)
    checked("only approved top-level keys changed", {key for key in set(old) | set(new)
            if old.get(key) != new.get(key)}.issubset(ALLOWED_CHANGED_TOP_KEYS))
    counts = {pool:len(new.get(pool, [])) for pool in source_pools}
    checked("summary and pool counts match", new["summary"]["pool_counts"]["strict_passed_spec"] == 10 and
            all(new["summary"]["pool_counts"][key] == value for key,value in counts.items()) and
            new["summary"]["processed_priority_source_observations"] == 76 and
            new["summary"]["unprocessed_editorial_observations"] == 1254)
    checked("30 receipt rows with four recovery IDs", len(receipt["event_records"]["formal_source_decisions"]) == 30 and
            set(receipt["newly_recovered_source_rows"]) == EXTRA_RECOVERED)

    checks = {}
    for label, script, arguments in (
        ("stage_artifact_contract_check", "stage_artifact_contract_check.py", ["A", args.artifact.name]),
        ("stage_lineage_contract_check", "stage_lineage_contract_check.py", ["stage_a", args.artifact.name]),
    ):
        run = subprocess.run([sys.executable, f"validation_scripts/{script}", *arguments],
                             cwd=args.native_root, text=True, capture_output=True, check=False)
        checks[label] = {"return_code":run.returncode, "output":run.stdout.strip(),
                         "error":run.stderr.strip()}
        checked(f"native {label} PASS", run.returncode == 0 and "PASS" in run.stdout)

    output = {
        "result":"PASS_INDEPENDENT_DELTA_AND_BOTH_NATIVE_CONTRACTS",
        "audit_scope":"Structural/lineage no-loss QC, not Stage B fact-safe certification",
        "base_sha256":sha(args.base), "artifact_sha256":sha(args.artifact),
        "preserved_original_source_ids":1330,
        "changed_source_count":len(changed_indices),
        "changed_source_row_indices":sorted(changed_indices),
        "new_event_strict_source_ids":sorted(rep_ids),
        "support_only_source_ids":sorted(support_ids),
        "unchanged_hold_source_rows":sorted(HELD_ROWS),
        "recovered_missing_review_source_rows":sorted(EXTRA_RECOVERED),
        "counts":{**counts,"review_resolution_ledger":len(new["review_pool_resolution_ledger"]),
                  "formal_completed":76,"formal_pending":1254,"universe":1330},
        "independent_native_checks":checks,
        "global_stage_a_status":"HOLD",
        "stage_b_executed":False,
        "main_full_related_production_mutated":False,
    }
    with args.output.open("w",encoding="utf-8",newline="\n") as dest:
        json.dump(output,dest,ensure_ascii=False,indent=2)
        dest.write("\n")
    print(json.dumps({"result":output["result"],"artifact_sha256":output["artifact_sha256"],
                      "counts":output["counts"]},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()

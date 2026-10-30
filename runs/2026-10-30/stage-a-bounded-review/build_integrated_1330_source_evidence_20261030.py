#!/usr/bin/env python3
"""Create-only Stage A source-evidence overlay; never assign native promotions.

One row = an immutable original Source ID. One source can report multiple
economic acts, and a multi-source topic group is *not* a per-ID event verdict.
This JSON is an analysis intermediary for a separate Artifact Tool workbook.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORK = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "STAGE_A_REASSESSMENT_LEDGER_1330_20261027.source.csv"
PREVIOUS = ROOT / "runs/2026-10-29/stage-a-identity"
SOURCE_SHA = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"
OUTPUT = WORK / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_20261030.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    assert digest(SOURCE) == SOURCE_SHA, "source CSV was modified"
    with SOURCE.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1330
    ids = [r["candidate_id"] for r in rows]
    assert len(ids) == len(set(ids))
    assert [int(r["source_row_index"]) for r in rows] == list(range(1330))
    pool = collections.Counter(r["stage_a_pool"] for r in rows)
    assert pool == {"candidate_review_pool": 636, "watchlist_context_pool": 658,
                    "existing_reinforcement": 28, "strict_passed_spec": 8}
    previous_45 = {r["candidate_id"] for r in rows if r["promotion_reassessment_status"].strip()}
    assert len(previous_45) == 45
    assert {r["candidate_id"] for r in rows if r["economic_event_cluster_id"].strip()} == previous_45

    evidence: dict[str, list[dict]] = collections.defaultdict(list)
    source_set = set(ids)

    def attach(sid: str, label: str, artifact: str, tier: str,
               case_ids: list[str] | None = None, event_units: list[str] | None = None,
               certainty: str = "SOURCE_TO_CASE_PROVISIONAL") -> None:
        assert sid in source_set, f"missing original Source ID {sid} from {artifact}"
        entry = {"evidence": label, "artifact": artifact, "tier": tier,
                 "case_ids": sorted(set(case_ids or [])),
                 "event_units": sorted(set(event_units or [])),
                 "mapping_certainty": certainty}
        if entry not in evidence[sid]:
            evidence[sid].append(entry)

    old_file = PREVIOUS / "STAGE_A_25_SOURCE_TO_CASE_EDGES_20261029.csv"
    with old_file.open(encoding="utf-8-sig", newline="") as fh:
        old_edges = list(csv.DictReader(fh))
    assert len(old_edges) == 25 and len({r["original_source_id"] for r in old_edges}) == 25
    for e in old_edges:
        attach(e["original_source_id"], "20261029_EXISTING_15_PACKAGE_IDENTITY_EVIDENCE",
               old_file.name, "BOUNDED_CASE_IDENTITY",
               [e["provisional_case_package_id"]],
               [v for v in e["underlying_event_unit_ids_from_package_owner_not_article_claimed"].split("|") if v],
               "20261029_PACKAGE_OBSERVATION_AND_UNITS_NOT_FINAL_ARTICLE")

    initial = WORK / "STAGE_A_NIO_NYSERDA_BOUNDED_0_1P_REVIEW_20261030.json"
    for case in load_json(initial)["cases"]:
        for observation in case["original_source_rows"]:
            attach(observation["candidate_id"], "NIO_NYSERDA_FIRST_PARTY_BOUNDED",
                   initial.name, "BOUNDED_CASE_PRIMARY", [case["case_id"]])

    earlier = WORK / "STAGE_A_THREE_MORE_64_POINT_CANDIDATES_BOUNDED_REVIEW_20261030.json"
    for case in load_json(earlier)["cases"]:
        for sid in case["source_ids"]:
            attach(sid, "EVE_ECOPRO_CATL_THREE_CASES", earlier.name,
                   "BOUNDED_CASE_PRIMARY", [case["case_id"]])

    five = WORK / "STAGE_A_FIVE_MIXED_POOL_SOURCE_GROUPS_CASE_ADJUDICATION_20261030.json"
    for case in load_json(five)["cases"]:
        for sid in case["source_ids"]:
            attach(sid, "FIVE_MIXED_POOL_IDENTICAL_URL_ECONOMIC_ACTS", five.name,
                   "BOUNDED_CASE_PRIMARY", [case["case_id"]])

    nine = WORK / "STAGE_A_NINE_REMAINING_MIXED_POOL_GROUPS_EVIDENCE_TRIAGE_20261030.json"
    for rec in load_json(nine)["triage_records"]:
        for sid in rec["original_source_ids"]:
            attach(sid, "NINE_MIXED_POOL_GROUPS_FIRST_PASS", nine.name,
                   "SOURCE_OBSERVATION_TRIAGE", [], [], "GROUP_ONLY_NOT_EVENT_IDENTITY")

    second = WORK / "STAGE_A_NEXT_HIGH64_PRIMARY_CASE_REVIEW_20261030.json"
    for rec in load_json(second)["source_case_records"]:
        for sid in rec["original_source_ids"]:
            attach(sid, "HIGH64_PRIMARY_SOURCE_CASE_RECORD", second.name,
                   "BOUNDED_CASE_PRIMARY", [rec["case_id"]])

    multi = WORK / "STAGE_A_HIGH64_MULTI_SOURCE_EVENT_IDENTITY_ADDENDUM_20261030.json"
    for group in load_json(multi)["evidence_groups"]:
        for sid in group["source_ids"]:
            attach(sid, "HIGH64_MULTISOURCE_SUBJECT_GROUP", multi.name,
                   "SUBJECT_AND_EVENT_MULTIPLICITY_BOUNDED", group["case_ids"], [],
                   "GROUP_CASES_NOT_ALLOCATION_TO_EACH_SOURCE_ID")

    fresh = WORK / "STAGE_A_FIVE_PRIMARY_CASES_EVENT_CUSTODY_20261030.json"
    fresh_data = load_json(fresh)
    assert fresh_data["candidate_case_count"] == len(fresh_data["cases"]) == 5
    for case in fresh_data["cases"]:
        for sid in case["source_ids"]:
            attach(sid, "20261030_FRESH_PRIMARY_BODY_READBACK", fresh.name,
                   "BOUNDED_CASE_PRIMARY", [case["case_id"]],
                   case["underlying_economic_units"],
                   "CASE_TO_SOURCE_ITEM_BOUNDED_NOT_NATIVE_CARD_JUDGMENT")

    url_file = WORK / "STAGE_A_1330_SOURCE_URL_OBSERVATION_EQUIVALENCE_20261030.json"
    source_observations = load_json(url_file)["all_1330_source_url_observation_assignments"]
    assert len(source_observations) == 1330
    group_by_id = {x["candidate_id"]: x for x in source_observations}
    assert set(group_by_id) == source_set

    high_file = WORK / "STAGE_A_103_SOURCE_HIGH_METADATA_NON_DECISION_INVENTORY_20261030.json"
    high_items = load_json(high_file)["queue"]
    high_ids = {x["candidate_id"] for x in high_items}
    assert len(high_items) == len(high_ids) == 103
    assert high_ids <= source_set

    overlay: list[dict] = []
    tiers_counts = collections.Counter()
    for r in rows:
        sid = r["candidate_id"]
        es = evidence.get(sid, [])
        tids = {e["tier"] for e in es}
        native_state = ("PREVIOUS_0_1P_INDIVIDUAL_REVIEW_PRESERVED" if sid in previous_45
                        else "NATIVE_INDIVIDUAL_0_1P_PENDING")
        review_state = ("BOUNDED_CASE_SOURCE_EVIDENCE" if "BOUNDED_CASE_PRIMARY" in tids
                        else "EXISTING_CASE_PACKAGE_EVIDENCE" if "BOUNDED_CASE_IDENTITY" in tids
                        else "SUBJECT_CASE_DISAGGREGATION_REVIEWED" if "SUBJECT_AND_EVENT_MULTIPLICITY_BOUNDED" in tids
                        else "PRELIMINARY_TRIAGE_ONLY" if "SOURCE_OBSERVATION_TRIAGE" in tids
                        else "NO_ADDITIONAL_EVIDENCE_ON_THIS_ID")
        tiers_counts[review_state] += 1
        exact_case_ids = sorted({x for e in es if e["mapping_certainty"] !=
                                 "GROUP_CASES_NOT_ALLOCATION_TO_EACH_SOURCE_ID"
                                 for x in e["case_ids"]})
        subject_candidate_ids = sorted({x for e in es if e["mapping_certainty"] ==
                                        "GROUP_CASES_NOT_ALLOCATION_TO_EACH_SOURCE_ID"
                                        for x in e["case_ids"]})
        original_url = group_by_id[sid]
        overlay.append({
            "source_row_index": int(r["source_row_index"]),
            "candidate_id": sid,
            "headline_raw": r["headline_raw"],
            "primary_url_original": r["primary_url"],
            "original_stage_a_pool": r["stage_a_pool"],
            "original_assessment_status": r["assessment_status"],
            "metadata_score_original_not_selection_decision": int(r["decision_news_value_score"]),
            "original_economic_event_cluster_id": r["economic_event_cluster_id"],
            "original_individual_0_1P_result": r["promotion_reassessment_status"],
            "native_0_1P_state": native_state,
            "additional_evidence_scope": review_state,
            "source_url_observation_group_id_NOT_EVENT": original_url["url_observation_group_id"] or "",
            "source_url_observation_occurrences": original_url["repeat_group_observation_count"],
            "provisional_case_package_ids_NOT_FORMAL_CLUSTER": exact_case_ids,
            "group_subject_case_ids_NOT_ASSIGNED_PER_SOURCE": subject_candidate_ids,
            "evidence_artifacts": sorted({e["artifact"] for e in es}),
            "evidence_reference_details": es,
            "new_native_strict_pass": False,
            "next_gate": "PRESERVE_PREVIOUS_0_1P" if sid in previous_45 else
                         "NATIVE_SOURCE_ID_EVENT_IDENTITY_AND_FOUR_JUDGMENTS_PENDING",
        })
    assert len(overlay) == 1330
    assert [x["candidate_id"] for x in overlay] == ids
    assert all(not x["new_native_strict_pass"] for x in overlay)

    old_id_set = {e["original_source_id"] for e in old_edges}
    new_id_set = {x for x, items in evidence.items() if any(
        e["artifact"] != old_file.name for e in items)}
    fresh_id_set = {sid for c in fresh_data["cases"] for sid in c["source_ids"]}
    source_count = len(evidence)
    assert len(new_id_set - fresh_id_set) == 65, "prior Oct30 65 evidence universe has drifted"
    assert len(fresh_id_set) == 6
    assert not (fresh_id_set & (new_id_set - fresh_id_set)), "not a new source set"

    high_with_evidence = len(high_ids & set(evidence))
    original_status_count = collections.Counter(x["native_0_1P_state"] for x in overlay)
    assert original_status_count["NATIVE_INDIVIDUAL_0_1P_PENDING"] == 1285
    results = {
        "artifact_type": "STAGE_A_INTEGRATED_SOURCE_EVIDENCE_OVERLAY_1_ROW_PER_IMMUTABLE_SOURCE_ID",
        "as_of_kst": "2026-10-30",
        "original_csv_sha256": SOURCE_SHA,
        "original_1330_count": len(rows),
        "original_source_id_count_unique": len(source_set),
        "original_pool_counts": dict(sorted(pool.items())),
        "original_formal_individually_reviewed_0_1P": len(previous_45),
        "original_formal_pending_0_1P_unchanged": 1285,
        "prior_oct29_case_evidence_original_ids": len(old_id_set),
        "oct30_existing_bounded_and_triaged_ids": 65,
        "oct30_new_primary_source_ids": len(fresh_id_set),
        "old_prior_case_overlap_with_oct30": len(old_id_set & new_id_set),
        "unique_source_ids_with_any_bounded_or_triage_evidence": source_count,
        "review_evidence_scope_counts": dict(sorted(tiers_counts.items())),
        "high_metadata_60_plus_pending_source_count": len(high_ids),
        "high_metadata_60_plus_with_some_case_or_triage_evidence": high_with_evidence,
        "high_metadata_60_plus_without_any_linked_additional_evidence": len(high_ids) - high_with_evidence,
        "all_other_source_ids_unreviewed_status_remains": True,
        "url_observation_not_economic_identity": True,
        "group_subject_cases_not_automatically_allocated_to_each_source": True,
        "not_native_stage_a_contract_pass": True,
        "not_native_stage_a_lineage_pass": True,
        "new_promotions": 0,
        "source_evidence_artifact_file_count": len({e["artifact"] for x in evidence.values() for e in x}),
        "source_rows": overlay,
    }
    with OUTPUT.open("x", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(json.dumps({key: val for key, val in results.items() if key != "source_rows"},
                     ensure_ascii=False, indent=2))
    print("OUTPUT_SHA256=" + digest(OUTPUT))


if __name__ == "__main__":
    main()

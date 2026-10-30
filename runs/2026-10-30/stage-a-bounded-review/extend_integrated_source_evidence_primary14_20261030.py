#!/usr/bin/env python3
"""Create-only 14-ID primary-evidence addendum for immutable Stage A 1,330 overlay.

This is a source-to-provisional-case link, not formal Stage A 0.1P adjudication.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_20261030.json"
PACK = HERE / "STAGE_A_ADDITIONAL_14_HIGH_SOURCE_PRIMARY_EVENT_REVIEW_20261030.json"
OUTPUT = HERE / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V2_20261030.json"
PARENT_SHA = "3993f348b1ab872a34a5f41b10451e65b143e61c647be7e649f37f1a9f7c2eba"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"create-only: {OUTPUT}")
    assert file_hash(PARENT) == PARENT_SHA, "wrong parent overlay version"
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    assert parent["original_1330_count"] == 1330
    assert parent["unique_source_ids_with_any_bounded_or_triage_evidence"] == 83
    assert pack["case_count"] == 13 and pack["original_high_metadata_source_id_count"] == 14
    old_rows = parent["source_rows"]
    assert len(old_rows) == 1330 and len({r["candidate_id"] for r in old_rows}) == 1330

    by_source: dict[str, list[dict]] = {}
    for case in pack["cases"]:
        for source_id in case["source_ids"]:
            by_source.setdefault(source_id, []).append(case)
    assert set(by_source) == set(pack["source_ids"])
    assert len(by_source) == 14 and all(len(v) == 1 for v in by_source.values())
    assert set(by_source).issubset({r["candidate_id"] for r in old_rows})

    out = copy.deepcopy(parent)
    out["artifact_type"] = "STAGE_A_INTEGRATED_SOURCE_EVIDENCE_OVERLAY_V2_CREATE_ONLY_PARENT_VERIFIED"
    out["parent_overlay_sha256"] = PARENT_SHA
    out["additive_primary14_pack_sha256"] = file_hash(PACK)
    out["new_primary_source_ids_after_previous_checkpoint"] = 14
    out["oct30_new_primary_source_ids"] = 20
    out["unique_source_ids_with_any_bounded_or_triage_evidence"] = 97
    out["high_metadata_60_plus_with_some_case_or_triage_evidence"] = 63
    out["high_metadata_60_plus_without_any_linked_additional_evidence"] = 40
    out["source_evidence_artifact_file_count"] += 1
    out["review_evidence_scope_counts"]["NO_ADDITIONAL_EVIDENCE_ON_THIS_ID"] -= 14
    out["review_evidence_scope_counts"]["BOUNDED_CASE_SOURCE_EVIDENCE"] += 14

    source_pack_name = PACK.name
    seen = set()
    for row in out["source_rows"]:
        source_id = row["candidate_id"]
        if source_id not in by_source:
            continue
        assert row["additional_evidence_scope"] == "NO_ADDITIONAL_EVIDENCE_ON_THIS_ID", source_id
        assert row["original_stage_a_pool"] == "candidate_review_pool", source_id
        assert row["metadata_score_original_not_selection_decision"] >= 60, source_id
        assert row["native_0_1P_state"] == "NATIVE_INDIVIDUAL_0_1P_PENDING", source_id
        assert not row["provisional_case_package_ids_NOT_FORMAL_CLUSTER"]
        case = by_source[source_id][0]
        row["additional_evidence_scope"] = "BOUNDED_CASE_SOURCE_EVIDENCE"
        row["provisional_case_package_ids_NOT_FORMAL_CLUSTER"] = [case["case_id"]]
        row["evidence_artifacts"] = [source_pack_name]
        row["evidence_reference_details"] = [
            {
                "evidence": "OCT30_14_ADDITIONAL_PRIMARY_SOURCE_EVENT_BOUND_CASE",
                "artifact": source_pack_name,
                "tier": "BOUNDED_CASE_PRIMARY_OR_GOVERNMENT",
                "case_ids": [case["case_id"]],
                "event_units": [],
                "mapping_certainty": "SOURCE_TO_CASE_PROVISIONAL_NOT_NATIVE_ADJUDICATED",
            }
        ]
        seen.add(source_id)
    assert seen == set(by_source)

    counts = Counter(r["additional_evidence_scope"] for r in out["source_rows"])
    assert dict(counts) == out["review_evidence_scope_counts"]
    assert len(out["source_rows"]) == 1330
    assert sum(1 for r in out["source_rows"] if r["additional_evidence_scope"] != "NO_ADDITIONAL_EVIDENCE_ON_THIS_ID") == 97
    high = [r for r in out["source_rows"] if r["original_stage_a_pool"] == "candidate_review_pool" and r["metadata_score_original_not_selection_decision"] >= 60]
    assert len(high) == 103
    assert sum(r["additional_evidence_scope"] != "NO_ADDITIONAL_EVIDENCE_ON_THIS_ID" for r in high) == 63
    assert out["original_formal_pending_0_1P_unchanged"] == 1285
    assert out["new_promotions"] == 0
    OUTPUT.open("x", encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(OUTPUT), "sha256": file_hash(OUTPUT), "source_ids": 1330, "added_evidence": 97, "high_with_evidence": 63, "high_without_evidence": 40, "native_pass": False}))


if __name__ == "__main__":
    main()

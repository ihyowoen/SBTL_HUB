#!/usr/bin/env python3
"""Independent losslessness and coverage QC for Stage A pre-native attachments.

Important: a passing receipt is NOT a 70-source native adjudication nor a
new strict promotion; the authoritative native checkers run separately.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

ADDED_FIELD = "pre_native_0_1P_judgment_attachment_20261101"
MANIFEST_FIELD = "pre_native_0_1P_attachment_manifest_20261101"
PARTITIONS = ("candidate_review_pool", "watchlist_context_pool", "existing_reinforcement")


def load(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser()
    for key in ("baseline", "enriched", "sidecar", "first54", "last16", "qc", "receipt"):
        p.add_argument("--" + key, required=True, type=Path)
    a = p.parse_args()
    baseline, enriched, sidecar, first54, last16, qc = (
        load(a.baseline), load(a.enriched), load(a.sidecar), load(a.first54),
        load(a.last16), load(a.qc)
    )

    original54 = {row["source_id"]: row for row in first54["source_level_judgments"]}
    original16 = {row["source_id"]: row for row in last16["judgments"]}
    source70 = {**original16, **original54}
    assert len(source70) == 70 and not set(original54) & set(original16)

    top_meta = enriched[MANIFEST_FIELD]
    assert top_meta["new_formal_decisions"] == 0
    assert top_meta["new_strict_promotions"] == 0
    assert top_meta["remaining_formal_source_count"] == 1285
    assert top_meta["source_batches"] == {"earlier16": 16, "policy_watch54": 54}

    attachment_decision_rows = []
    base_order = [row["candidate_id"] for row in baseline["decision_ledger"]]
    augmented_order = [row["candidate_id"] for row in enriched["decision_ledger"]]
    assert len(base_order) == 1330 and base_order == augmented_order

    # Strip only explicitly added fields and demand full equality of every
    # existing property, including arrays, text, URL, scores, order and gates.
    stripped = copy.deepcopy(enriched)
    stripped.pop(MANIFEST_FIELD)
    for row in stripped["decision_ledger"]:
        if ADDED_FIELD in row:
            attachment_decision_rows.append(row["candidate_id"])
            item = row.pop(ADDED_FIELD)
            assert item["authority"] == "PRE_NATIVE_ONLY_NOT_STAGE_A_APPROVAL"
            assert item["native_formal_adjudication_applied"] is False
            assert item["strict_eligibility_assigned"] is False
            assert item["source_id"] == row["candidate_id"]
            assert item["original_pre_native_judgment"] == source70[row["candidate_id"]]
    assert stripped["decision_ledger"] == baseline["decision_ledger"]
    assert set(attachment_decision_rows) == set(source70)

    attach_partition_rows = []
    for name in PARTITIONS:
        for row in stripped[name]:
            if ADDED_FIELD in row:
                item = row.pop(ADDED_FIELD)
                sid = row["candidate_id"]
                assert item["source_id"] == sid
                assert item["original_pre_native_judgment"] == source70[sid]
                attach_partition_rows.append(sid)
        assert stripped[name] == baseline[name], f"original partition changed: {name}"
    assert Counter(attach_partition_rows) == Counter(attachment_decision_rows)
    assert stripped == baseline, "a governed top-level Stage A field has changed"

    sidecar_ids = [row["source_id"] for row in sidecar["pre_native_judgments"]]
    assert sidecar_ids == attachment_decision_rows
    assert sidecar_ids == sidecar["new_pre_native70_source_ids_in_baseline_order"]
    assert all(row["judgment"] == source70[row["source_id"]] for row in sidecar["pre_native_judgments"])
    assert qc["pre_native_integration_count"] == 70
    assert qc["prior45_individual_adjudications_preserved"] == 45
    assert qc["strict_8_original"] == 8
    assert qc["formal_unadjudicated_remains"] == 1285
    assert qc["output_sha256"]["native_artifact_with_attachments"] == sha256(a.enriched)
    assert qc["output_sha256"]["sidecar"] == sha256(a.sidecar)

    receipt = {
        "artifact_type": "STAGE_A_70_INDEPENDENT_ATTACHMENT_READBACK_20261101",
        "status": "PASS_ADDITIVE_ATTACHMENT_ONLY",
        "baseline_sha256": sha256(a.baseline),
        "enriched_sha256": sha256(a.enriched),
        "sidecar_sha256": sha256(a.sidecar),
        "original_strict_spec_count_preserved": len(baseline["strict_passed_spec"]),
        "original_all_1330_decision_rows_byte_semantic_equal_after_strip": True,
        "original_all_stage_a_top_level_fields_equal_after_strip": True,
        "pre_native_judgments_exactly_preserved": len(source70),
        "pre_native_mapped_once_in_decision_and_partition": True,
        "pre_native_ids_do_not_enter_strict": True,
        "formal_pending_1285_unchanged": True,
        "new_native_adjudications": 0,
        "new_strict_promotions": 0,
        "validator_scope": "TWO_OFFICIAL_NATIVE_CHECKS_SEPARATE_AND_ONLY_PRIOR_EIGHT_STRICT",
    }
    with a.receipt.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

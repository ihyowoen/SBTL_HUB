#!/usr/bin/env python3
"""Attach 70 explicitly NON-NATIVE source judgments to the locked Stage A artifact.

This program performs a lossless provenance attachment, not an adjudication or
strict promotion. The ordinary Stage A validator is run on the output separately;
its PASS does *not* validate the added pre-native judgment content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


EXPECTED_BASE_SHA256 = "b64e4f99f97a872203a4224aed5017697894637391930410577efbcdc35ba8c6"
PARTITIONS = (
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "existing_reinforcement",
)
PRE_NATIVE_FIELD = "pre_native_0_1P_judgment_attachment_20261101"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def unique_index(rows, key: str, label: str) -> dict:
    assert isinstance(rows, list), f"{label}: not a list"
    out = {}
    for row in rows:
        assert isinstance(row, dict), f"{label}: non-object row"
        value = row.get(key)
        assert isinstance(value, str) and value, f"{label}: missing {key}"
        assert value not in out, f"{label}: repeated {key}={value}"
        out[value] = row
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("base", "judgments54", "judgments16", "prior45", "initial45", "out", "sidecar", "qc"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()

    input_paths = {
        "baseline_native_stage_a_20261027": args.base,
        "policy_watch54_four_judgments_20261031": args.judgments54,
        "last16_four_judgments_20261031": args.judgments16,
        "prior45_reassessment_20261027": args.prior45,
        "prior45_original_20261027": args.initial45,
    }
    input_sha256 = {key: sha256(path) for key, path in input_paths.items()}
    assert input_sha256["baseline_native_stage_a_20261027"] == EXPECTED_BASE_SHA256

    base = read_json(args.base)
    batch54 = read_json(args.judgments54)
    batch16 = read_json(args.judgments16)
    prior45 = read_json(args.prior45)
    initial45 = read_json(args.initial45)

    assert base.get("stage") == "stage_a"
    assert base.get("base_main_commit_sha") == "805c2718d6daf40a219ae94242d9687e33ac3e88"
    assert len(base["strict_passed_spec"]) == 8
    assert len(base["candidate_review_pool"]) == 636
    assert len(base["watchlist_context_pool"]) == 658
    assert len(base["existing_reinforcement"]) == 28
    assert len(base["decision_ledger"]) == 1330

    decision_by_id = unique_index(base["decision_ledger"], "candidate_id", "native decision ledger")
    assert len(decision_by_id) == 1330
    partition_by_id = {}
    partition_name_by_id = {}
    before_partition_ids = {}
    for name in PARTITIONS:
        items = base[name]
        ids = [row.get("candidate_id") for row in items]
        if name == "strict_passed_spec":
            # Strict spec IDs differ from source observation IDs by design.
            before_partition_ids[name] = [row.get("spec_id") for row in items]
            continue
        before_partition_ids[name] = ids
        for item in items:
            sid = item.get("candidate_id")
            assert sid in decision_by_id, f"partition missing decision record: {sid}"
            assert sid not in partition_by_id, f"partition duplicate: {sid}"
            partition_by_id[sid] = item
            partition_name_by_id[sid] = name

    # Ordinary Stage A accounts for the eight strict source observations in the
    # decision ledger, but not as 1:1 keys in the strictly selected specs.
    strict_source_ids = {
        sid for spec in base["strict_passed_spec"]
        for sid in spec.get("source_story_ids", [])
    }
    assert len(strict_source_ids) == 8
    assert set(decision_by_id) == (set(partition_by_id) | strict_source_ids)
    assert not (set(partition_by_id) & strict_source_ids)

    pre54 = unique_index(batch54["source_level_judgments"], "source_id", "new54")
    pre16 = unique_index(batch16["judgments"], "source_id", "prior16")
    assert len(pre54) == 54
    assert len(pre16) == 16
    assert not (set(pre54) & set(pre16)), "54 and 16 overlap"
    pre70 = {**pre16, **pre54}
    assert len(pre70) == 70
    assert not (set(pre70) & strict_source_ids), "pre-native material touches authorized strict"

    old45 = unique_index(prior45, "candidate_id", "prior45 reassessed")
    initial = unique_index(initial45, "candidate_id", "prior45 original")
    assert len(old45) == 45 and len(initial) == 45
    assert set(old45) == set(initial), "prior45 inconsistent between original and reassessment"
    assert set(old45) <= set(decision_by_id)
    assert not (set(old45) & set(pre70)), "new70 overlaps already adjudicated45"

    before_strict = json.dumps(base["strict_passed_spec"], ensure_ascii=False, sort_keys=True)
    before_authoritative_decision_fields = {
        sid: {key: value for key, value in row.items() if key != PRE_NATIVE_FIELD}
        for sid, row in decision_by_id.items()
    }

    # We attach original judgments under an explicitly non-authoritative field.
    # No score, route, gate, canonical relation, pool or promotion field changes.
    for sid, judgment in pre70.items():
        assert sid in partition_by_id, f"pre-native Source ID not in non-strict native partition: {sid}"
        decision = decision_by_id[sid]
        partition = partition_by_id[sid]
        assert sid not in strict_source_ids
        assert PRE_NATIVE_FIELD not in decision and PRE_NATIVE_FIELD not in partition
        assert decision["source_row_index"] == judgment["source_row_index"], (
            f"source row index mismatch: {sid}"
        )
        assert decision["headline_raw"] == judgment["headline_raw_original" if sid in pre54 else "headline_raw"], (
            f"original headline mismatch: {sid}"
        )
        assert partition["headline_raw"] == decision["headline_raw"]
        assert judgment["execution_credibility_gate"]["status"] in {"PASS", "REVIEW", "FAIL"}
        assert judgment["independent_cardability_gate"]["status"] in {"PASS", "REVIEW", "FAIL"}
        assert judgment["decision_news_value_score"] == sum(judgment["decision_value_breakdown"].values())
        assert partition_name_by_id[sid] in PARTITIONS[1:]

        snapshot = {
            "authority": "PRE_NATIVE_ONLY_NOT_STAGE_A_APPROVAL",
            "source_batch": "54_POLICY_WATCH" if sid in pre54 else "16_LAST_HIGH60",
            "source_input_sha256": input_sha256[
                "policy_watch54_four_judgments_20261031" if sid in pre54
                else "last16_four_judgments_20261031"
            ],
            "source_id": sid,
            "native_formal_adjudication_applied": False,
            "strict_eligibility_assigned": False,
            "original_pre_native_judgment": judgment,
        }
        decision[PRE_NATIVE_FIELD] = snapshot
        partition[PRE_NATIVE_FIELD] = snapshot

    assert json.dumps(base["strict_passed_spec"], ensure_ascii=False, sort_keys=True) == before_strict
    assert all(
        {key: value for key, value in row.items() if key != PRE_NATIVE_FIELD}
        == before_authoritative_decision_fields[sid]
        for sid, row in decision_by_id.items()
    ), "authoritative decision field changed"
    assert [row["candidate_id"] for row in base["decision_ledger"]] == list(decision_by_id)
    for name in PARTITIONS:
        if name == "strict_passed_spec":
            assert [x.get("spec_id") for x in base[name]] == before_partition_ids[name]
        else:
            assert [x.get("candidate_id") for x in base[name]] == before_partition_ids[name]

    by_partition = dict(Counter(partition_name_by_id[sid] for sid in pre70))
    by_cardability = dict(Counter(p["independent_cardability_gate"]["status"] for p in pre70.values()))
    by_execution = dict(Counter(p["execution_credibility_gate"]["status"] for p in pre70.values()))
    all_ids = list(decision_by_id)
    present_pre = [sid for sid in all_ids if sid in pre70]
    sidecar = {
        "artifact_type": "STAGE_A_70_SOURCE_PRE_NATIVE_JUDGMENTS_ATTACHED_TO_ORDINARY_NATIVE_STAGE_A",
        "as_of_utc": "2026-11-01",
        "source_baseline_sha256": EXPECTED_BASE_SHA256,
        "locked_main_commit": base["base_main_commit_sha"],
        "input_sha256": input_sha256,
        "existing_prior45_ids": list(old45),
        "new_pre_native70_source_ids_in_baseline_order": present_pre,
        "strict_source_ids_preserved": sorted(strict_source_ids),
        "pre_native_judgments": [
            {
                "source_id": sid,
                "source_row_index": pre70[sid]["source_row_index"],
                "native_partition_unchanged": partition_name_by_id[sid],
                "native_adjudication": "NOT_PERFORMED",
                "strict_promotion": False,
                "judgment": pre70[sid],
            }
            for sid in present_pre
        ],
        "native_validator_scope_warning": (
            "The two native checker PASS results apply to the unchanged eight strict specs "
            "and ordinary artifact contract, not substantive certification of these 70 attachments."
        ),
        "formal_remaining_1285_unchanged": True,
    }
    base["pre_native_0_1P_attachment_manifest_20261101"] = {
        "pre_native_source_count": 70,
        "prior_formal_source_count_unchanged": 45,
        "new_formal_decisions": 0,
        "new_strict_promotions": 0,
        "remaining_formal_source_count": 1285,
        "source_batches": {"earlier16": 16, "policy_watch54": 54},
        "authority": "EVIDENCE_ATTACHMENT_ONLY_GOVERNED_FIELDS_UNCHANGED",
        "native_validator_scope_warning": sidecar["native_validator_scope_warning"],
        "source_input_sha256": input_sha256,
    }

    qc = {
        "artifact_type": "STAGE_A_70_PRE_NATIVE_INTEGRATION_QC_20261101",
        "scope_status": "PASS_LOSSLESS_ATTACHMENT_NOT_70_NATIVE_PROMOTIONS",
        "baseline_artifact_sha256": EXPECTED_BASE_SHA256,
        "baseline_locked_main": base["base_main_commit_sha"],
        "original_source_ids": 1330,
        "original_distinct_source_ids": len(decision_by_id),
        "prior45_individual_adjudications_preserved": len(old45),
        "pre_native_integration_count": len(pre70),
        "pre_native_previous16": len(pre16),
        "pre_native_new54": len(pre54),
        "pre_native_prior45_overlap": len(set(pre70) & set(old45)),
        "pre_native_strict_overlap": len(set(pre70) & strict_source_ids),
        "source_ids_missing": 0,
        "authoritative_fields_changed": 0,
        "strict_payload_changed": False,
        "strict_8_original": len(base["strict_passed_spec"]),
        "partition_counts_unchanged": {name: len(base[name]) for name in PARTITIONS},
        "attached_partition_counts": by_partition,
        "attached_execution_gate_counts_non_native": by_execution,
        "attached_cardability_gate_counts_non_native": by_cardability,
        "formal_unadjudicated_remains": 1285,
        "new_formal_strict_promotions": 0,
        "stage_b_new_entry_authorized": False,
        "input_sha256": input_sha256,
        "native_checks": "RUN_SEPARATELY_AFTER_BUILD",
    }

    write_json(args.out, base)
    write_json(args.sidecar, sidecar)
    write_json(args.qc, qc)
    qc["output_sha256"] = {"native_artifact_with_attachments": sha256(args.out), "sidecar": sha256(args.sidecar)}
    write_json(args.qc, qc)
    print(json.dumps({"qc": qc, "out_bytes": args.out.stat().st_size}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

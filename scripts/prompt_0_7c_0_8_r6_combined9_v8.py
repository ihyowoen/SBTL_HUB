#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V5_PATH = ROOT / "scripts/prompt_0_7c_0_8_r6_combined9_v5.py"
spec = importlib.util.spec_from_file_location("r6_combined9_v5", V5_PATH)
v5 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(v5)

core = v5.core
STAGE_C_SOURCES = [
    ROOT / "runs/2026-09-03/stage_c_r6_accepted7_20260903_R1.json",
    ROOT / "runs/2026-09-03/stage_c_r6_promotion2_20260903_R1.json",
]


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _pass_marker(value) -> bool:
    return isinstance(value, str) and value.upper().startswith("PASS")


def _stage_c_by_spec() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in STAGE_C_SOURCES:
        payload = _load(path)
        if payload.get("status") != "PASS":
            raise AssertionError(f"Stage C source is not PASS: {path}")
        rows = payload.get("accepted_fact_safe")
        if not isinstance(rows, list):
            raise AssertionError(f"accepted_fact_safe[] missing: {path}")
        for row in rows:
            if not isinstance(row, dict):
                continue
            sid = row.get("source_spec_id") or row.get("spec_id")
            if not isinstance(sid, str) or not sid:
                raise AssertionError(f"Stage C row missing source_spec_id: {path}")
            if sid in out:
                raise AssertionError(f"duplicate Stage C source_spec_id: {sid}")
            out[sid] = row
    if len(out) != 9:
        raise AssertionError(f"expected 9 Stage C rows, found {len(out)}")
    return out


def _require_stage_c_contract(source: dict, sid: str) -> dict:
    lineage = source.get("related_lineage")
    if not isinstance(lineage, dict):
        raise AssertionError(f"{sid}: Stage C related_lineage missing")
    if not _pass_marker(lineage.get("same_event_check")):
        raise AssertionError(f"{sid}: Stage C same_event_check not PASS")
    if not _pass_marker(lineage.get("earliest_date_check")):
        raise AssertionError(f"{sid}: Stage C earliest_date_check not PASS")
    return lineage


def build_operations_post_core_stage_c_contract(final_rows, stage_refs):
    # First let v5 build the exact insertion/related_add structure. That core
    # intentionally converts a related insert to a temporary unrelated insert.
    # Only after that transformation do we re-attach already-validated Stage C
    # lifecycle assertions, so they cannot be discarded by core normalization.
    operations = v5.build_operations_with_complete_related_lineage(final_rows, stage_refs)
    stage_c = _stage_c_by_spec()

    insert_by_id: dict[str, dict] = {}
    for op in operations.get("insert", []):
        card = op.get("card") if isinstance(op, dict) else None
        if not isinstance(card, dict):
            raise AssertionError("insert card missing")
        sid = card.get("source_spec_id") or card.get("spec_id")
        source = stage_c.get(sid)
        if not isinstance(source, dict):
            raise AssertionError(f"{card.get('id')}: no exact Stage C source for {sid}")
        source_lineage = _require_stage_c_contract(source, sid)
        lineage = card.get("related_lineage")
        if not isinstance(lineage, dict):
            raise AssertionError(f"{card.get('id')}: insert related_lineage missing")

        lineage["same_event_checked"] = True
        lineage["earliest_same_event_date_checked"] = True

        source_relation_type = source_lineage.get("relation_type")
        # The insert may be temporarily new_unrelated_event even when the final
        # source relation is distinct_follow_up/program_lineage. Preserve the
        # item-specific follow-up semantics from Stage C for later related_add.
        if source_relation_type == "distinct_follow_up":
            anchor_class = source_lineage.get("fresh_follow_up_anchor_class")
            anchor = source_lineage.get("fresh_follow_up_anchor")
            incremental = source_lineage.get("incremental_fact_vs_predecessor") or source_lineage.get("incremental_fact")
            changed = source_lineage.get("changed_judgment_vs_predecessor") or source_lineage.get("changed_judgment")
            if not all(isinstance(v, str) and v.strip() for v in (anchor_class, anchor, incremental, changed)):
                raise AssertionError(f"{sid}: Stage C distinct-follow-up semantics incomplete")
            lineage["fresh_follow_up_anchor_class"] = anchor_class
            lineage["fresh_follow_up_anchor"] = anchor
            lineage["incremental_fact_vs_predecessor"] = incremental
            lineage["changed_judgment_vs_predecessor"] = changed

        card["related_lineage"] = lineage
        insert_by_id[card["id"]] = card

    for rel in operations.get("related_add", []):
        source_id = rel.get("source_id")
        card = insert_by_id.get(source_id)
        if not isinstance(card, dict):
            raise AssertionError(f"related source insert missing: {source_id}")
        lineage = card["related_lineage"]
        patches = rel.get("patches")
        if not isinstance(patches, list):
            raise AssertionError(f"{source_id}: related patches missing")

        # These booleans are already present in the insertion payload; include
        # them in the related operation audit too so the immutable operation
        # set documents the final lifecycle contract explicitly.
        v5._ensure_patch(patches, card_id=source_id, path="/related_lineage/same_event_checked", value=True, op="replace")
        v5._ensure_patch(patches, card_id=source_id, path="/related_lineage/earliest_same_event_date_checked", value=True, op="replace")

        if rel.get("relation_type") == "distinct_follow_up":
            for field in (
                "fresh_follow_up_anchor_class",
                "fresh_follow_up_anchor",
                "incremental_fact_vs_predecessor",
                "changed_judgment_vs_predecessor",
            ):
                value = lineage.get(field)
                if not isinstance(value, str) or not value.strip():
                    raise AssertionError(f"{source_id}: missing published {field}")
                v5._ensure_patch(
                    patches,
                    card_id=source_id,
                    path=f"/related_lineage/{field}",
                    value=value,
                    op="replace",
                )

    return operations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = parser.parse_args()

    v5.v4.v3.bind_validated_stage_b_rereview()
    v5.v4.bind_validated_stage_a_relation_rereview()
    core.build_operations = build_operations_post_core_stage_c_contract

    if args.phase == "prepare":
        core.prepare()
        v5.v4.v3.v2.normalize_document_universe_bridge()
    else:
        core.finalize_audit()


if __name__ == "__main__":
    main()

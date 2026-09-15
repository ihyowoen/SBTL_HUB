#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V5_PATH = ROOT / "scripts/prompt_0_7c_0_8_r6_combined9_v5.py"
spec = importlib.util.spec_from_file_location("r6_combined9_v5", V5_PATH)
v5 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(v5)

core = v5.core
ORIGINAL_BUILD_OPERATIONS = v5.build_operations_with_complete_related_lineage


def _pass_marker(value) -> bool:
    return isinstance(value, str) and value.upper().startswith("PASS")


def build_operations_with_published_related_contract(final_rows, stage_refs):
    operations = ORIGINAL_BUILD_OPERATIONS(final_rows, stage_refs)

    for insert in operations.get("insert", []):
        card = insert.get("card") if isinstance(insert, dict) else None
        if not isinstance(card, dict):
            raise AssertionError("insert card missing")
        lineage = card.get("related_lineage")
        if not isinstance(lineage, dict):
            raise AssertionError(f"{card.get('id')}: related_lineage missing")

        # Stage C/0.7 carry string PASS markers. The published lifecycle
        # contract requires explicit booleans; convert only when the source
        # markers themselves are passing, otherwise fail closed.
        same_event_marker = lineage.get("same_event_check")
        earliest_marker = lineage.get("earliest_date_check")
        if not _pass_marker(same_event_marker):
            raise AssertionError(f"{card.get('id')}: same_event_check is not PASS: {same_event_marker!r}")
        if not _pass_marker(earliest_marker):
            raise AssertionError(f"{card.get('id')}: earliest_date_check is not PASS: {earliest_marker!r}")
        lineage["same_event_checked"] = True
        lineage["earliest_same_event_date_checked"] = True

        relation_type = lineage.get("relation_type")
        if relation_type == "distinct_follow_up":
            # These semantics already exist in the fact-safe Stage C lineage;
            # map the legacy field names to the current published contract.
            anchor_class = lineage.get("fresh_follow_up_anchor_class")
            anchor = lineage.get("fresh_follow_up_anchor")
            incremental = lineage.get("incremental_fact_vs_predecessor") or lineage.get("incremental_fact")
            changed = lineage.get("changed_judgment_vs_predecessor") or lineage.get("changed_judgment")
            if not all(isinstance(v, str) and v.strip() for v in (anchor_class, anchor, incremental, changed)):
                raise AssertionError(f"{card.get('id')}: incomplete distinct-follow-up lineage semantics")
            lineage["incremental_fact_vs_predecessor"] = incremental
            lineage["changed_judgment_vs_predecessor"] = changed

        card["related_lineage"] = lineage

    # related_add patches must also write the lifecycle booleans and, for a
    # distinct follow-up, the exact item-specific semantics that the insert
    # payload carries. This keeps operation replay byte-semantic and makes the
    # reviewed operation set itself sufficient to reconstruct the contract.
    insert_by_id = {
        op["card"]["id"]: op["card"]
        for op in operations.get("insert", [])
        if isinstance(op, dict) and isinstance(op.get("card"), dict)
    }
    for rel in operations.get("related_add", []):
        source = rel["source_id"]
        card = insert_by_id.get(source)
        if not isinstance(card, dict):
            raise AssertionError(f"related source insert missing: {source}")
        lineage = card["related_lineage"]
        patches = rel.get("patches")
        if not isinstance(patches, list):
            raise AssertionError(f"{source}: related patches missing")

        v5._ensure_patch(patches, card_id=source, path="/related_lineage/same_event_checked", value=True, op="add")
        v5._ensure_patch(patches, card_id=source, path="/related_lineage/earliest_same_event_date_checked", value=True, op="add")

        if rel.get("relation_type") == "distinct_follow_up":
            for field in (
                "fresh_follow_up_anchor_class",
                "fresh_follow_up_anchor",
                "incremental_fact_vs_predecessor",
                "changed_judgment_vs_predecessor",
            ):
                value = lineage.get(field)
                if not isinstance(value, str) or not value.strip():
                    raise AssertionError(f"{source}: missing {field}")
                v5._ensure_patch(
                    patches,
                    card_id=source,
                    path=f"/related_lineage/{field}",
                    value=value,
                    op="add" if field not in {"fresh_follow_up_anchor_class", "fresh_follow_up_anchor"} else "replace",
                )

    return operations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = parser.parse_args()

    v5.v4.v3.bind_validated_stage_b_rereview()
    v5.v4.bind_validated_stage_a_relation_rereview()
    core.build_operations = build_operations_with_published_related_contract

    if args.phase == "prepare":
        core.prepare()
        v5.v4.v3.v2.normalize_document_universe_bridge()
    else:
        core.finalize_audit()


if __name__ == "__main__":
    main()

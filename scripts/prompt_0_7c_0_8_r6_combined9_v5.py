#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V4_PATH = ROOT / "scripts/prompt_0_7c_0_8_r6_combined9_v4.py"
spec = importlib.util.spec_from_file_location("r6_combined9_v4", V4_PATH)
v4 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(v4)

core = v4.v3.v2.core
ORIGINAL_BUILD_OPERATIONS = core.build_operations


def _ensure_patch(patches: list[dict], *, card_id: str, path: str, value, op: str) -> None:
    matches = [p for p in patches if p.get("card_id") == card_id and p.get("path") == path]
    if len(matches) > 1:
        raise AssertionError(f"duplicate related patch before normalization: {card_id} {path}")
    if matches:
        matches[0].update({"op": op, "value": value})
    else:
        patches.append({"card_id": card_id, "op": op, "path": path, "value": value})


def build_operations_with_complete_related_lineage(final_rows, stage_refs):
    operations = ORIGINAL_BUILD_OPERATIONS(final_rows, stage_refs)

    # Canonical cards publish `related[]` plus `related_lineage`; top-level
    # `related_ids` is a stage artifact convenience field and must not enter
    # the insertion payload or Prompt 0.8 patch language.
    for insert in operations.get("insert", []):
        card = insert.get("card") if isinstance(insert, dict) else None
        if isinstance(card, dict):
            card.pop("related_ids", None)

    for rel in operations.get("related_add", []):
        patches = rel.get("patches")
        if not isinstance(patches, list):
            raise AssertionError("related_add patches missing")
        patches[:] = [p for p in patches if p.get("path") != "/related_ids/-" and not str(p.get("path", "")).startswith("/related_ids/")]

        source = rel["source_id"]
        target = rel["target_id"]
        relation_type = rel["relation_type"]
        reason = rel["lineage_reason"]
        event_stage = rel["event_stage_relationship"]
        direction = rel["direction"]

        _ensure_patch(patches, card_id=source, path="/related/-", value=target, op="add")
        _ensure_patch(patches, card_id=source, path="/related_lineage/related_ids/-", value=target, op="add")
        _ensure_patch(patches, card_id=source, path="/related_lineage/relation_type", value=relation_type, op="replace")
        _ensure_patch(patches, card_id=source, path="/related_lineage/reason", value=reason, op="replace")
        _ensure_patch(patches, card_id=source, path="/related_lineage/event_stage_relationship", value=event_stage, op="replace")
        _ensure_patch(patches, card_id=source, path="/related_lineage/direction", value=direction, op="replace")

        if direction == "reciprocal":
            _ensure_patch(patches, card_id=target, path="/related/-", value=source, op="add")
            _ensure_patch(patches, card_id=target, path="/related_lineage/related_ids/-", value=source, op="add")
            _ensure_patch(patches, card_id=target, path="/related_lineage/relation_type", value=relation_type, op="replace")
            _ensure_patch(patches, card_id=target, path="/related_lineage/reason", value=reason, op="replace")
            _ensure_patch(patches, card_id=target, path="/related_lineage/event_stage_relationship", value=event_stage, op="replace")
            _ensure_patch(patches, card_id=target, path="/related_lineage/direction", value=direction, op="replace")
        elif direction != "directional":
            raise AssertionError(f"unsupported related direction: {direction}")

    return operations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = parser.parse_args()

    v4.v3.bind_validated_stage_b_rereview()
    v4.bind_validated_stage_a_relation_rereview()
    core.build_operations = build_operations_with_complete_related_lineage

    if args.phase == "prepare":
        core.prepare()
        v4.v3.v2.normalize_document_universe_bridge()
    else:
        core.finalize_audit()


if __name__ == "__main__":
    main()

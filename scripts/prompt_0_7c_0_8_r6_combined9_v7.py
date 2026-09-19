#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V6_PATH = ROOT / "scripts/prompt_0_7c_0_8_r6_combined9_v6.py"
spec = importlib.util.spec_from_file_location("r6_combined9_v6", V6_PATH)
v6 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(v6)

core = v6.core
STAGE_C_SOURCES = [
    ROOT / "runs/2026-09-03/stage_c_r6_accepted7_20260903_R1.json",
    ROOT / "runs/2026-09-03/stage_c_r6_promotion2_20260903_R1.json",
]


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _stage_c_by_spec() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in STAGE_C_SOURCES:
        payload = _load(path)
        if payload.get("status") != "PASS":
            raise AssertionError(f"Stage C fallback source is not PASS: {path}")
        rows = payload.get("accepted_fact_safe")
        if not isinstance(rows, list):
            raise AssertionError(f"Stage C fallback accepted_fact_safe[] missing: {path}")
        for row in rows:
            if not isinstance(row, dict):
                continue
            sid = row.get("source_spec_id") or row.get("spec_id")
            if not isinstance(sid, str) or not sid:
                raise AssertionError(f"Stage C row missing source_spec_id: {path}")
            if sid in out:
                raise AssertionError(f"duplicate Stage C source_spec_id across fallback artifacts: {sid}")
            out[sid] = row
    if len(out) != 9:
        raise AssertionError(f"expected 9 Stage C fallback rows, found {len(out)}")
    return out


def _copy_missing_lineage_fields(final_rows: list[dict]) -> list[dict]:
    stage_c = _stage_c_by_spec()
    enriched = copy.deepcopy(final_rows)
    fields = (
        "same_event_check",
        "earliest_date_check",
        "fresh_follow_up_anchor_class",
        "fresh_follow_up_anchor",
        "incremental_fact",
        "changed_judgment",
        "incremental_fact_vs_predecessor",
        "changed_judgment_vs_predecessor",
    )
    for row in enriched:
        sid = row.get("source_spec_id")
        if sid not in stage_c:
            raise AssertionError(f"final row has no exact Stage C fallback: {sid}")
        final_lineage = row.get("related_lineage")
        source_lineage = stage_c[sid].get("related_lineage")
        if not isinstance(final_lineage, dict) or not isinstance(source_lineage, dict):
            raise AssertionError(f"{sid}: related_lineage missing in final or Stage C source")

        # Only fill fields lost by downstream projections. Never overwrite a
        # non-empty 0.7 value and never synthesize a new adjudication.
        for field in fields:
            current = final_lineage.get(field)
            source = source_lineage.get(field)
            current_missing = current is None or current == ""
            if current_missing and source not in (None, ""):
                final_lineage[field] = copy.deepcopy(source)
        row["related_lineage"] = final_lineage
    return enriched


def build_operations_with_stage_c_lineage_fallback(final_rows, stage_refs):
    enriched = _copy_missing_lineage_fields(final_rows)
    return v6.build_operations_with_published_related_contract(enriched, stage_refs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = parser.parse_args()

    v6.v5.v4.v3.bind_validated_stage_b_rereview()
    v6.v5.v4.bind_validated_stage_a_relation_rereview()
    core.build_operations = build_operations_with_stage_c_lineage_fallback

    if args.phase == "prepare":
        core.prepare()
        v6.v5.v4.v3.v2.normalize_document_universe_bridge()
    else:
        core.finalize_audit()


if __name__ == "__main__":
    main()

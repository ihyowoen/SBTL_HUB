#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V3_PATH = ROOT / "scripts/prompt_0_7c_0_8_r6_combined9_v3.py"
spec = importlib.util.spec_from_file_location("r6_combined9_v3", V3_PATH)
v3 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(v3)

OLD_STAGE_A = ROOT / "runs/2026-09-03/stage_a_formal_r6_batch01_20260903_R1.json"
REREVIEW_STAGE_A = ROOT / "runs/2026-09-04/stage_a_r6_batch01_cn_tax_relation_rereview_R1.json"


def bind_validated_stage_a_relation_rereview() -> None:
    if not REREVIEW_STAGE_A.is_file():
        raise AssertionError(f"validated China-tax Stage A rereview missing: {REREVIEW_STAGE_A}")
    replaced = 0
    rebound = []
    for source, dest in v3.v2.core.BRIDGE_SOURCES:
        if source.resolve() == OLD_STAGE_A.resolve():
            source = REREVIEW_STAGE_A
            replaced += 1
        rebound.append((source, dest))
    if replaced != 1:
        raise AssertionError(f"expected exactly one strict7 Stage A bridge replacement, found {replaced}")
    v3.v2.core.BRIDGE_SOURCES = rebound


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = parser.parse_args()

    v3.bind_validated_stage_b_rereview()
    bind_validated_stage_a_relation_rereview()

    if args.phase == "prepare":
        v3.v2.core.prepare()
        v3.v2.normalize_document_universe_bridge()
    else:
        v3.v2.core.finalize_audit()


if __name__ == "__main__":
    main()

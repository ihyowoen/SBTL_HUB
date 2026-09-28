#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2_PATH = ROOT / "scripts/prompt_0_7c_0_8_r6_combined9_v2.py"
spec = importlib.util.spec_from_file_location("r6_combined9_v2", V2_PATH)
v2 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(v2)

OLD_STAGE_B = ROOT / "runs/2026-09-03/stage_b_r6_strict7_20260903_R1.json"
REREVIEW_STAGE_B = ROOT / "runs/2026-09-04/stage_b_r6_strict7_eu_relation_rereview_R2.json"


def bind_validated_stage_b_rereview() -> None:
    if not REREVIEW_STAGE_B.is_file():
        raise AssertionError(f"validated EU Stage B rereview missing: {REREVIEW_STAGE_B}")
    replaced = 0
    rebound = []
    for source, dest in v2.core.BRIDGE_SOURCES:
        if source.resolve() == OLD_STAGE_B.resolve():
            source = REREVIEW_STAGE_B
            replaced += 1
        rebound.append((source, dest))
    if replaced != 1:
        raise AssertionError(f"expected exactly one strict7 Stage B bridge replacement, found {replaced}")
    v2.core.BRIDGE_SOURCES = rebound


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = parser.parse_args()
    bind_validated_stage_b_rereview()
    if args.phase == "prepare":
        v2.core.prepare()
        v2.normalize_document_universe_bridge()
    else:
        v2.core.finalize_audit()


if __name__ == "__main__":
    main()

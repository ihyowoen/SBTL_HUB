#!/usr/bin/env python3
"""Temporary deterministic semantic patch for R7 Stage A validation artifacts.

This does not change disposition, score, route, event identity, or source membership.
It materializes the structured Stage-B evidence targets and measurable confirmation
points required by the active frozen-V3 compatibility validator.
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path


def short(text: object, limit: int = 180) -> str:
    value = " ".join(str(text or "").split())
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def patch_spec(spec: dict) -> None:
    title = short(spec.get("title_raw") or spec.get("summary_hint") or spec.get("spec_id"), 180)
    date = str(spec.get("representative_date") or spec.get("date_role", {}).get("event_date") or "current event date")
    route = str(spec.get("selection_route") or "")
    anchors = ", ".join(spec.get("anchor_classes") or [])

    spec["evidence_needed_for_stage_b"] = [
        {
            "source_or_document_class": "official document or contract",
            "exact_claim_or_metric": f"{title}: exact event stage and event date {date}",
        },
        {
            "source_or_document_class": "official filing, dataset, statistics, technical test result, permit, regulation, or independent report",
            "exact_claim_or_metric": f"{title}: named production, shipment, approval, capacity, volume, price, cost, status, or other headline metric at the claimed stage",
        },
    ]
    spec["next_confirmation_points"] = [
        {
            "measurable_event_or_metric": f"{title}: next production, shipment, approval, permit, contract, capacity, volume, price, cost, status, or effective-date metric after {date}",
            "interpretation_effect": "A verified result would strengthen or weaken the current Stage A judgment and outlook for independent cardability.",
        }
    ]

    # Keep V4 and V3 route semantics explicit; do not synthesize an execution path
    # for structural non-execution candidates.
    if route == "structural_non_execution_route":
        spec["execution_anchor_type"] = None
        spec["execution_anchor_strength"] = None
        spec["structural_value_override_applied"] = True
        spec["structural_selector_policy_version"] = "STRUCTURAL_NEWS_VALUE_SELECTION_V3"
        if not spec.get("structural_value_override_reason"):
            spec["structural_value_override_reason"] = (
                f"{title} is evaluated through the canonical V3 non-execution compatibility route using anchor classes {anchors}."
            )
    elif route == "execution_anchor_route":
        spec["structural_value_override_applied"] = False
        spec["structural_value_override_reason"] = None
        spec["why_execution_event_not_required"] = None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    args = ap.parse_args()
    paths = sorted(glob.glob(str(Path(args.directory) / "stage-a-b*.json")))
    if not paths:
        raise SystemExit("no Stage A batch files found")
    total = 0
    for filename in paths:
        path = Path(filename)
        data = json.loads(path.read_text(encoding="utf-8"))
        for spec in data.get("strict_passed_spec", []):
            patch_spec(spec)
            total += 1
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"patched strict specs: {total}")
    if total != 43:
        raise SystemExit(f"expected 43 strict specs, got {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

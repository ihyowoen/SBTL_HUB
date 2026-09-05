#!/usr/bin/env python3
"""Temporary deterministic semantic patch for R7 Stage A validation artifacts.

No disposition, score, route, event identity, source membership, or canonical relation
is changed. The patch only materializes machine-compatible Stage-B evidence targets,
measurable confirmation points, review-subtype metadata, and exact decision-ledger
carry fields required by current main.
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
        f"official document or contract: {title}; exact event stage and event date {date}",
        f"official filing, dataset, statistics, technical test result, permit, regulation, or independent report: {title}; production, shipment, approval, capacity, volume, price, cost, or status metric at the claimed stage",
    ]
    thesis = "structural thesis" if route == "structural_non_execution_route" else "execution thesis"
    # Separate the measurable target from the semantic interpretation clauses.
    # This avoids a measured noun in a long title being mistaken for the object
    # of strengthen/weaken by the current semantic binder.
    spec["next_confirmation_points"] = [
        f"{title}: production, shipment, approval, permit, contract, capacity, volume, price, cost, status, or effective-date milestone after {date}. The {thesis} would strengthen on confirmation; the {thesis} would weaken on reversal",
    ]

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


def patch_reviews(data: dict) -> None:
    for row in data.get("watchlist_context_pool", []):
        title = short(row.get("title_raw") or row.get("review_pool_item_id"), 160)
        row["recommended_next_action"] = (
            f"Monitor {title} for the recorded measurable trigger and reopen only if that trigger materially strengthens independent cardability."
        )
    for row in data.get("reject_or_support_only_pool", []):
        title = short(row.get("title_raw") or row.get("review_pool_item_id"), 160)
        row["recommended_next_action"] = (
            f"Retain {title} only as support or context for the current run; reopen only on a new independent event anchor."
        )
    for row in data.get("candidate_review_pool", []):
        subtype = row.get("review_pool_subtype")
        title = short(row.get("title_raw") or row.get("review_pool_item_id"), 160)
        if subtype == "structural_signal_review":
            row["structural_rescue_required"] = True
            row["structural_rescue_question"] = (
                f"Does bounded verification of {title} establish a current structural change strong enough to alter the judgment and justify independent cardability?"
            )
        if subtype == "earnings_deep_dive":
            row["earnings_deep_dive_required"] = True
            row["earnings_release_available"] = "unknown"
            row["ir_deck_available"] = "unknown"
            row["call_or_transcript_expected"] = "unknown"
            row["qna_status"] = "not_checked_stage_a"
            row["prior_period_comparison_required"] = True
            if not row.get("earnings_rescue_questions"):
                row["earnings_rescue_questions"] = [
                    f"Check the official earnings release or filing for {title}: revenue, profit, margin, volume, cost, capacity/utilisation, guidance, capex, prior-period comparison, and call/Q&A availability."
                ]


def sync_decision_ledger(data: dict) -> None:
    specs = {row.get("spec_id"): row for row in data.get("strict_passed_spec", []) if row.get("spec_id")}
    for row in data.get("decision_ledger", []):
        sid = row.get("spec_id") or row.get("merged_into_spec_id")
        spec = specs.get(sid)
        if not spec:
            continue
        row["evidence_needed_for_stage_b"] = list(spec["evidence_needed_for_stage_b"])
        row["next_confirmation_points"] = list(spec["next_confirmation_points"])


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
        patch_reviews(data)
        sync_decision_ledger(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"patched strict specs: {total}")
    if total != 43:
        raise SystemExit(f"expected 43 strict specs, got {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

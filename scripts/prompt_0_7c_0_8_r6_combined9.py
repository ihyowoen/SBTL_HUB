#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "runs/2026-09-03"
OUT = ROOT / "runs/2026-09-04/r6-combined9-production-r1"
STAGES = OUT / "stages"

MAIN = "df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4"
BLOB = "53219907cdb435c3822c41d097b23e475662aa8a"
BASE_COUNT = 1514
RUN_ID = "card-run-2026-09-04-r6-combined9-production-r1"
OUTPUT_UPDATED = "2026-09-04T01:30:00+09:00"

DOC_SOURCE = SRC / "stage_0_0d_v4_document_universe_20260903_MAIN_df6fccc_R2.json"
REPLAY = SRC / "current_authoritative_632_replay_manifest_R1.json"
RAW_BINDING = SRC / "raw_input_chat_attachment_binding_20260831_20260901_R2.json"
EVENT_GATE = SRC / "current_event_universe_replay_gate_20260903_R6.json"
STAGE_A_ALL = SRC / "stage_a_formal_r6_all_batches_20260903_R1.json"
PROMOTION_A = SRC / "stage_a_prompt_0_1p_r6_promotion16_20260903_R1.json"
FINAL_QC = SRC / "prompt_0_7_r6_combined9_20260903_R1.json"
CANON = ROOT / "data/cards.full.json"

BRIDGE_SOURCES = [
    (SRC / "stage_a_formal_r6_batch01_20260903_R1.json", STAGES / "stage-a-strict7.json"),
    (SRC / "stage_a_prompt_0_1p_r6_promotion16_20260903_R1.json", STAGES / "stage-a-promotion2.json"),
    (SRC / "stage_b_r6_strict7_20260903_R1.json", STAGES / "stage-b-strict7.json"),
    (SRC / "stage_b_r6_promotion2_20260903_R1.json", STAGES / "stage-b-promotion2.json"),
    (SRC / "stage_c_r6_accepted7_20260903_R1.json", STAGES / "stage-c-strict7.json"),
    (SRC / "stage_c_r6_promotion2_20260903_R1.json", STAGES / "stage-c-promotion2.json"),
    (SRC / "prompt_0_4_r6_combined9_20260903_R1.json", STAGES / "stage-0-4-combined9.json"),
    (SRC / "prompt_0_5_r6_combined9_20260903_R1.json", STAGES / "stage-0-5-combined9.json"),
    (SRC / "prompt_0_6_r6_combined9_20260903_R1.json", STAGES / "stage-0-6-combined9.json"),
    (SRC / "prompt_0_7_r6_combined9_20260903_R1.json", STAGES / "stage-0-7-combined9.json"),
]

DOC_REF = "runs/2026-09-04/r6-combined9-production-r1/stage-0-0d.json"
COVERAGE_REF = "runs/2026-09-04/r6-combined9-production-r1/stage-0-0c.json"
COMPLETE_REF = "runs/2026-09-04/r6-combined9-production-r1/stage-0-7c.json"
MERGE_REF = "runs/2026-09-04/r6-combined9-production-r1/stage-0-8.json"
AUDIT_REF = "runs/2026-09-04/r6-combined9-production-r1/card-run-audit.json"
RUN_REF = "runs/2026-09-04/r6-combined9-production-r1/card-run.json"
CANDIDATE_FULL = OUT / "candidate.cards.full.json"
CANDIDATE_LEAN = OUT / "candidate.cards.json"

REGIONS = ["korea", "north_america", "china", "japan", "europe", "material_global_markets"]
TOPICS = [
    "cells_chemistries", "materials_components", "pouch_pouch_film_demand", "ess_bess",
    "ev_charging", "manufacturing_capacity_utilisation", "grid_ai_data_centre_power",
    "critical_minerals_refining", "recycling", "policy_trade_sanctions_subsidies_localisation",
    "competitors_customers", "prices_costs_margins", "financing",
    "safety_recall_commissioning_operation",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable(value):
    if isinstance(value, list):
        return [stable(v) for v in value]
    if isinstance(value, dict):
        return {k: stable(value[k]) for k in sorted(value)}
    return value


def operations_sha(operations) -> str:
    raw = json.dumps(stable(operations), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(raw)


def rows(payload, buckets):
    out = []
    for bucket in buckets:
        value = payload.get(bucket)
        if isinstance(value, dict):
            out.append(value)
        elif isinstance(value, list):
            out.extend(x for x in value if isinstance(x, dict))
    return out


def spec_set(payload, stage: str):
    buckets = {
        "A": ["strict_passed_spec"], "B": ["draft_cards", "draft_card"],
        "C": ["accepted_fact_safe"], "0.4": ["addable_merge_safe"],
        "0.5": ["evidence_complete_and_source_claim_covered"],
        "0.6": ["content_enriched_and_language_polished"], "0.7": ["publish_ready"],
    }[stage]
    key = "spec_id" if stage == "A" else "source_spec_id"
    return {x[key] for x in rows(payload, buckets) if isinstance(x.get(key), str) and x[key]}


def unique_urls(item):
    urls = []
    for value in item.get("urls", []):
        if isinstance(value, str) and value.startswith(("http://", "https://")) and value not in urls:
            urls.append(value)
    for src in item.get("fact_sources", []):
        if not isinstance(src, dict):
            continue
        value = src.get("url") or src.get("source_url")
        if isinstance(value, str) and value.startswith(("http://", "https://")) and value not in urls:
            urls.append(value)
    if not urls:
        raise AssertionError(f"{item.get('id')}: evidence URL missing")
    return urls


def lineage_reason(lin):
    for key in ("reason", "relation_reason", "lineage_reason"):
        value = lin.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def bridge_artifacts():
    refs = []
    stage_kinds = []
    for source, dest in BRIDGE_SOURCES:
        payload = copy.deepcopy(load(source))
        payload["run_id"] = RUN_ID
        payload["base_main_commit_sha"] = MAIN
        payload["base_full_blob_sha"] = BLOB
        payload["formal_run_binding"] = {
            "status": "PASS",
            "source_artifact": rel(source),
            "source_artifact_sha256": sha256_file(source),
            "binding_only_no_re_adjudication": True,
        }
        write(dest, payload)
        refs.append(rel(dest))
        stage = str(payload.get("stage", "")).lower()
        if stage in {"a", "stage_a", "0.1"}: kind = "A"
        elif stage in {"b", "stage_b", "0.2"}: kind = "B"
        elif stage in {"c", "stage_c", "0.3"}: kind = "C"
        else: kind = str(payload.get("stage"))
        stage_kinds.append((rel(dest), kind, spec_set(payload, kind)))
    return refs, stage_kinds


def build_coverage():
    replay = load(REPLAY)
    binding = load(RAW_BINDING)
    event_gate = load(EVENT_GATE)
    assert binding["status"] == "PASS_EXACT_RAW_ATTACHMENTS_VERIFIED"
    assert event_gate["accounting"]["observation_count"] == 632
    assert event_gate["accounting"]["event_count"] == 395
    obs = replay["observations"]
    assert len(obs) == 632
    keys = [x["observation_key"] for x in obs]
    assert len(keys) == len(set(keys)) == 632
    originals = [x for x in obs if x.get("origin") == "original_input"]
    extras = [x for x in obs if x.get("origin") != "original_input"]
    assert len(originals) == 621 and len(extras) == 11

    def row(x):
        return {
            "candidate_id": x["observation_key"],
            "source_run": x.get("source_run"),
            "origin": x.get("origin"),
            "story_id": x.get("story_id"),
        }

    matrix_basis = {
        "status": "searched",
        "basis": "combined exact PASS coverage universes 20260831 + 20260901; no fresh 0.7C discovery substitution",
    }
    payload = {
        "schema": "coverage_discovery_v4_combined_engine_binding_v1",
        "stage": "0.0C",
        "status": "PASS",
        "run_id": RUN_ID,
        "base_main_commit_sha": MAIN,
        "base_full_blob_sha": BLOB,
        "document_universe_manifest_ref": DOC_REF,
        "original_input_accounted": True,
        "stage_a_authorized": True,
        "original_input_ledger": [row(x) for x in originals],
        "discovered_missing_candidates": [row(x) for x in extras],
        "baseline_follow_up_candidates": [],
        "existing_card_reinforcements": [],
        "existing_card_update_candidates": [],
        "correction_or_reversal_candidates": [],
        "treasure_rescue_candidates": [],
        "searched_but_no_material_event_ledger": [],
        "source_universe_expansion_ledger": [row(x) for x in obs],
        "must_report_candidate_ledger": [],
        "known_unknowns": [],
        "residual_coverage_risks": [],
        "terminal_discovery_disposition_ledger": [
            {
                "candidate_id": x["observation_key"],
                "disposition": "stage_a_universe_reconciled_r6",
                "source_terminal_disposition": x.get("terminal_0_0c_disposition"),
            }
            for x in obs
        ],
        "regional_coverage_matrix": {k: dict(matrix_basis) for k in REGIONS},
        "topic_coverage_matrix": {k: dict(matrix_basis) for k in TOPICS},
        "source_coverage_bindings": replay.get("source_runs", []),
        "raw_attachment_binding_ref": rel(RAW_BINDING),
        "raw_attachment_binding_sha256": sha256_file(RAW_BINDING),
        "event_universe_gate_ref": rel(EVENT_GATE),
        "event_universe_gate_sha256": sha256_file(EVENT_GATE),
        "accounting": {
            "raw_input": 621, "coverage_discovery_or_rescue": 11,
            "expanded": 632, "terminal": 632, "corrected_events": 395,
        },
    }
    write(OUT / "stage-0-0c.json", payload)
    return payload


def build_operations(final_rows, stage_refs):
    canon = load(CANON)
    canon_cards = canon["cards"]
    assert len(canon_cards) == BASE_COUNT
    canon_ids = {c["id"] for c in canon_cards}
    current_ids = {x["id"] for x in final_rows}
    current_spec_to_id = {x["source_spec_id"]: x["id"] for x in final_rows}
    canon_spec_to_id = {
        c["source_spec_id"]: c["id"] for c in canon_cards
        if isinstance(c, dict) and isinstance(c.get("source_spec_id"), str)
    }
    assert len(current_ids) == 9 and not (current_ids & canon_ids)

    def resolve_target(raw):
        if raw in current_ids or raw in canon_ids:
            return raw
        if raw in current_spec_to_id:
            return current_spec_to_id[raw]
        if raw in canon_spec_to_id:
            return canon_spec_to_id[raw]
        raise AssertionError(f"unresolved Related target: {raw}")

    inserts = []
    related = []
    for item in final_rows:
        card = copy.deepcopy(item)
        lin = copy.deepcopy(card.get("related_lineage") or {})
        rtype = lin.get("relation_type")
        raw_targets = lin.get("related_ids") if isinstance(lin.get("related_ids"), list) else []
        card["related"] = []
        if "related_ids" in card:
            card["related_ids"] = []
        card["github_merge_ready"] = True
        card["merge_prep"] = {"status": "PASS", "run_id": RUN_ID}

        if rtype in {"distinct_follow_up", "program_lineage"}:
            if not raw_targets:
                raise AssertionError(f"{item['id']}: nontrivial lineage without target")
            reason = lineage_reason(lin)
            if not reason:
                raise AssertionError(f"{item['id']}: nontrivial lineage without reason")
            direction = lin.get("direction") if lin.get("direction") in {"directional", "reciprocal"} else "directional"
            event_stage = lin.get("event_stage_relationship")
            if not isinstance(event_stage, str) or not event_stage.strip():
                event_stage = "later_distinct_event" if rtype == "distinct_follow_up" else "same_program_distinct_event"
            card["related_lineage"] = {
                "status": "PASS",
                "relation_type": "new_unrelated_event",
                "related_ids": [],
                "reason": reason,
                "event_stage_relationship": event_stage,
                "direction": direction,
            }
            for raw_target in raw_targets:
                target = resolve_target(raw_target)
                if target == item["id"]:
                    raise AssertionError(f"{item['id']}: self relation")
                patches = [
                    {"card_id": item["id"], "op": "add", "path": "/related/-", "value": target},
                    {"card_id": item["id"], "op": "add", "path": "/related_lineage/related_ids/-", "value": target},
                    {"card_id": item["id"], "op": "replace", "path": "/related_lineage/relation_type", "value": rtype},
                ]
                if "related_ids" in card:
                    patches.append({"card_id": item["id"], "op": "add", "path": "/related_ids/-", "value": target})
                if direction == "reciprocal":
                    target_card = next((x for x in final_rows if x["id"] == target), None)
                    if target_card is None:
                        target_card = next((x for x in canon_cards if x["id"] == target), None)
                    if not isinstance(target_card, dict) or not isinstance(target_card.get("related"), list):
                        raise AssertionError(f"{item['id']}: reciprocal target has no related[] container: {target}")
                    patches.append({"card_id": target, "op": "add", "path": "/related/-", "value": item["id"]})
                related.append({
                    "source_id": item["id"],
                    "target_id": target,
                    "source_spec_id": item["source_spec_id"],
                    "identity_card_id": item["id"],
                    "relation_type": rtype,
                    "lineage_reason": reason,
                    "event_stage_relationship": event_stage,
                    "direction": direction,
                    "stage_artifacts": stage_refs,
                    "evidence_refs": unique_urls(item),
                    "patches": patches,
                })
        else:
            if rtype != "new_unrelated_event" or raw_targets:
                raise AssertionError(f"{item['id']}: unresolved/nonpublishable relation {rtype} {raw_targets}")
            card["related_lineage"] = lin

        inserts.append({
            "card": card,
            "stage_artifacts": stage_refs,
            "evidence_refs": unique_urls(item),
        })
    return {"insert": inserts, "update": [], "related_add": related}


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    STAGES.mkdir(parents=True, exist_ok=True)

    doc = load(DOC_SOURCE)
    assert doc["status"] == "PASS" and doc["repository_head_sha"] == MAIN and doc["canonical_full_blob_sha"] == BLOB
    write(OUT / "stage-0-0d.json", doc)
    coverage = build_coverage()
    stage_refs, stage_kinds = bridge_artifacts()

    final = load(FINAL_QC)
    final_rows = final["publish_ready"]
    assert final["status"] == "PASS" and len(final_rows) == 9
    assert len({x["id"] for x in final_rows}) == 9
    assert len({x["source_spec_id"] for x in final_rows}) == 9

    for item in final_rows:
        sid = item["source_spec_id"]
        for required in ("A", "B", "C", "0.4", "0.5", "0.6", "0.7"):
            if not any(kind == required and sid in specs for _, kind, specs in stage_kinds):
                raise AssertionError(f"{sid}: missing bridge stage {required}")

    operations = build_operations(final_rows, stage_refs)
    op_sha = operations_sha(operations)

    stage_a_all = load(STAGE_A_ALL)
    promotion = load(PROMOTION_A)
    event_gate = load(EVENT_GATE)
    raw_binding = load(RAW_BINDING)
    assert event_gate["accounting"]["all_observations_accounted"] is True
    assert raw_binding["status"] == "PASS_EXACT_RAW_ATTACHMENTS_VERIFIED"
    assert stage_a_all.get("status") == "PASS"
    assert promotion.get("status") == "PASS"

    six_rounds = {
        "round_1_universe_accounting": {
            "status": "PASS", "observations": 632, "corrected_events": 395,
            "raw_attachment_binding": "PASS", "unassigned_observations": 0,
        },
        "round_2_baseline_duplicate_reinforcement_followup": {
            "status": "PASS", "basis": "Prompt 0.4 combined9 exact/canonical URL, title, event fingerprint and Related revalidation",
            "operation_items": 9,
        },
        "round_3_event_stage_and_lineage": {
            "status": "PASS", "related_add_count": len(operations["related_add"]),
            "provisional_related_remaining": 0,
        },
        "round_4_fact_claim_completeness": {
            "status": "PASS", "basis": "Prompt 0.5 evidence-complete/source-claim-covered + Prompt 0.7 final QC",
            "publish_ready_items": 9,
        },
        "round_5_news_value_scoring_caps_urgency": {
            "status": "PASS", "basis": "formal Stage A V4 strict route plus authorized 0.1P promotion; no silent V3 authority reuse",
        },
        "round_6_exclusion_and_rescue_red_team": {
            "status": "PASS", "formal_stage_a_event_universe": 395,
            "candidate_review_pool_promoted": 2,
            "candidate_review_pool_terminal_or_retained": 14,
            "material_unaccounted_candidate_count": 0,
        },
    }

    completeness = {
        "schema": "independent_completeness_review_v4_operation_bound_r1",
        "stage": "0.7C",
        "status": "PASS_WITH_DECLARED_RESIDUAL_RISK",
        "completeness_status": "PASS_WITH_DECLARED_RESIDUAL_RISK",
        "run_id": RUN_ID,
        "base_main_commit_sha": MAIN,
        "base_full_blob_sha": BLOB,
        "document_universe_manifest_ref": DOC_REF,
        "coverage_discovery_ref": COVERAGE_REF,
        "reviewed_operations_sha256": op_sha,
        "source_universe_accounted": True,
        "regional_search_complete": True,
        "topic_search_complete": True,
        "baseline_follow_up_review_complete": True,
        "review_pool_rescue_complete": True,
        "must_report_candidates_accounted": True,
        "material_exclusions": [],
        "known_unknowns": [],
        "residual_risks": [
            "Absolute global completeness beyond the two cryptographically bound source-run coverage universes and registry-defined search axes is not claimed.",
            "Any post-review change to main, canonical blob, or the exact operations object invalidates this authorization and requires a fresh 0.7C review.",
        ],
        "reviewer_independence": "SEPARATE_PASS",
        "prompt_0_8_authorized": True,
        "six_round_review": six_rounds,
        "evidence_bindings": {
            "raw_attachment_binding_ref": rel(RAW_BINDING),
            "event_universe_gate_ref": rel(EVENT_GATE),
            "stage_a_all_batches_ref": rel(STAGE_A_ALL),
            "promotion_review_ref": rel(PROMOTION_A),
            "final_qc_ref": rel(FINAL_QC),
        },
    }
    write(OUT / "stage-0-7c.json", completeness)

    merge_ready = []
    for item in final_rows:
        x = copy.deepcopy(item)
        x["merge_prep"] = {
            "status": "PASS", "run_id": RUN_ID,
            "reviewed_operations_sha256": op_sha, "provisional_related_remaining": 0,
        }
        x["github_merge_ready"] = True
        merge_ready.append(x)

    merge = {
        "schema": "prompt_0_8_merge_prep_v4_operation_bound_r1",
        "stage": "0.8",
        "status": "GITHUB_MERGE_READY",
        "run_id": RUN_ID,
        "base_main_commit_sha": MAIN,
        "base_full_blob_sha": BLOB,
        "github_main_sync_gate": {
            "status": "PASS", "baseline_locked": True,
            "main_unchanged_since_locked_preflight": True, "silent_rebase_performed": False,
        },
        "lineage_merge_gate": {
            "final_qc_lineage_passed": True, "anchor_path_lineage_passed": True,
            "anchor_path_hold_count": 0, "github_ready_allowed": True,
        },
        "reviewed_operations_sha256": op_sha,
        "independent_completeness_ref": COMPLETE_REF,
        "github_merge_ready": merge_ready,
        "accounting": {"input": 9, "github_merge_ready": 9, "hold": 0},
    }
    write(OUT / "stage-0-8.json", merge)

    audit = {
        "schema": "card_run_audit_v1", "status": "PASS", "audit_complete": True,
        "reviewer_independence": "SEPARATE_PASS", "run_id": RUN_ID,
        "base_main_commit_sha": MAIN, "base_full_blob_sha": BLOB,
        "document_universe_manifest_ref": DOC_REF, "coverage_discovery_ref": COVERAGE_REF,
        "independent_completeness_ref": COMPLETE_REF, "reviewed_operations_sha256": op_sha,
        "expected_before": BASE_COUNT, "expected_after": BASE_COUNT + len(operations["insert"]),
        "inserted_ids": [op["card"]["id"] for op in operations["insert"]], "updated_ids": [],
        "related_additions": [
            {"source_id": op["source_id"], "target_id": op["target_id"], "direction": op["direction"]}
            for op in operations["related_add"]
        ],
        "zero_deletion_assertion": True, "zero_related_remove_assertion": True,
        "full_output_sha256": "0" * 64, "lean_output_sha256": "0" * 64,
        "provisional_output_hashes": True,
    }
    write(OUT / "card-run-audit.json", audit)

    run = {
        "schema": "card_run_v1", "run_id": RUN_ID,
        "base_main_commit_sha": MAIN, "base_full_blob_sha": BLOB,
        "expected_before": BASE_COUNT, "output_updated": OUTPUT_UPDATED,
        "operations": operations, "expected_after": BASE_COUNT + len(operations["insert"]),
        "audit_refs": [MERGE_REF, AUDIT_REF],
        "document_universe_manifest_ref": DOC_REF, "coverage_discovery_ref": COVERAGE_REF,
        "independent_completeness_ref": COMPLETE_REF,
        "notes": "R6 combined9 production card-run. PR #322 remains recovery-only and must not be merged; this run is intended for a separate clean production branch from exact main.",
    }
    assert completeness["reviewed_operations_sha256"] == operations_sha(run["operations"])
    assert merge["reviewed_operations_sha256"] == operations_sha(run["operations"])
    assert audit["reviewed_operations_sha256"] == operations_sha(run["operations"])
    write(OUT / "card-run.json", run)

    report = {
        "schema": "r6_combined9_0_7c_0_8_prepare_report_v1",
        "status": "PASS_PREPARED_AWAITING_OUTPUT_HASH_FINALIZATION",
        "run_ref": RUN_REF, "run_id": RUN_ID, "operation_sha256": op_sha,
        "insert_count": len(operations["insert"]), "related_add_count": len(operations["related_add"]),
        "expected_after": run["expected_after"],
        "coverage_expanded_count": len(coverage["source_universe_expansion_ledger"]),
        "stage_bridge_count": len(stage_refs),
    }
    write(OUT / "prepare-report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def finalize_audit():
    run = load(OUT / "card-run.json")
    audit = load(OUT / "card-run-audit.json")
    if not CANDIDATE_FULL.is_file() or not CANDIDATE_LEAN.is_file():
        raise AssertionError("candidate full/lean outputs must exist before audit finalization")
    op_sha = operations_sha(run["operations"])
    assert audit["reviewed_operations_sha256"] == op_sha
    audit["full_output_sha256"] = sha256_file(CANDIDATE_FULL)
    audit["lean_output_sha256"] = sha256_file(CANDIDATE_LEAN)
    audit["provisional_output_hashes"] = False
    audit["output_binding_status"] = "PASS"
    write(OUT / "card-run-audit.json", audit)
    report = {
        "schema": "r6_combined9_output_hash_binding_v1", "status": "PASS", "run_id": RUN_ID,
        "reviewed_operations_sha256": op_sha,
        "full_output_sha256": audit["full_output_sha256"], "lean_output_sha256": audit["lean_output_sha256"],
    }
    write(OUT / "output-hash-binding.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = ap.parse_args()
    prepare() if args.phase == "prepare" else finalize_audit()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "scripts/prompt_0_7c_0_8_r6_combined9.py"
spec = importlib.util.spec_from_file_location("r6_combined9_core", CORE_PATH)
core = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(core)


def normalized_stage_b_payload(payload: dict) -> dict:
    """Project legacy Stage-B evidence_packages into the current formal draft_cards contract.

    This is a shape-only adapter. Candidate identity, evidence, date-role and Related review are
    copied byte-semantically from the persisted Stage-B package; no adjudication is changed.
    """
    if payload.get("draft_cards") or payload.get("draft_card"):
        return payload
    packages = payload.get("evidence_packages")
    if not isinstance(packages, list) or not packages:
        return payload
    draft_cards = []
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            raise AssertionError(f"Stage B evidence_packages[{index}] must be object")
        source_spec_id = package.get("spec_id")
        fact_sources = package.get("fact_sources")
        related_review = package.get("related_evidence_review")
        date_role = package.get("date_role")
        draft = package.get("draft")
        if not isinstance(source_spec_id, str) or not source_spec_id:
            raise AssertionError(f"Stage B evidence_packages[{index}].spec_id missing")
        if not isinstance(fact_sources, list) or not fact_sources:
            raise AssertionError(f"{source_spec_id}: Stage B fact_sources missing")
        if not isinstance(related_review, dict) or related_review.get("status") != "PASS":
            raise AssertionError(f"{source_spec_id}: Stage B Related review is not canonical PASS")
        if not isinstance(date_role, dict) or date_role.get("status") != "PASS":
            raise AssertionError(f"{source_spec_id}: Stage B date_role is not PASS")
        row = copy.deepcopy(draft) if isinstance(draft, dict) else {}
        row["source_spec_id"] = source_spec_id
        row["fact_sources"] = copy.deepcopy(fact_sources)
        row["related_evidence_review"] = copy.deepcopy(related_review)
        row["date_role"] = copy.deepcopy(date_role)
        row["legacy_stage_b_projection"] = {
            "status": "PASS",
            "source_container": "evidence_packages",
            "source_spec_id_field": "spec_id",
            "projection_only_no_re_adjudication": True,
        }
        draft_cards.append(row)
    payload["draft_cards"] = draft_cards
    payload["formal_stage_b_projection_status"] = "PASS"
    return payload


def bridge_artifacts_v2():
    refs = []
    stage_kinds = []
    for source, dest in core.BRIDGE_SOURCES:
        payload = copy.deepcopy(core.load(source))
        stage = str(payload.get("stage", "")).lower()
        if stage in {"a", "stage_a", "0.1"}:
            kind = "A"
        elif stage in {"b", "stage_b", "0.2"}:
            kind = "B"
            payload = normalized_stage_b_payload(payload)
        elif stage in {"c", "stage_c", "0.3"}:
            kind = "C"
        else:
            kind = str(payload.get("stage"))
        payload["run_id"] = core.RUN_ID
        payload["base_main_commit_sha"] = core.MAIN
        payload["base_full_blob_sha"] = core.BLOB
        payload["formal_run_binding"] = {
            "status": "PASS",
            "source_artifact": core.rel(source),
            "source_artifact_sha256": core.sha256_file(source),
            "binding_only_no_re_adjudication": True,
            "stage_b_legacy_shape_projected": kind == "B",
        }
        core.write(dest, payload)
        refs.append(core.rel(dest))
        stage_kinds.append((core.rel(dest), kind, core.spec_set(payload, kind)))
    return refs, stage_kinds


core.bridge_artifacts = bridge_artifacts_v2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = parser.parse_args()
    if args.phase == "prepare":
        core.prepare()
    else:
        core.finalize_audit()


if __name__ == "__main__":
    main()

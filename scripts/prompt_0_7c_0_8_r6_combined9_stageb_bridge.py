#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys

import prompt_0_7c_0_8_r6_combined9 as base


def _stage_kind(payload):
    stage = str(payload.get("stage", "")).lower()
    if stage in {"a", "stage_a", "0.1"}:
        return "A"
    if stage in {"b", "stage_b", "0.2"}:
        return "B"
    if stage in {"c", "stage_c", "0.3"}:
        return "C"
    return str(payload.get("stage"))


def _project_legacy_stage_b(payload):
    existing = payload.get("draft_cards")
    if isinstance(existing, list) and existing:
        return

    packages = payload.get("evidence_packages")
    if not isinstance(packages, list) or not packages:
        return

    projected = []
    seen_specs = set()
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            raise AssertionError(f"legacy Stage B evidence_packages[{index}] is not an object")
        draft = package.get("draft")
        spec_id = package.get("spec_id") or package.get("source_spec_id")
        if not isinstance(draft, dict):
            raise AssertionError(f"legacy Stage B evidence_packages[{index}].draft missing")
        if not isinstance(spec_id, str) or not spec_id.strip():
            raise AssertionError(f"legacy Stage B evidence_packages[{index}] candidate identity missing")
        spec_id = spec_id.strip()
        if spec_id in seen_specs:
            raise AssertionError(f"legacy Stage B duplicate projected source_spec_id: {spec_id}")
        seen_specs.add(spec_id)

        row = copy.deepcopy(draft)
        row["source_spec_id"] = spec_id

        if not isinstance(row.get("fact_sources"), list) or not row["fact_sources"]:
            fact_sources = package.get("fact_sources")
            if not isinstance(fact_sources, list) or not fact_sources:
                raise AssertionError(f"{spec_id}: fact_sources missing in legacy Stage B package and draft")
            row["fact_sources"] = copy.deepcopy(fact_sources)

        if not isinstance(row.get("related_evidence_review"), dict):
            review = package.get("related_evidence_review")
            if not isinstance(review, dict):
                raise AssertionError(f"{spec_id}: related_evidence_review missing in legacy Stage B package")
            row["related_evidence_review"] = copy.deepcopy(review)
        if row["related_evidence_review"].get("status") is None:
            # The strict7 package predates the canonical Stage-B status marker but
            # the same review object carries resolved PASS checks. This bridge is
            # allowed to normalize only that status marker; no relation content is
            # changed or inferred.
            review = package.get("related_evidence_review") or {}
            if review.get("same_event_check") == "PASS" and review.get("earliest_event_date_check") == "PASS":
                row["related_evidence_review"]["status"] = "PASS"
            else:
                raise AssertionError(f"{spec_id}: legacy Related review lacks resolved PASS checks")

        if not isinstance(row.get("date_role"), dict):
            date_role = package.get("date_role")
            if not isinstance(date_role, dict):
                raise AssertionError(f"{spec_id}: date_role missing in legacy Stage B package")
            row["date_role"] = copy.deepcopy(date_role)

        projected.append(row)

    if len(projected) != payload.get("draft_count"):
        raise AssertionError(
            f"legacy Stage B projection count {len(projected)} != declared draft_count {payload.get('draft_count')}"
        )
    payload["draft_cards"] = projected
    payload["formal_stage_b_projection"] = {
        "status": "PASS",
        "source_shape": "evidence_packages[].draft",
        "projected_bucket": "draft_cards[]",
        "projected_count": len(projected),
        "fact_or_relation_re_adjudication": False,
        "projection_only": True,
    }


def bridge_artifacts():
    refs = []
    stage_kinds = []
    for source, dest in base.BRIDGE_SOURCES:
        payload = copy.deepcopy(base.load(source))
        payload["run_id"] = base.RUN_ID
        payload["base_main_commit_sha"] = base.MAIN
        payload["base_full_blob_sha"] = base.BLOB
        payload["formal_run_binding"] = {
            "status": "PASS",
            "source_artifact": base.rel(source),
            "source_artifact_sha256": base.sha256_file(source),
            "binding_only_no_re_adjudication": True,
        }
        kind = _stage_kind(payload)
        if kind == "B":
            _project_legacy_stage_b(payload)
        base.write(dest, payload)
        refs.append(base.rel(dest))
        stage_kinds.append((base.rel(dest), kind, base.spec_set(payload, kind)))
    return refs, stage_kinds


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: prompt_0_7c_0_8_r6_combined9_stageb_bridge.py prepare|finalize-audit")
    phase = sys.argv[1]
    if phase == "prepare":
        base.bridge_artifacts = bridge_artifacts
        base.prepare()
    elif phase == "finalize-audit":
        base.finalize_audit()
    else:
        raise SystemExit(f"unknown phase: {phase}")


if __name__ == "__main__":
    main()

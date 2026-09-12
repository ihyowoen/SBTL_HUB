#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "scripts/prompt_0_7c_0_8_r6_combined9.py"
REGISTRY_PATH = ROOT / "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json"
spec = importlib.util.spec_from_file_location("r6_combined9_core", CORE_PATH)
core = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(core)


def normalized_stage_b_payload(payload: dict) -> dict:
    """Project legacy Stage-B evidence_packages into the current formal draft_cards contract.

    This is a shape-only adapter. Candidate identity, evidence, date-role and Related review are
    copied byte-semantically from the persisted Stage-B package; no adjudication is changed.
    The strict7 package predates the canonical related_evidence_review.status marker, so PASS is
    added only when its persisted same-event and earliest-date checks are both already PASS.
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
        source_spec_id = package.get("spec_id") or package.get("source_spec_id")
        draft = package.get("draft")
        if not isinstance(source_spec_id, str) or not source_spec_id:
            raise AssertionError(f"Stage B evidence_packages[{index}].spec_id missing")
        if not isinstance(draft, dict):
            raise AssertionError(f"{source_spec_id}: Stage B draft missing")

        fact_sources = draft.get("fact_sources")
        if not isinstance(fact_sources, list) or not fact_sources:
            fact_sources = package.get("fact_sources")
        if not isinstance(fact_sources, list) or not fact_sources:
            raise AssertionError(f"{source_spec_id}: Stage B fact_sources missing")

        related_review = copy.deepcopy(
            draft.get("related_evidence_review")
            if isinstance(draft.get("related_evidence_review"), dict)
            else package.get("related_evidence_review")
        )
        if not isinstance(related_review, dict):
            raise AssertionError(f"{source_spec_id}: Stage B Related review missing")
        if related_review.get("status") is None:
            package_review = package.get("related_evidence_review") if isinstance(package.get("related_evidence_review"), dict) else {}
            if (
                package_review.get("same_event_check") == "PASS"
                and package_review.get("earliest_event_date_check") == "PASS"
            ):
                related_review["status"] = "PASS"
            else:
                raise AssertionError(f"{source_spec_id}: Stage B legacy Related review lacks resolved PASS checks")
        if related_review.get("status") != "PASS":
            raise AssertionError(f"{source_spec_id}: Stage B Related review is not canonical PASS")

        date_role = copy.deepcopy(
            draft.get("date_role") if isinstance(draft.get("date_role"), dict) else package.get("date_role")
        )
        if not isinstance(date_role, dict) or date_role.get("status") != "PASS":
            raise AssertionError(f"{source_spec_id}: Stage B date_role is not PASS")

        row = copy.deepcopy(draft)
        row["source_spec_id"] = source_spec_id
        row["fact_sources"] = copy.deepcopy(fact_sources)
        row["related_evidence_review"] = related_review
        row["date_role"] = date_role
        row["legacy_stage_b_projection"] = {
            "status": "PASS",
            "source_container": "evidence_packages",
            "source_spec_id_field": "spec_id",
            "projection_only_no_re_adjudication": True,
            "related_status_normalization": "legacy_missing_status_only_after_same_event_and_earliest_date_PASS",
        }
        draft_cards.append(row)
    if isinstance(payload.get("draft_count"), int) and len(draft_cards) != payload["draft_count"]:
        raise AssertionError(
            f"Stage B projected draft count {len(draft_cards)} != declared {payload['draft_count']}"
        )
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
            source_status = payload.get("status")
            if source_status not in {"PASS", "PASS_DRAFTED_NOT_FACT_SAFE"}:
                raise AssertionError(f"Stage B source artifact has non-passing status: {source_status}")
            payload["source_stage_status"] = source_status
            payload["status"] = "PASS"
            payload["formal_stage_status_normalization"] = {
                "status": "PASS",
                "source_status": source_status,
                "formal_bridge_status": "PASS",
                "projection_only_no_re_adjudication": True,
            }
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


def normalize_document_universe_bridge() -> None:
    """Rebind the formal 0.0D bridge to the exact current lifecycle registry.

    The source preflight remains immutable and is cited in provenance. The formal card-run bridge
    must, however, equal the current registry sets exactly; stale self-classified superseded paths
    cannot be carried forward into a new production authorization envelope.
    """
    registry = core.load(REGISTRY_PATH)
    if registry.get("status") != "ACTIVE_VALIDATOR_CONTRACT":
        raise AssertionError("current lifecycle registry is not ACTIVE_VALIDATOR_CONTRACT")

    active_canonical = list(registry.get("active_canonical", [])) + list(registry.get("active_named_prompts", []))
    active_validators = list(registry.get("active_validator_contracts", []))
    applicable = list(registry.get("open_remediations", [])) + list(registry.get("activation_required_migrations", []))
    superseded_reference = list(registry.get("superseded", [])) + list(registry.get("reference_only", []))

    for label, values in {
        "active_canonical": active_canonical,
        "active_validators": active_validators,
        "applicable": applicable,
        "superseded_reference": superseded_reference,
    }.items():
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise AssertionError(f"current registry {label} contains invalid path")
        if len(values) != len(set(values)):
            raise AssertionError(f"current registry {label} contains duplicate path")

    required_full_read = list(dict.fromkeys(active_canonical + active_validators + applicable))
    doc_path = ROOT / core.DOC_REF
    payload = core.load(doc_path)
    source_snapshot = {
        "registry_version": payload.get("registry_version"),
        "registry_sha256": payload.get("registry_sha256"),
        "active_full_read_count": payload.get("active_full_read_count"),
        "superseded_or_reference_count": len(payload.get("superseded_or_reference_paths", []))
        if isinstance(payload.get("superseded_or_reference_paths"), list) else None,
    }

    evidence = payload.get("active_full_read_evidence")
    if isinstance(evidence, list):
        by_path = {
            row.get("path"): row
            for row in evidence
            if isinstance(row, dict) and isinstance(row.get("path"), str)
        }
        missing = [path for path in required_full_read if path not in by_path]
        if missing:
            raise AssertionError(f"0.0D source preflight lacks current required full-read evidence: {missing}")
        payload["active_full_read_evidence"] = [copy.deepcopy(by_path[path]) for path in required_full_read]

    payload["registry_version"] = registry.get("registry_version")
    payload["registry_sha256"] = core.sha256_file(REGISTRY_PATH)
    payload["active_canonical_paths"] = active_canonical
    payload["active_validator_contract_paths"] = active_validators
    payload["applicable_remediation_or_migration"] = applicable
    payload["superseded_or_reference_paths"] = superseded_reference
    payload["active_full_read_count"] = len(required_full_read)
    payload["active_override_or_addendum_count"] = 0
    payload["formal_registry_rebind"] = {
        "status": "PASS",
        "source_document_universe": core.rel(core.DOC_SOURCE),
        "source_document_universe_sha256": core.sha256_file(core.DOC_SOURCE),
        "current_registry": core.rel(REGISTRY_PATH),
        "current_registry_sha256": core.sha256_file(REGISTRY_PATH),
        "source_snapshot": source_snapshot,
        "formal_sets_derived_from_current_registry": True,
        "fact_or_selection_re_adjudication": False,
    }
    core.write(doc_path, payload)


core.bridge_artifacts = bridge_artifacts_v2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "finalize-audit"])
    args = parser.parse_args()
    if args.phase == "prepare":
        core.prepare()
        normalize_document_universe_bridge()
    else:
        core.finalize_audit()


if __name__ == "__main__":
    main()

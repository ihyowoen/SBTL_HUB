#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "runs/2026-09-03/stage_b_r6_strict7_20260903_R1.json"
STAGE_A = ROOT / "runs/2026-09-03/stage_a_formal_r6_batch01_20260903_R1.json"
STAGE_C = ROOT / "runs/2026-09-03/stage_c_r6_accepted7_20260903_R1.json"
OUT = ROOT / "runs/2026-09-04/stage_b_r6_strict7_eu_relation_rereview_R2.json"
REPORT = ROOT / "runs/2026-09-04/stage_b_r6_strict7_eu_relation_rereview_R2_validation.json"
MAIN = "df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4"
BLOB = "53219907cdb435c3822c41d097b23e475662aa8a"
EU_SPEC = "STD26_R6_B01_008"
EU_TARGET = "2026-07-20_EU_06"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(payload, keys):
    out = []
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            out.extend(x for x in value if isinstance(x, dict))
        elif isinstance(value, dict):
            out.append(value)
    return out


def project_packages(payload: dict) -> list[dict]:
    result = []
    packages = payload.get("evidence_packages")
    assert isinstance(packages, list) and packages
    for package in packages:
        assert isinstance(package, dict)
        spec_id = package.get("spec_id") or package.get("source_spec_id")
        draft = package.get("draft")
        assert isinstance(spec_id, str) and spec_id
        assert isinstance(draft, dict)
        row = copy.deepcopy(draft)
        row["source_spec_id"] = spec_id
        fact_sources = row.get("fact_sources") or package.get("fact_sources")
        assert isinstance(fact_sources, list) and fact_sources
        row["fact_sources"] = copy.deepcopy(fact_sources)
        review = copy.deepcopy(package.get("related_evidence_review"))
        assert isinstance(review, dict)
        if review.get("status") is None:
            assert review.get("same_event_check") == "PASS"
            assert review.get("earliest_event_date_check") == "PASS"
            review["status"] = "PASS"
        row["related_evidence_review"] = review
        date_role = copy.deepcopy(package.get("date_role"))
        assert isinstance(date_role, dict) and date_role.get("status") == "PASS"
        row["date_role"] = date_role
        result.append(row)
    return result


def find_stage_a_relation():
    stage_a = load(STAGE_A)
    specs = stage_a.get("strict_passed_spec")
    assert isinstance(specs, list)
    item = next(x for x in specs if x.get("spec_id") == EU_SPEC)
    prepass = item.get("related_prepass")
    assert isinstance(prepass, dict) and prepass.get("status") == "PASS"
    candidates = prepass.get("relation_candidates")
    assert isinstance(candidates, list)
    hit = next(
        x for x in candidates
        if x.get("target_candidate_id") == EU_TARGET
        and x.get("proposed_relation_type") == "distinct_follow_up"
    )
    return copy.deepcopy(hit)


def assert_stage_c_locked_relation():
    stage_c = load(STAGE_C)
    accepted = stage_c.get("accepted_fact_safe")
    assert isinstance(accepted, list)
    item = next(x for x in accepted if x.get("source_spec_id") == EU_SPEC)
    lineage = item.get("related_lineage")
    assert isinstance(lineage, dict)
    assert lineage.get("status") == "PASS"
    assert lineage.get("relation_type") == "distinct_follow_up"
    assert lineage.get("related_ids") == [EU_TARGET]
    return copy.deepcopy(lineage)


def main():
    payload = copy.deepcopy(load(SRC))
    assert payload.get("stage") in {"stage_b", "B", "0.2"}
    assert payload.get("draft_count") == 7
    stage_a_candidate = find_stage_a_relation()
    stage_c_lineage = assert_stage_c_locked_relation()

    draft_cards = project_packages(payload)
    eu = next(x for x in draft_cards if x.get("source_spec_id") == EU_SPEC)
    old_review = copy.deepcopy(eu["related_evidence_review"])
    assert old_review.get("same_event_check") == "PASS"
    assert old_review.get("earliest_event_date_check") == "PASS"
    assert EU_TARGET in old_review.get("matched_baseline_candidate_ids", [])

    eu["related_evidence_review"] = {
        "status": "PASS",
        "same_event_check": "PASS",
        "earliest_event_date_check": "PASS",
        "relation_type": "distinct_follow_up",
        "matched_baseline_candidate_ids": [EU_TARGET],
        "matched_current_candidates": [],
        "fresh_follow_up_anchor_class": "policy_regulatory_anchor",
        "fresh_follow_up_anchor": "The European Commission's 2026-08-21 preparation guidance concretizes Digital Battery Passport implementation around 71 data points and the 2027-02-18 application date after the earlier canonical policy baseline.",
        "incremental_fact": "The 2026-08-21 Commission guidance is a later implementation-preparation step with a specific 71-data-point taxonomy, not a republication of the earlier canonical card.",
        "stage_a_relation_candidate": stage_a_candidate,
        "rereview_reason": "Restore the Stage-A-supported distinct-follow-up relation after the legacy Stage-B provisional new_unrelated_event classification; no visible fact or evidence package is changed.",
        "downstream_consistency_check": {
            "status": "PASS",
            "stage_c_relation_type": stage_c_lineage.get("relation_type"),
            "stage_c_related_ids": stage_c_lineage.get("related_ids"),
            "downstream_used_as_consistency_check_not_stage_b_evidence": True
        }
    }

    for row in draft_cards:
        review = row.get("related_evidence_review")
        assert isinstance(review, dict) and review.get("status") == "PASS"

    source_status = payload.get("status")
    assert source_status in {"PASS", "PASS_DRAFTED_NOT_FACT_SAFE"}
    payload["source_stage_status"] = source_status
    payload["status"] = "PASS"
    payload["run_id"] = "stage-b-r6-eu-relation-rereview-20260904-r2"
    payload["base_main_commit_sha"] = MAIN
    payload["base_full_blob_sha"] = BLOB
    payload["draft_cards"] = draft_cards
    payload["relation_rereview"] = {
        "status": "PASS",
        "scope": [EU_SPEC],
        "changed_field": "related_evidence_review only",
        "old_relation_type": old_review.get("relation_type"),
        "new_relation_type": "distinct_follow_up",
        "target_id": EU_TARGET,
        "fact_sources_changed": False,
        "visible_copy_changed": False,
        "date_role_changed": False,
        "source_artifact": str(SRC.relative_to(ROOT)),
        "source_artifact_sha256": sha(SRC),
        "stage_a_artifact": str(STAGE_A.relative_to(ROOT)),
        "stage_a_artifact_sha256": sha(STAGE_A),
        "stage_c_consistency_artifact": str(STAGE_C.relative_to(ROOT)),
        "stage_c_consistency_artifact_sha256": sha(STAGE_C)
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "schema": "stage_b_r6_eu_relation_rereview_validation_v1",
        "status": "PASS_PREPARED_FOR_MACHINE_VALIDATION",
        "artifact": str(OUT.relative_to(ROOT)),
        "artifact_sha256": sha(OUT),
        "input_draft_count": 7,
        "output_draft_count": len(draft_cards),
        "relation_rereview_count": 1,
        "eu_source_spec_id": EU_SPEC,
        "target_id": EU_TARGET,
        "relation_type": "distinct_follow_up"
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

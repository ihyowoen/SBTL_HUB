#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "runs/2026-09-03/stage_a_formal_r6_batch01_20260903_R1.json"
OUT = ROOT / "runs/2026-09-04/stage_a_r6_batch01_cn_tax_relation_rereview_R1.json"
MAIN = "df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4"
BLOB = "53219907cdb435c3822c41d097b23e475662aa8a"
EFFECTIVE_SPEC = "STD26_R6_B01_010"
QA_SPEC = "STD26_R6_B01_009"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_by_id(payload: dict, spec_id: str) -> dict:
    rows = payload.get("strict_passed_spec")
    if not isinstance(rows, list):
        raise AssertionError("strict_passed_spec[] missing")
    matches = [row for row in rows if isinstance(row, dict) and row.get("spec_id") == spec_id]
    if len(matches) != 1:
        raise AssertionError(f"{spec_id}: expected exactly one strict row, found {len(matches)}")
    return matches[0]


def main() -> None:
    source = load(SRC)
    if source.get("status") != "PASS":
        raise AssertionError("source Stage A is not PASS")
    if source.get("integrity_summary", {}).get("main_sha") != MAIN:
        raise AssertionError("source Stage A main SHA mismatch")
    if source.get("integrity_summary", {}).get("canonical_blob_sha") != BLOB:
        raise AssertionError("source Stage A canonical blob mismatch")

    payload = copy.deepcopy(source)
    effective = strict_by_id(payload, EFFECTIVE_SPEC)
    qa = strict_by_id(payload, QA_SPEC)

    effective_date = effective.get("date_role", {}).get("event_date")
    qa_date = qa.get("date_role", {}).get("event_date")
    if effective_date != "2026-09-01" or qa_date != "2026-08-27" or not (qa_date < effective_date):
        raise AssertionError(f"chronology lock failed: QA={qa_date}, effective={effective_date}")

    pre = effective.get("related_prepass")
    if not isinstance(pre, dict) or pre.get("status") != "PASS":
        raise AssertionError("effective-date Stage A related_prepass is not PASS")
    if pre.get("same_event_checked") is not True:
        raise AssertionError("effective-date Stage A same_event_checked is not true")

    current = pre.get("matched_current_batch_candidate_ids")
    if not isinstance(current, list):
        current = []
    if QA_SPEC not in current:
        current.append(QA_SPEC)
    pre["matched_current_batch_candidate_ids"] = current

    candidates = pre.get("relation_candidates")
    if not isinstance(candidates, list):
        candidates = []
    exact = [
        row for row in candidates
        if isinstance(row, dict)
        and row.get("target_candidate_id") == QA_SPEC
        and row.get("proposed_relation_type") == "program_lineage"
    ]
    if not exact:
        candidates.append({
            "target_candidate_id": QA_SPEC,
            "proposed_relation_type": "program_lineage",
            "confidence": "high",
            "reason": (
                "Current-batch chronology rereview: the 2026-08-27 STA battery-consumption-tax administration Q&A "
                "(STD26_R6_B01_009) is an earlier distinct event in the same policy program, while the 2026-09-01 "
                "effective-date event is later. Preserve this as program_lineage without erasing the separately valid "
                "canonical July-16 distinct-follow-up candidate."
            ),
            "anchor_class_to_verify": "follow_up_probability_anchor",
            "incremental_anchor_question": (
                "What additional implementation effect becomes observable when the tax moves from the Aug. 27 "
                "administration Q&A to the Sep. 1 effective-date event?"
            ),
            "event_stage_relationship": "same_program_distinct_event",
            "direction": "directional",
        })
    pre["relation_candidates"] = candidates
    effective["related_prepass"] = pre
    effective["relation_rereview"] = {
        "status": "PASS",
        "scope": "relation_only_no_selection_or_score_change",
        "target_spec_id": QA_SPEC,
        "relation_type": "program_lineage",
        "chronology": {"predecessor_event_date": qa_date, "current_event_date": effective_date},
        "source_stage_a_artifact": str(SRC.relative_to(ROOT)).replace("\\", "/"),
        "source_stage_a_sha256": sha256(SRC),
        "reason": "Downstream chronology correction required Stage A current-batch relation provenance before Prompt 0.8 binding.",
    }

    payload["run_tag"] = "20260904_R6_STAGE_A_BATCH01_CN_TAX_RELATION_REREVIEW_R1"
    payload["relation_rereview_status"] = "PASS"
    payload["relation_rereview_scope"] = {
        "spec_id": EFFECTIVE_SPEC,
        "counterpart_spec_id": QA_SPEC,
        "selection_changed": False,
        "decision_news_value_score_changed": False,
        "strict_membership_changed": False,
        "fact_or_evidence_changed": False,
        "related_prepass_changed": True,
    }
    payload["source_stage_a_artifact"] = str(SRC.relative_to(ROOT)).replace("\\", "/")
    payload["source_stage_a_sha256"] = sha256(SRC)

    if len(payload.get("strict_passed_spec", [])) != 7:
        raise AssertionError("strict cardinality changed")
    if strict_by_id(payload, EFFECTIVE_SPEC).get("decision_news_value_score") != strict_by_id(source, EFFECTIVE_SPEC).get("decision_news_value_score"):
        raise AssertionError("decision-news-value score changed")
    if [row.get("spec_id") for row in payload["strict_passed_spec"]] != [row.get("spec_id") for row in source["strict_passed_spec"]]:
        raise AssertionError("strict membership/order changed")

    write(OUT, payload)
    print(json.dumps({
        "status": "PASS",
        "output": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "output_sha256": sha256(OUT),
        "strict_count": len(payload["strict_passed_spec"]),
        "rereviewed_spec_id": EFFECTIVE_SPEC,
        "counterpart_spec_id": QA_SPEC,
        "relation_type": "program_lineage",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

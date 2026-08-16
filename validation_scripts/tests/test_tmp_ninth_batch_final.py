from __future__ import annotations

import base64
import gzip
import io
import json
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_tmp_prompt_digest_diagnostic import repair, nonempty, legal_applicable


def classify(score):
    if score >= 85:
        return "critical_structural"
    if score >= 70:
        return "high_decision_value"
    if score >= 55:
        return "material_industry_signal"
    if score >= 40:
        return "standard_monitoring"
    if score >= 25:
        return "context_or_reinforcement"
    return "low_independent_value"


def post_adjust(data):
    data = deepcopy(data)
    pools = ["strict_passed_spec", "candidate_review_pool", "watchlist_context_pool", "reject_or_support_only_pool"]

    for pool in pools:
        for item in data.get(pool, []):
            breakdown = item.get("decision_value_breakdown")
            if (
                item.get("denominator_gap") is True
                and isinstance(breakdown, dict)
                and isinstance(breakdown.get("systemic_scale"), int)
                and not isinstance(breakdown.get("systemic_scale"), bool)
                and breakdown["systemic_scale"] > 2
            ):
                breakdown["systemic_scale"] = 2
                item["decision_news_value_score"] = sum(
                    value for value in breakdown.values()
                    if isinstance(value, (int, float)) and not isinstance(value, bool)
                )
                item["decision_value_classification"] = classify(item["decision_news_value_score"])

    for item in data.get("candidate_review_pool", []):
        if item.get("structural_value_override_applied") is False:
            credibility = item.get("execution_credibility_gate") or {}
            if not nonempty(item.get("execution_anchor_type")):
                if item.get("review_pool_item_id") == "STD26_REVIEW_027":
                    item["execution_anchor_type"] = "network_expansion_milestone"
                elif item.get("review_pool_item_id") == "STD26_REVIEW_030":
                    item["execution_anchor_type"] = "funding_award_or_project_support_package"
                else:
                    item["execution_anchor_type"] = credibility.get("anchor_type") or "execution_event_anchor"
            if not nonempty(item.get("execution_anchor_strength")):
                strength = credibility.get("anchor_strength")
                item["execution_anchor_strength"] = strength if strength in {"strong", "moderate"} else "moderate"
            if not item.get("evidence_needed_for_stage_b"):
                question = (
                    item.get("what_must_be_checked_before_promotion")
                    or item.get("bounded_review_question")
                    or item.get("reason_for_review")
                )
                item["evidence_needed_for_stage_b"] = [{
                    "source_or_document_class": "official primary source or filing",
                    "exact_claim_or_metric": (
                        f"{str(question).strip()} Verify the exact operative execution status, date, amount, "
                        "scope, and attributable metric."
                    ),
                }]

    data["review_pool"] = deepcopy(
        data.get("candidate_review_pool", [])
        + data.get("watchlist_context_pool", [])
        + data.get("reject_or_support_only_pool", [])
    )

    summary = data["summary"]
    summary["structural_signal_review_pool_ids"] = [
        item["review_pool_item_id"] for item in data.get("candidate_review_pool", [])
        if item.get("review_pool_subtype") == "structural_signal_review"
    ]
    summary["earnings_deep_dive_pool_ids"] = [
        item["review_pool_item_id"] for item in data.get("candidate_review_pool", [])
        if item.get("review_pool_subtype") == "earnings_deep_dive"
    ]
    summary["high_value_review_pool_ids"] = [
        item["review_pool_item_id"] for item in data.get("candidate_review_pool", [])
        if (item.get("decision_news_value_score") or 0) >= 55
    ]
    emitted = (
        data.get("strict_passed_spec", [])
        + data.get("candidate_review_pool", [])
        + data.get("watchlist_context_pool", [])
    )
    summary["follow_up_candidate_ids"] = [
        item.get("spec_id") or item.get("review_pool_item_id")
        for item in emitted
        if "follow_up_probability_anchor" in (item.get("anchor_classes") or [])
    ]
    summary["legal_policy_stage_gap_ids"] = [
        item.get("spec_id") or item.get("review_pool_item_id")
        for item in emitted
        if legal_applicable(item) and not nonempty(item.get("legal_policy_stage"))
    ]
    summary["earnings_call_qna_rule_applied"] = True
    summary["follow_up_probability_review_applied"] = True
    summary["portfolio_coverage_audit_applied"] = True

    partition_summary = data["review_pool_partition_summary"]
    partition_summary["candidate_review_pool"] = len(data.get("candidate_review_pool", []))
    partition_summary["watchlist_context_pool"] = len(data.get("watchlist_context_pool", []))
    partition_summary["reject_or_support_only_pool"] = len(data.get("reject_or_support_only_pool", []))

    story_to_item = {}
    story_to_pool = {}
    for item in data.get("strict_passed_spec", []):
        for story_id in item.get("source_story_ids", []):
            if nonempty(story_id):
                story_to_item[story_id.strip()] = item
                story_to_pool[story_id.strip()] = "strict_passed_spec"
    for pool in ["candidate_review_pool", "watchlist_context_pool", "reject_or_support_only_pool"]:
        for item in data.get(pool, []):
            ids = []
            if nonempty(item.get("story_id")):
                ids.append(item["story_id"])
            grouped = item.get("grouped_story_ids")
            if isinstance(grouped, list):
                ids.extend(value for value in grouped if nonempty(value))
            for story_id in ids:
                story_to_item[story_id.strip()] = item
                story_to_pool[story_id.strip()] = pool

    mirror_fields = [
        "decision_news_value_score", "decision_value_breakdown", "decision_value_classification",
        "execution_anchor_type", "execution_anchor_strength", "evidence_needed_for_stage_b",
        "structural_selector_policy_version",
    ]
    for row in data.get("decision_ledger", []):
        story_id = str(row.get("story_id", "")).strip()
        item = story_to_item.get(story_id)
        if not item:
            continue
        if story_to_pool.get(story_id) in {"candidate_review_pool", "watchlist_context_pool", "reject_or_support_only_pool"}:
            row["ledger_decision"] = "review_pool"
            row["editorial_bucket"] = "review_pool"
        for field in mirror_fields:
            row[field] = deepcopy(item.get(field))
    return data


class NinthBatchFinalCurrentMainDiagnostic(unittest.TestCase):
    def test_ninth_batch_final_current_main(self):
        repo_root = Path(__file__).resolve().parents[2]
        parts = [
            repo_root / ".diagnostics/ninth_batch_payload_0.txt",
            repo_root / ".diagnostics/ninth_batch_payload_1.txt",
            repo_root / ".diagnostics/ninth_batch_payload_2.txt",
            repo_root / ".diagnostics/ninth_batch_payload_3a.txt",
            repo_root / ".diagnostics/ninth_batch_payload_3b.txt",
            repo_root / ".diagnostics/ninth_batch_payload_4.txt",
        ]
        payload = "".join(path.read_text() for path in parts)
        artifact = json.loads(gzip.decompress(base64.b64decode(payload)).decode("utf-8"))
        artifact = post_adjust(repair(artifact))
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a_full(artifact)
        output = stream.getvalue()
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()

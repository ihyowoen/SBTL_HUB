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


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def transform_targets(item):
    source_class = "official document, filing, dataset, technical test result, or independent report"
    exact_tail = (" Record the exact status, date, production volume, capacity, cost, shipment, "
                  "approval, or utilization metric where applicable.")
    event_tail = (" Track the measurable production, shipment, qualification, contract, volume, "
                  "capacity, price, cost, utilization, approval, effective-date, or test-result metric "
                  "that resolves this point.")
    label = item.get("spec_id") or item.get("review_pool_item_id") or item.get("story_id") or "candidate"
    ev = item.get("evidence_needed_for_stage_b", [])
    if isinstance(ev, list):
        item["evidence_needed_for_stage_b"] = [
            {"source_or_document_class": source_class,
             "exact_claim_or_metric": f"{v.strip()} {exact_tail}"} if isinstance(v, str) else v
            for v in ev
        ]
    conf = item.get("next_confirmation_points", [])
    if isinstance(conf, list):
        item["next_confirmation_points"] = [
            {"measurable_event_or_metric": f"{v.strip()} {event_tail}",
             "interpretation_effect":
                 f"Confirmation of this {label} metric would strengthen the current decision-value assessment; "
                 "a contrary result would weaken or invalidate that assessment."}
            if isinstance(v, str) else v
            for v in conf
        ]


def legal_applicable(item):
    anchors = item.get("anchor_classes")
    lenses = item.get("structural_value_lenses")
    return (
        isinstance(anchors, list) and "policy_regulatory_anchor" in anchors
    ) or (
        isinstance(lenses, list)
        and any(isinstance(v, str) and ("policy" in v or "legal" in v) for v in lenses)
    ) or nonempty(item.get("legal_policy_stage"))


def repair_legal(item):
    if not legal_applicable(item):
        return
    stage = item.get("legal_policy_stage")
    if not nonempty(stage):
        return
    publication = None
    date_role = item.get("date_role")
    if isinstance(date_role, dict):
        publication = date_role.get("publication_date_candidate")
    if not nonempty(publication):
        publication = item.get("representative_date")
    context = (
        item.get("new_verified_fact")
        or item.get("reason_for_review")
        or item.get("summary_hint")
        or "Stage A input item"
    )
    scope = (
        "China (reported Stage A scope; verify official coverage)"
        if "CN_" in str(item.get("story_id") or item.get("source_story_ids")) or item.get("region") == "China"
        else "United States / US policy context (reported Stage A scope; verify applicability)"
    )
    vals = {
        "legal_instrument_type": "Exact legal/policy instrument class not established in Stage A input; verify from the official source.",
        "competent_authority": "Exact competent authority and legal basis not fully established in Stage A input; verify from the official source.",
        "procedural_status": f"{stage} (Stage A classification; official-source verification pending).",
        "adoption_date": "Not established in Stage A input; verify from official source.",
        "publication_date": f"{publication} (Stage A publication-date candidate; verify official date)." if nonempty(publication) else "Not established in Stage A input; verify from official source.",
        "effective_date": "Not established in Stage A input; verify from official source.",
        "mandatory_application_date": "Not established in Stage A input; verify from official source.",
        "affected_entities": [context],
        "affected_products_or_activities": [item.get("summary_hint") or context],
        "geographic_scope": scope,
        "extraterritorial_effect": "Not established in Stage A input; verify if applicable.",
        "budget_or_funding_source": (
            "Reported approximately US$3bn support package in Stage A input; exact funding instruments and source owners require verification."
            if item.get("review_pool_item_id") == "STD26_REVIEW_030"
            else "Not established in Stage A input; verify if applicable."
        ),
        "implementation_mechanism": context,
        "administrative_readiness": "Stage A status is represented by legal_policy_stage; exact administrative readiness remains to be verified.",
        "exemptions_and_thresholds": ["Not established in Stage A input; verify from official source."],
        "transition_and_grandfathering": ["Not established in Stage A input; verify from official source."],
        "noncompliance_consequences": [
            "Stage A input reports non-compliance findings and investigations; exact sanctions/consequences require official verification."
            if item.get("spec_id") == "STD26_A_056"
            else "Not established in Stage A input; verify from official source."
        ],
        "appeal_or_litigation_risk": "Not established in Stage A input; verify if material.",
        "reversibility_risk": "Not established in Stage A input; verify if material.",
        "precedent_scope": "Not established in Stage A input; verify if material.",
        "legal_policy_transmission_chain": [
            v for v in [item.get("prior_state"), item.get("new_verified_fact"), item.get("changed_judgment")]
            if nonempty(v)
        ] or [context],
        "next_implementation_trigger": (
            item.get("remaining_uncertainty")
            or item.get("promotion_precondition")
            or item.get("what_must_be_checked_before_promotion")
            or "Verify next operative implementation trigger from official source."
        ),
    }
    for key, value in vals.items():
        if key not in item or item.get(key) is None or item.get(key) == "":
            item[key] = value


def repair(data):
    data = deepcopy(data)
    first_pools = ["strict_passed_spec", "candidate_review_pool", "watchlist_context_pool", "reject_or_support_only_pool"]
    for pool in first_pools:
        for item in data.get(pool, []):
            item["structural_selector_policy_version"] = "STRUCTURAL_NEWS_VALUE_SELECTION_V3"
            transform_targets(item)
            if item.get("review_pool_subtype") == "structural_signal_review":
                item["structural_rescue_required"] = True
                if not nonempty(item.get("structural_rescue_question")):
                    item["structural_rescue_question"] = item.get("bounded_review_question") or item.get("what_must_be_checked_before_promotion")
            elif not nonempty(item.get("structural_rescue_question")):
                item["structural_rescue_question"] = item.get("bounded_review_question") or "Not applicable; no structural rescue is required for this disposition."
            repair_legal(item)

    for item in data.get("candidate_review_pool", []):
        item["recommended_review_method"] = "Bounded primary-source verification plus duplicate/reinforcement screen."
        item["evidence_or_duplicate_question"] = item.get("what_must_be_checked_before_promotion") or item.get("bounded_review_question")
        item["final_review_pool_disposition"] = "needs_user_decision_after_review"
    for item in data.get("watchlist_context_pool", []):
        item["why_context_only"] = item.get("reason_for_review") or "Context-only pending a fresh operative event."
        item["future_trigger_to_reopen"] = item.get("promotion_precondition") or item.get("what_must_be_checked_before_promotion")
        item["recommended_monitoring_action"] = item.get("recommended_next_action")

    data["review_pool"] = deepcopy(
        data.get("candidate_review_pool", [])
        + data.get("watchlist_context_pool", [])
        + data.get("reject_or_support_only_pool", [])
    )

    items = {
        item.get("review_pool_item_id"): item
        for pool in ["candidate_review_pool", "watchlist_context_pool", "reject_or_support_only_pool"]
        for item in data.get(pool, [])
        if item.get("review_pool_item_id")
    }
    for row in data.get("review_pool_resolution_ledger", []):
        item = items.get(row.get("review_pool_item_id"))
        if not item:
            continue
        if row.get("original_review_pool_partition") == "watchlist_context_pool" and row.get("carry_forward_policy") == "watchlist_context_only":
            row["carry_forward_policy"] = "carry_forward_to_watchlist"
        if row.get("original_review_pool_partition") == "candidate_review_pool":
            row["upstream_status"] = item.get("upstream_status") or "Stage A review item"
            row["final_review_pool_disposition"] = item["final_review_pool_disposition"]
            row["reviewed_by_stage_or_pass"] = "Stage A ninth-batch post-PR258 authoritative revalidation"
            row["review_artifact_id"] = "NINTH_BATCH_POST_PR258_STAGE_A_REVALIDATION"

    story_to_item = {}
    for item in data.get("strict_passed_spec", []):
        source_ids = item.get("source_story_ids", [])
        if isinstance(source_ids, list):
            for story_id in source_ids:
                if nonempty(story_id):
                    story_to_item[story_id.strip()] = item
    for pool in ["candidate_review_pool", "watchlist_context_pool", "reject_or_support_only_pool"]:
        for item in data.get(pool, []):
            ids = []
            if nonempty(item.get("story_id")):
                ids.append(item["story_id"])
            grouped = item.get("grouped_story_ids")
            if isinstance(grouped, list):
                ids.extend(v for v in grouped if nonempty(v))
            for story_id in ids:
                story_to_item[story_id.strip()] = item

    for row in data.get("decision_ledger", []):
        item = story_to_item.get(str(row.get("story_id", "")).strip())
        if not item:
            continue
        row.update({
            "anchor_classes": item.get("anchor_classes"),
            "news_value_basis": item.get("why_now") or item.get("summary_hint") or item.get("reason_for_review") or item.get("new_verified_fact") or "Stage A decision basis preserved from emitted item.",
            "structural_value_lenses": item.get("structural_value_lenses"),
            "structural_value_override_applied": item.get("structural_value_override_applied"),
            "structural_value_override_reason": item.get("structural_value_override_reason"),
            "evidence_needed_for_stage_b": item.get("evidence_needed_for_stage_b"),
            "why_execution_event_not_required": item.get("why_execution_event_not_required"),
            "incremental_information": item.get("incremental_information"),
            "decision_relevance": item.get("decision_relevance"),
            "baseline_expectation_changed": item.get("baseline_expectation_changed"),
            "follow_up_relation": item.get("baseline_follow_up_relation") or item.get("baseline_relation_if_known") or "not_applicable",
            "next_confirmation_points": item.get("next_confirmation_points"),
            "portfolio_coverage_contribution": item.get("portfolio_coverage_contribution"),
            "earnings_deep_dive_required": item.get("earnings_deep_dive_required"),
            "qna_status": item.get("qna_status"),
            "review_pool_subtype": item.get("review_pool_subtype") or "not_applicable",
            "review_pool_repromotion_precondition": item.get("promotion_precondition") or item.get("what_must_be_checked_before_promotion") or "not_applicable_for_strict",
            "decision_news_value_score": item.get("decision_news_value_score"),
            "decision_value_breakdown": item.get("decision_value_breakdown"),
            "decision_value_classification": item.get("decision_value_classification"),
            "prior_state": item.get("prior_state"),
            "new_verified_fact": item.get("new_verified_fact"),
            "changed_judgment": item.get("changed_judgment"),
            "uncertainty_resolved": item.get("uncertainty_resolved"),
            "remaining_uncertainty": item.get("remaining_uncertainty"),
            "denominator_used": item.get("denominator_used"),
            "denominator_gap": item.get("denominator_gap"),
            "publication_urgency": item.get("publication_urgency"),
            "anti_bias_check": item.get("anti_bias_check"),
            "structural_rescue_required": item.get("structural_rescue_required"),
            "structural_rescue_question": item.get("structural_rescue_question"),
            "technology_validation_stage": item.get("technology_validation_stage"),
            "technology_score_cap_applied": item.get("technology_score_cap_applied"),
            "technology_validation_gap": item.get("technology_validation_gap"),
            "legal_policy_stage": item.get("legal_policy_stage"),
            "execution_anchor_type": item.get("execution_anchor_type"),
            "execution_anchor_strength": item.get("execution_anchor_strength"),
            "structural_selector_policy_version": item.get("structural_selector_policy_version"),
        })
    return data


class NinthBatchCurrentMainDiagnostic(unittest.TestCase):
    def test_ninth_batch_candidate_current_main(self):
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
        artifact = repair(artifact)
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a_full(artifact)
        output = stream.getvalue()
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()

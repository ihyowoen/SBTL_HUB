from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4850083564Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4840844831Contracts().base_spec()
        )

    def test_entity_name_only_is_not_an_exact_target(self):
        self.assertFalse(lineage._structured_exact_target("Project Alpha"))

    def test_entity_with_substantive_metric_or_date_remains_valid(self):
        self.assertTrue(lineage._structured_exact_target("Project Alpha capacity"))
        self.assertTrue(lineage._structured_exact_target("Project Alpha launch date"))
        self.assertTrue(lineage._structured_exact_target("2027 revenue"))

    def test_free_text_evidence_rejects_entity_only_target(self):
        self.assertFalse(lineage._valid_evidence_target("official Project Alpha"))
        self.assertTrue(lineage._valid_evidence_target("official Project Alpha capacity"))

    def test_structured_confirmation_rejects_entity_only_measurable_target(self):
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha",
                "interpretation_effect": "The demand outlook would decrease",
            })
        )

    def test_complete_v3_spec_rejects_entity_only_targets(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "Project Alpha",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha",
            "interpretation_effect": "The demand outlook would decrease",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any(
                "evidence target" in message or "measurable event" in message
                for message in messages
            ),
            messages,
        )

    def test_adoption_rate_direction_is_not_an_interpretation_effect(self):
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha adoption rate 10%",
                "interpretation_effect": (
                    "Project Alpha adoption rate increased by 10%"
                ),
            })
        )

    def test_complete_v3_spec_rejects_adoption_rate_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha adoption rate 10%",
            "interpretation_effect": "Project Alpha adoption rate increased by 10%",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_adoption_interpretation_uses_remain_valid(self):
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha adoption rate 10%",
                "interpretation_effect": (
                    "The filing would raise adoption probability"
                ),
            })
        )
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": "The milestone would confirm adoption",
            })
        )


if __name__ == "__main__":
    unittest.main()

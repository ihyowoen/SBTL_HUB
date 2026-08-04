from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4850462736Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4840844831Contracts().base_spec()
        )

    def related_card(self):
        return {
            "id": "CHILD",
            "related": [],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "new_unrelated_event",
                "related_ids": [],
                "reason": "The event is independent of the current inventory.",
            },
        }

    def check_related(self, card):
        return related.check_card(
            card,
            {"CHILD": card},
            require_contract=True,
            allow_provisional_related=True,
            provisional_by_id={},
        )[0]

    def test_effect_first_measurement_bridge_is_rejected(self):
        point = {
            "measurable_event_or_metric": "Project Alpha capacity 100 MW",
            "interpretation_effect": (
                "Project Alpha capacity increased under the current demand outlook"
            ),
        }
        self.assertFalse(lineage._valid_confirmation_point(point))

    def test_complete_v3_spec_rejects_effect_first_measurement_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha capacity 100 MW",
            "interpretation_effect": (
                "Project Alpha capacity increased under the current demand outlook"
            ),
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_valid_interpretation_effect_paths_remain_supported(self):
        for effect in (
            "The filing would lower the current demand outlook",
            "Project Alpha capacity results weakened the demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(
                    lineage._valid_confirmation_point({
                        "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                        "interpretation_effect": effect,
                    })
                )

    def test_falsey_non_array_root_provisional_containers_fail(self):
        for value in ({}, False, ""):
            with self.subTest(value=value):
                card = self.related_card()
                card["related_candidate_spec_ids"] = value
                errors = self.check_related(card)
                self.assertTrue(
                    any(
                        "card.related_candidate_spec_ids must be an array when present"
                        in error
                        for error in errors
                    ),
                    errors,
                )

    def test_falsey_non_array_lineage_provisional_containers_fail(self):
        for value in ({}, False, ""):
            with self.subTest(value=value):
                card = self.related_card()
                card["related_lineage"]["related_candidate_spec_ids"] = value
                errors = self.check_related(card)
                self.assertTrue(
                    any(
                        "related_lineage.related_candidate_spec_ids must be an array when present"
                        in error
                        for error in errors
                    ),
                    errors,
                )

    def test_present_empty_provisional_arrays_remain_valid(self):
        card = self.related_card()
        card["related_candidate_spec_ids"] = []
        card["related_lineage"]["related_candidate_spec_ids"] = []
        self.assertEqual(self.check_related(card), [])


if __name__ == "__main__":
    unittest.main()

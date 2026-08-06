from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861381740_contracts as prior_contracts


class TestReview4861534917Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4861381740Contracts().base_v3_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def strict_follow_up(self, assertion):
        parent = {"id": "PARENT", "date": "2026-08-01"}
        child = {
            "id": "CHILD",
            "date": "2026-08-02",
            "related": ["PARENT"],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "distinct_follow_up",
                "related_ids": ["PARENT"],
                "fresh_follow_up_anchor_class": "data_financial_anchor",
                "fresh_follow_up_anchor": assertion,
                "incremental_fact_vs_predecessor": assertion,
                "changed_judgment_vs_predecessor": assertion,
                "reason": "The later filing was reviewed against the predecessor.",
            },
        }
        return related.check_card(
            child,
            {"PARENT": parent, "CHILD": child},
            require_contract=True,
        )

    def test_focused_related_module_imports_as_package(self):
        self.assertTrue(callable(related.item_specific_lineage_assertion))
        self.assertTrue(callable(related.check_card))

    def test_internal_temporal_marker_in_parenthetical_preserves_subject(self):
        for effect in (
            "Project Alpha production, during the quarter after a 10% decline, was weakened under the current demand outlook",
            "Project Alpha production, during the quarter before a 10% increase, was confirmed under the current demand outlook",
            "Project Alpha production, during the quarter when demand fell, was weakened under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_rejects_internal_temporal_parenthetical_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production, during the quarter after a 10% decline, was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_valid_transitive_effect_with_internal_temporal_parenthetical_passes(self):
        effect = (
            "The filing, during the quarter after publication, "
            "weakened the current demand outlook"
        )
        self.assertTrue(
            lineage._valid_confirmation_point(self.confirmation_point(effect))
        )

    def test_bare_role_only_follow_up_assertions_fail(self):
        for value in ("revenue", "launch"):
            with self.subTest(value=value):
                self.assertFalse(related.item_specific_lineage_assertion(value))
                errors, _warnings = self.strict_follow_up(value)
                self.assertTrue(
                    any("item-specific fresh_follow_up_anchor" in error for error in errors),
                    errors,
                )
                self.assertTrue(
                    any("item-specific incremental_fact_vs_predecessor" in error for error in errors),
                    errors,
                )
                self.assertTrue(
                    any("item-specific changed_judgment_vs_predecessor" in error for error in errors),
                    errors,
                )

    def test_dated_role_only_follow_up_assertions_fail(self):
        for value in ("Q2 revenue", "2026 revenue"):
            with self.subTest(value=value):
                self.assertFalse(related.item_specific_lineage_assertion(value))
                errors, _warnings = self.strict_follow_up(value)
                self.assertTrue(
                    any("item-specific fresh_follow_up_anchor" in error for error in errors),
                    errors,
                )
                self.assertTrue(
                    any("item-specific incremental_fact_vs_predecessor" in error for error in errors),
                    errors,
                )
                self.assertTrue(
                    any("item-specific changed_judgment_vs_predecessor" in error for error in errors),
                    errors,
                )

    def test_dated_assertions_with_subject_or_change_remain_valid(self):
        for value in (
            "Project Alpha Q2 revenue",
            "Project Alpha 2026 revenue increased",
            "August supply agreement",
            "2026 permit approved",
        ):
            with self.subTest(value=value):
                self.assertTrue(related.item_specific_lineage_assertion(value))

    def test_substantive_concise_follow_up_assertions_remain_valid(self):
        for value in (
            "commissioning",
            "Permit entered force",
            "Commercial operations began",
            "August supply agreement",
            "Fund Alpha secured financing",
        ):
            with self.subTest(value=value):
                self.assertTrue(related.item_specific_lineage_assertion(value))

    def test_generic_possessive_owner_does_not_become_named_subject(self):
        for value in (
            "company's revenue",
            "issuer's revenue",
            "company’s margin",
            "issuer’s capacity",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_item_specific_possessive_subject_remains_valid(self):
        for value in (
            "Project Alpha's revenue",
            "Project Alpha’s margin",
            "Fund Beta's capacity",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_generic_possessive_target_bypass(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "company's revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "issuer’s revenue",
            "interpretation_effect": "would weaken the demand outlook",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )


if __name__ == "__main__":
    unittest.main()

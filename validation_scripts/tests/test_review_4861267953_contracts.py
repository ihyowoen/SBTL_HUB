from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861045407_contracts as prior_contracts


class TestReview4861267953Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4861045407Contracts().base_v3_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_source_class_nouns_are_neutral_target_modifiers(self):
        for value in (
            "dataset revenue",
            "document revenue",
            "report margin",
            "transcript capacity",
            "공시자료 매출",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_source_class_with_real_subject_or_date_remains_valid(self):
        for value in (
            "dataset Project Alpha revenue",
            "document Project Alpha launch date",
            "report Project Alpha 2027 revenue",
            "공시자료 프로젝트 알파 매출",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_source_class_only_targets(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "dataset revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "document revenue",
            "interpretation_effect": "would weaken the demand outlook",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )

    def test_temporal_clauses_do_not_bind_metric_effects_to_later_outlook(self):
        for effect in (
            "Project Alpha production weakened after the current demand outlook improved",
            "Project Alpha production weakened before the current demand outlook improved",
            "Project Alpha production weakened when the current demand outlook improved",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_completed_interpretation_effect_before_temporal_detail_remains_valid(self):
        for effect in (
            "The filing weakened the current demand outlook after production declined",
            "The filing weakened the current demand outlook before production recovered",
            "The filing weakened the current demand outlook when production declined",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_rejects_temporal_clause_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production weakened after the current demand outlook improved"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_ambiguous_role_entity_labels_fail_before_role_shortcut(self):
        for value in (
            "Fund Alpha Beta",
            "Fund Project Gamma",
            "펀드 알파 베타",
        ):
            with self.subTest(value=value):
                self.assertFalse(related.item_specific_lineage_assertion(value))

    def test_entity_lead_with_substantive_event_remains_valid(self):
        for value in (
            "Fund Alpha secured financing",
            "Fund Alpha began operations",
            "펀드 알파 투자 완료",
        ):
            with self.subTest(value=value):
                self.assertTrue(related.item_specific_lineage_assertion(value))

    def test_strict_follow_up_rejects_fund_entity_label_in_all_assertions(self):
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
                "fresh_follow_up_anchor": "Fund Alpha Beta",
                "incremental_fact_vs_predecessor": "Fund Alpha Beta",
                "changed_judgment_vs_predecessor": "Fund Alpha Beta",
                "reason": "The later filing was reviewed against the predecessor.",
            },
        }
        errors, _warnings = related.check_card(
            child,
            {"PARENT": parent, "CHILD": child},
            require_contract=True,
        )
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


if __name__ == "__main__":
    unittest.main()

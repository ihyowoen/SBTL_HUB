from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "validation_scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import card_audit_utils as audit
import date_role_freshness_check as date_role
import evidence_qc_v8_check as evidence_qc
from validation_scripts import related_lifecycle_check as related


class TestReview4866342255ScopeContracts(unittest.TestCase):
    SELECTORS = (
        audit.select_scoped_cards,
        evidence_qc.select_scoped_cards,
        date_role.select_scoped_cards,
    )

    def test_unique_draft_and_source_spec_ids_select_premerge_cards(self):
        cards = [
            {"id": "LEGACY"},
            {"draft_id": "DRAFT_NEW", "source_spec_id": "SPEC_NEW"},
        ]
        for selector in self.SELECTORS:
            for requested in ({"DRAFT_NEW"}, {"SPEC_NEW"}):
                with self.subTest(selector=selector.__module__, requested=requested):
                    rows, scope = selector(cards, requested)
                    self.assertEqual("PASS", scope["status"])
                    self.assertEqual([cards[1]], rows)
                    self.assertEqual(1, scope["matched_count"])
                    self.assertEqual(1, scope["selected_card_count"])

    def test_ambiguous_provisional_and_cross_namespace_ids_fail_closed(self):
        cases = (
            ([{"draft_id": "DUP"}, {"source_spec_id": "DUP"}], "DUP"),
            ([{"id": "COLLIDE"}, {"draft_id": "COLLIDE"}], "COLLIDE"),
        )
        for selector in self.SELECTORS:
            for cards, requested in cases:
                with self.subTest(selector=selector.__module__, requested=requested):
                    rows, scope = selector(cards, {requested})
                    self.assertEqual([], rows)
                    self.assertEqual("FAIL", scope["status"])
                    self.assertEqual([requested], scope["ambiguous_ids"])
                    self.assertIn("ID scope matched zero cards", scope["errors"])
                    self.assertIn("ID scope has 1 ambiguous ID(s)", scope["errors"])

    def test_same_row_canonical_and_provisional_alias_is_unambiguous(self):
        cards = [{"id": "SAME", "draft_id": "SAME"}]
        for selector in self.SELECTORS:
            rows, scope = selector(cards, {"SAME"})
            self.assertEqual(cards, rows)
            self.assertEqual("PASS", scope["status"])
            self.assertEqual([], scope["ambiguous_ids"])

    def test_partial_scope_retains_unique_matches_but_fails(self):
        cards = [{"draft_id": "DRAFT_NEW"}]
        for selector in self.SELECTORS:
            rows, scope = selector(cards, {"DRAFT_NEW", "MISSING"})
            self.assertEqual(cards, rows)
            self.assertEqual("FAIL", scope["status"])
            self.assertEqual(["MISSING"], scope["missing_ids"])


class TestReview4866342255LetteredEntityContracts(unittest.TestCase):
    @staticmethod
    def _strict_follow_up(assertion: str):
        parent = {"id": "PARENT", "date": "2026-04-01", "related": []}
        child = {
            "id": "CHILD",
            "date": "2026-07-01",
            "related": ["PARENT"],
            "publish_ready": True,
            "related_lineage": {
                "status": "PASS",
                "relation_type": "distinct_follow_up",
                "related_ids": ["PARENT"],
                "reason": "The new verified data materially changes the predecessor assessment.",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "fresh_follow_up_anchor_class": "data_financial_anchor",
                "fresh_follow_up_anchor": assertion,
                "incremental_fact_vs_predecessor": assertion,
                "changed_judgment_vs_predecessor": assertion,
            },
        }
        return child, {"PARENT": parent, "CHILD": child}

    def _assert_strict_success(self, assertion: str):
        self.assertTrue(related.item_specific_lineage_assertion(assertion))
        child, by_id = self._strict_follow_up(assertion)
        errors, warnings = related.check_card(child, by_id, require_contract=True)
        self.assertEqual([], warnings)
        self.assertEqual([], errors)

    def test_lettered_project_and_facility_labels_are_concrete_subjects(self):
        assertions = (
            "Project A Q2 revenue",
            "Plant A Q2 inventory",
            "Facility B Q2 safety data",
            "Site C Q2 utilization",
            "Unit D Q2 operating data",
            "프로젝트 A Q2 매출",
            "공장 B Q2 재고",
        )
        for assertion in assertions:
            with self.subTest(assertion=assertion):
                self._assert_strict_success(assertion)

    def test_generic_owner_plus_letter_does_not_become_a_subject(self):
        assertions = ("Company A Q2 revenue", "Issuer A Q2 revenue", "a Q2 revenue")
        for assertion in assertions:
            with self.subTest(assertion=assertion):
                self.assertFalse(related.item_specific_lineage_assertion(assertion))


if __name__ == "__main__":
    unittest.main()

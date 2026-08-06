#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from related_lifecycle_check import check_card
from stage_lineage_contract_check import (
    _contains_generic_target_fragment,
    _structured_exact_target,
)


class RelatedCrossNamespaceDedupTest(unittest.TestCase):
    def test_final_and_provisional_aliases_for_same_target_fail(self):
        parent = {
            "id": "PARENT_FINAL",
            "draft_id": "PARENT_DRAFT",
            "date": "2026-08-01",
            "related": [],
        }
        child = {
            "id": "CHILD",
            "date": "2026-08-02",
            "related": ["PARENT_FINAL"],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "program_lineage",
                "related_ids": ["PARENT_FINAL"],
                "related_candidate_spec_ids": ["PARENT_DRAFT"],
                "reason": "same governed program",
            },
        }
        errors, _ = check_card(
            child,
            {"PARENT_FINAL": parent, "CHILD": child},
            True,
            allow_provisional_related=True,
            provisional_by_id={"PARENT_DRAFT": parent},
            ambiguous_provisional_ids=set(),
        )
        self.assertTrue(any(
            "final and provisional related aliases resolve to duplicate target" in error
            for error in errors
        ))


class UnicodeGenericTargetNormalizationTest(unittest.TestCase):
    def test_unicode_punctuation_and_wrappers_do_not_bypass_generic_check(self):
        variants = (
            "more evidence。",
            "more evidence…",
            "“more evidence”",
            "‘more evidence’",
            "「more evidence」",
            "（more evidence）",
            "【more evidence】",
        )
        for value in variants:
            with self.subTest(value=value):
                self.assertTrue(_contains_generic_target_fragment(value))
                self.assertFalse(_structured_exact_target(value))

    def test_specific_target_with_unicode_terminal_punctuation_still_passes(self):
        value = "additional data center capacity for Project Alpha。"
        self.assertFalse(_contains_generic_target_fragment(value))
        self.assertTrue(_structured_exact_target(value))


if __name__ == "__main__":
    unittest.main()

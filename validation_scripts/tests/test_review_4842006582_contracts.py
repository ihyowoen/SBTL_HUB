"""Regression coverage for Codex review 4842006582.

The suite keeps contextual uncertainty valid while modified placeholder-only
phrases remain blocked, and requires chronology exceptions to contain
item-specific basis and reason text rather than generic template scaffolding.
"""

from __future__ import annotations

import copy
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)
from validation_scripts.tests.test_review_4841890896_contracts import (
    TestReview4841890896Contracts,
)


class TestReview4842006582Contracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_modified_unknown_placeholders_fail_closed(self):
        for placeholder in (
            "currently unknown",
            "still unavailable",
            "unknown at this time",
            "현재 미확인",
        ):
            with self.subTest(placeholder=placeholder):
                spec = copy.deepcopy(self.base_spec())
                for field in lineage.STAGE_A_V3_NARRATIVE_FIELDS:
                    spec[field] = placeholder
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn("must be item-specific narrative text", output)

    def test_contextual_unknown_remains_valid(self):
        spec = copy.deepcopy(self.base_spec())
        spec["remaining_uncertainty"] = (
            "The named customer's volume remains unknown pending the August filing."
        )
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_generic_chronology_template_does_not_waive_inversion(self):
        parent, child = TestReview4841890896Contracts().provisional_cards(True)
        justification = child["related_lineage"]["follow_up_date_precedes_predecessor_justification"]
        justification["representative_date_basis"] = (
            "specific explanation of what event the earlier date represents"
        )
        justification["reason"] = (
            "specific explanation of why the earlier representative date remains a later distinct follow-up judgment"
        )
        by_id = {"PARENT_FINAL": parent, "CHILD_FINAL": child}
        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])
        errors, _ = related.check_card(
            child,
            by_id,
            require_contract=True,
            allow_provisional_related=True,
            provisional_by_id=provisional_by_id,
            ambiguous_provisional_ids=ambiguous,
        )
        self.assertIn(
            "follow-up chronology justification requires an item-specific representative_date_basis",
            errors,
        )
        self.assertIn(
            "follow-up date precedes provisional predecessor PARENT_SPEC",
            errors,
        )

    def test_specific_chronology_exception_still_passes(self):
        errors, warnings = TestReview4841890896Contracts().run_provisional(True)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()

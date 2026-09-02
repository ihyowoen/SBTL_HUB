from __future__ import annotations

import unittest

from validation_scripts import stage_a_full_v3_completeness as full


class TestStageAV4DenominatorGapCompatibility(unittest.TestCase):
    def validate(self, item):
        messages = []
        full._validate_denominator_gap_compat(item, "ITEM", messages)
        return messages

    def test_historical_v3_boolean_semantics_are_preserved(self):
        self.assertEqual(self.validate({"denominator_gap": False}), [])
        self.assertIn("ITEM: V3 denominator_gap must be boolean", self.validate({"denominator_gap": "gap"}))

    def test_v4_without_denominator_requires_explanatory_text(self):
        item = {
            "selection_policy_version": full.V4_POLICY_VERSION,
            "systemic_scale_denominator": None,
            "denominator_gap": "No defensible denominator is available from Stage A source metadata.",
        }
        self.assertEqual(self.validate(item), [])
        item["denominator_gap"] = False
        self.assertIn("V4 denominator_gap must be a non-empty explanation", self.validate(item)[0])

    def test_v4_with_denominator_requires_empty_gap(self):
        item = {
            "selection_policy_version": full.V4_POLICY_VERSION,
            "systemic_scale_denominator": "Q2 2026 U.S. storage additions = 20.2 GWh",
            "denominator_gap": None,
        }
        self.assertEqual(self.validate(item), [])
        item["denominator_gap"] = "should be empty"
        self.assertIn("V4 denominator_gap must be empty", self.validate(item)[0])


if __name__ == "__main__":
    unittest.main()

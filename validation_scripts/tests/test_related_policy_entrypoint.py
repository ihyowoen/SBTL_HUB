from __future__ import annotations

from pathlib import Path
import unittest

from validation_scripts import related_lifecycle_check as public
from validation_scripts import related_lifecycle_check_review_latest_base as legacy
from validation_scripts import related_subject_specificity as stable


class RelatedPolicyEntrypointTests(unittest.TestCase):
    def test_public_entrypoint_has_no_review_id_import(self):
        source = Path(public.__file__).read_text(encoding="utf-8")
        self.assertIn("related_subject_specificity as _impl", source)
        self.assertNotIn("related_lifecycle_check_review", source)

    def test_stable_policy_preserves_legacy_decisions(self):
        samples = (
            "Project A throughput growth",
            "Project A capex reduced",
            "Project A YOY profit decline",
            "Plant 1 yield improvement",
            "Facility 2 EBITDA improvement",
            "Acme Corp profit decline",
            "General Motors profit decline",
            "Panasonic capex reduction",
            "Project Profit decline",
            "Plant Yield Improvement",
            "Facility EBITDA improvement",
            "Alarming capex reduction",
            "emerging company profit decline",
        )
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertEqual(
                    legacy.item_specific_lineage_assertion(sample),
                    stable.item_specific_lineage_assertion(sample),
                )

    def test_stable_policy_exports_legacy_cli_graph(self):
        self.assertIs(stable.check_card, legacy.check_card)
        self.assertIs(stable.main, legacy.main)
        self.assertIs(
            stable.check_card.__globals__["item_specific_lineage_assertion"],
            stable.item_specific_lineage_assertion,
        )
        self.assertIs(stable.main.__globals__["check_card"], stable.check_card)

    def test_public_policy_keeps_latest_single_identifier_guard(self):
        for sample in (
            "Project A throughput growth",
            "Project A capex reduced",
            "Project A YOY profit decline",
            "Plant 1 yield improvement",
            "Facility 2 EBITDA improvement",
        ):
            with self.subTest(sample=sample):
                self.assertTrue(public.item_specific_lineage_assertion(sample))

        for sample in (
            "Project Profit decline",
            "Plant Yield Improvement",
            "Facility EBITDA improvement",
            "Alarming capex reduction",
            "emerging company profit decline",
        ):
            with self.subTest(sample=sample):
                self.assertFalse(public.item_specific_lineage_assertion(sample))


if __name__ == "__main__":
    unittest.main()

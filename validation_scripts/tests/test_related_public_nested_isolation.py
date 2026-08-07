from __future__ import annotations

import unittest

from validation_scripts import related_lifecycle_check as public
from validation_scripts import related_subject_specificity as stable


class RelatedPublicNestedIsolationTests(unittest.TestCase):
    def test_public_owns_nested_stable_metric_role_core_graph(self):
        self.assertIsNot(public._impl, stable)
        self.assertIsNot(public._impl._base, stable._base)
        self.assertIsNot(public._impl._base._prior, stable._base._prior)
        self.assertIsNot(
            public._impl._base._prior._base,
            stable._base._prior._base,
        )

    def test_public_metric_alias_points_to_public_nested_metric_state(self):
        self.assertIs(
            public._impl._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS,
            public._impl._base._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS,
        )
        self.assertIsNot(
            public._impl._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS,
            stable._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS,
        )

    def test_nested_metric_mutations_do_not_cross_public_stable_boundary(self):
        sample = "Project Alpha throughput growth"
        stable_terms = stable._base._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
        public_terms = public._impl._base._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS

        self.assertTrue(stable.item_specific_lineage_assertion(sample))
        self.assertTrue(public.item_specific_lineage_assertion(sample))
        self.assertIn("throughput", stable_terms)
        self.assertIn("throughput", public_terms)

        try:
            stable_terms.remove("throughput")
            self.assertFalse(stable.item_specific_lineage_assertion(sample))
            self.assertTrue(public.item_specific_lineage_assertion(sample))
        finally:
            stable_terms.add("throughput")

        try:
            public_terms.remove("throughput")
            self.assertTrue(stable.item_specific_lineage_assertion(sample))
            self.assertFalse(public.item_specific_lineage_assertion(sample))
        finally:
            public_terms.add("throughput")


if __name__ == "__main__":
    unittest.main()

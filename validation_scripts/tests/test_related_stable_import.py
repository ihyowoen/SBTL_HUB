from __future__ import annotations

from pathlib import Path
import unittest

from validation_scripts import related_subject_specificity as stable
from validation_scripts import related_subject_specificity_metric_base as metric_base


class RelatedStableImportTests(unittest.TestCase):
    def test_stable_layer_uses_module_clone_not_callable_seam(self):
        source = Path(stable.__file__).read_text(encoding="utf-8")
        self.assertIn("clone_module_with_shared_globals", source)
        self.assertNotIn("callable_seam", source)
        self.assertNotIn("clone_function_with_globals", source)

    def test_stable_layer_owns_isolated_metric_namespace(self):
        self.assertIsNot(stable._base, metric_base)
        self.assertIs(stable.check_card, stable._base.check_card)
        self.assertIs(stable.main, stable._base.main)
        self.assertIs(stable.check_card.__globals__, stable._base.__dict__)
        self.assertIs(stable.main.__globals__, stable._base.__dict__)
        self.assertIs(
            stable._base.item_specific_lineage_assertion,
            stable.item_specific_lineage_assertion,
        )
        self.assertIs(stable.main.__globals__["check_card"], stable.check_card)

    def test_stable_mutable_policy_state_is_isolated_from_metric_layer(self):
        stable_terms = stable._base._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
        metric_terms = metric_base._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
        self.assertIs(stable._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS, stable_terms)
        self.assertIsNot(stable_terms, metric_terms)

        stable_marker = "__stable_namespace_probe__"
        metric_marker = "__metric_namespace_probe__"
        try:
            stable_terms.add(stable_marker)
            self.assertNotIn(stable_marker, metric_terms)

            metric_terms.add(metric_marker)
            self.assertNotIn(metric_marker, stable_terms)
        finally:
            stable_terms.discard(stable_marker)
            metric_terms.discard(metric_marker)


if __name__ == "__main__":
    unittest.main()

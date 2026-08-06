from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validation_scripts import related_lifecycle_check as public
from validation_scripts import related_subject_specificity as stable
from validation_scripts import related_subject_specificity_metric_base as metric_base


class RelatedPolicyEntrypointTests(unittest.TestCase):
    def test_public_entrypoint_has_no_review_id_import(self):
        source = Path(public.__file__).read_text(encoding="utf-8")
        self.assertIn("related_subject_specificity as _impl", source)
        self.assertNotIn("related_lifecycle_check_review", source)

    def test_stable_policy_owns_latest_layer_directly(self):
        source = Path(stable.__file__).read_text(encoding="utf-8")
        self.assertIn("related_subject_specificity_metric_base as _base", source)
        self.assertNotIn("related_lifecycle_check_review4871397803_base", source)
        removed_layers = (
            "related_lifecycle_check_review_latest_base.py",
            "related_lifecycle_check_review4871397803_base.py",
        )
        for filename in removed_layers:
            with self.subTest(filename=filename):
                self.assertFalse(Path(stable.__file__).with_name(filename).exists())

    def test_stable_metric_layer_keeps_only_next_historical_dependency(self):
        source = Path(metric_base.__file__).read_text(encoding="utf-8")
        self.assertNotIn("related_lifecycle_check_review4871397803_base", source)
        self.assertIn("related_lifecycle_check_review4868891584_base.py", source)

    def test_stable_policy_script_is_directly_executable(self):
        script = Path(stable.__file__).resolve()
        with tempfile.TemporaryDirectory() as cwd:
            completed = subprocess.run(
                [sys.executable, str(script), "--help"],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertNotIn("ModuleNotFoundError", completed.stderr)

    def test_stable_and_public_decisions_match_locked_policy_cases(self):
        expected = {
            "Project A throughput growth": True,
            "Project A capex reduced": True,
            "Project A YOY profit decline": True,
            "Plant 1 yield improvement": True,
            "Facility 2 EBITDA improvement": True,
            "Acme Corp profit decline": True,
            "General Motors profit decline": True,
            "Panasonic capex reduction": True,
            "Project Profit decline": False,
            "Plant Yield Improvement": False,
            "Facility EBITDA improvement": False,
            "Alarming capex reduction": False,
            "emerging company profit decline": False,
        }
        for sample, decision in expected.items():
            with self.subTest(sample=sample):
                self.assertEqual(
                    decision, stable.item_specific_lineage_assertion(sample)
                )
                self.assertEqual(
                    decision, public.item_specific_lineage_assertion(sample)
                )

    def test_stable_policy_owns_isolated_callable_graph(self):
        self.assertIsNot(stable.check_card, metric_base.check_card)
        self.assertIsNot(stable.main, metric_base.main)
        self.assertIsNot(
            stable.check_card.__globals__, metric_base.check_card.__globals__
        )
        self.assertIs(
            stable.check_card.__globals__["item_specific_lineage_assertion"],
            stable.item_specific_lineage_assertion,
        )
        self.assertIs(stable.main.__globals__["check_card"], stable.check_card)

    def test_public_entrypoint_owns_isolated_final_callable_graph(self):
        self.assertIsNot(public.check_card, stable.check_card)
        self.assertIsNot(public.main, stable.main)
        self.assertIsNot(
            public.check_card.__globals__, stable.check_card.__globals__
        )
        self.assertIs(
            public.check_card.__globals__["item_specific_lineage_assertion"],
            public.item_specific_lineage_assertion,
        )
        self.assertIs(public.main.__globals__["check_card"], public.check_card)

    def test_lower_metric_layer_cannot_rebind_stable_or_public_policy(self):
        metric_base.check_card.__globals__["item_specific_lineage_assertion"] = (
            metric_base.item_specific_lineage_assertion
        )
        self.assertIs(
            stable.check_card.__globals__["item_specific_lineage_assertion"],
            stable.item_specific_lineage_assertion,
        )
        self.assertIs(
            public.check_card.__globals__["item_specific_lineage_assertion"],
            public.item_specific_lineage_assertion,
        )

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

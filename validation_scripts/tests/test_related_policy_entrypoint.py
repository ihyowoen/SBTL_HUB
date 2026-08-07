from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validation_scripts import related_lifecycle_check as public
from validation_scripts import related_lifecycle_core as core
from validation_scripts import related_subject_specificity as stable
from validation_scripts import related_subject_specificity_metric_base as metric_base
from validation_scripts import related_subject_specificity_role_base as role_base


class RelatedPolicyEntrypointTests(unittest.TestCase):
    def test_public_entrypoint_imports_and_clones_stable_dependency(self):
        source = Path(public.__file__).read_text(encoding="utf-8")
        self.assertIn("related_subject_specificity as _impl", source)
        self.assertIn("clone_module_with_rebound_functions", source)
        self.assertNotIn("callable_seam", source)
        self.assertNotIn("clone_function_with_globals", source)
        self.assertNotIn("related_lifecycle_check_review", source)
        self.assertFalse(Path(public.__file__).with_name("callable_seam.py").exists())

    def test_stable_policy_owns_latest_layer_directly(self):
        source = Path(stable.__file__).read_text(encoding="utf-8")
        self.assertIn("related_subject_specificity_metric_base as _base", source)
        self.assertNotIn("related_lifecycle_check_review4871397803_base", source)
        removed_layers = (
            "related_lifecycle_check_review_latest_base.py",
            "related_lifecycle_check_review4871397803_base.py",
            "related_lifecycle_check_review4868891584_base.py",
            "related_lifecycle_check_review4860866998_base.py",
        )
        for filename in removed_layers:
            with self.subTest(filename=filename):
                self.assertFalse(Path(stable.__file__).with_name(filename).exists())

    def test_stable_metric_layer_imports_and_clones_stable_role_dependency(self):
        source = Path(metric_base.__file__).read_text(encoding="utf-8")
        self.assertIn("related_subject_specificity_role_base as _role", source)
        self.assertIn("clone_module_with_cloned_dependency", source)
        self.assertNotIn("importlib.util", source)
        self.assertNotIn("spec_from_file_location", source)
        self.assertNotIn("related_subject_specificity_role_base.py", source)
        self.assertNotIn("related_lifecycle_check_review4868891584_base", source)

    def test_stable_role_layer_imports_and_clones_stable_core(self):
        source = Path(role_base.__file__).read_text(encoding="utf-8")
        self.assertIn("related_lifecycle_core as _core", source)
        self.assertIn("clone_module_with_shared_globals", source)
        self.assertNotIn("importlib.util", source)
        self.assertNotIn("spec_from_file_location", source)
        self.assertNotIn("related_lifecycle_check_review4860866998_base", source)

    def test_stable_role_core_clone_owns_shared_isolated_globals(self):
        self.assertIsNot(role_base._base, core)
        self.assertIsNot(role_base._base.check_card, core.check_card)
        self.assertIsNot(role_base._base.main, core.main)
        self.assertIs(role_base._base.check_card.__globals__, role_base._base.__dict__)
        self.assertIs(role_base._base.main.__globals__, role_base._base.__dict__)
        self.assertIs(
            role_base._base.item_specific_lineage_assertion,
            role_base.item_specific_lineage_assertion,
        )
        self.assertIsNot(
            core.item_specific_lineage_assertion,
            role_base.item_specific_lineage_assertion,
        )

    def test_stable_core_has_no_review_id_dependency(self):
        source = Path(core.__file__).read_text(encoding="utf-8")
        self.assertNotIn("related_lifecycle_check_review", source)
        self.assertIn("def check_card(", source)
        self.assertIn("def main()", source)

    def test_public_policy_script_is_directly_executable(self):
        script = Path(public.__file__).resolve()
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

    def test_stable_role_script_is_directly_executable(self):
        script = Path(role_base.__file__).resolve()
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

    def test_stable_core_script_is_directly_executable(self):
        script = Path(core.__file__).resolve()
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

    def test_public_entrypoint_owns_isolated_stable_namespace(self):
        self.assertIsNot(public._impl, stable)
        self.assertIs(public.check_card, public._impl.check_card)
        self.assertIs(public.main, public._impl.main)
        self.assertIs(public.check_card.__globals__, public._impl.__dict__)
        self.assertIs(public.main.__globals__, public._impl.__dict__)
        self.assertIs(
            public._impl.item_specific_lineage_assertion,
            public.item_specific_lineage_assertion,
        )
        self.assertIs(public.main.__globals__["check_card"], public.check_card)

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

    def test_public_mutable_policy_state_is_isolated_from_stable_layer(self):
        public_terms = public._impl._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
        stable_terms = stable._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS
        self.assertIs(public._RELATED_FINANCIAL_AND_OPERATING_METRIC_TERMS, public_terms)
        self.assertIsNot(public_terms, stable_terms)

        public_marker = "__public_namespace_probe__"
        stable_marker = "__stable_namespace_probe__"
        try:
            public_terms.add(public_marker)
            self.assertNotIn(public_marker, stable_terms)

            stable_terms.add(stable_marker)
            self.assertNotIn(stable_marker, public_terms)
        finally:
            public_terms.discard(public_marker)
            stable_terms.discard(stable_marker)

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

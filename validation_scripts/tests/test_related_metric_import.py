from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
import unittest

from validation_scripts import related_subject_specificity_metric_base as metric_base
from validation_scripts import related_subject_specificity_role_base as role_base
from validation_scripts.module_seam import clone_module_with_cloned_dependency


class RelatedMetricImportTests(unittest.TestCase):
    def test_nested_dependency_clone_rewires_aliases_and_mutable_state(self):
        dependency = ModuleType("sample_policy.base")
        exec(
            "POLICY = {'base'}\n"
            "def contains(value):\n"
            "    return value in POLICY\n",
            dependency.__dict__,
        )

        layer = ModuleType("sample_policy.layer")
        layer.__dict__["_base"] = dependency
        exec(
            "POLICY = _base.POLICY\n"
            "inherited_contains = _base.contains\n"
            "_prior_contains = _base.contains\n"
            "def layer_contains(value):\n"
            "    return _prior_contains(value)\n",
            layer.__dict__,
        )

        cloned = clone_module_with_cloned_dependency(
            layer,
            dependency_name="_base",
            module_name="sample_policy.cloned_layer",
        )

        self.assertIsNot(cloned, layer)
        self.assertIsNot(cloned._base, dependency)
        self.assertIs(cloned.POLICY, cloned._base.POLICY)
        self.assertIs(cloned.inherited_contains, cloned._base.contains)
        self.assertIs(cloned._prior_contains, cloned._base.contains)
        self.assertIs(cloned.layer_contains.__globals__, cloned.__dict__)
        self.assertIs(cloned._base.contains.__globals__, cloned._base.__dict__)

        cloned.POLICY.add("cloned-only")
        self.assertTrue(cloned.layer_contains("cloned-only"))
        self.assertNotIn("cloned-only", dependency.POLICY)

    def test_metric_layer_imports_and_clones_stable_role_dependency(self):
        source = Path(metric_base.__file__).read_text(encoding="utf-8")
        self.assertIn("related_subject_specificity_role_base as _role", source)
        self.assertIn("clone_module_with_cloned_dependency", source)
        self.assertNotIn("importlib.util", source)
        self.assertNotIn("spec_from_file_location", source)
        self.assertNotIn("related_subject_specificity_role_base.py", source)

    def test_metric_role_and_nested_base_are_isolated(self):
        self.assertIsNot(metric_base._prior, role_base)
        self.assertIsNot(metric_base._prior._base, role_base._base)
        self.assertIs(
            metric_base._prior.main.__globals__,
            metric_base._prior._base.__dict__,
        )
        self.assertIs(
            metric_base._prior.check_card.__globals__,
            metric_base._prior._base.__dict__,
        )
        self.assertIs(
            metric_base._prior._prior_item_specific_lineage_assertion.__globals__,
            metric_base._prior._base.__dict__,
        )
        self.assertIs(metric_base.main, metric_base._prior.main)
        self.assertIs(metric_base.check_card, metric_base._prior.check_card)

        sentinel = "__metric_clone_sentinel__"
        self.assertNotIn(sentinel, role_base._RELATED_DATA_FINANCIAL_ROLE_TERMS)
        self.assertNotIn(sentinel, role_base._base.PUBLISH_STATES)
        try:
            metric_base._prior._RELATED_DATA_FINANCIAL_ROLE_TERMS.add(sentinel)
            metric_base._prior._base.PUBLISH_STATES.add(sentinel)
            self.assertIn(
                sentinel,
                metric_base._prior._RELATED_DATA_FINANCIAL_ROLE_TERMS,
            )
            self.assertIn(sentinel, metric_base._prior._base.PUBLISH_STATES)
            self.assertNotIn(
                sentinel,
                role_base._RELATED_DATA_FINANCIAL_ROLE_TERMS,
            )
            self.assertNotIn(sentinel, role_base._base.PUBLISH_STATES)
        finally:
            metric_base._prior._RELATED_DATA_FINANCIAL_ROLE_TERMS.discard(sentinel)
            metric_base._prior._base.PUBLISH_STATES.discard(sentinel)

    def test_metric_policy_terms_do_not_leak_into_canonical_role(self):
        self.assertIn(
            "ebitda",
            metric_base._prior._RELATED_DATA_FINANCIAL_ROLE_TERMS,
        )
        self.assertNotIn("ebitda", role_base._RELATED_DATA_FINANCIAL_ROLE_TERMS)

    def test_metric_script_is_directly_executable_from_external_cwd(self):
        script = Path(metric_base.__file__).resolve()
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


if __name__ == "__main__":
    unittest.main()

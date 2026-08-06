from __future__ import annotations

from types import ModuleType
import unittest

from validation_scripts import related_lifecycle_core as core
from validation_scripts import related_subject_specificity_role_base as role_base
from validation_scripts.module_seam import clone_module_with_shared_globals


class ModuleSeamTests(unittest.TestCase):
    def test_nested_mutable_globals_are_isolated_and_visible_to_cloned_functions(self):
        source = ModuleType("test_source_module")
        exec(
            "POLICY = {'nested': ['base']}\n"
            "POLICY_SET = {'base'}\n"
            "def read_policy():\n"
            "    return POLICY, POLICY_SET\n",
            source.__dict__,
        )

        cloned = clone_module_with_shared_globals(
            source,
            module_name="test_cloned_module",
        )
        cloned.POLICY["nested"].append("clone")
        cloned.POLICY_SET.add("clone")

        self.assertEqual(["base"], source.POLICY["nested"])
        self.assertEqual({"base"}, source.POLICY_SET)
        self.assertEqual(["base", "clone"], cloned.POLICY["nested"])
        self.assertEqual({"base", "clone"}, cloned.POLICY_SET)
        self.assertIs(cloned.read_policy()[0], cloned.POLICY)
        self.assertIs(cloned.read_policy()[1], cloned.POLICY_SET)

    def test_role_policy_mutation_does_not_reach_canonical_core(self):
        marker = "__role_clone_only__"
        self.assertIsNot(role_base._base.PUBLISH_STATES, core.PUBLISH_STATES)
        role_base._base.PUBLISH_STATES.add(marker)
        try:
            self.assertNotIn(marker, core.PUBLISH_STATES)
            self.assertIn(marker, role_base._base.PUBLISH_STATES)
        finally:
            role_base._base.PUBLISH_STATES.discard(marker)


if __name__ == "__main__":
    unittest.main()

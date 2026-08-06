import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "validation_scripts" / "stage_lineage_contract_check.py"
SPEC = importlib.util.spec_from_file_location("stage_lineage_contract_check_review_4850266559", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


class Review4850266559Contracts(unittest.TestCase):
    def test_full_six_token_bridge_percentage_adoption_is_measurement(self):
        text = "A 10 percent increase in the current global Project Alpha adoption"
        self.assertFalse(MOD._has_bound_interpretation_effect(text))

    def test_full_six_token_bridge_percentage_adoption_structured_is_measurement(self):
        point = {
            "measurable_event_or_metric": "Project Alpha adoption percentage",
            "interpretation_effect": "A 10 percent increase in the current global Project Alpha adoption",
        }
        self.assertFalse(MOD._valid_confirmation_point(point))

    def test_object_first_full_bridge_measurement_is_rejected(self):
        self.assertFalse(MOD._has_bound_interpretation_effect(
            "Project Alpha adoption in the current global market increased by 10 percent"
        ))

    def test_semantic_adoption_effect_remains_valid(self):
        self.assertTrue(MOD._has_bound_interpretation_effect(
            "The filing would raise the current global Project Alpha adoption probability"
        ))

    def test_direct_confirmation_of_adoption_remains_valid(self):
        self.assertTrue(MOD._has_bound_interpretation_effect(
            "The capacity milestone would confirm Project Alpha adoption"
        ))


if __name__ == "__main__":
    unittest.main()

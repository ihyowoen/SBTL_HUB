#!/usr/bin/env python3
from pathlib import Path

validator = Path('validation_scripts/stage_lineage_contract_check.py')
text = validator.read_text()
old = """    # Directional movement plus a numeric/metric qualifier makes adoption a
    # measured outcome regardless of whether the movement appears before or
    # after the overloaded object (for example, \"10% increase in adoption\" or
    # \"adoption increased by 10%\"). Keep the window local so an unrelated
    # measurement elsewhere in the clause cannot reclassify the object.
    local_window = tokens[max(0, index - 6):min(len(tokens), index + 7)]
    has_directional_movement = any(
        _base._has_any_term(
            candidate, _base.STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS
        )
        for candidate in local_window
    )
    has_measurement = any(
        any(char.isdigit() for char in candidate)
        for candidate in local_window
    ) or any(
        candidate in _base.STAGE_A_INTERPRETATION_METRIC_QUALIFIERS
        for candidate in local_window
    )
    if has_directional_movement and has_measurement:
        return False
"""
new = """    # Directional movement plus a numeric/metric qualifier makes adoption a
    # measured outcome regardless of whether the movement appears before or
    # after the overloaded object (for example, \"10% increase in adoption\" or
    # \"adoption increased by 10%\"). Inspect every directional endpoint allowed
    # by the six-token semantic bridge, plus the two-token measurement modifier
    # immediately outside that endpoint (for example, \"10 percent increase\").
    directional_positions = [
        candidate_index
        for candidate_index in range(
            max(0, index - 7), min(len(tokens), index + 8)
        )
        if _base._has_any_term(
            tokens[candidate_index],
            _base.STAGE_A_DIRECTIONAL_INTERPRETATION_EFFECT_TERMS,
        )
    ]
    for directional_index in directional_positions:
        context_start = max(0, min(index, directional_index) - 2)
        context_end = min(len(tokens), max(index, directional_index) + 3)
        measurement_context = tokens[context_start:context_end]
        has_measurement = any(
            any(char.isdigit() for char in candidate)
            for candidate in measurement_context
        ) or any(
            candidate in _base.STAGE_A_INTERPRETATION_METRIC_QUALIFIERS
            for candidate in measurement_context
        )
        if has_measurement:
            return False
"""
if text.count(old) != 1:
    raise SystemExit(f'expected one validator target, found {text.count(old)}')
validator.write_text(text.replace(old, new))

test = Path('validation_scripts/tests/test_review_4850266559_contracts.py')
test.write_text('''import importlib.util\nimport unittest\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\nMODULE_PATH = ROOT / "validation_scripts" / "stage_lineage_contract_check.py"\nSPEC = importlib.util.spec_from_file_location("stage_lineage_contract_check_review_4850266559", MODULE_PATH)\nMOD = importlib.util.module_from_spec(SPEC)\nassert SPEC.loader is not None\nSPEC.loader.exec_module(MOD)\n\n\nclass Review4850266559Contracts(unittest.TestCase):\n    def test_full_six_token_bridge_percentage_adoption_is_measurement(self):\n        text = "A 10 percent increase in the current global Project Alpha adoption"\n        self.assertFalse(MOD._has_bound_interpretation_effect(text))\n\n    def test_full_six_token_bridge_percentage_adoption_structured_is_measurement(self):\n        point = {\n            "measurable_event_or_metric": "Project Alpha adoption percentage",\n            "interpretation_effect": "A 10 percent increase in the current global Project Alpha adoption",\n        }\n        self.assertFalse(MOD._valid_confirmation_point(point))\n\n    def test_object_first_full_bridge_measurement_is_rejected(self):\n        self.assertFalse(MOD._has_bound_interpretation_effect(\n            "Project Alpha adoption in the current global market increased by 10 percent"\n        ))\n\n    def test_semantic_adoption_effect_remains_valid(self):\n        self.assertTrue(MOD._has_bound_interpretation_effect(\n            "The filing would raise the current global Project Alpha adoption probability"\n        ))\n\n    def test_direct_confirmation_of_adoption_remains_valid(self):\n        self.assertTrue(MOD._has_bound_interpretation_effect(\n            "The capacity milestone would confirm Project Alpha adoption"\n        ))\n\n\nif __name__ == "__main__":\n    unittest.main()\n''')

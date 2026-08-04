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
"""
new = """    # Directional movement plus a numeric/metric qualifier makes adoption a
    # measured outcome regardless of whether the movement appears before or
    # after the overloaded object (for example, \"10% increase in adoption\" or
    # \"adoption increased by 10%\"). Scan the full semantic bridge accepted by
    # _effect_bridge_is_semantic(): six intervening tokens place the endpoint
    # effect seven positions away from the overloaded object.
    local_window = tokens[max(0, index - 7):min(len(tokens), index + 8)]
"""
if text.count(old) != 1:
    raise SystemExit(f'expected one validator target, found {text.count(old)}')
validator.write_text(text.replace(old, new))

test = Path('validation_scripts/tests/test_review_4850266559_contracts.py')
test.write_text('''import copy\nimport importlib.util\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\nMODULE_PATH = ROOT / "validation_scripts" / "stage_lineage_contract_check.py"\nSPEC = importlib.util.spec_from_file_location("stage_lineage_contract_check_review_4850266559", MODULE_PATH)\nMOD = importlib.util.module_from_spec(SPEC)\nassert SPEC.loader is not None\nSPEC.loader.exec_module(MOD)\n\n\ndef test_full_six_token_bridge_percentage_adoption_is_measurement():\n    text = "A 10 percent increase in the current global Project Alpha adoption"\n    assert MOD._has_bound_interpretation_effect(text) is False\n\n\ndef test_full_six_token_bridge_percentage_adoption_structured_is_measurement():\n    point = {\n        "measurable_event_or_metric": "Project Alpha adoption percentage",\n        "interpretation_effect": "A 10 percent increase in the current global Project Alpha adoption",\n    }\n    assert MOD._valid_confirmation_point(point) is False\n\n\ndef test_semantic_adoption_effect_remains_valid():\n    assert MOD._has_bound_interpretation_effect(\n        "The filing would raise the current global Project Alpha adoption probability"\n    ) is True\n\n\ndef test_direct_confirmation_of_adoption_remains_valid():\n    assert MOD._has_bound_interpretation_effect(\n        "The capacity milestone would confirm Project Alpha adoption"\n    ) is True\n''')

#!/usr/bin/env python3
from pathlib import Path

validator = Path('validation_scripts/stage_lineage_contract_check.py')
text = validator.read_text(encoding='utf-8')
old = '''    return (
        bool(text)
        and len(text.split()) >= 4
        and not _placeholder_only_text(text)
        and not _contains_generic_target_fragment(text)
        and has_measurable_event_or_metric
    )
'''
new = '''    has_interpretation_effect = _has_any_term(
        text, STAGE_A_INTERPRETATION_EFFECT_TERMS
    )
    return (
        bool(text)
        and len(text.split()) >= 4
        and not _placeholder_only_text(text)
        and not _contains_generic_target_fragment(text)
        and has_measurable_event_or_metric
        and has_interpretation_effect
    )
'''
if text.count(old) != 1:
    raise SystemExit(f'confirmation-point target block count={text.count(old)}')
validator.write_text(text.replace(old, new), encoding='utf-8')

test = Path('validation_scripts/tests/test_review_4849359963_contracts.py')
test.write_text('''import copy\nimport importlib.util\nimport unittest\nfrom pathlib import Path\n\nMODULE_PATH = Path(__file__).resolve().parents[1] / "stage_lineage_contract_check.py"\nspec = importlib.util.spec_from_file_location("stage_lineage_contract_check", MODULE_PATH)\nmodule = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(module)\n\n\nclass Review4849359963Contracts(unittest.TestCase):\n    def test_free_text_confirmation_requires_interpretation_effect(self):\n        self.assertFalse(\n            module._valid_confirmation_point(\n                "Project Alpha production capacity milestone"\n            )\n        )\n\n    def test_free_text_confirmation_accepts_measurable_effect_statement(self):\n        self.assertTrue(\n            module._valid_confirmation_point(\n                "Project Alpha production capacity milestone would confirm adoption"\n            )\n        )\n\n    def test_inflected_effect_and_complete_term_boundary_remain_supported(self):\n        self.assertTrue(\n            module._valid_confirmation_point(\n                "Project Alpha production capacity milestone invalidated the thesis"\n            )\n        )\n        self.assertFalse(\n            module._valid_confirmation_point(\n                "Project Alpha production capacity milestone remained unchanged"\n            )\n        )\n\n    def test_generic_confirmation_scaffold_still_fails(self):\n        self.assertFalse(\n            module._valid_confirmation_point("more evidence on adoption")\n        )\n\n\nif __name__ == "__main__":\n    unittest.main()\n''', encoding='utf-8')

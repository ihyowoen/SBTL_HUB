from __future__ import annotations

import copy
import re
import unittest

from validation_scripts.v3_contract import load_contract, validate_contract_document


class TestReview4871394041Contracts(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()

    def test_free_text_and_structured_values_require_non_whitespace(self):
        definitions = self.contract["$defs"]
        for definition_name in ("evidence_target", "confirmation_point"):
            options = definitions[definition_name]["oneOf"]
            with self.subTest(definition=definition_name, option="free_text"):
                free_text_schema = options[-1]
                self.assertEqual(4, free_text_schema["minLength"])
                self.assertIsNone(re.search(free_text_schema["pattern"], "    "))
                self.assertIsNotNone(re.search(free_text_schema["pattern"], "valid target"))

            for option in options[:-1]:
                for key in option["required"]:
                    with self.subTest(definition=definition_name, key=key):
                        property_schema = option["properties"][key]
                        self.assertEqual(2, property_schema["minLength"])
                        self.assertIsNone(re.search(property_schema["pattern"], "  "))
                        self.assertIsNotNone(re.search(property_schema["pattern"], "valid"))

    def test_canonical_and_compatibility_key_pairs_remain_valid(self):
        metadata = self.contract["x-sbtl-contract"]
        cases = (
            ("evidence_target", "structured_evidence_target_key_pairs"),
            ("confirmation_point", "structured_confirmation_point_key_pairs"),
        )
        for definition_name, metadata_key in cases:
            options = self.contract["$defs"][definition_name]["oneOf"]
            for index, pair in enumerate(metadata[metadata_key]):
                with self.subTest(definition=definition_name, pair=pair):
                    option = options[index]
                    self.assertEqual(pair, option["required"])
                    for key in pair:
                        schema = option["properties"][key]
                        self.assertIsNotNone(re.search(schema["pattern"], "valid value"))

    def test_removal_of_any_pattern_is_canonical_drift(self):
        for definition_name in ("evidence_target", "confirmation_point"):
            options = self.contract["$defs"][definition_name]["oneOf"]
            locations = [(len(options) - 1, None)]
            locations.extend(
                (index, key)
                for index, option in enumerate(options[:-1])
                for key in option["required"]
            )
            for option_index, key in locations:
                with self.subTest(
                    definition=definition_name, option=option_index, key=key
                ):
                    broken = copy.deepcopy(self.contract)
                    option = broken["$defs"][definition_name]["oneOf"][option_index]
                    schema = option if key is None else option["properties"][key]
                    schema.pop("pattern")
                    errors = validate_contract_document(broken)
                    self.assertTrue(
                        any(
                            f"{definition_name} definition differs" in error
                            for error in errors
                        ),
                        errors,
                    )


if __name__ == "__main__":
    unittest.main()

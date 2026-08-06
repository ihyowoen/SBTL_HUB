import copy
import re
import unittest

from validation_scripts.v3_contract import load_contract, validate_contract_document


class TestReview4871316124Contracts(unittest.TestCase):
    def test_narrative_schemas_require_non_whitespace_content(self):
        contract = load_contract()
        metadata = contract["x-sbtl-contract"]
        properties = contract["$defs"]["v3_non_execution_route"]["properties"]
        expected = r"^\s*\S[\s\S]{6,}\S\s*$"
        for field in metadata["v3_narrative_fields"]:
            with self.subTest(field=field):
                schema = properties[field]
                self.assertEqual(
                    {"type": "string", "minLength": 8, "pattern": expected},
                    schema,
                )
                self.assertIsNone(re.fullmatch(schema["pattern"], "        "))
                self.assertIsNotNone(
                    re.fullmatch(schema["pattern"], "verified fact")
                )

    def test_removed_narrative_pattern_is_canonical_drift(self):
        contract = load_contract()
        field = contract["x-sbtl-contract"]["v3_narrative_fields"][0]
        mutated = copy.deepcopy(contract)
        mutated["$defs"]["v3_non_execution_route"]["properties"][field].pop("pattern")
        errors = validate_contract_document(mutated)
        self.assertTrue(any(field in error and "non-empty narrative" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()

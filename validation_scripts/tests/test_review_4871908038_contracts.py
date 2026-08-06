from __future__ import annotations

import copy
import re
import unittest

from validation_scripts.v3_contract import load_contract, validate_contract_document


class TestReview4871908038Contracts(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()
        metadata = self.contract["x-sbtl-contract"]
        self.narrative_fields = tuple(metadata["v3_narrative_fields"])

    @staticmethod
    def _matches(schema, value):
        return (
            isinstance(value, str)
            and len(value) >= schema.get("minLength", 0)
            and re.fullmatch(schema["pattern"], value) is not None
        )

    def test_narrative_minimum_is_applied_after_trimming(self):
        expected = r"^\s*\S[\s\S]{6,}\S\s*$"
        properties = self.contract["$defs"]["v3_non_execution_route"][
            "properties"
        ]
        for field in self.narrative_fields:
            schema = properties[field]
            with self.subTest(field=field):
                self.assertEqual(
                    {"type": "string", "minLength": 8, "pattern": expected},
                    schema,
                )
                for invalid in (
                    " xxxxxxx",
                    "xxxxxxx ",
                    "  xxxxxxx  ",
                    "\txxxxxxx\n",
                ):
                    self.assertFalse(self._matches(schema, invalid))
                for valid in (
                    "abcdefgh",
                    " abcdefgh ",
                    "abc defg",
                    "\tabc defg\n",
                ):
                    self.assertTrue(self._matches(schema, valid))

    def test_narrative_pattern_removal_or_weakening_is_drift(self):
        for field in self.narrative_fields:
            for mutation in ("remove", "weaken"):
                with self.subTest(field=field, mutation=mutation):
                    broken = copy.deepcopy(self.contract)
                    schema = broken["$defs"]["v3_non_execution_route"][
                        "properties"
                    ][field]
                    if mutation == "remove":
                        schema.pop("pattern")
                    else:
                        schema["pattern"] = r"\S"
                    errors = validate_contract_document(broken)
                    self.assertTrue(
                        any(field in error and "narrative" in error for error in errors),
                        errors,
                    )

    def test_current_contract_is_self_consistent(self):
        self.assertEqual([], validate_contract_document(self.contract))


if __name__ == "__main__":
    unittest.main()

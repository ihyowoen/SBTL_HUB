from __future__ import annotations

import copy
import unittest

from validation_scripts.v3_contract import (
    load_contract,
    validate_contract_document,
)


class TestReview4871173263Contracts(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()

    def test_execution_anchor_requires_non_whitespace_pattern(self):
        schema = self.contract["$defs"]["execution_route"]["properties"][
            "execution_anchor_type"
        ]
        self.assertEqual(
            {"type": "string", "minLength": 1, "pattern": r"\S"},
            schema,
        )

        broken = copy.deepcopy(self.contract)
        del broken["$defs"]["execution_route"]["properties"][
            "execution_anchor_type"
        ]["pattern"]
        self.assertIn(
            "execution_anchor_type schema must require a non-whitespace string",
            validate_contract_document(broken),
        )

    def test_structured_alias_lists_are_fully_pinned(self):
        cases = (
            (
                "structured_evidence_target_key_pairs",
                "evidence_target",
                "structured_evidence_target_key_pairs must equal the canonical aliases",
            ),
            (
                "structured_confirmation_point_key_pairs",
                "confirmation_point",
                "structured_confirmation_point_key_pairs must equal the canonical aliases",
            ),
        )
        for metadata_key, definition_name, expected_error in cases:
            with self.subTest(metadata_key=metadata_key):
                broken = copy.deepcopy(self.contract)
                broken["x-sbtl-contract"][metadata_key][1] = ["foo", "bar"]
                option = broken["$defs"][definition_name]["oneOf"][1]
                option["required"] = ["foo", "bar"]
                option["properties"] = {
                    "foo": {"type": "string", "minLength": 2},
                    "bar": {"type": "string", "minLength": 2},
                }
                self.assertIn(
                    expected_error,
                    validate_contract_document(broken),
                )


if __name__ == "__main__":
    unittest.main()

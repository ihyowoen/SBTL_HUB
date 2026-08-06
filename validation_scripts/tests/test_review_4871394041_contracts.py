from __future__ import annotations

import copy
import re
import unittest

from validation_scripts.v3_contract import load_contract, validate_contract_document


class TestReview4871394041Contracts(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()

    @staticmethod
    def _matches(schema, value):
        return (
            isinstance(value, str)
            and len(value) >= schema.get("minLength", 0)
            and re.fullmatch(schema["pattern"], value) is not None
        )

    def test_structured_values_apply_minimum_after_trimming(self):
        expected = r"^\s*\S[\s\S]*\S\s*$"
        for definition_name in ("evidence_target", "confirmation_point"):
            for option in self.contract["$defs"][definition_name]["oneOf"][:2]:
                for key in option["required"]:
                    schema = option["properties"][key]
                    with self.subTest(definition=definition_name, key=key):
                        self.assertEqual(expected, schema["pattern"])
                        for invalid in (" x", "x ", "  x  ", "\tx\n"):
                            self.assertFalse(self._matches(schema, invalid))
                        for valid in ("xy", " x y ", "a b", "\tx y\n"):
                            self.assertTrue(self._matches(schema, valid))

    def test_free_text_applies_four_character_trimmed_minimum(self):
        expected = r"^\s*\S[\s\S]{2,}\S\s*$"
        for definition_name in ("evidence_target", "confirmation_point"):
            schema = self.contract["$defs"][definition_name]["oneOf"][2]
            with self.subTest(definition=definition_name):
                self.assertEqual(expected, schema["pattern"])
                for invalid in (" x ", " ab ", "abc", "  a b  "):
                    self.assertFalse(self._matches(schema, invalid))
                for valid in ("abcd", " a  b ", "ab cd", "\ta bc\n"):
                    self.assertTrue(self._matches(schema, valid))

    def test_pattern_removal_or_weakening_is_detected_as_drift(self):
        for definition_name in ("evidence_target", "confirmation_point"):
            definition = self.contract["$defs"][definition_name]
            for option_index, option in enumerate(definition["oneOf"]):
                keys = (None,) if option["type"] == "string" else tuple(option["required"])
                for key in keys:
                    for mutation in ("remove", "weaken"):
                        with self.subTest(
                            definition=definition_name,
                            option=option_index,
                            key=key,
                            mutation=mutation,
                        ):
                            broken = copy.deepcopy(self.contract)
                            target = broken["$defs"][definition_name]["oneOf"][option_index]
                            schema = target if key is None else target["properties"][key]
                            if mutation == "remove":
                                schema.pop("pattern")
                            else:
                                schema["pattern"] = r"\S"
                            errors = validate_contract_document(broken)
                            self.assertTrue(
                                any(
                                    f"{definition_name} definition differs" in error
                                    for error in errors
                                ),
                                errors,
                            )

    def test_canonical_and_compatibility_pairs_remain_valid(self):
        evidence = self.contract["$defs"]["evidence_target"]["oneOf"]
        confirmation = self.contract["$defs"]["confirmation_point"]["oneOf"]
        self.assertEqual(
            ["source_or_document_class", "exact_claim_or_metric"],
            evidence[0]["required"],
        )
        self.assertEqual(
            ["source_class", "verification_target"],
            evidence[1]["required"],
        )
        self.assertEqual(
            ["measurable_event_or_metric", "interpretation_effect"],
            confirmation[0]["required"],
        )
        self.assertEqual(
            ["confirmation_event", "confirm_weaken_invalidate"],
            confirmation[1]["required"],
        )
        self.assertEqual([], validate_contract_document(self.contract))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4844677489Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(TestReview4840844831Contracts().base_spec())

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_punctuated_placeholder_narratives_fail_closed(self):
        variants = (
            "not provided!",
            "“not provided”",
            "「not provided」",
            "not—provided",
        )
        for placeholder in variants:
            with self.subTest(placeholder=placeholder):
                spec = self.base_v3_spec()
                for field in lineage.STAGE_A_V3_NARRATIVE_FIELDS:
                    spec[field] = placeholder
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1, output)
                self.assertIn("must be item-specific narrative text", output)

    def test_non_string_anchor_classes_fail_without_type_error(self):
        for malformed in ([[]], [{}]):
            with self.subTest(malformed=malformed):
                spec = self.base_v3_spec()
                spec["anchor_classes"] = malformed
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1, output)
                self.assertIn("invalid non-execution anchor_classes", output)


if __name__ == "__main__":
    unittest.main()

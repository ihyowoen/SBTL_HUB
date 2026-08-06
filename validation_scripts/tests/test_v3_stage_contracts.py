from __future__ import annotations

import copy
import unittest
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as stage_validator
from validation_scripts import v3_stage_contracts


class V3StageContractGenerationTests(unittest.TestCase):
    def test_checked_in_projection_matches_canonical_schema(self):
        document = v3_stage_contracts.load_generated_stage_contract()
        self.assertEqual([], v3_stage_contracts.generated_stage_contract_errors(document))
        self.assertEqual(
            v3_stage_contracts.render_stage_contract_document(),
            v3_stage_contracts.DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"),
        )

    def test_all_operational_prompt_stages_are_projected(self):
        document = v3_stage_contracts.load_generated_stage_contract()
        expected = {
            "stage_a",
            "stage_b",
            "stage_c",
            "stage_b_revise",
            "stage_c_revise",
            "baseline_revalidation",
            "evidence_qc",
            "content_polish",
            "final_qc",
            "merge_prep",
            "production_verification",
        }
        self.assertEqual(expected, set(document["stages"]))
        for stage_name, stage in document["stages"].items():
            with self.subTest(stage=stage_name):
                self.assertEqual("#/canonical", stage["canonical_contract_ref"])
                self.assertTrue(Path(stage["prompt_path"]).is_file())
        self.assertEqual(
            "exactly_one", document["canonical"]["route_cardinality"]
        )
        self.assertEqual(
            ["execution", "v3_non_execution"],
            document["canonical"]["route_names"],
        )

    def test_public_stage_a_validator_consumes_generated_constants(self):
        expected = v3_stage_contracts.stage_a_validator_constants()
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(value, getattr(stage_validator, name))

    def test_tampered_generated_projection_is_rejected(self):
        document = v3_stage_contracts.load_generated_stage_contract()
        tampered = copy.deepcopy(document)
        tampered["canonical"]["route_cardinality"] = "at_least_one"
        self.assertTrue(v3_stage_contracts.generated_stage_contract_errors(tampered))

    def test_route_package_fields_cover_both_routes(self):
        document = v3_stage_contracts.load_generated_stage_contract()
        canonical = document["canonical"]
        preserve_fields = set(canonical["route_package_preserve_fields"])
        for fields in canonical["route_required_fields"].values():
            self.assertTrue(set(fields).issubset(preserve_fields))
        self.assertTrue(
            set(canonical["v3_override_required_fields"]).issubset(
                preserve_fields
            )
        )


if __name__ == "__main__":
    unittest.main()

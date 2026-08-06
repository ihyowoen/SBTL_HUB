from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
import textwrap
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

    def test_explicit_empty_projection_is_rejected(self):
        self.assertTrue(v3_stage_contracts.generated_stage_contract_errors({}))
        with self.assertRaises(ValueError):
            v3_stage_contracts.stage_a_validator_constants({})

    def test_public_validator_import_is_location_independent(self):
        validator_path = Path(stage_validator.__file__).resolve()
        repository_root = validator_path.parents[1]
        validation_dir = validator_path.parent
        script = textwrap.dedent(
            f"""
            import importlib.util
            import sys

            blocked = {{{str(repository_root)!r}, {str(validation_dir)!r}}}
            sys.path[:] = [entry for entry in sys.path if entry not in blocked]
            spec = importlib.util.spec_from_file_location(
                "external_stage_lineage_contract_check",
                {str(validator_path)!r},
            )
            if spec is None or spec.loader is None:
                raise RuntimeError("could not build validator spec")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            assert module.STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH
            """
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            completed = subprocess.run(
                [sys.executable, "-I", "-c", script],
                cwd=temp_dir,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(
            0,
            completed.returncode,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )

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

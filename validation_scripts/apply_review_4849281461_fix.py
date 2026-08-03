#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


generator = Path("validation_scripts/apply_prompt_contract_overlays.py")
replace_once(
    generator,
    "  `python validation_scripts/stage_artifact_contract_check.py A <STAGE_A_JSON>`.\n"
    "python validation_scripts/stage_lineage_contract_check.py stage_a <STAGE_A_JSON>`.\n",
    "  `python validation_scripts/stage_artifact_contract_check.py A <STAGE_A_JSON>`.\n"
    "  `python validation_scripts/stage_lineage_contract_check.py stage_a <STAGE_A_JSON>`.\n",
    "Stage A validator Markdown",
)

validator = Path("validation_scripts/stage_lineage_contract_check.py")
replace_once(
    validator,
    "    return _specific_string(value) and _has_any_term(value, STAGE_A_CONFIRMATION_EVENT_TERMS)\n",
    "    text = _normalized_text(value)\n"
    "    return (\n"
    "        bool(text)\n"
    "        and len(text.split()) >= 4\n"
    "        and not _placeholder_only_text(text)\n"
    "        and not _contains_generic_target_fragment(text)\n"
    "        and _has_any_term(text, STAGE_A_CONFIRMATION_EVENT_TERMS)\n"
    "    )\n",
    "free-text confirmation validation",
)

subprocess.run(
    [sys.executable, "validation_scripts/apply_prompt_contract_overlays.py", "--apply"],
    check=True,
)

Path("validation_scripts/tests/test_review_4849281461_contracts.py").write_text(
    '''from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4849281461Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(TestReview4840844831Contracts().base_spec())

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_stage_a_exit_commands_are_valid_markdown(self):
        expected = (
            "  `python validation_scripts/stage_lineage_contract_check.py "
            "stage_a <STAGE_A_JSON>`."
        )
        malformed = (
            "\\npython validation_scripts/stage_lineage_contract_check.py "
            "stage_a <STAGE_A_JSON>`."
        )
        for path in (
            Path("validation_scripts/apply_prompt_contract_overlays.py"),
            Path("docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md"),
        ):
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn(expected, text)
                self.assertNotIn(malformed, text)

    def test_specific_confirmation_with_generic_substring_passes(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [
            "Publication of additional data center capacity for Project Alpha would confirm adoption"
        ]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_placeholder_only_confirmation_still_fails(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = ["more evidence on adoption"]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1, output)
        self.assertIn("measurable events or metrics", output)


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)

original_workflow = '''name: Workflow contract validation

on:
  pull_request:
    paths:
      - "docs/RELATED_LIFECYCLE_CONTRACT.md"
      - "docs/SOURCE_AUDIT_CONTRACT.md"
      - "docs/llm_prompts/v1/**"
      - "validation_data/source_owner_registry.json"
      - "validation_scripts/**"
      - "scripts/lean_cards.mjs"
      - ".github/workflows/lean-cards.yml"
      - ".github/workflows/workflow-contract-validation.yml"
  push:
    branches:
      - agent/workflow-contract-related-source-audit
    paths:
      - "docs/RELATED_LIFECYCLE_CONTRACT.md"
      - "docs/SOURCE_AUDIT_CONTRACT.md"
      - "docs/llm_prompts/v1/**"
      - "validation_data/source_owner_registry.json"
      - "validation_scripts/**"
      - "scripts/lean_cards.mjs"
      - ".github/workflows/lean-cards.yml"
      - ".github/workflows/workflow-contract-validation.yml"

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Compile validators
        run: python -m compileall -q validation_scripts

      - name: Run workflow-contract and exporter regression tests
        run: python -m unittest discover -s validation_scripts/tests -v

      - name: Verify prompt overlays
        run: python validation_scripts/apply_prompt_contract_overlays.py --check
'''
Path(".github/workflows/workflow-contract-validation.yml").write_text(
    original_workflow,
    encoding="utf-8",
)
Path(__file__).unlink()

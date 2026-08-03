from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one target, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# P1: make the documented Stage A exit run the substantive V3 lineage validator.
exit_old = "python validation_scripts/stage_artifact_contract_check.py A <STAGE_A_OUTPUT.json>"
exit_new = (
    "python validation_scripts/stage_artifact_contract_check.py A <STAGE_A_OUTPUT.json>\n"
    "python validation_scripts/stage_lineage_contract_check.py stage_a <STAGE_A_OUTPUT.json>"
)
for path in (
    "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md",
    "validation_scripts/apply_prompt_contract_overlays.py",
):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if exit_new not in text:
        count = text.count(exit_old)
        if count < 1:
            raise SystemExit(f"{path}: Stage A exit command not found")
        p.write_text(text.replace(exit_old, exit_new), encoding="utf-8")

# P2: concise free-text source-class + exact metric should be accepted.
replace_once(
    "validation_scripts/stage_lineage_contract_check.py",
    "    return has_exact_metric_or_date or has_named_target\n\n\ndef _valid_confirmation_point",
    "    has_exact_metric_term = _has_any_term(target_text, STAGE_A_EXACT_TARGET_TERMS)\n"
    "    return has_exact_metric_or_date or has_named_target or has_exact_metric_term\n\n\ndef _valid_confirmation_point",
)

# P2: support ordinary participle/past-tense interpretation-effect forms while
# retaining complete-term boundaries and the source-class collision protections.
replace_once(
    "validation_scripts/stage_lineage_contract_check.py",
    "def _term_pattern(term):\n    escaped = re.escape(term)\n    if re.search(r'[가-힣]', term):",
    "def _term_pattern(term):\n"
    "    escaped = re.escape(term)\n"
    "    if term in STAGE_A_INTERPRETATION_EFFECT_TERMS and not re.search(r'[가-힣]', term):\n"
    "        irregular = {\n"
    "            'hold': r'(?:hold|holds|holding|held)',\n"
    "        }\n"
    "        if term in irregular:\n"
    "            body = irregular[term]\n"
    "        elif term.endswith('e'):\n"
    "            stem = re.escape(term[:-1])\n"
    "            body = rf'(?:{escaped}|{stem}es|{stem}ed|{stem}ing)'\n"
    "        else:\n"
    "            body = rf'(?:{escaped}|{escaped}s|{escaped}es|{escaped}ed|{escaped}ing)'\n"
    "        return rf'(?<![\\w]){body}(?![\\w])'\n"
    "    if re.search(r'[가-힣]', term):",
)

# Focused regression coverage.
test_path = Path("validation_scripts/tests/test_review_4848883611_contracts.py")
test_path.write_text('''from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4848883611Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(TestReview4840844831Contracts().base_spec())

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_stage_a_exit_runs_v3_lineage_validator(self):
        prompt = Path("docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md").read_text(encoding="utf-8")
        artifact = "python validation_scripts/stage_artifact_contract_check.py A <STAGE_A_OUTPUT.json>"
        lineage_cmd = "python validation_scripts/stage_lineage_contract_check.py stage_a <STAGE_A_OUTPUT.json>"
        self.assertIn(artifact, prompt)
        self.assertIn(lineage_cmd, prompt)
        self.assertLess(prompt.index(artifact), prompt.index(lineage_cmd))

    def test_concise_free_text_exact_metrics_are_accepted(self):
        for target in ("official revenue", "filing margin"):
            with self.subTest(target=target):
                spec = self.base_v3_spec()
                spec["evidence_needed_for_stage_b"] = [target]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 0, output)

    def test_interpretation_effect_inflections_are_accepted(self):
        variants = (
            "would be confirmed",
            "confirmed thesis",
            "would be weakened",
            "invalidated thesis",
        )
        for effect in variants:
            with self.subTest(effect=effect):
                spec = self.base_v3_spec()
                spec["next_confirmation_points"] = [{
                    "measurable_event_or_metric": "2027 revenue",
                    "interpretation_effect": effect,
                }]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 0, output)

    def test_complete_term_boundaries_remain_fail_closed(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "2027 revenue",
            "interpretation_effect": "unchanged thesis",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1, output)
        self.assertIn("invalid next_confirmation_points", output)


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

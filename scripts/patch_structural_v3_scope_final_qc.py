#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD = """- Run `evidence_qc_v8_check.py`, `related_lifecycle_check.py --require-contract`,
  `date_role_freshness_check.py --require-date-role`, and
  `stage_artifact_contract_check.py 0.7` before `publish_ready=true`."""
NEW = """- Build a merged baseline/candidate validation artifact so every current-run card and every referenced Related target is resolvable.
- Build `CURRENT_RUN_ID_FILE` containing only the production IDs / candidate IDs introduced or materially updated by the current run.
- Run `evidence_qc_v8_check.py`,
  `related_lifecycle_check.py --require-contract --new-id-file <CURRENT_RUN_ID_FILE>` against the merged baseline/candidate validation artifact,
  `date_role_freshness_check.py --require-date-role`, and
  `stage_artifact_contract_check.py 0.7` before `publish_ready=true`.
- Do not apply `--require-contract` unscoped to the full legacy inventory; strict V3 fields are current-run obligations while legacy rows remain under the legacy-compatible check."""

for rel in [
    "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
    "validation_scripts/apply_prompt_contract_overlays.py",
]:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(OLD)
    if count != 1:
        raise SystemExit(f"{rel}: expected one unscoped Final QC block, found {count}")
    path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")

# Update the focused regression from the now-superseded unscoped strict call
# to the current-run scoped contract required by this review.
test_path = ROOT / "validation_scripts/tests/test_review_4839991362_contracts.py"
test_text = test_path.read_text(encoding="utf-8")
old_test = '''    def test_final_qc_uses_strict_related_contract_in_prompt_and_generator(self) -> None:
        expected = "`related_lifecycle_check.py --require-contract`"
        old = "`related_lifecycle_check.py`,"
        for path in (
            "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
            "validation_scripts/apply_prompt_contract_overlays.py",
        ):
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(expected, text)
            self.assertNotIn(old, text)
'''
new_test = '''    def test_final_qc_uses_current_run_scoped_strict_related_contract(self) -> None:
        scoped = "`related_lifecycle_check.py --require-contract --new-id-file <CURRENT_RUN_ID_FILE>`"
        unscoped = "`related_lifecycle_check.py --require-contract`,"
        for path in (
            "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
            "validation_scripts/apply_prompt_contract_overlays.py",
        ):
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(scoped, text)
            self.assertIn("merged baseline/candidate validation artifact", text)
            self.assertIn("Do not apply `--require-contract` unscoped", text)
            self.assertNotIn(unscoped, text)
'''
if test_text.count(old_test) != 1:
    raise SystemExit("focused review test: expected exactly one old unscoped test block")
test_path.write_text(test_text.replace(old_test, new_test, 1), encoding="utf-8")

log = ROOT / "docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md"
with log.open("a", encoding="utf-8") as f:
    f.write("""

## Review 4839991362 follow-up: current-run strict scope

- Prompt 0.7 now runs the strict Related lifecycle validator with `--new-id-file <CURRENT_RUN_ID_FILE>`.
- The validator runs against a merged baseline/candidate artifact so Related targets remain resolvable.
- Unscoped strict validation of the full legacy inventory is explicitly forbidden; legacy-compatible validation remains unchanged.
- The overlay generator carries the identical scoped command.
- Focused regression coverage now rejects the superseded unscoped strict invocation.
""")

# Restore the canonical validation workflow after using it as a one-shot patch runner.
(ROOT / ".github/workflows/workflow-contract-validation.yml").write_text("""name: Workflow contract validation

on:
  pull_request:
    paths:
      - \"docs/RELATED_LIFECYCLE_CONTRACT.md\"
      - \"docs/SOURCE_AUDIT_CONTRACT.md\"
      - \"docs/llm_prompts/v1/**\"
      - \"validation_data/source_owner_registry.json\"
      - \"validation_scripts/**\"
      - \"scripts/lean_cards.mjs\"
      - \".github/workflows/lean-cards.yml\"
      - \".github/workflows/workflow-contract-validation.yml\"
  push:
    branches:
      - agent/workflow-contract-related-source-audit
    paths:
      - \"docs/RELATED_LIFECYCLE_CONTRACT.md\"
      - \"docs/SOURCE_AUDIT_CONTRACT.md\"
      - \"docs/llm_prompts/v1/**\"
      - \"validation_data/source_owner_registry.json\"
      - \"validation_scripts/**\"
      - \"scripts/lean_cards.mjs\"
      - \".github/workflows/lean-cards.yml\"
      - \".github/workflows/workflow-contract-validation.yml\"

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
          python-version: \"3.12\"

      - name: Compile validators
        run: python -m compileall -q validation_scripts

      - name: Run workflow-contract and exporter regression tests
        run: python -m unittest discover -s validation_scripts/tests -v

      - name: Verify prompt overlays
        run: python validation_scripts/apply_prompt_contract_overlays.py --check
""", encoding="utf-8")

(ROOT / "scripts/patch_structural_v3_scope_final_qc.py").unlink()
(ROOT / ".github/workflows/patch-final-qc-scope.yml").unlink()

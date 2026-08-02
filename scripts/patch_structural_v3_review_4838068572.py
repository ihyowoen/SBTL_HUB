#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_exact(text: str, old: str, new: str, label: str, expected: int = 1) -> str:
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"{label}: expected {expected} match(es), found {count}")
    return text.replace(old, new)


def replace_regex(text: str, pattern: str, replacement: str, label: str, expected: int = 1) -> str:
    updated, count = re.subn(pattern, replacement, text, flags=re.S)
    if count != expected:
        raise RuntimeError(f"{label}: expected {expected} match(es), found {count}")
    return updated


OLD_DOCS = """1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md"""

NEW_DOCS = """1. docs/FACT_DISCIPLINE.md
2. docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
3. docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md
4. docs/PROMPT_ABC_DEFAULT_MODE.md
5. docs/PROMPT_ABC_SUPPORTING_RULES.md
6. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
7. docs/CARD_ID_STANDARD.md
8. docs/WORKFLOW.md
9. docs/OPERATIONS.md
10. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md"""


def upgrade_required_docs(text: str, label: str) -> str:
    count = text.count(OLD_DOCS)
    if count < 1:
        raise RuntimeError(f"{label}: old required-doc block not found")
    text = text.replace(OLD_DOCS, NEW_DOCS)
    text = text.replace("All 8 documents above are mandatory.", "All 10 documents above are mandatory.")
    text = text.replace("list all 8 required docs", "list all 10 required docs")
    return text


# Stage C producer schema must materialize the selected anchor path.
stage_c_path = "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md"
stage_c = read(stage_c_path)
stage_c = replace_exact(
    stage_c,
    """- related
- fact_sources
- stage_c_findings""",
    """- related
- fact_sources
- anchor_path_validation
  - selected_anchor_path: execution|v3_non_execution
  - anchor_path_qc_passed: true
  - execution_anchor_qc_status: pass|not_applicable
  - structural_value_override_qc_status: pass|not_applicable
  - non_applicable_anchor_path_reason
- stage_c_findings""",
    "Stage C accepted_fact_safe anchor-path schema",
)
write(stage_c_path, stage_c)


# Prompt 0.4 must require and preserve Stage C anchor-path validation.
baseline_path = "docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md"
baseline = upgrade_required_docs(read(baseline_path), "Prompt 0.4 required docs")
baseline = replace_exact(
    baseline,
    """- accepted_fact_safe[]
- revise_required[]""",
    """- accepted_fact_safe[]
- every format-risk accepted_fact_safe item carries anchor_path_validation
- revise_required[]""",
    "Prompt 0.4 Stage C input contract",
)
baseline = replace_exact(
    baseline,
    """- no baseline revalidation work performed

If any supplied Stage C revise JSON""",
    """- no baseline revalidation work performed

For every format-risk `accepted_fact_safe[]` item, require a complete Stage C `anchor_path_validation` object with exactly one selected route, a passing `anchor_path_qc_passed`, coherent execution/non-execution route statuses, and a specific non-applicable-route reason. Missing, contradictory, or stale anchor-path metadata is `BLOCKED_STAGE_C_ANCHOR_PATH_MISSING`; do not reconstruct it from prose.

If any supplied Stage C revise JSON""",
    "Prompt 0.4 anchor-path preflight",
)
baseline = replace_exact(
    baseline,
    """For every addable_merge_safe item, set:

- evidence_complete: false
- source_claim_covered: false
- needs_evidence_completeness_qc: true
- needs_source_claim_coverage_qc: true""",
    """For every addable_merge_safe item, set:

- evidence_complete: false
- source_claim_covered: false
- needs_evidence_completeness_qc: true
- needs_source_claim_coverage_qc: true

Anchor-path preservation rule:

- copy Stage C `anchor_path_validation` byte-for-byte into every format-risk `addable_merge_safe[]` item;
- do not switch `selected_anchor_path`, alter either route status, or replace the non-applicable-route reason during baseline comparison;
- if the metadata is absent or conflicts with Stage C, route to `baseline_conflict` with `conflict_type: anchor_path_lineage_conflict` and do not send the item to Evidence QC.""",
    "Prompt 0.4 anchor-path preservation rule",
)
baseline = replace_exact(
    baseline,
    """- related
- fact_sources
- event_fingerprint""",
    """- related
- fact_sources
- anchor_path_validation
  - selected_anchor_path: execution|v3_non_execution
  - anchor_path_qc_passed: true
  - execution_anchor_qc_status: pass|not_applicable
  - structural_value_override_qc_status: pass|not_applicable
  - non_applicable_anchor_path_reason
- event_fingerprint""",
    "Prompt 0.4 addable schema",
)
baseline = replace_exact(
    baseline,
    """- event_fingerprint_summary
- id_collision_summary
- addable_merge_safe[]""",
    """- event_fingerprint_summary
- id_collision_summary
- anchor_path_preservation_summary
- addable_merge_safe[]""",
    "Prompt 0.4 root summary",
)
baseline = replace_exact(
    baseline,
    """- id_collision
- publish_ready_reset
- reason""",
    """- id_collision
- anchor_path_preserved
- publish_ready_reset
- reason""",
    "Prompt 0.4 decision ledger",
)
write(baseline_path, baseline)


V3_OVERLAY = """## Anchor-path and selector-lineage safety overlay — V3

This overlay prevents valid V3 non-execution cards from being misclassified after Final QC while still blocking unsupported or superseded lineage.

Terminology lock:

- Do not use or enforce a format-based hard-exclude rule.
- Product, demo, PoC, component, interview, commentary, roundup, speech, or personnel formats are not automatically rejected by format alone.
- A format-risk card is valid only when exactly one source-backed route passed the upstream workflow: a concrete execution anchor or a complete V3 non-execution Structural Value Override.
- The selected route, route-specific statuses, non-applicable-route reason, narrowed visible wording, and source coverage must remain consistent through production verification and remediation.
- A valid V3 non-execution route is not a selector-lineage defect merely because no conventional execution event exists.

"""

# Prompt 0.9 must verify both valid routes in production.
production_path = "docs/llm_prompts/v1/11_PROMPT_0_9_Production_Verification.md"
production = upgrade_required_docs(read(production_path), "Prompt 0.9 required docs")
production = replace_regex(
    production,
    r"## Execution-anchor and selector-lineage safety overlay — 2026-05-05\n.*?(?=### Production lineage verification gate)",
    V3_OVERLAY,
    "Prompt 0.9 V3 overlay",
)
production = replace_exact(
    production,
    """- format-risk cards still preserve the narrowed stage/caveat language approved by Final QC.""",
    """- format-risk cards still preserve the narrowed stage/caveat language approved by Final QC;
- every format-risk card preserves `selected_anchor_path`, `anchor_path_qc_passed`, both route statuses, and the specific non-applicable-route reason from Final QC and Merge Prep;
- execution-path cards retain source-backed execution evidence;
- V3 non-execution cards retain the verified anchor class, evidence targets, before-after chain, changed judgment, and `why_execution_event_not_required` without being reclassified as execution-defective.""",
    "Prompt 0.9 production lineage checks",
)
production = replace_exact(
    production,
    """  \"format_risk_cards_render_checked_count\": 0,
  \"decision\": \"pass|production_hold\"""",
    """  \"format_risk_cards_render_checked_count\": 0,
  \"execution_path_cards_checked_count\": 0,
  \"v3_non_execution_path_cards_checked_count\": 0,
  \"anchor_path_metadata_mismatch_count\": 0,
  \"decision\": \"pass|production_hold\"""",
    "Prompt 0.9 output schema",
)
write(production_path, production)


# Prompt 1.0 must remediate actual route defects, not valid non-execution cards.
remediation_path = "docs/llm_prompts/v1/12_PROMPT_1_0_Remediation.md"
remediation = upgrade_required_docs(read(remediation_path), "Prompt 1.0 required docs")
remediation = remediation.replace("Stage A V2 selector safety", "Stage A V3 selector and anchor-path safety")
remediation = replace_regex(
    remediation,
    r"## Execution-anchor and selector-lineage safety overlay — 2026-05-05\n.*?(?=### Remediation rule for selector-lineage or execution-anchor issues)",
    V3_OVERLAY,
    "Prompt 1.0 V3 overlay",
)
remediation = remediation.replace(
    "### Remediation rule for selector-lineage or execution-anchor issues",
    "### Remediation rule for selector-lineage or anchor-path issues",
)
remediation = replace_exact(
    remediation,
    """If Production Verification reports `selector_lineage_or_anchor_integrity_issue`, classify it as a data integrity issue, not a cosmetic rendering issue.""",
    """If Production Verification reports `selector_lineage_or_anchor_integrity_issue`, classify it as a data integrity issue, not a cosmetic rendering issue. Confirm first that the issue is a real selected-route, route-status, source-coverage, or lineage mismatch; a valid source-backed V3 non-execution route without a conventional execution event is not itself an integrity issue.""",
    "Prompt 1.0 remediation classification",
)
remediation = replace_exact(
    remediation,
    """  \"earliest_invalid_stage\": null,
  \"recommended_safe_action\": null,
  \"rollback_review_required\": false""",
    """  \"earliest_invalid_stage\": null,
  \"selected_anchor_path\": \"execution|v3_non_execution|unknown\",
  \"anchor_path_defect_confirmed\": false,
  \"recommended_safe_action\": null,
  \"rollback_review_required\": false""",
    "Prompt 1.0 output schema",
)
write(remediation_path, remediation)


# Restore the pre-existing legacy fresh-anchor check while gating only V2 additions.
validator_path = "validation_scripts/related_lifecycle_check.py"
validator = read(validator_path)
validator = replace_exact(
    validator,
    """    if require_contract and relation_type == \"distinct_follow_up\":
        if not lineage.get(\"fresh_follow_up_anchor\"):
            errors.append(\"distinct_follow_up requires fresh_follow_up_anchor\")
        anchor_class = lineage.get(\"fresh_follow_up_anchor_class\")""",
    """    if relation_type == \"distinct_follow_up\" and not lineage.get(\"fresh_follow_up_anchor\"):
        errors.append(\"distinct_follow_up requires fresh_follow_up_anchor\")
    if require_contract and relation_type == \"distinct_follow_up\":
        anchor_class = lineage.get(\"fresh_follow_up_anchor_class\")""",
    "Related legacy fresh-anchor check",
)
write(validator_path, validator)


# Regression tests for producer/consumer preservation, production gates, and legacy validation.
tests_path = "validation_scripts/tests/test_workflow_contracts.py"
tests = read(tests_path)
tests = replace_exact(
    tests,
    """    def test_duplicate_cannot_publish(self):""",
    """    def test_legacy_mode_still_requires_fresh_follow_up_anchor(self):
        child = deepcopy(self.child)
        child[\"related_lineage\"].pop(\"fresh_follow_up_anchor\")
        by_id = {self.parent[\"id\"]: self.parent, child[\"id\"]: child}
        errors, _ = check_card(child, by_id, False)
        self.assertTrue(any(\"fresh_follow_up_anchor\" in error for error in errors))

    def test_duplicate_cannot_publish(self):""",
    "Legacy fresh-anchor regression test",
)
tests = replace_exact(
    tests,
    """    def test_final_qc_consumes_route_status_schema(self):""",
    """    def test_stage_c_and_baseline_revalidation_preserve_anchor_path(self):
        stage_c = self.read_prompt(\"docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md\")
        baseline = self.read_prompt(\"docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md\")
        self.assertIn(\"Each accepted_fact_safe item must include:\", stage_c)
        self.assertIn(\"anchor_path_validation\", stage_c)
        self.assertIn(\"All 10 documents above are mandatory.\", baseline)
        self.assertIn(\"copy Stage C `anchor_path_validation` byte-for-byte\", baseline)
        self.assertIn(\"anchor_path_preservation_summary\", baseline)
        self.assertIn(\"anchor_path_preserved\", baseline)

    def test_production_and_remediation_accept_both_anchor_paths(self):
        production = self.read_prompt(\"docs/llm_prompts/v1/11_PROMPT_0_9_Production_Verification.md\")
        remediation = self.read_prompt(\"docs/llm_prompts/v1/12_PROMPT_1_0_Remediation.md\")
        for text in (production, remediation):
            self.assertIn(\"All 10 documents above are mandatory.\", text)
            self.assertIn(\"exactly one source-backed route\", text)
            self.assertIn(\"valid V3 non-execution route\", text)
            self.assertNotIn(\"without a concrete fresh execution anchor, they must not have entered\", text)
        self.assertIn(\"v3_non_execution_path_cards_checked_count\", production)
        self.assertIn(\"anchor_path_defect_confirmed\", remediation)

    def test_final_qc_consumes_route_status_schema(self):""",
    "Downstream production regression tests",
)
write(tests_path, tests)


# Record review closure and remove the one-shot machinery from the final tree.
validation_path = "docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md"
validation = read(validation_path)
validation += """

## Review 4838068572 end-to-end lineage closure

- Stage C's mandatory `accepted_fact_safe[]` schema now emits `anchor_path_validation`.
- Prompt 0.4 requires that object on format-risk inputs and preserves it byte-for-byte into `addable_merge_safe[]`; missing or contradictory metadata is blocked before Evidence QC.
- Prompt 0.9 verifies both execution and V3 non-execution routes after merge and does not misclassify a valid non-execution route as an execution defect.
- Prompt 1.0 remediates confirmed selected-route, route-status, source-coverage, or lineage defects only.
- The legacy `distinct_follow_up` fresh-anchor presence check remains unconditional; only the new V2 class, incremental-fact, and changed-judgment requirements are scoped to `--require-contract`.
- Regression tests cover Stage C → Prompt 0.4 preservation, production/remediation two-path handling, and legacy fresh-anchor enforcement.
"""
write(validation_path, validation)

for temporary in (
    ROOT / "scripts/patch_structural_v3_review_4838068572.py",
    ROOT / ".github/workflows/patch-structural-v3-review-4838068572.yml",
):
    if temporary.exists():
        temporary.unlink()

print("PASS: review 4838068572 patch applied")

#!/usr/bin/env python3
# Trigger verified patch workflow after workflow installation.
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# 1) Make the documented Final QC command executable and provide its required input.
old_cmd = "`related_lifecycle_check.py --require-contract --allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>` against the merged baseline/candidate validation artifact,"
new_cmd = "`python validation_scripts/related_lifecycle_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-contract --allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>`,"
for path in (
    "validation_scripts/apply_prompt_contract_overlays.py",
    "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
):
    replace_once(path, old_cmd, new_cmd)

# 2) Bare metric/event vocabulary is not item-specific enough by itself.
semantic_path = "validation_scripts/stage_lineage_contract_check_semantic.py"
old_return = '''    return (
        is_explicit_date
        or has_qualified_numeric_target
        or has_exact_role
        or has_event_role
        or has_predicate_role
    )
'''
new_return = '''    generic_role_tokens = set()
    for term in (
        tuple(_base.STAGE_A_EXACT_TARGET_TERMS)
        + tuple(_base.STAGE_A_CONFIRMATION_EVENT_TERMS)
        + tuple(_base.STAGE_A_SUBSTANTIVE_TARGET_PREDICATE_TERMS)
    ):
        generic_role_tokens.update(_base.re.findall(r"[a-z0-9가-힣]+", _base._normalized_text(term)))
    generic_role_tokens.update({
        "and", "or", "the", "a", "an", "of", "for", "to", "in", "on",
        "at", "by", "from", "with", "was", "were", "is", "are", "be",
        "및", "또는", "의", "에", "에서", "대한",
    })
    has_named_or_item_specific_subject = any(
        token not in generic_role_tokens and not token.isdigit()
        for token in tokens
    )
    has_substantive_role = has_exact_role or has_event_role or has_predicate_role
    return (
        is_explicit_date
        or has_qualified_numeric_target
        or (has_substantive_role and has_named_or_item_specific_subject)
    )
'''
replace_once(semantic_path, old_return, new_return)

# 3) Strict follow-up assertions must be item-specific, not generic lineage scaffolding.
related_path = "validation_scripts/related_lifecycle_check.py"
anchor = '''FRESH_FOLLOW_UP_ANCHOR_CLASSES = {
    "execution_event_anchor",
    "policy_regulatory_anchor",
    "data_financial_anchor",
    "strategic_behavior_anchor",
    "technology_commercialization_anchor",
    "follow_up_probability_anchor",
}
'''
helper = anchor + '''
_GENERIC_LINEAGE_ASSERTION_TOKENS = {
    "same", "project", "topic", "event", "related", "follow", "followup",
    "up", "update", "updated", "new", "information", "evidence", "fact",
    "incremental", "changed", "judgment", "judgement", "anchor", "fresh",
    "tbd", "none", "na", "n", "a", "sameproject", "sametopic",
    "동일", "프로젝트", "주제", "사건", "관련", "후속", "업데이트",
    "신규", "정보", "근거", "사실", "증분", "판단", "변경", "앵커",
    "미정", "없음",
}
_GENERIC_LINEAGE_ASSERTION_PHRASES = {
    "same project", "same topic", "same event", "related event",
    "follow up", "follow-up", "new information", "new evidence",
    "incremental fact", "changed judgment", "changed judgement",
    "fresh anchor", "same project update", "same topic update",
    "동일 프로젝트", "동일 주제", "관련 사건", "후속 업데이트",
    "신규 정보", "신규 근거", "증분 사실", "판단 변경",
}


def item_specific_lineage_assertion(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = re.sub(r"[^a-z0-9가-힣]+", " ", value.casefold()).strip()
    if not normalized or normalized in _GENERIC_LINEAGE_ASSERTION_PHRASES:
        return False
    tokens = [token for token in normalized.split() if token]
    if not tokens or all(token in _GENERIC_LINEAGE_ASSERTION_TOKENS for token in tokens):
        return False
    return True
'''
replace_once(related_path, anchor, helper)

old_contract = '''        incremental_fact = lineage.get("incremental_fact_vs_predecessor")
        if not isinstance(incremental_fact, str) or not incremental_fact.strip():
            errors.append("distinct_follow_up requires incremental_fact_vs_predecessor")
        changed_judgment = lineage.get("changed_judgment_vs_predecessor")
        if not isinstance(changed_judgment, str) or not changed_judgment.strip():
            errors.append("distinct_follow_up requires changed_judgment_vs_predecessor")
'''
new_contract = '''        fresh_anchor = lineage.get("fresh_follow_up_anchor")
        if not item_specific_lineage_assertion(fresh_anchor):
            errors.append("distinct_follow_up requires item-specific fresh_follow_up_anchor")
        incremental_fact = lineage.get("incremental_fact_vs_predecessor")
        if not item_specific_lineage_assertion(incremental_fact):
            errors.append("distinct_follow_up requires item-specific incremental_fact_vs_predecessor")
        changed_judgment = lineage.get("changed_judgment_vs_predecessor")
        if not item_specific_lineage_assertion(changed_judgment):
            errors.append("distinct_follow_up requires item-specific changed_judgment_vs_predecessor")
'''
replace_once(related_path, old_contract, new_contract)

# Focused regression coverage.
test_path = Path("validation_scripts/tests/test_review_4851050000_contracts.py")
test_path.write_text('''from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4851050000Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_bare_target_vocabulary_is_not_item_specific(self):
        for value in ("revenue", "margin", "capacity", "launch"):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_item_specific_or_qualified_targets_remain_valid(self):
        for value in (
            "Project Alpha revenue",
            "Project Alpha capacity",
            "2027 revenue",
            "Project Alpha was approved",
            "Project Alpha launch date",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_bare_structured_evidence_and_confirmation(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "revenue",
            "interpretation_effect": "would weaken the demand outlook",
        }]
        messages = []
        self.assertFalse(lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages))

    def test_generic_follow_up_assertions_fail(self):
        for value in ("same project", "same topic", "new evidence", "follow-up"):
            with self.subTest(value=value):
                self.assertFalse(related.item_specific_lineage_assertion(value))

    def test_item_specific_follow_up_assertions_pass(self):
        for value in (
            "DOE final rule moved Project Alpha eligibility to the effective stage",
            "The August filing added a 6 GWh contracted volume versus the predecessor",
            "The judgment changed from announced target to financed execution",
        ):
            with self.subTest(value=value):
                self.assertTrue(related.item_specific_lineage_assertion(value))

    def test_final_qc_overlay_contains_executable_merged_artifact_command(self):
        expected = (
            "python validation_scripts/related_lifecycle_check.py "
            "<MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-contract "
            "--allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>"
        )
        for path in (
            "validation_scripts/apply_prompt_contract_overlays.py",
            "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
        ):
            with self.subTest(path=path):
                text = open(path, encoding="utf-8").read()
                self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")

#!/usr/bin/env python3
from __future__ import annotations

# Triggered after the temporary workflow exists on the PR branch.
from pathlib import Path


def replace_once(path: str, old: str, new: str, label: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "validation_scripts/stage_lineage_contract_check.py",
    """    format_risk_tags = spec.get('format_risk_tags')
    has_format_risk = isinstance(format_risk_tags, list) and bool(format_risk_tags)
""",
    """    format_risk_tags = spec.get('format_risk_tags')
    if not isinstance(format_risk_tags, list):
        messages.append(f'{spec_id}: format_risk_tags must be an array')
        has_format_risk = False
    else:
        has_format_risk = bool(format_risk_tags)
""",
    "Stage A format_risk_tags type gate",
)

for prompt_path in (
    "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md",
    "docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md",
):
    replace_once(
        prompt_path,
        """- `changed_judgment`
- applicable uncertainty / probability-change fields
- applicable baseline-expectation / before-after fields
""",
        """- `changed_judgment`
- `uncertainty_resolved`
- `remaining_uncertainty`
- applicable probability-change fields
- applicable baseline-expectation / before-after fields
""",
        f"Exact uncertainty fields in {prompt_path}",
    )

replace_once(
    "validation_scripts/related_lifecycle_check.py",
    """    provisional = (
        lineage.get(\"related_candidate_spec_ids\")
        or card.get(\"related_candidate_spec_ids\")
        or []
    )
""",
    """    lineage_provisional = lineage.get(\"related_candidate_spec_ids\")
    card_provisional = card.get(\"related_candidate_spec_ids\")
    lineage_has_provisional = lineage_provisional not in (None, [])
    card_has_provisional = card_provisional not in (None, [])

    if lineage_has_provisional and card_has_provisional:
        if not isinstance(lineage_provisional, list) or not isinstance(card_provisional, list):
            errors.append(
                \"related_candidate_spec_ids representations must both be arrays when both are populated\"
            )
            provisional = lineage_provisional if isinstance(lineage_provisional, list) else card_provisional
        elif lineage_provisional != card_provisional:
            errors.append(
                \"conflicting related_candidate_spec_ids between related lifecycle and card root\"
            )
            provisional = dedupe(lineage_provisional + card_provisional)
        else:
            provisional = lineage_provisional
    elif lineage_has_provisional:
        provisional = lineage_provisional
    elif card_has_provisional:
        provisional = card_provisional
    else:
        provisional = []
""",
    "Provisional-edge container consistency",
)

Path("validation_scripts/tests/test_review_20260803_run4.py").write_text(
    '''#!/usr/bin/env python3
from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.related_lifecycle_check import check_card
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class StageAFormatRiskTypeTest(unittest.TestCase):
    def test_non_array_format_risk_tags_fail_closed(self):
        spec = copy.deepcopy(TestReview4840844831Contracts().base_spec())
        spec["format_risk_tags"] = "interview"
        spec["execution_anchor_type"] = "commercial_award"
        spec["execution_anchor_strength"] = "strong"
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        output = stream.getvalue()
        self.assertEqual(result, 1)
        self.assertIn("format_risk_tags must be an array", output)


class ProvisionalContainerConsistencyTest(unittest.TestCase):
    def test_conflicting_lineage_and_root_provisional_edges_fail(self):
        parent = {
            "id": "PARENT",
            "draft_id": "PD",
            "date": "2026-08-01",
            "related": [],
        }
        child = {
            "id": "CHILD",
            "date": "2026-08-02",
            "related": [],
            "related_candidate_spec_ids": ["MISSING"],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "program_lineage",
                "related_ids": [],
                "related_candidate_spec_ids": ["PD"],
                "reason": "same governed program",
            },
        }
        errors, _ = check_card(
            child,
            {"PARENT": parent, "CHILD": child},
            True,
            allow_provisional_related=True,
            provisional_by_id={"PD": parent},
            ambiguous_provisional_ids=set(),
        )
        self.assertTrue(any(
            "conflicting related_candidate_spec_ids" in error for error in errors
        ))
        self.assertTrue(any(
            "dangling provisional related ID: MISSING" in error for error in errors
        ))

    def test_matching_duplicate_representations_are_allowed(self):
        parent = {
            "id": "PARENT",
            "draft_id": "PD",
            "date": "2026-08-01",
            "related": [],
        }
        child = {
            "id": "CHILD",
            "date": "2026-08-02",
            "related": [],
            "related_candidate_spec_ids": ["PD"],
            "related_lineage": {
                "status": "PASS",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "relation_type": "program_lineage",
                "related_ids": [],
                "related_candidate_spec_ids": ["PD"],
                "reason": "same governed program",
            },
        }
        errors, _ = check_card(
            child,
            {"PARENT": parent, "CHILD": child},
            True,
            allow_provisional_related=True,
            provisional_by_id={"PD": parent},
            ambiguous_provisional_ids=set(),
        )
        self.assertFalse(any("conflicting related_candidate_spec_ids" in error for error in errors))
        self.assertFalse(any("dangling provisional related ID" in error for error in errors))


class UpstreamUncertaintyFieldPreservationTest(unittest.TestCase):
    def test_evidence_qc_and_content_polish_name_both_fields(self):
        for path in (
            Path("docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md"),
            Path("docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md"),
        ):
            text = path.read_text(encoding="utf-8")
            self.assertIn("- `uncertainty_resolved`", text)
            self.assertIn("- `remaining_uncertainty`", text)
            self.assertNotIn("applicable uncertainty / probability-change fields", text)


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


stage = ROOT / "validation_scripts/stage_lineage_contract_check.py"
replace_once(
    stage,
    """    'dummy', 'text', 'n/a', 'na', 'nil', 'yet', 'unavailable', 'undisclosed',\n    'missing', 'unknown', '미제공', '미공개', '비공개', '정보', '자료', '내용',\n    '없음', '해당', '확인', '불가', '아직',\n""",
    """    'dummy', 'text', 'n/a', 'na', 'nil', 'yet', 'unavailable', 'undisclosed',\n    'missing', 'unknown', 'currently', 'still', 'presently', 'current',\n    'present', 'at', 'as', 'of', 'now', 'this', 'time', 'remains', 'remaining',\n    'undetermined', 'unconfirmed', 'unverified', 'unclear', 'pending',\n    '미제공', '미공개', '비공개', '정보', '자료', '내용', '없음', '해당',\n    '확인', '불가', '아직', '현재', '여전히', '미정', '미확인', '불명',\n""",
    "expand modified placeholder token coverage",
)

related = ROOT / "validation_scripts/related_lifecycle_check.py"
replace_once(
    related,
    """import json\nimport sys\nfrom pathlib import Path\n""",
    """import json\nimport re\nimport sys\nfrom pathlib import Path\n""",
    "import re for chronology specificity",
)
replace_once(
    related,
    """def validate_follow_up_chronology_justification(\n    lineage: dict[str, Any],\n) -> tuple[set[str], str | None]:\n""",
    """CHRONOLOGY_GENERIC_TEMPLATE_PHRASES = (\n    \"specific explanation of what event the earlier date represents\",\n    \"specific explanation of why the earlier representative date remains a later distinct follow-up judgment\",\n    \"what event the earlier date represents\",\n    \"why the earlier representative date remains\",\n    \"generic explanation\",\n)\nCHRONOLOGY_GENERIC_TOKENS = {\n    'a', 'an', 'and', 'as', 'at', 'be', 'because', 'card', 'date', 'distinct',\n    'earlier', 'event', 'explanation', 'follow', 'for', 'generic', 'how', 'is',\n    'it', 'judgment', 'later', 'of', 'or', 'reason', 'remain', 'remains',\n    'representative', 'represents', 'specific', 'that', 'the', 'this', 'to',\n    'up', 'what', 'why', 'basis', 'chronology', 'predecessor', 'related',\n    'same', 'project', '대표일', '이전', '날짜', '사건', '설명', '사유',\n    '근거', '후속', '판단', '동일', '프로젝트',\n}\n\n\ndef _specific_chronology_text(value: Any, minimum_content_tokens: int = 2) -> bool:\n    if not isinstance(value, str):\n        return False\n    normalized = ' '.join(value.strip().lower().split())\n    if len(normalized) < 12:\n        return False\n    if any(phrase in normalized for phrase in CHRONOLOGY_GENERIC_TEMPLATE_PHRASES):\n        return False\n    tokens = re.findall(r'[a-z0-9가-힣]+', normalized)\n    content_tokens = {\n        token for token in tokens\n        if token not in CHRONOLOGY_GENERIC_TOKENS and not token.isdigit()\n    }\n    return len(content_tokens) >= minimum_content_tokens\n\n\ndef validate_follow_up_chronology_justification(\n    lineage: dict[str, Any],\n) -> tuple[set[str], str | None]:\n""",
    "add chronology specificity helper",
)
replace_once(
    related,
    """    basis = value.get(\"representative_date_basis\")\n    reason = value.get(\"reason\")\n    if not isinstance(basis, str) or len(basis.strip()) < 12:\n        return set(), \"follow-up chronology justification requires a specific representative_date_basis\"\n    if not isinstance(reason, str) or len(reason.strip()) < 20:\n        return set(), \"follow-up chronology justification requires a specific reason\"\n\n""",
    """    basis = value.get(\"representative_date_basis\")\n    reason = value.get(\"reason\")\n    if not _specific_chronology_text(basis):\n        return set(), \"follow-up chronology justification requires an item-specific representative_date_basis\"\n    if not _specific_chronology_text(reason):\n        return set(), \"follow-up chronology justification requires an item-specific reason\"\n    if ' '.join(basis.strip().lower().split()) == ' '.join(reason.strip().lower().split()):\n        return set(), \"follow-up chronology basis and reason must be independently specific\"\n\n""",
    "reject generic chronology scaffolding",
)

test = ROOT / "validation_scripts/tests/test_review_4842006582_contracts.py"
test.write_text('''"""Regression coverage for Codex review 4842006582."""\n\nfrom __future__ import annotations\n\nimport copy\nimport io\nimport sys\nimport unittest\nfrom contextlib import redirect_stdout\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n\nfrom validation_scripts import related_lifecycle_check as related\nfrom validation_scripts import stage_lineage_contract_check as lineage\nfrom validation_scripts.tests.test_review_4840844831_contracts import (\n    TestReview4840844831Contracts,\n)\nfrom validation_scripts.tests.test_review_4841890896_contracts import (\n    TestReview4841890896Contracts,\n)\n\n\nclass TestReview4842006582Contracts(unittest.TestCase):\n    def base_spec(self):\n        return TestReview4840844831Contracts().base_spec()\n\n    def run_stage_a(self, spec):\n        stream = io.StringIO()\n        with redirect_stdout(stream):\n            result = lineage.check_stage_a({\"strict_passed_spec\": [spec]})\n        return result, stream.getvalue()\n\n    def test_modified_unknown_placeholders_fail_closed(self):\n        for placeholder in (\n            \"currently unknown\",\n            \"still unavailable\",\n            \"unknown at this time\",\n            \"현재 미확인\",\n        ):\n            with self.subTest(placeholder=placeholder):\n                spec = copy.deepcopy(self.base_spec())\n                for field in lineage.STAGE_A_V3_NARRATIVE_FIELDS:\n                    spec[field] = placeholder\n                result, output = self.run_stage_a(spec)\n                self.assertEqual(result, 1)\n                self.assertIn(\"must be item-specific narrative text\", output)\n\n    def test_contextual_unknown_remains_valid(self):\n        spec = copy.deepcopy(self.base_spec())\n        spec[\"remaining_uncertainty\"] = (\n            \"The named customer's volume remains unknown pending the August filing.\"\n        )\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 0, output)\n\n    def test_generic_chronology_template_does_not_waive_inversion(self):\n        parent, child = TestReview4841890896Contracts().provisional_cards(True)\n        justification = child[\"related_lineage\"][\"follow_up_date_precedes_predecessor_justification\"]\n        justification[\"representative_date_basis\"] = (\n            \"specific explanation of what event the earlier date represents\"\n        )\n        justification[\"reason\"] = (\n            \"specific explanation of why the earlier representative date remains a later distinct follow-up judgment\"\n        )\n        by_id = {\"PARENT_FINAL\": parent, \"CHILD_FINAL\": child}\n        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])\n        errors, _ = related.check_card(\n            child,\n            by_id,\n            require_contract=True,\n            allow_provisional_related=True,\n            provisional_by_id=provisional_by_id,\n            ambiguous_provisional_ids=ambiguous,\n        )\n        self.assertIn(\n            \"follow-up chronology justification requires an item-specific representative_date_basis\",\n            errors,\n        )\n        self.assertIn(\n            \"follow-up date precedes provisional predecessor PARENT_SPEC\",\n            errors,\n        )\n\n    def test_specific_chronology_exception_still_passes(self):\n        errors, warnings = TestReview4841890896Contracts().run_provisional(True)\n        self.assertEqual(errors, [])\n        self.assertEqual(warnings, [])\n\n\nif __name__ == \"__main__\":\n    unittest.main()\n''', encoding="utf-8")

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "validation_scripts/related_lifecycle_check.py",
    '''        elif lineage_provisional != card_provisional:\n            errors.append(\n                "conflicting related_candidate_spec_ids between related lifecycle and card root"\n            )\n            provisional = dedupe(lineage_provisional + card_provisional)\n''',
    '''        elif lineage_provisional != card_provisional:\n            errors.append(\n                "conflicting related_candidate_spec_ids between related lifecycle and card root"\n            )\n            combined_provisional = lineage_provisional + card_provisional\n            if any(\n                not isinstance(value, str) or not value.strip()\n                for value in combined_provisional\n            ):\n                errors.append(\n                    "related_candidate_spec_ids must contain non-empty strings before deduplication"\n                )\n                provisional = combined_provisional\n            else:\n                provisional = dedupe(combined_provisional)\n''',
)

replace_once(
    "validation_scripts/stage_lineage_contract_check.py",
    '''def _term_pattern(term):\n    return rf'(?<![\\w]){re.escape(term)}(?![\\w])'\n''',
    '''def _term_pattern(term):\n    escaped = re.escape(term)\n    if re.search(r'[가-힣]', term):\n        # Korean source-class terms commonly appear inside compounds such as\n        # 공시자료. Preserve the left boundary so 비공식 does not satisfy 공식.\n        return rf'(?<![\\w]){escaped}'\n    # Accept ordinary English inflections such as filing/filings while keeping\n    # full left/right boundaries so unofficial does not satisfy official.\n    return rf'(?<![\\w]){escaped}(?:s|es)?(?![\\w])'\n''',
)

replace_once(
    "validation_scripts/stage_lineage_contract_check.py",
    '''    if not isinstance(format_risk_tags, list):\n        messages.append(f'{spec_id}: format_risk_tags must be an array')\n        has_format_risk = False\n    else:\n        has_format_risk = bool(format_risk_tags)\n''',
    '''    if not isinstance(format_risk_tags, list):\n        messages.append(f'{spec_id}: format_risk_tags must be an array')\n        has_format_risk = False\n    else:\n        invalid_format_risk_tags = [\n            value for value in format_risk_tags\n            if not isinstance(value, str) or not value.strip()\n        ]\n        if invalid_format_risk_tags:\n            messages.append(f'{spec_id}: format_risk_tags must contain non-empty strings')\n        normalized_format_risk_tags = [\n            value.strip().lower() for value in format_risk_tags\n            if isinstance(value, str) and value.strip()\n        ]\n        has_format_risk = normalized_format_risk_tags not in ([], ['none'])\n''',
)

Path("validation_scripts/tests/test_review_4845534152_contracts.py").write_text(
'''from __future__ import annotations\n\nimport copy\nimport io\nimport unittest\nfrom contextlib import redirect_stdout\n\nfrom validation_scripts import related_lifecycle_check as related\nfrom validation_scripts import stage_lineage_contract_check as lineage\nfrom validation_scripts.tests.test_review_4840844831_contracts import (\n    TestReview4840844831Contracts,\n)\n\n\nclass TestReview4845534152Contracts(unittest.TestCase):\n    def base_v3_spec(self):\n        return copy.deepcopy(TestReview4840844831Contracts().base_spec())\n\n    def run_stage_a(self, spec):\n        stream = io.StringIO()\n        with redirect_stdout(stream):\n            result = lineage.check_stage_a({"strict_passed_spec": [spec]})\n        return result, stream.getvalue()\n\n    def test_conflicting_malformed_provisional_arrays_fail_without_type_error(self):\n        parent = {"draft_id": "PD", "source_spec_id": "PS"}\n        child = {\n            "id": "CHILD",\n            "related": [],\n            "related_candidate_spec_ids": ["PD", {}],\n            "related_lineage": {\n                "status": "PASS",\n                "same_event_checked": True,\n                "earliest_same_event_date_checked": True,\n                "relation_type": "program_lineage",\n                "related_candidate_spec_ids": ["PS", []],\n            },\n        }\n        errors, _ = related.check_card(\n            child,\n            {"CHILD": child},\n            require_contract=True,\n            allow_provisional_related=True,\n            provisional_by_id={"PD": parent, "PS": parent},\n        )\n        self.assertTrue(any("before deduplication" in error for error in errors), errors)\n        self.assertTrue(any("non-empty strings" in error for error in errors), errors)\n\n    def test_source_class_compounds_and_inflections_are_accepted(self):\n        for source_class in ("금융감독원 공시자료", "SEC filings"):\n            with self.subTest(source_class=source_class):\n                spec = self.base_v3_spec()\n                spec["evidence_needed_for_stage_b"] = [{\n                    "source_or_document_class": source_class,\n                    "exact_claim_or_metric": "2027 revenue",\n                }]\n                result, output = self.run_stage_a(spec)\n                self.assertEqual(result, 0, output)\n\n    def test_unofficial_does_not_match_official(self):\n        spec = self.base_v3_spec()\n        spec["evidence_needed_for_stage_b"] = [{\n            "source_or_document_class": "unofficial rumor",\n            "exact_claim_or_metric": "2027 revenue",\n        }]\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 1, output)\n\n    def test_none_format_risk_sentinel_is_treated_as_empty(self):\n        spec = self.base_v3_spec()\n        spec["format_risk_tags"] = ["none"]\n        spec["structural_value_override_applied"] = False\n        for field in lineage.STAGE_A_V3_OVERRIDE_REQUIRED:\n            spec[field] = [] if field in {"anchor_classes", "evidence_needed_for_stage_b", "next_confirmation_points"} else None\n        spec["execution_anchor_type"] = "production_start"\n        spec["execution_anchor_strength"] = "strong"\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 0, output)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''',
    encoding="utf-8",
)

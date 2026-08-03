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
    """def _contains_generic_fragment(value):
    text = _normalized_text(value)
    return any(fragment in text for fragment in STAGE_A_GENERIC_OVERRIDE_FRAGMENTS)


def _specific_string(value):
""",
    """def _contains_generic_fragment(value):
    text = _normalized_text(value)
    return any(fragment in text for fragment in STAGE_A_GENERIC_OVERRIDE_FRAGMENTS)


def _contains_generic_target_fragment(value):
    text = _normalized_text(value)
    # Exact evidence targets may legitimately name a concrete residual unknown.
    # Keep generic evidence scaffolding fail-closed while allowing contextual
    # uncertainty that is qualified by a source class and named metric/claim.
    return any(
        fragment in text
        for fragment in STAGE_A_GENERIC_OVERRIDE_FRAGMENTS
        if fragment != 'unknown'
    )


def _specific_string(value):
""",
    "add target-specific generic helper",
)
replace_once(
    stage,
    """def _structured_component(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    return (
        len(text) >= 2
        and not _contains_generic_fragment(text)
        and not _placeholder_only_text(text)
    )


def _structured_source_class(value):
    return _structured_component(value) and _has_any_term(
        value, STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS
    )


def _structured_exact_target(value):
    if not _structured_component(value):
        return False
""",
    """def _structured_component(value):
    if not isinstance(value, str):
        return False
    text = value.strip()
    return len(text) >= 2 and not _placeholder_only_text(text)


def _structured_source_class(value):
    return (
        _structured_component(value)
        and not _contains_generic_fragment(value)
        and _has_any_term(value, STAGE_A_EVIDENCE_SOURCE_CLASS_TERMS)
    )


def _structured_exact_target(value):
    if not _structured_component(value) or _contains_generic_target_fragment(value):
        return False
""",
    "separate source and exact-target semantics",
)
replace_once(
    stage,
    """def _structured_interpretation_effect(value):
    return _structured_component(value) and _has_any_term(
        value, STAGE_A_INTERPRETATION_EFFECT_TERMS
    )
""",
    """def _structured_interpretation_effect(value):
    return (
        _structured_component(value)
        and not _contains_generic_fragment(value)
        and _has_any_term(value, STAGE_A_INTERPRETATION_EFFECT_TERMS)
    )
""",
    "keep interpretation effects specific",
)
replace_once(
    stage,
    """    text = _normalized_text(value)
    if not text or _contains_generic_fragment(text):
        return False
""",
    """    text = _normalized_text(value)
    if not text or _placeholder_only_text(text) or _contains_generic_target_fragment(text):
        return False
""",
    "allow contextual uncertainty in free-text evidence targets",
)

related = ROOT / "validation_scripts/related_lifecycle_check.py"
replace_once(
    related,
    """    chronology_exception_ids, chronology_exception_error = (
        validate_follow_up_chronology_justification(lineage)
    )
    if chronology_exception_error:
        errors.append(chronology_exception_error)

    if relation_type == \"distinct_follow_up\":
        child_date = parse_date(card.get(\"date\"))
        for target in related:
            parent = by_id.get(target)
            parent_date = parse_date(parent.get(\"date\")) if parent else None
            if (
                child_date
                and parent_date
                and child_date < parent_date
                and not chronology_exception_covers(target, parent, chronology_exception_ids)
            ):
                errors.append(f\"follow-up date precedes predecessor {target}\")
        for target, parent in resolved_provisional_targets:
            parent_date = parse_date(parent.get(\"date\"))
            if (
                child_date
                and parent_date
                and child_date < parent_date
                and not chronology_exception_covers(target, parent, chronology_exception_ids)
            ):
                errors.append(f\"follow-up date precedes provisional predecessor {target}\")

""",
    """    chronology_exception_value = lineage.get(
        \"follow_up_date_precedes_predecessor_justification\"
    )
    has_chronology_exception = chronology_exception_value not in (None, \"\", {})
    chronology_exception_ids, chronology_exception_error = (
        validate_follow_up_chronology_justification(lineage)
    )
    if chronology_exception_error:
        errors.append(chronology_exception_error)
    elif has_chronology_exception and relation_type != \"distinct_follow_up\":
        errors.append(
            \"follow-up chronology justification is only valid for an inverted distinct_follow_up\"
        )

    chronology_exception_used = False
    if relation_type == \"distinct_follow_up\":
        child_date = parse_date(card.get(\"date\"))
        for target in related:
            parent = by_id.get(target)
            parent_date = parse_date(parent.get(\"date\")) if parent else None
            if child_date and parent_date and child_date < parent_date:
                if chronology_exception_covers(target, parent, chronology_exception_ids):
                    chronology_exception_used = True
                else:
                    errors.append(f\"follow-up date precedes predecessor {target}\")
        for target, parent in resolved_provisional_targets:
            parent_date = parse_date(parent.get(\"date\"))
            if child_date and parent_date and child_date < parent_date:
                if chronology_exception_covers(target, parent, chronology_exception_ids):
                    chronology_exception_used = True
                else:
                    errors.append(f\"follow-up date precedes provisional predecessor {target}\")

        if (
            has_chronology_exception
            and chronology_exception_error is None
            and not chronology_exception_used
        ):
            errors.append(
                \"follow-up chronology justification requires at least one covered date inversion\"
            )

""",
    "require chronology exception applicability",
)

test = ROOT / "validation_scripts/tests/test_review_4842187150_contracts.py"
test.write_text('''"""Regression coverage for Codex review 4842187150."""\n\nfrom __future__ import annotations\n\nimport copy\nimport io\nimport sys\nimport unittest\nfrom contextlib import redirect_stdout\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n\nfrom validation_scripts import related_lifecycle_check as related\nfrom validation_scripts import stage_lineage_contract_check as lineage\nfrom validation_scripts.tests.test_review_4840844831_contracts import (\n    TestReview4840844831Contracts,\n)\nfrom validation_scripts.tests.test_review_4841890896_contracts import (\n    TestReview4841890896Contracts,\n)\n\n\nclass TestReview4842187150Contracts(unittest.TestCase):\n    def base_spec(self):\n        return TestReview4840844831Contracts().base_spec()\n\n    def run_stage_a(self, spec):\n        stream = io.StringIO()\n        with redirect_stdout(stream):\n            result = lineage.check_stage_a({\"strict_passed_spec\": [spec]})\n        return result, stream.getvalue()\n\n    def test_structured_contextual_unknown_evidence_target_passes(self):\n        spec = copy.deepcopy(self.base_spec())\n        spec[\"evidence_needed_for_stage_b\"] = [{\n            \"source_or_document_class\": \"SEC filing\",\n            \"exact_claim_or_metric\": \"named customer volume remains unknown\",\n        }]\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 0, output)\n\n    def test_free_text_contextual_unknown_evidence_target_passes(self):\n        spec = copy.deepcopy(self.base_spec())\n        spec[\"evidence_needed_for_stage_b\"] = [\n            \"SEC filing named customer volume remains unknown\"\n        ]\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 0, output)\n\n    def test_generic_evidence_scaffolding_still_fails(self):\n        spec = copy.deepcopy(self.base_spec())\n        spec[\"evidence_needed_for_stage_b\"] = [{\n            \"source_or_document_class\": \"SEC filing\",\n            \"exact_claim_or_metric\": \"more evidence on adoption\",\n        }]\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 1)\n        self.assertIn(\"evidence_needed_for_stage_b entries must identify\", output)\n\n    def run_provisional_card(self, parent, child):\n        by_id = {\"PARENT_FINAL\": parent, \"CHILD_FINAL\": child}\n        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])\n        return related.check_card(\n            child,\n            by_id,\n            require_contract=True,\n            allow_provisional_related=True,\n            provisional_by_id=provisional_by_id,\n            ambiguous_provisional_ids=ambiguous,\n        )\n\n    def test_chronology_exception_rejected_for_program_lineage(self):\n        parent, child = TestReview4841890896Contracts().provisional_cards(True)\n        child[\"related_lineage\"][\"relation_type\"] = \"program_lineage\"\n        errors, _ = self.run_provisional_card(parent, child)\n        self.assertIn(\n            \"follow-up chronology justification is only valid for an inverted distinct_follow_up\",\n            errors,\n        )\n\n    def test_chronology_exception_rejected_without_inversion(self):\n        parent, child = TestReview4841890896Contracts().provisional_cards(True)\n        child[\"date\"] = \"2026-08-11\"\n        errors, _ = self.run_provisional_card(parent, child)\n        self.assertIn(\n            \"follow-up chronology justification requires at least one covered date inversion\",\n            errors,\n        )\n\n    def test_chronology_exception_for_covered_inversion_still_passes(self):\n        errors, warnings = TestReview4841890896Contracts().run_provisional(True)\n        self.assertEqual(errors, [])\n        self.assertEqual(warnings, [])\n\n\nif __name__ == \"__main__\":\n    unittest.main()\n''', encoding="utf-8")

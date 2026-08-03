from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


related = ROOT / "validation_scripts/related_lifecycle_check.py"
replace_once(
    related,
    '''    try:\n        parsed = urlparse(text)\n        host = parsed.hostname\n    except ValueError:\n        return False\n    if parsed.scheme not in {"http", "https"} or not host:\n        return False\n''',
    '''    try:\n        parsed = urlparse(text)\n        host = parsed.hostname\n        # Accessing parsed.port is required: urllib defers malformed and\n        # out-of-range port validation until this property is read.\n        parsed.port\n    except ValueError:\n        return False\n    if parsed.scheme not in {"http", "https"} or not host:\n        return False\n''',
    "validate URL port",
)
replace_once(
    related,
    '''            for target in normalized_provisional:\n                if target in ambiguous_provisional_ids:\n                    errors.append(f"ambiguous provisional related ID: {target}")\n                    continue\n                resolved_target = provisional_by_id.get(target)\n                if resolved_target is card:\n                    errors.append("related_candidate_spec_ids contains self-reference")\n                elif resolved_target is None:\n                    errors.append(f"dangling provisional related ID: {target}")\n                else:\n                    resolved_provisional_targets.append((target, resolved_target))\n''',
    '''            resolved_provisional_aliases: dict[int, str] = {}\n            for target in normalized_provisional:\n                if target in ambiguous_provisional_ids:\n                    errors.append(f"ambiguous provisional related ID: {target}")\n                    continue\n                resolved_target = provisional_by_id.get(target)\n                if resolved_target is card:\n                    errors.append("related_candidate_spec_ids contains self-reference")\n                elif resolved_target is None:\n                    errors.append(f"dangling provisional related ID: {target}")\n                else:\n                    resolved_identity = id(resolved_target)\n                    previous_alias = resolved_provisional_aliases.get(resolved_identity)\n                    if previous_alias is not None:\n                        errors.append(\n                            "provisional related aliases resolve to duplicate target: "\n                            f"{previous_alias}, {target}"\n                        )\n                    else:\n                        resolved_provisional_aliases[resolved_identity] = target\n                        resolved_provisional_targets.append((target, resolved_target))\n''',
    "dedupe provisional resolved targets",
)

stage = ROOT / "validation_scripts/stage_lineage_contract_check.py"
replace_once(
    stage,
    '''def _contains_generic_target_fragment(value):\n    text = ' '.join(_normalized_text(value).replace(':', ' ').replace(';', ' ').split())\n    if not text:\n        return True\n''',
    '''def _contains_generic_target_fragment(value):\n    text = _normalized_text(value)\n    # Normalize ordinary punctuation so placeholder-only variants such as\n    # "additional data." cannot bypass complete-pattern matching.\n    text = re.sub(r"[\\s\\.,:;!?]+$", "", text)\n    text = ' '.join(text.replace(':', ' ').replace(';', ' ').split())\n    if not text:\n        return True\n''',
    "normalize generic-target punctuation",
)

test = ROOT / "validation_scripts/tests/test_review_484_new_contracts.py"
test.write_text('''"""Regression coverage for the unresolved PR233 review threads found 2026-08-03."""\n\nfrom __future__ import annotations\n\nimport copy\nimport io\nimport sys\nimport unittest\nfrom contextlib import redirect_stdout\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n\nfrom validation_scripts import related_lifecycle_check as related\nfrom validation_scripts import stage_lineage_contract_check as lineage\nfrom validation_scripts.tests.test_review_4840844831_contracts import (\n    TestReview4840844831Contracts,\n)\n\n\nclass TestLatestPR233ReviewContracts(unittest.TestCase):\n    def base_spec(self):\n        return TestReview4840844831Contracts().base_spec()\n\n    def run_stage_a(self, spec):\n        stream = io.StringIO()\n        with redirect_stdout(stream):\n            result = lineage.check_stage_a({"strict_passed_spec": [spec]})\n        return result, stream.getvalue()\n\n    def test_invalid_and_out_of_range_url_ports_are_rejected(self):\n        self.assertFalse(related._valid_http_url("https://example.com:bad/filing"))\n        self.assertFalse(related._valid_http_url("https://example.com:99999/filing"))\n        self.assertTrue(related._valid_http_url("https://example.com:443/filing"))\n\n    def test_provisional_aliases_resolving_to_same_target_are_rejected(self):\n        parent = {\n            "id": "PARENT_FINAL",\n            "draft_id": "PARENT_DRAFT",\n            "source_spec_id": "PARENT_SPEC",\n            "date": "2026-08-01",\n        }\n        child = {\n            "id": "CHILD_FINAL",\n            "date": "2026-08-02",\n            "related": [],\n            "related_candidate_spec_ids": ["PARENT_DRAFT", "PARENT_SPEC"],\n            "related_lineage": {\n                "status": "PASS",\n                "relation_type": "program_lineage",\n                "related_ids": [],\n                "related_candidate_spec_ids": ["PARENT_DRAFT", "PARENT_SPEC"],\n                "reason": "Both aliases identify the same predecessor program.",\n                "same_event_checked": True,\n                "earliest_same_event_date_checked": True,\n            },\n        }\n        by_id = {"PARENT_FINAL": parent, "CHILD_FINAL": child}\n        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])\n        errors, _ = related.check_card(\n            child,\n            by_id,\n            require_contract=True,\n            allow_provisional_related=True,\n            provisional_by_id=provisional_by_id,\n            ambiguous_provisional_ids=ambiguous,\n        )\n        self.assertIn(\n            "provisional related aliases resolve to duplicate target: PARENT_DRAFT, PARENT_SPEC",\n            errors,\n        )\n\n    def test_terminal_punctuation_does_not_hide_generic_target(self):\n        for value in ("additional data.", "more evidence.", "confirmation needed!"):\n            spec = copy.deepcopy(self.base_spec())\n            spec["evidence_needed_for_stage_b"] = [{\n                "source_or_document_class": "SEC filing",\n                "exact_claim_or_metric": value,\n            }]\n            result, output = self.run_stage_a(spec)\n            self.assertEqual(result, 1, (value, output))\n\n    def test_concrete_additional_data_target_still_passes(self):\n        spec = copy.deepcopy(self.base_spec())\n        spec["evidence_needed_for_stage_b"] = [{\n            "source_or_document_class": "SEC filing",\n            "exact_claim_or_metric": "additional data center capacity for Project Alpha",\n        }]\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 0, output)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''', encoding="utf-8")

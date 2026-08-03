#!/usr/bin/env python3
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
    '''                    previous_alias = resolved_provisional_aliases.get(resolved_identity)\n                    if previous_alias is not None:\n                        errors.append(\n                            "provisional related aliases resolve to duplicate target: "\n                            f"{previous_alias}, {target}"\n                        )\n                    else:\n                        resolved_provisional_aliases[resolved_identity] = target\n                        resolved_provisional_targets.append((target, resolved_target))\n''',
    '''                    final_alias = resolved_edge_aliases.get(resolved_identity)\n                    previous_alias = resolved_provisional_aliases.get(resolved_identity)\n                    if final_alias is not None:\n                        errors.append(\n                            "final and provisional related aliases resolve to duplicate target: "\n                            f"{final_alias}, {target}"\n                        )\n                    elif previous_alias is not None:\n                        errors.append(\n                            "provisional related aliases resolve to duplicate target: "\n                            f"{previous_alias}, {target}"\n                        )\n                    else:\n                        resolved_provisional_aliases[resolved_identity] = target\n                        resolved_provisional_targets.append((target, resolved_target))\n''',
    "cross final/provisional duplicate detection",
)
replace_once(
    related,
    '''                    "provisional related aliases resolve to duplicate target",\n''',
    '''                    "provisional related aliases resolve to duplicate target",\n                    "final and provisional related aliases resolve to duplicate target",\n''',
    "cross duplicate invalidates provisional edge",
)

stage = ROOT / "validation_scripts/stage_lineage_contract_check.py"
replace_once(
    stage,
    '''import json\nimport re\nimport sys\n''',
    '''import json\nimport re\nimport sys\nimport unicodedata\n''',
    "unicode import",
)
replace_once(
    stage,
    '''def _contains_generic_target_fragment(value):\n    text = _normalized_text(value)\n    # Normalize ordinary punctuation so placeholder-only variants such as\n    # "additional data." cannot bypass complete-pattern matching.\n    text = re.sub(r"[\\s\\.,:;!?]+$", "", text)\n    text = ' '.join(text.replace(':', ' ').replace(';', ' ').split())\n''',
    '''def _strip_unicode_edge_punctuation(value):\n    text = unicodedata.normalize('NFKC', _normalized_text(value)).strip()\n    while text:\n        before = text\n        while text and (\n            text[0].isspace()\n            or unicodedata.category(text[0]).startswith(('P', 'S'))\n        ):\n            text = text[1:].lstrip()\n        while text and (\n            text[-1].isspace()\n            or unicodedata.category(text[-1]).startswith(('P', 'S'))\n        ):\n            text = text[:-1].rstrip()\n        if text == before:\n            break\n    return text\n\n\ndef _contains_generic_target_fragment(value):\n    # Normalize Unicode punctuation and paired quote/bracket wrappers so\n    # placeholder-only variants such as “more evidence”… or more evidence。\n    # cannot bypass complete-pattern matching.\n    text = _strip_unicode_edge_punctuation(value)\n    text = ' '.join(text.replace(':', ' ').replace(';', ' ').split())\n''',
    "unicode generic target normalization",
)

new_test = ROOT / "validation_scripts/tests/test_review_4842822807.py"
new_test.write_text('''#!/usr/bin/env python3\nfrom __future__ import annotations\n\nimport sys\nimport unittest\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\nsys.path.insert(0, str(ROOT))\n\nfrom related_lifecycle_check import check_card\nfrom stage_lineage_contract_check import (\n    _contains_generic_target_fragment,\n    _structured_exact_target,\n)\n\n\nclass RelatedCrossNamespaceDedupTest(unittest.TestCase):\n    def test_final_and_provisional_aliases_for_same_target_fail(self):\n        parent = {\n            "id": "PARENT_FINAL",\n            "draft_id": "PARENT_DRAFT",\n            "date": "2026-08-01",\n            "related": [],\n        }\n        child = {\n            "id": "CHILD",\n            "date": "2026-08-02",\n            "related": ["PARENT_FINAL"],\n            "related_lineage": {\n                "status": "PASS",\n                "same_event_checked": True,\n                "earliest_same_event_date_checked": True,\n                "relation_type": "program_lineage",\n                "related_ids": ["PARENT_FINAL"],\n                "related_candidate_spec_ids": ["PARENT_DRAFT"],\n                "reason": "same governed program",\n            },\n        }\n        errors, _ = check_card(\n            child,\n            {"PARENT_FINAL": parent, "CHILD": child},\n            True,\n            allow_provisional_related=True,\n            provisional_by_id={"PARENT_DRAFT": parent},\n            ambiguous_provisional_ids=set(),\n        )\n        self.assertTrue(any(\n            "final and provisional related aliases resolve to duplicate target" in error\n            for error in errors\n        ))\n\n\nclass UnicodeGenericTargetNormalizationTest(unittest.TestCase):\n    def test_unicode_punctuation_and_wrappers_do_not_bypass_generic_check(self):\n        variants = (\n            "more evidence。",\n            "more evidence…",\n            "“more evidence”",\n            "‘more evidence’",\n            "「more evidence」",\n            "（more evidence）",\n            "【more evidence】",\n        )\n        for value in variants:\n            with self.subTest(value=value):\n                self.assertTrue(_contains_generic_target_fragment(value))\n                self.assertFalse(_structured_exact_target(value))\n\n    def test_specific_target_with_unicode_terminal_punctuation_still_passes(self):\n        value = "additional data center capacity for Project Alpha。"\n        self.assertFalse(_contains_generic_target_fragment(value))\n        self.assertTrue(_structured_exact_target(value))\n\n\nif __name__ == "__main__":\n    unittest.main()\n''', encoding="utf-8")

validation = ROOT / "docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md"
text = validation.read_text(encoding="utf-8")
marker = "## Review 4842822807 closure"
if marker not in text:
    text += '''\n\n## Review 4842822807 closure\n\n- final `related[]` and provisional `related_candidate_spec_ids[]` aliases are deduplicated against one shared resolved target identity map;\n- Unicode terminal punctuation, ellipsis, quotes, and bracket wrappers are normalized before generic V3 evidence-target matching;\n- focused regressions cover cross-namespace Related duplicates and multilingual punctuation-only placeholder variants.\n'''
    validation.write_text(text, encoding="utf-8")

# Remove the one-shot patch machinery from the resulting commit.
(ROOT / ".github/workflows/patch-structural-v3-review-4842822807.yml").unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)

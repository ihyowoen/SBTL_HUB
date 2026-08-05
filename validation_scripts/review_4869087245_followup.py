#!/usr/bin/env python3
from pathlib import Path


def replace(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected text not found in {path}: {old!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


stage = Path("validation_scripts/stage_lineage_contract_check.py")
stage_text = stage.read_text(encoding="utf-8")
needle = '''_prior_structured_exact_target = _prior._structured_exact_target


def _structured_exact_target(value):'''
replacement = '''_prior_structured_exact_target = _prior._structured_exact_target
_PERIOD_QUALIFIER_TOKEN_PATTERN = (
    r"(?:q[1-4]|[1-4]q|fy\\d{2,4}|(?:19|20)\\d{2}년?|h[12]|[12]h)"
)


def _is_period_qualifier_token(token):
    return bool(
        _prior._base_layer._base.re.fullmatch(
            _PERIOD_QUALIFIER_TOKEN_PATTERN, token
        )
    )


def _structured_exact_target(value):'''
if needle not in stage_text:
    raise RuntimeError("stage exact-target insertion point missing")
stage_text = stage_text.replace(needle, replacement, 1)
needle = '''        and not token.isdigit()
        and not (len(token) == 1 and token.isalpha())'''
replacement = '''        and not token.isdigit()
        and not _is_period_qualifier_token(token)
        and not (len(token) == 1 and token.isalpha())'''
if needle not in stage_text:
    raise RuntimeError("stage temporal exclusion point missing")
stage.write_text(stage_text.replace(needle, replacement, 1), encoding="utf-8")

replace(
    "validation_scripts/tests/test_review_4840431415_contracts.py",
    '"probability reduced"',
    '"Project Alpha probability reduced"',
)
replace(
    "validation_scripts/tests/test_review_4841064772_contracts.py",
    '"2027 revenue"',
    '"Project Alpha 2027 revenue"',
)
replace(
    "validation_scripts/tests/test_review_4841064772_contracts.py",
    '"2027년 매출"',
    '"알파 프로젝트 2027년 매출"',
)
replace(
    "validation_scripts/tests/test_review_4841207046_contracts.py",
    '"2027 revenue"',
    '"Project Alpha 2027 revenue"',
)
replace(
    "validation_scripts/tests/test_review_4841207046_followup_contracts.py",
    '"2027 revenue"',
    '"Project Alpha 2027 revenue"',
)
replace(
    "validation_scripts/tests/test_review_4841207046_followup_contracts.py",
    '"measurable_event_or_metric": "2027"',
    '"measurable_event_or_metric": "Project Alpha 2027 milestone"',
)
replace(
    "validation_scripts/tests/test_review_4845534152_contracts.py",
    '"2027 revenue"',
    '"Project Alpha 2027 revenue"',
)
replace(
    "validation_scripts/tests/test_review_4850083564_contracts.py",
    '"2027 revenue"',
    '"Project Alpha 2027 revenue"',
)
replace(
    "validation_scripts/tests/test_review_4851050000_contracts.py",
    '"2027 revenue"',
    '"Project Alpha 2027 revenue"',
)
replace(
    "validation_scripts/tests/test_review_4860866998_contracts.py",
    '"2027 revenue"',
    '"Project Alpha 2027 revenue"',
)
replace(
    "validation_scripts/tests/test_review_4861045407_contracts.py",
    '"2027 project approved"',
    '"Project Alpha 2027 approved"',
)
replace(
    "validation_scripts/tests/test_review_4861267953_contracts.py",
    '"report 2027 revenue"',
    '"report Project Alpha 2027 revenue"',
)
replace(
    "validation_scripts/tests/test_review_4861381740_contracts.py",
    '"reports 2027 revenue"',
    '"reports Project Alpha 2027 revenue"',
)
replace(
    "validation_scripts/tests/test_review_4866528845_contracts.py",
    '"2027 government revenue"',
    '"Project Alpha 2027 government revenue"',
)

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"unexpected match count in {path}: {text.count(old)}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")

replace_once(
    "validation_scripts/tests/test_review_4839991362_contracts.py",
    'scoped = "`related_lifecycle_check.py --require-contract --new-id-file <CURRENT_RUN_ID_FILE>`"',
    'scoped = "`related_lifecycle_check.py --require-contract --allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>`"',
)
replace_once(
    "validation_scripts/related_lifecycle_check.py",
    'errors.append("new_unrelated_event must have no final or provisional related edges")',
    'errors.append("new_unrelated_event must have empty related[] and no provisional related edges")',
)

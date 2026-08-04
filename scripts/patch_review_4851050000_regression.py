#!/usr/bin/env python3
from pathlib import Path

path = Path("validation_scripts/tests/test_review_4839991362_contracts.py")
text = path.read_text(encoding="utf-8")
old = '''        scoped = (
            "`related_lifecycle_check.py --require-contract "
            "--allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>`"
        )
'''
new = '''        scoped = (
            "`python validation_scripts/related_lifecycle_check.py "
            "<MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-contract "
            "--allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>`"
        )
'''
if text.count(old) != 1:
    raise SystemExit(f"expected one scoped-command fixture, found {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")

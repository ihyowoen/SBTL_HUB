#!/usr/bin/env python3
"""R23 branch-only correction: preserve the ORIGINAL economic-event fingerprint.

Only the approved two existing cards may differ from current main. This script
converts the already checked R23 preview's Ganfeng metadata to the governed
manual-direct-add V2 identity-preserving version; all other changes are rejected.
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FULL = ROOT / "data/cards.full.json"
LEAN = ROOT / "public/data/cards.json"
BEFORE_FULL_SHA = "15e202db02664e682890f1402d745ec71b2739274debc5c948e9567fa73582a1"
FROM_FULL_SHA = "09ebf08385b1bfe0cfa5816ec49f93d23f0016dfe83f1fc37b9da164157bedbb"
TO_FULL_SHA = "855566c8bb724a8c88a6759e5318d952892493ecdef8db1c4870319288164ea6"
LEAN_SHA = "df7b0c056554958fe4f75b96352d596b99d5b3b0ac52099c00a34e89044ea6ac"
MAIN_SHA = "b7847ca9885f6f27ae0566455b0a476ef1059d24"
KEEP_IDS = {"R3_07", "2026-08-24_GL_03"}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

assert os.environ.get("GITHUB_HEAD_REF", "ops/news-catchup-factual-fix-20261015") == "ops/news-catchup-factual-fix-20261015"
assert digest(LEAN.read_bytes()) == LEAN_SHA, "LEAN_NOT_THE_VERIFIED_R23_PATCH"
assert subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=ROOT, text=True).strip() == MAIN_SHA, "MAIN_CHANGED"
baseline_bytes = subprocess.check_output(["git", "show", "origin/main:data/cards.full.json"], cwd=ROOT)
assert digest(baseline_bytes) == BEFORE_FULL_SHA, "SOURCE_BLOB_CHANGED"
raw = FULL.read_bytes()
if digest(raw) == TO_FULL_SHA:
    print("R23 governed Full already in identity-preserving state")
    raise SystemExit(0)
assert digest(raw) == FROM_FULL_SHA, "UNRECOGNIZED_PREVIEW_REVISION"
base = json.loads(baseline_bytes)
current = json.loads(raw)
assert base["total"] == current["total"] == 1674
assert [x["id"] for x in base["cards"]] == [x["id"] for x in current["cards"]]
old = {x["id"]: x for x in base["cards"]}
for c in current["cards"]:
    if c["id"] == "2026-08-24_GL_03":
        c["event_fingerprint"] = old[c["id"]]["event_fingerprint"]
diff_ids = {c["id"] for c in current["cards"] if c != old[c["id"]]}
assert diff_ids == KEEP_IDS, diff_ids
updated = (json.dumps(current, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
assert digest(updated) == TO_FULL_SHA, "FINAL_BLOB_SHA_MISMATCH"
FULL.write_bytes(updated)
print("R23 governed correction staged: changed only two existing cards; original event fingerprint preserved")

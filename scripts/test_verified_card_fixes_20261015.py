#!/usr/bin/env python3
"""Repeatable 2026-10-15 R23 targeted content-fix gate. Standard library only.

This checks the generated *staging copies* of Full/Lean, not publication readiness.
DO NOT interpret these tests as a formal Stage 0.0C PASS.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("/tmp/R23_FOCUSED_CORRECTIONS_20261015")
BASELINE = {
    "data/cards.full.json": "d0b472e4173e565284616bb7eec0e4b28e1a42b9",
    "public/data/cards.json": "c39eac64afde20ff0ccacd920e12abbdab1b3d02",
}
EXPECTED = {
    "data/cards.full.json": "b248617fa7822a342374a882afd688436f8e5eb45a86b47280f9ed2cbb7f9aa1",
    "public/data/cards.json": "7e0063f0c49105b6037307f76668ab6225dbb9d6e2b8fe75ebde9a083346190a",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def card(doc, card_id):
    matches = [row for row in doc["cards"] if row.get("id") == card_id]
    assert len(matches) == 1, card_id
    return matches[0]


def main():
    for path, expected in BASELINE.items():
        actual = subprocess.check_output(
            ["git", "hash-object", path], cwd=ROOT, text=True
        ).strip()
        assert actual == expected, (path, "baseline changed", actual)
    subprocess.run(
        [sys.executable, "scripts/prepare_verified_card_fixes_20261015.py"],
        cwd=ROOT, check=True
    )
    docs = {}
    for path, expected in EXPECTED.items():
        staged = OUT / path
        assert staged.is_file(), path
        assert sha256(staged) == expected, (path, "candidate output drift")
        docs[path] = json.loads(staged.read_text(encoding="utf-8"))
    full = docs["data/cards.full.json"]
    lean = docs["public/data/cards.json"]
    assert len(full["cards"]) == len(lean["cards"]) == 1674
    assert [r["id"] for r in full["cards"]] == [r["id"] for r in lean["cards"]]
    assert full["updated"] == lean["updated"]
    ids = {"R3_07", "2026-08-24_GL_03"}
    for cid in ids:
        f, l = card(full, cid), card(lean, cid)
        for name in l:
            assert f[name] == l[name], (cid, name)
        assert f["related"] == l["related"] == []
    assert "조건합의" in card(full, "R3_07")["title"]
    assert "전환사채" in card(full, "2026-08-24_GL_03")["title"]
    assert len(card(full, "2026-08-24_GL_03")["fact_sources"]) == 3
    for path, expected in BASELINE.items():
        assert subprocess.check_output(
            ["git", "hash-object", path], cwd=ROOT, text=True
        ).strip() == expected, "staging build illegally modified live JSON"
    print("R23 PASS: exact two-card repair outputs, Full/Lean parity, immutable baseline")


if __name__ == "__main__":
    main()

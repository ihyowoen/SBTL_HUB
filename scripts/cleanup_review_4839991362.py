#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
for cache in (ROOT / "validation_scripts").rglob("__pycache__"):
    if cache.is_dir():
        shutil.rmtree(cache)

(ROOT / "scripts/cleanup_review_4839991362.py").unlink()
(ROOT / ".github/workflows/cleanup-review-4839991362.yml").unlink()

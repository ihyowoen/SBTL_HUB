#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apply_prompt_contract_overlays import BEGIN, END, apply_one, overlay


class PromptOverlayTest(unittest.TestCase):
    def test_apply_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prompt.md"
            path.write_text("# Prompt\n\nOriginal rule.\n", encoding="utf-8")
            block = "Stage-specific contract."
            self.assertTrue(apply_one(path, block))
            first = path.read_text(encoding="utf-8")
            self.assertIn(BEGIN, first)
            self.assertIn(END, first)
            self.assertEqual(first.count(BEGIN), 1)
            self.assertFalse(apply_one(path, block))
            second = path.read_text(encoding="utf-8")
            self.assertEqual(first, second)

    def test_existing_overlay_is_replaced_not_duplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prompt.md"
            path.write_text(
                "# Prompt\n\n" + overlay("Old rule.").strip() + "\n",
                encoding="utf-8",
            )
            self.assertTrue(apply_one(path, "New rule."))
            text = path.read_text(encoding="utf-8")
            self.assertEqual(text.count(BEGIN), 1)
            self.assertNotIn("Old rule.", text)
            self.assertIn("New rule.", text)


if __name__ == "__main__":
    unittest.main()

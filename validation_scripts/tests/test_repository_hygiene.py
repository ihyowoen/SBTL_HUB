#!/usr/bin/env python3
"""Repository hygiene regressions for generated Python bytecode."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class RepositoryHygieneTests(unittest.TestCase):
    def test_no_python_bytecode_is_tracked(self) -> None:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        tracked = [
            path.decode("utf-8")
            for path in result.stdout.split(b"\0")
            if path
        ]
        generated = [
            path
            for path in tracked
            if path.endswith((".pyc", ".pyo"))
            or "__pycache__" in Path(path).parts
        ]
        self.assertEqual(
            [],
            generated,
            "generated Python bytecode must never be committed: "
            + ", ".join(generated),
        )

    def test_gitignore_blocks_python_bytecode(self) -> None:
        ignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        ignore_rules = {
            line.strip()
            for line in ignore_text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        self.assertIn("__pycache__/", ignore_rules)
        self.assertTrue(
            {"*.pyc", "*.py[cod]"} & ignore_rules,
            ".gitignore must block compiled Python bytecode",
        )


if __name__ == "__main__":
    unittest.main()

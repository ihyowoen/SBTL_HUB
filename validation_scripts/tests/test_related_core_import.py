from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


class RelatedCoreImportTests(unittest.TestCase):
    def test_core_is_first_import_in_fresh_process(self):
        repo_root = Path(__file__).resolve().parents[2]
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import validation_scripts.related_lifecycle_core as core; "
                    "assert callable(core.check_card); "
                    "assert callable(core.main)"
                ),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertNotIn("ModuleNotFoundError", completed.stderr)


if __name__ == "__main__":
    unittest.main()

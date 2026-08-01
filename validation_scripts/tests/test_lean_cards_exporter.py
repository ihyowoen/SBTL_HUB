import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "lean_cards.mjs"


@unittest.skipUnless(shutil.which("node"), "node runtime is required")
class LeanCardsExporterTest(unittest.TestCase):
    def make_full(self) -> dict:
        return {
            "updated": "2026-08-02T00:00:00+09:00",
            "total": 2,
            "schema": "cards_v1",
            "sort": "date_desc_id_desc",
            "cards": [
                {
                    "id": "2026-08-02_GL_01",
                    "region": "GL",
                    "date": "2026-08-02",
                    "cat": "market",
                    "title": "First",
                    "fact": "Fact one",
                    "urls": ["https://example.com/one"],
                    "related": [],
                    "audit_only": {"stage": "0.7C"},
                },
                {
                    "id": "2026-08-01_US_01",
                    "region": "US",
                    "date": "2026-08-01",
                    "cat": "policy",
                    "title": "Second",
                    "fact": "Fact two",
                    "urls": ["https://example.com/two"],
                    "related": ["2026-08-02_GL_01"],
                    "lineage_private": "preserve-in-full",
                },
            ],
        }

    def run_exporter(self, full_path: Path, public_path: Path, *args: str):
        env = os.environ.copy()
        env["CARDS_FULL_PATH"] = str(full_path)
        env["CARDS_PUBLIC_PATH"] = str(public_path)
        return subprocess.run(
            ["node", str(SCRIPT), *args],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_generation_repairs_malformed_public_without_mutating_full(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            full_path = root / "cards.full.json"
            public_path = root / "cards.json"
            full_doc = self.make_full()
            full_bytes = (json.dumps(full_doc, ensure_ascii=False, indent=1) + "\n").encode()
            full_path.write_bytes(full_bytes)
            public_path.write_text('{"cards": [', encoding="utf-8")

            result = self.run_exporter(full_path, public_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(full_path.read_bytes(), full_bytes)

            public_doc = json.loads(public_path.read_text(encoding="utf-8"))
            self.assertEqual(public_doc["total"], 2)
            self.assertEqual(
                [card["id"] for card in public_doc["cards"]],
                ["2026-08-02_GL_01", "2026-08-01_US_01"],
            )
            self.assertNotIn("audit_only", public_doc["cards"][0])
            self.assertNotIn("lineage_private", public_doc["cards"][1])

            check_result = self.run_exporter(full_path, public_path, "--check")
            self.assertEqual(check_result.returncode, 0, check_result.stderr)

    def test_same_full_and_public_path_is_rejected_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            full_path = Path(tmp) / "cards.full.json"
            full_bytes = (json.dumps(self.make_full(), ensure_ascii=False, indent=1) + "\n").encode()
            full_path.write_bytes(full_bytes)

            result = self.run_exporter(full_path, full_path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("경로가 동일", result.stderr)
            self.assertEqual(full_path.read_bytes(), full_bytes)


if __name__ == "__main__":
    unittest.main()

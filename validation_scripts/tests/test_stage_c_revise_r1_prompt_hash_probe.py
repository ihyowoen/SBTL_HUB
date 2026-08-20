from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md"


class TestStageCReviseR1PromptHashProbe(unittest.TestCase):
    def test_prompt_sha256_probe(self):
        raw = PROMPT.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        print(f"PROMPT_0_3R_SHA256={sha}")
        self.assertTrue(len(raw) > 0)
        self.assertEqual(len(sha), 64)


if __name__ == "__main__":
    unittest.main()

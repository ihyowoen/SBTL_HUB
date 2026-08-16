from pathlib import Path
import hashlib
import unittest


class CurrentPromptDigestDiagnostic(unittest.TestCase):
    def test_emit_current_stage_a_prompt_digest(self):
        repo_root = Path(__file__).resolve().parents[2]
        prompt = repo_root / "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md"
        digest = hashlib.sha256(prompt.read_bytes()).hexdigest()
        self.fail(f"CURRENT_STAGE_A_PROMPT_SHA256={digest}")


if __name__ == "__main__":
    unittest.main()

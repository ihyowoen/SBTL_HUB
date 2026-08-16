from pathlib import Path
import hashlib


def test_emit_current_stage_a_prompt_digest():
    repo_root = Path(__file__).resolve().parents[2]
    prompt = repo_root / "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md"
    digest = hashlib.sha256(prompt.read_bytes()).hexdigest()
    raise AssertionError(f"CURRENT_STAGE_A_PROMPT_SHA256={digest}")

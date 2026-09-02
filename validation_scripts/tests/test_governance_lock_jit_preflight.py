from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json"
HELPER = ROOT / "scripts/governance_lock_v4.mjs"
AUDIT_DISPATCH = ROOT / "scripts/validate_card_run_audits_dispatch.mjs"
MASTER = ROOT / "docs/llm_prompts/v1/00_NEW_RUN_MASTER_PROMPT.md"
PREFLIGHT = ROOT / "docs/llm_prompts/v1/00D_PROMPT_0_0D_DOCUMENT_UNIVERSE_PREFLIGHT.md"
POLICY = ROOT / "docs/DOCUMENT_UNIVERSE_POLICY.md"

BOOTSTRAP = {
    "docs/WORKFLOW.md",
    "docs/OPERATIONS.md",
    "docs/DOCUMENT_UNIVERSE_POLICY.md",
    "docs/RUN_GOVERNANCE_INDEX.md",
    "docs/llm_prompts/v1/PROMPT_MANIFEST.md",
    "docs/llm_prompts/v1/00_NEW_RUN_MASTER_PROMPT.md",
    "docs/llm_prompts/v1/00D_PROMPT_0_0D_DOCUMENT_UNIVERSE_PREFLIGHT.md",
    "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json",
}


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=ROOT, text=True, capture_output=True, check=check
    )


class GovernanceLockJitPreflightTests(unittest.TestCase):
    def test_registry_has_small_exact_bootstrap_set(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(set(registry["bootstrap_read"]), BOOTSTRAP)
        authority = set(registry["active_canonical"])
        authority.update(registry["active_named_prompts"])
        authority.update(registry["active_validator_contracts"])
        authority.update(registry["open_remediations"])
        authority.update(registry["activation_required_migrations"])
        self.assertLess(len(BOOTSTRAP), len(authority))
        self.assertTrue(BOOTSTRAP.issubset(authority))

    def test_prompts_forbid_count_only_read_attestation(self) -> None:
        master = MASTER.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")
        policy = POLICY.read_text(encoding="utf-8")
        self.assertIn("Do not use `active_full_read_count`", master)
        self.assertIn("legacy count-only self-attestation is not accepted", preflight)
        self.assertIn("A model-generated count is not evidence", policy)
        self.assertIn("Do **not** pre-load all 17 named-stage prompts", master)
        self.assertIn("jit_before_stage", preflight)

    def test_machine_pass_does_not_claim_cognitive_bootstrap_read(self) -> None:
        preflight = PREFLIGHT.read_text(encoding="utf-8")
        policy = POLICY.read_text(encoding="utf-8")
        self.assertIn("not something the 0.0D machine artifact claims to prove", preflight)
        self.assertIn("It is **not** a read counter", preflight)
        self.assertIn("not represented as a machine-proven read attestation", preflight)
        self.assertIn("not whether a model cognitively consumed", policy)
        self.assertIn("No machine PASS field claims", policy)

    def test_helper_self_test_rejects_legacy_count_only_artifact(self) -> None:
        result = run("node", str(HELPER), "--self-test")
        combined = result.stdout + result.stderr
        self.assertIn("legacy count-only attestation rejected", combined)

    def test_formal_audit_dispatch_replays_governance_lock(self) -> None:
        source = AUDIT_DISPATCH.read_text(encoding="utf-8")
        self.assertIn('from "./governance_lock_v4.mjs"', source)
        self.assertIn("verifyGovernanceArtifactFromGit", source)
        self.assertIn("BLOCKED_RUN_GOVERNANCE_LOCK", source)
        self.assertLess(
            source.index("governanceVerifier(root, run)"),
            source.index("splitAuditRefs(root, run)"),
        )
        result = run("node", str(AUDIT_DISPATCH), "--self-test")
        self.assertIn("replays governance lock", result.stdout)

    def test_emitted_lock_is_replayable_and_registry_bound(self) -> None:
        head = run("git", "rev-parse", "HEAD").stdout.strip()
        full_blob = run("git", "rev-parse", f"{head}:data/cards.full.json").stdout.strip()
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        authority = set(registry["active_canonical"])
        authority.update(registry["active_named_prompts"])
        authority.update(registry["active_validator_contracts"])
        authority.update(registry["open_remediations"])
        authority.update(registry["activation_required_migrations"])

        with tempfile.TemporaryDirectory() as td:
            artifact_path = Path(td) / "0.0d.json"
            emit = run(
                "node", str(HELPER), "--emit",
                "--base-main-sha", head,
                "--base-full-blob-sha", full_blob,
            )
            artifact_path.write_text(emit.stdout, encoding="utf-8")
            artifact = json.loads(emit.stdout)
            self.assertEqual(artifact["locked_authority_count"], len(authority))
            self.assertEqual(artifact["bootstrap_read_count"], len(BOOTSTRAP))
            self.assertEqual(artifact["active_full_read_count"], len(authority))
            self.assertEqual(artifact["governance_lock"]["schema"], "governance_lock_v1")
            self.assertEqual(
                {row["path"] for row in artifact["governance_lock"]["locked_authorities"]},
                authority,
            )
            verify = run(
                "node", str(HELPER), "--verify",
                "--base-main-sha", head,
                "--base-full-blob-sha", full_blob,
                "--artifact", str(artifact_path),
            )
            self.assertIn("matches locked main git tree", verify.stdout)

    def test_43_style_count_claim_without_lock_is_rejected(self) -> None:
        head = run("git", "rev-parse", "HEAD").stdout.strip()
        full_blob = run("git", "rev-parse", f"{head}:data/cards.full.json").stdout.strip()
        emit = run(
            "node", str(HELPER), "--emit",
            "--base-main-sha", head,
            "--base-full-blob-sha", full_blob,
        )
        artifact = json.loads(emit.stdout)
        artifact.pop("governance_lock")
        artifact["active_full_read_count"] = artifact["locked_authority_count"]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fake-count-only.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            result = run(
                "node", str(HELPER), "--verify",
                "--base-main-sha", head,
                "--base-full-blob-sha", full_blob,
                "--artifact", str(path),
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BLOCKED_GOVERNANCE_LOCK_MISSING", result.stderr)


if __name__ == "__main__":
    unittest.main()

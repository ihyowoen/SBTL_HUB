from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path

from validation_scripts import card_run_v4_binding_hardening as binding


ROOT = Path(__file__).resolve().parents[2]


def source(**overrides):
    row = {
        "source_id": "S1",
        "source_url": "https://example.test/source",
        "supports": ["fact"],
        "source_quote": "Alpha commissioned 20 MW of storage in 2026.",
        "source_quote_status": "body_quote_verified",
        "fetched": True,
    }
    row.update(overrides)
    return row


def row05(*, fact="Alpha commissioned 20 MW of storage in 2026.", sources=None, refs=None):
    sources = [source()] if sources is None else sources
    refs = ["S1"] if refs is None else refs
    return {
        "source_spec_id": "SPEC_1",
        "fact": fact,
        "fact_sources": sources,
        "source_discovery_ledger": [],
        "claim_source_coverage": {
            "status": "PASS",
            "visible_fact": {"claim": fact, "supported_by_source_ids": refs},
            "unsupported_visible_claim_count": 0,
        },
    }


class V5EvidenceHandoffTests(unittest.TestCase):
    def assertBlocks(self, payload):
        with self.assertRaises(binding.Blocked):
            binding.validate_v5_stage_05_handoff_row(payload, "test")

    def test_verified_literal_quote_handoff_passes(self):
        binding.validate_v5_stage_05_handoff_row(row05(), "test")

    def test_context_only_unverified_source_can_be_preserved_but_not_ground(self):
        context = source(
            source_id="CTX",
            source_url="https://example.test/context",
            supports=[],
            source_quote_status="not_applicable_paraphrase_only",
            source_quote="",
            fetched=True,
            evidence_role="context_only",
        )
        binding.validate_v5_stage_05_handoff_row(row05(sources=[source(), context]), "test")

    def test_editor_claim_does_not_replace_literal_quote(self):
        self.assertBlocks(row05(sources=[source(source_quote="", claim="Alpha commissioned 20 MW of storage in 2026.")]))

    def test_body_level_evidence_verified_is_not_promoted(self):
        self.assertBlocks(row05(sources=[source(source_quote_status="body_level_evidence_verified")]))

    def test_fetched_true_is_required_for_v5_handoff(self):
        self.assertBlocks(row05(sources=[source(fetched=False)]))

    def test_explicit_fact_permission_is_required(self):
        self.assertBlocks(row05(sources=[source(supports=["sub"])]))

    def test_implicit_all_field_permission_is_not_accepted_for_handoff(self):
        s = source()
        s.pop("supports")
        self.assertBlocks(row05(sources=[s]))

    def test_claim_coverage_must_match_carried_fact(self):
        payload = row05()
        payload["claim_source_coverage"]["visible_fact"]["claim"] = "Different claim."
        self.assertBlocks(payload)

    def test_claim_coverage_ref_must_resolve_uniquely(self):
        self.assertBlocks(row05(refs=["MISSING"]))
        duplicated = [source(), source(source_url="https://example.test/other")]
        self.assertBlocks(row05(sources=duplicated, refs=["S1"]))

    def test_duplicate_claim_refs_are_rejected(self):
        self.assertBlocks(row05(refs=["S1", "S1"]))

    def test_unsupported_visible_claim_count_must_be_zero(self):
        payload = row05()
        payload["claim_source_coverage"]["unsupported_visible_claim_count"] = 1
        self.assertBlocks(payload)

    def test_verified_quote_with_editor_metadata_still_passes(self):
        payload = row05(sources=[source(claim="Editor summary that is not used as grounding.", claim_status="unverified")])
        binding.validate_v5_stage_05_handoff_row(payload, "test")


class DocumentUniverseRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json").read_text(encoding="utf-8"))

    def test_registry_classifies_every_tracked_docs_path_exactly_once(self):
        tracked = set(subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files", "docs"], text=True
        ).splitlines())
        classified = binding._registry_lifecycle_paths(self.registry)
        self.assertEqual(tracked, classified)

    def test_locked_head_docs_tree_matches_tracked_docs_paths(self):
        head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        tree = binding._locked_docs_tree_paths(head)
        tracked = set(subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files", "docs"], text=True
        ).splitlines())
        self.assertEqual(tracked, tree)

    def test_registry_duplicate_cross_classification_is_blocked(self):
        bad = copy.deepcopy(self.registry)
        bad["reference_only"].append(bad["active_canonical"][0])
        with self.assertRaises(binding.Blocked):
            binding._registry_lifecycle_paths(bad)


if __name__ == "__main__":
    unittest.main()

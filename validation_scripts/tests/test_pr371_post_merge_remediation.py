import copy
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts import card_run_v4_binding_hardening as hardening
from validation_scripts.card_audit_utils import load_owner_registry, source_audit_measure


ROOT = Path(__file__).resolve().parents[2]
SEP9_STAGE_A = (
    ROOT
    / "runs/2026-09-10/sep9-r1-current-main-production-r1/stages/stage-a.json"
)
SEP9_STAGE_B = (
    ROOT
    / "runs/2026-09-10/sep9-r1-current-main-production-r1/stages/stage-b.json"
)
SEP9_STAGE_C = (
    ROOT
    / "runs/2026-09-10/sep9-r1-current-main-production-r1/stages/stage-c.json"
)
SEP9_CARD_RUN = (
    ROOT
    / "runs/2026-09-10/sep9-r1-current-main-production-r1/card-run.json"
)
V4_NODE_GATE = ROOT / "scripts/validate_card_run_v4_hardening.mjs"


class Pr371PostMergeRemediationTests(unittest.TestCase):
    def check(self, payload):
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            return lineage.check_stage_a(payload)

    def test_self_asserted_production_subset_cannot_bypass_full_stage_a(self):
        artifact = json.loads(SEP9_STAGE_A.read_text(encoding="utf-8"))
        self.assertNotEqual(self.check(artifact), 0)

    def test_subset_flags_do_not_hide_missing_required_docs(self):
        artifact = json.loads(SEP9_STAGE_A.read_text(encoding="utf-8"))
        artifact.pop("required_docs_check")
        self.assertNotEqual(self.check(artifact), 0)

    def test_subset_flags_do_not_hide_empty_strict_pool(self):
        artifact = json.loads(SEP9_STAGE_A.read_text(encoding="utf-8"))
        artifact["strict_passed_spec"] = []
        self.assertNotEqual(self.check(artifact), 0)

    def test_0_7c_cannot_pass_without_identity_level_terminal_ledger(self):
        run = json.loads(SEP9_CARD_RUN.read_text(encoding="utf-8"))
        with self.assertRaises(hardening.Blocked):
            hardening.validate_completeness(run)

    def test_node_production_gate_invokes_python_hardening_with_run(self):
        gate = V4_NODE_GATE.read_text(encoding="utf-8")
        self.assertIn(
            'runPythonChecker("validation_scripts/card_run_v4_binding_hardening.py", ["--run", runPath]',
            gate,
        )

    def test_terminal_decision_requires_governed_vocabulary_and_basis(self):
        governed = {"CAND_1": ("candidate_review_pool", "stage_a_basis")}
        ids, dispositions = hardening.validate_terminal_decision_binding(
            [
                {
                    "identity": "CAND_1",
                    "disposition": "candidate_review_pool",
                    "terminal": True,
                    "basis": "stage_a_basis",
                }
            ],
            governed,
        )
        self.assertEqual(ids, ["CAND_1"])
        self.assertEqual(dispositions, ["candidate_review_pool"])
        with self.assertRaises(hardening.Blocked):
            hardening.validate_terminal_decision_binding(
                [
                    {
                        "identity": "CAND_1",
                        "disposition": "invented",
                        "terminal": True,
                        "basis": "stage_a_basis",
                    }
                ],
                governed,
            )
        with self.assertRaises(hardening.Blocked):
            hardening.validate_terminal_decision_binding(
                [
                    {
                        "identity": "CAND_1",
                        "disposition": "candidate_review_pool",
                        "terminal": True,
                        "basis": "self_asserted_basis",
                    }
                ],
                governed,
            )

    def test_mining_com_reuters_copy_is_not_an_independent_owner(self):
        card = {
            "fact_sources": [
                {
                    "source_url": "https://www.mining.com/web/example",
                    "source_owner_id": "Mining.com/Reuters",
                    "evidence_role": "primary_event_evidence",
                    "supports": ["fact"],
                },
                {
                    "source_url": "https://www.reuters.com/world/example/",
                    "source_owner_id": "Reuters",
                    "evidence_role": "corroboration",
                    "supports": ["fact"],
                },
            ]
        }
        registry = load_owner_registry(ROOT / "validation_data/source_owner_registry.json")
        measure = source_audit_measure(card, registry)
        self.assertEqual(measure["source_independent_owner_count"], 1)
        self.assertEqual(measure["independent_owners"], ["reuters_syndication"])

    def test_reuters_checked_url_is_two_urls_two_domains_one_owner_and_non_supporting(self):
        for path, bucket in (
            (SEP9_STAGE_B, "draft_cards"),
            (SEP9_STAGE_C, "accepted_fact_safe"),
        ):
            artifact = json.loads(path.read_text(encoding="utf-8"))
            row = next(
                item
                for item in artifact[bucket]
                if item["source_spec_id"] == "STD26_0909_A_007"
            )
            self.assertEqual(
                row["source_diversity_measure"],
                {"unique_urls": 2, "unique_domains": 2, "independent_owner_count": 1},
            )
            reuters = next(
                source
                for source in row["fact_sources"]
                if "reuters.com" in source["url"]
            )
            self.assertEqual(reuters["role"], "checked_not_used_for_visible_claims")
            self.assertEqual(reuters["visible_claim_support"], [])
            self.assertEqual(reuters["source_owner_id_normalized"], "reuters")


if __name__ == "__main__":
    unittest.main()

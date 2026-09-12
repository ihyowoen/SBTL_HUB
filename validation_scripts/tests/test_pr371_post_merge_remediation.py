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
SEP9_CARD_RUN = (
    ROOT
    / "runs/2026-09-10/sep9-r1-current-main-production-r1/card-run.json"
)


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


if __name__ == "__main__":
    unittest.main()

import copy
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts import card_run_v4_binding_hardening as hardening
from validation_scripts.card_audit_utils import load_owner_registry, source_audit_measure
from validation_scripts.tests.test_stage_a_v4_required_docs_authority import (
    StageAV4RequiredDocsAuthorityTest,
)


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "runs/2026-09-10/sep9-r1-current-main-production-r1"
SEP9_STAGE_A = RUN_ROOT / "stages/stage-a.json"
SEP9_STAGE_B = RUN_ROOT / "stages/stage-b.json"
SEP9_STAGE_C = RUN_ROOT / "stages/stage-c.json"
SEP9_STAGE_05 = RUN_ROOT / "stages/stage-0-5.json"
SEP9_STAGE_06 = RUN_ROOT / "stages/stage-0-6.json"
SEP9_STAGE_07 = RUN_ROOT / "stages/stage-0-7.json"
SEP9_CARD_RUN = RUN_ROOT / "card-run.json"
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
            [{"identity":"CAND_1","disposition":"candidate_review_pool","terminal":True,"basis":"stage_a_basis"}],
            governed,
        )
        self.assertEqual(ids, ["CAND_1"])
        self.assertEqual(dispositions, ["candidate_review_pool"])
        with self.assertRaises(hardening.Blocked):
            hardening.validate_terminal_decision_binding(
                [{"identity":"CAND_1","disposition":"invented","terminal":True,"basis":"stage_a_basis"}],
                governed,
            )
        with self.assertRaises(hardening.Blocked):
            hardening.validate_terminal_decision_binding(
                [{"identity":"CAND_1","disposition":"candidate_review_pool","terminal":True,"basis":"self_asserted_basis"}],
                governed,
            )

    def test_passing_governed_decision_ledger_must_pass_full_stage_a_checker(self):
        run = json.loads(SEP9_CARD_RUN.read_text(encoding="utf-8"))
        ledger = {
            "status": "PASS",
            "prior_partial_ledger_ref": "runs/2026-09-10/sep9-r1-current-main-production-r1/stage-a-cumulative-ledger-r1.json",
        }
        with self.assertRaisesRegex(hardening.Blocked, "full Stage A checker"):
            hardening.governed_stage_a_decisions(run, ledger)

    def test_stage_a_alias_is_accepted_before_authoritative_checker(self):
        self.assertEqual(hardening.stage({"stage": "stage_a"}, "test"), "A")
        self.assertEqual(hardening.stage({"stage": "A"}, "test"), "A")

    def test_terminal_authority_is_derived_from_checked_pools_not_terminal_decisions(self):
        source = {
            "legacy_keep": [],
            "review_pool": [],
            "strict_passed_spec": [{"spec_id":"SPEC_1","source_story_ids":["CAND_1"]}],
            "candidate_review_pool": [],
            "watchlist_context_pool": [],
            "reject_or_support_only_pool": [],
            "rejected": [],
            "existing_reinforcement": [],
            "support_source_only": [],
            "terminal_decisions": [{"identity":"CAND_1","decision":"rejected","basis":"invented"}],
        }
        governed = hardening.checker_validated_stage_a_decisions(source)
        self.assertEqual(governed["CAND_1"], ("strict_passed_spec", "stage_a_checker:strict_passed_spec:SPEC_1"))

    def test_real_passing_v4_artifact_ignores_unchecked_terminal_array(self):
        artifact = StageAV4RequiredDocsAuthorityTest().active_full_artifact()
        self.assertEqual(artifact["stage"], "stage_a")
        self.assertEqual(self.check(artifact), 0)
        spec = artifact["strict_passed_spec"][0]
        identity = spec["source_story_ids"][0]
        artifact["terminal_decisions"] = [{"identity":identity,"decision":"rejected","basis":"invented"}]
        self.assertEqual(self.check(artifact), 0)
        governed = hardening.checker_validated_stage_a_decisions(artifact)
        self.assertEqual(governed[identity], ("strict_passed_spec", f"stage_a_checker:strict_passed_spec:{spec['spec_id']}"))

    def test_duplicate_identity_inside_one_non_strict_row_is_deduplicated(self):
        source = {
            "review_pool": [],
            "legacy_keep": [{"story_id":"CAND_1","grouped_story_ids":["CAND_1"]}],
            "strict_passed_spec": [],
            "candidate_review_pool": [],
            "watchlist_context_pool": [],
            "reject_or_support_only_pool": [],
            "rejected": [],
            "existing_reinforcement": [],
            "support_source_only": [],
        }
        self.assertEqual(
            hardening.checker_validated_stage_a_decisions(source),
            {"CAND_1": ("legacy_keep", "stage_a_checker:legacy_keep:CAND_1")},
        )

    def test_legacy_keep_is_preserved_as_checker_governed_terminal_disposition(self):
        source = {
            "review_pool": [],
            "legacy_keep": [{"story_id":"LEGACY_1"}],
            "strict_passed_spec": [],
            "candidate_review_pool": [],
            "watchlist_context_pool": [],
            "reject_or_support_only_pool": [],
            "rejected": [],
            "existing_reinforcement": [],
            "support_source_only": [],
        }
        governed = hardening.checker_validated_stage_a_decisions(source)
        self.assertEqual(governed["LEGACY_1"], ("legacy_keep", "stage_a_checker:legacy_keep:LEGACY_1"))
        ids, dispositions = hardening.validate_terminal_decision_binding(
            [{"identity":"LEGACY_1","disposition":"legacy_keep","terminal":True,"basis":"stage_a_checker:legacy_keep:LEGACY_1"}],
            governed,
        )
        self.assertEqual(ids, ["LEGACY_1"])
        self.assertEqual(dispositions, ["legacy_keep"])

    def test_checker_valid_artifact_does_not_need_top_level_status_alias_for_authority(self):
        artifact = StageAV4RequiredDocsAuthorityTest().active_full_artifact()
        self.assertNotIn("status", artifact)
        self.assertEqual(self.check(artifact), 0)
        governed = hardening.checker_validated_stage_a_decisions(artifact)
        self.assertTrue(governed)

    def test_operation_stage_a_binding_must_match_governed_strict_identity(self):
        governed = {"CAND_1": ("strict_passed_spec", "stage_a_checker:strict_passed_spec:SPEC_1")}
        strict_specs = hardening.governed_strict_spec_identities(governed)
        hardening.validate_governed_stage_a_operation(
            {"A":[{"spec_id":"SPEC_1","source_story_ids":["CAND_1"]}]}, "SPEC_1", strict_specs, "insert[0]"
        )
        with self.assertRaisesRegex(hardening.Blocked, "disagrees with terminal authority"):
            hardening.validate_governed_stage_a_operation(
                {"A":[{"spec_id":"SPEC_1","source_story_ids":["CAND_2"]}]}, "SPEC_1", strict_specs, "insert[0]"
            )
        rejected = {"CAND_1": ("rejected", "stage_a_checker:rejected:CAND_1")}
        with self.assertRaisesRegex(hardening.Blocked, "not a checker-validated strict Stage A outcome"):
            hardening.validate_governed_stage_a_operation(
                {"A":[{"spec_id":"SPEC_1","source_story_ids":["CAND_1"]}]},
                "SPEC_1",
                hardening.governed_strict_spec_identities(rejected),
                "insert[0]",
            )

    def test_mining_com_reuters_copy_is_not_an_independent_owner(self):
        card = {"fact_sources":[
            {"source_url":"https://www.mining.com/web/example","source_owner_id":"Mining.com/Reuters","evidence_role":"primary_event_evidence","supports":["fact"]},
            {"source_url":"https://www.reuters.com/world/example/","source_owner_id":"Reuters","evidence_role":"corroboration","supports":["fact"]},
        ]}
        registry = load_owner_registry(ROOT / "validation_data/source_owner_registry.json")
        measure = source_audit_measure(card, registry)
        self.assertEqual(measure["source_independent_owner_count"], 1)
        self.assertEqual(measure["independent_owners"], ["reuters_syndication"])

    def test_reuters_checked_url_is_two_urls_two_domains_one_owner_and_non_supporting(self):
        for path, bucket in ((SEP9_STAGE_B,"draft_cards"),(SEP9_STAGE_C,"accepted_fact_safe")):
            artifact = json.loads(path.read_text(encoding="utf-8"))
            row = next(item for item in artifact[bucket] if item["source_spec_id"] == "STD26_0909_A_007")
            self.assertEqual(row["source_diversity_measure"], {"unique_urls":2,"unique_domains":2,"independent_owner_count":1})
            reuters = next(source for source in row["fact_sources"] if "reuters.com" in source["url"])
            self.assertEqual(reuters["role"], "checked_not_used_for_visible_claims")
            self.assertEqual(reuters["visible_claim_support"], [])
            self.assertEqual(reuters["source_owner_id_normalized"], "reuters")

    def test_stale_a007_downstream_source_diversity_chain_is_fail_closed(self):
        artifacts = [json.loads(path.read_text(encoding="utf-8")) for path in (SEP9_STAGE_B,SEP9_STAGE_C,SEP9_STAGE_05,SEP9_STAGE_06,SEP9_STAGE_07)]
        rows_by_stage = {}
        for artifact in artifacts:
            stage = hardening.stage(artifact, "test")
            rows = hardening.matching_rows(artifact, stage, "STD26_0909_A_007")
            self.assertTrue(rows)
            rows_by_stage[stage] = rows
        with self.assertRaisesRegex(hardening.Blocked, "source_diversity_status drifts"):
            hardening.validate_source_diversity_chain(rows_by_stage, "STD26_0909_A_007")

    def test_source_diversity_status_is_required_at_every_stage(self):
        rows_by_stage = {stage:[{"source_diversity_status":"PASS_MULTI_SOURCE"}] for stage in ("B","C","0.5","0.6","0.7")}
        hardening.validate_source_diversity_chain(rows_by_stage, "SPEC")
        rows_by_stage["C"] = [{}]
        with self.assertRaisesRegex(hardening.Blocked, "requires non-empty source_diversity_status"):
            hardening.validate_source_diversity_chain(rows_by_stage, "SPEC")


if __name__ == "__main__":
    unittest.main()

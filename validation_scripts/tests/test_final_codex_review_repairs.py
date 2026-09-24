"""Final-head Codex review regressions for PR #385.

These fixtures are synthetic contract probes. They do not certify live-source truth.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

ROOT = Path(__file__).resolve().parents[2]
BASE_343 = '34386663f1795aef6cb730f9320f6cae715a5c79'


class FinalCodexReviewRepairs(unittest.TestCase):
    def validate(self, prior, current, quote, dimensions=('quantitative_anchor',)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, 'final codex review', operation_card=copy.deepcopy(chain['0.6'][0]),
            locked_prompt_version='PROMPT_0_6_V5_20260919')
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            self.validate(*args, **kwargs)

    def standalone(self, prior, current, quote, dimensions=('quantitative_anchor',), *, fake_v4=False, row_fake_v4=False, remove_audit=False):
        chain = chain_for(prior, current, quote, dimensions)
        row = copy.deepcopy(chain['0.6'][0])
        row.update(
            language_terminology_polished=True,
            related_lineage={'status':'PASS','relation_type':'new_unrelated_event','related_ids':[]},
            date_role={'representative_date':'2026-09-01'},
            source_diversity_status='PASS_MULTI_SOURCE',
        )
        if row_fake_v4:
            row['prompt_provenance_0_6']={'prompt_version':'PROMPT_0_6_V4_FAKE'}
        if remove_audit:
            row.pop('content_enrichment_audit', None)
        payload = {
            'stage':'0.6','upstream_lineage_integrity':'PASS','lineage_and_anchor_guard':'PASS',
            'content_enriched_and_language_polished':[row],
        }
        if fake_v4:
            payload['prompt_provenance']={'prompt_version':'PROMPT_0_6_V4_FAKE'}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'stage-0-6.json'
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
            proc = subprocess.run(
                [sys.executable, str(ROOT/'validation_scripts/stage_artifact_contract_check.py'), '0.6', str(path)],
                cwd=ROOT, text=True, capture_output=True, timeout=30)
        return proc, json.loads(proc.stdout)

    def test_standalone_changed_field_grounds_non_dimensional_facts(self):
        proc, result = self.standalone(
            'Capacity is 10 MW.', 'Capacity is 20 MW. Alpha sold coal.', 'Capacity is 20 MW.')
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn('C06.GROUNDING.FIELD_IDENTITY', [x.get('rule_id') for x in result['findings']])
        good, result = self.standalone(
            'Capacity is 10 MW.', 'Capacity is 20 MW. Alpha sold coal.', 'Capacity is 20 MW. Alpha sold coal.')
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)

    def test_standalone_changed_field_grounds_factual_relations(self):
        prior = 'Capacity is 10 MW.'
        current = 'Capacity is 20 MW. Alpha sold gas. Beta sold coal.'
        wrong_quote = 'Capacity is 20 MW. Alpha sold coal. Beta sold gas.'
        proc, result = self.standalone(prior, current, wrong_quote)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn('C06.GROUNDING.FIELD_RELATION', [x.get('rule_id') for x in result['findings']])
        good, result = self.standalone(prior, current, current)
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)

    def test_unlocked_row_level_v4_declaration_cannot_disable_v5(self):
        proc, result = self.standalone(
            'Capacity is 10 MW.', 'Capacity is 20 MW.', 'Capacity is 20 MW.',
            row_fake_v4=True, remove_audit=True)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn('content_enrichment_audit', [x.get('field') for x in result['findings']])

    def test_exported_recipient_swap_is_ordered(self):
        before = 'Capacity is 10 MW. Alpha exported coal to Beta. Alpha exported gas to Gamma.'
        after = 'Capacity is 20 MW. Alpha exported coal to Gamma. Alpha exported gas to Beta.'
        self.blocked(before, after, before.replace('10 MW','20 MW'))
        self.validate(before, after, after)

    def test_passive_recipient_swap_is_ordered(self):
        before = 'Capacity is 10 MW. Coal was sold by Alpha to Beta. Gas was sold by Alpha to Gamma.'
        after = 'Capacity is 20 MW. Coal was sold by Alpha to Gamma. Gas was sold by Alpha to Beta.'
        self.blocked(before, after, before.replace('10 MW','20 MW'))
        self.validate(before, after, after)

    def test_multiword_korean_subject_swap_is_bound(self):
        before = '용량은 10 MW이다. 알파 공장은 석탄을 판매했다. 베타 공장은 가스를 판매했다.'
        after = '용량은 20 MW이다. 알파 공장은 가스를 판매했다. 베타 공장은 석탄을 판매했다.'
        self.blocked(before, after, before.replace('10 MW','20 MW'))
        self.validate(before, after, after)

    def test_metric_period_after_metric_is_bound(self):
        before = 'Alpha capacity in 2025 was 10 MW and capacity in 2026 was 20 MW. Gamma may be delayed.'
        after = 'Alpha capacity in 2025 was 20 MW and capacity in 2026 was 10 MW. Gamma is delayed.'
        quote = 'Alpha capacity in 2025 was 10 MW and capacity in 2026 was 20 MW. Gamma is delayed.'
        self.blocked(before, after, quote, ('quantitative_anchor','changed_state'))
        self.validate(before, after, after, ('quantitative_anchor','changed_state'))

    def test_case_only_duplicate_is_not_novel(self):
        self.blocked('Alpha was approved.', 'Alpha was approved. alpha was approved.',
                     'Alpha was approved. alpha was approved.', ('changed_state',))
        self.validate('Alpha was approved.', 'Alpha was approved. Beta was approved.',
                      'Alpha was approved. Beta was approved.', ('changed_state',))

    def test_state_pronoun_keeps_immediate_topic(self):
        before = 'Capacity is 10 MW. Alpha project. It may be approved. Beta project. It is approved.'
        after = 'Capacity is 20 MW. Alpha project. It is approved. Beta project. It may be approved.'
        quote = 'Capacity is 20 MW. Alpha project. It may be approved. Beta project. It is approved.'
        self.blocked(before, after, quote, ('quantitative_anchor','changed_state'))
        self.validate(before, after, after, ('quantitative_anchor','changed_state'))

    def test_unlocked_top_level_v4_declaration_cannot_disable_v5(self):
        proc, result = self.standalone(
            'Capacity is 10 MW.', 'Capacity is 20 MW.', 'Capacity is 20 MW.',
            fake_v4=True, remove_audit=True)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertTrue(any('locked' in (x.get('message') or '').lower() for x in result['findings']), result['findings'])

    def test_python_preflight_uses_registry_from_locked_revision(self):
        current_registry = json.loads((ROOT/'docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json').read_text())
        fields = ('active_canonical','active_named_prompts','active_validator_contracts','open_remediations',
                  'activation_required_migrations','superseded','reference_only')
        locked_registry = copy.deepcopy(current_registry)
        for field in fields:
            locked_registry[field] = [p for p in locked_registry[field] if not p.startswith('docs/audits/pr385/')]
        docs = sorted({p for field in fields for p in locked_registry[field]})
        payload = {
            'docs_inventory_count':len(docs),'classified_count':len(docs),
            'active_full_read_count':len(set(locked_registry['active_canonical'])|set(locked_registry['active_named_prompts'])|
                                         set(locked_registry['active_validator_contracts'])|set(locked_registry['open_remediations'])|
                                         set(locked_registry['activation_required_migrations'])),
            'active_canonical_paths':locked_registry['active_canonical']+locked_registry['active_named_prompts'],
            'active_validator_contract_paths':locked_registry['active_validator_contracts'],
            'applicable_remediation_or_migration':locked_registry['open_remediations']+locked_registry['activation_required_migrations'],
            'superseded_or_reference_paths':locked_registry['superseded']+locked_registry['reference_only'],
        }
        manifest = ROOT/'tmp-final-codex-preflight.json'
        manifest.write_text(json.dumps(payload), encoding='utf-8')
        def fake_git(args):
            if args[:1] == ['show']:
                return json.dumps(locked_registry)
            if args[:4] == ['ls-tree','-r','--name-only',BASE_343]:
                return '\n'.join(docs)
            raise AssertionError(args)
        try:
            with mock.patch.object(binding, '_git', side_effect=fake_git):
                binding.validate_preflight({'document_universe_manifest_ref':manifest.name,'base_main_commit_sha':BASE_343})
        finally:
            manifest.unlink(missing_ok=True)



if __name__ == '__main__':
    unittest.main()
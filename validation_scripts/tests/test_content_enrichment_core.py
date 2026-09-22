"""Shared-policy regressions; synthetic evidence, not production publication."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest import mock

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_enrichment_core as core
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

ROOT = Path(__file__).resolve().parents[2]
DENSE = ('prior_state', 'changed_state', 'quantitative_anchor', 'boundary_or_uncertainty')
TENTATIVE = 'Previously planned at 10 MW; Alpha may be approved; target remains subject to permit.'
REALIZED = TENTATIVE.replace('may be approved', 'was approved')


def full(chain, operation=None):
    row = chain['0.6'][0]
    binding.validate_content_enrichment_delta(
        chain, 'shared-policy-test', operation_card=copy.deepcopy(row) if operation is None else operation,
        locked_prompt_version='PROMPT_0_6_V5_20260919',
    )


class SharedCoreTests(unittest.TestCase):
    def test_entrypoints_share_normalizer_and_occurrence_matcher(self):
        self.assertIs(binding._normalize_text, core._normalize_text)
        self.assertIs(stage._normalize_text, core._normalize_text)
        self.assertIs(binding._normalized_visible_value, stage._normalized_visible_value)
        self.assertIs(binding._strength_multiset_covers, core._strength_multiset_covers)

    def test_normalization_preserves_substantive_operators_and_retraction(self):
        for text in ('- 10 MW', '> 10 MW', '−10 MW', '20억원', '20조원', '~~approved~~', '<del>approved</del>'):
            with self.subTest(text=text):
                self.assertEqual(core._normalize_text(text), text)
        self.assertEqual(core._normalize_text('**Alpha\nwas approved.**'), 'Alpha was approved.')

    def test_snapshot_detaches_every_mutable_level(self):
        support={'S': {'fact'}}; texts={'S': ['Alpha was approved.']}
        packages={'S': [{'source_quote': 'Alpha was approved.', 'nested': {'items': [1]}}]}
        ctx=core.ResolvedEvidenceContext.from_maps(scope='bound_upstream',support=support,texts=texts,packages=packages)
        support['S'].clear(); texts['S'].append('forged'); packages['S'][0]['nested']['items'].append(2)
        a,b,c=ctx.legacy_maps()
        self.assertEqual(a, {'S': {'fact'}}); self.assertEqual(b, {'S': ['Alpha was approved.']})
        self.assertEqual(c['S'][0]['nested']['items'], [1])
        c['S'][0]['nested']['items'].append(3); a['S'].clear(); b['S'].clear()
        self.assertEqual(ctx.legacy_maps()[2]['S'][0]['nested']['items'], [1])
        self.assertEqual(ctx.legacy_maps()[0]['S'], {'fact'})
        with self.assertRaises(FrozenInstanceError): ctx.scope='local_row'

    def test_snapshot_is_deterministic_for_mapping_and_support_order(self):
        a=core.ResolvedEvidenceContext.from_maps(scope='local_row',support={'B': {'fact','sub'},'A': {'fact'}},
             texts={'B': ['b'],'A': ['a']},packages={'B': [{'quote':'b','fetched':True}],'A': []})
        b=core.ResolvedEvidenceContext.from_maps(scope='local_row',support={'A': ['fact'],'B': ['sub','fact']},
             texts={'A': ['a'],'B': ['b']},packages={'A': [],'B': [{'fetched':True,'quote':'b'}]})
        self.assertEqual(a,b)

    def test_local_context_does_not_claim_upstream_or_operation_validation(self):
        ctx=core.ResolvedEvidenceContext.from_maps(scope='local_row', support={}, texts={}, packages={})
        self.assertEqual(set(ctx.unverified_scopes), {'locked_upstream_authority','actual_visible_copy_delta','materialized_operation'})

    def test_snapshot_rejects_missing_maps_and_unknown_scope(self):
        for kwargs in ({'scope':'trusted_because_row_says_pass','support':{},'texts':{},'packages':{}},
                       {'scope':'local_row','support':None,'texts':{},'packages':{}},
                       {'scope':'local_row','support':{'S':{'invented_field'}},'texts':{},'packages':{}},
                       {'scope':'local_row','support':{},'texts':{'S':[None]},'packages':{}}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                core.ResolvedEvidenceContext.from_maps(**kwargs)

    def test_full_path_resolves_authoritative_packages_once(self):
        chain=chain_for('Capacity is 10 MW','Capacity is 20 MW','Capacity is 20 MW')
        with mock.patch.object(binding,'_nearest_upstream_evidence_packages',wraps=binding._nearest_upstream_evidence_packages) as resolve:
            full(chain)
            self.assertEqual(resolve.call_count,1)

    def test_shape_count_and_mode_cannot_be_boolean_shortcuts(self):
        density=chain_for(REALIZED,REALIZED,REALIZED,DENSE)['0.6'][0]['content_enrichment_audit']['density_audit']
        for value in (True,'4',None):
            with self.subTest(value=value):
                item=copy.deepcopy(density);item['supported_dimension_count']=value
                self.assertIn('C06.DENSITY.COUNT_TYPE',[f.rule_id for f in core.density_policy_issues(item,no_change=True)])
        with self.assertRaises(ValueError): core.density_policy_issues(density,no_change='true')
        self.assertFalse(core.density_policy_issues(density,no_change=True))

    def test_density_minimum_is_mode_specific(self):
        density=chain_for('Capacity is 10 MW','Capacity is 20 MW','Capacity is 20 MW')['0.6'][0]['content_enrichment_audit']['density_audit']
        self.assertFalse(core.density_policy_issues(density,no_change=False))
        self.assertIn('C06.DENSITY.MINIMUM',[f.rule_id for f in core.density_policy_issues(density,no_change=True)])

    def test_grounding_realization_mode_is_explicit(self):
        counts=Counter({'approval':1}); strengths={'alpha=>approval':[1]}
        self.assertFalse(core.grounding_issues('changed_state',counts,counts,strengths,strengths,require_realized=False))
        issues=core.grounding_issues('changed_state',counts,counts,strengths,strengths,require_realized=True)
        self.assertEqual([x.rule_id for x in issues],['C06.GROUNDING.REALIZED'])
        with self.assertRaises(ValueError):
            core.grounding_issues('changed_state',counts,counts,strengths,strengths,require_realized=None)

    def test_missing_subject_modality_or_occurrence_still_blocks(self):
        cases=(
            (Counter({'approval':2}),Counter({'approval':1}),{'alpha=>approval':[2]},{'alpha=>approval':[2]},'C06.GROUNDING.OCCURRENCES'),
            (Counter({'approval':1}),Counter({'approval':1}),{'alpha=>approval':[2]},{'alpha=>approval':[1]},'C06.GROUNDING.MODALITY'),
            (Counter({'approval':1}),Counter({'approval':1}),{'alpha=>approval':[2]},{'beta=>approval':[2]},'C06.GROUNDING.MODALITY'),
        )
        for vc,ec,vs,es,code in cases:
            with self.subTest(code=code):
                self.assertIn(code,[x.rule_id for x in core.grounding_issues('changed_state',vc,ec,vs,es,require_realized=False)])

    def test_full_and_standalone_both_reject_tentative_zero_delta(self):
        chain=chain_for(TENTATIVE,TENTATIVE,TENTATIVE,DENSE)
        with self.assertRaisesRegex(binding.Blocked,'realized strength-2'): full(chain)
        findings=stage._content_enrichment_audit_findings(chain['0.6'][0],'test')
        self.assertIn('C06.GROUNDING.REALIZED',[f.get('rule_id') for f in findings])

    def test_full_and_standalone_accept_grounded_tentative_changed_copy(self):
        before='Capacity is 10 MW; Alpha project.'
        after='Capacity is 20 MW; Alpha may be delayed.'
        chain=chain_for(before,after,after,('quantitative_anchor','changed_state','boundary_or_uncertainty'))
        full(chain)
        self.assertFalse(stage._content_enrichment_audit_findings(chain['0.6'][0],'test'))

    def test_full_and_standalone_accept_realized_zero_delta(self):
        chain=chain_for(REALIZED,REALIZED,REALIZED,DENSE)
        full(chain)
        self.assertFalse(stage._content_enrichment_audit_findings(chain['0.6'][0],'test'))

    def test_both_entrypoints_actually_call_shared_grounding_policy(self):
        chain=chain_for(REALIZED,REALIZED,REALIZED,DENSE)
        for action in (lambda:full(chain),lambda:stage._content_enrichment_audit_findings(chain['0.6'][0],'test')):
            with mock.patch.object(core,'grounding_issues',wraps=core.grounding_issues) as check:
                action();self.assertEqual(check.call_count,4)
                self.assertTrue(all(call.kwargs['require_realized'] for call in check.call_args_list))

    def test_context_refactor_preserves_upstream_exclusion(self):
        chain=chain_for('Capacity is 10 MW','Capacity is 20 MW','Capacity is 20 MW')
        chain['0.5'][0]['source_discovery_ledger']=[{'source_id':'SRC1','visible_supports':[]}]
        with self.assertRaises(binding.Blocked): full(chain)

    def test_context_refactor_preserves_operation_copy_binding(self):
        chain=chain_for('Capacity is 10 MW','Capacity is 20 MW','Capacity is 20 MW')
        operation=copy.deepcopy(chain['0.6'][0]);operation['fact']='Capacity is 999 MW'
        with self.assertRaisesRegex(binding.Blocked,'operation visible copy'): full(chain,operation)

    def test_context_refactor_preserves_source_package_binding(self):
        chain=chain_for('Capacity is 10 MW','Capacity is 20 MW','Capacity is 20 MW')
        operation=copy.deepcopy(chain['0.6'][0]);operation['fact_sources'][0]['fetched']=False
        with self.assertRaises(binding.Blocked): full(chain,operation)

    def run_cli(self,chain):
        row=copy.deepcopy(chain['0.6'][0]);row.update(
            language_terminology_polished=True,
            related_lineage={'status':'PASS','relation_type':'new_unrelated_event','related_ids':[]},
            date_role={'representative_date':'2026-09-01'},source_diversity_status='PASS_MULTI_SOURCE')
        payload={'stage':'0.6','upstream_lineage_integrity':'PASS','lineage_and_anchor_guard':'PASS',
                 'content_enriched_and_language_polished':[row]}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'input.json';path.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
            proc=subprocess.run([sys.executable,str(ROOT/'validation_scripts/stage_artifact_contract_check.py'),'0.6',str(path)],
                                cwd=tmp,text=True,capture_output=True,timeout=30)
        return proc,json.loads(proc.stdout)

    def test_actual_standalone_cli_blocks_tentative_zero_delta(self):
        proc,result=self.run_cli(chain_for(TENTATIVE,TENTATIVE,TENTATIVE,DENSE))
        self.assertEqual(proc.returncode,1,proc.stderr)
        self.assertIn('C06.GROUNDING.REALIZED',[f.get('rule_id') for f in result['findings']])

    def test_actual_standalone_cli_accepts_grounded_tentative_change(self):
        after='Capacity is 20 MW; Alpha may be delayed.'
        proc,result=self.run_cli(chain_for('Capacity is 10 MW; Alpha project.',after,after,
                                          ('quantitative_anchor','changed_state','boundary_or_uncertainty')))
        self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout);self.assertEqual(result['status'],'PASS')

    def test_missing_upstream_context_cannot_certify_a_full_transition(self):
        chain=chain_for('Capacity is 10 MW','Capacity is 20 MW','Capacity is 20 MW')
        del chain['C']
        with self.assertRaises(binding.Blocked): full(chain)

    def test_standalone_cli_exposes_unverified_scopes_even_on_pass(self):
        proc,result=self.run_cli(chain_for(REALIZED,REALIZED,REALIZED,DENSE))
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(result['validation_scope'], {
            'mode':'stage_artifact_only',
            'not_verified':['upstream_evidence_authority','actual_visible_copy_delta','materialized_operation'],
        })

if __name__=='__main__': unittest.main()

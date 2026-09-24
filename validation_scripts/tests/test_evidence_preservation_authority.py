"""Source preservation is not permission to ground a visible claim.

All fixtures are synthetic. Tests use real bound-content and standalone paths;
no validator or permission resolver is replaced. This is not publication proof.
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_enrichment_core as core
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

ROOT = Path(__file__).resolve().parents[2]
V5 = 'PROMPT_0_6_V5_20260919'
U1 = 'https://example.test/source'
U2 = 'https://example.test/paraphrase'


def fixture(extra=None):
    chain = copy.deepcopy(chain_for('Capacity is 10 MW', 'Capacity is 20 MW', 'Capacity is 20 MW.'))
    src = copy.deepcopy(chain['C'][0]['fact_sources'][0])
    sources = [src] + ([copy.deepcopy(extra)] if extra else [])
    for name in ('B', 'C', '0.4', '0.5', '0.6'):
        chain[name][0]['fact_sources'] = copy.deepcopy(sources)
    chain['0.6'][0]['prompt_provenance_0_6'] = {'prompt_version': V5}
    return chain


def paraphrase(**extra):
    return {'source_id': 'SRC2', 'source_url': U2, 'source_quote': '',
            'source_quote_status': 'not_applicable_paraphrase_only', 'fetched': True,
            'claim': 'Capacity is 999 MW.', 'supports': ['fact'], **extra}


def run_bound(chain, card=None):
    binding.validate_content_enrichment_delta(chain, 'evidence-preservation',
        operation_card=copy.deepcopy(chain['0.6'][0]) if card is None else card,
        locked_prompt_version=V5)


def remap(chain, ref):
    chain['0.6'][0]['content_enrichment_audit']['density_audit']['dimension_evidence']['quantitative_anchor']['evidence_refs'] = [ref]


def cli(row):
    row = copy.deepcopy(row)
    row.update(language_terminology_polished=True,
        related_lineage={'status': 'PASS', 'relation_type': 'new_unrelated_event', 'related_ids': []},
        date_role={'representative_date': '2026-09-01'}, source_diversity_status='PASS_MULTI_SOURCE')
    payload = {'stage': '0.6', 'upstream_lineage_integrity': 'PASS', 'lineage_and_anchor_guard': 'PASS',
               'content_enriched_and_language_polished': [row]}
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)/'stage-0-6.json'
        path.write_text(json.dumps(payload), encoding='utf-8')
        proc = subprocess.run([sys.executable, str(ROOT/'validation_scripts/stage_artifact_contract_check.py'),
                               '0.6', str(path)], cwd=temp, text=True, capture_output=True, timeout=45)
    return proc.returncode, json.loads(proc.stdout)


class EvidencePreservationTests(unittest.TestCase):
    def test_f18_preserving_upstream_paraphrase_does_not_introduce_a_source(self):
        run_bound(fixture(paraphrase()))

    def test_metadata_only_sources_remain_preservable_not_usable(self):
        for record in (paraphrase(), paraphrase(source_quote_status='body_level_evidence_verified'),
                       paraphrase(source_quote_status='body_quote_verified'),
                       paraphrase(fetched=False)):
            with self.subTest(record=record):
                chain = fixture(record)
                run_bound(chain)
                self.assertNotIn('SRC2', binding._resolve_content_evidence_context(chain, 'x').legacy_maps()[1])

    def test_unverified_source_cannot_ground_even_when_preserved(self):
        chain = fixture(paraphrase(source_quote='Capacity is 20 MW.'))
        remap(chain, 'SRC2')
        with self.assertRaises(binding.Blocked): run_bound(chain)
        self.assertTrue(stage._content_enrichment_audit_findings(chain['0.6'][0], 'x'))

    def test_claim_only_verified_looking_source_cannot_ground(self):
        chain = fixture(paraphrase(source_quote_status='body_quote_verified', claim='Capacity is 20 MW.'))
        remap(chain, 'SRC2')
        with self.assertRaises(binding.Blocked): run_bound(chain)

    def test_dropping_non_grounding_source_is_not_a_workaround(self):
        chain = fixture(paraphrase()); card = copy.deepcopy(chain['0.6'][0])
        card['fact_sources'].pop()
        with self.assertRaisesRegex(binding.Blocked, 'drops authoritative'): run_bound(chain, card)

    def test_dropping_unreferenced_usable_source_still_blocks(self):
        chain = fixture(paraphrase(source_quote='Capacity is 20 MW.', source_quote_status='body_quote_verified'))
        card = copy.deepcopy(chain['0.6'][0]); card['fact_sources'].pop()
        with self.assertRaisesRegex(binding.Blocked, 'drops authoritative'): run_bound(chain, card)

    def test_usable_quote_does_not_make_context_source_grounding_evidence(self):
        context = paraphrase(source_quote='Capacity is 20 MW.', source_quote_status='body_quote_verified',
                             supporting_context_only_not_visible_claim_support=True)
        chain = fixture(context); run_bound(chain)
        remap(chain, 'SRC2')
        with self.assertRaises(binding.Blocked): run_bound(chain)

    def test_new_context_only_source_cannot_evade_source_inventory(self):
        chain = fixture(); card = copy.deepcopy(chain['0.6'][0])
        card['fact_sources'].append(paraphrase(supporting_context_only_not_visible_claim_support=True))
        with self.assertRaisesRegex(binding.Blocked, 'introduces evidence source tokens'): run_bound(chain, card)

    def test_new_non_grounding_ledger_source_is_still_new(self):
        chain = fixture(); card = copy.deepcopy(chain['0.6'][0])
        card['source_discovery_ledger'] = [paraphrase(outcome='not_used', supports=[])]
        with self.assertRaisesRegex(binding.Blocked, 'introduces evidence source tokens'): run_bound(chain, card)

    def test_existing_context_record_is_preserved(self):
        chain = fixture(paraphrase(evidence_role='context_only', supports=[])); run_bound(chain)
        card = copy.deepcopy(chain['0.6'][0]); card['fact_sources'].pop()
        with self.assertRaisesRegex(binding.Blocked, 'drops authoritative'): run_bound(chain, card)

    def test_unreferenced_source_verification_cannot_be_upgraded_downstream(self):
        chain = fixture(paraphrase()); card = copy.deepcopy(chain['0.6'][0])
        card['fact_sources'][1].update(source_quote_status='body_quote_verified', source_quote='Capacity is 20 MW.')
        with self.assertRaisesRegex(binding.Blocked, 'source-token bindings|source record'): run_bound(chain, card)

    def test_non_grounding_source_metadata_cannot_change(self):
        for key, value in (('claim', 'Capacity is 5 MW.'), ('fetched', False), ('supports', ['fact', 'sub']),
                           ('evidence_role', 'primary_event_evidence')):
            with self.subTest(key=key):
                chain = fixture(paraphrase()); card = copy.deepcopy(chain['0.6'][0]);card['fact_sources'][1][key]=value
                with self.assertRaisesRegex(binding.Blocked, 'source-token bindings|source record'): run_bound(chain, card)

    def test_same_tokens_cannot_hide_extra_source_record(self):
        chain = fixture(paraphrase()); card = copy.deepcopy(chain['0.6'][0])
        card['fact_sources'].append(paraphrase(claim='a different claim'))
        with self.assertRaisesRegex(binding.Blocked, 'source-token bindings|source record'): run_bound(chain, card)

    def test_removing_an_exclusion_record_cannot_restore_authority(self):
        chain = fixture(paraphrase(supports=[]))
        for name in ('B', 'C', '0.4', '0.5', '0.6'):
            chain[name][0]['source_discovery_ledger'] = [paraphrase(outcome='not_used', supports=[])]
        card = copy.deepcopy(chain['0.6'][0]); card['source_discovery_ledger'] = []
        with self.assertRaisesRegex(binding.Blocked, 'source-token bindings|source record'): run_bound(chain, card)

    def test_source_container_role_cannot_change_downstream(self):
        chain = fixture(paraphrase()); card = copy.deepcopy(chain['0.6'][0])
        card['source_discovery_ledger'] = [card['fact_sources'].pop()]
        with self.assertRaisesRegex(binding.Blocked, 'source-token bindings|source record'): run_bound(chain, card)

    def test_source_order_and_dictionary_key_order_do_not_matter(self):
        chain = fixture(paraphrase()); card = copy.deepcopy(chain['0.6'][0])
        card['fact_sources'] = [dict(reversed(list(s.items()))) for s in reversed(card['fact_sources'])]
        run_bound(chain, card)

    def test_nearest_source_record_is_preserved_without_older_metadata_union(self):
        chain = fixture(paraphrase())
        chain['B'][0]['fact_sources'][1]['claim'] = 'Older version.'
        chain['C'][0]['fact_sources'][1]['claim'] = 'Another older version.'
        run_bound(chain)

    def test_missing_nearer_source_falls_back_to_older_record(self):
        chain = fixture(paraphrase())
        for name in ('0.4', '0.5'): chain[name][0].pop('fact_sources')
        run_bound(chain)

    def test_nearer_unusable_quote_does_not_fall_back_to_stale_verified_quote(self):
        chain = fixture()
        chain['0.5'][0]['fact_sources'][0]['source_quote'] = ''
        with self.assertRaisesRegex(binding.Blocked, 'grounded|package|evidence'): run_bound(chain)

    def test_alias_added_only_downstream_is_rejected(self):
        chain = fixture(paraphrase()); card = copy.deepcopy(chain['0.6'][0])
        card['fact_sources'][1]['canonical_url'] = 'https://example.test/new-alias'
        with self.assertRaisesRegex(binding.Blocked, 'introduces evidence source tokens'): run_bound(chain, card)

    def test_no_alias_source_substitution_using_same_quote(self):
        chain = fixture(); card=copy.deepcopy(chain['0.6'][0]);card['fact_sources'][0]['source_url']=U2
        with self.assertRaises(binding.Blocked): run_bound(chain,card)

    def test_original_fact_and_source_inputs_are_not_mutated(self):
        chain=fixture(paraphrase());before=copy.deepcopy(chain); run_bound(chain);self.assertEqual(chain,before)

    def test_known_historical_v4_policy_is_not_reclassified(self):
        chain=fixture(paraphrase());chain['0.6'][0]['prompt_provenance_0_6']['prompt_version']='PROMPT_0_6_V4_20260901'
        binding.validate_content_enrichment_delta(chain,'historical',operation_card=copy.deepcopy(chain['0.6'][0]),
            locked_prompt_version='PROMPT_0_6_V4_20260901')

    def test_new_standalone_cli_accepts_preserved_paraphrase_only_as_metadata(self):
        rc,result=cli(fixture(paraphrase())['0.6'][0]); self.assertEqual(rc,0,result)

    def test_source_field_scope_order_is_not_a_substantive_source_change(self):
        chain=fixture(paraphrase(supports=['fact','sub']));card=copy.deepcopy(chain['0.6'][0])
        card['fact_sources'][1]['supports']=['sub','fact']
        run_bound(chain,card)

    def test_actual_update_materialization_preserves_metadata_only_source(self):
        chain=fixture(paraphrase());base=copy.deepcopy(chain['C'][0]);base['id']='CARD'
        op={'id':'CARD','changes':[{'op':'replace','path':'/fact','value':chain['0.6'][0]['fact']}]}
        card=binding._materialized_operation_card('update',op,'SPEC',{}, {}, {'CARD':base}, {}, {},'update[0]')
        run_bound(chain,card)
        self.assertEqual(base['fact'],'Capacity is 10 MW')
        op['changes'].append({'op':'remove','path':'/fact_sources/1'})
        card=binding._materialized_operation_card('update',op,'SPEC',{}, {}, {'CARD':base}, {}, {},'update[0]')
        with self.assertRaisesRegex(binding.Blocked,'drops authoritative'):run_bound(chain,card)

    def test_actual_insert_materialization_preserves_metadata_only_source(self):
        chain=fixture(paraphrase());op={'card':copy.deepcopy(chain['0.6'][0])}
        card=binding._materialized_operation_card('insert',op,'SPEC',{}, {}, {}, {}, {},'insert[0]')
        run_bound(chain,card)
        self.assertIsNot(card,op['card'])


class SharedEvidenceAuthorityTests(unittest.TestCase):
    def test_f14_full_claim_coverage_cannot_widen_explicit_scope(self):
        chain=fixture()
        for name in ('B','C','0.4','0.5','0.6'):
            row=chain[name][0];row['fact_sources'][0]['visible_supports']=['sub']
            row['claim_source_coverage']={'visible_fact':{'supported_by_source_ids':['SRC1']}}
        self.assertEqual(binding._upstream_evidence_token_support(chain,'x')['SRC1'],{'sub'})
        with self.assertRaisesRegex(binding.Blocked,'do not support mapped visible fields'):
            binding.validate_content_enrichment_delta(chain,'x',locked_prompt_version=V5)
        with self.assertRaisesRegex(binding.Blocked,'do not support mapped visible fields'): run_bound(chain)
        self.assertTrue(stage._content_enrichment_audit_findings(chain['0.6'][0],'x'))

    def test_alias_cannot_restore_explicitly_scoped_fact_authority(self):
        chain=fixture();row=chain['0.6'][0]; row['fact_sources'][0]['supports']=['sub']
        row['claim_source_coverage']={'visible_fact':{'supported_by_source_ids':[U1]}}
        for resolver in (binding._row_evidence_token_support,stage._row_evidence_token_support):
            self.assertEqual(resolver(row)['SRC1'],{'sub'});self.assertEqual(resolver(row)[U1],{'sub'})

    def test_f15_standalone_exclusion_follows_id_url_alias(self):
        row=fixture()['0.6'][0];src=copy.deepcopy(row['fact_sources'][0]);src['outcome']='used_in_fact_sources'
        row['fact_sources']=[{'source_url':U1,'supporting_context_only_not_visible_claim_support':True}]
        row['source_discovery_ledger']=[src]
        self.assertEqual(stage._row_evidence_token_support(row),{})
        self.assertTrue(stage._content_enrichment_audit_findings(row,'x'))

    def test_transitive_alias_exclusions_are_order_independent(self):
        row=fixture()['0.6'][0];src=row['fact_sources'][0]
        row['source_discovery_ledger']=[
            {'source_url':U1,'canonical_url':U2,'supports':['fact']},
            {'source_url':U2,'supports':[]}]
        for reverse in (False,True):
            if reverse: row['source_discovery_ledger'].reverse()
            for resolver in (binding._row_evidence_token_support,stage._row_evidence_token_support,binding._materialized_card_evidence_support):
                self.assertEqual(resolver(row),{})

    def test_claim_coverage_cannot_undo_exclusion(self):
        row=fixture()['0.6'][0];row['fact_sources'][0]['supports']=[]
        row['claim_source_coverage']={'visible_fact':{'supported_by_source_ids':['SRC1',U1]}}
        self.assertEqual(binding._row_evidence_token_support(row),{})
        self.assertEqual(stage._row_evidence_token_support(row),{})

    def test_explicit_supported_fact_control_still_works(self):
        chain=fixture()
        for name in ('B','C','0.4','0.5','0.6'):
            row=chain[name][0];row['fact_sources'][0]['supports']=['fact']
            row['claim_source_coverage']={'visible_fact':{'supported_by_source_ids':['SRC1']}}
        run_bound(chain);self.assertFalse(stage._content_enrichment_audit_findings(chain['0.6'][0],'x'))

    def test_explicit_scope_cannot_be_widened_by_unscoped_alias_record(self):
        row=fixture()['0.6'][0];row['fact_sources'][0]['supports']=['sub']
        row['source_discovery_ledger']=[{'source_url':U1,'outcome':'used_in_fact_sources'}]
        for resolver in (binding._row_evidence_token_support,stage._row_evidence_token_support):
            self.assertEqual(resolver(row)['SRC1'],{'sub'})

    def test_real_cli_rejects_excluded_alias_with_positive_control(self):
        row=fixture()['0.6'][0];rc,result=cli(row);self.assertEqual(rc,0,result)
        src=copy.deepcopy(row['fact_sources'][0]);src['outcome']='used_in_fact_sources'
        row['fact_sources']=[{'source_url':U1,'supports':[]}];row['source_discovery_ledger']=[src]
        rc,result=cli(row);self.assertEqual(rc,1,result)
        self.assertTrue(any('evidence' in f.get('message','') for f in result['findings']))

    def test_real_cli_rejects_scoped_alias_with_positive_control(self):
        row=fixture()['0.6'][0];row['fact_sources'][0]['supports']=['sub']
        row['claim_source_coverage']={'visible_fact':{'supported_by_source_ids':[U1]}}
        rc,result=cli(row);self.assertEqual(rc,1,result)

    def test_preservation_snapshot_detaches_both_inputs_and_outputs(self):
        records=[{'container':'fact_sources','source':paraphrase()}]
        ctx=core.ResolvedEvidenceContext.from_maps(scope='bound_upstream',support={},texts={},packages={},source_records=records)
        records[0]['source']['claim']='mutation'
        result=ctx.source_records();self.assertEqual(result[0]['source']['claim'],'Capacity is 999 MW.')
        result[0]['source']['supports'].clear();self.assertEqual(ctx.source_records()[0]['source']['supports'],['fact'])

    def test_context_without_inventory_does_not_claim_to_validate_preservation(self):
        ctx=core.ResolvedEvidenceContext.from_maps(scope='local_row',support={},texts={},packages={})
        self.assertIsNone(ctx.source_records())

    def test_entrypoints_share_source_scope_helper(self):
        self.assertIs(stage._source_supported_visible_fields,binding._source_supported_visible_fields)
        self.assertIs(stage._evidence_tokens,binding._evidence_tokens)

    def test_invalid_source_snapshot_is_not_silently_authorized(self):
        for value in ({},[{'container':'invented','source':paraphrase()}],[{'container':'fact_sources','source':True}]):
            with self.subTest(value=value),self.assertRaises(ValueError):
                core.ResolvedEvidenceContext.from_maps(scope='bound_upstream',support={},texts={},packages={},source_records=value)


if __name__=='__main__':unittest.main()

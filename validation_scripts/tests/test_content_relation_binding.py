"""Finite relation counterexamples: retain original inputs and genuine controls.

Fixtures model source metadata, not authentication of a live news source. Bound
checks supply the materialized card; standalone assertions name their own scope.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import stage_artifact_contract_check as standalone
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

DENSE = ('prior_state', 'changed_state', 'quantitative_anchor', 'boundary_or_uncertainty')
ROOT = Path(__file__).resolve().parents[2]


class RelationBindingTests(unittest.TestCase):
    def check(self, prior, current, quote, dimensions=('quantitative_anchor',)):
        chain = chain_for(prior, current, quote, dimensions)
        binding.validate_content_enrichment_delta(
            chain, 'relation regression', operation_card=copy.deepcopy(chain['0.6'][0]),
            locked_prompt_version='PROMPT_0_6_V5_20260919')
        return chain

    def blocked(self, *args, **kwargs):
        with self.assertRaises(binding.Blocked):
            self.check(*args, **kwargs)

    def test_korean_copular_claim_cannot_hitchhike_on_quantity(self):
        self.blocked('용량은 10 MW이다.', '용량은 20 MW이다. 알파는 선두 기업이다.', '용량은 20 MW이다.')

    def test_grounded_korean_copular_claim_passes(self):
        current = '용량은 20 MW이다. 알파는 선두 기업이다.'
        self.check('용량은 10 MW이다.', current, current)

    def test_modified_common_noun_state_swap_blocks(self):
        before = 'The northern refinery may be approved. The southern refinery is approved. Capacity is 10 MW.'
        after = 'The northern refinery is approved. The southern refinery may be approved. Capacity is 20 MW.'
        self.blocked(before, after, before.replace('10 MW', '20 MW'), ('changed_state','quantitative_anchor'))

    def test_grounded_modified_common_noun_state_swap_passes(self):
        before = 'The northern refinery may be approved. The southern refinery is approved. Capacity is 10 MW.'
        after = 'The northern refinery is approved. The southern refinery may be approved. Capacity is 20 MW.'
        self.check(before, after, after, ('changed_state','quantitative_anchor'))

    def test_possessive_proper_subject_addition_blocks(self):
        before = 'Alpha project. Capacity is 10 MW.'
        after = "Alpha's plant sells coal. Capacity is 20 MW."
        self.blocked(before, after, 'Capacity is 20 MW.')

    def test_grounded_possessive_proper_subject_addition_passes(self):
        before = 'Alpha project. Capacity is 10 MW.'
        after = "Alpha's plant sells coal. Capacity is 20 MW."
        self.check(before, after, after)

    def test_location_relation_change_blocks(self):
        before = 'Alpha is in Texas. Capacity is 10 MW.'
        after = 'Alpha is from Texas. Capacity is 20 MW.'
        self.blocked(before, after, 'Alpha is in Texas. Capacity is 20 MW.')

    def test_grounded_location_relation_change_passes(self):
        before = 'Alpha is in Texas. Capacity is 10 MW.'
        after = 'Alpha is from Texas. Capacity is 20 MW.'
        self.check(before, after, after)

    def test_korean_description_cannot_hitchhike_on_quantity(self):
        self.blocked('용량은 10 MW이다.', '용량은 20 MW이다. 알파는 수익성이 높다.', '용량은 20 MW이다.')

    def test_grounded_korean_description_passes(self):
        current = '용량은 20 MW이다. 알파는 수익성이 높다.'
        self.check('용량은 10 MW이다.', current, current)

    def test_korean_descriptive_tokens_are_not_empty(self):
        for text in ('알파는 수익성이 높다.', '알파는 비용이 낮다.', '알파는 수익성이 없다.'):
            with self.subTest(text=text):
                self.assertTrue(binding._korean_factual_tokens(text))

    def test_korean_description_subject_swap_blocks(self):
        before = '알파는 수익성이 높다. 베타는 수익성이 낮다. 용량은 10 MW이다.'
        after = '알파는 수익성이 낮다. 베타는 수익성이 높다. 용량은 20 MW이다.'
        self.blocked(before, after, before.replace('10 MW', '20 MW'))

    def test_grounded_korean_description_subject_swap_passes(self):
        before = '알파는 수익성이 높다. 베타는 수익성이 낮다. 용량은 10 MW이다.'
        after = '알파는 수익성이 낮다. 베타는 수익성이 높다. 용량은 20 MW이다.'
        self.check(before, after, after)

    def test_korean_quantified_object_swap_blocks(self):
        before = '알파는 석탄을 10 MW 공정에 사용했다. 베타는 가스를 10 MW 공정에 사용했다. 용량은 10 MW이다.'
        after = '알파는 가스를 10 MW 공정에 사용했다. 베타는 석탄을 10 MW 공정에 사용했다. 용량은 20 MW이다.'
        self.blocked(before, after, before.replace('용량은 10 MW', '용량은 20 MW'))

    def test_grounded_korean_quantified_object_swap_passes(self):
        before = '알파는 석탄을 10 MW 공정에 사용했다. 베타는 가스를 10 MW 공정에 사용했다. 용량은 10 MW이다.'
        after = '알파는 가스를 10 MW 공정에 사용했다. 베타는 석탄을 10 MW 공정에 사용했다. 용량은 20 MW이다.'
        self.check(before, after, after)

    def test_korean_relation_counter_keeps_quantified_context(self):
        a = '알파는 석탄을 10 MW 공정에 사용했다.'
        b = '알파는 가스를 10 MW 공정에 사용했다.'
        self.assertTrue(binding._korean_factual_relation_counter(a))
        self.assertNotEqual(binding._korean_factual_relation_counter(a), binding._korean_factual_relation_counter(b))

    def test_korean_relation_still_keeps_unquantified_context(self):
        self.assertNotEqual(binding._korean_factual_relation_counter('알파는 석탄을 사용했다.'),
                            binding._korean_factual_relation_counter('알파는 가스를 사용했다.'))

    def test_boundary_subject_zero_delta_blocks_without_opt_in(self):
        text = 'Previously planned at 10 MW; Gamma was approved; Alpha target remains subject to permit.'
        self.blocked(text, text, text.replace('Alpha', 'Beta'), DENSE)

    def test_boundary_subject_positive_zero_delta(self):
        text = 'Previously planned at 10 MW; Gamma was approved; Alpha target remains subject to permit.'
        self.check(text, text, text, DENSE)

    def test_standalone_boundary_subject_zero_delta_blocks(self):
        text = 'Previously planned at 10 MW; Gamma was approved; Alpha target remains subject to permit.'
        row = chain_for(text, text, text.replace('Alpha','Beta'), DENSE)['0.6'][0]
        findings = standalone._content_enrichment_audit_findings(row, 'test')
        self.assertTrue(any('subject' in x.get('message','') for x in findings), findings)

    def test_repetition_is_not_novelty_even_when_quote_repeats(self):
        self.blocked('Alpha was approved.', 'Alpha was approved. Alpha was approved.',
                     'Alpha was approved. Alpha was approved.', ('changed_state',))

    def test_distinct_subject_is_genuine_new_state(self):
        self.check('Alpha was approved.', 'Alpha was approved. Beta was approved.',
                   'Alpha was approved. Beta was approved.', ('changed_state',))

    def test_real_increment_is_not_lost_due_to_repetition(self):
        self.check('Alpha was approved. Capacity is 10 MW.',
                   'Alpha was approved. Alpha was approved. Capacity is 20 MW.',
                   'Alpha was approved. Alpha was approved. Capacity is 20 MW.',
                   ('changed_state','quantitative_anchor'))

    def test_pronoun_topic_object_swap_blocks(self):
        before = 'Capacity is 10 MW. Alpha project. It sold coal. Beta project. It sold gas.'
        after = 'Capacity is 20 MW. Alpha project. It sold gas. Beta project. It sold coal.'
        self.blocked(before, after, before.replace('10 MW','20 MW'))

    def test_grounded_pronoun_topic_swap_passes(self):
        before = 'Capacity is 10 MW. Alpha project. It sold coal. Beta project. It sold gas.'
        after = 'Capacity is 20 MW. Alpha project. It sold gas. Beta project. It sold coal.'
        self.check(before, after, after)

    def test_transaction_recipient_regrouping_blocks(self):
        before = 'Capacity is 10 MW. Alpha sold coal to Beta. Alpha sold gas to Gamma.'
        after = 'Capacity is 20 MW. Alpha sold coal to Gamma. Alpha sold gas to Beta.'
        self.blocked(before, after, before.replace('10 MW','20 MW'))

    def test_grounded_transaction_recipient_regrouping_passes(self):
        before = 'Capacity is 10 MW. Alpha sold coal to Beta. Alpha sold gas to Gamma.'
        after = 'Capacity is 20 MW. Alpha sold coal to Gamma. Alpha sold gas to Beta.'
        self.check(before, after, after)

    def test_transaction_source_direction_is_not_erased(self):
        before = 'Capacity is 10 MW. Alpha acquired coal from Beta.'
        after = 'Capacity is 20 MW. Alpha acquired coal to Beta.'
        self.blocked(before, after, before.replace('10 MW','20 MW'))

    def test_metric_association_swap_blocks(self):
        before = 'Alpha capacity is 10 MW and output is 20 MW. Gamma may be delayed.'
        after = 'Alpha capacity is 20 MW and output is 10 MW. Gamma is delayed.'
        self.blocked(before, after, before.replace('may be delayed','is delayed'), ('quantitative_anchor','changed_state'))

    def test_grounded_metric_association_swap_passes(self):
        before = 'Alpha capacity is 10 MW and output is 20 MW. Gamma may be delayed.'
        after = 'Alpha capacity is 20 MW and output is 10 MW. Gamma is delayed.'
        self.check(before, after, after, ('quantitative_anchor','changed_state'))

    def test_metric_positive_plain_entity_quantity(self):
        self.check('Alpha capacity is 10 MW.', 'Alpha capacity is 20 MW.', 'Alpha capacity is 20 MW.')

    def test_standalone_metric_association_blocks(self):
        before = 'Alpha capacity is 10 MW and output is 20 MW. Gamma may be delayed.'
        after = 'Alpha capacity is 20 MW and output is 10 MW. Gamma is delayed.'
        row = chain_for(before, after, before.replace('may be delayed','is delayed'),
                        ('quantitative_anchor','changed_state'))['0.6'][0]
        findings = standalone._content_enrichment_audit_findings(row, 'test')
        self.assertTrue(any('metric' in x.get('message','') for x in findings), findings)

    def test_metric_positive_numeric_formatting(self):
        self.check('Alpha capacity is 10 MW. Gamma may be delayed.',
                   'Alpha capacity is 20.0 MW. Gamma is delayed.',
                   'Alpha capacity is 20 MW. Gamma is delayed.', ('quantitative_anchor','changed_state'))

    def test_quantity_subject_zero_delta_blocks_without_opt_in(self):
        text = 'Previously planned; Alpha capacity is 10 MW; Gamma was approved; target remains subject to permit.'
        self.blocked(text, text, text.replace('Alpha','Beta'), DENSE)



    def test_original_a06_trailing_quantities_preserve_roles(self):
        before = '알파는 석탄을 사용했다 10 MW. 베타는 가스를 사용했다 10 MW.'
        after = '알파는 가스를 사용했다 10 MW. 베타는 석탄을 사용했다 10 MW.'
        self.assertTrue(binding._korean_factual_relation_counter(before))
        self.assertNotEqual(binding._korean_factual_relation_counter(before), binding._korean_factual_relation_counter(after))

    def test_trailing_quantity_relation_bound_bad_and_good_quote(self):
        before = '알파는 석탄을 사용했다 10 MW. 베타는 가스를 사용했다 10 MW. 용량은 10 MW이다.'
        after = '알파는 가스를 사용했다 10 MW. 베타는 석탄을 사용했다 10 MW. 용량은 20 MW이다.'
        self.blocked(before, after, before.replace('용량은 10 MW','용량은 20 MW'))
        self.check(before, after, after)

    def test_metric_rebinding_requires_declaration_even_without_value_delta(self):
        before = 'Alpha capacity is 10 MW and output is 20 MW. Gamma may be delayed.'
        after = 'Alpha capacity is 20 MW and output is 10 MW. Gamma is delayed.'
        self.blocked(before, after, after, ('changed_state',))

    def test_metric_period_binding_cannot_be_permuted(self):
        before = 'Alpha 2025 capacity is 10 MW and 2026 capacity is 20 MW. Gamma may be delayed.'
        after = 'Alpha 2025 capacity is 20 MW and 2026 capacity is 10 MW. Gamma is delayed.'
        self.blocked(before, after, before.replace('may be delayed','is delayed'), ('quantitative_anchor','changed_state'))
        self.check(before, after, after, ('quantitative_anchor','changed_state'))

    def test_independent_transaction_sentence_order_is_not_semantic(self):
        before = 'Capacity is 10 MW. Alpha sold coal to Beta. Alpha sold gas to Gamma.'
        after = 'Capacity is 20 MW. Alpha sold gas to Gamma. Alpha sold coal to Beta.'
        quote = 'Capacity is 20 MW. Alpha sold coal to Beta. Alpha sold gas to Gamma.'
        self.check(before, after, quote)

    def test_transaction_ordered_tail_preserves_modal_and_negative_words(self):
        from validation_scripts import content_claim_relations as rel
        self.assertNotEqual(rel.english_relations('Alpha can sell coal to Beta.'),
                            rel.english_relations('Alpha must sell coal to Beta.'))
        self.assertNotEqual(rel.english_relations('Alpha did sell coal to Beta.'),
                            rel.english_relations('Alpha did not sell coal to Beta.'))

    def test_relation_sentence_split_preserves_decimals_and_initialisms(self):
        from validation_scripts import content_claim_relations as rel
        text = 'U.S. Battery sold 10.5 MW to Beta. Gamma sold 20 MW to Delta.'
        self.assertEqual(len(rel.clauses(text)), 2)
        self.assertEqual(len(rel.english_relations(text)), 2)
        self.assertNotEqual(rel.english_relations(text), rel.english_relations(text.replace('Beta','Delta',1)))

    def test_grounded_korean_quantified_context_reformat_passes(self):
        current = '알파는 석탄을 20.0 MW 공정에 사용했다. 용량은 20 MW이다.'
        self.check('알파는 석탄을 10 MW 공정에 사용했다. 용량은 10 MW이다.', current,
                   current.replace('20.0 MW','20 MW'))

    def test_unresolved_new_pronoun_is_not_a_self_certifying_match(self):
        self.blocked('Capacity is 10 MW.',
                     'Capacity is 20 MW. It sold coal to Beta.',
                     'Capacity is 20 MW. It sold coal to Beta.')

    def test_pronoun_resolution_does_not_cross_evidence_text_fragments(self):
        prior = 'Capacity is 10 MW.'
        current = 'Capacity is 20 MW. Alpha project. It sold coal.'
        chain = chain_for(prior, current, ['Capacity is 20 MW. Alpha project.', 'It sold coal.'])
        with self.assertRaises(binding.Blocked):
            binding.validate_content_enrichment_delta(chain, 'fragment test', operation_card=copy.deepcopy(chain['0.6'][0]),
                                                      locked_prompt_version='PROMPT_0_6_V5_20260919')

    def test_topic_pronoun_normal_positive(self):
        current = 'Capacity is 20 MW. Alpha project. It sold coal.'
        self.check('Capacity is 10 MW.', current, current)

    def test_topic_pronoun_does_not_cross_pipe_field_separator(self):
        from validation_scripts import content_claim_relations as rel
        result = rel.english_relations('Alpha project | It sold coal.')
        self.assertTrue(any(key[0] == 'relation:unresolved' for key in result), result)

    def test_same_company_different_goods_recipients_keep_whole_relations(self):
        from validation_scripts import content_claim_relations as rel
        source = 'Omega sold lithium to Buyer. Omega sold graphite to Client.'
        forged = 'Omega sold lithium to Client. Omega sold graphite to Buyer.'
        self.assertEqual(len(rel.english_relations(source)), 2)
        self.assertNotEqual(rel.english_relations(source), rel.english_relations(forged))

    def test_no_new_number_does_not_excuse_wrong_boundary_subject(self):
        before = 'Capacity is 10 MW; Alpha target remains subject to permit; Beta project.'
        after = 'Capacity is 20 MW; Beta target remains subject to permit; Alpha project.'
        self.blocked(before, after, before.replace('10 MW','20 MW'), ('quantitative_anchor','boundary_or_uncertainty'))
        self.check(before, after, after, ('quantitative_anchor','boundary_or_uncertainty'))

    def test_field_scoped_mapping_cannot_cross_metric_evidence(self):
        before = 'Alpha capacity is 10 MW and output is 20 MW. Gamma may be delayed.'
        after = 'Alpha capacity is 20 MW and output is 10 MW. Gamma is delayed.'
        chain = chain_for(before, after, before.replace('may be delayed','is delayed'),
                          ('quantitative_anchor','changed_state'))
        row = chain['0.6'][0]
        for entry in row['content_enrichment_audit']['density_audit']['dimension_evidence'].values():
            entry['field_evidence_refs'] = {'fact': entry['evidence_refs']}
        with self.assertRaises(binding.Blocked):
            binding.validate_content_enrichment_delta(chain, 'mapped test', operation_card=copy.deepcopy(row),
                                                      locked_prompt_version='PROMPT_0_6_V5_20260919')

    def test_exact_repeat_rule_does_not_fold_different_periods(self):
        from validation_scripts import content_claim_relations as rel
        first = rel.exact_clause_set(['Alpha 2025 output is 10 MW.'])
        second = rel.exact_clause_set(['Alpha 2026 output is 10 MW.'])
        self.assertNotEqual(first, second)

    def test_actual_standalone_cli_boundary_wrong_and_right_subject(self):
        text = 'Previously planned at 10 MW; Gamma was approved; Alpha target remains subject to permit.'
        for quote, expected in ((text,0),(text.replace('Alpha','Beta'),1)):
            with self.subTest(expected=expected):
                self.run_cli(chain_for(text,text,quote,DENSE)['0.6'][0], expected)

    def test_actual_standalone_cli_metric_wrong_and_right_assignment(self):
        before = 'Alpha capacity is 10 MW and output is 20 MW. Gamma may be delayed.'
        after = 'Alpha capacity is 20 MW and output is 10 MW. Gamma is delayed.'
        for quote, expected in ((after,0),(before.replace('may be delayed','is delayed'),1)):
            with self.subTest(expected=expected):
                self.run_cli(chain_for(before,after,quote,('quantitative_anchor','changed_state'))['0.6'][0],expected)

    def run_cli(self, row, expected):
        row = copy.deepcopy(row)
        row.update(language_terminology_polished=True,
                   related_lineage={'status':'PASS','relation_type':'new_unrelated_event','related_ids':[]},
                   date_role={'representative_date':'2026-09-01'}, source_diversity_status='PASS_MULTI_SOURCE')
        payload = {'stage':'0.6','upstream_lineage_integrity':'PASS','lineage_and_anchor_guard':'PASS',
                   'content_enriched_and_language_polished':[row]}
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'stage-0-6.json'; p.write_text(json.dumps(payload),encoding='utf-8')
            cmd = [sys.executable,str(ROOT/'validation_scripts/stage_artifact_contract_check.py'),'0.6',str(p)]
            proc = subprocess.run(cmd,cwd=temp,capture_output=True,text=True,timeout=30)
        self.assertEqual(proc.returncode,expected,proc.stdout+proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result['status'],'PASS' if expected==0 else 'BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT')
        if expected:
            self.assertIn('C06.GROUNDING.FIELD_IDENTITY',[item.get('rule_id') for item in result['findings']])


if __name__ == '__main__':
    unittest.main()

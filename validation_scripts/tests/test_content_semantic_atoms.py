"""Phase4a contracts: operators/scales and non-realized state scopes.

Fixtures are synthetic; passing these tests is not source truth certification.
The complete historical 32-case harness remains separate and unmodified.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_enrichment_core as core
from validation_scripts import content_semantic_atoms as atoms
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for
from validation_scripts.tests.test_content_enrichment_core import DENSE, REALIZED

ROOT = Path(__file__).resolve().parents[2]


def full(chain):
    row = chain['0.6'][0]
    binding.validate_content_enrichment_delta(
        chain, 'phase4a', operation_card=copy.deepcopy(row),
        locked_prompt_version='PROMPT_0_6_V5_20260919',
    )


def local(chain):
    return stage._content_enrichment_audit_findings(chain['0.6'][0], 'phase4a')


def q(text):
    return binding._signal_counter('quantitative_anchor', text)


class QuantityObservationTests(unittest.TestCase):
    def test_entrypoints_share_the_same_quantity_implementation(self):
        self.assertIs(binding.QUANT_SIGNAL_RE, atoms.QUANT_SIGNAL_RE)
        self.assertIs(binding._quantitative_signal_from_match, atoms.quantitative_signal_from_match)

    def test_observations_keep_source_span_and_are_immutable(self):
        text = 'Investment is −20억원.'
        atom, = atoms.quantitative_observations(text)
        self.assertEqual(text[atom.start:atom.end], atom.raw)
        self.assertEqual(atom.number, '2000000000')
        self.assertEqual(atom.currency_code, 'krw')
        self.assertEqual(atom.sign, '-')
        with self.assertRaises(FrozenInstanceError):
            atom.number = '20'

    def test_equivalent_minus_glyphs_preserve_polarity(self):
        for glyph in ('-', '−', '﹣', '－'):
            for text in (f'{glyph}10 MW', f'{glyph} 10 MW'):
                with self.subTest(text=text):
                    self.assertEqual(q(text), q('-10 MW'))
                    self.assertNotEqual(q(text), q('10 MW'))

    def test_fullwidth_plus_remains_an_explicit_plus(self):
        self.assertEqual(q('＋10 MW'), q('+10 MW'))
        self.assertNotEqual(q('＋10 MW'), q('-10 MW'))

    def test_bound_sign_unit_and_currency_remain_distinct(self):
        for a,b in (('−10 MW','10 MW'), ('>20억원','<20억원'),
                    ('20억원','20조원'), ('20억원','20억엔'),
                    ('20억원','20억유로'), ('20 MW','20 MWh')):
            with self.subTest(a=a,b=b):
                self.assertNotEqual(q(a),q(b))

    def test_dimensionless_rate_retains_its_denominator(self):
        self.assertNotEqual(q('20 per year'), q('20 per month'))
        self.assertNotEqual(q('20 per year'), q('20'))
        self.assertEqual(q('20 / year'), q('20 per year'))

    def test_single_scale_korean_amounts_use_exact_values(self):
        for text, value in (('20천원','20000'), ('20만원','200000'),
                            ('20백만원','20000000'), ('20억원','2000000000'),
                            ('20조원','20000000000000'), ('1.25억 원','125000000')):
            with self.subTest(text=text):
                self.assertEqual(q(text),q(value+'원'))

    def test_large_decimal_money_is_not_rounded(self):
        number='123456789012345678901234567890.123456'
        self.assertEqual(q(number+'억원'), q('12345678901234567890123456789012345600원'))

    def test_korean_dollar_does_not_guess_us_currency(self):
        self.assertNotEqual(q('20만 달러'),q('200000 USD'))
        self.assertEqual(atoms.quantitative_observations('20만달러')[0].currency_code,
                         'dollar_unspecified')

    def test_unsupported_compound_amount_is_not_split_into_bare_numbers(self):
        for text in ('1조 2000억원','1억2000만원','1조 2천억원','2천억원'):
            with self.subTest(text=text):
                self.assertTrue(atoms.unsupported_quantity_spans(text))
                self.assertFalse(atoms.quantitative_signals(text))

    def test_unsupported_quote_does_not_supply_an_inner_number(self):
        for text in ('1조 2000억원', '1조 2천억원'):
            with self.subTest(text=text):
                self.assertNotIn('1',q(text))
                self.assertNotIn('2',q(text))
                self.assertNotIn('200000000000 krw',q(text))

    def test_equivalent_korean_money_format_is_not_enrichment(self):
        chain=chain_for('투자액은 1억원이다.','투자액은 100000000원이다.',
                        '투자액은 100000000원이다.')
        with self.assertRaises(binding.Blocked): full(chain)

    def test_grounded_signed_quantity_passes_both_paths(self):
        for glyph in ('-', '−', '﹣', '－'):
            chain=chain_for('Capacity is 5 MW',f'Capacity is {glyph}10 MW',
                            'Capacity is -10 MW')
            with self.subTest(glyph=glyph):
                full(chain)
                self.assertFalse(local(chain))

    def test_ungrounded_sign_is_blocked_both_paths(self):
        for glyph in ('-', '−', '﹣', '－'):
            chain=chain_for('Capacity is 5 MW',f'Capacity is {glyph}10 MW',
                            'Capacity is 10 MW')
            with self.subTest(glyph=glyph):
                with self.assertRaises(binding.Blocked): full(chain)
                self.assertTrue(local(chain))

    def test_grounded_scale_change_passes_both_paths(self):
        chain=chain_for('투자액은 10억원이다.','투자액은 20조원이다.',
                        '투자액은 20조원이다.')
        full(chain)
        self.assertFalse(local(chain))

    def test_ungrounded_scale_change_blocks_both_paths(self):
        chain=chain_for('투자액은 10억원이다.','투자액은 20조원이다.',
                        '투자액은 20억원이다.')
        with self.assertRaises(binding.Blocked): full(chain)
        self.assertTrue(local(chain))

    def test_compound_amount_is_an_explicit_coverage_block_both_paths(self):
        for amount in ('1조 2000억원','1억2000만원','1조 2천억원'):
            chain=chain_for('투자액은 10억원이다.',f'투자액은 {amount}이다.',
                            f'투자액은 {amount}이다.')
            with self.subTest(amount=amount):
                with self.assertRaisesRegex(binding.Blocked, 'C06.QUANTITY.UNSUPPORTED'):
                    full(chain)
                self.assertIn('C06.QUANTITY.UNSUPPORTED',[x.get('rule_id') for x in local(chain)])

    def test_compound_in_unmapped_field_is_not_silently_skipped(self):
        chain=chain_for('Capacity is 10 MW','Capacity is 20 MW','Capacity is 20 MW')
        chain['0.6'][0]['sub']='투자액은 1조 2000억원이다.'
        with self.assertRaisesRegex(binding.Blocked,'C06.QUANTITY.UNSUPPORTED'): full(chain)
        self.assertIn('C06.QUANTITY.UNSUPPORTED',[x.get('rule_id') for x in local(chain)])


class StateObservationTests(unittest.TestCase):
    def observe(self,text):
        pattern=binding.DIMENSION_CANONICAL_SIGNAL_RES['changed_state']['approval']
        return atoms.state_observation(text,pattern.search(text))

    def test_korean_asserted_states_are_not_blanket_rejected(self):
        for text in ('알파는 승인했다.','알파는 승인됐다.','알파는 승인되었다.',
                     '알파는 승인을 받았다.','알파는 승인 완료.','알파는 승인한다.'):
            with self.subTest(text=text):
                self.assertEqual(self.observe(text).strength,2)
                self.assertEqual(self.observe(text).classification,'realized')

    def test_korean_negation_is_not_realized(self):
        for text in ('알파는 승인되지 않았다.','알파는 승인을 받지 못했다.',
                     '알파는 승인하지 않는다.','알파는 승인된 적 없다.',
                     '알파는 미승인 상태다.','알파는 안 승인했다.'):
            with self.subTest(text=text):
                observation=self.observe(text)
                self.assertEqual(observation.strength,0)
                self.assertEqual(observation.classification,'negated')

    def test_korean_conditions_and_future_do_not_become_realized(self):
        for text in ('알파는 승인되면 착공한다.','알파는 승인된 경우 진행한다.',
                     '알파는 승인할 예정이다.','알파는 승인될 전망이다.',
                     '알파는 승인 계획이다.','알파는 승인해야 한다.'):
            with self.subTest(text=text): self.assertEqual(self.observe(text).strength,0)

    def test_korean_possibility_is_tentative_not_realized(self):
        self.assertEqual(self.observe('알파는 승인될 수 있다.').strength,1)
        self.assertEqual(self.observe('알파는 승인 가능성이 있다.').strength,1)

    def test_unknown_korean_state_is_explicitly_unresolved(self):
        observed=self.observe('알파 승인')
        self.assertEqual(observed.strength,0)
        self.assertEqual(observed.classification,'unsupported')
        self.assertEqual(observed.reason,'korean_state_syntax_unresolved')

    def test_approval_in_progress_is_not_granted_approval(self):
        self.assertEqual(self.observe('알파는 승인 중이다.').strength,0)
        pattern=binding.DIMENSION_CANONICAL_SIGNAL_RES['changed_state']['production_operation']
        text='공장은 가동 중이다.'
        self.assertEqual(atoms.state_observation(text,pattern.search(text)).strength,2)

    def test_korean_negation_stops_at_independent_subject(self):
        pattern=binding.DIMENSION_CANONICAL_SIGNAL_RES['changed_state']['approval']
        for text,expected in (
            ('알파는 승인됐고 베타는 승인되지 않았다.',[2,0]),
            ('알파는 승인되지 않았지만 베타는 승인됐다.',[0,2]),
        ):
            with self.subTest(text=text):
                self.assertEqual([atoms.state_observation(text,m).strength for m in pattern.finditer(text)],expected)

    def test_english_preposed_and_postposed_conditions(self):
        for text in ('If Alpha is approved, demand increases.',
                     'Unless Alpha is approved, demand falls.',
                     'Alpha is approved if demand increases.',
                     'Whether Alpha was approved remains unclear.',
                     'Assuming Alpha is approved, demand increases.',
                     'Provided that Alpha is approved, demand increases.'):
            with self.subTest(text=text):
                self.assertEqual(self.observe(text).strength,0)
                self.assertEqual(self.observe(text).classification,'conditional')

    def test_condition_scope_includes_and_conjunct(self):
        text='If Alpha is approved and Beta is approved, demand increases.'
        pattern=binding.DIMENSION_CANONICAL_SIGNAL_RES['changed_state']['approval']
        self.assertEqual([atoms.state_observation(text,m).strength for m in pattern.finditer(text)],[0,0])

    def test_condition_scope_stops_at_sentence_or_independent_contrast(self):
        pattern=binding.DIMENSION_CANONICAL_SIGNAL_RES['changed_state']['approval']
        for separator in ('. ', '; ', ', but '):
            text='If Alpha is approved, demand increases'+separator+'Beta was approved.'
            with self.subTest(separator=separator):
                self.assertEqual([atoms.state_observation(text,m).strength for m in pattern.finditer(text)],[0,2])

    def test_decimal_inside_a_condition_does_not_end_its_scope(self):
        for text in ('If capacity is 1.5 MW, Alpha was approved.',
                     'If U.S. officials agreed, Alpha was approved.'):
            with self.subTest(text=text): self.assertEqual(self.observe(text).strength,0)

    def test_english_infinitive_does_not_assert_realization(self):
        for text in ('Alpha is to be approved.','Alpha needs to be approved.'):
            with self.subTest(text=text): self.assertEqual(self.observe(text).strength,0)

    def test_original_nonrealized_zero_cases_block_both_paths(self):
        for clause in ('알파는 승인되지 않았다','If Alpha is approved, demand increases'):
            text=f'Previously planned at 10 MW; {clause}; target remains subject to permit.'
            chain=chain_for(text,text,text,DENSE)
            with self.subTest(clause=clause):
                with self.assertRaises(binding.Blocked): full(chain)
                self.assertTrue(local(chain))

    def test_realized_korean_zero_case_passes_both_paths(self):
        text='Previously planned at 10 MW; 알파는 승인됐다; target remains subject to permit.'
        chain=chain_for(text,text,text,DENSE)
        full(chain)
        self.assertFalse(local(chain))

    def test_realized_claim_cannot_be_grounded_by_korean_negated_evidence(self):
        text='Previously planned at 10 MW; 알파는 승인됐다; target remains subject to permit.'
        chain=chain_for(text,text,text.replace('승인됐다','승인되지 않았다'),DENSE)
        with self.assertRaises(binding.Blocked): full(chain)
        self.assertTrue(local(chain))

    def test_changed_tentative_positive_control_stays_valid(self):
        chain=chain_for('Capacity is 10 MW; Alpha project.',
            'Capacity is 20 MW; Alpha may be delayed.',
            'Capacity is 20 MW; Alpha may be delayed.',
            ('quantitative_anchor','changed_state','boundary_or_uncertainty'))
        full(chain)
        self.assertFalse(local(chain))


class StandaloneAtomCliTests(unittest.TestCase):
    def run_cli(self, chain):
        row=copy.deepcopy(chain['0.6'][0])
        row.update(language_terminology_polished=True,
            related_lineage={'status':'PASS','relation_type':'new_unrelated_event','related_ids':[]},
            date_role={'representative_date':'2026-09-01'},source_diversity_status='PASS_MULTI_SOURCE')
        payload={'stage':'0.6','upstream_lineage_integrity':'PASS','lineage_and_anchor_guard':'PASS',
                 'content_enriched_and_language_polished':[row]}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'input.json'
            path.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
            proc=subprocess.run([sys.executable,str(ROOT/'validation_scripts/stage_artifact_contract_check.py'),
                                 '0.6',str(path)],cwd=tmp,text=True,capture_output=True,timeout=30)
        self.assertIn(proc.returncode,(0,1),proc.stderr)
        return proc,json.loads(proc.stdout)

    def test_cli_mismatched_quantities_block(self):
        for prior,current,quote in (
            ('Capacity is 5 MW','Capacity is −10 MW','Capacity is 10 MW'),
            ('투자액은 10억원이다.','투자액은 20조원이다.','투자액은 20억원이다.'),
        ):
            with self.subTest(current=current):
                proc,result=self.run_cli(chain_for(prior,current,quote))
                self.assertEqual(proc.returncode,1,proc.stderr)
                self.assertTrue(result['findings'])

    def test_cli_nonrealized_zero_delta_blocks(self):
        for clause in ('알파는 승인되지 않았다','If Alpha is approved, demand increases'):
            text=f'Previously planned at 10 MW; {clause}; target remains subject to permit.'
            with self.subTest(clause=clause):
                proc,result=self.run_cli(chain_for(text,text,text,DENSE))
                self.assertEqual(proc.returncode,1,proc.stderr)
                self.assertTrue(result['findings'])

    def test_cli_grounded_inputs_still_pass_with_limited_scope(self):
        korean='Previously planned at 10 MW; 알파는 승인됐다; target remains subject to permit.'
        for chain in (
            chain_for('Capacity is 5 MW','Capacity is −10 MW','Capacity is -10 MW'),
            chain_for('투자액은 10억원이다.','투자액은 20조원이다.','투자액은 20조원이다.'),
            chain_for(korean,korean,korean,DENSE),
        ):
            with self.subTest(current=chain['0.6'][0]['fact']):
                proc,result=self.run_cli(chain)
                self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout)
                self.assertEqual(result['status'],'PASS')
                self.assertIn('materialized_operation',result['validation_scope']['not_verified'])

    def test_cli_unparsed_amount_reports_coverage_rule(self):
        chain=chain_for('투자액은 10억원이다.','투자액은 1조 2000억원이다.','투자액은 1조 2000억원이다.')
        proc,result=self.run_cli(chain)
        self.assertEqual(proc.returncode,1,proc.stderr)
        self.assertIn('C06.QUANTITY.UNSUPPORTED',[x.get('rule_id') for x in result['findings']])


if __name__=='__main__':
    unittest.main()

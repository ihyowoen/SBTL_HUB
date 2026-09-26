"""Bounded fixes from PR385 independent review; paired synthetic controls.

Exercise the original entrypoints, not copies of their recognizers. Fixture
source flags are synthetic and do not assert that a live source was fetched.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import content_semantic_atoms as atoms
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

ROOT = Path(__file__).resolve().parents[2]
V5 = 'PROMPT_0_6_V5_20260919'
DENSE = ('prior_state', 'changed_state', 'quantitative_anchor', 'boundary_or_uncertainty')
QC = ('quantitative_anchor', 'changed_state')
PRIOR = '용량은 10 MW이다.'


def full(chain):
    row = chain['0.6'][0]
    binding.validate_content_enrichment_delta(
        chain, 'review-state-quantity', operation_card=copy.deepcopy(row),
        locked_prompt_version=V5,
    )


def observe(text, marker='approval'):
    pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES['changed_state'][marker]
    match = pattern.search(text)
    if match is None:
        raise AssertionError(f'missing {marker} marker: {text}')
    return atoms.state_observation(text, match)


def dense(clause):
    return f'Previously planned at 10 MW; {clause}; target remains subject to permit.'


class StateReviewRepairs(unittest.TestCase):
    def test_f03_common_construction_predicates_are_realized(self):
        for clause in ('공장은 착공에 들어갔다.', '공장은 착공에 돌입했다.',
                       '공장은 착공을 시작했다.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause, 'construction').strength, 2)

    def test_f03_negated_idiom_is_not_realized(self):
        for clause in ('공장은 착공에 들어가지 않았다.', '공장은 착공에 돌입하지 않았다.',
                       '공장은 착공을 시작하지 않았다.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause, 'construction').classification, 'negated')

    def test_f03_realized_idiom_cannot_hide_behind_quantity(self):
        current = '용량은 20 MW이다. 공장은 착공에 들어갔다.'
        quote = '용량은 20 MW이다. 공장은 착공에 들어가지 않았다.'
        for dimensions in (('quantitative_anchor',), QC):
            with self.subTest(dimensions=dimensions), self.assertRaises(binding.Blocked):
                full(chain_for(PRIOR, current, quote, dimensions))

    def test_f03_grounded_realized_idiom_passes_both_content_paths(self):
        text = '용량은 20 MW이다. 공장은 착공에 들어갔다.'
        chain = chain_for(PRIOR, text, text, QC)
        full(chain)
        self.assertFalse(stage._content_enrichment_audit_findings(chain['0.6'][0], 'control'))

    def test_f03_common_idiom_zero_delta_is_valid(self):
        text = '당초 10 MW로 계획됐던 공장은 착공에 들어갔다; 목표는 인증 조건부다.'
        chain = chain_for(text, text, text, DENSE)
        full(chain)
        self.assertFalse(stage._content_enrichment_audit_findings(chain['0.6'][0], 'control'))

    def test_f03_paraphrase_does_not_delete_state(self):
        current = '용량은 20 MW이다. 공장은 착공에 들어갔다.'
        full(chain_for('용량은 10 MW이다. 공장은 착공했다.', current, current))

    def test_supported_idiom_does_not_override_conditional_or_future(self):
        for clause in ('공장은 착공에 들어갈 예정이다.', '공장은 착공에 들어갔다면 투자한다.',
                       '공장은 착공에 돌입할 계획이다.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause, 'construction').strength, 0)

    def test_f09_later_whether_complement_does_not_retroactively_negate_approval(self):
        for clause in ('The regulator approved the permit and will decide whether to extend it.',
                       'The regulator approved the permit and Beta will decide whether to extend it.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause).strength, 2)

    def test_f09_zero_delta_preceding_approval_passes(self):
        text = dense('the regulator approved the permit and will decide whether to extend it')
        chain = chain_for(text, text, text, DENSE)
        full(chain)
        self.assertFalse(stage._content_enrichment_audit_findings(chain['0.6'][0], 'control'))

    def test_actual_preposed_or_postposed_conditions_still_block(self):
        for clause in ('Whether Alpha was approved remains unclear.',
                       'If Alpha is approved and Beta is approved, demand increases.',
                       'Alpha is approved if demand increases.',
                       'Alpha is approved only if the permit is extended.'):
            with self.subTest(clause=clause):
                pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES['changed_state']['approval']
                self.assertTrue(all(atoms.state_observation(clause, m).strength == 0
                                    for m in pattern.finditer(clause)))

    def test_nouns_ending_an_do_not_become_negation(self):
        for clause in ('제안 승인했다.', '방안 승인했다.', '법안 승인됐다.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause).strength, 2)
        for clause in ('알파는 안 승인했다.', '알파는 못 승인했다.', '알파는 미승인 상태다.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause).strength, 0)

    def test_f11_interruption_never_asserts_running(self):
        for clause in ('공장은 가동 중단됐다.', '공장은 가동 중지됐다.',
                       '공장은 가동중단됐다.', '공장은 가동 중단 상태다.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause, 'production_operation').strength, 0)

    def test_f11_actual_running_remains_realized(self):
        for clause in ('공장은 가동 중이다.', '공장은 가동중이다.',
                       '공장은 양산 중이다.', '공장은 가동했다.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause, 'production_operation').strength, 2)

    def test_f11_grounded_running_passes_halted_evidence_blocks(self):
        current = '용량은 20 MW이다. 공장은 가동 중이다.'
        full(chain_for(PRIOR, current, current, QC))
        for quote in (current.replace('가동 중이다', '가동 중단됐다'),
                      current.replace('가동 중이다', '가동 중지됐다')):
            with self.subTest(quote=quote):
                chain = chain_for(PRIOR, current, quote, QC)
                with self.assertRaises(binding.Blocked): full(chain)
                self.assertTrue(stage._content_enrichment_audit_findings(chain['0.6'][0], 'control'))

    def test_f11_zero_delta_cannot_use_halted_evidence_for_running(self):
        text = '당초 10 MW로 계획됐던 공장은 가동 중이다; 목표는 인증 조건부다.'
        with self.assertRaises(binding.Blocked):
            full(chain_for(text, text, text.replace('가동 중이다', '가동 중단됐다'), DENSE))

    def test_f11_halted_event_itself_remains_a_realized_change(self):
        for clause in ('공장은 가동 중단됐다.', '공장은 가동 중지됐다.'):
            with self.subTest(clause=clause):
                counts = binding._signal_counter('changed_state', clause)
                self.assertEqual(counts, {'suspension': 1})
                text = dense(clause)
                full(chain_for(text, text, text, DENSE))

    def test_f11_construction_in_progress_is_not_partial_halted_match(self):
        self.assertFalse(binding._signal_counter('changed_state', '건설 중단 예정'))
        self.assertEqual(binding._signal_counter('changed_state', '건설 중이다.'), {'construction': 1})
        self.assertEqual(binding._signal_counter('changed_state', '건설 중단됐다.'), {'suspension': 1})

    def test_f12_dated_nonpast_is_not_realized(self):
        for clause in ('공장은 2027년 양산한다.', '공장은 2027년에 양산한다.',
                       '공장은 내년 초부터 양산한다.', '향후 공장은 가동한다.',
                       '공장은 앞으로 생산시설을 가동한다.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause, 'production_operation').strength, 0)

    def test_f12_explicit_past_and_ongoing_are_not_destroyed_by_date(self):
        for clause in ('공장은 2025년 양산했다.', '공장은 2025년부터 가동 중이다.',
                       '공장은 2025년에 가동을 시작했다.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause, 'production_operation').strength, 2)

    def test_future_project_date_does_not_negate_its_already_granted_approval(self):
        for clause in ('내년 사업계획을 승인했다.', '향후 증설 계획을 승인했다.'):
            with self.subTest(clause=clause):
                self.assertEqual(observe(clause).strength, 2)
        self.assertEqual(observe('내년 납품을 위해 가동 중이다.', 'production_operation').strength, 2)

    def test_f12_future_cannot_satisfy_zero_delta_realized_gate(self):
        text = '당초 10 MW로 계획됐던 공장은 2027년 양산한다; 목표는 인증 조건부다.'
        chain = chain_for(text, text, text, DENSE)
        with self.assertRaises(binding.Blocked): full(chain)
        self.assertTrue(stage._content_enrichment_audit_findings(chain['0.6'][0], 'control'))

    def test_future_or_negation_in_later_independent_clause_preserves_first_state(self):
        clause = '알파는 승인됐고 베타는 승인할 예정이다.'
        pattern = binding.DIMENSION_CANONICAL_SIGNAL_RES['changed_state']['approval']
        self.assertEqual([atoms.state_observation(clause, m).strength for m in pattern.finditer(clause)], [2, 0])


class QuantityReviewRepairs(unittest.TestCase):
    def test_f02_bare_korean_scales_are_values_not_ignored_suffixes(self):
        for amount, expected in (('5억', '500000000'), ('5조', '5000000000000'),
                                 ('1.25만', '12500')):
            with self.subTest(amount=amount):
                observations = atoms.quantitative_observations(amount)
                self.assertEqual(len(observations), 1)
                self.assertEqual(observations[0].number, expected)
                self.assertEqual(observations[0].currency_code, '')
        self.assertNotEqual(atoms.quantitative_signals('5억'), atoms.quantitative_signals('5조'))
        self.assertNotEqual(atoms.quantitative_signals('5억'), atoms.quantitative_signals('5억원'))

    def test_f02_grounded_bare_scale_passes_ungrounded_scale_blocks(self):
        current = '용량은 20 MW이다. 투자 규모는 5조이다.'
        full(chain_for(PRIOR, current, current))
        bad = chain_for(PRIOR, current, current.replace('5조', '5억'))
        with self.assertRaises(binding.Blocked): full(bad)
        self.assertTrue(stage._content_enrichment_audit_findings(bad['0.6'][0], 'control'))

    def test_bare_scale_equivalent_notation_is_not_new_information(self):
        self.assertEqual(atoms.quantitative_signals('5억'), atoms.quantitative_signals('500000000'))
        with self.assertRaises(binding.Blocked):
            full(chain_for('투자 규모는 5억이다.', '투자 규모는 500000000이다.', '투자 규모는 500000000이다.'))

    def test_f04_unimplemented_scale_composition_is_explicit_not_partial(self):
        for amount in ('6십억원', '6십만원', '5백억원', '2천억원',
                       '1조 2000억원', '1조 2000억'):
            with self.subTest(amount=amount):
                self.assertTrue(atoms.unsupported_quantity_spans(amount))
                self.assertFalse(atoms.quantitative_signals(amount))

    def test_f04_both_paths_report_coverage_without_claiming_to_parse_compound(self):
        text = '용량은 20 MW이다. 매출은 6십억원이다.'
        chain = chain_for(PRIOR, text, text)
        with self.assertRaisesRegex(binding.Blocked, 'C06.QUANTITY.UNSUPPORTED'): full(chain)
        findings = stage._content_enrichment_audit_findings(chain['0.6'][0], 'control')
        self.assertIn('C06.QUANTITY.UNSUPPORTED', [item.get('rule_id') for item in findings])

    def test_korean_particles_cannot_erase_scale_or_hide_composition(self):
        for suffix in ('이다', '을', '를', '은', '는', '이', '가', '의', '에', '에서', '까지', '부터', '보다'):
            with self.subTest(suffix=suffix):
                self.assertNotEqual(atoms.quantitative_signals('5억'+suffix), atoms.quantitative_signals('5조'+suffix))
                self.assertTrue(atoms.unsupported_quantity_spans('1조 2000억'+suffix))
                self.assertFalse(atoms.quantitative_signals('1조 2000억'+suffix))

    def test_ordinal_article_is_not_a_trillion_amount(self):
        for text in ('제5조', '제5조의', '법 제 5조에'):
            with self.subTest(text=text):
                observed, = atoms.quantitative_observations(text)
                self.assertEqual(observed.number, '5')
                self.assertEqual(observed.unit, '조항')
                self.assertNotEqual(atoms.quantitative_signals(text), atoms.quantitative_signals('5조'))
        self.assertEqual(atoms.quantitative_observations('투자액 5조')[0].number, '5000000000000')

    def test_simple_tens_and_hundreds_are_exact(self):
        for text, value in (('6십원', '60'), ('6백원', '600')):
            with self.subTest(text=text):
                self.assertEqual(atoms.quantitative_observations(text)[0].number, value)

    def test_f13_attached_and_spaced_t_unit_match(self):
        self.assertEqual(atoms.quantitative_signals('30,000t이다.'), atoms.quantitative_signals('30,000 t이다.'))
        self.assertEqual(atoms.quantitative_observations('30,000t이다.')[0].unit, 't')
        current = '생산능력은 30,000t이다. 용량은 20 MW이다.'
        full(chain_for('생산능력은 30,000 t이다.', current, current))

    def test_units_never_match_prefix_of_english_word(self):
        for text in ('20 turbines', '20 tomatoes', '20 tpa', '20 tons'):
            with self.subTest(text=text):
                self.assertNotEqual(atoms.quantitative_observations(text)[0].unit, 't')
        self.assertEqual(atoms.quantitative_signals('20turbines'), ())

    def test_sign_currency_and_bounds_survive_bare_scale_parsing(self):
        for left, right in (('−5억', '5억'), ('>5억', '<5억'),
                            ('5억원', '5억엔'), ('20 MW', '20 MWh')):
            with self.subTest(left=left, right=right):
                self.assertNotEqual(atoms.quantitative_signals(left), atoms.quantitative_signals(right))


class RepairedStateStandaloneCli(unittest.TestCase):
    def run_cli(self, chain):
        row = copy.deepcopy(chain['0.6'][0])
        row.update(language_terminology_polished=True,
                   related_lineage={'status':'PASS','relation_type':'new_unrelated_event','related_ids':[]},
                   date_role={'representative_date':'2026-09-01'},source_diversity_status='PASS_MULTI_SOURCE')
        payload = {'stage':'0.6','upstream_lineage_integrity':'PASS','lineage_and_anchor_guard':'PASS',
                   'content_enriched_and_language_polished':[row]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'input.json'
            path.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
            proc = subprocess.run([sys.executable,str(ROOT/'validation_scripts/stage_artifact_contract_check.py'),
                                   '0.6',str(path)],cwd=tmp,capture_output=True,text=True,timeout=30)
        self.assertIn(proc.returncode,(0,1),proc.stderr)
        return proc.returncode,json.loads(proc.stdout)

    def test_f03_and_f09_cli_positive_controls(self):
        for text in (dense('공장은 착공에 들어갔다'),
                     dense('the regulator approved the permit and will decide whether to extend it')):
            with self.subTest(text=text):
                rc,payload = self.run_cli(chain_for(text,text,text,DENSE))
                self.assertEqual(rc,0,payload)
                self.assertIn('materialized_operation',payload['validation_scope']['not_verified'])

    def test_f03_and_f11_cli_opposite_evidence_blocks(self):
        for state,bad_state in (('착공에 들어갔다','착공에 들어가지 않았다'),
                                ('가동 중이다','가동 중단됐다')):
            current = f'용량은 20 MW이다. 공장은 {state}.'
            with self.subTest(state=state):
                rc,payload = self.run_cli(chain_for(PRIOR,current,current.replace(state,bad_state),QC))
                self.assertEqual(rc,1,payload)
                self.assertTrue(payload['findings'])

    def test_f02_and_f04_cli_quantity_controls(self):
        current = '용량은 20 MW이다. 투자 규모는 5조이다.'
        for quote,expected in ((current,0),(current.replace('5조','5억'),1)):
            with self.subTest(quote=quote):
                rc,payload = self.run_cli(chain_for(PRIOR,current,quote))
                self.assertEqual(rc,expected,payload)
        compound = '용량은 20 MW이다. 매출은 6십억원이다.'
        rc,payload = self.run_cli(chain_for(PRIOR,compound,compound))
        self.assertEqual(rc,1,payload)
        self.assertIn('C06.QUANTITY.UNSUPPORTED',[i.get('rule_id') for i in payload['findings']])


if __name__ == '__main__':
    unittest.main()

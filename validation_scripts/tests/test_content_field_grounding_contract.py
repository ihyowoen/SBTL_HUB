"""F05: explicit field-scoped quote reuse, never inherited-fact exemption.

Synthetic facts; exercises real bound content, standalone findings and CLI.
The same complete normalized field may reuse a quote. Merely sharing a number,
entity or state marker does not establish identical claims.
"""
import copy
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for
from validation_scripts.tests.test_evidence_preservation_authority import cli

V5 = 'PROMPT_0_6_V5_20260919'
DIMS = ('prior_state', 'changed_state', 'quantitative_anchor', 'boundary_or_uncertainty')
DENSE = ('Previously planned at 1 GWh; Beta production started at 2 GWh; '
         'target remains subject to certification.')


def source(ref, quote, fields):
    return {'source_id': ref, 'source_url': 'https://example.test/' + ref,
            'source_quote': quote, 'source_quote_status': 'body_quote_verified',
            'fetched': True, 'supports': list(fields)}


def fixture(*, scoped=True, no_change=False, duplicate=False):
    current = {'sub': 'Alpha capacity is 20 MW.', 'fact': DENSE if no_change else 'Beta output is 5 GWh.'}
    prior = dict(current, sub=current['sub'] if no_change else 'Alpha capacity is 10 MW.')
    if duplicate:
        current['fact'] = current['sub']; prior['fact'] = prior['sub']
        sources = [source('S1', current['sub'], ['sub', 'fact'])]
        field_refs = {'sub': ['S1'], 'fact': ['S1']}
    else:
        sources = [source('S1', current['sub'], ['sub']), source('S2', current['fact'], ['fact'])]
        field_refs = {'sub': ['S1'], 'fact': ['S2']}
    enabled = DIMS if no_change else ('quantitative_anchor',)
    chain = copy.deepcopy(chain_for(prior['fact'], current['fact'], current['fact'], enabled))
    for st in ('B', 'C', '0.4', '0.5', '0.6'):
        chain[st][0]['fact_sources'] = copy.deepcopy(sources)
        if st != 'B': chain[st][0].update(current if st == '0.6' else prior)
    row = chain['0.6'][0]
    row['prompt_provenance_0_6'] = {'prompt_version': V5}
    audit = row['content_enrichment_audit']
    audit.update(changed_fields=[f for f in ('sub', 'fact') if prior[f] != current[f]],
                 no_change_required=no_change, no_change_reason='All retained facts keep their verified quotes.' if no_change else '')
    for dim in enabled:
        refs = field_refs if dim == 'quantitative_anchor' else {'fact': ['S2']}
        entry = {'fields': list(refs), 'evidence_refs': sorted(set(r for values in refs.values() for r in values))}
        if scoped: entry['field_evidence_refs'] = copy.deepcopy(refs)
        audit['density_audit']['dimension_evidence'][dim] = entry
    return chain


def entry(chain, dim='quantitative_anchor'):
    return chain['0.6'][0]['content_enrichment_audit']['density_audit']['dimension_evidence'][dim]


def bound(chain, card=None):
    return binding.validate_content_enrichment_delta(chain, 'F05',
        operation_card=copy.deepcopy(chain['0.6'][0]) if card is None else card,
        locked_prompt_version=V5)


def mutate_sources(chain, fn):
    for st in ('B', 'C', '0.4', '0.5', '0.6'):
        fn(chain[st][0]['fact_sources'])


class FieldGroundingContractTests(unittest.TestCase):
    def assertBothPass(self, chain):
        bound(chain)
        self.assertEqual(stage._content_enrichment_audit_findings(chain['0.6'][0], 'F05'), [])

    def assertBothBlock(self, chain):
        with self.assertRaises(binding.Blocked): bound(chain)
        self.assertTrue(stage._content_enrichment_audit_findings(chain['0.6'][0], 'F05'))

    def test_split_field_authority_changed_copy_passes(self):
        self.assertBothPass(fixture())

    def test_split_field_authority_zero_delta_passes(self):
        self.assertBothPass(fixture(no_change=True))

    def test_legacy_cross_product_contract_is_not_silently_reinterpreted(self):
        self.assertBothBlock(fixture(scoped=False))

    def test_retained_fact_cannot_drop_its_quote_reference(self):
        c = fixture(); e = entry(c)
        e['evidence_refs'] = ['S1']; e['field_evidence_refs']['fact'] = ['S1']
        self.assertBothBlock(c)

    def test_retained_fact_cannot_rely_on_old_pass_label(self):
        c = fixture(no_change=True)
        for st in ('C', '0.4', '0.5'): c[st][0]['evidence_qc_status'] = 'PASS'
        mutate_sources(c, lambda ss: ss[1].update(source_quote=DENSE.replace('2 GWh', '')))
        self.assertBothBlock(c)

    def test_retained_source_needs_literal_quote_not_editorial_claim(self):
        c = fixture()
        mutate_sources(c, lambda ss: ss[1].update(source_quote='', claim='Beta output is 5 GWh.'))
        self.assertBothBlock(c)

    def test_retained_source_status_is_not_automatically_upgraded(self):
        c = fixture(); mutate_sources(c, lambda ss: ss[1].update(source_quote_status='body_level_evidence_verified'))
        self.assertBothBlock(c)

    def test_failed_fetch_remains_unusable(self):
        c = fixture(); mutate_sources(c, lambda ss: ss[1].update(fetched=False))
        self.assertBothBlock(c)

    def test_unrelated_quote_cannot_be_borrowed_from_other_field(self):
        c = fixture()
        mutate_sources(c, lambda ss: [s.update(supports=['sub', 'fact']) for s in ss])
        entry(c)['field_evidence_refs'] = {'sub': ['S2'], 'fact': ['S1']}
        self.assertBothBlock(c)

    def test_matching_number_with_wrong_entity_remains_blocked(self):
        c = fixture(duplicate=True)
        c['0.6'][0]['fact'] = 'Beta capacity is 20 MW.'
        for st in ('C', '0.4', '0.5'): c[st][0]['fact'] = 'Beta capacity is 10 MW.'
        self.assertBothBlock(c)

    def test_identical_complete_field_copy_reuses_quote(self):
        self.assertBothPass(fixture(duplicate=True))

    def test_presentation_equivalent_complete_field_reuses_quote(self):
        c = fixture(duplicate=True); c['0.6'][0]['sub'] = '**Alpha capacity is 20 MW.**'
        self.assertBothPass(c)

    def test_same_number_different_whole_claim_does_not_share_occurrence_budget(self):
        c = fixture(duplicate=True); c['0.6'][0]['fact'] = 'Alpha output is 20 MW.'
        for st in ('C', '0.4', '0.5'): c[st][0]['fact'] = 'Alpha output is 10 MW.'
        self.assertBothBlock(c)

    def test_same_field_repeated_occurrences_are_not_deduplicated(self):
        c = fixture(duplicate=True); c['0.6'][0]['fact'] += ' Alpha capacity is 20 MW.'
        self.assertBothBlock(c)

    def test_copying_old_field_alone_is_not_new_enrichment(self):
        c = fixture(duplicate=True)
        for st in ('C', '0.4', '0.5'):
            c[st][0]['fact'] = 'Alpha capacity is 20 MW.'
            c[st][0]['sub'] = 'Alpha capacity.'
        c['0.6'][0]['content_enrichment_audit']['changed_fields'] = ['sub']
        with self.assertRaisesRegex(binding.Blocked, 'substantive|newly|new/deepened'): bound(c)

    def test_new_false_number_cannot_hide_next_to_retained_grounded_number(self):
        c = fixture(); c['0.6'][0]['sub'] += ' Alpha storage is 900 MWh.'
        self.assertBothBlock(c)

    def test_zero_delta_one_grounded_number_is_not_enough(self):
        c = fixture(no_change=True)
        mutate_sources(c, lambda ss: ss[1].update(source_quote=DENSE.replace('2 GWh', '3 GWh')))
        self.assertBothBlock(c)

    def test_modality_not_upgraded_by_separate_field(self):
        c = fixture(no_change=True)
        mutate_sources(c, lambda ss: ss[1].update(source_quote=DENSE.replace('production started', 'production may start')))
        self.assertBothBlock(c)

    def test_field_map_must_cover_exact_mapped_fields(self):
        for field_map in ({'sub': ['S1']}, {'sub':['S1'], 'fact':['S2'], 'gate':['S1']}):
            with self.subTest(field_map=field_map):
                c = fixture(); entry(c)['field_evidence_refs'] = field_map; self.assertBothBlock(c)

    def test_malformed_field_map_fails_closed(self):
        for bad in (None, [], '', True, 42, {'sub':['S1'], 'fact':None}, {'sub':['S1'], 'fact':'S2'},
                    {'sub':['S1'], 'fact':[]}, {'sub':['S1'], 'fact':[{}]}, {'sub':['S1'], 'fact':['']}):
            with self.subTest(bad=bad):
                c = fixture(); entry(c)['field_evidence_refs'] = bad; self.assertBothBlock(c)

    def test_field_refs_union_must_equal_declared_refs(self):
        c = fixture(); entry(c)['field_evidence_refs']['fact'] = ['S1']
        self.assertBothBlock(c)

    def test_undeclared_field_ref_cannot_supply_evidence(self):
        c = fixture(); entry(c)['field_evidence_refs']['fact'] = ['S3']; self.assertBothBlock(c)

    def test_duplicate_trimmed_field_ref_is_not_extra_evidence(self):
        c = fixture(); entry(c)['field_evidence_refs']['fact'] = ['S2', ' S2 ']; self.assertBothBlock(c)

    def test_one_source_reused_across_fields_is_not_duplicate_ref_error(self):
        c = fixture(duplicate=True)
        entry(c)['field_evidence_refs']['sub'] = [' S1 ']
        self.assertBothPass(c)

    def test_id_url_alias_cannot_multiply_quotes(self):
        c = fixture(duplicate=True); e = entry(c); alias = 'https://example.test/S1'
        e['evidence_refs'].append(alias); e['field_evidence_refs']['sub'].append(alias)
        self.assertBothBlock(c)

    def test_excluded_alias_cannot_reenter_via_field_map(self):
        c = fixture()
        mutate_sources(c, lambda ss: ss[1].update(supporting_context_only_not_visible_claim_support=True))
        self.assertBothBlock(c)

    def test_field_map_does_not_widen_explicit_support(self):
        c = fixture(); entry(c)['field_evidence_refs']['fact'] = ['S1', 'S2']; self.assertBothBlock(c)

    def test_preserved_record_and_its_quote_must_survive_materialization(self):
        c = fixture(); card = copy.deepcopy(c['0.6'][0]); card['fact_sources'][1]['source_quote'] = 'Beta output is 50 GWh.'
        with self.assertRaisesRegex(binding.Blocked, 'preserve|source record'): bound(c, card)

    def test_source_loss_is_not_a_repair(self):
        c = fixture(); card = copy.deepcopy(c['0.6'][0]); card['fact_sources'].pop()
        with self.assertRaisesRegex(binding.Blocked, 'drops|preserve'): bound(c, card)

    def test_newer_invalid_evidence_cannot_fall_back_to_older_quote(self):
        c = fixture()
        c['0.5'][0]['fact_sources'][1]['source_quote'] = ''
        with self.assertRaises(binding.Blocked): bound(c)

    def test_real_standalone_cli_positive_and_negative(self):
        c = fixture(); rc, good = cli(c['0.6'][0]); self.assertEqual(rc, 0, good)
        entry(c)['field_evidence_refs']['fact'] = ['S1']
        rc, bad = cli(c['0.6'][0]); self.assertEqual(rc, 1, bad)

    def test_field_and_source_order_do_not_change_verdict(self):
        c = fixture(); entry(c)['fields'].reverse(); entry(c)['evidence_refs'].reverse()
        entry(c)['field_evidence_refs'] = dict(reversed(list(entry(c)['field_evidence_refs'].items())))
        mutate_sources(c, lambda ss: ss.reverse()); self.assertBothPass(c)

    def test_identical_dense_zero_delta_fields_reuse_all_dimensions(self):
        c = fixture(no_change=True)
        src = source('S1', DENSE, ['sub', 'fact'])
        for st in ('B', 'C', '0.4', '0.5', '0.6'):
            c[st][0]['fact_sources'] = [copy.deepcopy(src)]
            if st != 'B': c[st][0].update(sub=DENSE, fact=DENSE)
        for dim in DIMS:
            c['0.6'][0]['content_enrichment_audit']['density_audit']['dimension_evidence'][dim] = {
                'fields': ['sub', 'fact'], 'evidence_refs': ['S1'],
                'field_evidence_refs': {'sub': ['S1'], 'fact': ['S1']}}
        self.assertBothPass(c)

    def test_unmapped_destination_cannot_borrow_copy_reuse(self):
        c = fixture(duplicate=True)
        for st in ('B', 'C', '0.4', '0.5', '0.6'):
            c[st][0]['fact_sources'][0]['supports'] = ['fact']
            c[st][0]['fact_sources'].append(source('S3', 'Gamma capacity is 30 MW.', ['gate']))
            if st != 'B':
                c[st][0].update(fact='Alpha capacity is 20 MW.',
                    sub='Alpha capacity is 20 MW.' if st == '0.6' else 'Alpha capacity.',
                    gate='Gamma capacity is 30 MW.' if st == '0.6' else 'Gamma capacity is 10 MW.')
        c['0.6'][0]['content_enrichment_audit']['changed_fields'] = ['sub', 'gate']
        e = entry(c); e.update(fields=['fact','gate'], evidence_refs=['S1','S3'],
                             field_evidence_refs={'fact':['S1'], 'gate':['S3']})
        with self.assertRaisesRegex(binding.Blocked, 'does not map that field'): bound(c)

    def test_factual_addition_cannot_borrow_other_fields_quote(self):
        c = fixture()
        c['0.6'][0]['sub'] += ' Alpha uses nickel.'
        mutate_sources(c, lambda ss: ss[1].update(source_quote='Beta output is 5 GWh. Alpha uses nickel.'))
        with self.assertRaisesRegex(binding.Blocked, 'factual|predicate'): bound(c)

    def test_retraction_markup_is_not_exact_copy_identity(self):
        c = fixture(duplicate=True); c['0.6'][0]['fact'] = '~~Alpha capacity is 20 MW.~~'
        self.assertBothBlock(c)

    def test_mixed_scoped_and_legacy_dimensions_are_supported(self):
        c = fixture(no_change=True); entry(c, 'changed_state').pop('field_evidence_refs')
        self.assertBothPass(c)

    def test_normalization_does_not_mutate_input_or_refs(self):
        c = fixture(duplicate=True); entry(c)['field_evidence_refs']['fact'] = [' S1 ']
        before = copy.deepcopy(c); self.assertBothPass(c); self.assertEqual(before, c)

    def test_missing_mapped_visible_value_is_not_a_vacuous_pass(self):
        for value in (None, '', '**'):
            with self.subTest(value=value):
                c = fixture(); c['0.6'][0]['fact'] = value; self.assertBothBlock(c)

    def test_legacy_unscoped_single_field_positive_stays_valid(self):
        c = copy.deepcopy(chain_for('Capacity is 10 MW.', 'Capacity is 20 MW.', 'Capacity is 20 MW.'))
        self.assertBothPass(c)


if __name__ == '__main__': unittest.main()

"""Verified quote status never certifies editor-authored text.

Synthetic fixtures exercise the real helper, bound content gate and standalone
CLI. Package preservation remains stricter than semantic grounding: editorial
metadata is retained/bound but contributes no facts to a verified quote.
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validation_scripts import card_run_v4_binding_hardening as binding
from validation_scripts import stage_artifact_contract_check as stage
from validation_scripts.tests.test_review_5265937741_contracts import chain_for

ROOT = Path(__file__).resolve().parents[2]
V5 = 'PROMPT_0_6_V5_20260919'
# Independent expected contract, not a copy of the implementation's key set.
QUOTE_KEYS = ('source_quote', 'quote', 'source_excerpt', 'excerpt')
EDITOR_KEYS = ('claim', 'source_claim', 'claim_text', 'visible_claim', 'evidence_text')
QUOTE = 'Capacity is 2 MW.'
FORGED = 'Capacity is 5 MW.'


def source(**extra):
    return {'source_id': 'SRC1', 'source_url': 'https://example.test/source',
            'source_quote': QUOTE, 'source_quote_status': 'body_quote_verified',
            'fetched': True, **extra}


def chain_with_source(src, current=FORGED, *, prior='Capacity is 1 MW.',
                      dimensions=('quantitative_anchor',)):
    chain = copy.deepcopy(chain_for(prior, current, QUOTE, dimensions))
    for name in ('B', 'C', '0.4', '0.5', '0.6'):
        chain[name][0]['fact_sources'] = [copy.deepcopy(src)]
    chain['0.6'][0]['prompt_provenance_0_6'] = {'prompt_version': V5}
    return chain


def bound_gate(chain, operation=None):
    binding.validate_content_enrichment_delta(
        chain, 'quote-trust-test', locked_prompt_version=V5,
        operation_card=copy.deepcopy(chain['0.6'][0]) if operation is None else operation,
    )


class QuoteTrustBoundaryTests(unittest.TestCase):
    def test_editor_aliases_never_add_grounding_text(self):
        for key in EDITOR_KEYS:
            for value in (FORGED, [FORGED]):
                with self.subTest(key=key, value=value):
                    src = source(**{key: value})
                    self.assertEqual(binding._source_evidence_texts(src), [QUOTE])
                    self.assertEqual(binding._package_texts(binding._source_evidence_package(src)), [QUOTE])

    def test_editor_only_cannot_become_usable_by_quote_status(self):
        for key in EDITOR_KEYS:
            with self.subTest(key=key):
                src = source(**{key: FORGED}); src.pop('source_quote')
                self.assertFalse(binding._source_evidence_is_usable(src))
                self.assertEqual(binding._source_evidence_texts(src), [])
                self.assertEqual(binding._source_evidence_package(src), {})

    def test_each_literal_quote_alias_still_grounds(self):
        for key in QUOTE_KEYS:
            for value in (QUOTE, ['  ' + QUOTE + '  ', QUOTE]):
                with self.subTest(key=key, value=value):
                    src = source(claim=FORGED); src.pop('source_quote'); src[key] = value
                    self.assertTrue(binding._source_evidence_is_usable(src))
                    self.assertEqual(binding._source_evidence_texts(src), [QUOTE])
                    bound_gate(chain_with_source(src, QUOTE))

    def test_approved_quote_statuses_do_not_change_the_text_boundary(self):
        for status in ('body_quote_verified', 'official_material_quote_verified', 'document_quote_verified'):
            with self.subTest(status=status):
                src = source(source_quote_status=status, claim=FORGED)
                self.assertEqual(binding._source_evidence_texts(src), [QUOTE])
                bound_gate(chain_with_source(src, QUOTE))
                with self.assertRaises(binding.Blocked):
                    bound_gate(chain_with_source(src))

    def test_claim_status_cannot_certify_editor_text_or_erase_good_quote(self):
        for status in ('unverified', 'verified', 'body_quote_verified'):
            with self.subTest(status=status):
                src = source(claim=FORGED, claim_status=status)
                self.assertEqual(binding._source_evidence_texts(src), [QUOTE])
                bound_gate(chain_with_source(src, QUOTE))
                with self.assertRaises(binding.Blocked):
                    bound_gate(chain_with_source(src))

    def test_editor_metadata_is_preserved_in_binding_package(self):
        src = source(**{key: [FORGED] for key in EDITOR_KEYS}, claim_status='unverified')
        before = copy.deepcopy(src)
        package = binding._source_evidence_package(src)
        for key in (*EDITOR_KEYS, 'claim_status'):
            self.assertEqual(package[key], src[key])
        self.assertEqual(src, before)
        package['claim'].append('mutated detached copy')
        self.assertEqual(src, before)

    def test_materialized_editor_metadata_tampering_still_blocks(self):
        for key in EDITOR_KEYS:
            with self.subTest(key=key):
                chain = chain_with_source(source(**{key: FORGED}), QUOTE)
                bound_gate(chain)
                operation = copy.deepcopy(chain['0.6'][0])
                operation['fact_sources'][0][key] = 'Changed editorial metadata.'
                with self.assertRaises(binding.Blocked):
                    bound_gate(chain, operation)

    def test_bound_and_local_gates_reject_quantity_laundering_for_every_alias(self):
        for key in EDITOR_KEYS:
            with self.subTest(key=key):
                chain = chain_with_source(source(**{key: FORGED}))
                with self.assertRaises(binding.Blocked):
                    bound_gate(chain)
                self.assertTrue(stage._content_enrichment_audit_findings(chain['0.6'][0], 'quote-trust-test'))

    def test_bound_and_local_gates_keep_valid_copy_with_editor_metadata(self):
        src = source(**{key: FORGED for key in EDITOR_KEYS})
        chain = chain_with_source(src, QUOTE)
        bound_gate(chain)
        self.assertFalse(stage._content_enrichment_audit_findings(chain['0.6'][0], 'quote-trust-test'))

    def test_editor_text_does_not_promote_a_planned_state_to_realized(self):
        quote = 'Alpha may be delayed. Capacity is 2 MW.'
        forged = 'Alpha is delayed. Capacity is 2 MW.'
        for key in EDITOR_KEYS:
            with self.subTest(key=key):
                src = source(source_quote=quote, **{key: forged})
                chain = chain_with_source(src, forged, prior='Alpha may be delayed. Capacity is 1 MW.',
                                          dimensions=('quantitative_anchor', 'changed_state'))
                with self.assertRaises(binding.Blocked):
                    bound_gate(chain)
                self.assertTrue(stage._content_enrichment_audit_findings(chain['0.6'][0], 'quote-trust-test'))

    def test_nearer_editor_only_package_does_not_backfill_from_older_quote(self):
        chain = chain_with_source(source(source_quote=FORGED))
        near = source(claim=FORGED); near.pop('source_quote')
        chain['0.5'][0]['fact_sources'] = [copy.deepcopy(near)]
        chain['0.6'][0]['fact_sources'] = [copy.deepcopy(near)]
        with self.assertRaises(binding.Blocked):
            bound_gate(chain)

    def test_discovery_ledger_uses_the_same_quote_only_rule(self):
        src = source(claim=FORGED, outcome='accepted_visible_evidence', supports=['fact'])
        chain = chain_with_source(src)
        for name in ('B', 'C', '0.4', '0.5', '0.6'):
            row = chain[name][0]
            row['source_discovery_ledger'] = row.pop('fact_sources')
        self.assertEqual(binding._row_evidence_token_texts(chain['0.5'][0])['SRC1'], [QUOTE])
        with self.assertRaises(binding.Blocked):
            bound_gate(chain)
        self.assertTrue(stage._content_enrichment_audit_findings(chain['0.6'][0], 'quote-trust-test'))
        chain['0.6'][0]['fact'] = QUOTE
        bound_gate(chain)

    def test_existing_fetch_and_quote_failure_guards_remain(self):
        for extra in ({'fetched': False}, {'fetched': 'true'}, {'fetch_status': 'blocked'},
                      {'resolved_article_matches_quote': False}, {'headline_only': True},
                      {'rss_or_snippet_only': True}, {'source_quote_status': 'unverified'},
                      {'quote_status': 'document_quote_verified'}):
            with self.subTest(extra=extra):
                self.assertFalse(binding._source_evidence_is_usable(source(claim=FORGED, **extra)))

    def test_unusable_quote_values_are_not_repaired_by_editor_text(self):
        for value in (None, '', [], 5, {'text': QUOTE}):
            with self.subTest(value=value):
                self.assertFalse(binding._source_evidence_is_usable(source(source_quote=value, claim=FORGED)))

    def test_full_gate_keeps_explicit_historical_v4_behavior(self):
        chain = chain_with_source(source(claim=FORGED))
        chain['0.6'][0]['prompt_provenance_0_6']['prompt_version'] = 'PROMPT_0_6_V4_20260901'
        binding.validate_content_enrichment_delta(chain, 'historical-v4',
            operation_card=copy.deepcopy(chain['0.6'][0]), locked_prompt_version='PROMPT_0_6_V4_20260901')

    def test_real_standalone_cli_rejects_forged_and_accepts_grounded_copy(self):
        for key in EDITOR_KEYS:
            for text, rc in ((FORGED, 1), (QUOTE, 0)):
                with self.subTest(key=key, text=text):
                    chain = chain_with_source(source(**{key: FORGED}), text)
                    row = copy.deepcopy(chain['0.6'][0]); row.update(
                        language_terminology_polished=True,
                        related_lineage={'status': 'PASS', 'relation_type': 'new_unrelated_event', 'related_ids': []},
                        date_role={'representative_date': '2026-09-01'}, source_diversity_status='PASS_MULTI_SOURCE')
                    payload = {'stage': '0.6', 'upstream_lineage_integrity': 'PASS',
                               'lineage_and_anchor_guard': 'PASS', 'content_enriched_and_language_polished': [row]}
                    with tempfile.TemporaryDirectory() as tmp:
                        path = Path(tmp) / 'stage-0-6.json'; path.write_text(json.dumps(payload), encoding='utf-8')
                        proc = subprocess.run([sys.executable, str(ROOT/'validation_scripts/stage_artifact_contract_check.py'),
                                               '0.6', str(path)], cwd=tmp, text=True, capture_output=True, timeout=30)
                    result = json.loads(proc.stdout)
                    self.assertEqual(proc.returncode, rc, proc.stderr + proc.stdout)
                    self.assertEqual(result['status'], 'PASS' if rc == 0 else 'BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT')
                    if rc:
                        self.assertIn('C06.GROUNDING.OCCURRENCES', [f.get('rule_id') for f in result['findings']])


if __name__ == '__main__':
    unittest.main()

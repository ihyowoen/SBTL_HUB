import base64
import gzip
import io
import json
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path

from validation_scripts.stage_lineage_contract_check import check_stage_a_full

PAYLOAD = ''.join(
    Path(f'.diagnostics/early16_payload_{i}.txt').read_text().strip()
    for i in range(8)
)

REPAIRS = {
    'STD26_A_001': {
        'next_confirmation_points': [{
            'measurable_event_or_metric': 'Section 232 polysilicon proclamation effective date and final covered-HTS tariff schedule publication',
            'interpretation_effect': 'The published schedule would confirm or invalidate the U.S. polysilicon market-access and supply-chain impact thesis.'
        }],
    },
    'STD26_A_009': {
        'next_confirmation_points': [{
            'measurable_event_or_metric': 'GM-Samsung SDI Indiana JV transaction closing date and transferred 49.99% ownership status',
            'interpretation_effect': 'Transaction closing would confirm or invalidate the GM-Samsung SDI strategic-control and Indiana asset-use thesis.'
        }],
    },
    'STD26_A_010': {
        'evidence_needed_for_stage_b': [{
            'source_or_document_class': 'official EIA Short-Term Energy Outlook dataset',
            'exact_claim_or_metric': 'EIA 2026 U.S. electricity-demand billion-kWh forecast, EIA 2027 billion-kWh forecast, and stated AI/data-center load contribution'
        }],
        'next_confirmation_points': [{
            'measurable_event_or_metric': 'EIA next STEO U.S. electricity-demand billion-kWh forecast and published data-center load billion-kWh estimate',
            'interpretation_effect': 'The EIA update would confirm or invalidate the sustained U.S. record-demand and storage-demand thesis.'
        }],
    },
    'STD26_A_013': {
        'evidence_needed_for_stage_b': [{
            'source_or_document_class': 'SNE Research official statistics dataset',
            'exact_claim_or_metric': 'SNE H1 2026 non-China EV battery usage 269.0 GWh, 26.3% year-on-year growth, and Korean-three supplier-share percentage'
        }],
        'next_confirmation_points': [{
            'measurable_event_or_metric': 'SNE H2 2026 non-China EV battery usage GWh and Korean-three supplier-share percentage',
            'interpretation_effect': 'The SNE update would confirm or invalidate the non-China EV battery market-growth and supplier-share-shift thesis.'
        }],
    },
    'STD26_A_016': {
        'next_confirmation_points': [{
            'measurable_event_or_metric': 'Salares Altoandinos Chinese antitrust clearance date or formally revised binding project-milestone date',
            'interpretation_effect': 'Clearance or a revised milestone would confirm or invalidate the Salares Altoandinos project-timing and execution-probability thesis.'
        }],
    },
    'STD26_A_017': {
        'evidence_needed_for_stage_b': [{
            'source_or_document_class': 'official government demonstration-program notice or project document',
            'exact_claim_or_metric': 'KREST-Lobos 2026 humanoid hot-swap demonstration award status, field-test start date, test duration, robot count, and battery-swap cycle target'
        }],
    },
    'STD26_A_018': {
        'next_confirmation_points': [{
            'measurable_event_or_metric': 'Bikaner phase-2 800 MWh commissioning date, utilization percentage, or contracted-delivery performance percentage',
            'interpretation_effect': 'The measured result would confirm or invalidate the Bikaner BESS scale-up and operating-performance thesis.'
        }],
    },
    'STD26_A_021': {
        'next_confirmation_points': [{
            'measurable_event_or_metric': 'DR Congo export-ban customs-enforcement start date, exemption status, or monthly copper/cobalt concentrate export-volume tonnes',
            'interpretation_effect': 'The enforcement data would confirm or invalidate the DR Congo domestic-processing and trade-shift thesis.'
        }],
    },
    'STD26_A_022': {
        'next_confirmation_points': [{
            'measurable_event_or_metric': 'Korea Zinc next-quarter segment-margin percentage, sales volume, and operating-profit bridge',
            'interpretation_effect': 'The filing would confirm or invalidate the Korea Zinc profitability-persistence thesis.'
        }],
    },
    'STD26_A_023': {
        'next_confirmation_points': [{
            'measurable_event_or_metric': 'Albemarle next-quarter realized lithium price, sales volume, and Energy Storage EBITDA-margin percentage',
            'interpretation_effect': 'The earnings update would confirm or invalidate the Albemarle lithium-recovery and earnings-persistence thesis.'
        }],
    },
}


def repair(data):
    repaired = deepcopy(data)
    strict_by_story = {}
    for item in repaired['strict_passed_spec']:
        spec_id = item.get('spec_id')
        patch = REPAIRS.get(spec_id)
        if patch:
            for field, value in patch.items():
                item[field] = deepcopy(value)
        for story_id in item.get('source_story_ids', []):
            strict_by_story[story_id] = item

    # PR258 full-artifact validation requires the decision ledger to mirror
    # the emitted strict V3 package exactly for every source-story row.
    for row in repaired['decision_ledger']:
        spec = strict_by_story.get(row.get('story_id'))
        if not spec:
            continue
        row['evidence_needed_for_stage_b'] = deepcopy(spec.get('evidence_needed_for_stage_b'))
        row['next_confirmation_points'] = deepcopy(spec.get('next_confirmation_points'))
    return repaired


class Early16CurrentContractDiagnostic(unittest.TestCase):
    def test_early16_current_contract(self):
        original = json.loads(gzip.decompress(base64.b64decode(PAYLOAD)))
        data = repair(original)
        out = io.StringIO()
        with redirect_stdout(out):
            rc = check_stage_a_full(data)
        self.assertEqual(rc, 0, out.getvalue())
        self.assertEqual(len(data['strict_passed_spec']), 16)
        self.assertEqual(len(data['decision_ledger']), 25)
        self.assertEqual(
            [x['spec_id'] for x in data['strict_passed_spec']],
            [x['spec_id'] for x in original['strict_passed_spec']],
        )
        # Only evidence/confirmation target semantics may change in strict rows.
        allowed = {'evidence_needed_for_stage_b', 'next_confirmation_points'}
        for before, after in zip(original['strict_passed_spec'], data['strict_passed_spec']):
            changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
            self.assertTrue(changed <= allowed, (before.get('spec_id'), changed))
        Path('early16_repaired_current_main.json').write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print('RESULT: PASS_EARLY16_CURRENT_MAIN_REPAIRED')


if __name__ == '__main__':
    unittest.main()

import base64
import gzip
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts.stage_lineage_contract_check import check_stage_a_full

PAYLOAD = ''.join(
    Path(f'.diagnostics/early16_payload_{i}.txt').read_text().strip()
    for i in range(8)
)

FAILED_IDS = {
    'STD26_A_001','STD26_A_009','STD26_A_010','STD26_A_013','STD26_A_016',
    'STD26_A_017','STD26_A_018','STD26_A_021','STD26_A_022','STD26_A_023'
}


class Early16CurrentContractDiagnostic(unittest.TestCase):
    def test_early16_current_contract(self):
        data = json.loads(gzip.decompress(base64.b64decode(PAYLOAD)))
        print('EARLY16_TARGET_FIELDS_BEGIN')
        for item in data['strict_passed_spec']:
            if item.get('spec_id') in FAILED_IDS:
                print(json.dumps({
                    'spec_id': item.get('spec_id'),
                    'headline': item.get('headline'),
                    'route': 'v3_non_execution' if item.get('structural_value_override_applied') else 'execution',
                    'execution_anchor_type': item.get('execution_anchor_type'),
                    'anchor_classes': item.get('anchor_classes'),
                    'evidence_needed_for_stage_b': item.get('evidence_needed_for_stage_b'),
                    'next_confirmation_points': item.get('next_confirmation_points'),
                    'changed_judgment': item.get('changed_judgment'),
                    'remaining_uncertainty': item.get('remaining_uncertainty'),
                }, ensure_ascii=False, sort_keys=True))
        print('EARLY16_TARGET_FIELDS_END')
        out = io.StringIO()
        with redirect_stdout(out):
            rc = check_stage_a_full(data)
        self.assertEqual(rc, 0, out.getvalue())
        self.assertEqual(len(data['strict_passed_spec']), 16)
        self.assertEqual(len(data['decision_ledger']), 25)


if __name__ == '__main__':
    unittest.main()

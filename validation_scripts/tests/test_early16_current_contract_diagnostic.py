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


class Early16CurrentContractDiagnostic(unittest.TestCase):
    def test_early16_current_contract(self):
        data = json.loads(gzip.decompress(base64.b64decode(PAYLOAD)))
        out = io.StringIO()
        with redirect_stdout(out):
            rc = check_stage_a_full(data)
        self.assertEqual(rc, 0, out.getvalue())
        self.assertEqual(len(data["strict_passed_spec"]), 16)
        self.assertEqual(len(data["decision_ledger"]), 25)


if __name__ == "__main__":
    unittest.main()

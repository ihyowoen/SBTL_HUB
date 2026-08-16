from __future__ import annotations

import base64
import gzip
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage


class NinthBatchCurrentMainDiagnostic(unittest.TestCase):
    def test_ninth_batch_candidate_current_main(self):
        repo_root = Path(__file__).resolve().parents[2]
        parts = [
            repo_root / f".diagnostics/ninth_batch_repaired_{i}.txt"
            for i in range(7)
        ]
        payload = "".join(p.read_text() for p in parts)
        artifact = json.loads(gzip.decompress(base64.b64decode(payload)).decode("utf-8"))
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a_full(artifact)
        output = stream.getvalue()
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()

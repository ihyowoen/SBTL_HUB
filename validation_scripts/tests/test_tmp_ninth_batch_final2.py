from __future__ import annotations

import base64
import gzip
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_tmp_prompt_digest_diagnostic import repair
from validation_scripts.tests.test_tmp_ninth_batch_final import post_adjust


class NinthBatchFinal2CurrentMainDiagnostic(unittest.TestCase):
    def test_ninth_batch_final2_current_main(self):
        repo_root = Path(__file__).resolve().parents[2]
        parts = [
            repo_root / ".diagnostics/ninth_batch_payload_0.txt",
            repo_root / ".diagnostics/ninth_batch_payload_1.txt",
            repo_root / ".diagnostics/ninth_batch_payload_2.txt",
            repo_root / ".diagnostics/ninth_batch_payload_3a.txt",
            repo_root / ".diagnostics/ninth_batch_payload_3b.txt",
            repo_root / ".diagnostics/ninth_batch_payload_4.txt",
        ]
        payload = "".join(path.read_text() for path in parts)
        artifact = json.loads(gzip.decompress(base64.b64decode(payload)).decode("utf-8"))
        artifact = post_adjust(repair(artifact))
        artifact["summary"]["high_value_review_pool_ids"] = []
        artifact["summary"]["follow_up_candidate_ids"] = [
            "STD26_REVIEW_027",
            "STD26_REVIEW_028",
            "STD26_REVIEW_029",
            "STD26_REVIEW_030",
            "STD26_REVIEW_031",
        ]
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a_full(artifact)
        output = stream.getvalue()
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()

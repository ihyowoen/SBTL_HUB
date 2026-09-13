import hashlib
from pathlib import Path
import unittest


class TmpPr371StageBShaProbe(unittest.TestCase):
    def test_emit_corrected_stage_b_sha256(self):
        root = Path(__file__).resolve().parents[2]
        path = root / "runs/2026-09-10/sep9-r1-current-main-production-r1/stages/stage-b.json"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.fail(f"PR371_CORRECTED_STAGE_B_SHA256={digest}")


if __name__ == "__main__":
    unittest.main()

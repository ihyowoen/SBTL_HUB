import json
from pathlib import Path
import unittest


class TmpPr374CanonicalProbe(unittest.TestCase):
    def test_emit_bounded_current_fields(self):
        root = Path(__file__).resolve().parents[2]
        doc = json.loads((root / "data/cards.full.json").read_text(encoding="utf-8-sig"))
        wanted = {
            "STD26_0909_A_004",
            "STD26_0909_A_007",
            "STD26_0909_A_012",
        }
        fields = [
            "id", "source_spec_id", "fact_sources", "date_role", "claim_map",
            "source_discovery_ledger", "source_diversity_status", "source_diversity_measure",
            "source_diversity_roles", "source_synthesis_applied", "source_synthesis_fields",
            "source_synthesis_audit", "single_source_exception", "stage_b_lineage"
        ]
        out = {}
        for card in doc["cards"]:
            spec = card.get("source_spec_id")
            if spec in wanted:
                out[spec] = {key: card.get(key, "__MISSING__") for key in fields}
        self.assertEqual(set(out), wanted)
        self.fail("PR374_CANONICAL_PROBE=" + json.dumps(out, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()

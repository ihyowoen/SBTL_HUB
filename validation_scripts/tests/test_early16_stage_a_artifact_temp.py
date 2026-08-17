import base64
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_COMMIT = "4a83213501925ffdd4b5e0107aa091e4d2e26d66"
BASE_SHA = "fe6154824fa99a09755e4c2b3efe342abaa4043438adf2a91d3853e0d55a1cca"
EXPECTED_SHA = "a452997389108de6c081faf59d45964c4a9d0b31f47f91322e0a0aa4b09bb338"
REPAIRS = {
    "STD26_A_001": (
        "Official presidential proclamation or tariff notice confirming the polysilicon tariff scope, the 120-day effective stage/date, and covered derivatives",
        "Publication of the final tariff schedule with covered HTS lines and the effective date would confirm or weaken the market-access and supply-chain impact interpretation",
    ),
    "STD26_A_009": (
        "Official transaction filing or GM/Samsung SDI company notice confirming the GM 49.99% JV stake-transfer or termination status, Indiana asset transaction stage, and transaction date",
        "Publication of the transaction closing or official ownership-transfer filing with the closing date and post-JV production plan would confirm or weaken the strategic-control and asset-use interpretation",
    ),
    "STD26_A_010": (
        "Official EIA dataset or Short-Term Energy Outlook confirming the 2026 and 2027 U.S. electricity-demand forecasts and the quantified contribution attributed to AI/data-center load",
        "Publication of the next EIA Short-Term Energy Outlook with updated 2026 and 2027 demand forecasts and a quantified data-center load estimate would confirm or weaken the sustained record-demand and storage-demand thesis",
    ),
    "STD26_A_013": (
        "SNE Research source dataset or release confirming H1 2026 non-China EV battery usage of 269.0GWh, 26.3% year-on-year growth, and the reported Korean-three supplier share",
        "Publication of H2 or the next monthly non-China EV battery usage in GWh and supplier-share percentages would confirm or weaken the market-growth and share-shift interpretation",
    ),
    "STD26_A_016": (
        "Official ENAMI/Rio Tinto transaction update or competent antitrust-authority decision confirming the Chinese antitrust review status, clearance date, or revised transaction/project schedule for Salares Altoandinos",
        "Publication of formal antitrust clearance with the clearance date or a revised binding project milestone would confirm or weaken the project-timing and execution-probability impact",
    ),
    "STD26_A_017": (
        "Official government demonstration-program notice or project document confirming the 2026 humanoid hot-swap battery demonstration selection, test period, test scale, and stated objective",
        "Publication of field-test completion results with cycle or reliability metrics or a quantified fleet-adoption count would confirm or weaken the technology-commercialization interpretation",
    ),
    "STD26_A_018": (
        "Official company commissioning notice or project document confirming the Bikaner phase-1 50MW/200MWh commissioning date and operating stage",
        "Commissioning of the 800MWh phase 2 with an operating date, utilization metric, or contracted-delivery performance metric would confirm or weaken the scale-up and operating-performance interpretation",
    ),
    "STD26_A_021": (
        "Official ministerial order or customs notice confirming the copper/cobalt concentrate export-ban adoption and effective date, covered products, and enforcement stage",
        "Publication of customs enforcement data, official exemption status, or post-rule concentrate export volumes would confirm or weaken the domestic-processing and trade-shift interpretation",
    ),
    "STD26_A_022": (
        "Official Korea Zinc earnings release, filing, or IR material confirming H1 2026 sales and operating profit, Q2 sales and operating profit, and the segment drivers of the record result",
        "Publication of the next quarterly filing or earnings-call data with segment margin, volume, and an earnings bridge would confirm or weaken the persistence of the profitability improvement",
    ),
    "STD26_A_023": (
        "Official Albemarle Q2 earnings release, filing, or investor material confirming Q2 2026 net income, realized lithium selling-price change, sales-volume change, and the segment margin or cash-flow bridge",
        "Publication of the next quarterly realized lithium price, sales volume, and segment EBITDA or margin would confirm or weaken the lithium-recovery and earnings-persistence interpretation",
    ),
}


def load_exact_base():
    encoded_parts = []
    for i in range(1, 5):
        url = (
            "https://raw.githubusercontent.com/ihyowoen/SBTL_HUB/"
            f"{BASE_COMMIT}/validation_scripts/tests/fixtures/early16_stage_a_target.b64.{i:03d}"
        )
        with urllib.request.urlopen(url, timeout=30) as response:
            encoded_parts.append(response.read().decode("utf-8").strip())
    raw = gzip.decompress(base64.b64decode("".join(encoded_parts)))
    if hashlib.sha256(raw).hexdigest() != BASE_SHA:
        raise AssertionError("historical exact base SHA mismatch")
    return json.loads(raw.decode("utf-8"))


class TestEarly16StageAArtifact(unittest.TestCase):
    def test_current_main_stage_lineage_validator(self):
        payload = load_exact_base()
        touched = set()
        for spec in payload["strict_passed_spec"]:
            spec_id = spec.get("spec_id")
            if spec_id in REPAIRS:
                evidence, confirmation = REPAIRS[spec_id]
                spec["evidence_needed_for_stage_b"] = [evidence]
                spec["next_confirmation_points"] = [confirmation]
                touched.add(spec_id)
        self.assertEqual(touched, set(REPAIRS))
        raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fh:
            fh.write(raw)
            target = Path(fh.name)
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    "validation_scripts/stage_lineage_contract_check.py",
                    "stage_a",
                    str(target),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + "\n" + proc.stderr)
            self.assertIn("RESULT: PASS_STAGE_A_SCHEMA_CONTRACT", proc.stdout)
        finally:
            target.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

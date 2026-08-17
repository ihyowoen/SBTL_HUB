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
R2_SHA = "a452997389108de6c081faf59d45964c4a9d0b31f47f91322e0a0aa4b09bb338"
R3_SHA = "b0052769450b275fca4989ee1d1d93fe9fb6615b16da33fc99b54c07834573a8"
R4_SHA = "0840494aa4f7e1f7101f882c3a6379d887524920825d5d01705ec97a2b9fe66d"
EXPECTED_SHA = "6aecf3e72234fbcbc27d3f3ab0758f9ade52bd3ed7587230483bd3de6f3eea91"

R2_REPAIRS = {
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

R3_REPAIRS = {
    "STD26_A_001": {
        "evidence": {"source_or_document_class": "Official presidential tariff notice", "exact_claim_or_metric": "Polysilicon final tariff schedule effective date and covered HTS lines"},
        "confirmation": {"measurable_event_or_metric": "Polysilicon final tariff schedule effective date and covered HTS lines", "interpretation_effect": "This result would strengthen the market-access interpretation"},
    },
    "STD26_A_009": {
        "evidence": {"source_or_document_class": "Official transaction filing or company notice", "exact_claim_or_metric": "GM Samsung SDI Indiana JV stake-transfer status and transaction closing date"},
        "confirmation": {"measurable_event_or_metric": "GM Samsung SDI Indiana JV transaction closing date and ownership transfer", "interpretation_effect": "This result would strengthen the strategic-control assessment"},
    },
    "STD26_A_010": {
        "evidence": {"source_or_document_class": "Official EIA dataset", "exact_claim_or_metric": "EIA 2026 and 2027 U.S. electricity demand volume forecast"},
        "confirmation": {"measurable_event_or_metric": "EIA 2026 and 2027 U.S. electricity demand volume", "interpretation_effect": "This result would strengthen the record-demand thesis"},
    },
    "STD26_A_013": {
        "evidence": {"source_or_document_class": "SNE Research dataset", "exact_claim_or_metric": "SNE H1 2026 non-China EV battery volume 269.0GWh and supplier share"},
        "confirmation": {"measurable_event_or_metric": "SNE non-China EV battery volume and supplier share", "interpretation_effect": "This result would strengthen the market-growth thesis"},
    },
    "STD26_A_016": {
        "evidence": {"source_or_document_class": "Official antitrust authority decision or transaction document", "exact_claim_or_metric": "Salares Altoandinos antitrust approval date and revised project schedule"},
        "confirmation": {"measurable_event_or_metric": "Salares Altoandinos antitrust approval date", "interpretation_effect": "This result would strengthen the project-timing assessment"},
    },
    "STD26_A_017": {
        "evidence": {"source_or_document_class": "Official demonstration program document", "exact_claim_or_metric": "KREST Lobros 2026 humanoid hot-swap field-test stage and test period"},
        "confirmation": {"measurable_event_or_metric": "KREST Lobros field-test cycle reliability metric", "interpretation_effect": "This result would strengthen the technology-commercialization interpretation"},
    },
    "STD26_A_018": {
        "evidence": {"source_or_document_class": "Official company commissioning notice or project document", "exact_claim_or_metric": "Bikaner phase-1 50MW/200MWh commissioning date and operating stage"},
        "confirmation": {"measurable_event_or_metric": "Bikaner phase-2 800MWh commissioning date and utilization", "interpretation_effect": "This result would strengthen the scale-up assessment"},
    },
    "STD26_A_021": {
        "evidence": {"source_or_document_class": "Official ministerial order or customs notice", "exact_claim_or_metric": "DR Congo copper cobalt concentrate export-ban effective date and enforcement stage"},
        "confirmation": {"measurable_event_or_metric": "DR Congo post-rule concentrate export volume", "interpretation_effect": "This result would strengthen the domestic-processing interpretation"},
    },
    "STD26_A_022": {
        "evidence": {"source_or_document_class": "Official Korea Zinc earnings release or filing", "exact_claim_or_metric": "Korea Zinc H1 2026 sales and operating profit and Q2 segment margin"},
        "confirmation": {"measurable_event_or_metric": "Korea Zinc next-quarter segment margin and sales volume", "interpretation_effect": "This result would strengthen the profitability outlook"},
    },
    "STD26_A_023": {
        "evidence": {"source_or_document_class": "Official Albemarle earnings release or filing", "exact_claim_or_metric": "Albemarle Q2 2026 net income lithium price sales volume and segment margin"},
        "confirmation": {"measurable_event_or_metric": "Albemarle next-quarter lithium price sales volume and segment margin", "interpretation_effect": "This result would strengthen the earnings-recovery thesis"},
    },
}


def gh_error(title, message):
    safe = str(message).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::error title={title}::{safe}", flush=True)


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
    actual = hashlib.sha256(raw).hexdigest()
    if actual != BASE_SHA:
        raise AssertionError(f"historical exact base SHA mismatch: {actual}")
    return json.loads(raw.decode("utf-8"))


def serialized(payload):
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


class TestEarly16StageAArtifact(unittest.TestCase):
    def test_current_main_stage_lineage_validator(self):
        target = None
        try:
            payload = load_exact_base()
            touched = set()
            for spec in payload["strict_passed_spec"]:
                spec_id = spec.get("spec_id")
                if spec_id in R2_REPAIRS:
                    evidence, confirmation = R2_REPAIRS[spec_id]
                    spec["evidence_needed_for_stage_b"] = [evidence]
                    spec["next_confirmation_points"] = [confirmation]
                    touched.add(spec_id)
            self.assertEqual(touched, set(R2_REPAIRS))
            self.assertEqual(hashlib.sha256(serialized(payload)).hexdigest(), R2_SHA)

            for spec in payload["strict_passed_spec"]:
                spec_id = spec.get("spec_id")
                if spec_id in R3_REPAIRS:
                    spec["evidence_needed_for_stage_b"] = [R3_REPAIRS[spec_id]["evidence"]]
                    spec["next_confirmation_points"] = [R3_REPAIRS[spec_id]["confirmation"]]

            for row in payload.get("decision_ledger", []):
                spec_id = row.get("spec_id")
                if spec_id in R3_REPAIRS:
                    row["evidence_needed_for_stage_b"] = [R3_REPAIRS[spec_id]["evidence"]]
                    row["next_confirmation_points"] = [R3_REPAIRS[spec_id]["confirmation"]]

            self.assertEqual(hashlib.sha256(serialized(payload)).hexdigest(), R3_SHA)

            r4_confirmation = {
                "measurable_event_or_metric": "EIA 2026 electricity demand volume",
                "interpretation_effect": "The record-demand thesis would strengthen",
            }
            for spec in payload["strict_passed_spec"]:
                if spec.get("spec_id") == "STD26_A_010":
                    spec["next_confirmation_points"] = [r4_confirmation]
            for row in payload.get("decision_ledger", []):
                if row.get("spec_id") == "STD26_A_010":
                    row["next_confirmation_points"] = [r4_confirmation]

            self.assertEqual(hashlib.sha256(serialized(payload)).hexdigest(), R4_SHA)

            payload["status"] = "PASS_STAGE_A_SCHEMA_CONTRACT_CURRENT_MAIN_VALIDATED"
            payload["authoritative_stage_a"] = True
            payload["stage_b_eligible"] = True
            payload.setdefault("rematerialization_provenance", {})["stage_b_rerun_authorized"] = True
            payload["recommended_for"] = [
                "Stage B r0 / Prompt 0.2 using Stage A strict_passed_spec[] only"
            ]
            payload["repo_validation_contract"] = {
                "current_main_sha": "d3bd43d0bdc0870bd0c81917f0e30b0fbb078542",
                "stage_lineage_contract_check_blob_sha": "6564a15009dce9cfa0377a3b6f8e8656d20db62f",
                "stage_artifact_contract_check_blob_sha": "6f49dad0db3ecc68d708d398a74beb3036e46308",
                "workflow_contract_validation_file": ".github/workflows/workflow-contract-validation.yml",
                "validation_mode": "current-main repository-native full Stage A lineage validation",
                "temporary_validation_pr": 259,
                "card_data_blob_sha": "0cc4e610f9c1ad105761d399be1cd0e316f95128",
                "canonical_card_count": 1373,
                "stage_b_c_evidence_imported": False,
                "historical_editorial_outcomes_reopened": False,
            }

            raw = serialized(payload)
            actual_sha = hashlib.sha256(raw).hexdigest()
            self.assertEqual(actual_sha, EXPECTED_SHA)
            with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fh:
                fh.write(raw)
                target = Path(fh.name)

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
            if proc.returncode != 0:
                gh_error(
                    "Early16 Stage A validator",
                    f"target_sha={actual_sha}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
                )
            self.assertEqual(proc.returncode, 0, proc.stdout + "\n" + proc.stderr)
            self.assertIn("RESULT: PASS_STAGE_A_SCHEMA_CONTRACT", proc.stdout)
        except Exception as exc:
            gh_error("Early16 test harness", f"{type(exc).__name__}: {exc}")
            raise
        finally:
            if target is not None:
                target.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

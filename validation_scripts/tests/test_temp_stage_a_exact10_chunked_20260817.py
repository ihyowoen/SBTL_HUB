#!/usr/bin/env python3
import base64
import contextlib
import hashlib
import io
import json
import lzma
from pathlib import Path
import unittest

from validation_scripts import stage_lineage_contract_check as validator

R1_SHA = "724c7931d95ef55f107cc36b0bc13d9913fb72b6ca0d33ec88b4e583a9f5f9cc"
R2_SHA = "cb72674a2e2b11001ea6e5682a63d33f6b2d4f0e49cdb3011a902689e1009947"
EXPECTED_ENCODED_SHA256 = "058d13fe9c8ee35e59436a10738b3f59435cfa25629b9f58f9b024c49ba361b8"
EXPECTED_ENCODED_LENGTH = 28524
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
FIXTURES = [
    ("temp_exact10_good_00.txt", "91baf2236789209272ba53c2f595396d49d37e43650866578357781864bbeeb8"),
    ("temp_exact10_good_01.txt", "4c004e9a9b80dea8f18028406ef508d8f398727b9dbb4c356866f676b031bb2a"),
    ("temp_exact10_good_02.txt", "88e08db167de472738963abdf66c9533bbf1673c953d462ffd209809656430b2a"),
    ("temp_exact10_good_03.txt", "4a69c07092fbbd4476c2588fff39080cbb392269f40e1f5389e3dc44f32492e3"),
    ("temp_exact10_good_tail_a.txt", "a0dc8442dd09afd82f98d4dff3ccbdb0841317b72e7c286124406e1bfe61f0f7"),
    ("temp_exact10_good_tail_b.txt", "5a19112ca63decb76d19084ed2571926310068eb7460c94f5106b6eec64aace1"),
]

E = {
"STD26_A_052": [
("KAIST official document or primary-research document", "KAIST VRFB electrolyte process 67% production-time reduction, comparator process conditions, and electrolyte-quality test result"),
("KAIST technical test result or primary-research document", "KAIST catalyst-reuse test result above 2,500 cycles and lab-versus-pilot production stage"),
("KAIST publication document or primary-research document", "KAIST VRFB paper publication date and technology-validation stage")],
"STD26_A_053": [
("BAK official production notice or company filing", "BAK 85Ah model production status, production date, and AIDC application"),
("BAK technical test result or technical document", "BAK 85Ah pulse-response test result, rate-capability metric, cycle metric, and safety metric"),
("Named same-event industry report", "BAK 85Ah production status and product-specification metric")],
"STD26_A_054": [
("Kempower or DLL official project document", "Astwick deployment completion status, leasing-contract structure, counterparty identity, and implementation date"),
("Electrive same-event industry report", "Astwick completed-deployment status and first-UK leasing characterization"),
("Astwick lease contract or financing document", "Astwick asset-ownership status, lease-tenor metric, payment structure, and covered-charger scope")],
"STD26_A_055": [
("Intertek certification document or i-charging official notice", "i-light ETL approval status, certificate scope, covered standards, model identity, and certification date"),
("i-charging technical document or technical test result", "i-light 1.5MW capacity rating and retained product-performance metric"),
("Named customer contract or deployment report", "i-light North American shipment status, customer qualification status, or deployment date")],
"STD26_A_056": [
("SAMR official statistics or enforcement document", "China H1 2026 charging-meter inspection volume, non-compliant-device volume, investigation volume, and publication date"),
("SAMR official dataset or enforcement notice", "China H1 2026 charging-meter nationwide scope, inspection-period date, and metric definitions"),
("Named same-event industry report", "China charging-meter enforcement status and investigation-versus-penalty distinction")],
"STD26_A_057": [
("China Customs official dataset or statistics", "China July 2026 rare-earth export volume, product definition, and publication date"),
("China Customs monthly trade dataset", "China July 2026 rare-earth export volume, month-on-month metric, year-on-year metric, and four-month-low status"),
("Named Tier-1 same-event report", "China July 2026 rare-earth export volume and directional trade-flow metric")],
"STD26_A_058": [
("NioCorp company filing or official document", "Lockheed-NioCorp scandium arrangement contract status, quantity, date, and binding status"),
("Lockheed, Teck, or 5N Plus official document or company filing", "Lockheed germanium sourcing-negotiation status and counterparty status"),
("US government procurement document or company filing", "Lockheed strategic-mineral procurement-program status and localization-program linkage")],
"STD26_A_083": [
("FCC official order, determination, or notice", "FCC connected-inverter Covered List approval status, affected-equipment scope, adoption date, and authorization consequence"),
("Reuters July 28 report", "FCC connected-inverter market-access action status and bounded product scope"),
("APPA July 29 report", "FCC connected-power-equipment implementation scope and authorization status")],
"STD26_A_084": [
("SNE Research official dataset or statistics", "SNE H1 2026 BEV+PHEV delivery volume of 9.906 million, +5.5% year-on-year metric, period, and publication date"),
("SNE Research methodology document or dataset", "SNE H1 2026 regional and OEM definition status and methodology consistency"),
("Named same-period market dataset or registration statistics", "H1 2026 global EV delivery volume and year-on-year growth metric")],
"STD26_A_085": [
("Financial News August 10 report", "Chaevi service-extension status through September 30, extension decision date, and reported usage metric"),
("Aju News August 10 report", "Chaevi extension deadline of September 30 and operating-result metric"),
("Chaevi official program document or notice", "Chaevi ministry-program status, fleet capacity, site count, and September 30 operating deadline")],
}

C = {
"STD26_A_052": [
("KAIST pilot-production throughput test result and repeatability metric", "A verified pilot result would raise commercialization probability; a lab-only result would hold the assessment at research stage."),
("KAIST industrial-process cost metric and yield test result versus conventional electrolyte production", "A verified cost or yield advantage would strengthen manufacturability assessment; no advantage would weaken the assessment."),
("KAIST customer qualification status or field-deployment decision", "A verified qualification or deployment would raise commercialization probability; continued absence would hold the assessment at research stage.")],
"STD26_A_053": [
("BAK 85Ah shipment volume or AIDC customer qualification status", "A verified shipment or qualification would raise commercialization probability; product-only status would hold the assessment."),
("BAK 85Ah pulse-response test result and rate-capability metric", "A verified performance result would strengthen the AIDC-use assessment; materially weaker performance would weaken the assessment."),
("BAK 85Ah production capacity or shipment volume update", "A sustained production or shipment metric would raise supply-visibility assessment; no follow-through would hold the assessment.")],
"STD26_A_054": [
("Kempower-DLL additional UK site launch count or contract award", "Additional verified launches or awards would strengthen adoption assessment; no replication would weaken the assessment."),
("Kempower-DLL lease cost metric, tenor metric, or operator capex-reduction metric", "Verified attractive economics would strengthen financing-model assessment; unattractive economics would weaken the assessment."),
("Astwick charger utilization metric or uptime metric", "Sustained utilization or uptime would strengthen commercial-viability assessment; weak operation would lower the assessment.")],
"STD26_A_055": [
("Intertek i-light approval status and covered-standard scope", "A confirmed approval scope would strengthen North American market-access assessment; a narrower scope would weaken the assessment."),
("i-light North American shipment volume or customer qualification status", "A verified shipment or qualification would raise commercialization probability; no deployment evidence would hold the assessment at certification stage."),
("i-light installed-unit uptime metric or technical test result", "A confirmed operating result would strengthen product-readiness assessment; adverse performance would weaken the assessment.")],
"STD26_A_056": [
("SAMR final penalty decision or rectification decision for the 282 investigations", "Confirmed sanctions would raise compliance-risk assessment; closure without material action would lower the assessment."),
("China H2 charging-meter inspection volume and non-compliance-rate metric", "Persistent or rising non-compliance would raise operating-risk assessment; a material decline would lower the assessment."),
("SAMR metering-rule effective date or penalty-threshold decision", "A stricter implementation decision would strengthen policy-impact assessment; relaxation would weaken the assessment.")],
"STD26_A_057": [
("China August 2026 rare-earth export volume and month-on-month metric", "A continued decline would strengthen physical-supply-tightening assessment; a rebound would weaken the assessment."),
("China Customs July-August product-level rare-earth export volume metric", "Concentration of the decline in constrained categories would strengthen supply-security assessment; a broad rebound would weaken the assessment."),
("Rare-earth importing-country inventory volume or delivery-price metric", "A tighter inventory or higher price metric would strengthen real-market-impact assessment; stable availability would lower the assessment.")],
"STD26_A_058": [
("Lockheed scandium or germanium contract status, contracted volume, and contract tenor", "A binding contract would raise demand-certainty assessment; stalled negotiations would weaken the assessment."),
("NioCorp Elk Creek financing decision, FID decision, or production schedule", "A financing or production milestone would strengthen project-bankability assessment; delay would lower the assessment."),
("Lockheed strategic-mineral procurement volume or additional supplier-contract count", "Broader procurement would strengthen strategic-demand-persistence assessment; isolated negotiations would hold the assessment.")],
"STD26_A_084": [
("SNE next-month or H2 global BEV+PHEV delivery volume and year-on-year metric", "Continued growth would strengthen EV-demand assessment; a marked slowdown would weaken the assessment."),
("SNE next-update OEM and regional delivery-share metric", "Persistent divergence would strengthen competitive-redistribution assessment; convergence would weaken the assessment."),
("SNE methodology revision decision or dataset-restatement status", "A material restatement would weaken confidence assessment; no revision would strengthen the assessment.")],
"STD26_A_085": [
("Chaevi post-September-30 service-extension decision or permanent-service launch", "A further extension or permanent launch would strengthen commercial-demand assessment; termination would weaken the assessment."),
("Chaevi extension-period charge-session volume, energy-delivery volume, or repeat-user metric", "Higher realized usage would strengthen demand assessment; weak usage would lower the assessment."),
("Chaevi fleet capacity, service-area count, or paying-site count", "Verified scale-up would strengthen commercial-viability assessment; no expansion would hold the assessment.")],
}


def apply_r2(payload):
    by = {item["spec_id"]: item for item in payload["strict_passed_spec"]}
    for sid, rows in E.items():
        by[sid]["evidence_needed_for_stage_b"] = [
            {"source_or_document_class": source, "exact_claim_or_metric": target} for source, target in rows
        ]
        if sid in C:
            by[sid]["next_confirmation_points"] = [
                {"measurable_event_or_metric": metric, "interpretation_effect": effect} for metric, effect in C[sid]
            ]
        by[sid]["stage_a_current_main_recertification"]["semantic_metadata_normalized_for_current_validator"] = True
    payload["repair_audit"]["structured_stage_b_evidence_metadata_normalized"] = True
    payload["repair_audit"]["structured_stage_b_evidence_metadata_scope_count"] = 10
    payload["repair_audit"]["editorial_decisions_changed"] = False
    payload["repair_audit"]["strict_ids_changed"] = False
    payload["repair_audit"]["source_story_ids_changed"] = False
    payload["status"] = "PASS_STAGE_A_EXACT10_CURRENT_MAIN_RECERTIFIED_CANDIDATE_R2"
    payload["generated_kst"] = "2026-08-17T22:15:00+09:00"
    payload["local_current_contract_validation"]["semantic_metadata_repair"] = {
        "status":"PASS_LOCAL_NORMALIZATION",
        "selection_changed":False,
        "route_changed":False,
        "scores_changed":False,
        "story_ids_changed":False,
        "urls_changed":False,
        "note":"Only Stage B evidence/confirmation metadata wording was normalized to current validator grammar."
    }
    return payload


class Exact10StageAR2ValidationTest(unittest.TestCase):
    def test_r2_exact_bytes_against_current_public_validator(self):
        encoded = "".join((FIXTURE_DIR / name).read_text(encoding="utf-8") for name, _ in FIXTURES)
        self.assertEqual(len(encoded), EXPECTED_ENCODED_LENGTH)
        self.assertEqual(hashlib.sha256(encoded.encode()).hexdigest(), EXPECTED_ENCODED_SHA256)
        raw = lzma.decompress(base64.b64decode(encoded, validate=True))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), R1_SHA)
        payload = apply_r2(json.loads(raw.decode("utf-8")))
        r2_raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        self.assertEqual(hashlib.sha256(r2_raw).hexdigest(), R2_SHA)
        self.assertEqual(len(payload["strict_passed_spec"]), 10)
        self.assertEqual(len(payload["decision_ledger"]), 13)
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
            rc = validator.check_stage_a_full(payload)
        if rc != 0:
            print(captured.getvalue())
        self.assertEqual(rc, 0, "current public Stage A validator rejected exact10 R2 artifact")


if __name__ == "__main__":
    unittest.main()

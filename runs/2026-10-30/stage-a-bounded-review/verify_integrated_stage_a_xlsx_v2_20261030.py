#!/usr/bin/env python3
"""Independently verify V2 @oai/artifact-tool OOXML output and recalculated counts."""
from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = HERE / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V2_20261030.json"
XLSX = ROOT / "outputs/stagea-20261030-integrated-v2/STAGE_A_1330_SOURCE_EVIDENCE_INTEGRATED_V2_20261030.xlsx"
OUT = HERE / "STAGE_A_1330_XLSX_V2_EXPORT_READBACK_QC_20261030.json"
XML = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def value(cell, strings):
    if cell.get("t") == "inlineStr":
        return "".join(x.text or "" for x in cell.iter(XML + "t"))
    v = cell.find(XML + "v")
    if v is None:
        return ""
    return strings[int(v.text)] if cell.get("t") == "s" else v.text or ""


def main():
    if OUT.exists():
        raise FileExistsError("create-only verifier receipt already exists")
    src = json.loads(SOURCE.read_text(encoding="utf-8"))
    original_ids = [r["candidate_id"] for r in src["source_rows"]]
    assert len(original_ids) == len(set(original_ids)) == 1330
    with zipfile.ZipFile(XLSX) as f:
        assert f.testzip() is None
        shared = ET.fromstring(f.read("xl/sharedStrings.xml"))
        strings = ["".join(x.text or "" for x in si.iter(XML + "t")) for si in shared.findall(XML + "si")]
        sheet = ET.fromstring(f.read("xl/worksheets/sheet2.xml"))
        ids = {}
        for c in sheet.iter(XML + "c"):
            address = c.get("r", "")
            if address.startswith("B") and address[1:].isdigit() and 5 <= int(address[1:]) <= 1334:
                ids[int(address[1:])] = value(c, strings)
        assert [ids[i] for i in range(5, 1335)] == original_ids
        first = ET.fromstring(f.read("xl/worksheets/sheet1.xml"))
        cells = {c.get("r"): c for c in first.iter(XML + "c")}
        expectations = {"B6": "1330", "B7": "45", "B8": "1285", "B9": "97",
                        "B10": "1233", "B11": "103", "B12": "63", "B13": "40"}
        for key, want in expectations.items():
            assert cells[key].find(XML + "f") is not None, key
            assert value(cells[key], strings) == want, key
        assert "40 score-60+ IDs" in value(cells["A29"], strings)
        assert "xl/tables/table1.xml" in f.namelist()
    result = {
        "qc_result": "PASS_V2_XLSX_1330_ORIGINAL_ID_ORDER_EIGHT_CACHED_FORMULAS_AND_FILTER_NOT_STAGE_A_NATIVE_PASS",
        "source_json_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "xlsx_sha256": hashlib.sha256(XLSX.read_bytes()).hexdigest(),
        "xlsx_bytes": XLSX.stat().st_size,
        "original_ids": 1330,
        "original_formal_pending": 1285,
        "evidence_linked": 97,
        "high_no_evidence": 40,
        "native_strict_promotions": 0
    }
    OUT.open("x", encoding="utf-8").write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

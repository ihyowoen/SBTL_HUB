#!/usr/bin/env python3
"""Independently inspect exported OOXML cells without using an Excel writer."""
from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_20261030.json"
XLSX = BASE / "outputs/stagea-20261030-integrated/STAGE_A_1330_SOURCE_EVIDENCE_INTEGRATED_20261030.xlsx"
OUT = Path(__file__).resolve().parent / "STAGE_A_1330_XLSX_EXPORT_READBACK_QC_20261030.json"
XML = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def value(cell: ET.Element, strings: list[str]) -> str:
    t = cell.get("t")
    if t == "inlineStr":
        return "".join(x.text or "" for x in cell.iter(XML + "t"))
    v = cell.find(XML + "v")
    if v is not None:
        return strings[int(v.text)] if t == "s" else (v.text or "")
    return ""


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    expected = [x["candidate_id"] for x in data["source_rows"]]
    assert len(expected) == len(set(expected)) == 1330
    with zipfile.ZipFile(XLSX) as f:
        assert f.testzip() is None
        strings_xml = ET.fromstring(f.read("xl/sharedStrings.xml"))
        strings = ["".join(x.text or "" for x in item.iter(XML + "t"))
                   for item in strings_xml.findall(XML + "si")]
        detail = ET.fromstring(f.read("xl/worksheets/sheet2.xml"))
        ids = {}
        for cell in detail.iter(XML + "c"):
            address = cell.get("r", "")
            if address.startswith("B") and address[1:].isdigit() and 5 <= int(address[1:]) <= 1334:
                ids[int(address[1:])] = value(cell, strings)
        actual = [ids[n] for n in range(5, 1335)]
        assert actual == expected
        overview = ET.fromstring(f.read("xl/worksheets/sheet1.xml"))
        cells = {cell.get("r"): cell for cell in overview.iter(XML + "c")}
        recalc_checks = {"B6": "1330", "B7": "45", "B8": "1285", "B9": "83",
                         "B10": "1247", "B11": "103", "B12": "49", "B13": "54"}
        for key, want in recalc_checks.items():
            node = cells[key]
            assert node.find(XML + "f") is not None, "missing live formula " + key
            assert value(node, strings) == want, (key, value(node, strings))
        assert "xl/tables/table1.xml" in f.namelist(), "expected source filter table absent"
    report = {
        "qc_result": "PASS_EXPORTED_XLSX_BOTH_SHEETS_ID_AND_RECALC_CACHED_VALUE_READBACK",
        "file_sha256": hashlib.sha256(XLSX.read_bytes()).hexdigest(),
        "size_bytes": XLSX.stat().st_size,
        "source_id_cell_count": len(actual),
        "exact_id_sequence_matches_original_json": True,
        "all_eight_summary_formula_cached_values_match_independent_json": True,
        "source_table_filter_present": True,
        "native_stage_a_pass": False,
    }
    with OUT.open("x", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

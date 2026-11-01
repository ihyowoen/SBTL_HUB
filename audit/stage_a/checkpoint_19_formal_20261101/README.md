# Stage A CP19 — Audit branch index (2026-11-01)

Audit only. **Global Stage A HOLD: 1,204 / 1,330 Source IDs remain without formal 0.1P disposition.** No Stage B, `main`, Full, Related, or production mutations.

## Verified outcomes

| Field | Value |
|---|---:|
| Preserved original Source IDs | 1,330 |
| CP18 cumulative formal adjudications | 105 |
| CP19 added formal adjudications | 21 |
| CP19 cumulative formal adjudications | **126** |
| Pending | **1,204** |
| CP19 new strictly selected event representatives | **10** |
| CP19 same-event source supports | **6** |
| CP19 original-stage/protected-metric WATCH | **3** |
| CP19 verified out-of-industry rejections | **2** |
| Cumulative strict selected events | **30** |
| Native artifact contract | **PASS** |
| Native Stage A lineage contract | **PASS_STAGE_A_SCHEMA_CONTRACT** |
| Independent read-only QC | **INDEPENDENT_QC_PASS** |

## Saved complete artifacts

- [CP19 all-in-one ZIP: 1,330-row Stage A JSON, receipt, primary-source report, builder and independent QC](https://drive.google.com/file/d/1zaJtOnzjUpHixq4Cq30uIzyWN8zIL7Mb/view)
- [Korean event-by-event report with owner-primary links](https://drive.google.com/file/d/1ncwJAM9ugifk6YpIbagCnE5jXIS-Qk8-/view)
- [Independent QC result JSON](https://drive.google.com/file/d/1ujx3Yp3hhbZbPhu8TwxWPZFvlp9tSz7Z/view)
- [21-row formal decision receipt](https://drive.google.com/file/d/1hEK0H0hgDPAECTt8N_4jozrcuC3Xj_t2/view)

## Integrity

| File | SHA256 |
|---|---|
| CP19 Stage A 1,330-row JSON | `bf30369c00bd528b4ab32c628a388b48a56471ac5e8f34fd22631bcb8eaead7d` |
| All-in-one ZIP | `103fdae80c9497b39035a971a7160e9caa6f4040f742bc1d27fb5cf60f20f7f5` |
| CP18 baseline JSON | `4b9039f9f045e92ae5485ddab4ab0ab40bb19da8fdf59bb02c6c0b5adba44b66` |
| Locked Full 1,676 cards | `d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9` |

The four uploaded Drive files were independently downloaded back and matched byte-for-byte SHA256 with their respective original local files. ZIP integrity (`unzip -t`) also passed.

## Audit branch contents

`report.md`: Korean 21-source adjudication report with original owner URLs.  
`receipt.json`: changed Source IDs, explicit event cluster and individual economic-action edges.  
`independent_qc.json`: independent validation including native outputs.  
`build_cp19.py`: builder from immutable CP18 + locked Full1676 references.  
`verify_cp19.py`: independent baseline comparison, exact 21-row delta, disjoint 1,330-source partitions, native contract re-run.  

Sub-event demarcation is deliberate: Nth Cycle–Glencore signed a binding preliminary term sheet, *not* an executed final ten-year offtake; VaultCo's Glencore and Mercuria each announced a separate USD500m commitment, *not* a documented cash draw or already stocked mineral inventory. Potential regulation, legislative passage, project selection, physical commissioning, and actual payment likewise remain distinct stages.

**Permission boundary:** This index belongs to `audit/stage-a-event-family-20261101` only. None of these documents is a published article or authorization to enter Stage B.

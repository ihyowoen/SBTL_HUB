# Stage A CP20 — Audit branch index (2026-11-01)

Audit-only checkpoint. **Global Stage A HOLD: 1,177 of 1,330 original Source IDs remain without formal 0.1P disposition.** No Stage B, `main`, Full, Related, or production mutations.

## Verified outcome

| Field | Value |
|---|---:|
| Preserved source IDs and source-row order | 1,330 |
| CP19 previously formal adjudications, unchanged | 126 |
| CP20 newly formal adjudications | **27** |
| CP20 cumulative formal adjudications | **153** |
| Pending formal decisions | **1,177** |
| CP20 new strictly selected event representatives | **12** |
| CP20 same-event support sources | **14** |
| CP20 prior Full event reinforcement | **1** |
| Cumulative strictly selected event representatives | **42** |
| Native artifact contract | **PASS** (42 strict, zero missing) |
| Native Stage A lineage contract | **PASS_STAGE_A_SCHEMA_CONTRACT** |
| Independent QC | **PASS** (27 exact rows changed, 126 earlier formal unchanged) |
| New final articles, Stage B execution | **0** |

## Persisted complete artifacts in the existing Google Drive audit folder

- [CP20 entire 1,330-row formal Stage A JSON](https://drive.google.com/file/d/1yE8ftwMo9yNtRi3zZK3sc1jZ4ucXHrWG/view)
- [CP20 bundled ZIP containing 1,330-row JSON, 27-ID receipt, Korean report, builder, verifier and independent QC](https://drive.google.com/file/d/19qw5KmfHyhSW_-uaNSSHXbo7yaN3_ZjT/view)
- [27-ID detailed first-party evidence report (Korean)](https://drive.google.com/file/d/1c73wWhgs_BX7cx_FmeOtwysuwHiDrKnV/view)
- [CP20 independent QC result](https://drive.google.com/file/d/1-WlLvK2GP62NPtt3VgnPPZDjwhCeC-D_/view)

## Cryptographic read-back check

Each of the four uploaded Drive files was independently fetched again. Re-downloaded SHA256 digests equal the original local file digests. The four file lengths match as well. The local combined ZIP also passed `unzip -t` on all six entries.

| File | SHA256 |
|---|---|
| CP20 1,330-row Stage A JSON | `b0b06dae8fd3ac19950772479ba087e0c8b661f3388899b9bbd370f789cd21c1` |
| Entire CP20 ZIP | `ab41ff5424580037fab0251622030232d2548a61b9312e5c580958ae197507d7` |
| Korean first-party report | `0628515be00b8215f018c1c5de59bb519ded4f1ad88f82dfaced024f8f547a7d` |
| Independent QC | `6587229467077aeff7b338e9d9047f8665d9e694b959cc7ba5c4efc62167bba9` |
| Receipt contained in ZIP | `4412a400d1775e214fecbbfb0e7a6c2cc91d4879aee93a5ea2cf822ea3a0a1df` |
| Immutable CP19 baseline | `bf30369c00bd528b4ab32c628a388b48a56471ac5e8f34fd22631bcb8eaead7d` |
| Immutable 1,676 Full reference | `d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9` |

## Audit branch contents

`report.md`: Korean detailed 12-event adjudication, 14 same-event-support dispositions, 1 Full reinforcement, with original corporate URLs.  
`receipt.json`: exact 27 immutable Source IDs, adjudication outcomes, cluster IDs and preserved economic-act edges. The receipt is written before QC; look at independent QC for the subsequent PASS.  
`independent_qc.json`: formal-row immutability, original source preservation, important stage guards, and both native contract outputs.  
`build_cp20.py`: reproducible CP20 build from CP19 and locked Full.  
`verify_cp20.py`: independent comparative QC and native contract invocation.

## Stage and deduplication safeguards

- Jupiter Power primary source says **3.6GWh**, not 3.8GWh in media headline; four transactions closed **April–July 2026**, disclosed in September.
- Finland AKKU One **300MWh construction** is a separate economic phase from Sungrow's **600MWh supply allocation**, but the former 300MWh is within the latter 600MWh; do not add the two.
- NIO–Geely definitive agreement and Global Lithium–Titan Scheme Implementation Deed do **not** by themselves evidence a transaction close.
- VW/PowerCo–Gotion's planned 3 JVs and conditionally contracted 5.3% equity sale are distinct sub-acts, not commissioned factories or a closed stake transfer.
- EVE 30GWh is company-reported strategic cooperation, not independently verified binding per-counterparty orders; Geely's 20% battery-life result is company-reported, not externally validated.
- CATL copper-foil source row 1184 supports the existing locked Full event `2026-09-06_CN_03` and does not create a new event card.

**Permission boundary:** These files belong only to `audit/stage-a-event-family-20261101`. The corpus is not fully adjudicated, so Stage A stays HOLD and no Stage B authorization is implied.

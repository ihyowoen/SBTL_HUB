# Stage A exhaustive source-URL observations (2026-10-30 KST)

**Source universe:** original 1,330 rows; SHA256 `5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116`; 1,330 unique Source IDs and no edited originals. This is an **observational provenance graph**, **not** a final economic-event cluster ledger or Stage A native PASS.

## Measured evidence

| Read-only check | Exact result |
|---|---:|
| Source ID rows | **1,330** |
| Rows containing a source URL in this CSV | **1,324** |
| Distinct query-aware normalized source URLs | **1,210** |
| Singleton URL source observations | **1,098** |
| Distinct repeated-URL observation groups | **112** |
| Source IDs in those groups | **226** |
| Additional observations above first for each repeated URL | **114** |
| Repeated-URL groups with different prior Stage A pool labels | **14** |
| Repeated-URL groups with different prior scores | **16** |
| Rows with blank primary_url in this CSV | **6** |

The six blank-URL Source IDs are `R13_DISC_001`, `R13_DISC_002`, `R13_DISC_003`, `R4_DISC_001`, `R13_DISC_004`, `R13_DISC_005`. **Some are among the prior eight strict-passed specs and may have source paths in their other artifacts**: a blank column here must not be reported as absolute evidence absence. Verify their actual Stage spec lineage instead of deleting them.

## Why this matters for 658 WATCH and 636 review candidates

The same exact preserved source URL can have different metadata adjudication depending on collection run. Fourteen groups have different pool labels; examples:

- A [Porsche recycled-cathode news URL](https://www.impacton.net/news/articleView.html?idxno=30033) is Source IDs `SRC26-20260923_132732-0034` (review 44) **and** `SRC26-20260926_120143-0112` (WATCH 26).
- A [Sorégies–BP Pulse France fast-charging acquisition story](https://www.electrive.com/2026/09/25/soregies-acquires-bp-pulse-fast-charging-network-in-france) is `SRC26-20260926_120143-0236` (WATCH 26) **and** `SRC26-20260928_160143-0208` (review 64).
- A [Reuters Indonesia nickel-curb commentary](https://www.reuters.com/commentary/reuters-open-interest/indonesias-nickel-production-curbs-leave-market-unconvinced-2026-09-22) is `SRC26-20260923_132732-0160` (WATCH 26) **and** `SRC26-20260926_120143-0223` (review 57).

These differences are concrete metadata classification inconsistency signals, **not** proof that either copy deserves publication. Each retained Source ID still needs event/Related/date and four-judgment review. Do not lower-score-drop the 26-point copies automatically and do not treat higher scores as final value. The graph preserves all 1,330 observations, including 226 Source IDs on repeated URLs, with no destructive collapse.

The first-pass URL parser must retain query keys that define article identity (`idxno`, `no`, `list_no` and other nontracking parameters). Dropping query strings falsely merges at least two unrelated article pairs already identified in the 103-source audit. Exact URL equality also need not mean the underlying page contents and economic act are unchanged: revised notices and government board attachments can evolve. Therefore the script writes `SOURCE_URL_OBSERVATION_…` identifiers **only**, never fills the original economic-event cluster field.

## Automated QC and remaining gate

`build_1330_source_url_observation_graph_20261030.py` enforces original SHA256, all 1,330 unique Source IDs, 1,324/1,210 URL arithmetic, 112/226/114 recapture accounting, 14 mixed-pool and 16 mixed-score group counts, and six missing column URLs. Its JSON includes a full **1,330-row Source ID → query-aware URL-observation mapping** plus all 112 multi-observation groups. Running the source builder is a **scoped provenance QC PASS**, not `stage_artifact_contract_check.py A`/`stage_lineage_contract_check.py stage_a` pass.

**Status:** Source ID preservation PASS; URL grouping PASS; full economic clustering and 1,285 formal 0.1P outcomes **HOLD**; new strict promotions 0; native Stage A exit **NOT EXECUTED**. Preserve existing 7 drafts separately. Next single bottleneck remains source-bound full-universe event identity and four judgments, treating the 14 mixed-pool groups as an early inconsistency-review lane while systematically covering remaining 636 review and 658 WATCH records.

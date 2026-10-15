# R24 — PR #386 pre-review blocker fixes and URL reproducibility

**2026-10-15 KST | AUDIT ONLY | HUMAN REVIEW PENDING | NO MERGE / NO CARD APPLY**

## Historical input and current baseline separation
- The original four 2026-09-20/23/26/28 Collector ZIPs remain immutable, with original ZIP SHA-256 pinned by `RECOVERY_CHECKPOINT.md`.
- Independently verified archived `R4_SOURCE_ROW_LEDGER_1157.csv` SHA256: `6fafdd2470cf33c6c58dcda6b7a5cd065faaef6ed5ece2c01302e504de619111`.
- Historical R12 comparison source: PR #386 head commit `4bce4b1f3e7bd454538e718df7666f03c5310aa0`, crosswalk original blob `63b092bb1e6938c8fdbd0a31e98142c198e1e368`.
- Later `main=6851fdbe4a25b30b7204d07708a1238123c14910` (PR #391 merged two existing-card corrections); Full blob `1af792e2e80516e1ec1d7d9660c150b312168b21`, Lean blob `41b51ca4fa4e4f40a92c18577ea0655483295be1`. **This new `main` is not covered by the historical R16 native 0.0D PASS**. Current-baseline 0.0D requires a fresh governance readback before any 0.0C authorization.

## Fixes responding to nine open Copilot review threads
1. `RECOVERY_CHECKPOINT.md`: exact URL normalization/replay pointer, replace obsolete 6×8 with required *6 region +14 topic* 0.0C machine axes and separate *12 structural editorial* lenses. Keep 26 Weekly discovery pathways distinct.
2. `PRELIMINARY_EVENT_QUEUE.md`: correct noncanonical eight-lens completeness claim.
3. `R12_EXACT_CANONICAL_AND_COVERAGE_AUDIT_20261012.md`: restore entire 40-hex Lean Git blob `c39eac64afde20ff0ccacd920e12abbdab1b3d02`. The previous string was 38 hex; add 0.0D historical-context correction.
4. `EVENT_BRIDGE_AND_QC_R2.md`: fix `RC26-014/014/015` to actual **new `RC26-020/021/022`** and preserve reused existing `RC26-014`. Correct obsolete lens descriptions, preserve IDs and original R2 provenance.
5. `R12_FULL_CANONICAL_URL_CROSSWALK_1157.csv`: strip acquisition-only query markers `sourceType=rss`, `.tsrc=rss`, `sc=rssn` on **exactly three** rows. Preserve semantic URL query identity parameters such as `no`, `idxno`, and `newsId`; no broad query stripping.
6. Add **`R24_NORMALIZED_URL_REPLAY_MANIFEST_1157.csv`**, a reviewable per-original-row manifest including old/new primary URLs, candidate IDs, triage and repeat group, stripped-param audit. Add **`R24_REPLAY_ARTICLE_URLS_V2.mjs`**: no external dependencies, uses pinned prior Git R12 blob, verifies all manifest and updated R12 bytes against Git hashes and all input UIDs (run with `node runs/2026-10-08/ops-recovery-intake-v1/R24_REPLAY_ARTICLE_URLS_V2.mjs`).
- Audit checked counts: 1,157 archive source IDs = KEEP **919** + TRIAGE_FILTERED **234** + REVIEW **4**; **1,045** distinct normalized URLs, **110** repeated URL groups covering 222 observed rows, **112** repeat recaptures. Removing those three markers does **not** change these totals.
- Updated crosswalk Git blob `b418ba95a17505e3344afabfc255f67be128243d`; derived URL manifest blob `61de9d5a104821040504124014fa3f7116285dd1`.

## Mandatory hard HOLD remains
- The current **0.0C full-universe coverage, 6+14 machine axes, 12 structural editorial lenses**, candidate event terminal statuses and new-baseline 0.0D recertification are **not complete**. The *industry* 26 discovery lenses broaden recall, not a formal replacement for any gate.
- Stage A/0.4–0.8 and production release remain unauthorized. **PR #386 changes audit files only; merging it would NOT publish news**. Original Collector ZIPs, Full/Lean, Related, production, Revolution Masterfile/Downstream remain unchanged.
- All preexisting Copilot review threads remain for **human and reviewer re-review**, not silently marked resolved. This R24 is prepared for inspection, **not merged**.

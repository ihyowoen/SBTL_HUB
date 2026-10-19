# R25 — Persist R24 replay input and harden audit rename allowlist

**2026-10-20 KST · AUDIT ONLY · NO PRODUCTION / CARD WRITES · REVIEW REQUIRED · DO NOT MERGE**

## Durable original R12 input
- Historical PR-branch commit `4bce4b1f3e7bd454538e718df7666f03c5310aa0`, original R12 pre-correction blob `63b092bb1e6938c8fdbd0a31e98142c198e1e368`.
- `R24_ORIGINAL_R12_INPUT_1157.csv` is a tracked, byte-identical fixture (1,157 source UID rows; three raw RSS tracking query rows) reconstructed from immutable corrected-R12 rows and the original URL column of the R24 normalized-manifest. Independently submitted to the GitHub blob API, which returned the **exact original blob SHA** `63b092bb1e6938c8fdbd0a31e98142c198e1e368`.
- The R24 Node replay now reads and hashes this fixture, not `git show` on a historical branch-only commit that might be garbage-collected. Existing expected corrected CSV Git blob `b418ba95a17505e3344afabfc255f67be128243d` and manifest blob `61de9d5a104821040504124014fa3f7116285dd1` remain the hash-locked outputs.

## Rename-safe audit boundary
- `.github/workflows/r24-audit-url-replay.yml` now runs `git diff --no-renames --name-only -z` and iterates NUL-delimited paths, rejecting *both* sides if a production file is moved into the audit-only directory. Shell errors remain fatal via `set -euo pipefail`.
- Added an explicit negative regression that stages `data/cards.full.json` → an allowlisted audit destination inside a disposable Git repo, requiring the validator to observe BOTH pathnames. No production file was actually moved.

## Stage status, provenance and exclusions
- On **historical main** `b7847ca9885f6f27ae0566455b0a476ef1059d24`, Stage **0.0D isolated native executable PASS** occurred in R16 (2026-10-13); this is not a formal complete production run.
- On **later main** `6851fdbe4a25b30b7204d07708a1238123c14910`, fresh 0.0D re-certification **NOT RUN**. Stage **0.0C BLOCKED** (6 regions +14 topics; separate 12 editorial lenses; Weekly 26 independent recall paths), Stage A unauthorized.
- Initial R1–R3 statements that 0.0D had not run and only five files changed are **historical snapshots superseded by R16–R25**. Current PR change scope is audit-only and includes R4–R25; it is not limited to five files.
- 1,157 observations, 1,045 distinct normalized article URLs, 110 URL duplicate groups, zero formally accepted event-terminal decisions. No canonical Full, Lean, Related, Revolution Masterfile/Downstream, or production mutations.
- **CI must be rerun and observed on this exact new head before any PASS assertion. No automatic merge.**

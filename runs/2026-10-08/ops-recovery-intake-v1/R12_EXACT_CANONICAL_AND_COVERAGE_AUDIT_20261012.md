# R12 — Full Canonical Exact URL / Related / 0.0D–0.0C Continued Audit (2026-10-12)

**READ-ONLY AUDIT · NO STAGE A · NO CARD MUTATION · DRAFT/UNMERGED**

## Locked observational baseline
- GitHub `main`: `b7847ca9885f6f27ae0566455b0a476ef1059d24`.
- Canonical full blob `d0b472e4173e565284616bb7eec0e4b28e1a42b9`; lean blob `c39eac64afde20ff0ccacd920e12abbdab1b3d02`. Full card count 1,674.
- R4 Collector source ledger SHA256 `6fafdd2470cf33c6c58dcda6b7a5cd065faaef6ed5ece2c01302e504de619111`; 1,157 source row UIDs, KEEP 919 / TRIAGE_FILTERED 234 / REVIEW 4; 1,045 normalized primary URLs.

## Exact primary-URL crosswalk (not semantic event determination)
Authenticated full canonical JSON was read for this audit, and all 3,448 distinct normalized `cards.urls` values were screened against the 1,045 Collector primary URLs. The preliminary 13 filter hits were independently checked using exact URL equality (11 false positives).

- **2** exact primary URL overlaps: `2026-09-14_GL_01` CATL–BME Egypt official 9/16 source; `2026-09-10_EU_02` Vattenfall Brunsbüttel BESS FID.
- **1,043** Collector URLs have no exact primary-URL overlap. **NOT** 1,043 new events. Additional URL/syndication/event identity and current-card `Related` review remains.
- The 2 matches correspond to 2 preserved original source UIDs. All 1,157 are accounted as original observations; **none** has received a formal governed 0.0C terminal disposition. No content or source UID deletion.

## Related pre-existing debt is unchanged
Current full includes 513 `related[]` entries, with **14 dangling target IDs affecting 13 cards**. This is an exact set match to the pre-existing `docs/remediation/RELATED_LEGACY_DANGLING_MANIFEST_20260723.json`. No newly introduced dangling target; previous 14 remain unresolved. No target guessed, removed, or repaired here.

## Priority nonterminal event/Related leads
1. **NIO–Geely 9/27 definitive conditional transaction**: NIO Power 30% post-close in return for Geely Yiyi equity + RMB640m cash, NIO Power post-money RMB16bn; still subject to regulatory and customary closing conditions. 9/28 corporate communication is supporting same-transaction publicity, not a second completed acquisition. First party: https://ir.nio.com/news-releases/news-release-details/nio-announces-definitive-agreements-strategic-transaction-geely
2. **CATL Debrecen 9/22**: official first two cell lines **trial operations**, not 100GWh series output. https://www.catl.com/en/news/7000.html
3. **LGES–B2U** 9/22–24 cooperation must be challenged against `2026-09-09_US_01` operating repurposed BESS, not conflated.
4. **Geely PowerMind** 9/23 and earlier 1,500 kW charger `R8_02` require chronology and execution-stage challenge; four shared press-commentary articles are not four independent releases.
5. **Li Auto / Sunwoda / CALB** supply roles: `2026-09-04_CN_01` equity and `2026-09-07_CN_02` product prior lines require direct actor/action review.
6. **Hunan Yuneng** permitting vs `2026-07-16_CN_05` prior investment and separate legal entity **Ronbay** should not be silently merged.
7. **CATL ESS online list prices** vs `2026-09-09_CN_01` general rising-price trend; advertised list ≠ executed spot transaction.

These are candidate identity/reinforcement/follow-up **questions**, not approved editorial NEW items, Related edges, or production operations.

## Formal stage gates remain BLOCKED
- 0.0D: registry-tree path equality **96/96**, required active/dependency read count **43**, current governance code identified as `scripts/validate_card_run_v4_hardening.mjs` and `validation_scripts/card_run_v4_binding_hardening.py`. **Native execution on byte-exact current-main checkout and complete authority-conflict certification not executed.** Do not assert formal PASS or authorize 0.0C.
- 0.0C: Bounded queries were attempted across all **6 official region and 14 official topic machine keys** for 9/29–10/12 (72h → 7d → gap). All formal axis status values remain `blocked` with reasons because independent full result/source provenance, 1,157 UID-to-event terminal dispositions, discovered-item terminal ledger, and full semantic canonical/Related reconciliation remain incomplete.
- `original_input_accounted=false` means terminal accounting is unfinished, **not** that original files or UIDs were lost. `stage_a_authorized=false`.

## Audit evidence, external read-only preservation
- Drive: https://drive.google.com/file/d/1RMLj_pDs1lEZP4ls_hJqkF7WpAeyYLS_/view
- Evidence ZIP contains 1,157 UID crosswalk, 1,045 URL crosswalk, 20 formal-blocked axes with bounded search examples, candidate relation queue, Legacy Related 14/14 verification, formal 0.0D block diagnostics, SHA-256 manifest and reproducible local source+canonical verifier. Original article body/text is **not** committed to this public repository.
- The ZIP is evidence-only. No production card or lean writes. No Revolution master/downstream changes. This Draft PR **must not be merged** to release cards.

Next: execute 0.0D native gate under exact immutable checkout, complete 0.0C terminal universe/canonical/Related review, then formally Stage A/B/C and downstream separately.
### 2026-10-15 historical baseline clarification

The 2026-10-12 0.0D "not yet natively executed" line above accurately describes the **R12 snapshot** but was superseded by the R16 2026-10-13 native 0.0D executable PASS on then-current `main=b7847ca`. PR #391 subsequently moved `main` to `6851fdbe` (two previously existing card corrections), so new baseline-bound 0.0D certification is **not** claimed here. All 0.0C coverage statuses still remain BLOCKED.

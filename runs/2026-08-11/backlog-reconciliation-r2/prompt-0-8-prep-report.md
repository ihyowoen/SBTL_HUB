# Prompt 0.8 — Canonical Incremental Merge Preparation

Run: `20260809_BACKLOG_RECONCILIATION_R2`  
Baseline main: `d3137945860664116b1bf90bbb7bee54d2a6c1d9`  
Canonical blob: `a52745170c70aa649323e346413615c5995b890b`  
Baseline count: **1,343**

## Result

**BLOCKED_RUNTIME_CANONICAL_APPLY_AND_PROJECTION_VERIFICATION_UNAVAILABLE_IN_CHAT_RUNTIME**

The Prompt 0.8 **declarative merge package is complete**, but `github_merge_ready` is intentionally **not** asserted.

### Prepared operations

- insert: **32**
- update: **1** (`2026-06-26_EU_01`, Ofgem LDES)
- related_add: **10**
- related_remove: **0**
- delete: **0**
- declarative expected count after apply: **1,375**

### Production IDs

All **32** production IDs are allocated against the locked current-main date/region namespace.  
No historical suffix gap is reused.

### 0.8 consumer-gate correction

`REC26_A2_036` contained a stale Related fresh-anchor string referring to 2026-08-02 while the card's representative event, visible fields and Reuters evidence are 2026-07-27.  
The target (`2026-07-24_GL_01`) and `distinct_follow_up` decision are unchanged; only source-backed Related metadata was corrected.

### Ofgem update

`OFGEM_LDES_728` is an **existing-card update**, not a new insert.

Target: `2026-06-26_EU_01`

The update adds the 21 July revised minded-to special licence conditions / 28 July guidance and preserves the boundary that final decisions remain after autumn 2026 cap-and-floor awards.

Because this adds a source URL, the repository runtime must recompute source-audit metadata before Evidence QC.

## Why this is not yet github_merge_ready

Prompt 0.8 requires the actual locked canonical full to be applied and validated, then the lean projection regenerated and checked exactly.  
The GitHub connector verifies the canonical SHA/count and exposes its content, but the full git object is not mounted as local bytes in this chat runtime. Therefore the following have **not** been falsely claimed:

- governed apply/verify against the complete 1,343-card canonical
- source-audit recompute on the updated Ofgem card
- repository Evidence QC on the merge-ID scope
- Related lifecycle validator on the merge-ID scope
- generated 1,375-card canonical file
- regenerated lean projection exact match

No GitHub write, branch or PR was created.

## Exact next runtime sequence

```text
place this bundle at runs/2026-08-11/backlog-reconciliation-r2/
→ node scripts/apply_card_run.mjs --run <card-run> --base-main-sha d3137945860664116b1bf90bbb7bee54d2a6c1d9 --check
→ apply against canonical full
→ recompute source-audit metadata
→ run Evidence QC + Related lifecycle validators
→ node scripts/lean_cards.mjs
→ node scripts/lean_cards.mjs --check
→ only if all pass: mark github_merge_ready / pr_candidate_ready
```

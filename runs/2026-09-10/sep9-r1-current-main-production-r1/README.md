# Sep 9 R1 Current-Main Governed Run

Status: **PRODUCTION MERGED — POST-MERGE REMEDIATION OPEN**

PR #371 merged 16 inserts and two Related additions on 2026-09-12. A Codex review submitted after the merge found that the production subset had bypassed the full Stage A completeness discriminator and that the final 0.7C artifact did not contain an identity-level 415-row disposition ledger. This README records the actual current state; it supersedes the pre-merge `IN PROGRESS` checkpoint text without rewriting the historical operation.

## Locked source and baseline

- source file: `final_news_llm_input_newsletter_expanded_20260909_135804.json`
- SHA256: `623de4b2dd7726b92e01ca9c329c5780ee8c963af26d3e6c5e0b4b0536cd4c92`
- bytes: **10,601,218**
- original stories: **393**
- Prompt 0.0C expansion: **20** provenance-distinct discoveries + **2** event-split children
- governed universe: **415 identities**
- frozen pre-merge main: `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- frozen pre-merge canonical: **1,617 cards** / Git blob `beb2aa7615b583b4c9c0c269974601a0b26c2684`

The source bytes were recovered again during post-merge remediation and exactly matched the recorded byte size and SHA256.

## What completed

- Stage 0.0D and Prompt 0.0C source-universe construction completed.
- The 16 published cards passed their card-level Stage B through 0.7 content/evidence chain.
- PR #371 applied **16 insert / 0 update / 2 related_add / 0 delete / 0 related_remove**.
- Canonical cardinality moved **1,617 → 1,633**.

## What did not complete

The authoritative cumulative Stage A ledger contains only:

- terminal identities: **55 / 415**
- open identities: **360**
- duplicate terminal identities: **0**
- unknown terminal identities: **0**

The former 0.7C summary claimed `415/415`, but its four displayed disposition counts summed to only **403** and no identity-level ledger supported the claim. The post-merge reconciliation artifact now lists all 415 identities explicitly: the 55 documented terminal decisions remain terminal, and the other 360 are marked `UNADJUDICATED_BLOCKING` rather than being assigned invented dispositions.

Authoritative remediation records:

- `stage-a-terminal-accounting-post-merge.json`
- `stage-0-7c-415-final.json` — now fail-closed
- `stage-0-8-415-final.json` — prior merge authorization invalidated
- `direct-adds/2026-09-12-pr371-post-merge-remediation/audit.json`

## Published-card corrections

The bounded post-merge correction preserves all 16 card identities and all Related edges while:

- binding every card's `stage_b_lineage.artifact_sha256` to the exact corrected Stage B bytes;
- recording the September 8 publication dates of the ESS News and pv magazine HiNa–Volta articles while preserving September 2 as the event date;
- recording September 1 for the pv magazine China battery-tax article while preserving September 9 as the representative price-signal date;
- treating the Mining.com page as Reuters syndication, not as a second independent owner, and replacing the false multi-source PASS with a bounded single-source exception.

## Current authorization boundary

The 16 already-published cards remain in canonical because the post-merge findings concern full-universe selection completeness and metadata lineage, not a demonstrated false event identity. No deletion or Related removal is authorized by this remediation.

The run may not again claim full Stage A, 0.7C, or Prompt 0.8 completion until all 415 identities are terminally adjudicated in a machine-validated ledger. The active Stage A validator now rejects self-asserted production-subset flags as a completeness bypass.

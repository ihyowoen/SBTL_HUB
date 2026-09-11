# Sep 9 R1 Current-Main Governed Run

Status: **IN PROGRESS — STAGE A BATCHED EXACT-SOURCE ADJUDICATION**

This branch is the dedicated governed run for the Sep 9 raw input and is intentionally separate from historical reconciliation PR #369 and historical PROMOTE-95 rematerialization PR #372.

## Locked source and baseline

- source run: `2026-09-09 13:58 KST`
- source file: `final_news_llm_input_newsletter_expanded_20260909_135804.json`
- SHA256: `623de4b2dd7726b92e01ca9c329c5780ee8c963af26d3e6c5e0b4b0536cd4c92`
- bytes: **10,601,218**
- original stories: **393**
- KEEP **298** / REVIEW **3** / TRIAGE_FILTERED treasure **92**
- duplicate story IDs / primary URLs: **0 / 0**
- orphan / dropped: **0 / 0**
- upstream integrity groups: **7 groups / 25 flagged stories / 0 excluded**
- main: `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- canonical card count: **1,617**
- canonical full Git blob: `beb2aa7615b583b4c9c0c269974601a0b26c2684`

## Completed gates

- Stage 0.0D: **PASS**
- Raw Input Audit: **PASS**
- Prompt 0.0C: **PASS — RELOCKED**
- Prompt 0.0C validation: **PASS**

The authoritative Prompt 0.0C universe is **415 terminal identities**:

- **393** exact original source rows;
- **20** provenance-distinct external/pre-clean discoveries;
- **2** event-split child identities required to separate the two discrete BESS projects bundled in `EU_2026-09-08_C07` (Lixhe and Coo).

Terminal accounting is **415/415**, with duplicate / missing / unknown identities **0 / 0 / 0**. The prior **413** state is superseded because it counted only one of two independent `+2` repairs: the Lixhe/Coo event split and the later Cloudbreak/Elmet pre-clean rescue.

## Current Stage A progress

The current cumulative Stage A ledger is:

- terminal identities: **55 / 415**
- open identities: **360**
- duplicate terminal identities: **0**
- unknown terminal identities: **0**
- existing reinforcement / same-event: **15**
- split parent decomposed: **1**
- candidate review: **24**
- watch / support context: **6**
- reject / support only: **8**
- support-source-only: **1**

The active U.S. batch contains **32 original source rows**. Current exact-source accounting is **17 / 32 resolved**, including 2 identities already terminal before the batch and 15 newly adjudicated rows. **15 U.S. identities remain unresolved** because their exact Sep9 source metadata has not yet been safely recovered; they are not inferred from older raw copies or reused story IDs.

Authoritative progress artifacts:

- `stage-a-cumulative-ledger-r1.json`
- `stage-a-cumulative-validation-r1.json`
- `stage-a-batch-us32-partial-r1.json`

## Semantic and cardinality red-team

A semantic red-team of the 13 hard-coded canonical-repeat mappings confirmed **13/13 same-event**, false mapping **0**. Because story IDs are run-local and may be reused between raw runs, cross-run story-ID equality is never treated as event evidence.

A second completeness repair re-examined four battery/ESS/materials events present only in the raw pre-clean universe. Cloudbreak–GETEC and Elmet–ams OSRAM were rescued into 0.0C as provenance-distinct discoveries (`SEP09_DISC_012`, `SEP09_DISC_013`); the PG&E SHARE VPP re-report and Zeekr 200,000-unit milestone were explicitly not promoted.

## Legacy stage-chain fail-close

A prior static Stage A→0.7C chain and a 16-insert / 2-related-add operation freeze existed on this branch. It is **not current authority**:

- the associated `.github/workflows/tmp-sep9-stage-chain-materialize.yml` contained a placeholder payload and all four workflow runs failed before creating any job;
- the static chain predated the combined 415-universe relock;
- the old Stage A full artifact is referenced only by SHA and is not present in the repo;
- the preserved compressed production-card payload was intended as **4 parts**, but only **part00 and part01** were ever committed. Decoder run `34569174493` failed with gzip EOF, so the incomplete payload is not recoverable authority.

The legacy chain is therefore marked **SUPERSEDED_REVALIDATION_REQUIRED**. Its 15 Stage A strict specs, one 0.1P-promoted spec, relation hints, and downstream findings may be reused only as per-spec salvage candidates after current source identity, event semantics, canonical relation, and 415-universe membership are revalidated.

## Stage A execution mode

Stage A is processed in **bounded exact-source batches** directly against the SHA-locked raw plus the authoritative 393-ID membership ledger, together with the 20 discovery identities and 2 event-split children. The final Stage A artifact cannot PASS until all **415/415 terminal identities** appear exactly once in the cumulative decision ledger.

The previously created `stage-a-input-features.json` contained an empty `stories[]` array and has been fail-closed. It is not authority for Stage A accounting.

Stage A rules remain unchanged:

- no external web/search fetch in Stage A;
- exact Sep9 raw controls the 393 original rows;
- Prompt 0.0C discoveries and event-split children remain separate provenance lanes;
- integrity-flagged rows remain individually reviewable;
- strict/review/watch/reject/support/reinforcement decisions must be exhaustively accounted;
- production IDs and canonical operations remain forbidden until downstream gates pass.

## Current parallel-work boundary

- PR #369 historical reconciliation: **COMPLETE / READY FOR REVIEW** — 243/243 terminally assigned.
- PR #372 historical PROMOTE-95 rematerialization: **DRAFT / PREFLIGHT PAUSED** while this current run advances.

## Required chain from here

`Stage A 415/415 → 0.1P → Stage B → Stage C → 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 → apply/merge → 0.9`

No canonical card mutation, production ID, delete or `related_remove` is authorized by this checkpoint.

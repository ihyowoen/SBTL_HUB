# SBTL_HUB Operations V4.1

**Status:** `ACTIVE_CANONICAL`  
**Version:** `SBTL_OPERATIONS_V4_1_20260902`

## 1. Start an ordinary new-news run

Use `docs/llm_prompts/v1/00_NEW_RUN_MASTER_PROMPT.md` as the launcher.

1. Read current `main` HEAD.
2. Lock `data/cards.full.json` blob SHA and card count.
3. Verify `public/data/cards.json` is the current deterministic projection.
4. Generate and replay-verify the deterministic 0.0D governance lock.
5. Load the registry-declared bootstrap context.
6. Audit raw input.
7. Load the locked 0.0C prompt just in time and run coverage discovery.
8. Lock the authoritative expanded event universe.
9. Reconcile the event universe against the complete canonical full before Stage A.
10. Before every later named stage, load that prompt from the locked commit and verify its blob against the governance lock.
11. Continue through named stages without skipping state transitions.

Unmerged PRs are not baseline.

## 2. 0.0D operating model

0.0D is machine-first. It does not ask the LLM to prove that it read dozens of active files.

Required order:

1. lock `main` SHA and canonical full blob SHA;
2. run `scripts/governance_lock_v4.mjs --emit` to create the 0.0D artifact from the git tree;
3. run the same helper with `--verify` to replay the lock from the exact baseline;
4. require complete `docs/**` lifecycle classification, exact active-authority blob bindings, zero active runtime override/addendum dependencies, and Stage A embedded-policy verification;
5. fully read only the exact `bootstrap_read_paths` emitted by the verified lock;
6. do not pre-load future named-stage prompts merely to satisfy a count;
7. stop on any registry/tree/blob mismatch.

`active_full_read_count` is not an authorization signal. A handwritten or model-generated count cannot replace the deterministic lock.

The compatibility field `all_docs_files_read_or_parsed` describes successful machine inventory/classification/blob-lock processing in V4.1; it is not a claim that the model deep-read every active body.

## 3. Just-in-time prompt loading

Every active named prompt is locked during 0.0D. Before executing a stage:

1. find the prompt entry in `governance_lock.locked_authorities`;
2. require `load_policy = jit_before_stage` unless the prompt was part of bootstrap;
3. load the file from the locked `repository_head_sha`;
4. verify its git blob SHA equals the lock entry;
5. execute the stage.

If the path/blob does not reproduce, re-lock/revalidate rather than silently using the current branch tip.

## 4. Raw input audit

Record schema, run tag, generated timestamp, story count, status counts, usable-text/source-packet coverage, date distribution, regions, sources, exact/canonical URL duplicates, headline duplicates, cross-run story-ID collision risk, future dates, stale recollection, publication/event-date confusion, source/body mismatch, and quarantine dispositions.

`KEEP`, `REVIEW`, `TRIAGE_FILTERED`, newsletter flags, and upstream recommendations are not card approval.

## 5. 0.0C coverage discovery

Search the supplied raw, current canonical full, trackers/watchlists/review pools, unresolved holds, official sources, and high-quality independent sources.

Required regions: Korea, North America, China, Japan, Europe, and material global markets.

Required topics include cells/chemistries, materials/components, pouch/pouch-film signals, ESS/BESS, EV/charging, manufacturing/capacity/utilisation, AI/data-centre power and grids, critical minerals, recycling, policy/trade/localisation, competitors/customers, prices/costs/margins, financing, safety, commissioning, and operating validation.

Every discovered item receives a terminal discovery disposition before Stage A.

## 6. Event clustering and reconciliation

Treat articles, events, and cards as different objects.

Classify:

- same article;
- same event / multi-source evidence cluster;
- existing-card reinforcement;
- existing-card update candidate;
- distinct material follow-up;
- new unrelated event;
- correction or reversal;
- hold/review.

Use event fingerprint, not actor/topic similarity.

## 7. Stage A integrated selector

Stage A uses only metadata/source-candidate information available in the expanded universe. It performs no web/body fetch.

For every strict or high-potential review candidate emit:

- credibility gate;
- cardability gate;
- anchor classes;
- decision-news-value score and breakdown;
- publication urgency;
- relation pre-pass;
- source/date/evidence questions for Stage B.

The full scoring policy and hard caps are embedded in the locked Stage A prompt.

## 8. Stage B / C and bounded repair

Stage B fetches and verifies evidence and produces an evidence-bounded draft. Stage C independently red-teams fact safety and lineage.

`0.2R` repairs only B-owned evidence/date/source/draft defects. `0.3R` performs controlled C revalidation after an authorized repair. A coverage, selection, duplicate, staleness, or material event-identity defect routes to the earliest owning stage and all affected downstream gates are rerun.

## 9. Addability through production

- `0.4`: latest-baseline addability revalidation;
- `0.5`: evidence/source-claim completeness;
- `0.6`: content/terminology polish;
- `0.7`: final publish readiness;
- `0.7C`: independent completeness/news-value challenge;
- `0.8`: exact declared incremental mutation and merge prep;
- merge only after active validators/review pass;
- `0.9`: merged-main and production verification.

Merge alone is not completion.

## 10. Manual direct-add boundary

An intentionally bounded already-reviewed direct add uses `MANUAL_DIRECT_ADD_V2`. It does not fabricate the formal stage ladder and remains mutually exclusive with formal card-run mutation in the same data PR.

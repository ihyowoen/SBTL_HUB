# SBTL_HUB — Standard New News Run Master Prompt V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `NEW_RUN_MASTER_PROMPT_V4_20260829`

Use this launcher for an ordinary new SBTL news run. It is not a backlog-reconciliation shortcut and does not inherit prior-run PASS states.

## 1. Absolute start rule

Do not start Stage A or draft cards from the attached raw file.

Start in this order:

```text
current GitHub main baseline lock
→ 0.0D Active Governance Preflight
→ Raw Input Audit
→ 0.0C Coverage Discovery
→ authoritative expanded event universe lock
→ complete canonical reconciliation + event clustering
→ Stage A Integrated Selector
→ Stage B
   ↔ 0.2R only for bounded Stage-B repair
→ Stage C
   ↔ 0.3R only for controlled Stage-C revalidation
→ 0.4 Addability Revalidation
→ 0.5
→ 0.6
→ 0.7
→ 0.7C
→ 0.8
→ validators / PR / merge
→ 0.9 production verification
```

0.2R/0.3R are conditional loops, not mandatory stages. A downstream defect routes to the earliest responsible stage and all affected downstream gates are rerun.

Current main governance outranks this launcher if a later canonical version explicitly replaces it.

### 1.1 Mandatory formal stage-artifact envelope

For a **formal card run**, every ordinary candidate artifact emitted by Stage A, B, C, 0.4, 0.5, 0.6, and 0.7 must declare these top-level bindings in addition to its stage-specific payload:

```json
{
  "stage": "A|B|C|0.4|0.5|0.6|0.7",
  "run_id": "<exact card-run run_id>",
  "base_main_commit_sha": "<exact locked main SHA>",
  "base_full_blob_sha": "<exact locked data/cards.full.json blob SHA>"
}
```

The three run/baseline values must exactly equal the subsequent `card-run.json`. `stage` is explicit and authoritative; bucket-name inference is not a production substitute. `0.2R`/`0.3R` never substitute for re-established B/C outputs. If any ordinary stage artifact lacks or mismatches these bindings, stop and regenerate/revalidate the affected stage chain before 0.8.

This envelope is the shared producer contract for the seven ordinary stage prompts and is machine-enforced by the formal card-run hardeners.

## 2. Baseline lock

Report and lock:

- current `main` HEAD SHA;
- `data/cards.full.json` blob SHA and count;
- `public/data/cards.json` count and projection consistency;
- current card-run/direct-add engine and schemas;
- active validators/workflows;
- open PRs that may affect canonical data, prompts, schemas, validators, governance, Related, source audit, stage lineage, or mutation engines.

Unmerged PRs and previous local copies are not baseline.

## 3. 0.0D preflight — active authority first

Open the current 0.0D prompt and follow `RUN_GOVERNANCE_INDEX.md` plus `DOCUMENT_UNIVERSE_POLICY.md`.

Inventory every `docs/**` path. Fully read every active canonical/validator/applicable-remediation dependency before 0.0C. Confirm superseded/reference/archived files are non-operative. Block unregistered active-looking documents, missing dependencies, or unresolved conflicts.

**Hard check:** active Stage A must report `selection_policy_version = EMBEDDED_NEWS_VALUE_SELECTION_V4`. No separate Structural News Value or Structural Value Override prompt may be required or applied.

## 4. Raw input audit

Audit schema/run metadata, story counts/statuses, usable text/source packets, date/region/source distribution, future/stale dates, exact/canonical URL duplicates, headline similarity, syndicated/cross-language same-event reporting, publication/event-date mismatch, source/body mismatch, malformed grouping, and cross-run story-ID collision risk.

Upstream labels are not final card decisions.

## 5. 0.0C coverage discovery

Before Stage A, independently search required regions/topics, current canonical follow-ups, corrections/reversals, reinforcement opportunities, and rescue-worthy filtered/held items. Discovery results are source candidates, not final evidence.

Every original and discovered item receives a terminal discovery disposition.

## 6. Expanded event universe and canonical reconciliation

Lock the current-run authoritative event universe. Cluster by event, not article. Compare against the complete canonical full for same event, reinforcement, update, distinct follow-up, correction/reversal, program lineage, and new unrelated event.

Do not infer Related from same actor/topic.

## 7. Stage A integrated news value + Related pre-pass

Run only the current Stage A prompt. It already contains the complete news-value policy and Related pre-pass.

For each strict/high-potential candidate preserve the four independent judgments, score/breakdown, anchor classes, selection route, before/after chain, baseline relation, Related candidates, evidence targets, and next confirmation points.

No web/body fetch in Stage A.

## 8. B/C, R, and lineage

Stage B verifies evidence and resolves relation/date/source questions before drafting. Stage C fact-safe red-teams and locks lineage for accepted new cards.

Use 0.2R only to repair a bounded Stage-B-owned defect, then re-establish B validity and return to C. Use 0.3R only to revalidate an authorized repaired item at Stage C and re-lock fact-safe lineage.

Do not use R to hide a coverage, selection, duplicate, staleness, or material event-identity defect. Route those defects to 0.0C/A/B/C as owned, then rerun all affected downstream gates.

`accepted_fact_safe` is not addable or publish-ready.

## 9. 0.4 addability

Recheck Stage C accepted cards against the exact latest canonical and current batch. 0.4 decides whether the already-lineage-audited card is still addable now; it does not create lineage for the first time.

## 10. 0.5–0.7C

Run evidence completeness, content polish, final publish readiness, then a separate completeness/news-value red team. A formal full run cannot enter 0.8 without 0.7C authorization.

A defect found here is routed to its earliest responsible stage. Do not create new ordinary 0.4R/0.5R/0.6R/0.7R prompt families.

## 11. 0.8 and merge

Use only declared `insert`, `update`, and `related_add` operations. Re-lock baseline, resolve provisional relation IDs, apply canonical mutation, regenerate lean from full, run active validators, inspect diff, and merge only after required checks/review.

## 12. 0.9

Verify new main and production counts/data/rendering/Related/deployment surfaces. Merge alone is not completion.

## 13. Direct-add boundary

If the user intentionally chooses an already-reviewed bounded direct add instead of a formal full run, stop claiming the formal stage ladder and use `MANUAL_DIRECT_ADD_V2`. New direct-added cards still require explicit news-value/editorial attestation and evidence review provenance.

## 14. First report before Stage A

Report:

A. current baseline and engine/workflow status;  
B. 0.0D active governance inventory/classification and PASS/blockers;  
C. raw input audit;  
D. 0.0C coverage findings and residual risks;  
E. authoritative event-universe counts/clusters;  
F. proposed Stage A queue by strict/reinforcement/update/follow-up/review/hold.

If gates pass, continue through the workflow without stopping for redundant confirmation.
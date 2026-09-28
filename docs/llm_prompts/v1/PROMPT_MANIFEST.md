# SBTL LLM Prompt Manifest V4.1

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_MANIFEST_V4_1_20260902`

## 1. Launcher

Ordinary new-news runs start with:

`docs/llm_prompts/v1/00_NEW_RUN_MASTER_PROMPT.md`

The run first creates a deterministic governance lock. Future named-stage prompts are locked at that time but loaded just in time, not all pre-read at startup.

## 2. Pipeline

```text
0.0D machine governance lock + bootstrap context
→ Input Audit
→ JIT 0.0C → expanded event universe lock → canonical/event reconciliation
→ JIT 0.1 A
→ JIT 0.2 B ⇄ JIT 0.2R bounded B repair when needed
→ JIT 0.3 C ⇄ JIT 0.3R controlled C revalidation when needed
→ JIT 0.4 → JIT 0.5 → JIT 0.6 → JIT 0.7 → JIT 0.7C → JIT 0.8
→ merge → JIT 0.9 → optional 1.0 → 1.1
```

0.2R and 0.3R are conditional repair loops. Downstream defects route to the earliest responsible stage; there are no ordinary 0.4R/0.5R/0.6R/0.7R prompt families.

## 3. Active named-stage prompts

| Stage | File | Complete role |
|---|---|---|
| 0.0D | `00D_PROMPT_0_0D_DOCUMENT_UNIVERSE_PREFLIGHT.md` | deterministic governance lock + bootstrap gate |
| 0.0C | `00C_PROMPT_0_0C_COVERAGE_DISCOVERY.md` | missing-news/follow-up/reinforcement/correction discovery |
| 0.1 | `01_PROMPT_0_1_Stage_A.md` | integrated news-value selector + Related pre-pass |
| 0.2 | `02_PROMPT_0_2_Stage_B_r0.md` | evidence/date/source/Related resolution + draft |
| 0.2R | `04_PROMPT_0_2R_Stage_B_Revise.md` | bounded B-owned evidence/date/source/draft repair, then return to C |
| 0.3 | `03_PROMPT_0_3_Stage_C_r0.md` | fact-safe red-team + lineage lock |
| 0.3R | `05_PROMPT_0_3R_Stage_C_Revise.md` | controlled fact-safe revalidation + lineage re-lock |
| 0.4 | `06_PROMPT_0_4_Baseline_Revalidation.md` | latest-baseline addability revalidation |
| 0.5 | `07_PROMPT_0_5_Evidence_QC.md` | evidence/source-claim completeness and freshness backstop |
| 0.6 | `08_PROMPT_0_6_Content_Polish.md` | content/terminology/strategic read-through |
| 0.7 | `09_PROMPT_0_7_Final_QC.md` | final publish-readiness gate |
| 0.7C | `09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md` | independent completeness/news-value challenge |
| 0.8 | `10_PROMPT_0_8_GitHub_Merge_Prep.md` | declared incremental mutation + merge prep |
| 0.9 | `11_PROMPT_0_9_Production_Verification.md` | main/live verification |
| 1.0 | `12_PROMPT_1_0_Remediation.md` | bounded defect routing/repair |
| 1.1 | `13_PROMPT_1_1_Retrospective.md` | retrospective and canonical rule promotion |
| 0.1P | `14_PROMPT_0_1P_Review_Pool_Promotion.md` | authorized review-pool promotion |

There is **no active 0.1S companion/override stage**.

## 4. Locked/JIT contract

`GOVERNANCE_LIFECYCLE_REGISTRY.json` registers the complete named-prompt set. `scripts/governance_lock_v4.mjs` binds each prompt path to the exact git blob at the run's locked `main` SHA.

Except for the 0.0D prompt in the bootstrap set, named prompts use `load_policy = jit_before_stage`.

Before executing a stage, load that prompt from the locked commit and verify its blob against the governance lock. Do not silently substitute a later `main` version.

## 5. Active canonical domains

Governed by `RUN_GOVERNANCE_INDEX.md`. Item news value is embedded in Stage A; portfolio news value/completeness is in `EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`; Related is in `RELATED_LIFECYCLE_CONTRACT.md`.

Active domain contracts are also blob-locked at 0.0D and loaded on demand when a stage explicitly requires them. Locking authority does not require placing every active body in model context before 0.0C.

## 6. No active patch assembly

No ordinary named prompt requires an active override, hardening addendum, overlay injection, or patch stub. Files retained with those historical names must be lifecycle-marked non-operative.

## 7. Compatibility contracts

Existing V3 machine schemas/validators may remain to validate historical and current compatibility fields until separately migrated. They do not create a second editorial authority and do not require retired V3 policy files to be read.

## 8. Mutation modes

- formal 0.8 card-run;
- governed `MANUAL_DIRECT_ADD_V2` for already-reviewed bounded changes.

These modes are mutually exclusive within one data PR.

## 9. Package validity

Invalid when the deterministic governance lock cannot be reproduced, a stage prompt path/blob does not match the lock, an active prompt depends on a later overlay/addendum, Stage A lacks embedded news value/Related pre-pass, R is used to launder a selection/event-identity defect, 0.4 is treated as first lineage creation, raw is treated as complete without 0.0C, 0.8 is authorized without 0.7C in a formal run, baseline is not current canonical full, or direct add fabricates full-run states.

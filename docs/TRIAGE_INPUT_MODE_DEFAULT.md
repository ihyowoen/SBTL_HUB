# TRIAGE Input Mode Default

> **Status: Legacy / exception mode.**
>
> The current default card-generation workflow is governed by `docs/PROMPT_ABC_DEFAULT_MODE.md`, which uses `final_news_llm_input.stories[]` as the primary input universe for the Final-input era.
>
> Use this document only when the user explicitly invokes the legacy `triage_output + rescue + dropped` mode or when processing older runs that were produced before the Final-input era workflow.
>
> If this document conflicts with `docs/PROMPT_ABC_DEFAULT_MODE.md`, follow `docs/PROMPT_ABC_DEFAULT_MODE.md` and the higher-level governance hierarchy defined there.

## Purpose

This document locks the legacy/exception input mode for older or explicitly requested card-generation runs.
It is not a one-off PR instruction.
It is an operating rule for recurring editorial workflow only when the legacy input mode is explicitly active.

This document locks **input discipline only**.
It does not redefine card field semantics or final production schema.
Those are governed by:
- `docs/PROMPT_ABC_DEFAULT_MODE.md`
- `docs/WORKFLOW.md`
- `docs/OPERATIONS.md`
- `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md`

---

## 1. Legacy Input Set

When the legacy mode is explicitly invoked, the input set is:

- `triage_output`
- `rescue`
- `dropped`

### Interpretation
- `triage_output` = primary working input
- `rescue` = rescue-only auxiliary input
- `dropped` = treasure-hunt / salvage pool

This is not the current Final-input era default. It is the legacy/exception operating set.

---

## 2. Candidate Unit

In legacy mode, the primary candidate unit remains:
- `kept_clusters[]` from `triage_output`

This means the legacy workflow follows the original direct-input logic:
- primary source = `triage_output`
- primary candidate unit = `kept_cluster`

`rescue` and `dropped` are auxiliary review pools, not replacements for the main working unit.

---

## 3. Why `dropped` Is Included in Legacy Mode

`dropped` must not be treated as a dead bin.

It is a treasure-hunt / salvage pool used to recover:
- wrongly excluded candidates
- parser-damaged candidates
- date-contaminated candidates
- under-selected candidates
- weak-gate false negatives

Operationally:
- `dropped` is reviewed by default in legacy-mode runs
- `dropped` is not an afterthought
- `dropped` is a structured salvage pool

---

## 4. Why `rescue` Is Included in Legacy Mode

`rescue` is the structured auxiliary pool for candidates that should be reconsidered outside the primary `kept_clusters[]` flow.

Operationally:
- `rescue` is rescue-only auxiliary input
- it is not the main working source
- it is used to pull back candidates that merit editorial reconsideration

---

## 5. Debugging-Only Exception Inputs

The following inputs are not part of the legacy run set:

- `collector`
- `refined`

Use them only for debugging and upstream diagnosis, such as:
- upstream omission tracing
- parser/date contamination investigation
- gate/source-policy failure diagnosis
- collector recall audit
- refined precision audit

They are exception inputs, not standard run inputs.

---

## 6. Baseline Rule

Current cards baseline is always:
- GitHub `main` `public/data/cards.json`

### Hard rules
- never use uploaded `cards.json` as baseline
- never use helper payload files as baseline
- helper payloads are working artifacts only

---

## 7. A/B/C Structure Remains Unchanged

This legacy input mode does **not** replace the current A/B/C architecture.
It only describes how older `triage_output + rescue + dropped` inputs are interpreted when that mode is explicitly invoked.

### Prompt A = Card Spec Builder
- processes every `kept_cluster`
- reviews `rescue` and `dropped`
- salvage / discard / merge are allowed only here
- assigns category / signal / representative source / representative date
- compares candidates against GitHub `main` `public/data/cards.json`

### Prompt B = Insight Writer
- writes every passed spec
- does not discard
- does not merge
- does not change category / signal / representative date

### Prompt C = Enhanced Red Team + Cross-Functional Validator + Formatter
- reviews every card draft
- tightens / validates / formats
- must not silently discard
- must not silently merge
- final production output is **full schema only**

---

## 8. Zero Omission Rule

Zero Omission is enforced at:
- cluster level
- spec level
- card level

Meaning in legacy mode:
- Prompt A must process every `kept_cluster`
- Prompt B must write every passed spec
- Prompt C must review every card draft

No silent loss is allowed.

---

## 9. Short Operating Declaration

```text
Operating Mode: legacy triage_output + rescue + dropped mode

- current default is governed by docs/PROMPT_ABC_DEFAULT_MODE.md
- use this mode only when explicitly invoked or processing older runs
- triage_output = primary working input
- rescue = rescue-only auxiliary input
- dropped = treasure-hunt / salvage pool
- kept_clusters[] from triage_output = primary candidate unit
- cards baseline = GitHub main public/data/cards.json
- helper payloads = working artifacts, not baseline
- collector/refined = debugging-only exception inputs
- discard/merge allowed only in Prompt A
- Prompt B must write every passed spec
- Prompt C must review every card draft and must not silently discard
- Prompt C final production output = full schema only
```

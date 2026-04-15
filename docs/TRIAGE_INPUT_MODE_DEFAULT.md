# TRIAGE Input Mode Default

## Purpose

This document locks the durable default input mode for future card-generation runs.
It is not a one-off PR instruction.
It is an operating rule for recurring editorial workflow.

This document should be read together with:
- `docs/CARD_WORKFLOW_VFINAL.md`
- `docs/OPERATIONS.md`
- `docs/CARD_WORKFLOW_VFINAL_ADDENDUM_20260407.md`
- `docs/OPERATIONS_CARD_EXECUTION_ADDENDUM_20260407.md`

---

## 1. Default Input Set

The default input set for future runs is:

- `triage_output`
- `rescue`
- `dropped`

### Interpretation
- `triage_output` = primary working input
- `rescue` = rescue-only auxiliary input
- `dropped` = treasure-hunt / salvage pool

This is the standard operating set.

---

## 2. Candidate Unit

The primary candidate unit remains:
- `kept_clusters[]` from `triage_output`

This means the workflow still follows the original direct-input logic:
- primary source = `triage_output`
- primary candidate unit = `kept_cluster`

`rescue` and `dropped` are auxiliary review pools, not replacements for the main working unit.

---

## 3. Why `dropped` Is Included by Default

`dropped` must not be treated as a dead bin.

It is a treasure-hunt / salvage pool used to recover:
- wrongly excluded candidates
- parser-damaged candidates
- date-contaminated candidates
- under-selected candidates
- weak-gate false negatives

Operationally:
- `dropped` is reviewed by default in every run
- `dropped` is not an afterthought
- `dropped` is a structured salvage pool

---

## 4. Why `rescue` Is Included by Default

`rescue` is the structured auxiliary pool for candidates that should be reconsidered outside the primary `kept_clusters[]` flow.

Operationally:
- `rescue` is rescue-only auxiliary input
- it is not the main working source
- it is used to pull back candidates that merit editorial reconsideration

---

## 5. Debugging-Only Exception Inputs

The following inputs are not part of the default run set:

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

This default input mode does **not** replace the original A/B/C architecture.
It preserves it.

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

---

## 8. Zero Omission Rule

Zero Omission is enforced at:
- cluster level
- spec level
- card level

Meaning:
- Prompt A must process every `kept_cluster`
- Prompt B must write every passed spec
- Prompt C must review every card draft

No silent loss is allowed.

---

## 9. Short Operating Declaration

```text
Operating Mode: triage_output + rescue + dropped default mode

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
```

---

## 10. Final Principle

Keep the original A/B/C design as the governing workflow.
Only the durable default input set is being locked here.

That durable default input set is:
- `triage_output`
- `rescue`
- `dropped`

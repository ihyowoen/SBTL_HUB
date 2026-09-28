# Document Universe Policy V2.1

**Status:** `ACTIVE_CANONICAL`  
**Version:** `DOCUMENT_UNIVERSE_POLICY_V2_1_20260902`

## 0. Goal

Prevent both failures:

- missing an active rule because only a remembered core list was used;
- forcing an LLM to pre-load the entire active governance universe and then self-attest that it read everything.

The repository, not model memory, defines the authority universe.

## 1. Inventory is universal; authority is machine-locked

Stage 0.0D must inventory every path under `docs/**` from the locked repository state.

Lifecycle is derived from the locked lifecycle registry. Permitted classes include:

- `ACTIVE_CANONICAL`;
- `ACTIVE_NAMED_PROMPT`;
- `ACTIVE_VALIDATOR_CONTRACT`;
- `OPEN_REMEDIATION`;
- `ACTIVE_MIGRATION`;
- `SUPERSEDED`;
- `REFERENCE_ONLY`;
- completed/archived non-operative classes when explicitly registered.

Every path is classified; no file silently disappears.

For every active authority, the deterministic governance-lock helper records the exact git blob SHA. This is the authority proof for the run.

## 2. Bootstrap context before 0.0C

The lifecycle registry contains `bootstrap_read[]`.

After deterministic 0.0D verification and before executing 0.0C, load only that exact small set. The bootstrap set contains the workflow/index/policy/launcher/preflight documents needed to begin safely.

The machine artifact proves the bootstrap **path set and locked versions**, not whether a model cognitively consumed those files. Bootstrap loading is an operator/model transition obligation and must not be represented as a machine-proven read count.

Do not convert the entire locked authority set into a pre-0.0C context requirement.

## 3. Just-in-time named-stage prompts

Every active named-stage prompt is locked at 0.0D but is loaded immediately before its stage executes.

The operator/model must:

1. use the path registered in the lock;
2. load it from the locked `repository_head_sha`;
3. verify its git blob equals the lock entry;
4. execute that prompt as the complete stage contract.

A future-stage prompt is not required context for an earlier stage merely because it is active.

## 4. Other active canonical/validator authority

Active canonical domain contracts, validator contracts, open remediations, and activated migrations are also blob-locked at 0.0D.

They are loaded on demand when the current stage explicitly requires them, when a validator invokes them, or when a conflict/remediation question requires inspection. Their authority is fixed from the start even when their bodies are not all placed in the model context at once.

## 5. Historical/reference treatment

When a file is authoritatively registered `SUPERSEDED`, `REFERENCE_ONLY`, completed, or archived, 0.0D classifies it without deep-reading its historical body. It remains auditable but non-operative.

If lifecycle registration is missing, duplicated, contradictory, or a registered path is missing from the locked tree, block rather than guess.

## 6. No late authority

After 0.0D PASS, no later-read document may become a different authority version during the run. All operative loads must reproduce the locked path/blob.

If `main` changes and the run intentionally adopts the new governance state, re-lock the baseline and re-run 0.0D plus every affected downstream gate.

## 7. No active patch assembly

Ordinary active governance must not require runtime assembly of:

- append-this-override-later;
- hardening addenda;
- prompt overlay injection;
- patch stubs that supersede a portion of a named prompt.

Recurring rules belong in clean active canonical/named-stage documents.

## 8. Read-attestation prohibition

A model-generated count is not evidence that a document was read.

New V4.1 runs must not authorize 0.0C using `active_full_read_count`, a handwritten list of claimed reads, or an excerpt/hash ledger generated solely from self-report. The machine authorization object is the deterministic `governance_lock` replayed against the locked git tree.

Legacy-named compatibility fields may remain in the generated artifact, but they describe machine inventory/classification state and must not be interpreted as cognitive-read proof.

No machine PASS field claims that bootstrap or JIT prompt content was cognitively read. Those loads are explicit execution steps.

## 9. 0.0D exit

Machine 0.0D PASS requires:

- repository SHA and canonical full blob locked;
- deterministic governance lock generated and replay-verified;
- every `docs/**` path classified;
- every active authority bound to its exact blob SHA;
- exact bootstrap-context path set fixed in the lock;
- active override/addendum count zero;
- Stage A embedded policy verified;
- no unclassified/missing/duplicate lifecycle entry;
- no unresolved active-authority blocker;
- repository-state preflight eligible for Stage 0.0C.

After machine PASS, the operator/model must load the declared bootstrap context before actually executing 0.0C. That transition is required behavior, not a machine read-attestation.

Otherwise stop with `BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE_OR_CONFLICTED`.

# Document Universe Policy V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `DOCUMENT_UNIVERSE_POLICY_V2_20260829`

## 0. Goal

Prevent both failures:

- missing an active rule because only a remembered core list was read;
- allowing historical/reference material to override a run because every old document was treated as equally operative.

## 1. Inventory is universal; deep-read is applicability-driven

Stage 0.0D must inventory **every** path under `docs/**` from the locked repository state.

For each file determine lifecycle from the governance registry and authoritative header. Permitted lifecycle classes include:

- `ACTIVE_CANONICAL`
- `ACTIVE_VALIDATOR_CONTRACT`
- `OPEN_REMEDIATION`
- `ACTIVE_MIGRATION`
- `SUPERSEDED`
- `REFERENCE_ONLY`
- `COMPLETED_REFERENCE`
- `ARCHIVED`

Every file is classified; no file silently disappears.

## 2. Mandatory full-read set

Before 0.0C, fully read or completely parse:

- every `ACTIVE_CANONICAL` file;
- every `ACTIVE_VALIDATOR_CONTRACT` required by the run path;
- every applicable `OPEN_REMEDIATION`;
- every explicitly activated migration;
- every direct dependency referenced by those active files;
- the current named-stage prompt immediately before executing that stage.

## 3. Historical/reference treatment

When a file is authoritatively registered/header-marked `SUPERSEDED`, `REFERENCE_ONLY`, `COMPLETED_REFERENCE`, or `ARCHIVED`, 0.0D may classify it from lifecycle metadata without deep-reading its historical body. It remains discoverable for audit but is non-operative.

If lifecycle metadata is missing, contradictory, or the file appears to contain an active instruction, block and inspect the file rather than guessing.

## 4. No late authority

After 0.0D PASS, a historical/reference file cannot later become an ordinary-run rule merely because it was opened. New active authority requires a repository governance change and a new preflight/rebase as applicable.

## 5. No active patch assembly

Ordinary active governance must not require:

- append-this-override-later;
- hardening addenda;
- prompt overlay injection;
- patch stubs that supersede a portion of a named prompt at runtime.

Recurring rules are integrated into clean active canonical/named-stage documents.

## 6. 0.0D exit

Required:

- repository SHA locked;
- all `docs/**` paths inventoried;
- lifecycle classification complete;
- active dependency closure fully read/parsed;
- unread active files = 0;
- unclassified files = 0;
- unresolved dependencies/conflicts = 0;
- unregistered active-looking files = 0;
- applicable remediation/migration dispositioned;
- Stage 0.0C authorized.

Otherwise stop with `BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE_OR_CONFLICTED`.
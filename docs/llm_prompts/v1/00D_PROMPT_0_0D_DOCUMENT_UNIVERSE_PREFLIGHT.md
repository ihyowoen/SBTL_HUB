# Prompt 0.0D — Deterministic Governance Lock + Bootstrap Preflight V4.1

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_0D_V4_1_20260902`

## Purpose

Bind the run to the complete governance universe at the locked GitHub `main` commit **without asking the LLM to pretend it has deep-read every active file**.

0.0D has two separate responsibilities:

1. **machine lock** — deterministically inventory/classify `docs/**`, lock every active authority to a git blob SHA, and prove the registry/baseline is internally consistent;
2. **bootstrap context** — read only the small registry-declared `bootstrap_read[]` set needed to begin the run safely.

All other active authority remains locked and auditable but is loaded only when the current stage explicitly needs it. Every named-stage prompt is loaded **just in time from the locked commit**, never from a later moving `main`.

## Required input

- current GitHub `main` HEAD SHA;
- current `data/cards.full.json` blob SHA;
- current repository git history/tree;
- `docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json` at that locked SHA.

## 1. Mandatory machine-generated 0.0D artifact

Do **not** hand-author the PASS artifact and do not calculate counts from memory.

Generate it from the locked git tree:

```bash
node scripts/governance_lock_v4.mjs \
  --emit \
  --base-main-sha <LOCKED_MAIN_SHA> \
  --base-full-blob-sha <LOCKED_FULL_BLOB_SHA> \
  --output <RUN_DIR>/stage_0_0d.json
```

Then verify the exact artifact by replaying the locked commit:

```bash
node scripts/governance_lock_v4.mjs \
  --verify \
  --base-main-sha <LOCKED_MAIN_SHA> \
  --base-full-blob-sha <LOCKED_FULL_BLOB_SHA> \
  --artifact <RUN_DIR>/stage_0_0d.json
```

A count-only artifact, including one that merely states `active_full_read_count = <registry closure size>`, is not valid evidence and must not authorize 0.0C.

## 2. What the machine lock proves

The deterministic helper derives these facts from the exact locked commit:

- complete `docs/**` inventory;
- one lifecycle classification for every `docs/**` path registered by the current lifecycle registry;
- exact active-authority set;
- exact git blob SHA for every locked active authority;
- exact registry blob SHA;
- classification digest;
- exact bootstrap-read set;
- active named prompts marked `jit_before_stage` unless they belong to bootstrap;
- no active override/addendum runtime dependency;
- Stage A contains `EMBEDDED_NEWS_VALUE_SELECTION_V4` and `related_prepass`;
- exact `data/cards.full.json` baseline blob binding.

`governance_lock.lock_sha256` binds the complete lock payload. Changing a path, blob SHA, lifecycle, load policy, baseline SHA, or registry state requires a new lock.

## 3. Bootstrap read — the only mandatory pre-0.0C LLM read set

After the machine lock verifies, fully read the exact `bootstrap_read_paths` emitted in the artifact. That list is registry-derived and intentionally much smaller than the full locked authority set.

The bootstrap set must include:

- `docs/WORKFLOW.md`;
- `docs/OPERATIONS.md`;
- `docs/DOCUMENT_UNIVERSE_POLICY.md`;
- `docs/RUN_GOVERNANCE_INDEX.md`;
- `docs/llm_prompts/v1/PROMPT_MANIFEST.md`;
- `docs/llm_prompts/v1/00_NEW_RUN_MASTER_PROMPT.md`;
- this 0.0D prompt;
- the lifecycle registry.

Do not pre-load every future Stage B/C/0.4/0.5/0.6/0.7/0.8/0.9 prompt merely to satisfy a count.

## 4. Just-in-time named-stage rule

Before executing a named stage:

1. locate that prompt in `governance_lock.locked_authorities`;
2. require its `load_policy` to be `jit_before_stage` or `bootstrap`;
3. load the prompt from `repository_head_sha`, not from a later branch tip;
4. verify the loaded file's git blob SHA equals the locked `blob_sha`;
5. only then execute the stage.

If the prompt path/blob cannot be reproduced from the lock, stop and re-run 0.0D against the intended baseline.

A later `main` change never silently changes an in-progress run.

## 5. Historical/reference treatment

`SUPERSEDED`, `REFERENCE_ONLY`, archived, and completed historical material is inventory/classification evidence, not an ordinary-run rule. It is not deep-read merely because it exists.

If the deterministic inventory finds an unclassified path, a missing registered path, duplicate lifecycle registration, non-zero active override/addendum count, or other registry inconsistency, 0.0D is BLOCKED.

## 6. Compatibility field semantics

Several legacy-named fields remain in the machine-generated artifact for current engine compatibility. In V4.1 they are **machine-state fields, not cognitive-read attestations**:

- `all_docs_files_read_or_parsed = true` means the deterministic helper completed the required git-tree inventory/classification/blob-lock parse. It does **not** claim that an LLM deep-read every active body.
- `unread_active_paths = []` is a compatibility mirror for active authority omitted from the deterministic lock. It is not evidence of LLM reading.
- `active_full_read_count` is no longer an authorization field and should not be emitted by new V4.1 artifacts.
- `locked_authority_count` is the number of active authorities cryptographically bound to the run.
- `bootstrap_read_count` is the small context set the operator/model reads before 0.0C.

The production gate requires a valid `governance_lock`; legacy count-only self-attestation is rejected.

## 7. Required output

The canonical 0.0D artifact is generated by `scripts/governance_lock_v4.mjs`. Its essential shape is:

```json
{
  "stage": "0.0D",
  "status": "PASS",
  "repository_head_sha": "<locked main>",
  "canonical_full_blob_sha": "<locked full blob>",
  "docs_inventory_count": 0,
  "classified_count": 0,
  "locked_authority_count": 0,
  "bootstrap_read_count": 0,
  "bootstrap_read_paths": [],
  "active_canonical_paths": [],
  "active_validator_contract_paths": [],
  "applicable_remediation_or_migration": [],
  "superseded_or_reference_paths": [],
  "unclassified_paths": [],
  "unread_active_paths": [],
  "unresolved_dependencies": [],
  "unresolved_conflicts": [],
  "unregistered_active_looking_paths": [],
  "active_override_or_addendum_count": 0,
  "stage_a_embedded_news_value_verified": true,
  "all_docs_files_read_or_parsed": true,
  "unresolved_rule_conflicts": [],
  "incomplete_universe_defects": [],
  "stage_0_0c_authorized": true,
  "governance_lock": {
    "schema": "governance_lock_v1",
    "registry_blob_sha": "",
    "classification_digest_sha256": "",
    "locked_authority_count": 0,
    "bootstrap_read_count": 0,
    "bootstrap_read_paths": [],
    "locked_authorities": [],
    "lock_sha256": ""
  }
}
```

## 8. PASS / BLOCKED rule

PASS requires:

- deterministic `--verify` success against the exact locked `main` and canonical full blob;
- complete docs classification with no missing/unclassified registered paths;
- exact active authority/blob lock;
- exact registry bootstrap set;
- zero active override/addendum runtime dependencies;
- Stage A embedded news-value/Related contract verified;
- all blocker arrays empty;
- the bootstrap set actually loaded before 0.0C.

The machine artifact proves repository state. The model must never manufacture a larger read count as a substitute for repository evidence.

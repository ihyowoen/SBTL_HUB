# Manual Direct Add V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `MANUAL_DIRECT_ADD_V2_20260901`

## 1. Purpose

`manual_direct_add_v2` is the governed path for bounded card mutations when the editorial/evidence review has already been completed outside the formal Stage A/B/C artifact chain.

It is not a shortcut that fabricates missing stage states. A V2 PASS means the declared direct-add review and mutation contract passed; it does **not** mean Stage A/B/C, Prompt 0.7C, or formal Prompt 0.8 ran.

Use for:

- one or more intentionally direct-added, already-reviewed cards;
- bounded evidence/reinforcement/correction updates to existing cards;
- one-to-one Story ID / representative-event-date / region identity correction.

## 2. Required PR shape

A direct-add data PR contains exactly:

- `data/cards.full.json`;
- `public/data/cards.json`;
- one `direct-adds/<batch>/direct-add.json`.

Formal card-run, direct-add, and dedicated migration modes are mutually exclusive in one data PR.

## 3. Manifest core

The manifest locks:

- exact base `main` commit SHA;
- exact base canonical full blob SHA;
- before/after counts;
- output timestamp;
- declared `add`, `update`, and `id_migration` scope;
- `review_mode = already_reviewed_bounded_direct_add`;
- `formal_full_run_claimed = false`.

Only `manual_direct_add_v2` is accepted by the active production validator. V1 manifests are historical/audit-only.

## 4. Editorial attestation for every direct-added card

Every `operations.add` ID has exactly one attestation containing:

- `execution_credibility_gate = PASS`;
- `independent_cardability_gate = PASS`;
- at least one valid anchor class;
- `selection_route = execution_anchor_route|structural_non_execution_route`;
- decision-news-value score and classification;
- publication urgency;
- `prior_state`, `new_verified_fact`, `changed_judgment`;
- evidence-review summary;
- next confirmation points;
- inclusion decision.

This is an attestation that the review occurred; it is not a fabricated Stage A artifact.

### Standard inclusion

`standard_include` requires decision-news-value score >= 55.

### Owner override inclusion

A deliberately included lower-value card is allowed only as `owner_override_include` with a non-empty item-specific `owner_override_reason`. This preserves user editorial authority without hiding that the standard score threshold was overridden.

### Route/anchor correlation

`execution_anchor_route` requires `execution_event_anchor`.

`structural_non_execution_route` must not claim `execution_event_anchor`; it requires at least one non-execution anchor plus non-empty `structural_non_execution_reason` and `why_execution_event_not_required`.

### Direct-add provenance and Related boundary

A direct-added card must start with `related[]` empty (and `related_ids[]` empty when that compatibility field exists). A direct-add manifest does not carry the predecessor evidence, relation type, fresh-anchor review, and lineage lock required to create a production Related edge. Establish any new relation through the formal Related lifecycle after the card exists.

A direct-added card must not contain formal-run state/provenance fields such as `stage_a_validity_status`, `stage_b_validity_status`, `stage_c_validity_status`, `final_qc_status`, `merge_status`, or `pipeline_lineage`. `formal_full_run_claimed=false` and the published card must tell the same audit story.

## 5. Update attestation and identity guard

Every `operations.update` ID has exactly one bounded update attestation with:

- `change_type = reinforcement|correction|evidence_update|content_correction`;
- exact `changed_fields[]`;
- item-specific reason;
- evidence-review summary.

The validator recomputes the actual before/after top-level changed fields and requires exact equality with `changed_fields[]`. An update must preserve the existing card ID, representative date, region, and production `related[]`; date/ID/region correction uses `id_migration`, and relation changes use the governed relation path.

Every update must preserve both stable event identity and at least one durable event anchor from the existing title/source URL/fact-source URL/event fingerprint set. A declaration cannot reuse an old ID while replacing the represented event.

Additional update-type boundaries:

- `evidence_update` may not change visible event fields or `event_fingerprint`;
- `reinforcement` may add/strengthen evidence and bounded fact/context, but may not change title/taxonomy/signal/event fingerprint;
- `content_correction` may repair visible wording but may not change taxonomy/event fingerprint;
- `correction` is the broadest update type, but the immutable-field and stable-event-anchor checks still apply.

Updates do not require an artificial new-card news-value score.

## 6. ID migration

`id_migration` is one-to-one and count-neutral. The validator requires the old ID to disappear, the new ID to appear, and stable identity evidence to remain. Migration reason must be explicit.

A migration is an **identity correction, not a content-update bypass**. The replacement card may differ only in `id`, `date`, and `region`. URLs, facts, title, taxonomy, evidence, event fingerprint, Related state, and every other top-level content/audit field must remain byte-equivalent at the JSON-value level. If content also needs correction, perform that as a separately governed operation rather than hiding it inside `id_migration`.

## 7. What CI proves

The production direct-add gate proves:

1. manifest baseline equals the PR base main/full blob;
2. lost and introduced IDs exactly match declared migration/add scope;
3. declared updates exist before/after and their actual changed fields exactly match the attestation;
4. update identity/immutable-field/type-specific boundaries are preserved;
5. no undeclared existing card changed;
6. each added/updated card has exactly one required V2 attestation;
7. score/classification/route/override rules are internally coherent;
8. ID migration is restricted to `id`/`date`/`region` identity correction and cannot replace event content;
9. direct-added cards contain no unaudited Related edge;
10. direct-added cards contain no fabricated formal-run state/provenance;
11. no new dangling Related edge is introduced;
12. counts and output timestamp match;
13. lean is the deterministic projection of full through the existing repository checks.

For a declared ID migration only, the existing card-deletion guard may be enabled after the direct-add validator proves the exact one-to-one migration.

## 8. Boundary

Use the formal card-run when the publication claim depends on formal Stage A/B/C/0.7C/0.8 artifacts. Use V2 when those stage claims are not being made and the remaining task is an explicitly reviewed bounded mutation.
# Manual Direct Add V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `MANUAL_DIRECT_ADD_V2_20260829`

## 1. Purpose

`manual_direct_add_v2` is the governed path for bounded card mutations when the editorial/evidence review has already been completed outside the formal Stage A/B/C artifact chain.

It is not a shortcut that fabricates missing stage states. A V2 PASS means the declared direct-add review and mutation contract passed; it does **not** mean Stage A/B/C, Prompt 0.7C, or formal Prompt 0.8 ran.

Use for:

- one or more intentionally direct-added, already-reviewed cards;
- bounded evidence/reinforcement/correction updates to existing cards;
- one-to-one Story ID / representative-event-date correction.

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

### Structural non-execution route

When no conventional execution event is required, both `structural_non_execution_reason` and `why_execution_event_not_required` are mandatory and must explain why the verified policy/data/financial/strategic/technology/follow-up change is independently decision-useful.

## 5. Update attestation

Every `operations.update` ID has exactly one bounded update attestation with:

- update type;
- item-specific reason;
- evidence-review summary.

Updates do not require an artificial new-card news-value score.

## 6. ID migration

`id_migration` is one-to-one and count-neutral. The validator requires the old ID to disappear, the new ID to appear, and stable identity evidence to remain. Migration reason must be explicit.

## 7. What CI proves

The validator proves:

1. manifest baseline equals the PR base main/full blob;
2. lost and introduced IDs exactly match declared migration/add scope;
3. declared updates exist before/after and actually changed;
4. no undeclared existing card changed;
5. each added/updated card has exactly one required V2 attestation;
6. score/classification/route/override rules are internally coherent;
7. ID migration keeps stable identity evidence;
8. no new dangling Related edge is introduced;
9. counts and output timestamp match;
10. lean is the deterministic projection of full through the existing repository checks.

For a declared ID migration only, the existing card-deletion guard may be enabled after the direct-add validator proves the exact one-to-one migration.

## 8. Boundary

Use the formal card-run when the publication claim depends on formal Stage A/B/C/0.7C/0.8 artifacts. Use V2 when those stage claims are not being made and the remaining task is an explicitly reviewed bounded mutation.
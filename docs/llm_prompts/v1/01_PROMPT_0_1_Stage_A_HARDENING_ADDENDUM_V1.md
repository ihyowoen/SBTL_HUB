# Prompt 0.1 Stage A Hardening Addendum V1

Base prompt blob: `a96290f9de4ca5f65e94807893a75f807bc66c60`
Integrity override: `00_DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_V1.md`
Integrity override SHA-256: `6d3cd9e6dcf7ad47801ef587f25633ec849a2108a9b9f6aa8b775076206ec05d`

## Required per-story output

Every decision-ledger row must add:

- `raw_region`
- `resolved_event_region`
- `region_resolution_basis`
- `date_role_audit`
- `story_id_lineage_audit`
- `baseline_relation_type`
- `baseline_target_card_ids[]`
- `related_candidate_generation_status`

## Strict-pass date gate

A strict item must have:

- a non-null `event_date_candidate`;
- an explicit `event_date_basis`;
- a separately recorded `source_published_date`;
- no future-date or day/month parsing anomaly;
- no unresolved event/source contradiction.

Failure status: `BLOCKED_DATE_ROLE_AMBIGUITY`.

## Story-ID gate

Story ID may be carried as discovery lineage only. A cross-run match that lacks
URL/event-fingerprint support must be recorded as a collision and ignored for
duplicate routing.

## Related gate

Stage A nominates related candidates only. It must not edit production
`related[]`. Generic similarity is prohibited.

## Required summary fields

- `date_role_anomaly_count`
- `date_role_strict_block_count`
- `story_id_cross_run_match_count`
- `story_id_collision_count`
- `story_id_trusted_identity_match_count`
- `related_candidate_nomination_count`
- `related_candidate_target_missing_count`

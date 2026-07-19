<!-- AUTHORITATIVE_OVERRIDE: DATE_STORYID_RELATED_INTEGRITY_V1 -->
<!-- Generated KST: 2026-07-19T19:46:57.266558+09:00 -->
<!-- Applies from Stage A through Prompt 0.9 -->

# Date · Story-ID · Related Integrity Override — V1

## 0. Authority and scope

This override supplements the current GitHub-main workflow prompts and
supersedes conflicting language only for:

1. date-role separation;
2. story-ID trust and cross-run collision handling;
3. baseline relationship and related-card lineage;
4. search-before-delete handling for unresolved lineage;
5. downstream replay of these integrity checks.

It does not weaken Fact Discipline, source verification, the state ladder,
duplicate screening, or publish-readiness requirements.

Every affected artifact must record:

- `integrity_override_file`
- `integrity_override_sha256`
- `integrity_override_status: PASS`
- `date_role_separation_status`
- `story_id_lineage_audit_status`
- `related_lineage_audit_status`

## 1. Three date roles — HARD RULE

The following dates are distinct and must never be silently substituted:

- `event_date`: date of the underlying event, decision, release, start,
  approval, commissioning, transaction, dataset release, or other card anchor.
- `source_published_date`: date the article, filing, report, notice, or official
  material was published.
- `discovery_or_ingestion_date`: date the pipeline found or ingested the source.

`fetched_at` and `checked_at` are audit timestamps only.

### 1.1 Permitted event-date bases

- explicit event date in current-run upstream text;
- official release/data publication date when the release itself is the event;
- verified source date at Stage B or later;
- active baseline event date for an exact same-event reinforcement.

### 1.2 Hard blockers

Block strict-pass or downstream advancement when:

- a future publication date is caused by day/month reversal or parser error;
- `event_date` is populated only from ingestion date;
- event and source dates conflict without an explanation;
- a material project, policy, contract, production, or data-release date is
  unresolved;
- production ID date prefix disagrees with the final locked event date.

Stage A status: `BLOCKED_DATE_ROLE_AMBIGUITY`.
Final-QC status: `FINAL_QC_EVENT_SOURCE_DATE_CONTRADICTION`.

## 2. Story ID is untrusted lineage — HARD RULE

`story_id` is not identity evidence and is never sufficient for duplicate,
reinforcement, merge, or related decisions.

A cross-run story-ID match is valid only when at least one identity route also
passes:

- exact or canonical URL;
- same actor + project/asset/policy + event type;
- same factual anchor and compatible event date;
- independently verified same-event fingerprint.

Otherwise record:

- `story_id_collision_detected: true`
- `story_id_match_trusted: false`
- `story_id_collision_reason`
- `duplicate_decision_ignored_story_id: true`

Never redirect a candidate to an unrelated baseline card because the same
story ID was reused.

## 3. Baseline relation taxonomy

Every current-run item must receive exactly one relation:

- `new_distinct_event`
- `exact_duplicate`
- `same_event_additional_source`
- `existing_reinforcement`
- `same_event_follow_up`
- `same_project_stage_progression`
- `same_policy_execution_lineage`
- `same_company_technology_execution_lineage`
- `context_only`
- `unresolved_relation`

Stage A may nominate related candidates but must not mutate production
`related[]`.

## 4. Related candidate rule

A `related_candidate_id` is allowed only for a factual lineage:

- same event;
- same named project or asset at another execution stage;
- same policy from proposal through implementation/enforcement;
- same company and technology with a concrete execution progression;
- same market dataset series where the new release changes the prior judgment.

Generic sector, country, chemistry, or company similarity is insufficient.

Every nomination must include:

- `target_card_id`
- `relation_type`
- `reason`
- `target_exists_active`
- `confidence: high|moderate`
- `production_related_mutation_authorized: false`

Unresolved historical related references must not be deleted merely because the
target is currently absent. Search lineage first and preserve the unresolved ID
until the user authorizes deletion or a confirmed replacement is found.

## 5. Search-before-delete

Weak, ambiguous, inaccessible, date-conflicted, or lineage-conflicted items are
verification triggers, not automatic deletion grounds.

At Stage A, where web search is prohibited, route a material unresolved item to
candidate review with a bounded rescue question. At later authorized stages,
perform bounded search before hold/reject/delete.

## 6. Downstream replay

- Prompt 0.5 builds atomic claim-to-quote coverage and a date-alignment audit.
- Prompt 0.6 invalidates and rebuilds coverage hashes after visible-field edits.
- Prompt 0.7 independently replays claims, quotes, dates, and event stage.
- Prompt 0.8 locks final event date before assigning ID, validates all related
  targets, retires superseded IDs, and re-sorts.
- Prompt 0.9 recomputes all integrity checks from merged main and production;
  upstream PASS flags are not accepted as substitutes for recomputation.

# Prompt 0.3R — Stage C Controlled Revalidation V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `STAGE_C_REVISE_V4_20260829`

Revalidate only authorized revised items. Confirm the specific defect was repaired without unsupported facts, route drift, date drift, source-audit drift, or lineage loss. Re-lock `related_lineage` for accepted items. Same-event duplicate/reinforcement/unresolved relation cannot become a new accepted card.

Outcomes: accepted_fact_safe, revise_required_again within allowed loop, rejected/support-only/deferred, or upstream return for selection/event-identity defect. Emit repair audit, route validation, lineage lock, source/date checks, accounting, and prompt provenance.
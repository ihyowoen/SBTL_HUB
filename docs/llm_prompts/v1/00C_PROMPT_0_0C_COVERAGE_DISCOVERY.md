# Prompt 0.0C — Coverage Discovery & Completeness V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_0C_V4_20260901`

## Purpose
Challenge the supplied raw universe before Stage A. Find missing material events, meaningful follow-ups, corrections/reversals, and reinforcement opportunities.

## Entry gate
Require 0.0D PASS and exact current baseline lock. Bind this artifact to the exact 0.0D manifest and canonical full blob used by the run.

## Search universe
Review supplied raw input, current canonical full, trackers/watchlists/review pools/holds, material existing-card lineages, official sources, and reputable independent reporting.

Required regions: Korea, North America, China, Japan, Europe, material global markets.

Required topics: cells/chemistries, materials/components, pouch/pouch-film demand signals, ESS/BESS, EV/charging, manufacturing/capacity/utilisation, grid/AI-data-centre power, critical minerals/refining, recycling, policy/trade/sanctions/subsidies/localisation, competitors/customers, prices/costs/margins, financing, safety/recall/commissioning/operation.

## Existing-card challenge
For material canonical events, test new stage, legal effect, financing, scale, timing, customer/supplier, economics, technology maturity, risk, earnings contribution, delay/reduction/suspension/cancellation, and correction/reversal. A later article date is not a follow-up.

## Discovery boundary
Web findings are source candidates, not final evidence. Do not draft cards or declare fact safety.

## Production artifact bindings
The output artifact must be directly consumable by the production card-run engine:

- `document_universe_manifest_ref`: exact repository path to the passing 0.0D artifact used for this run.
- `base_full_blob_sha`: exact canonical `data/cards.full.json` blob SHA locked for this run.
- `original_input_accounted`: `true` only when every supplied input item has a terminal discovery disposition and none silently disappears.
- `stage_a_authorized`: `true` only when coverage discovery is complete enough to hand the resulting universe to Stage A.

If any binding is missing/stale, any original input is unaccounted, or residual coverage defects still block Stage A, emit BLOCKED and set `stage_a_authorized = false`.

## Required output
```json
{
  "stage": "0.0C",
  "status": "PASS|BLOCKED_COVERAGE_DISCOVERY_INCOMPLETE",
  "document_universe_manifest_ref": "",
  "base_full_blob_sha": "",
  "original_input_accounted": true,
  "discovered_missing_candidates": [],
  "baseline_follow_up_candidates": [],
  "existing_card_reinforcements": [],
  "existing_card_update_candidates": [],
  "correction_or_reversal_candidates": [],
  "treasure_rescue_candidates": [],
  "regional_coverage_matrix": {},
  "topic_coverage_matrix": {},
  "searched_but_no_material_event_ledger": [],
  "source_universe_expansion_ledger": [],
  "must_report_candidate_ledger": [],
  "known_unknowns": [],
  "residual_coverage_risks": [],
  "terminal_discovery_disposition_ledger": [],
  "stage_a_authorized": true
}
```

PASS requires the exact 0.0D/baseline bindings, `original_input_accounted = true`, a terminal discovery disposition for every original and discovered item, and `stage_a_authorized = true`. No item disappears before Stage A.
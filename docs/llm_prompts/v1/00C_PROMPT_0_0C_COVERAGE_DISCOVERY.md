# Prompt 0.0C — Coverage Discovery & Completeness V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_0C_V4_20260901`

## Purpose
Challenge the supplied raw universe before Stage A. Find missing material events, meaningful follow-ups, corrections/reversals, and reinforcement opportunities.

## Entry gate
Require 0.0D PASS and exact current baseline lock. Bind this artifact to the exact 0.0D manifest and canonical full blob used by the run.

## Search universe
Review supplied raw input, current canonical full, trackers/watchlists/review pools/holds, material existing-card lineages, official sources, and reputable independent reporting.

Required regional axes and exact machine keys:

- Korea → `korea`
- North America → `north_america`
- China → `china`
- Japan → `japan`
- Europe → `europe`
- material global markets → `material_global_markets`

Required topic axes and exact machine keys:

- cells/chemistries → `cells_chemistries`
- materials/components → `materials_components`
- pouch/pouch-film demand signals → `pouch_pouch_film_demand`
- ESS/BESS → `ess_bess`
- EV/charging → `ev_charging`
- manufacturing/capacity/utilisation → `manufacturing_capacity_utilisation`
- grid/AI-data-centre power → `grid_ai_data_centre_power`
- critical minerals/refining → `critical_minerals_refining`
- recycling → `recycling`
- policy/trade/sanctions/subsidies/localisation → `policy_trade_sanctions_subsidies_localisation`
- competitors/customers → `competitors_customers`
- prices/costs/margins → `prices_costs_margins`
- financing → `financing`
- safety/recall/commissioning/operation → `safety_recall_commissioning_operation`

Every required regional/topic axis must terminate with an object whose `status` is exactly `searched` or `blocked`. A `blocked` row must contain a non-empty `reason`. Missing axes, arbitrary substitute keys, or non-terminal statuses block Stage A. Additional scoped axes are allowed but do not replace the mandatory keys.

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

If any binding is missing/stale, any mandatory coverage axis lacks a terminal searched/blocked disposition, any original input is unaccounted, or residual coverage defects still block Stage A, emit BLOCKED and set `stage_a_authorized = false`.

## Machine ledger identity and reconciliation
Every row that represents an original or discovered candidate must carry a stable non-empty `candidate_id`. A pre-existing governed identity such as `story_id`, `source_story_id`, `spec_id`, `source_spec_id`, or production `id` may be retained as an alias, but `candidate_id` is the canonical 0.0C reconciliation key for newly generated artifacts.

The ledgers have distinct roles:

- `original_input_ledger[]`: every supplied input item exactly once.
- candidate buckets (`discovered_missing_candidates`, `baseline_follow_up_candidates`, `existing_card_reinforcements`, `existing_card_update_candidates`, `correction_or_reversal_candidates`, `treasure_rescue_candidates`, `must_report_candidate_ledger`) retain their governed candidate identity.
- `source_universe_expansion_ledger[]`: the complete expanded event universe, including every original-input candidate and every discovered candidate retained for terminal accounting.
- `terminal_discovery_disposition_ledger[]`: exactly one terminal row for every `source_universe_expansion_ledger` candidate, with non-empty `disposition`.

On PASS, every candidate in the original/candidate ledgers must be present in `source_universe_expansion_ledger`, and the set of candidate identities in `terminal_discovery_disposition_ledger` must equal the expanded-universe identity set exactly. Duplicate identities, missing terminal rows, terminal rows for unknown candidates, missing mandatory coverage axes, or non-terminal matrix rows are BLOCKED.

## Required output
```json
{
  "stage": "0.0C",
  "status": "PASS|BLOCKED_COVERAGE_DISCOVERY_INCOMPLETE",
  "document_universe_manifest_ref": "",
  "base_full_blob_sha": "",
  "original_input_accounted": true,
  "original_input_ledger": [
    {"candidate_id": "", "story_id": null, "discovery_origin": "original_input"}
  ],
  "discovered_missing_candidates": [],
  "baseline_follow_up_candidates": [],
  "existing_card_reinforcements": [],
  "existing_card_update_candidates": [],
  "correction_or_reversal_candidates": [],
  "treasure_rescue_candidates": [],
  "regional_coverage_matrix": {
    "korea": {"status": "searched"},
    "north_america": {"status": "searched"},
    "china": {"status": "searched"},
    "japan": {"status": "searched"},
    "europe": {"status": "searched"},
    "material_global_markets": {"status": "searched"}
  },
  "topic_coverage_matrix": {
    "cells_chemistries": {"status": "searched"},
    "materials_components": {"status": "searched"},
    "pouch_pouch_film_demand": {"status": "searched"},
    "ess_bess": {"status": "searched"},
    "ev_charging": {"status": "searched"},
    "manufacturing_capacity_utilisation": {"status": "searched"},
    "grid_ai_data_centre_power": {"status": "searched"},
    "critical_minerals_refining": {"status": "searched"},
    "recycling": {"status": "searched"},
    "policy_trade_sanctions_subsidies_localisation": {"status": "searched"},
    "competitors_customers": {"status": "searched"},
    "prices_costs_margins": {"status": "searched"},
    "financing": {"status": "searched"},
    "safety_recall_commissioning_operation": {"status": "searched"}
  },
  "searched_but_no_material_event_ledger": [],
  "source_universe_expansion_ledger": [
    {"candidate_id": "", "origin": "original_input|discovered"}
  ],
  "must_report_candidate_ledger": [],
  "known_unknowns": [],
  "residual_coverage_risks": [],
  "terminal_discovery_disposition_ledger": [
    {"candidate_id": "", "disposition": ""}
  ],
  "stage_a_authorized": true
}
```

PASS requires exact 0.0D/baseline bindings, `original_input_accounted = true`, all mandatory regional/topic keys with terminal searched/blocked status, exact expanded-universe/terminal-ledger reconciliation, a terminal discovery disposition for every original and discovered item, and `stage_a_authorized = true`. No item or mandatory coverage axis disappears before Stage A.

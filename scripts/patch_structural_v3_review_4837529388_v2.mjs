#!/usr/bin/env node
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";

const p = {
  a: "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md",
  o: "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md",
  b: "docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md",
  q: "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
  r: "validation_scripts/related_lifecycle_check.py",
  t: "validation_scripts/tests/test_workflow_contracts.py",
  v: "docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md",
};
const oldScript = "scripts/patch_structural_v3_review_4837529388.mjs";
const self = "scripts/patch_structural_v3_review_4837529388_v2.mjs";
const wf = ".github/workflows/patch-structural-v3-review-4837529388.yml";

function one(s, oldText, newText, label) {
  const i = s.indexOf(oldText);
  if (i < 0) throw new Error(`${label}: target not found`);
  if (s.indexOf(oldText, i + oldText.length) >= 0) throw new Error(`${label}: target not unique`);
  return s.slice(0, i) + newText + s.slice(i + oldText.length);
}
function edit(path, fn) {
  const before = readFileSync(path, "utf8");
  const after = fn(before);
  if (after === before) throw new Error(`${path}: unchanged`);
  writeFileSync(path, after);
}

edit(p.o, (s) => {
  s = one(s,
`## 8. Review-pool partition

Use:

- \`candidate_review_pool[]\`
- \`structural_signal_review_pool[]\`
- \`earnings_deep_dive_pool[]\`
- \`watchlist_context_pool[]\`
- \`existing_reinforcement[]\`
- \`support_source_only[]\`
- \`rejected[]\`

Each non-strict item must include:

- \`review_pool_partition\`
- \`review_pool_partition_reason\`
- \`promotion_precondition\`
- \`bounded_review_question\`
- \`recommended_next_action\`

High-value unresolved structural items require:

- \`structural_rescue_required: true\`
- a concrete \`structural_rescue_question\`

Stage A remains no-fetch. Rescue means bounded-question capture and preservation, not external search.`,
`## 8. Review-pool partition

Use only the supported top-level Stage A partitions:

- \`candidate_review_pool[]\`
- \`watchlist_context_pool[]\`
- \`reject_or_support_only_pool[]\`

\`existing_reinforcement[]\`, \`support_source_only[]\`, and \`rejected[]\` remain separate non-review outcomes.

\`structural_signal_review_pool\` and \`earnings_deep_dive_pool\` are not standalone top-level partition arrays. They are \`review_pool_subtype\` values inside \`candidate_review_pool[]\` so the existing promotion workflow remains authoritative.

For every non-strict review item include:

- \`review_pool_partition\`
- \`review_pool_subtype\`
- \`review_pool_partition_reason\`
- \`promotion_precondition\`
- \`bounded_review_question\`
- \`recommended_next_action\`

For \`review_pool_partition: candidate_review_pool\`, set exactly one subtype:

- \`general_candidate\`
- \`structural_signal_review_pool\`
- \`earnings_deep_dive_pool\`

High-value unresolved structural items use \`structural_signal_review_pool\`; listed-company results awaiting full call/Q&A or prior-period comparison use \`earnings_deep_dive_pool\`. Both remain promotable only through the existing candidate-review authorization path.

High-value unresolved structural items require:

- \`structural_rescue_required: true\`
- a concrete \`structural_rescue_question\`

Stage A remains no-fetch. Rescue means bounded-question capture and preservation, not external search.`, "override partitions");
  s = one(s, "- `review_pool_repromotion_precondition`", "- `review_pool_subtype`\n- `review_pool_repromotion_precondition`", "override subtype ledger");
  s = one(s, "- a mandatory structural domain is zero without recheck and explanation;", "- a mandatory structural domain is zero without recheck and explanation;\n- `structural_signal_review_pool` or `earnings_deep_dive_pool` is emitted as a standalone top-level partition instead of a `candidate_review_pool` subtype;\n- a candidate-review item lacks a valid `review_pool_subtype`;", "override subtype blockers");
  return s;
});

edit(p.a, (s) => {
  s = one(s, "   - concrete execution anchor when format-risk tags are present", "   - for format-risk items, either a concrete execution anchor or a complete V3 Structural Value Override package with a valid non-execution anchor class, item-specific Stage B evidence targets, and a specific explanation of why execution is not required", "Stage A strict gate");
  s = one(s, "`review_pool[]` may remain only as a backward-compatible aggregate container.\nIf `review_pool[]` is emitted, every item inside it must duplicate the exact `review_pool_partition` used in the first-class partition arrays.", "`review_pool[]` may remain only as a backward-compatible aggregate container.\nIf `review_pool[]` is emitted, every item inside it must duplicate the exact `review_pool_partition` used in the first-class partition arrays.\n\n`structural_signal_review_pool` and `earnings_deep_dive_pool` are not additional top-level partition arrays. They are `review_pool_subtype` values within `candidate_review_pool[]`, preserving the existing promotion workflow and partition enum.", "Stage A subtype declaration");
  s = one(s,
`1. \`candidate_review_pool[]\`
   - Plausibly cardable after bounded clarification.
   - Must have direct SBTL_HUB lane fit.
   - Must have a plausible concrete execution anchor or a clearly checkable path to one.
   - Must have a specific unresolved issue that can be resolved by a later review/promotion run.
   - Must include \`promotion_precondition\` and \`bounded_review_question\`.`,
`1. \`candidate_review_pool[]\`
   - Plausibly cardable after bounded clarification.
   - Must have direct SBTL_HUB lane fit.
   - Must have a plausible valid anchor class or a clearly checkable path to one.
   - A non-execution candidate must carry the V3 Structural Value Override fields, including item-specific Stage B evidence targets and why a conventional execution event is unnecessary.
   - Must have a specific unresolved issue that can be resolved by a later review/promotion run.
   - Must include \`review_pool_subtype\`, \`promotion_precondition\`, and \`bounded_review_question\`.
   - Allowed subtypes are \`general_candidate\`, \`structural_signal_review_pool\`, and \`earnings_deep_dive_pool\`.`, "Stage A candidate review definition");
  s = one(s,
`- \`execution_anchor_type\`
- \`execution_anchor_strength\`
- \`strict_pass_gate_status\`
- \`strict_pass_gate_reason\`
- \`review_pool_partition\`
- \`review_pool_partition_reason\``,
`- \`execution_anchor_type\`
- \`execution_anchor_strength\`
- \`structural_value_override_applied\`
- \`anchor_classes\`
- \`evidence_needed_for_stage_b\`
- \`why_execution_event_not_required\`
- \`strict_pass_gate_status\`
- \`strict_pass_gate_reason\`
- \`review_pool_partition\`
- \`review_pool_subtype\`
- \`review_pool_partition_reason\``, "Stage A CSV fields");
  s = one(s, "- If `format_risk_tags` is not empty/none, `execution_anchor_strength` must be `strong` or `moderate`.", "- If `format_risk_tags` is not empty/none, either `execution_anchor_strength` must be `strong` or `moderate`, or `structural_value_override_applied` must be true with at least one valid non-execution `anchor_classes` value, non-empty item-specific `evidence_needed_for_stage_b`, and non-empty specific `why_execution_event_not_required`.", "Stage A CSV strict alternatives");
  s = one(s, "- `promotion_precondition` must not be empty for `candidate_review_pool`.\n- `recommended_next_action` must not recommend Stage B for `watchlist_context_pool` or `reject_or_support_only_pool`.", "- `promotion_precondition` must not be empty for `candidate_review_pool`.\n- For `candidate_review_pool`, `review_pool_subtype` must be exactly one of `general_candidate`, `structural_signal_review_pool`, or `earnings_deep_dive_pool`.\n- `structural_signal_review_pool` and `earnings_deep_dive_pool` must never appear as top-level `review_pool_partition` values.\n- `recommended_next_action` must not recommend Stage B for `watchlist_context_pool` or `reject_or_support_only_pool`.", "Stage A CSV subtype rules");
  return s;
});

edit(p.b, (s) => {
  s = one(s,
`1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`,
`1. docs/FACT_DISCIPLINE.md
2. docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
3. docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md
4. docs/PROMPT_ABC_DEFAULT_MODE.md
5. docs/PROMPT_ABC_SUPPORTING_RULES.md
6. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
7. docs/CARD_ID_STANDARD.md
8. docs/WORKFLOW.md
9. docs/OPERATIONS.md
10. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`, "Stage B hierarchy");
  s = one(s,
`Stage B strict-pass gate validation:

Stage B must inspect Stage A format-risk and execution-anchor metadata when present.

- If a strict_passed_spec has format_risk_tags other than none, Stage B must verify that fetched evidence supports the claimed execution anchor.
- In v13 replace-all mode, missing \`strict_pass_gate\` is a Stage A structural failure. Stage B must stop with \`BLOCKED_STAGE_A_STRICT_GATE_METADATA_MISSING\` rather than infer the anchor. A legacy exception is allowed only if the user explicitly declares a non-v13 legacy Stage A artifact as authoritative for a one-off recovery run.
- If fetched evidence shows the item is only product news, demo, PoC, pilot, prototype, component launch, interview, commentary, roundup, speech, personnel, or partnership/integration with no concrete execution anchor, mark draft_blocked.
- If fetched evidence supports only a weaker stage than Stage A implied, mark draft_blocked with source_direction_mismatch or execution_anchor_missing.
- If the item remains strategically useful but not independently cardable, recommend support_source_only or review_pool triage in recommended_next_action; do not force a draft.

Allowed concrete execution anchors are the same as Stage A: signed contract, binding customer order, offtake, price floor/risk-sharing facility, commercial deployment, field installation, commissioning, production start, facility opening, certification/regulatory approval, regulatory decision/enforcement, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory safety action, named customer adoption, named deployment site with measurable pilot scale/duration/objective, factory/project groundbreaking, or final investment decision.`,
`Stage B strict-pass gate validation:

Stage B must inspect Stage A format-risk, anchor-class, and Structural Value Override metadata when present.

- In V3 mode, a format-risk strict candidate must follow one of two source-backed paths: (a) a concrete execution anchor, or (b) a complete Structural Value Override using a valid non-execution anchor class.
- The non-execution path requires \`structural_selector_policy_version: STRUCTURAL_NEWS_VALUE_SELECTION_V3\`, \`structural_value_override_applied: true\`, at least one valid non-execution \`anchor_classes[]\` value, item-specific \`evidence_needed_for_stage_b[]\`, a specific \`why_execution_event_not_required\`, and the required before-after and changed-judgment fields.
- Stage B must fetch and verify the exact claim, metric, stage, date, or uncertainty named in every \`evidence_needed_for_stage_b[]\` entry. Generic evidence categories do not satisfy this gate.
- Missing \`strict_pass_gate\` is a Stage A structural failure. Stage B must stop with \`BLOCKED_STAGE_A_STRICT_GATE_METADATA_MISSING\` rather than infer an anchor. A legacy exception is allowed only if the user explicitly declares a non-V3 legacy Stage A artifact as authoritative for a one-off recovery run.
- Product news, demo, PoC, pilot, prototype, component launch, interview, commentary, roundup, speech, personnel, or partnership/integration must be marked \`draft_blocked\` only when fetched evidence supports neither a concrete execution anchor nor a valid source-backed V3 non-execution anchor package.
- If fetched evidence supports a weaker execution stage, weaker non-execution claim, or different anchor class than Stage A implied, mark \`draft_blocked\` with \`source_direction_mismatch\` or \`anchor_evidence_missing\`.
- Stage B must carry the validated anchor classes, override fields, evidence targets, before-after chain, and changed judgment into the evidence package and draft metadata.
- If the item remains strategically useful but not independently cardable, recommend \`support_source_only\` or candidate-review triage in \`recommended_next_action\`; do not force a draft.

Allowed execution anchors remain: signed contract, binding customer order, offtake, price floor/risk-sharing facility, commercial deployment, field installation, commissioning, production start, facility opening, certification/regulatory approval, regulatory decision/enforcement, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory safety action, named customer adoption, named deployment site with measurable pilot scale/duration/objective, factory/project groundbreaking, or final investment decision.

Allowed V3 non-execution anchor classes are: \`policy_regulatory_anchor\`, \`data_financial_anchor\`, \`strategic_behavior_anchor\`, \`technology_commercialization_anchor\`, and \`follow_up_probability_anchor\`. Their use never waives evidence, source-direction, full-schema cardability, or no-anchor-laundering rules.`, "Stage B anchor gate");
  return s;
});

edit(p.q, (s) => {
  s = one(s, "Upstream lineage integrity rule — Stage A V2 selector safety:", "Upstream lineage integrity rule — Stage A V3 selector safety:", "Final QC heading");
  s = one(s, "This step must verify that every upstream workflow output belongs to the same current run lineage and that the Stage A V2 selector gates were valid.", "This step must verify that every upstream workflow output belongs to the same current run lineage and that the Stage A V3 selector gates were valid.", "Final QC lineage");
  s = one(s, "- Stage A selector marker is present and accepted. Accepted markers include `enhanced_selector_precision_version: 20260505_safe_execution_anchor` or later/equivalent, or legacy `selector_policy_version: stage_a_high_precision_execution_anchor_v2` or later.\n- strict_pass_gate or strict_gate_check exists for every candidate that originated from strict_passed_spec[]\n- execution_anchor_type / execution_anchor_strength is present for every format-risk candidate", "- Stage A selector marker is present and accepted. The current marker is `structural_selector_policy_version: STRUCTURAL_NEWS_VALUE_SELECTION_V3`; explicitly authorized legacy markers may be accepted only for a declared one-off recovery run.\n- `strict_pass_gate` or `strict_gate_check` exists for every candidate that originated from `strict_passed_spec[]`\n- every format-risk candidate carries either source-backed `execution_anchor_type` / `execution_anchor_strength`, or a validated V3 Structural Value Override package with a valid non-execution anchor class, item-specific Stage B evidence targets, and a specific explanation of why execution is not required", "Final QC required fields");
  s = one(s,
`Final QC execution-anchor publish gate:

A card may receive publish_ready=true only if final QC confirms that any Stage A format-risk / execution-anchor risk was resolved with source-backed evidence.

Hard fail for publish_ready:

- missing strict_pass_gate / strict_gate_check metadata
- Stage A selector validity not PASS
- artifact consistency not PASS
- format-risk card has no execution_anchor_type or no source-backed execution anchor
- execution anchor was inflated in title, sub, gate, fact, or implication
- card entered the pipeline from review_pool, support_source_only, rejected, duplicate_hold, existing_reinforcement, or any non-addable state without an explicit authorized reopen`,
`Final QC anchor publish gate:

A card may receive \`publish_ready=true\` only if final QC confirms that every Stage A format-risk was resolved through one source-backed path: a concrete execution anchor or a valid V3 non-execution Structural Value Override.

Hard fail for \`publish_ready\`:

- missing \`strict_pass_gate\` / \`strict_gate_check\` metadata
- Stage A selector validity not PASS
- artifact consistency not PASS
- a format-risk card has neither a source-backed execution anchor nor a validated V3 non-execution anchor package
- \`structural_value_override_applied: true\` but the valid non-execution anchor class, concrete item-specific evidence targets, specific \`why_execution_event_not_required\`, before-after chain, or changed judgment is missing or unsupported
- execution stage, non-execution anchor class, Structural Value Override, title, sub, gate, fact, or implication was inflated beyond fetched evidence
- the card entered the pipeline from review_pool, support_source_only, rejected, duplicate_hold, existing_reinforcement, or any non-addable state without an explicit authorized reopen`, "Final QC publish gate");
  s = one(s,
`1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`,
`1. docs/FACT_DISCIPLINE.md
2. docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
3. docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md
4. docs/PROMPT_ABC_DEFAULT_MODE.md
5. docs/PROMPT_ABC_SUPPORTING_RULES.md
6. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
7. docs/CARD_ID_STANDARD.md
8. docs/WORKFLOW.md
9. docs/OPERATIONS.md
10. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`, "Final QC hierarchy");
  return s;
});

edit(p.r, (s) => {
  s = one(s,
`DISALLOWED_PUBLISH_RELATIONS = {
    "same_event_duplicate",
    "existing_card_reinforcement",
    "uncertain_needs_review",
}
`,
`DISALLOWED_PUBLISH_RELATIONS = {
    "same_event_duplicate",
    "existing_card_reinforcement",
    "uncertain_needs_review",
}
FRESH_FOLLOW_UP_ANCHOR_CLASSES = {
    "execution_event_anchor",
    "policy_regulatory_anchor",
    "data_financial_anchor",
    "strategic_behavior_anchor",
    "technology_commercialization_anchor",
    "follow_up_probability_anchor",
}
`, "validator classes");
  s = one(s,
`    if relation_type == "distinct_follow_up" and not lineage.get("fresh_follow_up_anchor"):
        errors.append("distinct_follow_up requires fresh_follow_up_anchor")
`,
`    if relation_type == "distinct_follow_up":
        if not lineage.get("fresh_follow_up_anchor"):
            errors.append("distinct_follow_up requires fresh_follow_up_anchor")
        anchor_class = lineage.get("fresh_follow_up_anchor_class")
        if anchor_class not in FRESH_FOLLOW_UP_ANCHOR_CLASSES:
            errors.append("distinct_follow_up requires valid fresh_follow_up_anchor_class")
        incremental_fact = lineage.get("incremental_fact_vs_predecessor")
        if not isinstance(incremental_fact, str) or not incremental_fact.strip():
            errors.append("distinct_follow_up requires incremental_fact_vs_predecessor")
        changed_judgment = lineage.get("changed_judgment_vs_predecessor")
        if not isinstance(changed_judgment, str) or not changed_judgment.strip():
            errors.append("distinct_follow_up requires changed_judgment_vs_predecessor")
`, "validator follow-up fields");
  return s;
});

edit(p.t, (s) => {
  s = one(s,
`                "reason": "contract followed by commissioning",
                "fresh_follow_up_anchor": "commissioning",
                "related_candidate_spec_ids": [],`,
`                "reason": "contract followed by commissioning",
                "fresh_follow_up_anchor_class": "execution_event_anchor",
                "fresh_follow_up_anchor": "commissioning",
                "incremental_fact_vs_predecessor": "Commissioning is now source-confirmed.",
                "changed_judgment_vs_predecessor": "The project moved from contracted to operating-stage evidence.",
                "related_candidate_spec_ids": [],`, "test fixture");
  s = one(s,
`    def test_duplicate_cannot_publish(self):
        self.child["related_lineage"]["relation_type"] = "same_event_duplicate"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("may not use" in error for error in errors))
`,
`    def test_distinct_follow_up_requires_valid_anchor_class(self):
        self.child["related_lineage"]["same_event_checked"] = True
        self.child["related_lineage"]["earliest_same_event_date_checked"] = True
        self.child["related_lineage"].pop("fresh_follow_up_anchor_class")
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("fresh_follow_up_anchor_class" in error for error in errors))

    def test_distinct_follow_up_rejects_invalid_anchor_class(self):
        self.child["related_lineage"]["same_event_checked"] = True
        self.child["related_lineage"]["earliest_same_event_date_checked"] = True
        self.child["related_lineage"]["fresh_follow_up_anchor_class"] = "generic_topic_anchor"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("fresh_follow_up_anchor_class" in error for error in errors))

    def test_distinct_follow_up_requires_incremental_fact(self):
        self.child["related_lineage"]["same_event_checked"] = True
        self.child["related_lineage"]["earliest_same_event_date_checked"] = True
        self.child["related_lineage"]["incremental_fact_vs_predecessor"] = ""
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("incremental_fact_vs_predecessor" in error for error in errors))

    def test_distinct_follow_up_requires_changed_judgment(self):
        self.child["related_lineage"]["same_event_checked"] = True
        self.child["related_lineage"]["earliest_same_event_date_checked"] = True
        self.child["related_lineage"]["changed_judgment_vs_predecessor"] = ""
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("changed_judgment_vs_predecessor" in error for error in errors))

    def test_duplicate_cannot_publish(self):
        self.child["related_lineage"]["relation_type"] = "same_event_duplicate"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("may not use" in error for error in errors))
`, "validator tests");
  return s;
});

edit(p.v, (s) => {
  s = one(s,
`This governance change upgrades the canonical structural-value and Stage A override files introduced by PR #176 and aligns the Related lifecycle contract:

- \`docs/STRUCTURAL_NEWS_VALUE_SELECTION.md\`
- \`docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md\`
- \`docs/RELATED_LIFECYCLE_CONTRACT.md\`

It does not modify card data, the card-run engine, or any production ID.`,
`This rollout upgrades the canonical structural-value policy and aligns the executable selector, evidence, final-QC, and Related contracts:

- \`docs/STRUCTURAL_NEWS_VALUE_SELECTION.md\`
- \`docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md\`
- \`docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md\`
- \`docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md\`
- \`docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md\`
- \`docs/RELATED_LIFECYCLE_CONTRACT.md\`
- \`validation_scripts/related_lifecycle_check.py\`
- \`validation_scripts/tests/test_workflow_contracts.py\`

It does not modify card data, the card-run engine, or any production ID.`, "validation scope");
  s = one(s, "7. structural and earnings-specific review pools;", "7. structural and earnings-specific review subtypes routed through the supported `candidate_review_pool`;", "validation review subtype");
  s = one(s, "- non-execution follow-ups have a defined Related evidence contract;", "- non-execution follow-ups have a defined Related evidence contract;\n- the production Related validator enforces the V2 anchor-class, incremental-fact, and changed-judgment fields;\n- Stage A review subtypes remain inside the supported candidate partition;\n- Stage B and Final QC accept only fully evidenced V3 non-execution anchor packages;", "validation checklist");
  s = one(s,
`## Declared implementation boundary

This PR establishes governance authority, the Stage A override, and the Related lifecycle semantic contract.

A follow-up implementation PR must align the downstream executable contracts, including where applicable:

- base Stage A prompt required-doc list and strict-gate wording;
- Stage B/C and post-acceptance prompt field preservation;
- Stage A JSON/CSV schemas;
- Related JSON/schema and validators for the new anchor-class fields;
- structural-value, earnings-Q&A, follow-up, coverage, and content-depth validators;
- artifact contracts and regression fixtures.

The follow-up implementation must not weaken Fact Discipline or the card-run safety engine.`,
`## Executable alignment completed in this PR

This PR aligns the central V3 feature with the active execution path:

- base Stage A accepts either a concrete execution anchor or a complete V3 non-execution override for format-risk strict items;
- structural and earnings review categories are subtypes of the supported \`candidate_review_pool\`, not unsupported top-level partitions;
- the Stage A CSV gate carries and validates the subtype and override fields;
- Stage B verifies the exact non-execution anchor claims and evidence targets instead of demanding an execution event;
- Final QC accepts a source-backed V3 non-execution path and hard-fails incomplete or inflated overrides;
- the Related production validator enforces fresh anchor class, incremental fact, and changed judgment for every \`distinct_follow_up\`;
- regression fixtures cover the new Related blockers.

Remaining future implementation may add dedicated structural-value, earnings-Q&A, portfolio-coverage, and content-depth validators, but it must not reintroduce an execution-only gate or unsupported review partition. Fact Discipline and the card-run safety engine remain unchanged.`, "validation boundary");
  return s;
});

for (const [path, needles] of [
  [p.a, ["review_pool_subtype", "structural_value_override_applied"]],
  [p.o, ["They are `review_pool_subtype` values inside `candidate_review_pool[]`"]],
  [p.b, ["Allowed V3 non-execution anchor classes", "anchor_evidence_missing"]],
  [p.q, ["Stage A V3 selector safety", "validated V3 non-execution anchor package"]],
  [p.r, ["FRESH_FOLLOW_UP_ANCHOR_CLASSES", "incremental_fact_vs_predecessor"]],
  [p.t, ["test_distinct_follow_up_rejects_invalid_anchor_class"]],
  [p.v, ["Executable alignment completed in this PR"]],
]) {
  const s = readFileSync(path, "utf8");
  const missing = needles.filter((n) => !s.includes(n));
  if (missing.length) throw new Error(`${path}: missing ${missing.join(", ")}`);
}

for (const path of [oldScript, self, wf]) unlinkSync(path);
console.log("PASS: V3 downstream gates and Related validator aligned; temporary files removed");

#!/usr/bin/env node
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";

const path = "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md";
const self = "scripts/patch_structural_v3_stage_a_residuals.mjs";
const workflow = ".github/workflows/patch-structural-v3-stage-a-residuals.yml";
let text = readFileSync(path, "utf8");

function once(oldText, newText, label) {
  const count = text.split(oldText).length - 1;
  if (count !== 1) throw new Error(`${label}: expected 1, found ${count}`);
  text = text.replace(oldText, newText);
}

once(
  "   Do not use the phrases hard-exclude, automatic exclusion, or categorical exclusion in Stage A reasoning for these formats. The correct reasoning is: strict-pass blocked unless a concrete fresh execution anchor is visible.",
  "   Do not use the phrases hard-exclude, automatic exclusion, or categorical exclusion in Stage A reasoning for these formats. The correct reasoning is: strict-pass blocked unless either a concrete fresh execution anchor or a complete V3 non-execution Structural Value Override is visible in the allowed Stage A inputs.",
  "format-risk reasoning",
);
once(
  "B. If all 8 required docs are confirmed, load {{SOURCE_INPUT_FILE}}.",
  "B. If all 10 required docs are confirmed, load {{SOURCE_INPUT_FILE}}.",
  "task doc count",
);
once(
  "   - concrete execution-anchor viability when format-risk is present",
  "   - concrete execution-anchor or complete V3 non-execution-anchor viability when format-risk is present",
  "lane-sanity anchor viability",
);
once(
  "   - Use for product/demo/PoC/partnership/commentary/macro items where the execution anchor is absent or too weak.",
  "   - Use for product/demo/PoC/partnership/commentary/macro items where neither a concrete execution anchor nor a complete V3 non-execution anchor package is sufficient.",
  "reject-support partition wording",
);
once(
  "   - list all 8 required docs",
  "   - list all 10 required docs",
  "report doc count",
);
once(
  "   - execution anchor type and strength\n   - format-risk tags, if any",
  "   - execution anchor type and strength\n   - Structural Value Override status, anchor classes, Stage B evidence targets, and why execution is not required, when applicable\n   - format-risk tags, if any",
  "strict manifest override visibility",
);
once(
  "   - execution-anchor gap or source-strength gap, if applicable",
  "   - execution-anchor, non-execution-anchor, or source-strength gap, if applicable",
  "review manifest gap wording",
);
once(
  "The following patterns must not enter `strict_passed_spec[]` unless a concrete battery/grid/ESS/EV/materials execution anchor is present:",
  "The following patterns must not enter `strict_passed_spec[]` unless either a concrete battery/grid/ESS/EV/materials execution anchor or a complete, item-specific V3 Structural Value Override is present:",
  "negative-filter V3 alternative",
);
once(
`- \`execution_anchor_type\`
- \`execution_anchor_strength\`
- \`baseline_relation\``,
`- \`execution_anchor_type\`
- \`execution_anchor_strength\`
- \`structural_value_override_applied\`
- \`anchor_classes\`
- \`evidence_needed_for_stage_b\`
- \`why_execution_event_not_required\`
- \`baseline_relation\``,
  "lineage override fields",
);

for (const needle of [
  "If all 10 required docs are confirmed",
  "complete V3 non-execution Structural Value Override is visible",
  "list all 10 required docs",
  "structural_value_override_applied",
]) {
  if (!text.includes(needle)) throw new Error(`missing ${needle}`);
}
if (text.includes("If all 8 required docs are confirmed")) throw new Error("stale 8-doc task wording remains");
if (text.includes("strict-pass blocked unless a concrete fresh execution anchor is visible")) throw new Error("execution-only reasoning remains");

writeFileSync(path, text);
unlinkSync(self);
unlinkSync(workflow);
console.log("PASS: Stage A residual V3 contradictions removed");

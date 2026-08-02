#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";

const path = "scripts/patch_structural_v3_review_4837763004.mjs";
let text = readFileSync(path, "utf8");
const oldText = '        self.assertNotIn("the execution anchor is explicitly covered by `fact_sources` and `source_claim_coverage_map`;", text)';
const newText = '        self.assertNotIn("the execution anchor is explicitly covered by \\`fact_sources\\` and \\`source_claim_coverage_map\\`;", text)';
const count = text.split(oldText).length - 1;
if (count !== 1) throw new Error(`expected one unescaped regression assertion, found ${count}`);
text = text.replace(oldText, newText);
writeFileSync(path, text);

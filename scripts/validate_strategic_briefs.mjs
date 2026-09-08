#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { validateStrategicBriefLibrary } from "../lib/brief/strategicPublication.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const target = process.argv[2]
  ? path.resolve(process.cwd(), process.argv[2])
  : path.join(root, "public/data/strategic_briefs.json");

let parsed;
try {
  parsed = JSON.parse(fs.readFileSync(target, "utf8"));
} catch (error) {
  console.error(`STRATEGIC_BRIEF_INVALID: cannot read/parse ${target}`);
  console.error(error?.message || String(error));
  process.exit(1);
}

const errors = validateStrategicBriefLibrary(parsed);
if (errors.length) {
  console.error(`STRATEGIC_BRIEF_INVALID: ${errors.length} error(s)`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`STRATEGIC_BRIEF_VALID: ${parsed.items.length} published issue(s)`);

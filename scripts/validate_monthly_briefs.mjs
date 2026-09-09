import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { validateMonthlyBriefLibrary } from "../lib/brief/monthlyPublication.js";
import { createGitProvenanceResolver, validateMonthlyBriefProvenance } from "../lib/brief/monthlyProvenance.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const file = path.join(root, "public/data/monthly_briefs.json");

const library = JSON.parse(fs.readFileSync(file, "utf8"));
const errors = [
  ...validateMonthlyBriefLibrary(library),
  ...validateMonthlyBriefProvenance(library, createGitProvenanceResolver({ cwd: root })),
];

if (errors.length) {
  console.error(`Monthly Brief validation failed (${errors.length})`);
  errors.forEach((error) => console.error(`- ${error}`));
  process.exit(1);
}

console.log(`Monthly Brief validation PASS · ${library.items.length} official issue(s)`);
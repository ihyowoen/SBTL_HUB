import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");

const ACTIVE_FILES = [
  "src/App.jsx",
  "lib/chat/appCommand.js",
  "src/MonthlyBriefPanel.jsx",
  "src/monthlyBriefSelection.js",
  "lib/brief/monthlyPublication.js",
  "schemas/monthly-brief.v1.schema.json",
  "package.json",
  "public/data/monthly_briefs.json",
];

const OBSOLETE_FILES = [
  "product/STRATEGIC_BRIEF_EDITORIAL_CONTRACT.md",
  "public/data/strategic_briefs.json",
  "schemas/strategic-brief.v1.schema.json",
  "lib/brief/strategicPublication.js",
  "scripts/validate_strategic_briefs.mjs",
  "src/StrategicBriefPanel.jsx",
  "src/strategicBriefSelection.js",
  ".github/workflows/validate-strategic-briefs.yml",
];

describe("active HUB Monthly Brief domain", () => {
  it("contains no active Strategic/VOL product identity", () => {
    const legacy = /StrategicBrief|strategic_show|strategic-brief|strategic_briefs|VOL\./;
    for (const rel of ACTIVE_FILES) {
      const text = fs.readFileSync(path.join(root, rel), "utf8");
      expect(text, rel).not.toMatch(legacy);
    }
  });

  it("does not retain obsolete Strategic Brief runtime/publication files", () => {
    for (const rel of OBSOLETE_FILES) {
      expect(fs.existsSync(path.join(root, rel)), rel).toBe(false);
    }
  });
});

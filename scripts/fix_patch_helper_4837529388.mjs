#!/usr/bin/env node
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";

const target = "scripts/patch_structural_v3_review_4837529388_v2.mjs";
const self = "scripts/fix_patch_helper_4837529388.mjs";
let text = readFileSync(target, "utf8");
const oldHelper = `function one(s, oldText, newText, label) {
  const i = s.indexOf(oldText);
  if (i < 0) throw new Error(\`${"${label}"}: target not found\`);
  if (s.indexOf(oldText, i + oldText.length) >= 0) throw new Error(\`${"${label}"}: target not unique\`);
  return s.slice(0, i) + newText + s.slice(i + oldText.length);
}`;
const newHelper = `function one(s, oldText, newText, label) {
  const count = s.split(oldText).length - 1;
  if (count === 0) throw new Error(\`${"${label}"}: target not found\`);
  if (count > 1) {
    if (!label.toLowerCase().includes("hierarchy")) {
      throw new Error(\`${"${label}"}: target not unique\`);
    }
    return s.split(oldText).join(newText);
  }
  const i = s.indexOf(oldText);
  return s.slice(0, i) + newText + s.slice(i + oldText.length);
}`;
if (!text.includes(oldHelper)) throw new Error("v2 helper target not found");
text = text.replace(oldHelper, newHelper);
writeFileSync(target, text);
unlinkSync(self);
console.log("PASS: hierarchy replacements may update all identical governance blocks");

#!/usr/bin/env node
import { gunzipSync } from "node:zlib";
import { dirname } from "node:path";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";

const payload = [1, 2, 3, 4, 5]
  .map((part) => readFileSync(`scripts/.pr232-payload/part${part}`, "utf8").trim())
  .join("");
const files = JSON.parse(gunzipSync(Buffer.from(payload, "base64")).toString("utf8"));
for (const [path, content] of Object.entries(files)) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content);
  console.log(`restored ${path}`);
}
rmSync("scripts/.pr232-payload", { recursive: true, force: true });
rmSync("scripts/pr232_apply_review_fix.mjs", { force: true });
rmSync(".github/workflows/pr232-apply-review-fix.yml", { force: true });
console.log("PASS: PR232 review-fix payload restored and bootstrap removed");

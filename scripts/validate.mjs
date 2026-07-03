#!/usr/bin/env node
// SBTL_HUB tracker validator — zero dependency (node: built-ins only)
// Usage:
//   node scripts/validate.mjs                      # defaults to public/data/*
//   node scripts/validate.mjs path/to/tracker.json path/to/region_policy.json
// Exit code 1 if any ERROR (CI gate). WARNINGs never block (migration nudges).

import { readFileSync, existsSync, readdirSync } from "node:fs";
import { join, basename } from "node:path";

const REGIONS = ["NA", "EU", "CN", "KR", "JP", "GL"];
const STATUSES = ["ACTIVE", "UPCOMING", "WATCH", "DONE"];
const INSTRUMENT_TYPES = ["law", "decree", "notification", "standard"]; // scope: enacted instruments only
const BANNED = ["🚨", "🆕", "🎉"];
const ID_RE = /^[A-Z]{2}-\d{3}$/;
const ISO_RE = /^\d{4}-\d{2}-\d{2}$/;
const BAKED_DDAY_RE = /\bD-\d+\b/; // staleness smell: hard-coded countdown in text

const errors = [];
const warns = [];
const E = (m) => errors.push(m);
const W = (m) => warns.push(m);

// ---- locate inputs ----
function resolveInputs() {
  const argv = process.argv.slice(2);
  if (argv.length) {
    const tr = argv.filter((p) => /tracker/i.test(basename(p)));
    const rp = argv.find((p) => /region_policy/i.test(basename(p)));
    return { trackerFiles: tr.length ? tr : argv.filter((p) => !/region_policy/i.test(p)), regionPolicy: rp };
  }
  const dir = "public/data";
  if (!existsSync(dir)) { E(`data dir not found: ${dir} (pass paths as args)`); return { trackerFiles: [], regionPolicy: null }; }
  const files = readdirSync(dir);
  const trackerFiles = files.filter((f) => /^tracker_data.*\.json$/.test(f)).map((f) => join(dir, f));
  const rp = files.find((f) => f === "region_policy.json");
  return { trackerFiles, regionPolicy: rp ? join(dir, rp) : null };
}

function loadJSON(path) {
  try { return JSON.parse(readFileSync(path, "utf-8")); }
  catch (e) { E(`JSON parse failed [${path}]: ${e.message}`); return null; }
}

function deepText(o) {
  // concatenate all string values for emoji scanning
  if (o == null) return "";
  if (typeof o === "string") return o;
  if (Array.isArray(o)) return o.map(deepText).join("\u0001");
  if (typeof o === "object") return Object.values(o).map(deepText).join("\u0001");
  return "";
}

// ---- validate tracker(s) ----
const allItems = [];
const idIndex = new Map();

function validateTracker(path) {
  const data = loadJSON(path);
  if (!data) return;
  const items = data.items || data.tracker || (Array.isArray(data) ? data : null);
  if (!Array.isArray(items)) { E(`no items[] array in ${path}`); return; }

  for (const blob of [data.meta, data._meta]) {
    if (blob) for (const b of BANNED) if (deepText(blob).includes(b)) E(`banned emoji ${b} in meta [${path}]`);
  }

  for (const it of items) {
    const id = it.id ?? "(no id)";
    // required base fields
    for (const f of ["id", "r", "s", "t"]) if (it[f] == null || it[f] === "") E(`${id}: missing required field '${f}'`);
    // id format + uniqueness
    if (it.id != null) {
      if (!ID_RE.test(it.id)) E(`${id}: id format invalid (expect XX-NNN)`);
      if (idIndex.has(it.id)) E(`duplicate id '${it.id}' (in ${basename(path)} and ${basename(idIndex.get(it.id))})`);
      else idIndex.set(it.id, path);
    }
    // region + status enums
    if (it.r != null && !REGIONS.includes(it.r)) E(`${id}: region '${it.r}' not in ${REGIONS.join("/")}`);
    if (it.s != null && !STATUSES.includes(it.s)) E(`${id}: status '${it.s}' not in ${STATUSES.join("/")}`);
    // banned emoji anywhere in the item
    const txt = deepText(it);
    for (const b of BANNED) if (txt.includes(b)) E(`${id}: banned emoji ${b}`);

    // ---- migration-aware WARNINGS (do not block) ----
    if (it.effectiveDate == null) W(`${id}: no effectiveDate (D-day should derive from ISO, not be baked)`);
    else if (!ISO_RE.test(it.effectiveDate)) E(`${id}: effectiveDate '${it.effectiveDate}' not ISO YYYY-MM-DD`);
    if (typeof it.dt === "string" && BAKED_DDAY_RE.test(it.dt)) W(`${id}: dt contains baked 'D-…' (staleness smell)`);
    if (it.instrumentType == null) W(`${id}: no instrumentType (scope enum: ${INSTRUMENT_TYPES.join("/")})`);
    else if (!INSTRUMENT_TYPES.includes(it.instrumentType)) E(`${id}: instrumentType '${it.instrumentType}' not in ${INSTRUMENT_TYPES.join("/")}`);
    if (it.lastChecked != null && !ISO_RE.test(it.lastChecked)) E(`${id}: lastChecked '${it.lastChecked}' not ISO`);

    // src hygiene
    if (Array.isArray(it.src)) {
      it.src.forEach((s, i) => {
        if (!s || typeof s !== "object") { E(`${id}: src[${i}] not an object`); return; }
        if (!s.u || !/^https?:\/\//.test(s.u)) W(`${id}: src[${i}] missing/!http url`);
        if (s.accessedDate == null) W(`${id}: src[${i}] no accessedDate (link-rot trail)`);
      });
    }
    allItems.push({ ...it, __file: path });
  }
}

// ---- canonical / supersededBy integrity (cross-file, after all loaded) ----
function validateCanonical() {
  const ids = new Set(allItems.map((i) => i.id));
  for (const it of allItems) {
    for (const f of ["canonicalId", "supersededBy"]) {
      if (it[f] != null) {
        if (!ids.has(it[f])) E(`${it.id}: ${f} -> '${it[f]}' does not exist`);
        if (it[f] === it.id) E(`${it.id}: ${f} points to itself`);
      }
    }
  }
}

// ---- region_policy cross-consistency ----
function validateRegionPolicy(path) {
  if (!path) { W("region_policy.json not found — skipping cross-check"); return; }
  const rp = loadJSON(path);
  if (!rp) return;
  for (const b of BANNED) if (deepText(rp).includes(b)) E(`banned emoji ${b} in region_policy`);
  const policyRegions = Object.keys(rp).filter((k) => REGIONS.includes(k));
  // every region with items must have a policy entry
  const itemRegions = new Set(allItems.map((i) => i.r));
  for (const r of itemRegions) if (!policyRegions.includes(r)) W(`region '${r}' has items but no region_policy entry`);
  for (const r of policyRegions) {
    const seg = rp[r];
    for (const f of ["name", "headline", "summary", "watchpoints"]) if (seg[f] == null) E(`region_policy.${r}: missing '${f}'`);
    if (Array.isArray(seg.watchpoints)) {
      seg.watchpoints.forEach((w, i) => {
        if (w && typeof w === "object" && typeof w.d_day === "number") {
          // presence noted; correctness needs effectiveDate to verify
        }
      });
    }
  }
  if (!rp._meta || !rp._meta.lastUpdated) W("region_policy._meta.lastUpdated missing");
}

// ---- run ----
const { trackerFiles, regionPolicy } = resolveInputs();
if (!trackerFiles.length) E("no tracker_data file(s) found");
for (const f of trackerFiles) validateTracker(f);
validateCanonical();
validateRegionPolicy(regionPolicy);

// ---- report ----
const byRegion = {}, byStatus = {};
for (const i of allItems) { byRegion[i.r] = (byRegion[i.r] || 0) + 1; byStatus[i.s] = (byStatus[i.s] || 0) + 1; }

console.log("── SBTL_HUB validate ──");
console.log(`files: ${trackerFiles.map((f) => basename(f)).join(", ")}${regionPolicy ? " + " + basename(regionPolicy) : ""}`);
console.log(`items: ${allItems.length}`);
console.log(`region: ${REGIONS.map((r) => `${r}${byRegion[r] || 0}`).join(" ")}`);
console.log(`status: ${STATUSES.map((s) => `${s}${byStatus[s] || 0}`).join(" ")}`);
if (warns.length) { console.log(`\nWARN (${warns.length}) — migration nudges, non-blocking:`); for (const w of warns.slice(0, 40)) console.log("  ! " + w); if (warns.length > 40) console.log(`  … +${warns.length - 40} more`); }
if (errors.length) { console.log(`\nERROR (${errors.length}) — blocks merge:`); for (const e of errors) console.log("  ✗ " + e); }

if (errors.length) { console.log("\nRESULT: FAIL"); process.exit(1); }
console.log("\nRESULT: PASS" + (warns.length ? ` (${warns.length} warnings)` : ""));

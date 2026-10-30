import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

// Immutable v1 artifact-tool workbook builder is instantiated with V3's
// bounded-evidence counts only. No original source row or formula is rewritten.
const [builderPath, sourcePath, outputDir] = process.argv.slice(2);
if (!builderPath || !sourcePath || !outputDir) throw Error("USAGE: wrapper builder.mjs V3.json output_dir");
const sourceAbs = path.resolve(sourcePath);
const outputAbs = path.resolve(outputDir);
const source = JSON.parse(await fs.readFile(sourceAbs, "utf8"));
if (source.original_1330_count !== 1330 ||
    source.original_formal_pending_0_1P_unchanged !== 1285 ||
    source.unique_source_ids_with_any_bounded_or_triage_evidence !== 121 ||
    source.high_metadata_60_plus_without_any_linked_additional_evidence !== 16) {
  throw Error("V3 universe and bounded-only custody mismatch");
}
const originalLabel = "Next bottleneck: source-body and existing Full checks for 54 score-60+ IDs without any added evidence.";
const newLabel = "Next bottleneck: primary-body and Full checks for 16 score-60+ IDs without added evidence; native 0.1P remains pending.";
const originalName = "STAGE_A_1330_SOURCE_EVIDENCE_INTEGRATED_20261030.xlsx";
const newName = "STAGE_A_1330_SOURCE_EVIDENCE_INTEGRATED_V3_20261030.xlsx";
let builder = await fs.readFile(path.resolve(builderPath), "utf8");
if (builder.split(originalLabel).length !== 2 || builder.split(originalName).length !== 2) {
  throw Error("Unrecognized locked builder version");
}
builder = builder.replace(originalLabel, newLabel).replace(originalName, newName);
await fs.mkdir(outputAbs, { recursive: true });
try {
  await fs.access(path.join(outputAbs, newName));
  throw Error("create-only workbook already exists");
} catch (err) {
  if (err.code !== "ENOENT") throw err;
}
const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "sbtl-stagea-v3-"));
const modulePath = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
if (!modulePath) throw Error("CODEX_PRIMARY_RUNTIME_NODE_MODULES missing");
await fs.symlink(modulePath, path.join(tmp, "node_modules"), "dir");
const tempBuilder = path.join(tmp, "builder.mjs");
await fs.writeFile(tempBuilder, builder, "utf8");
const runner = process.env.CODEX_PRIMARY_RUNTIME_NODE || process.execPath;
const result = spawnSync(runner, [tempBuilder, sourceAbs, outputAbs], {
  cwd: outputAbs, encoding: "utf8", timeout: 150000, maxBuffer: 16 * 1024 * 1024
});
if (result.stdout) process.stdout.write(result.stdout);
if (result.stderr) process.stderr.write(result.stderr);
if (result.status !== 0) throw Error(`artifact-tool builder failed: ${result.status}`);
const xlsxPath = path.join(outputAbs, newName);
console.log(JSON.stringify({ workbook: xlsxPath, bytes: (await fs.stat(xlsxPath)).size, high_without_evidence: 16 }));

import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

// The v1 @oai/artifact-tool builder and its exported workbook stay immutable.
// This wrapper creates a TEMPORARY text-only derivative in the OS temp folder,
// changes only the computed next-bottleneck label and new output file name,
// then invokes the same artifact-tool generator on the create-only V2 overlay.
const [builderPath, sourcePath, outputDir] = process.argv.slice(2);
if (!builderPath || !sourcePath || !outputDir) {
  throw Error("USAGE: wrapper v1-builder.mjs overlay_v2.json output_dir");
}
const builderAbs = path.resolve(builderPath);
const sourceAbs = path.resolve(sourcePath);
const outputAbs = path.resolve(outputDir);
const source = JSON.parse(await fs.readFile(sourceAbs, "utf8"));
if (source.original_1330_count !== 1330 ||
    source.original_formal_pending_0_1P_unchanged !== 1285 ||
    source.unique_source_ids_with_any_bounded_or_triage_evidence !== 97 ||
    source.high_metadata_60_plus_without_any_linked_additional_evidence !== 40) {
  throw Error("V2 source universe / custody numbers mismatch");
}

let builder = await fs.readFile(builderAbs, "utf8");
const oldLabel = "Next bottleneck: source-body and existing Full checks for 54 score-60+ IDs without any added evidence.";
const newLabel = "Next bottleneck: source-body and existing Full checks for 40 score-60+ IDs without added evidence.";
const oldName = "STAGE_A_1330_SOURCE_EVIDENCE_INTEGRATED_20261030.xlsx";
const newName = "STAGE_A_1330_SOURCE_EVIDENCE_INTEGRATED_V2_20261030.xlsx";
if (builder.split(oldLabel).length !== 2 || builder.split(oldName).length !== 2) {
  throw Error("Unexpected v1 builder version; would not perform replacement");
}
builder = builder.replace(oldLabel, newLabel).replace(oldName, newName);
await fs.mkdir(outputAbs, { recursive: true });
try {
  await fs.access(path.join(outputAbs, newName));
  throw Error("create-only output workbook already exists");
} catch (error) {
  if (error.message !== "create-only output workbook already exists" && error.code !== "ENOENT") throw error;
  if (error.message === "create-only output workbook already exists") throw error;
}

const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "sbtl-stagea-v2-"));
const tempBuilder = path.join(tmpDir, "builder.mjs");
const modulePath = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
if (!modulePath) throw Error("CODEX_PRIMARY_RUNTIME_NODE_MODULES is required");
await fs.symlink(modulePath, path.join(tmpDir, "node_modules"), "dir");
await fs.writeFile(tempBuilder, builder, "utf8");
const runner = process.env.CODEX_PRIMARY_RUNTIME_NODE || process.execPath;
const result = spawnSync(runner, [tempBuilder, sourceAbs, outputAbs], {
  cwd: outputAbs, encoding: "utf8", timeout: 150000, maxBuffer: 16 * 1024 * 1024
});
if (result.stdout) process.stdout.write(result.stdout);
if (result.stderr) process.stderr.write(result.stderr);
if (result.status !== 0) throw Error("Artifact-tool generator failed: " + result.status);
const finalPath = path.join(outputAbs, newName);
const stat = await fs.stat(finalPath);
console.log(JSON.stringify({ v2_workbook: finalPath, bytes: stat.size, high_without_evidence: 40 }));

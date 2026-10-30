import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

// This builder is copied to a conversation-scoped OS tmp dir before execution.
// Input/output locations come from explicit CLI arguments, never from CWD.
const [inputPath, outputDir] = process.argv.slice(2);
if (!inputPath || !outputDir) throw new Error("USAGE: builder input.json output_dir");
const input = JSON.parse(await fs.readFile(inputPath, "utf8"));
const originals = input.source_rows;
if (originals.length !== 1330 || input.original_formal_pending_0_1P_unchanged !== 1285) {
  throw new Error("Input Stage A universe or formal audit invariant failed");
}

const wb = Workbook.create();
const summary = wb.worksheets.add("Overview");
const detail = wb.worksheets.add("Source evidence");
summary.tabColor = "#173652";
summary.showGridLines = false;
detail.showGridLines = false;
const navy = "#193753";
const light = "#EDF3F7";
const orange = "#AD6800";

summary.getRange("A2").values = [["SBTL_HUB Stage A source reconciliation"]];
summary.getRange("A3").values = [["2026-10-30 KST · 1,330 original Source IDs · evidence-only integration"]];
summary.getRange("A2:G2").format.font = { name: "Arial", size: 15, bold: true, color: navy };
summary.getRange("A3:G3").format.font = { name: "Arial", size: 10, italic: true, color: "#536477" };
summary.getRange("A4:G4").format.borders = { bottom: { style: "thin", color: "#AEBFCA" } };

const metricNames = [
  "Original Source IDs",
  "Prior individual 0.1P records",
  "Formal individual 0.1P pending",
  "Source IDs with added evidence",
  "Source IDs without added evidence",
  "Pending review IDs scored 60+",
  "Scored 60+ with added evidence",
  "Scored 60+ without added evidence",
  "Formal Stage A native status",
  "New strict promotions",
];
summary.getRange("A6:A15").values = metricNames.map((v) => [v]);
const form = [
  "=COUNTA('Source evidence'!B5:B1334)",
  '=COUNTIFS(\'Source evidence\'!F5:F1334,"PREVIOUS_0_1P_INDIVIDUAL_REVIEW_PRESERVED")',
  '=COUNTIFS(\'Source evidence\'!F5:F1334,"NATIVE_INDIVIDUAL_0_1P_PENDING")',
  '=COUNTIFS(\'Source evidence\'!H5:H1334,"<>NO_ADDITIONAL_EVIDENCE_ON_THIS_ID")',
  '=COUNTIFS(\'Source evidence\'!H5:H1334,"NO_ADDITIONAL_EVIDENCE_ON_THIS_ID")',
  '=COUNTIFS(\'Source evidence\'!D5:D1334,"candidate_review_pool",\'Source evidence\'!E5:E1334,">=60",\'Source evidence\'!F5:F1334,"NATIVE_INDIVIDUAL_0_1P_PENDING")',
  '=COUNTIFS(\'Source evidence\'!D5:D1334,"candidate_review_pool",\'Source evidence\'!E5:E1334,">=60",\'Source evidence\'!F5:F1334,"NATIVE_INDIVIDUAL_0_1P_PENDING",\'Source evidence\'!H5:H1334,"<>NO_ADDITIONAL_EVIDENCE_ON_THIS_ID")',
  '=COUNTIFS(\'Source evidence\'!D5:D1334,"candidate_review_pool",\'Source evidence\'!E5:E1334,">=60",\'Source evidence\'!F5:F1334,"NATIVE_INDIVIDUAL_0_1P_PENDING",\'Source evidence\'!H5:H1334,"NO_ADDITIONAL_EVIDENCE_ON_THIS_ID")',
];
summary.getRange("B6:B13").formulas = form.map((v) => [v]);
summary.getRange("B14:B15").values = [["HOLD — native not executed"], [0]];

summary.getRange("A17:B17").values = [["Original Stage A pool", "Source IDs"]];
const poolNames = ["candidate_review_pool", "watchlist_context_pool", "existing_reinforcement", "strict_passed_spec"];
summary.getRange("A18:A21").values = poolNames.map((v) => [v]);
summary.getRange("B18:B21").formulas = poolNames.map((v) => [`=COUNTIFS('Source evidence'!D5:D1334,"${v}")`]);
summary.getRange("A23").values = [["Evidence links are bounded research, not formal 0.1P outcomes."]];
summary.getRange("A24").values = [["Metadata score orders review only; an identical URL is not proof of the same economic event."]];
summary.getRange("A25").values = [["Multiple event IDs in one source and overlapping earlier Full card projects remain separate until native review."]];
summary.getRange("A27").values = [["Locked source SHA256: " + input.original_csv_sha256]];
summary.getRange("A29").values = [["Next bottleneck: source-body and existing Full checks for 54 score-60+ IDs without any added evidence."]];
summary.getRange("A6:B15").format.font = { name: "Arial", size: 10, color: navy };
summary.getRange("A17:B21").format.font = { name: "Arial", size: 10, color: navy };
summary.getRange("A17:B17").format = { fill: navy, font: { name: "Arial", color: "#FFFFFF", bold: true, size: 10 } };
summary.getRange("A6:B6").format.fill = light;
summary.getRange("A8:B8").format.fill = "#FFF2D5";
summary.getRange("A13:B13").format.fill = "#FFF2D5";
summary.getRange("B14").format.font = { name: "Arial", bold: true, size: 10, color: orange };
summary.getRange("A23:A29").format.font = { name: "Arial", size: 10, color: "#48596A" };
summary.getRange("B6:B13").setNumberFormat("#,##0");
summary.getRange("B15").setNumberFormat("#,##0");
summary.getRange("B18:B21").setNumberFormat("#,##0");
summary.getRange("A:A").format.columnWidth = 55;
summary.getRange("B:B").format.columnWidth = 29;
summary.getRange("1:1").format.rowHeight = 15;
summary.getRange("2:2").format.rowHeight = 31;

detail.getRange("A2").values = [["Source ID evidence register — original population preserved"]];
detail.getRange("A3").values = [["Original pool, score, formal review state and URL identity are immutable; case labels are provisional."]];
detail.getRange("A2:L2").format.font = { name: "Arial", size: 13, bold: true, color: navy };
detail.getRange("A3:L3").format.font = { name: "Arial", size: 9, italic: true, color: "#536477" };
const headers = [
  "Original row", "Source ID", "Headline (original)", "Original pool", "Score (metadata)",
  "0.1P formal state", "Original cluster ID", "Added evidence scope",
  "Case package IDs (provisional)", "Group cases (not allocated to this ID)",
  "Original source URL", "Evidence files",
];
detail.getRange("A4:L4").values = [headers];
const matrix = originals.map((r) => [
  r.source_row_index,
  r.candidate_id,
  r.headline_raw,
  r.original_stage_a_pool,
  r.metadata_score_original_not_selection_decision,
  r.native_0_1P_state,
  r.original_economic_event_cluster_id,
  r.additional_evidence_scope,
  r.provisional_case_package_ids_NOT_FORMAL_CLUSTER.join("; "),
  r.group_subject_case_ids_NOT_ASSIGNED_PER_SOURCE.join("; "),
  r.primary_url_original,
  r.evidence_artifacts.join("; "),
]);
detail.getRange("A5:L1334").values = matrix;
const tbl = detail.tables.add("A4:L1334", true, "StageASourceEvidence");
tbl.showBandedColumns = false;
detail.getRange("A4:L4").format = {
  fill: navy,
  font: { name: "Arial", bold: true, color: "#FFFFFF", size: 10 },
};
detail.getRange("A5:L1334").format.font = { name: "Arial", size: 9, color: "#233548" };
detail.getRange("A4:L1334").format.verticalAlignment = "center";
detail.getRange("A4:L4").format.rowHeight = 29;
detail.getRange("A5:L1334").format.rowHeight = 18;
detail.getRange("A:A").format.columnWidth = 14;
detail.getRange("B:B").format.columnWidth = 38;
detail.getRange("C:C").format.columnWidth = 72;
detail.getRange("D:D").format.columnWidth = 28;
detail.getRange("E:E").format.columnWidth = 20;
detail.getRange("F:F").format.columnWidth = 37;
detail.getRange("G:G").format.columnWidth = 38;
detail.getRange("H:H").format.columnWidth = 41;
detail.getRange("I:I").format.columnWidth = 68;
detail.getRange("J:J").format.columnWidth = 68;
detail.getRange("K:K").format.columnWidth = 70;
detail.getRange("L:L").format.columnWidth = 83;
detail.getRange("A5:A1334").setNumberFormat("#,##0");
detail.getRange("E5:E1334").setNumberFormat("#,##0");
detail.freezePanes.freezeRows(4);
detail.freezePanes.freezeColumns(2);

// Independent source-key readback from the in-memory workbook, before export.
const xIds = detail.getRange("B5:B1334").values.map((r) => r[0]);
if (xIds.length !== 1330 || xIds.some((v, i) => v !== originals[i].candidate_id)) {
  throw new Error("Workbook source ID order or coverage mismatch");
}
wb.recalculate();
const keyRanges = ["Overview!A6:B15", "Overview!A17:B21"];
for (const range of keyRanges) {
  const checked = await wb.inspect({ kind: "table", range, include: "values,formulas", tableMaxRows: 12, tableMaxCols: 3, maxChars: 6000 });
  console.log("INSPECT " + range + "\n" + checked.ndjson);
}
const errors = await wb.inspect({kind:"match", searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options:{useRegex:true,maxResults:50}, maxChars:3000});
console.log("FORMULA_ERROR_SCAN\n" + errors.ndjson);

await fs.mkdir(outputDir, {recursive:true});
for (const [sheetName, range, stem] of [
  ["Overview", "A1:B29", "stage_a_overview_preview.png"],
  ["Source evidence", "A2:F10", "stage_a_source_preview.png"],
]) {
  const preview = await wb.render({ sheetName, range, scale: 1.5, format:"png" });
  await fs.writeFile(path.join(outputDir, stem), new Uint8Array(await preview.arrayBuffer()));
}
const outputName = "STAGE_A_1330_SOURCE_EVIDENCE_INTEGRATED_20261030.xlsx";
const outputFile = path.join(outputDir, outputName);
const out = await SpreadsheetFile.exportXlsx(wb);
await out.save(outputFile);
console.log(JSON.stringify({
  workbook: outputFile,
  original_source_ids: xIds.length,
  first_source_id: xIds[0],
  last_source_id: xIds.at(-1),
  original_csv_sha256: input.original_csv_sha256,
  native_stage_a: "HOLD_NOT_EXECUTED",
}, null, 2));

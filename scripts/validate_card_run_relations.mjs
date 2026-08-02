#!/usr/bin/env node
import {
  existsSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve, sep } from "node:path";

class ValidationError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

const fail = (code, message) => {
  throw new ValidationError(code, message);
};

const readJson = (path, label) => {
  let raw;
  try {
    raw = readFileSync(path, "utf8").replace(/^\uFEFF/, "");
  } catch (error) {
    fail("BLOCKED_RELATED_RUN_INVALID", `${label}: 읽기 실패 — ${path}: ${error.message}`);
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    fail("BLOCKED_RELATED_RUN_INVALID", `${label}: JSON 파싱 실패 — ${path}: ${error.message}`);
  }
};

const resolveRepoJson = (root, reference, label) => {
  if (typeof reference !== "string" || !reference.trim()) {
    fail("BLOCKED_RELATED_RUN_INVALID", `${label}: 빈 reference`);
  }
  if (!reference.toLowerCase().endsWith(".json")) {
    fail("BLOCKED_RELATED_RUN_INVALID", `${label}: JSON run이어야 함 — ${reference}`);
  }
  const absoluteRoot = resolve(root);
  const absolute = resolve(absoluteRoot, reference);
  if (absolute !== absoluteRoot && !absolute.startsWith(`${absoluteRoot}${sep}`)) {
    fail("BLOCKED_RELATED_RUN_INVALID", `${label}: repository 밖 경로 — ${reference}`);
  }
  if (!existsSync(absolute)) {
    fail("BLOCKED_RELATED_RUN_INVALID", `${label}: 파일 없음 — ${reference}`);
  }
  const stat = statSync(absolute);
  if (!stat.isFile() || stat.size <= 0) {
    fail("BLOCKED_RELATED_RUN_INVALID", `${label}: 비어 있거나 파일이 아님 — ${reference}`);
  }
  return absolute;
};

const requiredPatchesForSide = (operation, cardId, counterpartId) => [
  { path: "/related/-", op: "add", value: counterpartId, kind: "published edge" },
  { path: "/related_ids/-", op: "add", value: counterpartId, kind: "legacy edge mirror" },
  { path: "/related_lineage/related_ids/-", op: "add", value: counterpartId, kind: "lineage edge" },
  { path: "/related_lineage/relation_type", value: operation.relation_type, kind: "lineage relation_type" },
  { path: "/related_lineage/reason", value: operation.lineage_reason, kind: "lineage reason" },
  {
    path: "/related_lineage/event_stage_relationship",
    value: operation.event_stage_relationship,
    kind: "lineage event_stage_relationship",
  },
  { path: "/related_lineage/direction", value: operation.direction, kind: "lineage direction" },
].map((requirement) => ({ ...requirement, card_id: cardId }));

const validatePatchShape = (patch, label) => {
  if (!patch || typeof patch !== "object" || Array.isArray(patch)) {
    fail("BLOCKED_RELATED_PATCH_INVALID", `${label}: patch 객체 필요`);
  }
  for (const key of ["card_id", "op", "path"]) {
    if (typeof patch[key] !== "string" || !patch[key].trim()) {
      fail("BLOCKED_RELATED_PATCH_INVALID", `${label}.${key} 누락`);
    }
  }
  if (!("value" in patch)) {
    fail("BLOCKED_RELATED_PATCH_INVALID", `${label}.value 누락`);
  }
};

const findMatchingPatches = (operation, requirement) => operation.patches.filter((patch) =>
  patch.card_id === requirement.card_id && patch.path === requirement.path);

const validateRequiredSide = (operation, cardId, counterpartId, label) => {
  const requirements = requiredPatchesForSide(operation, cardId, counterpartId);
  for (const requirement of requirements) {
    const matches = findMatchingPatches(operation, requirement);
    if (matches.length !== 1) {
      const code = requirement.path === "/related/-"
        ? "BLOCKED_RELATED_PUBLISHED_EDGE_MISSING"
        : "BLOCKED_RELATED_LINEAGE_INCOMPLETE";
      fail(
        code,
        `${label}: ${cardId} ${requirement.kind} patch는 정확히 1개여야 함 — ${requirement.path}, found ${matches.length}`,
      );
    }
    const [patch] = matches;
    if (requirement.op && patch.op !== requirement.op) {
      fail("BLOCKED_RELATED_PATCH_INVALID", `${label}: ${requirement.path}는 ${requirement.op}여야 함`);
    }
    if (!requirement.op && !["add", "replace"].includes(patch.op)) {
      fail("BLOCKED_RELATED_PATCH_INVALID", `${label}: ${requirement.path}는 add 또는 replace여야 함`);
    }
    if (patch.value !== requirement.value) {
      fail(
        "BLOCKED_RELATED_PATCH_VALUE_MISMATCH",
        `${label}: ${cardId} ${requirement.path} 값이 선언값과 불일치`,
      );
    }
  }
};

const validateRelatedOperation = (operation, index) => {
  const label = `related_add[${index}]`;
  if (!operation || typeof operation !== "object" || Array.isArray(operation)) {
    fail("BLOCKED_RELATED_RUN_INVALID", `${label}: 객체 필요`);
  }
  for (const key of [
    "source_id", "target_id", "relation_type", "lineage_reason",
    "event_stage_relationship", "direction",
  ]) {
    if (typeof operation[key] !== "string" || !operation[key].trim()) {
      fail("BLOCKED_RELATED_RUN_INVALID", `${label}.${key} 누락`);
    }
  }
  if (!Array.isArray(operation.patches) || !operation.patches.length) {
    fail("BLOCKED_RELATED_RUN_INVALID", `${label}.patches가 비어 있음`);
  }
  operation.patches.forEach((patch, patchIndex) => validatePatchShape(patch, `${label}.patches[${patchIndex}]`));

  const pathKeys = operation.patches.map((patch) => `${patch.card_id}:${patch.path}`);
  if (new Set(pathKeys).size !== pathKeys.length) {
    fail("BLOCKED_RELATED_PATCH_DUPLICATE", `${label}: card_id/path 중복 patch 존재`);
  }

  validateRequiredSide(operation, operation.source_id, operation.target_id, label);
  if (operation.direction === "reciprocal") {
    validateRequiredSide(operation, operation.target_id, operation.source_id, label);
  } else if (operation.direction !== "directional") {
    fail("BLOCKED_RELATED_RUN_INVALID", `${label}.direction은 directional 또는 reciprocal이어야 함`);
  }

  const allowedCards = new Set(
    operation.direction === "reciprocal"
      ? [operation.source_id, operation.target_id]
      : [operation.source_id],
  );
  for (const patch of operation.patches) {
    if (!allowedCards.has(patch.card_id)) {
      fail(
        "BLOCKED_RELATED_UNDECLARED_SIDE_PATCH",
        `${label}: ${operation.direction} 관계에 허용되지 않은 side patch — ${patch.card_id}`,
      );
    }
  }
};

const validateRun = (run) => {
  if (!run || typeof run !== "object" || Array.isArray(run)) {
    fail("BLOCKED_RELATED_RUN_INVALID", "card-run 최상위 객체 필요");
  }
  if (!run.operations || typeof run.operations !== "object" || Array.isArray(run.operations)) {
    fail("BLOCKED_RELATED_RUN_INVALID", "operations 객체 필요");
  }
  if (!Array.isArray(run.operations.related_add)) {
    fail("BLOCKED_RELATED_RUN_INVALID", "operations.related_add 배열 필요");
  }
  run.operations.related_add.forEach(validateRelatedOperation);
  return run.operations.related_add.length;
};

const makePatches = (operation, cardId, counterpartId) => requiredPatchesForSide(
  operation,
  cardId,
  counterpartId,
).map((requirement) => ({
  card_id: cardId,
  op: requirement.op || "replace",
  path: requirement.path,
  value: requirement.value,
}));

const runSelfTest = () => {
  const root = mkdtempSync(join(tmpdir(), "card-run-related-lifecycle-"));
  try {
    mkdirSync(join(root, "runs"), { recursive: true });
    const baseOperation = {
      source_id: "A",
      target_id: "B",
      relation_type: "follow_up",
      lineage_reason: "same project advanced",
      event_stage_relationship: "contract_to_construction",
      direction: "directional",
      patches: [],
    };

    const validDirectional = structuredClone(baseOperation);
    validDirectional.patches = makePatches(validDirectional, "A", "B");
    validateRun({ operations: { related_add: [validDirectional] } });

    const validReciprocal = structuredClone(baseOperation);
    validReciprocal.direction = "reciprocal";
    validReciprocal.patches = [
      ...makePatches(validReciprocal, "A", "B"),
      ...makePatches(validReciprocal, "B", "A"),
    ];
    validateRun({ operations: { related_add: [validReciprocal] } });

    const expectFailure = (operation, expectedCode, label) => {
      let caught = null;
      try {
        validateRun({ operations: { related_add: [operation] } });
      } catch (error) {
        caught = error;
      }
      if (!(caught instanceof ValidationError) || caught.code !== expectedCode) {
        throw new Error(`${label}: expected ${expectedCode}, got ${caught?.code || "PASS"}`);
      }
    };

    const idsOnly = structuredClone(validDirectional);
    idsOnly.patches = idsOnly.patches.filter((patch) => patch.path !== "/related/-");
    expectFailure(idsOnly, "BLOCKED_RELATED_PUBLISHED_EDGE_MISSING", "related_ids-only");

    const relatedOnly = structuredClone(validDirectional);
    relatedOnly.patches = relatedOnly.patches.filter((patch) =>
      !patch.path.startsWith("/related_lineage/"));
    expectFailure(relatedOnly, "BLOCKED_RELATED_LINEAGE_INCOMPLETE", "missing lineage");

    const missingLegacyMirror = structuredClone(validDirectional);
    missingLegacyMirror.patches = missingLegacyMirror.patches.filter((patch) =>
      patch.path !== "/related_ids/-");
    expectFailure(missingLegacyMirror, "BLOCKED_RELATED_LINEAGE_INCOMPLETE", "missing related_ids mirror");

    console.log(
      "PASS: validate_card_run_relations — published edge, related_ids mirror, lineage ID, and lineage metadata are mandatory",
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
};

const parseArgs = (argv) => {
  const options = { run: null, selfTest: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--self-test") options.selfTest = true;
    else if (arg === "--run") {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) fail("INVALID_ARGUMENT", "--run PATH가 필요함");
      options.run = value;
      index += 1;
    } else fail("INVALID_ARGUMENT", `지원하지 않는 인자 ${arg}`);
  }
  return options;
};

try {
  const options = parseArgs(process.argv.slice(2));
  if (options.selfTest) {
    runSelfTest();
    process.exit(0);
  }
  if (!options.run) fail("INVALID_ARGUMENT", "--run PATH가 필요함");
  const absolute = resolveRepoJson(".", options.run, "card run");
  const run = readJson(absolute, "card run");
  const count = validateRun(run);
  console.log(JSON.stringify({
    status: "PASS",
    run_path: options.run,
    related_add_count: count,
    lifecycle_contract: [
      "/related/-",
      "/related_ids/-",
      "/related_lineage/related_ids/-",
      "/related_lineage/relation_type",
      "/related_lineage/reason",
      "/related_lineage/event_stage_relationship",
      "/related_lineage/direction",
    ],
  }, null, 2));
  console.log(`PASS: ${count} related_add operations carry complete published and lineage patches`);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`FAIL [${error.code}]: ${error.message}`);
    process.exit(1);
  }
  throw error;
}

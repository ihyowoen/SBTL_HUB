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
    fail("BLOCKED_RELATED_CONTAINER_INPUT_INVALID", `${label}: 읽기 실패 — ${path}: ${error.message}`);
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    fail("BLOCKED_RELATED_CONTAINER_INPUT_INVALID", `${label}: JSON 파싱 실패 — ${path}: ${error.message}`);
  }
};

const resolveRepoJson = (root, reference, label) => {
  if (typeof reference !== "string" || !reference.trim()) {
    fail("BLOCKED_RELATED_CONTAINER_INPUT_INVALID", `${label}: 빈 reference`);
  }
  if (!reference.toLowerCase().endsWith(".json")) {
    fail("BLOCKED_RELATED_CONTAINER_INPUT_INVALID", `${label}: JSON 파일이어야 함 — ${reference}`);
  }
  const absoluteRoot = resolve(root);
  const absolute = resolve(absoluteRoot, reference);
  if (absolute !== absoluteRoot && !absolute.startsWith(`${absoluteRoot}${sep}`)) {
    fail("BLOCKED_RELATED_CONTAINER_INPUT_INVALID", `${label}: repository 밖 경로 — ${reference}`);
  }
  if (!existsSync(absolute)) {
    fail("BLOCKED_RELATED_CONTAINER_INPUT_INVALID", `${label}: 파일 없음 — ${reference}`);
  }
  const stat = statSync(absolute);
  if (!stat.isFile() || stat.size <= 0) {
    fail("BLOCKED_RELATED_CONTAINER_INPUT_INVALID", `${label}: 비어 있거나 파일이 아님 — ${reference}`);
  }
  return absolute;
};

const assertPreparedRelationContainer = (card, cardId, label) => {
  if (!card || typeof card !== "object" || Array.isArray(card)) {
    fail("BLOCKED_RELATED_CONTAINER_INPUT_INVALID", `${label}: 카드 객체 없음 — ${cardId}`);
  }
  if (!Array.isArray(card.related)) {
    fail(
      "BLOCKED_RELATED_PUBLISHED_CONTAINER_MISSING",
      `${label}: ${cardId}.related 배열이 사전 초기화되어 있지 않음`,
    );
  }
  const lineage = card.related_lineage;
  if (!lineage || typeof lineage !== "object" || Array.isArray(lineage)) {
    fail(
      "BLOCKED_RELATED_LINEAGE_CONTAINER_MISSING",
      `${label}: ${cardId}.related_lineage 객체가 사전 초기화되어 있지 않음`,
    );
  }
  if (!Array.isArray(lineage.related_ids)) {
    fail(
      "BLOCKED_RELATED_LINEAGE_CONTAINER_MISSING",
      `${label}: ${cardId}.related_lineage.related_ids 배열이 사전 초기화되어 있지 않음`,
    );
  }
};

const validateRun = (run, canonical) => {
  if (!run || typeof run !== "object" || Array.isArray(run)) {
    fail("INVALID_RUN", "card-run 최상위 객체 필요");
  }
  if (!run.operations || typeof run.operations !== "object" || Array.isArray(run.operations)) {
    fail("INVALID_RUN", "operations 객체 필요");
  }
  if (!Array.isArray(run.operations.insert) || !Array.isArray(run.operations.related_add)) {
    fail("INVALID_RUN", "operations.insert/related_add 배열 필요");
  }
  if (!canonical || typeof canonical !== "object" || !Array.isArray(canonical.cards)) {
    fail("BLOCKED_RELATED_CONTAINER_INPUT_INVALID", "canonical cards 배열 필요");
  }

  const cardsById = new Map(canonical.cards.map((card) => [card?.id, card]));
  for (const [index, operation] of run.operations.insert.entries()) {
    const card = operation?.card;
    if (!card || typeof card.id !== "string" || !card.id.trim()) {
      fail("INVALID_RUN", `insert[${index}].card.id 누락`);
    }
    cardsById.set(card.id, card);
  }

  let checkedSides = 0;
  run.operations.related_add.forEach((operation, index) => {
    if (!operation || typeof operation !== "object" || Array.isArray(operation)) {
      fail("INVALID_RUN", `related_add[${index}] 객체 필요`);
    }
    const requiredSides = operation.direction === "reciprocal"
      ? [operation.source_id, operation.target_id]
      : [operation.source_id];
    for (const cardId of requiredSides) {
      if (typeof cardId !== "string" || !cardId.trim()) {
        fail("INVALID_RUN", `related_add[${index}] endpoint 누락`);
      }
      const card = cardsById.get(cardId);
      if (!card) {
        fail("BLOCKED_NEW_MISSING_RELATED_TARGETS", `related_add[${index}]: 카드 없음 — ${cardId}`);
      }
      assertPreparedRelationContainer(card, cardId, `related_add[${index}]`);
      checkedSides += 1;
    }
  });
  return { related_add_count: run.operations.related_add.length, checked_sides: checkedSides };
};

const runSelfTest = () => {
  const root = mkdtempSync(join(tmpdir(), "card-run-lineage-containers-"));
  try {
    mkdirSync(join(root, "fixtures"), { recursive: true });
    const canonical = {
      cards: [
        { id: "READY", related: [], related_lineage: { related_ids: [] } },
        { id: "NO_LINEAGE", related: [] },
        { id: "MALFORMED", related: [], related_lineage: { related_ids: { "-": "X" } } },
      ],
    };
    const makeRun = (sourceId) => ({
      operations: {
        insert: [],
        related_add: [{ source_id: sourceId, target_id: "READY", direction: "directional" }],
      },
    });

    validateRun(makeRun("READY"), canonical);

    const expectFailure = (sourceId, expectedCode) => {
      let caught = null;
      try {
        validateRun(makeRun(sourceId), canonical);
      } catch (error) {
        caught = error;
      }
      if (!(caught instanceof ValidationError) || caught.code !== expectedCode) {
        throw new Error(`${sourceId}: expected ${expectedCode}, got ${caught?.code || "PASS"}`);
      }
    };
    expectFailure("NO_LINEAGE", "BLOCKED_RELATED_LINEAGE_CONTAINER_MISSING");
    expectFailure("MALFORMED", "BLOCKED_RELATED_LINEAGE_CONTAINER_MISSING");

    const insertedReady = {
      operations: {
        insert: [{ card: { id: "NEW", related: [], related_lineage: { related_ids: [] } } }],
        related_add: [{ source_id: "NEW", target_id: "READY", direction: "directional" }],
      },
    };
    validateRun(insertedReady, canonical);

    console.log(
      "PASS: validate_card_run_lineage_containers — missing or malformed relation containers fail closed before apply",
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
};

const parseArgs = (argv) => {
  const options = {
    run: null,
    canonical: "data/cards.full.json",
    selfTest: false,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--self-test") options.selfTest = true;
    else if (arg === "--run" || arg === "--canonical") {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) fail("INVALID_ARGUMENT", `${arg} 값이 필요함`);
      if (arg === "--run") options.run = value;
      else options.canonical = value;
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
  const runPath = resolveRepoJson(".", options.run, "card run");
  const canonicalPath = resolveRepoJson(".", options.canonical, "canonical full");
  const result = validateRun(readJson(runPath, "card run"), readJson(canonicalPath, "canonical full"));
  console.log(JSON.stringify({
    status: "PASS",
    run_path: options.run,
    canonical_path: options.canonical,
    ...result,
  }, null, 2));
  console.log(`PASS: ${result.checked_sides} relation sides have initialized array containers`);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`FAIL [${error.code}]: ${error.message}`);
    process.exit(1);
  }
  throw error;
}

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
export const WORKFLOW_V4_COVERAGE_AXES_PATH = process.env.WORKFLOW_V4_COVERAGE_AXES_PATH
  ? resolve(process.env.WORKFLOW_V4_COVERAGE_AXES_PATH)
  : resolve(HERE, "../schemas/workflow-v4-coverage-axes.json");

export class CoverageAxesContractError extends Error {
  constructor(message) {
    super(message);
    this.name = "CoverageAxesContractError";
  }
}

const normalize = (value, label) => {
  if (!Array.isArray(value) || value.length === 0 || value.some((item) => typeof item !== "string" || !item.trim())) {
    throw new CoverageAxesContractError(`workflow V4 coverage axes ${label} must be a non-empty string array`);
  }
  const out = value.map((item) => item.trim());
  if (new Set(out).size !== out.length) {
    throw new CoverageAxesContractError(`workflow V4 coverage axes ${label} contains duplicates`);
  }
  return Object.freeze(out);
};

export function loadWorkflowV4CoverageAxes(contractPath = WORKFLOW_V4_COVERAGE_AXES_PATH) {
  let payload;
  try {
    payload = JSON.parse(readFileSync(contractPath, "utf8").replace(/^\uFEFF/, ""));
  } catch (error) {
    throw new CoverageAxesContractError(`workflow V4 coverage axes contract is unreadable: ${error.message}`);
  }

  if (payload?.schema !== "workflow_v4_coverage_axes_v1") {
    throw new CoverageAxesContractError("workflow V4 coverage axes contract has unexpected schema id");
  }

  return Object.freeze({
    regions: normalize(payload.regions, "regions"),
    topics: normalize(payload.topics, "topics"),
  });
}

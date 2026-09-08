// Official SBTL Monthly Brief publication contract.
//
// `monthly` is also a time-window concept elsewhere in the product. This module
// validates publication authority and the Monthly Brief product shape. Automated
// 30-day/calendar-month analysis must never satisfy this contract by accident.

export const MONTHLY_BRIEF_SCHEMA_VERSION = "monthly-brief.v1";
export const MONTHLY_BRIEF_PRODUCT_NAME = "SBTL Monthly Brief";
export const OFFICIAL_PUBLICATION_CLASS = "official_editorial";
export const OFFICIAL_PUBLICATION_MODE = "editorial_curated";
export const PUBLIC_STATUSES = new Set(["published", "revised"]);

const SHA40 = /^[0-9a-f]{40}$/;
const MONTH = /^\d{4}-(0[1-9]|1[0-2])$/;
const DATE = /^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])$/;
const QC_FIELDS = ["evidence_status", "red_team_status", "editorial_coherence_status", "language_terminology_status"];

const LIBRARY_KEYS = new Set(["schema_version", "updated_at", "items"]);
const ITEM_KEYS = new Set([
  "id", "product_name", "month", "revision", "status", "publication_class", "publication_mode",
  "published_at", "title", "executive_diagnosis", "what_changed", "source_baseline", "source_card_ids",
  "key_flows", "watch", "refs", "qc", "approval",
]);
const BASELINE_KEYS = new Set(["main_commit_sha", "full_blob_sha", "source_month_count"]);
const FLOW_KEYS = new Set(["id", "title", "summary", "card_ids"]);
const REF_KEYS = new Set(["n", "id", "title", "date", "url"]);
const QC_KEYS = new Set([...QC_FIELDS, "reviewed_at", "reviewer_role", "notes"]);
const APPROVAL_KEYS = new Set(["status", "approved_at", "reviewer_role", "notes"]);

function nonEmptyString(v) {
  return typeof v === "string" && v.trim().length > 0;
}

function validIsoDate(v) {
  if (!nonEmptyString(v)) return false;
  const m = v.match(DATE);
  if (!m) return false;
  const year = Number(m[1]);
  const month = Number(m[2]);
  const day = Number(m[3]);
  const d = new Date(Date.UTC(year, month - 1, day));
  return d.getUTCFullYear() === year && d.getUTCMonth() + 1 === month && d.getUTCDate() === day;
}

function push(errors, path, message) {
  errors.push(`${path}: ${message}`);
}

function validateAllowedKeys(errors, value, path, allowed) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return;
  Object.keys(value).forEach((key) => {
    if (!allowed.has(key)) push(errors, `${path}.${key}`, "is not allowed by the Monthly Brief contract");
  });
}

function validateStringArray(errors, value, path, { min = 0 } = {}) {
  if (!Array.isArray(value)) {
    push(errors, path, "must be an array");
    return;
  }
  if (value.length < min) push(errors, path, `must contain at least ${min} item(s)`);
  const seen = new Set();
  value.forEach((v, i) => {
    if (!nonEmptyString(v)) push(errors, `${path}[${i}]`, "must be a non-empty string");
    else if (seen.has(v)) push(errors, `${path}[${i}]`, "must not duplicate an earlier value");
    else seen.add(v);
  });
}

function validateFlow(errors, flow, path) {
  if (!flow || typeof flow !== "object" || Array.isArray(flow)) {
    push(errors, path, "must be an object");
    return;
  }
  validateAllowedKeys(errors, flow, path, FLOW_KEYS);
  if (!nonEmptyString(flow.id)) push(errors, `${path}.id`, "is required");
  if (!nonEmptyString(flow.title)) push(errors, `${path}.title`, "is required");
  if (!nonEmptyString(flow.summary)) push(errors, `${path}.summary`, "is required");
  validateStringArray(errors, flow.card_ids, `${path}.card_ids`, { min: 1 });
}

function validateRef(errors, ref, path, expectedN) {
  if (!ref || typeof ref !== "object" || Array.isArray(ref)) {
    push(errors, path, "must be an object");
    return;
  }
  validateAllowedKeys(errors, ref, path, REF_KEYS);
  if (!Number.isInteger(ref.n) || ref.n < 1) push(errors, `${path}.n`, "must be a positive integer");
  else if (ref.n !== expectedN) push(errors, `${path}.n`, `must equal ${expectedN} so public citations are contiguous and ordered`);
  if (!nonEmptyString(ref.id)) push(errors, `${path}.id`, "is required");
  if (!nonEmptyString(ref.title)) push(errors, `${path}.title`, "is required");
  if (!validIsoDate(ref.date)) push(errors, `${path}.date`, "must be a real YYYY-MM-DD calendar date");
  if (ref.url != null && typeof ref.url !== "string") push(errors, `${path}.url`, "must be a string when present");
}

function validateFlowEvidence(errors, flows, sourceIds, path) {
  (flows || []).forEach((flow, fi) => {
    (flow?.card_ids || []).forEach((id, ci) => {
      if (!sourceIds.has(id)) push(errors, `${path}[${fi}].card_ids[${ci}]`, "must exist in source_card_ids");
    });
  });
}

function validateQc(errors, qc, path) {
  if (!qc || typeof qc !== "object" || Array.isArray(qc)) {
    push(errors, path, "is required");
    return;
  }
  validateAllowedKeys(errors, qc, path, QC_KEYS);
  for (const field of QC_FIELDS) {
    if (qc[field] !== "PASS") push(errors, `${path}.${field}`, "must equal PASS");
  }
  if (qc.reviewed_at != null && !validIsoDate(qc.reviewed_at)) push(errors, `${path}.reviewed_at`, "must be a real YYYY-MM-DD calendar date when present");
  if (qc.reviewer_role != null && !nonEmptyString(qc.reviewer_role)) push(errors, `${path}.reviewer_role`, "must be a non-empty string when present");
}

export function validateMonthlyBriefItem(item, path = "item") {
  const errors = [];
  if (!item || typeof item !== "object" || Array.isArray(item)) return [`${path}: must be an object`];
  validateAllowedKeys(errors, item, path, ITEM_KEYS);

  if (!nonEmptyString(item.id)) push(errors, `${path}.id`, "is required");
  if (item.product_name !== MONTHLY_BRIEF_PRODUCT_NAME) push(errors, `${path}.product_name`, `must equal ${MONTHLY_BRIEF_PRODUCT_NAME}`);
  if (!nonEmptyString(item.month) || !MONTH.test(item.month)) push(errors, `${path}.month`, "must be YYYY-MM");
  if (!Number.isInteger(item.revision) || item.revision < 1) push(errors, `${path}.revision`, "must be an integer >= 1");
  if (!PUBLIC_STATUSES.has(item.status)) push(errors, `${path}.status`, "must be published or revised in the public library");
  if (item.status === "published" && item.revision !== 1) push(errors, `${path}.revision`, "published status is reserved for revision 1; later versions use revised");
  if (item.status === "revised" && (!Number.isInteger(item.revision) || item.revision < 2)) push(errors, `${path}.revision`, "revised status requires revision >= 2");
  if (item.publication_class !== OFFICIAL_PUBLICATION_CLASS) push(errors, `${path}.publication_class`, `must equal ${OFFICIAL_PUBLICATION_CLASS}`);
  if (item.publication_mode !== OFFICIAL_PUBLICATION_MODE) push(errors, `${path}.publication_mode`, `must equal ${OFFICIAL_PUBLICATION_MODE}`);
  if (!validIsoDate(item.published_at)) push(errors, `${path}.published_at`, "must be a real YYYY-MM-DD calendar date");
  if (!nonEmptyString(item.title)) push(errors, `${path}.title`, "is required");
  if (!nonEmptyString(item.executive_diagnosis)) push(errors, `${path}.executive_diagnosis`, "is required");
  if (!nonEmptyString(item.what_changed)) push(errors, `${path}.what_changed`, "is required");

  const baseline = item.source_baseline;
  if (!baseline || typeof baseline !== "object" || Array.isArray(baseline)) {
    push(errors, `${path}.source_baseline`, "is required");
  } else {
    validateAllowedKeys(errors, baseline, `${path}.source_baseline`, BASELINE_KEYS);
    if (!nonEmptyString(baseline.main_commit_sha) || !SHA40.test(baseline.main_commit_sha)) push(errors, `${path}.source_baseline.main_commit_sha`, "must be a 40-character lowercase git SHA");
    if (!nonEmptyString(baseline.full_blob_sha) || !SHA40.test(baseline.full_blob_sha)) push(errors, `${path}.source_baseline.full_blob_sha`, "must be a 40-character lowercase git SHA");
    if (!Number.isInteger(baseline.source_month_count) || baseline.source_month_count < 0) push(errors, `${path}.source_baseline.source_month_count`, "must be an integer >= 0");
  }

  validateStringArray(errors, item.source_card_ids, `${path}.source_card_ids`, { min: 1 });

  if (!Array.isArray(item.key_flows) || item.key_flows.length < 1) {
    push(errors, `${path}.key_flows`, "must contain at least one key flow");
  } else {
    const flowIds = new Set();
    item.key_flows.forEach((flow, i) => {
      validateFlow(errors, flow, `${path}.key_flows[${i}]`);
      if (nonEmptyString(flow?.id)) {
        if (flowIds.has(flow.id)) push(errors, `${path}.key_flows[${i}].id`, "must be unique within the brief");
        flowIds.add(flow.id);
      }
    });
  }

  if (item.watch != null) validateStringArray(errors, item.watch, `${path}.watch`);

  if (!Array.isArray(item.refs) || item.refs.length < 1) {
    push(errors, `${path}.refs`, "must contain at least one reference");
  } else {
    const refIds = new Set();
    item.refs.forEach((ref, i) => {
      validateRef(errors, ref, `${path}.refs[${i}]`, i + 1);
      if (nonEmptyString(ref?.id)) {
        if (refIds.has(ref.id)) push(errors, `${path}.refs[${i}].id`, "must be unique");
        refIds.add(ref.id);
      }
    });
  }

  validateQc(errors, item.qc, `${path}.qc`);

  const approval = item.approval;
  if (!approval || typeof approval !== "object" || Array.isArray(approval)) {
    push(errors, `${path}.approval`, "is required");
  } else {
    validateAllowedKeys(errors, approval, `${path}.approval`, APPROVAL_KEYS);
    if (approval.status !== "APPROVED") push(errors, `${path}.approval.status`, "must equal APPROVED");
    if (!validIsoDate(approval.approved_at)) push(errors, `${path}.approval.approved_at`, "must be a real YYYY-MM-DD calendar date");
    if (!nonEmptyString(approval.reviewer_role)) push(errors, `${path}.approval.reviewer_role`, "is required");
    if (validIsoDate(approval.approved_at) && validIsoDate(item.published_at) && approval.approved_at > item.published_at) {
      push(errors, `${path}.approval.approved_at`, "cannot be later than published_at");
    }
  }

  if (Array.isArray(item.source_card_ids)) {
    const sourceIds = new Set(item.source_card_ids);
    validateFlowEvidence(errors, item.key_flows, sourceIds, `${path}.key_flows`);
    if (Array.isArray(item.refs)) {
      const refIds = new Set(item.refs.map((r) => r?.id).filter(nonEmptyString));
      item.source_card_ids.forEach((id, i) => {
        if (nonEmptyString(id) && !refIds.has(id)) push(errors, `${path}.source_card_ids[${i}]`, "must have a matching refs[].id entry");
      });
      item.refs.forEach((ref, i) => {
        if (nonEmptyString(ref?.id) && !sourceIds.has(ref.id)) push(errors, `${path}.refs[${i}].id`, "must exist in source_card_ids");
      });
    }
  }

  return errors;
}

export function validateMonthlyBriefLibrary(library) {
  const errors = [];
  if (!library || typeof library !== "object" || Array.isArray(library)) return ["library: must be an object"];
  validateAllowedKeys(errors, library, "library", LIBRARY_KEYS);
  if (library.schema_version !== MONTHLY_BRIEF_SCHEMA_VERSION) push(errors, "library.schema_version", `must equal ${MONTHLY_BRIEF_SCHEMA_VERSION}`);
  if (library.updated_at != null && !validIsoDate(library.updated_at)) push(errors, "library.updated_at", "must be null or a real YYYY-MM-DD calendar date");
  if (!Array.isArray(library.items)) {
    push(errors, "library.items", "must be an array");
    return errors;
  }

  const ids = new Set();
  const monthRevision = new Set();
  library.items.forEach((item, i) => {
    errors.push(...validateMonthlyBriefItem(item, `library.items[${i}]`));
    if (nonEmptyString(item?.id)) {
      if (ids.has(item.id)) push(errors, `library.items[${i}].id`, "must be unique");
      ids.add(item.id);
    }
    if (nonEmptyString(item?.month) && Number.isInteger(item?.revision)) {
      const key = `${item.month}#${item.revision}`;
      if (monthRevision.has(key)) push(errors, `library.items[${i}]`, "month + revision must be unique");
      monthRevision.add(key);
    }
  });
  return errors;
}

export function isOfficialMonthlyBrief(item) {
  return !!item
    && item.product_name === MONTHLY_BRIEF_PRODUCT_NAME
    && item.publication_class === OFFICIAL_PUBLICATION_CLASS
    && item.publication_mode === OFFICIAL_PUBLICATION_MODE
    && PUBLIC_STATUSES.has(item.status)
    && QC_FIELDS.every((field) => item.qc?.[field] === "PASS")
    && item.approval?.status === "APPROVED";
}

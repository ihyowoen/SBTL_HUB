// Official SBTL Strategic Brief publication contract.
//
// IMPORTANT: `monthly` is a time window elsewhere in the product. This module
// validates publication authority, not duration. Automated 30-day/calendar-month
// analysis must never satisfy this contract by accident.

export const STRATEGIC_BRIEF_SCHEMA_VERSION = "strategic-brief.v1";
export const OFFICIAL_PUBLICATION_CLASS = "official_editorial";
export const OFFICIAL_PUBLICATION_MODE = "manual_editorial";
export const PUBLIC_STATUSES = new Set(["published", "revised"]);

const SHA40 = /^[0-9a-f]{40}$/;
const MONTH = /^\d{4}-(0[1-9]|1[0-2])$/;
const DATE = /^\d{4}-(0[1-9]|1[0-2])-([0-2]\d|3[01])$/;
const EDITION = /^VOL\.\d{2,}$/;

function nonEmptyString(v) {
  return typeof v === "string" && v.trim().length > 0;
}

function push(errors, path, message) {
  errors.push(`${path}: ${message}`);
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

function validateSignal(errors, signal, path) {
  if (!signal || typeof signal !== "object" || Array.isArray(signal)) {
    push(errors, path, "must be an object");
    return;
  }
  if (!nonEmptyString(signal.id)) push(errors, `${path}.id`, "is required");
  if (!nonEmptyString(signal.title)) push(errors, `${path}.title`, "is required");
  if (!nonEmptyString(signal.summary)) push(errors, `${path}.summary`, "is required");
  validateStringArray(errors, signal.card_ids, `${path}.card_ids`, { min: 1 });
}

function validateRef(errors, ref, path) {
  if (!ref || typeof ref !== "object" || Array.isArray(ref)) {
    push(errors, path, "must be an object");
    return;
  }
  if (!Number.isInteger(ref.n) || ref.n < 1) push(errors, `${path}.n`, "must be a positive integer");
  if (!nonEmptyString(ref.id)) push(errors, `${path}.id`, "is required");
  if (!nonEmptyString(ref.title)) push(errors, `${path}.title`, "is required");
  if (!nonEmptyString(ref.date) || !DATE.test(ref.date)) push(errors, `${path}.date`, "must be YYYY-MM-DD");
  if (ref.url != null && typeof ref.url !== "string") push(errors, `${path}.url`, "must be a string when present");
}

export function validateStrategicBriefItem(item, path = "item") {
  const errors = [];
  if (!item || typeof item !== "object" || Array.isArray(item)) {
    return [`${path}: must be an object`];
  }

  if (!nonEmptyString(item.id)) push(errors, `${path}.id`, "is required");
  if (!nonEmptyString(item.edition) || !EDITION.test(item.edition)) push(errors, `${path}.edition`, "must match VOL.XX");
  if (!nonEmptyString(item.month) || !MONTH.test(item.month)) push(errors, `${path}.month`, "must be YYYY-MM");
  if (!Number.isInteger(item.revision) || item.revision < 1) push(errors, `${path}.revision`, "must be an integer >= 1");
  if (!PUBLIC_STATUSES.has(item.status)) push(errors, `${path}.status`, "must be published or revised in the public library");
  if (item.publication_class !== OFFICIAL_PUBLICATION_CLASS) push(errors, `${path}.publication_class`, `must equal ${OFFICIAL_PUBLICATION_CLASS}`);
  if (item.publication_mode !== OFFICIAL_PUBLICATION_MODE) push(errors, `${path}.publication_mode`, `must equal ${OFFICIAL_PUBLICATION_MODE}`);
  if (!nonEmptyString(item.published_at) || !DATE.test(item.published_at)) push(errors, `${path}.published_at`, "must be YYYY-MM-DD");
  if (!nonEmptyString(item.title)) push(errors, `${path}.title`, "is required");
  if (!nonEmptyString(item.executive_diagnosis)) push(errors, `${path}.executive_diagnosis`, "is required");

  const baseline = item.source_baseline;
  if (!baseline || typeof baseline !== "object" || Array.isArray(baseline)) {
    push(errors, `${path}.source_baseline`, "is required");
  } else {
    if (!nonEmptyString(baseline.main_commit_sha) || !SHA40.test(baseline.main_commit_sha)) push(errors, `${path}.source_baseline.main_commit_sha`, "must be a 40-character lowercase git SHA");
    if (!nonEmptyString(baseline.full_blob_sha) || !SHA40.test(baseline.full_blob_sha)) push(errors, `${path}.source_baseline.full_blob_sha`, "must be a 40-character lowercase git SHA");
    if (!Number.isInteger(baseline.source_month_count) || baseline.source_month_count < 0) push(errors, `${path}.source_baseline.source_month_count`, "must be an integer >= 0");
  }

  validateStringArray(errors, item.source_card_ids, `${path}.source_card_ids`, { min: 1 });

  if (!Array.isArray(item.structural_signals) || item.structural_signals.length < 1) {
    push(errors, `${path}.structural_signals`, "must contain at least one structural signal");
  } else {
    item.structural_signals.forEach((signal, i) => validateSignal(errors, signal, `${path}.structural_signals[${i}]`));
  }

  if (item.watch != null) validateStringArray(errors, item.watch, `${path}.watch`);

  if (!Array.isArray(item.refs) || item.refs.length < 1) {
    push(errors, `${path}.refs`, "must contain at least one reference");
  } else {
    item.refs.forEach((ref, i) => validateRef(errors, ref, `${path}.refs[${i}]`));
    const nums = item.refs.map((r) => r?.n).filter(Number.isInteger);
    if (new Set(nums).size !== nums.length) push(errors, `${path}.refs`, "reference numbers must be unique");
  }

  const approval = item.approval;
  if (!approval || typeof approval !== "object" || Array.isArray(approval)) {
    push(errors, `${path}.approval`, "is required");
  } else {
    if (approval.status !== "APPROVED") push(errors, `${path}.approval.status`, "must equal APPROVED");
    if (!nonEmptyString(approval.approved_at) || !DATE.test(approval.approved_at)) push(errors, `${path}.approval.approved_at`, "must be YYYY-MM-DD");
    if (!nonEmptyString(approval.reviewer_role)) push(errors, `${path}.approval.reviewer_role`, "is required");
  }

  // Cross-field evidence integrity. Every structural-signal card must be within
  // the issue's governed source set, and every source card must be resolvable by
  // at least one reference row in the public artifact.
  if (Array.isArray(item.source_card_ids)) {
    const sourceIds = new Set(item.source_card_ids);
    if (Array.isArray(item.structural_signals)) {
      item.structural_signals.forEach((signal, si) => {
        (signal?.card_ids || []).forEach((id, ci) => {
          if (!sourceIds.has(id)) push(errors, `${path}.structural_signals[${si}].card_ids[${ci}]`, "must exist in source_card_ids");
        });
      });
    }
    if (Array.isArray(item.refs)) {
      const refIds = new Set(item.refs.map((r) => r?.id).filter(nonEmptyString));
      item.source_card_ids.forEach((id, i) => {
        if (nonEmptyString(id) && !refIds.has(id)) push(errors, `${path}.source_card_ids[${i}]`, "must have a matching refs[].id entry");
      });
    }
  }

  return errors;
}

export function validateStrategicBriefLibrary(library) {
  const errors = [];
  if (!library || typeof library !== "object" || Array.isArray(library)) return ["library: must be an object"];
  if (library.schema_version !== STRATEGIC_BRIEF_SCHEMA_VERSION) push(errors, "library.schema_version", `must equal ${STRATEGIC_BRIEF_SCHEMA_VERSION}`);
  if (!Array.isArray(library.items)) {
    push(errors, "library.items", "must be an array");
    return errors;
  }

  const ids = new Set();
  const editionRevision = new Set();
  const monthRevision = new Set();
  library.items.forEach((item, i) => {
    errors.push(...validateStrategicBriefItem(item, `library.items[${i}]`));
    if (nonEmptyString(item?.id)) {
      if (ids.has(item.id)) push(errors, `library.items[${i}].id`, "must be unique");
      ids.add(item.id);
    }
    if (nonEmptyString(item?.edition) && Number.isInteger(item?.revision)) {
      const key = `${item.edition}#${item.revision}`;
      if (editionRevision.has(key)) push(errors, `library.items[${i}]`, "edition + revision must be unique");
      editionRevision.add(key);
    }
    if (nonEmptyString(item?.month) && Number.isInteger(item?.revision)) {
      const key = `${item.month}#${item.revision}`;
      if (monthRevision.has(key)) push(errors, `library.items[${i}]`, "month + revision must be unique");
      monthRevision.add(key);
    }
  });

  return errors;
}

export function isOfficialStrategicBrief(item) {
  return !!item
    && item.publication_class === OFFICIAL_PUBLICATION_CLASS
    && item.publication_mode === OFFICIAL_PUBLICATION_MODE
    && PUBLIC_STATUSES.has(item.status)
    && item.approval?.status === "APPROVED";
}

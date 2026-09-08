import fs from "node:fs";

function replaceOnce(text, from, to, label) {
  const first = text.indexOf(from);
  if (first < 0) throw new Error(`${label}: anchor not found`);
  if (text.indexOf(from, first + from.length) >= 0) throw new Error(`${label}: anchor not unique`);
  return text.slice(0, first) + to + text.slice(first + from.length);
}

// 1) Match the JSON schema's optional-field semantics: absent is allowed, explicit null is not.
{
  const path = "lib/brief/monthlyPublication.js";
  let text = fs.readFileSync(path, "utf8");
  text = replaceOnce(
    text,
    'function nonEmptyString(v) {\n  return typeof v === "string" && v.trim().length > 0;\n}\n',
    'function nonEmptyString(v) {\n  return typeof v === "string" && v.trim().length > 0;\n}\n\nfunction hasOwn(value, key) {\n  return Object.prototype.hasOwnProperty.call(value, key);\n}\n',
    "hasOwn helper",
  );
  text = replaceOnce(text, 'if (ref.url != null && typeof ref.url !== "string")', 'if (hasOwn(ref, "url") && typeof ref.url !== "string")', "ref.url null strictness");
  text = replaceOnce(text, 'if (qc.reviewed_at != null && !validIsoDate(qc.reviewed_at))', 'if (hasOwn(qc, "reviewed_at") && !validIsoDate(qc.reviewed_at))', "qc.reviewed_at null strictness");
  text = replaceOnce(text, 'if (qc.reviewer_role != null && !nonEmptyString(qc.reviewer_role))', 'if (hasOwn(qc, "reviewer_role") && !nonEmptyString(qc.reviewer_role))', "qc.reviewer_role null strictness");
  text = replaceOnce(text, 'if (qc.notes != null && typeof qc.notes !== "string")', 'if (hasOwn(qc, "notes") && typeof qc.notes !== "string")', "qc.notes null strictness");
  text = replaceOnce(text, 'if (item.watch != null) validateStringArray(errors, item.watch, `${path}.watch`);', 'if (hasOwn(item, "watch")) validateStringArray(errors, item.watch, `${path}.watch`);', "watch null strictness");
  text = replaceOnce(text, 'if (approval.notes != null && typeof approval.notes !== "string")', 'if (hasOwn(approval, "notes") && typeof approval.notes !== "string")', "approval.notes null strictness");
  fs.writeFileSync(path, text);
}

// 2) Reserve natural Monthly Brief create variants before the generic auto-analysis matcher.
{
  const path = "lib/chat/appCommand.js";
  let text = fs.readFileSync(path, "utf8");
  text = replaceOnce(
    text,
    'const CMD_MONTHLY_BRIEF_CREATE = new RegExp(`(?:((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월)\\\\s*)?(?:SBTL\\\\s*)?월간\\\\s*브리프(?:을|를)?\\\\s*(?:지금\\\\s*|새로\\\\s*|다시\\\\s*)*(?:만들어|만들|생성|발행|뽑아)${IMPERATIVE_TAIL}`, "i");',
    'const CMD_MONTHLY_BRIEF_CREATE = new RegExp(`(?:((?:\\\\d{4}년\\\\s*)?\\\\d{1,2}월)\\\\s*)?(?:SBTL\\\\s*)?월간\\\\s*브리프(?:을|를)?\\\\s*(?:지금\\\\s*|새로\\\\s*|다시\\\\s*|하나\\\\s*|한\\\\s*개\\\\s*|한\\\\s*번\\\\s*|한번\\\\s*)*(?:만들어|만들|생성|발행|뽑아)${IMPERATIVE_TAIL}`, "i");',
    "Monthly Brief create fillers",
  );
  fs.writeFileSync(path, text);
}

// 3) Make provenance membership failures identify the offending governed card ID.
{
  const path = "lib/brief/monthlyProvenance.js";
  let text = fs.readFileSync(path, "utf8");
  text = replaceOnce(
    text,
    'errors.push(`library.items[${i}].source_card_ids[${j}]: card id does not exist in the declared ${SOURCE_PATH} snapshot`);',
    'errors.push(`library.items[${i}].source_card_ids[${j}]: card id ${id} does not exist in the declared ${SOURCE_PATH} snapshot`);',
    "provenance missing id detail",
  );
  fs.writeFileSync(path, text);
}

// 4) Regression coverage for explicit nulls on every optional field whose schema excludes null.
{
  const path = "__tests__/monthlyBriefPublication.test.js";
  let text = fs.readFileSync(path, "utf8");
  const anchor = '  it("requires baseline provenance and real calendar dates", () => {';
  const test = `  it("rejects explicit nulls for optional fields that do not allow null in the schema", () => {\n    const cases = [\n      ["watch", sample({ watch: null })],\n      ["refs[0].url", (() => { const item = sample(); item.refs[0].url = null; return item; })()],\n      ["qc.reviewed_at", sample({ qc: { ...sample().qc, reviewed_at: null } })],\n      ["qc.reviewer_role", sample({ qc: { ...sample().qc, reviewer_role: null } })],\n      ["qc.notes", sample({ qc: { ...sample().qc, notes: null } })],\n      ["approval.notes", sample({ approval: { ...sample().approval, notes: null } })],\n    ];\n    for (const [field, item] of cases) expect(validateMonthlyBriefItem(item).join("\\n"), field).toContain(field);\n  });\n\n`;
  text = replaceOnce(text, anchor, test + anchor, "explicit null regression test");
  fs.writeFileSync(path, text);
}

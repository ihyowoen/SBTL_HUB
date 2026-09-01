#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { isDeepStrictEqual } from "node:util";

class SchemaValidationError extends Error {
  constructor(message) { super(message); this.name = "SchemaValidationError"; }
}

const readJson = (path, label) => {
  try { return JSON.parse(readFileSync(path, "utf8").replace(/^\uFEFF/, "")); }
  catch (error) { throw new SchemaValidationError(`${label}: ${error.message}`); }
};

const escapePointer = (value) => value.replace(/~1/g, "/").replace(/~0/g, "~");
const resolveRef = (root, ref) => {
  if (typeof ref !== "string" || !ref.startsWith("#/")) {
    throw new SchemaValidationError(`unsupported $ref ${String(ref)}; only local #/ refs are allowed`);
  }
  let node = root;
  for (const token of ref.slice(2).split("/").map(escapePointer)) {
    if (!node || typeof node !== "object" || !Object.prototype.hasOwnProperty.call(node, token)) {
      throw new SchemaValidationError(`unresolvable $ref ${ref}`);
    }
    node = node[token];
  }
  return node;
};

const SUPPORTED_KEYWORDS = new Set([
  "$schema", "$id", "$comment", "$defs", "$ref", "title", "description", "default", "examples",
  "type", "const", "enum",
  "minLength", "maxLength", "pattern", "format",
  "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
  "minItems", "maxItems", "uniqueItems", "items", "contains", "minContains", "maxContains",
  "required", "properties", "additionalProperties",
  "allOf", "anyOf", "oneOf", "not", "if", "then", "else",
]);
const SUPPORTED_FORMATS = new Set(["date", "date-time"]);
const SCHEMA_MAP_KEYS = new Set(["$defs", "properties"]);
const SCHEMA_SINGLE_KEYS = new Set(["items", "contains", "additionalProperties", "not", "if", "then", "else"]);
const SCHEMA_ARRAY_KEYS = new Set(["allOf", "anyOf", "oneOf"]);

function assertSupportedSchema(schema, path = "$") {
  if (schema === true || schema === false) return;
  if (!schema || typeof schema !== "object" || Array.isArray(schema)) {
    throw new SchemaValidationError(`${path}: invalid schema node`);
  }
  for (const key of Object.keys(schema)) {
    if (!SUPPORTED_KEYWORDS.has(key)) {
      throw new SchemaValidationError(`${path}: unsupported JSON Schema keyword ${key}`);
    }
  }
  if (schema.format !== undefined) {
    if (typeof schema.format !== "string" || !SUPPORTED_FORMATS.has(schema.format)) {
      throw new SchemaValidationError(`${path}: unsupported format ${String(schema.format)}`);
    }
  }
  for (const key of SCHEMA_MAP_KEYS) {
    if (schema[key] === undefined) continue;
    if (!schema[key] || typeof schema[key] !== "object" || Array.isArray(schema[key])) {
      throw new SchemaValidationError(`${path}.${key}: schema map must be an object`);
    }
    for (const [name, child] of Object.entries(schema[key])) assertSupportedSchema(child, `${path}.${key}.${name}`);
  }
  for (const key of SCHEMA_SINGLE_KEYS) {
    if (schema[key] !== undefined && typeof schema[key] !== "boolean") assertSupportedSchema(schema[key], `${path}.${key}`);
  }
  for (const key of SCHEMA_ARRAY_KEYS) {
    if (schema[key] === undefined) continue;
    if (!Array.isArray(schema[key])) throw new SchemaValidationError(`${path}.${key}: must be an array`);
    schema[key].forEach((child, index) => assertSupportedSchema(child, `${path}.${key}[${index}]`));
  }
}

const jsonType = (value) => {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  if (typeof value === "number") return Number.isInteger(value) ? "integer" : "number";
  return typeof value;
};
const typeMatches = (value, expected) => {
  const actual = jsonType(value);
  if (expected === "number") return actual === "number" || actual === "integer";
  return actual === expected;
};
const uniqueJson = (values) => {
  for (let i = 0; i < values.length; i += 1) {
    for (let j = i + 1; j < values.length; j += 1) {
      if (isDeepStrictEqual(values[i], values[j])) return false;
    }
  }
  return true;
};

const validCalendarDate = (year, month, day) => {
  const probe = new Date(Date.UTC(year, month - 1, day));
  return probe.getUTCFullYear() === year && probe.getUTCMonth() === month - 1 && probe.getUTCDate() === day;
};
const DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/;
const DATETIME_RE = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-](\d{2}):(\d{2}))$/;
function formatMatches(value, format) {
  if (format === "date") {
    const match = value.match(DATE_RE);
    if (!match) return false;
    return validCalendarDate(Number(match[1]), Number(match[2]), Number(match[3]));
  }
  if (format === "date-time") {
    const match = value.match(DATETIME_RE);
    if (!match) return false;
    const [, ys, ms, ds, hs, mins, ss, oh, om] = match;
    if (!validCalendarDate(Number(ys), Number(ms), Number(ds))) return false;
    if (Number(hs) > 23 || Number(mins) > 59 || Number(ss) > 59 || Number(oh || 0) > 23 || Number(om || 0) > 59) return false;
    return !Number.isNaN(Date.parse(value));
  }
  throw new SchemaValidationError(`unsupported format ${format}`);
}

function validateNode(schema, value, root, path = "$") {
  if (schema === true) return [];
  if (schema === false) return [`${path}: false schema`];
  if (!schema || typeof schema !== "object" || Array.isArray(schema)) return [`${path}: invalid schema node`];
  if (schema.$ref) return validateNode(resolveRef(root, schema.$ref), value, root, path);

  const errors = [];
  if (schema.const !== undefined && !isDeepStrictEqual(value, schema.const)) errors.push(`${path}: expected const ${JSON.stringify(schema.const)}`);
  if (Array.isArray(schema.enum) && !schema.enum.some((candidate) => isDeepStrictEqual(candidate, value))) errors.push(`${path}: value is not in enum`);

  if (schema.type !== undefined) {
    const expected = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!expected.some((type) => typeMatches(value, type))) {
      errors.push(`${path}: expected type ${expected.join("|")}, got ${jsonType(value)}`);
      return errors;
    }
  }

  if (typeof value === "string") {
    if (Number.isInteger(schema.minLength) && value.length < schema.minLength) errors.push(`${path}: minLength ${schema.minLength}`);
    if (Number.isInteger(schema.maxLength) && value.length > schema.maxLength) errors.push(`${path}: maxLength ${schema.maxLength}`);
    if (typeof schema.pattern === "string") {
      let regex;
      try { regex = new RegExp(schema.pattern); }
      catch (error) { throw new SchemaValidationError(`${path}: invalid schema pattern ${schema.pattern}: ${error.message}`); }
      if (!regex.test(value)) errors.push(`${path}: pattern mismatch ${schema.pattern}`);
    }
    if (typeof schema.format === "string" && !formatMatches(value, schema.format)) errors.push(`${path}: format ${schema.format} mismatch`);
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    if (typeof schema.minimum === "number" && value < schema.minimum) errors.push(`${path}: minimum ${schema.minimum}`);
    if (typeof schema.maximum === "number" && value > schema.maximum) errors.push(`${path}: maximum ${schema.maximum}`);
    if (typeof schema.exclusiveMinimum === "number" && value <= schema.exclusiveMinimum) errors.push(`${path}: exclusiveMinimum ${schema.exclusiveMinimum}`);
    if (typeof schema.exclusiveMaximum === "number" && value >= schema.exclusiveMaximum) errors.push(`${path}: exclusiveMaximum ${schema.exclusiveMaximum}`);
    if (typeof schema.multipleOf === "number" && schema.multipleOf > 0) {
      const quotient = value / schema.multipleOf;
      if (Math.abs(quotient - Math.round(quotient)) > 1e-9) errors.push(`${path}: multipleOf ${schema.multipleOf}`);
    }
  } else if (typeof value === "number" && !Number.isFinite(value)) {
    errors.push(`${path}: non-finite JSON number is invalid`);
  }

  if (Array.isArray(value)) {
    if (Number.isInteger(schema.minItems) && value.length < schema.minItems) errors.push(`${path}: minItems ${schema.minItems}`);
    if (Number.isInteger(schema.maxItems) && value.length > schema.maxItems) errors.push(`${path}: maxItems ${schema.maxItems}`);
    if (schema.uniqueItems === true && !uniqueJson(value)) errors.push(`${path}: uniqueItems violated`);
    if (schema.items !== undefined) value.forEach((item, index) => errors.push(...validateNode(schema.items, item, root, `${path}[${index}]`)));
    if (schema.contains !== undefined) {
      const matches = value.filter((item, index) => validateNode(schema.contains, item, root, `${path}[${index}]`).length === 0).length;
      const minimum = Number.isInteger(schema.minContains) ? schema.minContains : 1;
      const maximum = Number.isInteger(schema.maxContains) ? schema.maxContains : null;
      if (matches < minimum || (maximum !== null && matches > maximum)) errors.push(`${path}: contains requirement not satisfied`);
    }
  }

  if (value && typeof value === "object" && !Array.isArray(value)) {
    if (Array.isArray(schema.required)) {
      for (const key of schema.required) if (!Object.prototype.hasOwnProperty.call(value, key)) errors.push(`${path}.${key}: required property missing`);
    }
    const properties = schema.properties && typeof schema.properties === "object" ? schema.properties : {};
    for (const [key, child] of Object.entries(properties)) {
      if (Object.prototype.hasOwnProperty.call(value, key)) errors.push(...validateNode(child, value[key], root, `${path}.${key}`));
    }
    for (const key of Object.keys(value)) {
      if (Object.prototype.hasOwnProperty.call(properties, key)) continue;
      if (schema.additionalProperties === false) errors.push(`${path}.${key}: additional property not allowed`);
      else if (schema.additionalProperties && typeof schema.additionalProperties === "object") errors.push(...validateNode(schema.additionalProperties, value[key], root, `${path}.${key}`));
    }
  }

  if (Array.isArray(schema.allOf)) for (const child of schema.allOf) errors.push(...validateNode(child, value, root, path));
  if (Array.isArray(schema.anyOf) && !schema.anyOf.some((child) => validateNode(child, value, root, path).length === 0)) errors.push(`${path}: anyOf requirement not satisfied`);
  if (Array.isArray(schema.oneOf)) {
    const matches = schema.oneOf.filter((child) => validateNode(child, value, root, path).length === 0).length;
    if (matches !== 1) errors.push(`${path}: oneOf matched ${matches} schemas`);
  }
  if (schema.not !== undefined && validateNode(schema.not, value, root, path).length === 0) errors.push(`${path}: not-schema matched`);
  if (schema.if !== undefined) {
    const condition = validateNode(schema.if, value, root, path).length === 0;
    if (condition && schema.then !== undefined) errors.push(...validateNode(schema.then, value, root, path));
    if (!condition && schema.else !== undefined) errors.push(...validateNode(schema.else, value, root, path));
  }
  return errors;
}

function runSelfTest() {
  const schema = {
    type: "object", additionalProperties: false, required: ["kind", "items", "when"],
    properties: {
      kind: { const: "ok" },
      items: { type: "array", minItems: 1, uniqueItems: true, items: { type: "integer", minimum: 0 } },
      when: { type: "string", format: "date-time" },
      note: { type: ["string", "null"] },
    },
    allOf: [{ if: { properties: { kind: { const: "ok" } }, required: ["kind"] }, then: { required: ["note"] } }],
  };
  assertSupportedSchema(schema);
  const valid = { kind: "ok", items: [1, 2], when: "2026-09-01T00:00:00Z", note: null };
  if (validateNode(schema, valid, schema).length) throw new Error("self-test rejected valid instance");
  const invalid = { kind: "ok", items: [1, 1], when: "2026-02-30T00:00:00Z", extra: true };
  const errors = validateNode(schema, invalid, schema);
  if (!errors.some((error) => error.includes("uniqueItems")) || !errors.some((error) => error.includes("additional property")) || !errors.some((error) => error.includes("format date-time")) || !errors.some((error) => error.includes("note"))) {
    throw new Error(`self-test failed to catch required constraints: ${errors.join("; ")}`);
  }
  let unknownBlocked = false;
  try { assertSupportedSchema({ type: "string", dependentRequired: {} }); }
  catch (error) { unknownBlocked = error instanceof SchemaValidationError; }
  if (!unknownBlocked) throw new Error("self-test failed to block unsupported schema keyword");
  let formatBlocked = false;
  try { assertSupportedSchema({ type: "object", properties: { url: { type: "string", format: "uri" } } }); }
  catch (error) { formatBlocked = error instanceof SchemaValidationError && error.message.includes("unsupported format uri"); }
  if (!formatBlocked) throw new Error("self-test failed to reject unsupported format at schema-load time");
  console.log("PASS: fail-closed JSON Schema subset validator self-test");
}

const args = process.argv.slice(2);
const arg = (name) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : null; };
try {
  if (args.includes("--self-test")) { runSelfTest(); process.exit(0); }
  const schemaPath = arg("--schema"), instancePath = arg("--instance");
  if (!schemaPath || !instancePath) throw new SchemaValidationError("--schema PATH --instance PATH required");
  const schema = readJson(schemaPath, "schema"), instance = readJson(instancePath, "instance");
  assertSupportedSchema(schema);
  const errors = validateNode(schema, instance, schema);
  if (errors.length) {
    console.error("FAIL [BLOCKED_JSON_SCHEMA_NONCOMPLIANT]");
    for (const error of errors.slice(0, 100)) console.error(`- ${error}`);
    if (errors.length > 100) console.error(`- ... ${errors.length - 100} additional errors`);
    process.exit(1);
  }
  console.log(JSON.stringify({ status: "PASS", schema: schemaPath, instance: instancePath }, null, 2));
} catch (error) {
  if (error instanceof SchemaValidationError) { console.error(`FAIL [BLOCKED_JSON_SCHEMA_INVALID]: ${error.message}`); process.exit(1); }
  console.error(`FAIL [BLOCKED_JSON_SCHEMA_INTERNAL]: ${error?.message || String(error)}`);
  process.exit(1);
}

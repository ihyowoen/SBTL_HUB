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

function validateNode(schema, value, root, path = "$") {
  if (schema === true) return [];
  if (schema === false) return [`${path}: false schema`];
  if (!schema || typeof schema !== "object" || Array.isArray(schema)) {
    return [`${path}: invalid schema node`];
  }
  if (schema.$ref) return validateNode(resolveRef(root, schema.$ref), value, root, path);

  const errors = [];
  if (schema.const !== undefined && !isDeepStrictEqual(value, schema.const)) {
    errors.push(`${path}: expected const ${JSON.stringify(schema.const)}`);
  }
  if (Array.isArray(schema.enum) && !schema.enum.some((candidate) => isDeepStrictEqual(candidate, value))) {
    errors.push(`${path}: value is not in enum`);
  }

  if (schema.type !== undefined) {
    const expected = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!expected.some((type) => typeMatches(value, type))) {
      errors.push(`${path}: expected type ${expected.join("|")}, got ${jsonType(value)}`);
      return errors;
    }
  }

  if (typeof value === "string") {
    if (Number.isInteger(schema.minLength) && value.length < schema.minLength) errors.push(`${path}: minLength ${schema.minLength}`);
    if (typeof schema.pattern === "string") {
      let regex;
      try { regex = new RegExp(schema.pattern); }
      catch (error) { throw new SchemaValidationError(`${path}: invalid schema pattern ${schema.pattern}: ${error.message}`); }
      if (!regex.test(value)) errors.push(`${path}: pattern mismatch ${schema.pattern}`);
    }
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    if (typeof schema.minimum === "number" && value < schema.minimum) errors.push(`${path}: minimum ${schema.minimum}`);
    if (typeof schema.maximum === "number" && value > schema.maximum) errors.push(`${path}: maximum ${schema.maximum}`);
  } else if (typeof value === "number" && !Number.isFinite(value)) {
    errors.push(`${path}: non-finite JSON number is invalid`);
  }

  if (Array.isArray(value)) {
    if (Number.isInteger(schema.minItems) && value.length < schema.minItems) errors.push(`${path}: minItems ${schema.minItems}`);
    if (Number.isInteger(schema.maxItems) && value.length > schema.maxItems) errors.push(`${path}: maxItems ${schema.maxItems}`);
    if (schema.uniqueItems === true && !uniqueJson(value)) errors.push(`${path}: uniqueItems violated`);
    if (schema.items !== undefined) {
      value.forEach((item, index) => errors.push(...validateNode(schema.items, item, root, `${path}[${index}]`)));
    }
    if (schema.contains !== undefined && !value.some((item, index) => validateNode(schema.contains, item, root, `${path}[${index}]`).length === 0)) {
      errors.push(`${path}: contains requirement not satisfied`);
    }
  }

  if (value && typeof value === "object" && !Array.isArray(value)) {
    if (Array.isArray(schema.required)) {
      for (const key of schema.required) {
        if (!Object.prototype.hasOwnProperty.call(value, key)) errors.push(`${path}.${key}: required property missing`);
      }
    }
    const properties = schema.properties && typeof schema.properties === "object" ? schema.properties : {};
    for (const [key, child] of Object.entries(properties)) {
      if (Object.prototype.hasOwnProperty.call(value, key)) errors.push(...validateNode(child, value[key], root, `${path}.${key}`));
    }
    if (schema.additionalProperties === false) {
      for (const key of Object.keys(value)) {
        if (!Object.prototype.hasOwnProperty.call(properties, key)) errors.push(`${path}.${key}: additional property not allowed`);
      }
    }
  }

  if (Array.isArray(schema.allOf)) {
    for (const child of schema.allOf) errors.push(...validateNode(child, value, root, path));
  }
  if (Array.isArray(schema.anyOf)) {
    if (!schema.anyOf.some((child) => validateNode(child, value, root, path).length === 0)) errors.push(`${path}: anyOf requirement not satisfied`);
  }
  if (schema.not !== undefined && validateNode(schema.not, value, root, path).length === 0) {
    errors.push(`${path}: not-schema matched`);
  }
  if (schema.if !== undefined && validateNode(schema.if, value, root, path).length === 0 && schema.then !== undefined) {
    errors.push(...validateNode(schema.then, value, root, path));
  }
  return errors;
}

function runSelfTest() {
  const schema = {
    type: "object",
    additionalProperties: false,
    required: ["kind", "items"],
    properties: {
      kind: { const: "ok" },
      items: { type: "array", minItems: 1, uniqueItems: true, items: { type: "integer", minimum: 0 } },
      note: { type: ["string", "null"] },
    },
    allOf: [{ if: { properties: { kind: { const: "ok" } } }, then: { required: ["note"] } }],
  };
  const valid = { kind: "ok", items: [1, 2], note: null };
  if (validateNode(schema, valid, schema).length) throw new Error("self-test rejected valid instance");
  const invalid = { kind: "ok", items: [1, 1], extra: true };
  const errors = validateNode(schema, invalid, schema);
  if (!errors.some((error) => error.includes("uniqueItems")) || !errors.some((error) => error.includes("additional property")) || !errors.some((error) => error.includes("note"))) {
    throw new Error(`self-test failed to catch required constraints: ${errors.join("; ")}`);
  }
  console.log("PASS: dependency-free JSON Schema subset validator self-test");
}

const args = process.argv.slice(2);
const arg = (name) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : null; };
try {
  if (args.includes("--self-test")) { runSelfTest(); process.exit(0); }
  const schemaPath = arg("--schema"), instancePath = arg("--instance");
  if (!schemaPath || !instancePath) throw new SchemaValidationError("--schema PATH --instance PATH required");
  const schema = readJson(schemaPath, "schema"), instance = readJson(instancePath, "instance");
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
  throw error;
}

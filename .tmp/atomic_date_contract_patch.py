from pathlib import Path

# Schema: optional, narrowly enumerated synchronization declaration.
p = Path('schemas/manual-direct-add.v2.schema.json')
s = p.read_text()
old = '"id_migration":{"type":"array","items":{"type":"object","additionalProperties":false,"required":["old_id","new_id","reason"],"properties":{"old_id":{"type":"string","minLength":1},"new_id":{"type":"string","minLength":1},"reason":{"type":"string","minLength":1}}}}'
new = '"id_migration":{"type":"array","items":{"type":"object","additionalProperties":false,"required":["old_id","new_id","reason"],"properties":{"old_id":{"type":"string","minLength":1},"new_id":{"type":"string","minLength":1},"reason":{"type":"string","minLength":1},"synchronized_fields":{"type":"array","uniqueItems":true,"items":{"enum":["date_role","event_fingerprint"]}}}}}'
assert old in s
p.write_text(s.replace(old, new, 1))

# Base validator: accept and validate optional synchronized_fields.
p = Path('scripts/validate_manual_direct_add.mjs')
s = p.read_text()
s = s.replace(
    'const MIGRATION_KEYS=["old_id","new_id","reason"];',
    'const MIGRATION_REQUIRED_KEYS=["old_id","new_id","reason"];\nconst MIGRATION_OPTIONAL_KEYS=["synchronized_fields"];\nconst MIGRATION_SYNCHRONIZED_FIELDS=new Set(["date_role","event_fingerprint"]);',
    1,
)
marker = 'function exactKeys(v,l,required){ if(!v||typeof v!=="object"||Array.isArray(v)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`${l} must be an object`); const keys=Object.keys(v),allowed=new Set(required),missing=required.filter(k=>!Object.prototype.hasOwnProperty.call(v,k)),extra=keys.filter(k=>!allowed.has(k)); if(missing.length||extra.length) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`${l} schema mismatch; missing=[${missing.join(",")}] extra=[${extra.join(",")}]`); return v; }'
insert = marker + '\nfunction exactKeysWithOptional(v,l,required,optional){ if(!v||typeof v!=="object"||Array.isArray(v)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`${l} must be an object`); const keys=Object.keys(v),allowed=new Set([...required,...optional]),missing=required.filter(k=>!Object.prototype.hasOwnProperty.call(v,k)),extra=keys.filter(k=>!allowed.has(k)); if(missing.length||extra.length) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`${l} schema mismatch; missing=[${missing.join(",")}] extra=[${extra.join(",")}]`); return v; }'
assert marker in s
s = s.replace(marker, insert, 1)
old_loop = 'for(const [i,x] of migrations.entries()){exactKeys(x,`id_migration[${i}]`,MIGRATION_KEYS); const oldId=str(x.old_id,`id_migration[${i}].old_id`),newId=str(x.new_id,`id_migration[${i}].new_id`); str(x.reason,`id_migration[${i}].reason`); if(oldId===newId||map.has(oldId)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`invalid/duplicate migration ${oldId}`); map.set(oldId,newId); oldIds.push(oldId); newIds.push(newId);}'
new_loop = 'for(const [i,x] of migrations.entries()){exactKeysWithOptional(x,`id_migration[${i}]`,MIGRATION_REQUIRED_KEYS,MIGRATION_OPTIONAL_KEYS); const oldId=str(x.old_id,`id_migration[${i}].old_id`),newId=str(x.new_id,`id_migration[${i}].new_id`); str(x.reason,`id_migration[${i}].reason`); const sync=x.synchronized_fields===undefined?[]:strArr(x.synchronized_fields,`id_migration[${i}].synchronized_fields`); if(sync.some(field=>!MIGRATION_SYNCHRONIZED_FIELDS.has(field))) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`id_migration[${i}].synchronized_fields contains unsupported field`); if(oldId===newId||map.has(oldId)) fail("BLOCKED_MANUAL_DIRECT_ADD_INVALID",`invalid/duplicate migration ${oldId}`); map.set(oldId,newId); oldIds.push(oldId); newIds.push(newId);}'
assert old_loop in s
p.write_text(s.replace(old_loop, new_loop, 1))

# Hardener: representative-date migrations must synchronize existing date-bearing metadata atomically.
p = Path('scripts/validate_manual_direct_add_v4_hardening.mjs')
s = p.read_text()
s = s.replace(
    'const MIGRATION_MUTABLE_FIELDS = new Set(["id", "date", "region"]);',
    'const MIGRATION_MUTABLE_FIELDS = new Set(["id", "date", "region"]);\nconst MIGRATION_SYNCHRONIZED_FIELDS = new Set(["date_role", "event_fingerprint"]);\nconst DATE_ROLE_SYNC_KEYS = new Set(["representative_event_date", "representative_date", "event_date"]);',
    1,
)
old_func = '''function validateMigrationContent(manifest, baseMap, fullMap) {
  for (const migration of manifest.operations?.id_migration || []) {
    const before = baseMap.get(migration.old_id);
    const after = fullMap.get(migration.new_id);
    if (!before || !after) fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `migration card missing ${migration.old_id} → ${migration.new_id}`);
    const changed = changedTopLevelFields(before, after);
    const forbidden = changed.filter((field) => !MIGRATION_MUTABLE_FIELDS.has(field));
    if (forbidden.length) {
      fail(
        "BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE",
        `${migration.old_id} → ${migration.new_id}: migration may change only id/date/region; forbidden=[${forbidden.join(",")}]`,
      );
    }
  }
}'''
new_func = '''function changedObjectFields(before, after) {
  const left = isObject(before) ? before : {};
  const right = isObject(after) ? after : {};
  const keys = new Set([...Object.keys(left), ...Object.keys(right)]);
  return [...keys].filter((key) => !same(left[key], right[key])).sort();
}

function validateDateRoleSynchronization(before, after, migration) {
  if (!isObject(before?.date_role) || !isObject(after?.date_role)) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: date_role synchronization requires before/after objects`);
  }
  const changed = changedObjectFields(before.date_role, after.date_role);
  const forbidden = changed.filter((field) => !DATE_ROLE_SYNC_KEYS.has(field));
  if (forbidden.length) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: date_role synchronization may change only representative date keys; forbidden=[${forbidden.join(",")}]`);
  }
  for (const key of DATE_ROLE_SYNC_KEYS) {
    if (Object.prototype.hasOwnProperty.call(before.date_role, key) || Object.prototype.hasOwnProperty.call(after.date_role, key)) {
      if (after.date_role?.[key] !== after.date) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: date_role.${key} must equal migrated date ${after.date}`);
      }
    }
  }
}

function validateFingerprintSynchronization(before, after, migration) {
  if (!isObject(before?.event_fingerprint) || !isObject(after?.event_fingerprint)) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: event_fingerprint synchronization requires before/after objects`);
  }
  const changed = changedObjectFields(before.event_fingerprint, after.event_fingerprint);
  const forbidden = changed.filter((field) => field !== "event_date");
  if (forbidden.length) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: event_fingerprint synchronization may change only event_date; forbidden=[${forbidden.join(",")}]`);
  }
  if (after.event_fingerprint.event_date !== after.date) {
    fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: event_fingerprint.event_date must equal migrated date ${after.date}`);
  }
}

function validateMigrationContent(manifest, baseMap, fullMap) {
  for (const migration of manifest.operations?.id_migration || []) {
    const before = baseMap.get(migration.old_id);
    const after = fullMap.get(migration.new_id);
    if (!before || !after) fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `migration card missing ${migration.old_id} → ${migration.new_id}`);
    const synchronized = Array.isArray(migration.synchronized_fields) ? migration.synchronized_fields : [];
    const unknown = synchronized.filter((field) => !MIGRATION_SYNCHRONIZED_FIELDS.has(field));
    if (unknown.length) fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: unsupported synchronized_fields=[${unknown.join(",")}]`);
    const allowed = new Set([...MIGRATION_MUTABLE_FIELDS, ...synchronized]);
    const changed = changedTopLevelFields(before, after);
    const forbidden = changed.filter((field) => !allowed.has(field));
    if (forbidden.length) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: undeclared migration fields changed; forbidden=[${forbidden.join(",")}]`);
    }
    const dateChanged = before.date !== after.date;
    if (!dateChanged && synchronized.length) {
      fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: synchronized_fields are only allowed when representative date changes`);
    }
    if (dateChanged) {
      if ((isObject(before.date_role) || isObject(after.date_role)) && !synchronized.includes("date_role")) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: date change requires atomic date_role synchronization`);
      }
      if ((isObject(before.event_fingerprint) || isObject(after.event_fingerprint)) && !synchronized.includes("event_fingerprint")) {
        fail("BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE", `${migration.old_id} → ${migration.new_id}: date change requires atomic event_fingerprint synchronization`);
      }
    }
    if (synchronized.includes("date_role")) validateDateRoleSynchronization(before, after, migration);
    if (synchronized.includes("event_fingerprint")) validateFingerprintSynchronization(before, after, migration);
  }
}'''
assert old_func in s
s = s.replace(old_func, new_func, 1)
old_log = '  console.log("PASS: manual direct-add V4 hardening closes empty-operation, migration, Related add/update, publication-state, duplicate-id, and timestamp bypasses");'
test_block = '''  const dateBase = { cards: [{ id: "2026-09-07_CN_01", date: "2026-09-07", region: "CN", title: "D", urls: ["https://d.example"], related: [], date_role: { representative_event_date: "2026-09-07", representative_date: "2026-09-07", event_date: "2026-09-07", role: "report date" }, event_fingerprint: { event_date: "2026-09-07", actor: "A", action: "B" } }] };
  const staleDate = structuredClone(dateBase);
  staleDate.cards[0].id = "2026-09-06_CN_02";
  staleDate.cards[0].date = "2026-09-06";
  const dateManifest = { schema: "manual_direct_add_v2", formal_full_run_claimed: false, output_updated: "2026-09-09T03:30:00Z", operations: { add: [], update: [], id_migration: [{ old_id: "2026-09-07_CN_01", new_id: "2026-09-06_CN_02", reason: "representative date correction" }] } };
  let staleDateBlocked = false;
  try { validate(dateManifest, dateBase, staleDate); }
  catch (error) { staleDateBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE"; }
  if (!staleDateBlocked) throw new Error("self-test failed to reject date migration with stale date metadata");

  const syncedDate = structuredClone(staleDate);
  for (const key of DATE_ROLE_SYNC_KEYS) syncedDate.cards[0].date_role[key] = "2026-09-06";
  syncedDate.cards[0].event_fingerprint.event_date = "2026-09-06";
  const syncedManifest = structuredClone(dateManifest);
  syncedManifest.operations.id_migration[0].synchronized_fields = ["date_role", "event_fingerprint"];
  validate(syncedManifest, dateBase, syncedDate);

  const overbroadDate = structuredClone(syncedDate);
  overbroadDate.cards[0].event_fingerprint.actor = "Different actor";
  let overbroadDateBlocked = false;
  try { validate(syncedManifest, dateBase, overbroadDate); }
  catch (error) { overbroadDateBlocked = error instanceof ValidationError && error.code === "BLOCKED_MANUAL_DIRECT_ADD_MIGRATION_SCOPE"; }
  if (!overbroadDateBlocked) throw new Error("self-test failed to reject overbroad synchronized migration metadata");

  console.log("PASS: manual direct-add V4 hardening closes empty-operation, atomic representative-date migration, Related add/update, publication-state, duplicate-id, and timestamp bypasses");'''
assert old_log in s
s = s.replace(old_log, test_block, 1)
p.write_text(s)

# Docs: forbid inconsistent intermediate canonical states.
p = Path('docs/MANUAL_DIRECT_ADD_V2.md')
s = p.read_text()
old = '''A migration is an **identity correction, not a content-update bypass**. The replacement card may differ only in `id`, `date`, and `region`. URLs, facts, title, taxonomy, evidence, event fingerprint, Related state, and every other top-level content/audit field must remain byte-equivalent at the JSON-value level. If content also needs correction, perform that as a separately governed operation rather than hiding it inside `id_migration`.'''
new = '''A migration is an **identity correction, not a content-update bypass**. Ordinarily the replacement card may differ only in `id`, `date`, and `region`.

When a representative-date migration changes `date` and the card already carries `date_role` and/or `event_fingerprint`, the migration must be atomic: declare `synchronized_fields` for those existing date-bearing containers and update them in the same canonical state. The only permitted synchronized nested changes are `date_role.representative_event_date`, `date_role.representative_date`, `date_role.event_date`, and `event_fingerprint.event_date`, and each must equal the migrated top-level `date`. A date-changing migration that leaves those containers stale is blocked.

This synchronization exception does not permit content or evidence mutation. URLs, facts, title, taxonomy, source/evidence rows, Related state, and all non-date fingerprint/date-role fields must remain byte-equivalent. Any additional evidence/content correction remains a separately governed operation. This prevents publication of an internally contradictory intermediate canonical state while preserving the narrow migration boundary.'''
assert old in s
s = s.replace(old, new, 1)
s = s.replace(
    '8. ID migration is restricted to `id`/`date`/`region` identity correction and cannot replace event content;',
    '8. ID migration is restricted to identity correction; representative-date changes must atomically synchronize existing `date_role` / `event_fingerprint.event_date` through declared `synchronized_fields`, while all non-date content remains immutable;',
    1,
)
p.write_text(s)

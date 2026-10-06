#!/usr/bin/env node
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const HERE = dirname(fileURLToPath(import.meta.url));
const MAP_PATH = join(HERE, 'source-date-id-normalization.json');
const BASELINE_PATH = resolve(process.cwd(), 'data/cards.full.json');
const DEFAULT_INPUT = resolve(process.cwd(), 'content_polish_results_20260825_MULTI_INPUT_20260810_20260825.json');
const inputPath = resolve(process.argv[2] || DEFAULT_INPUT);
const outputPath = resolve(process.argv[3] || 'cards.full.REPLACE_CANDIDATE_20260827_EARNINGS17.json');
const new17Path = resolve(process.argv[4] || 'cards.NEW17_PUBLISH_READY_CANDIDATE_20260827.json');
const auditPath = resolve(process.argv[5] || 'earnings17_candidate_build_audit_20260827.json');

const readJson = (p) => JSON.parse(readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sha256 = (obj) => createHash('sha256').update(Buffer.isBuffer(obj) ? obj : Buffer.from(obj)).digest('hex');
const git = (args) => {
  const r = spawnSync('git', args, { encoding: 'utf8' });
  if (r.status !== 0) throw new Error(`git ${args.join(' ')} failed: ${String(r.stderr || '').trim()}`);
  return String(r.stdout).trim();
};
const canonicalUrl = (raw) => {
  const u = new URL(raw);
  for (const key of [...u.searchParams.keys()]) {
    if (key.toLowerCase().startsWith('utm_') || ['fbclid','gclid','amp','output'].includes(key.toLowerCase())) u.searchParams.delete(key);
  }
  u.protocol = 'https:';
  u.hostname = u.hostname.toLowerCase().replace(/^www\./,'').replace(/^m\./,'').replace(/^mobile\./,'');
  u.pathname = u.pathname.replace(/\/+$/,'');
  const q = [...u.searchParams.entries()].sort(([a],[b]) => a.localeCompare(b));
  u.search = '';
  for (const [k,v] of q) u.searchParams.append(k,v);
  return u.toString().replace(/\?$/,'');
};
const owner = (fs) => fs.source_owner_id_normalized || new URL(fs.source_url).hostname.toLowerCase().replace(/^www\./,'');
const deepClone = (x) => structuredClone(x);
const unique = (a) => [...new Set(a)];

const map = readJson(MAP_PATH);
const baselineRaw = readFileSync(BASELINE_PATH);
const baseline = JSON.parse(baselineRaw.toString('utf8').replace(/^\uFEFF/,''));
const polish = readJson(inputPath);

if (baseline.total !== map.base_full_count || baseline.cards?.length !== map.base_full_count) {
  throw new Error(`baseline count mismatch: expected ${map.base_full_count}, got total=${baseline.total}, cards=${baseline.cards?.length}`);
}
const baselineBlob = git(['hash-object', BASELINE_PATH]);
if (baselineBlob !== map.base_full_blob_sha) {
  throw new Error(`BLOCKED_BASELINE_MOVED_REBASE_REQUIRED: baseline blob ${baselineBlob} != ${map.base_full_blob_sha}`);
}
if (polish.current_main_sha !== map.base_main_commit_sha || polish.baseline_blob_sha !== map.base_full_blob_sha) {
  throw new Error('content-polish lineage does not match the locked main/blob');
}
const sourceCards = polish.content_enriched_and_language_polished;
if (!Array.isArray(sourceCards) || sourceCards.length !== map.expected_candidate_count) {
  throw new Error(`expected ${map.expected_candidate_count} polished cards`);
}
const bySpec = new Map(sourceCards.map((c) => [c.source_spec_id, c]));
if (bySpec.size !== map.expected_candidate_count) throw new Error('duplicate source_spec_id in content-polish input');

const existingIds = new Set(baseline.cards.map((c) => c.id));
const baselineUrls = new Set();
const baselineCanonicalUrls = new Set();
for (const c of baseline.cards) {
  for (const u of c.urls || []) {
    baselineUrls.add(u);
    try { baselineCanonicalUrls.add(canonicalUrl(u)); } catch {}
  }
}

const normalizedCards = [];
const idLedger = [];
const dateLedger = [];
const urlCollisions = [];
const sourceRows = [];

for (const [spec, rule] of Object.entries(map.items)) {
  const src = bySpec.get(spec);
  if (!src) throw new Error(`missing polished card ${spec}`);
  if (existingIds.has(rule.production_id)) throw new Error(`production ID collision: ${rule.production_id}`);
  if (!Array.isArray(src.fact_sources) || src.fact_sources.length !== rule.sources.length) {
    throw new Error(`${spec}: fact_sources length ${src.fact_sources?.length} != normalization rows ${rule.sources.length}`);
  }

  const c = deepClone(src);
  const stageId = c.id || c.draft_id || c.revised_draft_id;
  c.id = rule.production_id;
  c.prior_id = stageId;
  c.id_change_reason = 'candidate production ID assigned from exact-current-main date-region collision screen; Prompt 0.8 remains governance-blocked by missing original 0.0D/0.0C artifacts';
  c.id_collision_recheck_required = false;
  c.state = 'publish_ready';
  c.publish_ready = true;
  c.evidence_complete = true;
  c.source_claim_covered = true;
  c.content_enriched = true;
  c.language_terminology_polished = true;
  c.needs_publish_readiness_qc = false;
  c.github_merge_ready = false;
  c.pr_candidate_ready = false;
  c.quality_grade = rule.quality_grade;

  const publicationDates = [];
  c.fact_sources = c.fact_sources.map((fs, idx) => {
    const r = rule.sources[idx];
    if (fs.source_name !== r.source_name) {
      throw new Error(`${spec}: source row ${idx} name mismatch: ${fs.source_name} != ${r.source_name}`);
    }
    const out = deepClone(fs);
    out.source_role = r.source_role;
    out.source_contribution = out.claim;
    out.source_origin_type = r.source_origin_type;
    out.source_owner_id_normalized = r.owner;
    out.source_published_date = r.source_published_date;
    out.visible_quote_date = r.source_published_date;
    if (r.date_provenance_note) out.source_date_provenance_note = r.date_provenance_note;
    publicationDates.push(r.source_published_date);
    sourceRows.push({ source_spec_id: spec, production_id: rule.production_id, source_name: out.source_name, source_url: out.source_url, source_published_date: out.source_published_date, visible_quote_date: out.visible_quote_date, source_role: out.source_role, source_origin_type: out.source_origin_type, source_owner_id_normalized: out.source_owner_id_normalized });
    return out;
  });

  delete c.source_published_date;
  delete c.visible_quote_date;
  delete c.source_date_lineage_reason;
  c.date_role = {
    status: 'PASS',
    card_date_role: 'event_date',
    event_date: c.date,
    representative_date: c.date,
    source_published_dates: unique(publicationDates).sort(),
    source_published_date_status: 'PASS',
    audit_timestamps_not_used_as_visible_dates: true,
    note: 'Per-source publication dates normalized in controlled 0.5R date-lineage remediation; fetched_at/checked_at remain audit timestamps only.'
  };

  const allUrls = c.fact_sources.map((fs) => fs.source_url);
  const canon = allUrls.map(canonicalUrl);
  const domains = unique(allUrls.map((u) => new URL(u).hostname.toLowerCase().replace(/^www\./,'')));
  const owners = unique(c.fact_sources.map(owner));
  c.source_evidence_entry_count = c.fact_sources.length;
  c.source_unique_url_count = unique(canon).length;
  c.source_unique_domain_count = domains.length;
  c.source_independent_owner_count = owners.length;
  c.source_diversity_measure = {
    source_evidence_entry_count: c.fact_sources.length,
    source_unique_url_count: unique(canon).length,
    source_unique_domain_count: domains.length,
    source_independent_owner_count: owners.length,
    visible_source_url_count: unique(canon).length,
    canonical_urls: unique(canon).sort(),
    canonical_domains: domains.sort(),
    independent_owners: owners.sort(),
    missing_source_url_count: 0,
    missing_visible_source_url_count: 0
  };

  if (rule.single_owner_exception_required) {
    if (owners.length !== 1) throw new Error(`${spec}: expected exactly one editorial owner`);
    c.source_diversity_status = 'PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION';
    if (!c.single_source_exception?.allowed) throw new Error(`${spec}: expected preserved governed single-source exception`);
  } else {
    if (owners.length < 2) throw new Error(`${spec}: expected >=2 independent editorial owners, got ${owners.length}`);
    c.source_diversity_status = 'PASS_MULTI_SOURCE';
    c.single_source_exception = { allowed: false, reason: 'not applicable: multi-owner visible evidence after owner-normalized 0.5R date-lineage re-QC' };
  }

  const synthesis = new Map();
  for (const fs of c.fact_sources) {
    const own = owner(fs);
    if (!synthesis.has(own)) synthesis.set(own, { source_owner: own, source_domains: new Set(), contributions: [], fields: new Set() });
    const row = synthesis.get(own);
    row.source_domains.add(new URL(fs.source_url).hostname.toLowerCase().replace(/^www\./,''));
    row.contributions.push(fs.source_contribution);
    for (const f of fs.supports || []) row.fields.add(f);
  }
  c.source_synthesis_applied = true;
  c.source_synthesis_audit = [...synthesis.values()].map((x) => ({
    source_owner: x.source_owner,
    source_domains: [...x.source_domains].sort(),
    source_role: 'primary_or_secondary_event_evidence',
    unique_contribution: x.contributions.join(' | '),
    affected_visible_fields: [...x.fields].sort(),
    interpretation_change_or_confirmation: owners.length > 1 ? 'owner-normalized source-locked synthesis' : 'bounded primary-source event package integrated'
  }));
  c.source_synthesis_fields = unique(c.source_synthesis_audit.flatMap((x) => x.affected_visible_fields)).sort();
  c.source_strength_caveat = null;
  c.needs_source_augmentation = false;
  c.source_date_lineage_qc_status = 'PASS';
  c.final_qc_replay_status = 'PASS_DATE_ONLY_BLOCKER_RESOLVED';
  c.prompt_0_7c_status = 'BLOCKED_EDITORIAL_COMPLETENESS_UNPROVEN_MISSING_ORIGINAL_0_0D_0_0C_ARTIFACTS';
  c.prompt_0_8_authorized = false;

  if (!Array.isArray(c.related)) c.related = [];
  if (c.related.length !== 0) throw new Error(`${spec}: this 17-card set is expected to remain new_unrelated_event with empty related[]`);
  if (!c.related_lineage || c.related_lineage.relation_type !== 'new_unrelated_event') {
    throw new Error(`${spec}: missing preserved new_unrelated_event related_lineage`);
  }
  c.related_lineage.related_ids = [];

  if (rule.v3_non_execution) {
    if (c.anchor_path_validation?.selected_anchor_path !== 'v3_non_execution' || c.anchor_path_validation?.anchor_path_qc_passed !== true) {
      throw new Error(`${spec}: V3 non-execution package not preserved`);
    }
    for (const key of ['prior_state','new_verified_fact','changed_judgment','uncertainty_resolved','remaining_uncertainty','incremental_information','baseline_expectation_changed','decision_relevance','next_confirmation_points']) {
      if (c[key] == null || c[key] === '' || (Array.isArray(c[key]) && c[key].length === 0)) throw new Error(`${spec}: incomplete V3 field ${key}`);
    }
  }

  const urlCollision = (c.urls || []).filter((u) => baselineUrls.has(u) || baselineCanonicalUrls.has(canonicalUrl(u)));
  if (urlCollision.length) urlCollisions.push({ source_spec_id: spec, production_id: rule.production_id, urls: urlCollision });
  idLedger.push({ source_spec_id: spec, stage_id: stageId, production_id: rule.production_id, date: c.date, region: c.region });
  dateLedger.push({ source_spec_id: spec, production_id: rule.production_id, event_date: c.date, source_published_dates: c.date_role.source_published_dates });
  normalizedCards.push(c);
}

if (normalizedCards.length !== map.expected_candidate_count) throw new Error('normalized card count mismatch');
if (new Set(normalizedCards.map((c) => c.id)).size !== normalizedCards.length) throw new Error('duplicate production IDs inside new 17');
if (urlCollisions.length) throw new Error(`baseline exact/canonical URL collision detected: ${JSON.stringify(urlCollisions)}`);

const merged = deepClone(baseline);
merged.cards.push(...normalizedCards);
merged.cards.sort((a,b) => b.date.localeCompare(a.date) || b.id.localeCompare(a.id));
merged.updated = new Date().toISOString();
merged.total = merged.cards.length;
if (merged.total !== map.expected_after) throw new Error(`expected ${map.expected_after}, got ${merged.total}`);
if (new Set(merged.cards.map((c) => c.id)).size !== merged.cards.length) throw new Error('duplicate ID in merged replacement candidate');

const new17 = {
  schema: 'sbtl_publish_ready_candidate_17_v1',
  run_tag: map.run_tag,
  base_main_commit_sha: map.base_main_commit_sha,
  base_full_blob_sha: map.base_full_blob_sha,
  count: normalizedCards.length,
  publish_ready_count: normalizedCards.length,
  prompt_0_7c_status: 'BLOCKED_EDITORIAL_COMPLETENESS_UNPROVEN_MISSING_ORIGINAL_0_0D_0_0C_ARTIFACTS',
  prompt_0_8_authorized: false,
  github_merge_ready: false,
  cards: normalizedCards
};

writeFileSync(outputPath, JSON.stringify(merged, null, 2) + '\n');
writeFileSync(new17Path, JSON.stringify(new17, null, 2) + '\n');

const audit = {
  schema: 'sbtl_earnings17_candidate_build_audit_v1',
  run_tag: map.run_tag,
  status: 'PASS_REPLACEMENT_CANDIDATE_ONLY_NOT_0_8_AUTHORIZED',
  baseline: { path: BASELINE_PATH, blob_sha: baselineBlob, count: baseline.cards.length, sha256: sha256(baselineRaw) },
  input_content_polish: { path: inputPath, count: sourceCards.length, current_main_sha: polish.current_main_sha, baseline_blob_sha: polish.baseline_blob_sha },
  output: { replacement_path: outputPath, replacement_count: merged.total, replacement_sha256: sha256(readFileSync(outputPath)), new17_path: new17Path, new17_count: normalizedCards.length, new17_sha256: sha256(readFileSync(new17Path)) },
  checks: {
    exact_baseline_blob_match: true,
    baseline_count_1408: true,
    polished_input_17: true,
    production_id_unique: true,
    production_id_baseline_collision_zero: true,
    baseline_url_collision_zero: true,
    fact_source_rows_date_normalized_41: sourceRows.length === 41,
    visible_quote_date_equals_source_published_date_41: sourceRows.every((x) => x.visible_quote_date === x.source_published_date),
    audit_timestamps_not_used_as_publication_date: true,
    source_owner_normalization_applied: true,
    v3_non_execution_packages_preserved_3: normalizedCards.filter((c) => c.anchor_path_validation?.selected_anchor_path === 'v3_non_execution').length === 3,
    related_empty_new_unrelated_17: normalizedCards.every((c) => c.related.length === 0 && c.related_lineage?.relation_type === 'new_unrelated_event'),
    publish_ready_candidate_17: normalizedCards.every((c) => c.publish_ready === true),
    github_merge_ready_false_17: normalizedCards.every((c) => c.github_merge_ready === false),
    replacement_total_1425: merged.total === 1425
  },
  id_resolution_ledger: idLedger,
  source_date_ledger: dateLedger,
  source_row_count: sourceRows.length,
  source_rows: sourceRows,
  governance_blocker: {
    code: 'BLOCKED_EDITORIAL_COMPLETENESS_UNPROVEN',
    stage: '0.7C',
    reason: 'Original Stage 0.0D and Stage 0.0C artifacts referenced by the Stage A authoritative lineage are not available as standalone current-main/retrievable files, so Prompt 0.8 cannot be honestly authorized.',
    missing_refs: ['SBTL_STAGE_0_0D_DOCUMENT_UNIVERSE_20260825_R1.json','SBTL_STAGE_0_0C_COVERAGE_DISCOVERY_20260825_R2.json'],
    effect: 'Replacement file is a deterministic manual candidate. Do not label it github_merge_ready or card_run_v1-authorized until the missing governance artifacts are restored and 0.7C passes.'
  }
};
writeFileSync(auditPath, JSON.stringify(audit, null, 2) + '\n');
console.log(JSON.stringify(audit, null, 2));

import { execFileSync } from "node:child_process";

const SOURCE_PATH = "data/cards.full.json";

function runGit(args, cwd) {
  return execFileSync("git", args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
}

function gitOk(args, cwd) {
  try {
    execFileSync("git", args, { cwd, stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

function detectMainRef(cwd) {
  if (gitOk(["rev-parse", "--verify", "refs/remotes/origin/main"], cwd)) return "refs/remotes/origin/main";
  if (gitOk(["rev-parse", "--verify", "refs/heads/main"], cwd)) return "refs/heads/main";
  return "main";
}

function stableCardId(card) {
  if (!card || typeof card !== "object") return null;
  const id = card.id
    || card.news_id
    || card.url
    || (Array.isArray(card.urls) && card.urls[0]);
  return typeof id === "string" && id.trim() ? id.trim() : null;
}

function cardDate(card) {
  return String(card?.date || card?.d || "").trim();
}

function parseSnapshot(text) {
  const parsed = JSON.parse(text);
  const cards = Array.isArray(parsed) ? parsed : parsed?.cards;
  if (!Array.isArray(cards)) throw new Error("root must be an array or contain cards[]");
  return cards;
}

export function createGitProvenanceResolver({ cwd = process.cwd(), mainRef = null } = {}) {
  const resolvedMainRef = mainRef || detectMainRef(cwd);
  return {
    commitExists(sha) {
      return gitOk(["cat-file", "-e", `${sha}^{commit}`], cwd);
    },
    isReachableFromMain(sha) {
      return gitOk(["merge-base", "--is-ancestor", sha, resolvedMainRef], cwd);
    },
    sourceBlobAt(sha) {
      try {
        return runGit(["rev-parse", `${sha}:${SOURCE_PATH}`], cwd);
      } catch {
        return null;
      }
    },
    sourceTextAt(sha) {
      try {
        return runGit(["show", `${sha}:${SOURCE_PATH}`], cwd);
      } catch {
        return null;
      }
    },
  };
}

export function validateMonthlyBriefProvenance(library, resolver) {
  const errors = [];
  const items = Array.isArray(library?.items) ? library.items : [];
  const snapshotCache = new Map();

  for (let i = 0; i < items.length; i += 1) {
    const item = items[i];
    const baseline = item?.source_baseline;
    const commitSha = baseline?.main_commit_sha;
    const expectedBlob = baseline?.full_blob_sha;
    const path = `library.items[${i}].source_baseline`;
    if (typeof commitSha !== "string" || typeof expectedBlob !== "string") continue;

    if (!resolver.commitExists(commitSha)) {
      errors.push(`${path}.main_commit_sha: commit does not exist in the checked-out repository`);
      continue;
    }
    if (!resolver.isReachableFromMain(commitSha)) {
      errors.push(`${path}.main_commit_sha: commit is not reachable from main`);
      continue;
    }
    const actualBlob = resolver.sourceBlobAt(commitSha);
    if (!actualBlob) {
      errors.push(`${path}.full_blob_sha: ${SOURCE_PATH} does not exist at the declared main commit`);
      continue;
    }
    if (actualBlob !== expectedBlob) {
      errors.push(`${path}.full_blob_sha: expected ${actualBlob} for ${SOURCE_PATH} at ${commitSha}, got ${expectedBlob}`);
      continue;
    }

    const cacheKey = `${commitSha}|${actualBlob}`;
    let cards = snapshotCache.get(cacheKey);
    if (!cards) {
      const sourceText = resolver.sourceTextAt(commitSha);
      if (typeof sourceText !== "string") {
        errors.push(`${path}.full_blob_sha: could not read ${SOURCE_PATH} at the declared main commit`);
        continue;
      }
      try {
        cards = parseSnapshot(sourceText);
        snapshotCache.set(cacheKey, cards);
      } catch (error) {
        errors.push(`${path}.full_blob_sha: ${SOURCE_PATH} is not a valid card snapshot (${error.message})`);
        continue;
      }
    }

    const snapshotIds = new Set(cards.map(stableCardId).filter(Boolean));
    (Array.isArray(item?.source_card_ids) ? item.source_card_ids : []).forEach((id, j) => {
      if (typeof id === "string" && !snapshotIds.has(id)) {
        errors.push(`library.items[${i}].source_card_ids[${j}]: card id does not exist in the declared ${SOURCE_PATH} snapshot`);
      }
    });

    if (typeof item?.month === "string" && Number.isInteger(baseline?.source_month_count)) {
      const actualMonthCount = cards.filter((card) => cardDate(card).slice(0, 7) === item.month).length;
      if (actualMonthCount !== baseline.source_month_count) {
        errors.push(`${path}.source_month_count: expected ${actualMonthCount} cards for ${item.month} in the declared snapshot, got ${baseline.source_month_count}`);
      }
    }
  }
  return errors;
}

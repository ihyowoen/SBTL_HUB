import { execFileSync } from "node:child_process";

const SOURCE_PATH = "data/cards.full.json";
// The governed canonical archive is already tens of MB and grows over time. Node's
// child-process default maxBuffer is ~1 MiB, so `git show <sha>:data/cards.full.json`
// must opt into a publication-safe ceiling or the first real issue fails closed as
// "unreadable" even when the locked blob is valid.
const GIT_OUTPUT_MAX_BUFFER = 256 * 1024 * 1024;

function runGit(args, cwd) {
  return execFileSync("git", args, {
    cwd,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "ignore"],
    maxBuffer: GIT_OUTPUT_MAX_BUFFER,
  }).trim();
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

function cardTitle(card) {
  return String(card?.title || card?.T || "").trim();
}

function cardDate(card) {
  return String(card?.date || card?.d || "").trim();
}

function cardPrimaryUrl(card) {
  if (Array.isArray(card?.urls)) {
    const first = card.urls.find((value) => typeof value === "string" && value.trim());
    if (first) return first.trim();
  }
  return typeof card?.url === "string" ? card.url.trim() : "";
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

    const snapshotById = new Map();
    for (const card of cards) {
      const id = stableCardId(card);
      if (id && !snapshotById.has(id)) snapshotById.set(id, card);
    }

    (Array.isArray(item?.source_card_ids) ? item.source_card_ids : []).forEach((id, j) => {
      if (typeof id === "string" && !snapshotById.has(id)) {
        errors.push(`library.items[${i}].source_card_ids[${j}]: card id ${id} does not exist in the declared ${SOURCE_PATH} snapshot`);
      }
    });

    (Array.isArray(item?.refs) ? item.refs : []).forEach((ref, j) => {
      if (!ref || typeof ref !== "object" || typeof ref.id !== "string") return;
      const card = snapshotById.get(ref.id);
      const refPath = `library.items[${i}].refs[${j}]`;
      if (!card) {
        errors.push(`${refPath}.id: card id ${ref.id} does not exist in the declared ${SOURCE_PATH} snapshot`);
        return;
      }

      const expectedTitle = cardTitle(card);
      const expectedDate = cardDate(card);
      const expectedUrl = cardPrimaryUrl(card);
      if (ref.title !== expectedTitle) {
        errors.push(`${refPath}.title: expected locked card title ${JSON.stringify(expectedTitle)}, got ${JSON.stringify(ref.title)}`);
      }
      if (ref.date !== expectedDate) {
        errors.push(`${refPath}.date: expected locked card date ${JSON.stringify(expectedDate)}, got ${JSON.stringify(ref.date)}`);
      }
      if (Object.prototype.hasOwnProperty.call(ref, "url") && ref.url !== expectedUrl) {
        errors.push(`${refPath}.url: expected locked card primary URL ${JSON.stringify(expectedUrl)}, got ${JSON.stringify(ref.url)}`);
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

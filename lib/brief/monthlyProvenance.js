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
  };
}

export function validateMonthlyBriefProvenance(library, resolver) {
  const errors = [];
  const items = Array.isArray(library?.items) ? library.items : [];
  for (let i = 0; i < items.length; i += 1) {
    const baseline = items[i]?.source_baseline;
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
    }
  }
  return errors;
}

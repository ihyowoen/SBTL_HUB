import { describe, expect, it } from "vitest";
import { validateMonthlyBriefProvenance } from "../lib/brief/monthlyProvenance.js";

function library(main_commit_sha = "1".repeat(40), full_blob_sha = "2".repeat(40)) {
  return { items: [{ source_baseline: { main_commit_sha, full_blob_sha } }] };
}

function resolver(overrides = {}) {
  return {
    commitExists: () => true,
    isReachableFromMain: () => true,
    sourceBlobAt: () => "2".repeat(40),
    ...overrides,
  };
}

describe("Monthly Brief git provenance", () => {
  it("accepts a reachable main commit whose cards.full blob matches", () => {
    expect(validateMonthlyBriefProvenance(library(), resolver())).toEqual([]);
  });

  it("rejects a nonexistent declared commit", () => {
    const errors = validateMonthlyBriefProvenance(library(), resolver({ commitExists: () => false })).join("\n");
    expect(errors).toContain("commit does not exist");
  });

  it("rejects a commit that is not reachable from main", () => {
    const errors = validateMonthlyBriefProvenance(library(), resolver({ isReachableFromMain: () => false })).join("\n");
    expect(errors).toContain("not reachable from main");
  });

  it("rejects a missing cards.full snapshot", () => {
    const errors = validateMonthlyBriefProvenance(library(), resolver({ sourceBlobAt: () => null })).join("\n");
    expect(errors).toContain("does not exist at the declared main commit");
  });

  it("rejects a declared blob that does not match cards.full at the commit", () => {
    const errors = validateMonthlyBriefProvenance(library(), resolver({ sourceBlobAt: () => "3".repeat(40) })).join("\n");
    expect(errors).toContain("full_blob_sha");
    expect(errors).toContain("expected");
  });
});

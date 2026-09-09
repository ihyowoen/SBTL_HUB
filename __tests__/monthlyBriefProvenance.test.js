import { describe, expect, it } from "vitest";
import { validateMonthlyBriefProvenance } from "../lib/brief/monthlyProvenance.js";

const SNAPSHOT = {
  cards: [
    { id: "AUG_A", date: "2026-08-10", title: "August A", urls: ["https://example.com/a"] },
    { news_id: "AUG_B", d: "2026-08-20", T: "August B", url: "https://example.com/b" },
    { id: "SEP_A", date: "2026-09-01", title: "September A", urls: ["https://example.com/sep"] },
  ],
};

function library(main_commit_sha = "1".repeat(40), full_blob_sha = "2".repeat(40), overrides = {}) {
  return {
    items: [{
      month: "2026-08",
      source_baseline: { main_commit_sha, full_blob_sha, source_month_count: 2 },
      source_card_ids: ["AUG_A", "AUG_B"],
      refs: [
        { n: 1, id: "AUG_A", title: "August A", date: "2026-08-10", url: "https://example.com/a" },
        { n: 2, id: "AUG_B", title: "August B", date: "2026-08-20", url: "https://example.com/b" },
      ],
      ...overrides,
    }],
  };
}

function resolver(overrides = {}) {
  return {
    commitExists: () => true,
    isReachableFromMain: () => true,
    sourceBlobAt: () => "2".repeat(40),
    sourceTextAt: () => JSON.stringify(SNAPSHOT),
    ...overrides,
  };
}

describe("Monthly Brief git provenance", () => {
  it("accepts a reachable main commit whose cards.full blob, governed cards and refs match", () => {
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

  it("rejects governed source card ids that are absent from the locked snapshot", () => {
    const errors = validateMonthlyBriefProvenance(
      library(undefined, undefined, { source_card_ids: ["AUG_A", "INVENTED_CARD"] }),
      resolver(),
    ).join("\n");
    expect(errors).toContain("INVENTED_CARD");
    expect(errors).toContain("does not exist in the declared data/cards.full.json snapshot");
  });

  it("rejects a source_month_count that disagrees with the locked snapshot", () => {
    const lib = library();
    lib.items[0].source_baseline.source_month_count = 99;
    const errors = validateMonthlyBriefProvenance(lib, resolver()).join("\n");
    expect(errors).toContain("source_month_count");
    expect(errors).toContain("expected 2 cards for 2026-08");
  });

  it("rejects public reference title, date or URL that diverges from the locked card", () => {
    for (const [field, value] of [
      ["title", "Wrong title"],
      ["date", "2026-08-11"],
      ["url", "https://wrong.example/evidence"],
    ]) {
      const lib = library();
      lib.items[0].refs[0][field] = value;
      const errors = validateMonthlyBriefProvenance(lib, resolver()).join("\n");
      expect(errors).toContain(`refs[0].${field}`);
      expect(errors).toContain("locked card");
    }
  });

  it("allows an omitted optional reference URL while still binding title and date", () => {
    const lib = library();
    delete lib.items[0].refs[0].url;
    expect(validateMonthlyBriefProvenance(lib, resolver())).toEqual([]);
  });

  it("rejects unreadable or malformed locked card snapshots", () => {
    expect(validateMonthlyBriefProvenance(library(), resolver({ sourceTextAt: () => null })).join("\n")).toContain("could not read");
    expect(validateMonthlyBriefProvenance(library(), resolver({ sourceTextAt: () => "not-json" })).join("\n")).toContain("not a valid card snapshot");
  });
});

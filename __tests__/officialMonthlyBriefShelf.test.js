import { describe, expect, it } from "vitest";
import { officialMonthlyBriefShelfItems } from "../src/OfficialMonthlyBriefShelf.jsx";

const issue = (month, revision = 1, status = "published") => ({
  id: `monthly-brief-${month}-r${revision}`,
  product_name: "SBTL Monthly Brief",
  month,
  revision,
  status,
  publication_class: "official_editorial",
  publication_mode: "editorial_curated",
  published_at: `${month}-28`,
  title: `SBTL Monthly Brief · ${month}`,
  executive_diagnosis: "x",
  what_changed: "x",
  source_baseline: { main_commit_sha: "a".repeat(40), full_blob_sha: "b".repeat(40), source_month_count: 1 },
  source_card_ids: ["A"],
  key_flows: [{ id: "01", title: "x", summary: "x", card_ids: ["A"] }],
  refs: [{ n: 1, id: "A", title: "x", date: `${month}-01` }],
  qc: { evidence_status: "PASS", red_team_status: "PASS", editorial_coherence_status: "PASS", language_terminology_status: "PASS", reviewed_at: `${month}-28`, reviewer_role: "editorial_red_team" },
  approval: { status: "APPROVED", approved_at: `${month}-28`, reviewer_role: "editorial_owner" },
});

describe("Official Monthly Brief shelf", () => {
  it("keeps the latest approved official issue as hero and older issues as archive", () => {
    const library = { items: [issue("2026-06"), issue("2026-08"), issue("2026-07")] };
    const { latest, archive } = officialMonthlyBriefShelfItems(library);
    expect(latest.month).toBe("2026-08");
    expect(archive.map((x) => x.month)).toEqual(["2026-07", "2026-06"]);
  });

  it("does not surface non-official or unapproved entries", () => {
    const draft = issue("2026-09", 1, "draft");
    const { latest, archive } = officialMonthlyBriefShelfItems({ items: [draft, issue("2026-08")] });
    expect(latest.month).toBe("2026-08");
    expect(archive).toEqual([]);
  });
});

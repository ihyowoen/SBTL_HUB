import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  OFFICIAL_PUBLICATION_CLASS,
  OFFICIAL_PUBLICATION_MODE,
  isOfficialStrategicBrief,
  validateStrategicBriefItem,
  validateStrategicBriefLibrary,
} from "../lib/brief/strategicPublication.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");

function sample(overrides = {}) {
  return {
    id: "strategic_2026-08_vol10_r1",
    edition: "VOL.10",
    month: "2026-08",
    revision: 1,
    status: "published",
    publication_class: OFFICIAL_PUBLICATION_CLASS,
    publication_mode: OFFICIAL_PUBLICATION_MODE,
    published_at: "2026-09-08",
    title: "VOL.10 — STRATEGIC BRIEFING",
    executive_diagnosis: "수요와 공급망의 재편을 월간 카드 전체에서 재검증한 편집 진단이다.",
    source_baseline: {
      main_commit_sha: "1".repeat(40),
      full_blob_sha: "2".repeat(40),
      source_month_count: 100,
    },
    source_card_ids: ["2026-08-01_US_01", "2026-08-02_CN_01"],
    structural_signals: [
      {
        id: "01",
        title: "수요 다변화",
        summary: "EV 단일 성장축에서 ESS·HEV 등 복수 수요축으로 분화했다.",
        card_ids: ["2026-08-01_US_01", "2026-08-02_CN_01"],
      },
    ],
    watch: ["9월 실적과 실제 발주가 구조적 전환을 확인하는지 본다."],
    refs: [
      { n: 1, id: "2026-08-01_US_01", title: "미국 카드", date: "2026-08-01", url: "https://example.com/a" },
      { n: 2, id: "2026-08-02_CN_01", title: "중국 카드", date: "2026-08-02", url: "https://example.com/b" },
    ],
    approval: {
      status: "APPROVED",
      approved_at: "2026-09-08",
      reviewer_role: "editorial_owner",
    },
    ...overrides,
  };
}

describe("official Strategic Brief publication boundary", () => {
  it("accepts a fully approved manual editorial issue", () => {
    const item = sample();
    expect(validateStrategicBriefItem(item)).toEqual([]);
    expect(isOfficialStrategicBrief(item)).toBe(true);
  });

  it("rejects an automated monthly-window output from becoming official", () => {
    const item = sample({ publication_class: "exploratory_auto", publication_mode: "llm_generated" });
    const errors = validateStrategicBriefItem(item).join("\n");
    expect(errors).toContain("publication_class");
    expect(errors).toContain("publication_mode");
    expect(isOfficialStrategicBrief(item)).toBe(false);
  });

  it("requires immutable baseline provenance for a public issue", () => {
    const item = sample({ source_baseline: { main_commit_sha: "bad", full_blob_sha: "bad", source_month_count: 100 } });
    const errors = validateStrategicBriefItem(item).join("\n");
    expect(errors).toContain("main_commit_sha");
    expect(errors).toContain("full_blob_sha");
  });

  it("rejects structural-signal evidence outside the governed source set", () => {
    const item = sample({
      structural_signals: [{ id: "01", title: "signal", summary: "summary", card_ids: ["UNKNOWN_CARD"] }],
    });
    expect(validateStrategicBriefItem(item).join("\n")).toContain("must exist in source_card_ids");
  });

  it("rejects source cards without public reference rows", () => {
    const item = sample({ refs: [{ n: 1, id: "2026-08-01_US_01", title: "미국 카드", date: "2026-08-01" }] });
    expect(validateStrategicBriefItem(item).join("\n")).toContain("must have a matching refs[].id entry");
  });

  it("keeps edition/revision and month/revision unique", () => {
    const a = sample();
    const b = sample({ id: "strategic_duplicate" });
    const errors = validateStrategicBriefLibrary({ schema_version: "strategic-brief.v1", items: [a, b] }).join("\n");
    expect(errors).toContain("edition + revision must be unique");
    expect(errors).toContain("month + revision must be unique");
  });

  it("validates the repository public official library", () => {
    const library = JSON.parse(fs.readFileSync(path.join(root, "public/data/strategic_briefs.json"), "utf8"));
    expect(validateStrategicBriefLibrary(library)).toEqual([]);
  });
});

import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  MONTHLY_BRIEF_PRODUCT_NAME,
  OFFICIAL_PUBLICATION_CLASS,
  OFFICIAL_PUBLICATION_MODE,
  isOfficialMonthlyBrief,
  validateMonthlyBriefItem,
  validateMonthlyBriefLibrary,
} from "../lib/brief/monthlyPublication.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");

function sample(overrides = {}) {
  return {
    id: "monthly-brief-2026-08-r1",
    product_name: MONTHLY_BRIEF_PRODUCT_NAME,
    month: "2026-08",
    revision: 1,
    status: "published",
    publication_class: OFFICIAL_PUBLICATION_CLASS,
    publication_mode: OFFICIAL_PUBLICATION_MODE,
    published_at: "2026-09-08",
    title: "SBTL Monthly Brief · 2026.08",
    executive_diagnosis: "수요와 공급망 변화가 한 달 동안 어떻게 연결됐는지 재검증한 핵심 진단이다.",
    what_changed: "개별 사건을 넘어 ESS·현지화·고객 다변화가 동시에 실행 단계로 이동했다.",
    source_baseline: {
      main_commit_sha: "1".repeat(40),
      full_blob_sha: "2".repeat(40),
      source_month_count: 100,
    },
    source_card_ids: ["2026-08-01_US_01", "2026-08-02_CN_01"],
    key_flows: [
      {
        id: "01",
        title: "수요 다변화",
        summary: "EV 단일 성장축에서 ESS·HEV 등 복수 수요축으로 넓어졌다.",
        card_ids: ["2026-08-01_US_01", "2026-08-02_CN_01"],
      },
    ],
    watch: ["9월 실적과 실제 발주가 변화의 지속성을 확인하는지 본다."],
    refs: [
      { n: 1, id: "2026-08-01_US_01", title: "미국 카드", date: "2026-08-01", url: "https://example.com/a" },
      { n: 2, id: "2026-08-02_CN_01", title: "중국 카드", date: "2026-08-02", url: "https://example.com/b" },
    ],
    qc: {
      evidence_status: "PASS",
      red_team_status: "PASS",
      editorial_coherence_status: "PASS",
      language_terminology_status: "PASS",
      reviewed_at: "2026-09-08",
      reviewer_role: "editorial_red_team",
    },
    approval: {
      status: "APPROVED",
      approved_at: "2026-09-08",
      reviewer_role: "editorial_owner",
    },
    ...overrides,
  };
}

describe("official SBTL Monthly Brief publication boundary", () => {
  it("accepts a fully approved editorially curated brief", () => {
    const item = sample();
    expect(validateMonthlyBriefItem(item)).toEqual([]);
    expect(isOfficialMonthlyBrief(item)).toBe(true);
  });

  it("rejects automated monthly-window output from becoming official", () => {
    const item = sample({ publication_class: "exploratory_auto", publication_mode: "llm_generated" });
    const errors = validateMonthlyBriefItem(item).join("\n");
    expect(errors).toContain("publication_class");
    expect(errors).toContain("publication_mode");
    expect(isOfficialMonthlyBrief(item)).toBe(false);
  });

  it("requires the Monthly Brief product identity", () => {
    const item = sample({ product_name: "SBTL Strategic Briefing" });
    expect(validateMonthlyBriefItem(item).join("\n")).toContain("product_name");
    expect(isOfficialMonthlyBrief(item)).toBe(false);
  });

  it("rejects legacy Newsletter/Strategic Brief fields", () => {
    const item = sample({ edition: "VOL.10", structural_signals: [], regional_signals: [], conclusion: "legacy" });
    const errors = validateMonthlyBriefItem(item).join("\n");
    expect(errors).toContain("edition");
    expect(errors).toContain("structural_signals");
    expect(errors).toContain("regional_signals");
    expect(errors).toContain("conclusion");
  });

  it("requires key flows and what-changed judgment", () => {
    expect(validateMonthlyBriefItem(sample({ key_flows: [] })).join("\n")).toContain("key_flows");
    expect(validateMonthlyBriefItem(sample({ what_changed: "" })).join("\n")).toContain("what_changed");
  });

  it("requires all four publication QC gates", () => {
    const item = sample({
      qc: {
        evidence_status: "PASS",
        red_team_status: "FAIL",
        editorial_coherence_status: "PASS",
        language_terminology_status: "PASS",
      },
    });
    expect(validateMonthlyBriefItem(item).join("\n")).toContain("red_team_status");
    expect(isOfficialMonthlyBrief(item)).toBe(false);
  });

  it("requires baseline provenance and real calendar dates", () => {
    const item = sample({
      published_at: "2026-02-31",
      source_baseline: { main_commit_sha: "bad", full_blob_sha: "bad", source_month_count: 100 },
    });
    const errors = validateMonthlyBriefItem(item).join("\n");
    expect(errors).toContain("real YYYY-MM-DD calendar date");
    expect(errors).toContain("main_commit_sha");
    expect(errors).toContain("full_blob_sha");
  });

  it("rejects key-flow evidence outside the governed source set", () => {
    const item = sample({ key_flows: [{ id: "01", title: "flow", summary: "summary", card_ids: ["UNKNOWN_CARD"] }] });
    expect(validateMonthlyBriefItem(item).join("\n")).toContain("must exist in source_card_ids");
  });

  it("requires refs to be contiguous, unique and one-to-one with source cards", () => {
    const item = sample({
      refs: [
        { n: 2, id: "2026-08-01_US_01", title: "미국 카드", date: "2026-08-01" },
        { n: 3, id: "2026-08-01_US_01", title: "중복 카드", date: "2026-08-01" },
      ],
    });
    const errors = validateMonthlyBriefItem(item).join("\n");
    expect(errors).toContain("must equal 1");
    expect(errors).toContain("must be unique");
    expect(errors).toContain("must have a matching refs[].id entry");
  });

  it("enforces revision semantics and month/revision uniqueness", () => {
    expect(validateMonthlyBriefItem(sample({ revision: 2, status: "published" })).join("\n")).toContain("revision 1");
    expect(validateMonthlyBriefItem(sample({ revision: 1, status: "revised" })).join("\n")).toContain("revision >= 2");
    expect(validateMonthlyBriefItem(sample({ revision: 2, status: "revised" }))).toEqual([]);
    const a = sample();
    const b = sample({ id: "monthly-brief-duplicate" });
    expect(validateMonthlyBriefLibrary({ schema_version: "monthly-brief.v1", items: [a, b] }).join("\n")).toContain("month + revision must be unique");
  });

  it("validates the repository public official library", () => {
    const library = JSON.parse(fs.readFileSync(path.join(root, "public/data/monthly_briefs.json"), "utf8"));
    expect(validateMonthlyBriefLibrary(library)).toEqual([]);
  });
});

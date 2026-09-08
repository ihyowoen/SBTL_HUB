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
    conclusion: "자동화는 탐색을 돕고, 공식 결론은 편집 검증을 거쳐 발행한다.",
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

describe("official Strategic Brief publication boundary", () => {
  it("accepts a fully approved editorially curated issue", () => {
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

  it("allows automation-assisted production only after editorial curation", () => {
    const item = sample({ publication_mode: "manual_editorial" });
    expect(validateStrategicBriefItem(item).join("\n")).toContain("publication_mode");
    expect(isOfficialStrategicBrief(item)).toBe(false);
  });

  it("requires all four publication QC gates to pass", () => {
    const item = sample({
      qc: {
        evidence_status: "PASS",
        red_team_status: "FAIL",
        editorial_coherence_status: "PASS",
        language_terminology_status: "PASS",
      },
    });
    const errors = validateStrategicBriefItem(item).join("\n");
    expect(errors).toContain("red_team_status");
    expect(isOfficialStrategicBrief(item)).toBe(false);
  });

  it("requires baseline provenance for a public issue", () => {
    const item = sample({ source_baseline: { main_commit_sha: "bad", full_blob_sha: "bad", source_month_count: 100 } });
    const errors = validateStrategicBriefItem(item).join("\n");
    expect(errors).toContain("main_commit_sha");
    expect(errors).toContain("full_blob_sha");
  });

  it("rejects impossible calendar dates", () => {
    const item = sample({ published_at: "2026-02-31" });
    expect(validateStrategicBriefItem(item).join("\n")).toContain("real YYYY-MM-DD calendar date");
  });

  it("requires a conclusion instead of allowing a structural-signal list to stand in for the issue-level judgment", () => {
    const item = sample({ conclusion: "" });
    expect(validateStrategicBriefItem(item).join("\n")).toContain("conclusion");
  });

  it("rejects structural-signal evidence outside the governed source set", () => {
    const item = sample({
      structural_signals: [{ id: "01", title: "signal", summary: "summary", card_ids: ["UNKNOWN_CARD"] }],
    });
    expect(validateStrategicBriefItem(item).join("\n")).toContain("must exist in source_card_ids");
  });

  it("applies the same governed-source rule to regional signals", () => {
    const item = sample({
      regional_signals: [{ title: "북미", summary: "지역 요약", card_ids: ["UNKNOWN_CARD"] }],
    });
    expect(validateStrategicBriefItem(item).join("\n")).toContain("regional_signals[0].card_ids[0]");
  });

  it("requires refs to be a one-to-one, contiguous public resolution table", () => {
    const item = sample({
      refs: [
        { n: 2, id: "2026-08-01_US_01", title: "미국 카드", date: "2026-08-01" },
        { n: 3, id: "2026-08-01_US_01", title: "중복 카드", date: "2026-08-01" },
      ],
    });
    const errors = validateStrategicBriefItem(item).join("\n");
    expect(errors).toContain("must equal 1");
    expect(errors).toContain("must be unique");
    expect(errors).toContain("must have a matching refs[].id entry");
  });

  it("rejects detached refs that are outside source_card_ids", () => {
    const item = sample({
      refs: [
        { n: 1, id: "2026-08-01_US_01", title: "미국 카드", date: "2026-08-01" },
        { n: 2, id: "DETACHED", title: "분리 카드", date: "2026-08-02" },
      ],
    });
    expect(validateStrategicBriefItem(item).join("\n")).toContain("must exist in source_card_ids");
  });

  it("requires editorial approval before publication and keeps approval no later than publication", () => {
    const item = sample({ approval: { status: "APPROVED", approved_at: "2026-09-09", reviewer_role: "editorial_owner" } });
    expect(validateStrategicBriefItem(item).join("\n")).toContain("cannot be later than published_at");
  });

  it("reserves published for revision 1 and revised for later revisions", () => {
    expect(validateStrategicBriefItem(sample({ revision: 2, status: "published" })).join("\n")).toContain("revision 1");
    expect(validateStrategicBriefItem(sample({ revision: 1, status: "revised" })).join("\n")).toContain("revision >= 2");
    expect(validateStrategicBriefItem(sample({ revision: 2, status: "revised" }))).toEqual([]);
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

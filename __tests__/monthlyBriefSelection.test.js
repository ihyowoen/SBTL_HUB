import { describe, expect, it } from "vitest";
import { matchesMonthlyBriefRequest, selectMonthlyBrief } from "../src/monthlyBriefSelection.js";

const issues = [
  { id: "monthly-2026-08-r1", month: "2026-08", revision: 1 },
  { id: "monthly-2026-07-r1", month: "2026-07", revision: 1 },
];

describe("official Monthly Brief selection policy", () => {
  it("selects an exact requested month", () => {
    const out = selectMonthlyBrief(issues, { month: "2026-08" });
    expect(out.issue?.id).toBe("monthly-2026-08-r1");
    expect(out.requestMissing).toBe(false);
    expect(matchesMonthlyBriefRequest(issues[0], { month: "2026-08" })).toBe(true);
  });

  it("never falls back to another month when the requested brief is absent", () => {
    const out = selectMonthlyBrief(issues, { month: "2026-09" });
    expect(out.issue).toBeNull();
    expect(out.requestMissing).toBe(true);
  });

  it("uses selected/latest behavior only when no month was specifically requested", () => {
    expect(selectMonthlyBrief(issues, null, "monthly-2026-07-r1").issue?.id).toBe("monthly-2026-07-r1");
    expect(selectMonthlyBrief(issues).issue?.id).toBe("monthly-2026-08-r1");
  });
});

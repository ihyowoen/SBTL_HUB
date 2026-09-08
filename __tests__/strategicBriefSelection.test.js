import { describe, expect, it } from "vitest";
import { matchesStrategicRequest, selectStrategicIssue } from "../src/strategicBriefSelection.js";

const issues = [
  { id: "vol10-r1", edition: "VOL.10", month: "2026-08", revision: 1 },
  { id: "vol09-r1", edition: "VOL.09", month: "2026-07", revision: 1 },
];

describe("official Strategic Brief selection policy", () => {
  it("selects an exact requested month", () => {
    const out = selectStrategicIssue(issues, { month: "2026-08" });
    expect(out.issue?.id).toBe("vol10-r1");
    expect(out.requestMissing).toBe(false);
  });

  it("selects an exact requested edition", () => {
    expect(matchesStrategicRequest(issues[0], { edition: "VOL.10" })).toBe(true);
    expect(selectStrategicIssue(issues, { edition: "VOL.10" }).issue?.id).toBe("vol10-r1");
  });

  it("never falls back to another issue when the requested official issue is absent", () => {
    const out = selectStrategicIssue(issues, { month: "2026-09" });
    expect(out.issue).toBeNull();
    expect(out.requestMissing).toBe(true);
  });

  it("uses selected/latest behavior only when no official issue was specifically requested", () => {
    expect(selectStrategicIssue(issues, null, "vol09-r1").issue?.id).toBe("vol09-r1");
    expect(selectStrategicIssue(issues).issue?.id).toBe("vol10-r1");
  });
});

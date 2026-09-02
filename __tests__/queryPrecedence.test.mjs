// ops/check_query_precedence.mjs 부정 케이스 — CI 게이트라 실제 PR 에서만 돌던 분기를 여기서 고정한다.
// 스크립트를 자식 프로세스로 실행한다(process.exit 를 쓰는 CLI 라 그게 실제 동작이다).
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { execFileSync } from "child_process";
import { mkdtempSync, writeFileSync, rmSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

const SCRIPT = "ops/check_query_precedence.mjs";
let dir;
beforeAll(() => { dir = mkdtempSync(join(tmpdir(), "qp-")); });
afterAll(() => { rmSync(dir, { recursive: true, force: true }); });

const cell = (region, axis, queries, lastSwept) => ({ region, axis, items: [], queries, lastSwept });
const write = (name, cells) => {
  const p = join(dir, name);
  writeFileSync(p, JSON.stringify({ cells }));
  return p;
};
/** [exitCode, 합쳐진 출력] */
const run = (base, head) => {
  try {
    const out = execFileSync(process.execPath, [SCRIPT, base, head], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    return [0, out];
  } catch (e) {
    return [e.status ?? 1, String(e.stdout ?? "") + String(e.stderr ?? "")];
  }
};

describe("check_query_precedence — 통과해야 하는 경로", () => {
  it("변경 없음", () => {
    const c = [cell("CN", "trade", ["q1", "q2", "q3"], "2026-08-31")];
    const [code] = run(write("b1.json", c), write("h1.json", c));
    expect(code).toBe(0);
  });

  it("쿼리만 추가 (스탬프 전진 없음) — 선행 PR 이 해야 할 일", () => {
    const [code, out] = run(
      write("b2.json", [cell("CN", "trade", ["q1"], "2026-08-31")]),
      write("h2.json", [cell("CN", "trade", ["q1", "q2", "q3"], "2026-08-31")]));
    expect(code).toBe(0);
    expect(out).toContain("선행성 확인");
  });

  it("스탬프만 전진 (쿼리는 base 에 이미 있음) — 정상 스윕", () => {
    const [code] = run(
      write("b3.json", [cell("CN", "trade", ["q1", "q2", "q3"], "2026-08-31")]),
      write("h3.json", [cell("CN", "trade", ["q1", "q2", "q3"], "2026-09-01")]));
    expect(code).toBe(0);
  });

  it("다른 셀에서 각각 — 쿼리 추가 셀과 스탬프 전진 셀이 다르면 통과", () => {
    const [code] = run(
      write("b4.json", [cell("CN", "trade", ["q1", "q2", "q3"], "2026-08-31"), cell("EU", "trade", ["p1"], "2026-08-31")]),
      write("h4.json", [cell("CN", "trade", ["q1", "q2", "q3"], "2026-09-01"), cell("EU", "trade", ["p1", "p2"], "2026-08-31")]));
    expect(code).toBe(0);
  });
});

describe("check_query_precedence — 막아야 하는 경로", () => {
  it("자기인증 — 같은 셀에서 쿼리 추가 + 스탬프 전진", () => {
    const [code, out] = run(
      write("b5.json", [cell("CN", "trade", ["q1"], "2026-08-31")]),
      write("h5.json", [cell("CN", "trade", ["q1", "q2", "q3"], "2026-09-01")]));
    expect(code).toBe(1);
    expect(out).toContain("CN/trade");
    expect(out).toContain("자기인증");
  });

  it("신규 셀을 쿼리+스탬프째로 추가", () => {
    const [code, out] = run(
      write("b6.json", []),
      write("h6.json", [cell("KR", "packaging", ["q1", "q2", "q3"], "2026-09-01")]));
    expect(code).toBe(1);
    expect(out).toContain("KR/packaging");
  });

  it("어느 셀·어느 쿼리인지 보고한다", () => {
    const [, out] = run(
      write("b7.json", [cell("CN", "trade", [], "2026-08-31")]),
      write("h7.json", [cell("CN", "trade", ["새 쿼리 A"], "2026-09-01")]));
    expect(out).toContain("2026-08-31");
    expect(out).toContain("2026-09-01");
    expect(out).toContain("새 쿼리 A");
  });

  it("lastSwept 가 없던 셀에 처음 찍는 경우도 전진으로 본다", () => {
    const [code] = run(
      write("b8.json", [cell("CN", "trade", [], undefined)]),
      write("h8.json", [cell("CN", "trade", ["q1"], "2026-09-01")]));
    expect(code).toBe(1);
  });
});

describe("check_query_precedence — fail-closed", () => {
  it("깨진 JSON 이면 통과시키지 않는다", () => {
    const p = join(dir, "bad.json");
    writeFileSync(p, "{ broken");
    const [code] = run(p, write("h9.json", []));
    expect(code).not.toBe(0);
  });

  it("인자가 없으면 사용법과 함께 실패한다", () => {
    try {
      execFileSync(process.execPath, [SCRIPT], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
      throw new Error("실패해야 한다");
    } catch (e) {
      expect(e.status).toBe(2);
      expect(String(e.stderr)).toContain("usage");
    }
  });
});

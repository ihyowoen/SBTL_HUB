// MdText 렌더 검증 — 실제 데이터를 서버 렌더해 마커가 태그로 바뀌는지 본다.
// 화면 스크린샷 대신 이 방식을 쓴 이유: 이 변경의 주장은 "마커가 별표로 보이지 않고 강조로 렌더된다"
// 이고, 그 주장은 출력 HTML 로 직접 증명하는 편이 정확하다.
import { describe, it, expect } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "fs";
import MdText from "../src/MdText";
import { parseInline, parseBlocks, visibleText } from "../src/mdParse";

const html = (props) => renderToStaticMarkup(<MdText {...props} />);
const BT = String.fromCharCode(96);

describe("mdParse — 노드 트리", () => {
  it("빈·null 입력", () => {
    expect(parseInline("")).toEqual([]);
    expect(parseInline(null)).toEqual([]);
  });
  it("평문·볼드 위치", () => {
    expect(parseInline("발효 2026-09-01")).toEqual(["발효 2026-09-01"]);
    expect(parseInline("**발효**")).toEqual([{ b: ["발효"] }]);
    expect(parseInline("a **b** c")).toEqual(["a ", { b: ["b"] }, " c"]);
    expect(parseInline("**a** x **b**")).toEqual([{ b: ["a"] }, " x ", { b: ["b"] }]);
  });
  it("볼드 안 코드는 재귀 파싱한다 (실측 16건)", () => {
    expect(parseInline(`**세번 ${BT}7607${BT} 확인**`))
      .toEqual([{ b: ["세번 ", { code: "7607" }, " 확인"] }]);
  });
  it("짝 없는 마커·빈 마커는 리터럴", () => {
    expect(parseInline("**열린 채 끝")).toEqual(["**열린 채 끝"]);
    expect(parseInline("**a** b **c")).toEqual([{ b: ["a"] }, " b **c"]);
    expect(parseInline(`${BT}열린 백틱`)).toEqual([`${BT}열린 백틱`]);
    expect(parseInline("****")).toEqual(["****"]);
  });
  it("헤더 판정 — # 하나·공백 없음은 헤더가 아니다", () => {
    expect(parseBlocks("## 법적 근거")).toEqual([{ h: 2, nodes: ["법적 근거"] }]);
    expect(parseBlocks("### 세부")).toEqual([{ h: 3, nodes: ["세부"] }]);
    expect(parseBlocks("# 제목")).toEqual([{ nodes: ["# 제목"] }]);
    expect(parseBlocks("##제목")).toEqual([{ nodes: ["##제목"] }]);
    expect(parseBlocks("## **강조** 헤더")).toEqual([{ h: 2, nodes: [{ b: ["강조"] }, " 헤더"] }]);
  });
  it("visibleText 는 마커를 뺀 글자만 돌려준다", () => {
    expect(visibleText(parseInline(`**발효** ${BT}7607${BT} 확인`))).toBe("발효 7607 확인");
  });
});

describe("MdText — 마커가 태그로 바뀐다", () => {
  it("볼드", () => {
    const out = html({ text: "발효 **2021-12-09** 확인" });
    expect(out).toContain("<strong");
    expect(out).toContain("2021-12-09");
    expect(out).not.toContain("**");
  });

  it("코드", () => {
    const out = html({ text: `세번 ${BT}7607${BT} 확인` });
    expect(out).toContain("<code");
    expect(out).toContain("7607");
    expect(out).not.toContain(BT);
  });

  it("볼드 안 코드 중첩", () => {
    const out = html({ text: `**세번 ${BT}7607${BT} 확인**` });
    expect(out).toContain("<strong");
    expect(out).toContain("<code");
    expect(out).not.toContain("**");
  });

  it("## 헤더는 block 에서만 처리", () => {
    const withBlock = html({ text: "## 법적 근거", block: true });
    expect(withBlock).toContain("<strong");
    expect(withBlock).not.toContain("## ");
    // block 이 아니면 헤더 문법을 건드리지 않는다(d·tip 은 한 덩어리 문장이다)
    expect(html({ text: "## 법적 근거" })).toContain("## 법적 근거");
  });

  it("개행을 보존한다 (부모의 pre-line 이 처리)", () => {
    expect(html({ text: "## A\n본문", block: true })).toContain("\n");
  });

  it("불릿·단일 별표는 건드리지 않는다", () => {
    expect(html({ text: "• 항목 하나" })).toContain("• 항목 하나");
    expect(html({ text: "a * b" })).toContain("a * b");
  });

  it("짝 없는 마커는 리터럴로 남긴다 — 데이터 결함을 숨기지 않는다", () => {
    const out = html({ text: "**a** b **c" });
    expect(out).toContain("<strong");
    expect(out).toContain("**c");
  });

  it("XSS — 태그 문자열은 이스케이프된다", () => {
    const out = html({ text: '**<img src=x onerror=alert(1)>**' });
    expect(out).toContain("&lt;img");
    expect(out).not.toContain("<img");
  });
});

describe("실데이터 전수", () => {
  const t = JSON.parse(readFileSync("public/data/tracker_data.json", "utf8"));
  const rp = JSON.parse(readFileSync("public/data/region_policy.json", "utf8"));

  it("항목 필드 — 마커 짝이 맞으면 출력에 별표가 남지 않고 내용이 보존된다", () => {
    const leaked = [];
    let checked = 0;
    for (const i of t.items) {
      for (const f of ["d", "tip", "detail"]) {
        const v = i[f];
        if (typeof v !== "string" || !v) continue;
        if ((v.match(/\*\*/g) || []).length % 2) continue;
        checked++;
        const out = html({ text: v, block: f === "detail" });
        if (out.includes("**")) leaked.push(`${i.id}.${f}:별표잔존`);
        const vis = parseBlocks(v).map((ln) => visibleText(ln.nodes)).join("\n");
        const stripped = v.replace(/\*\*/g, "").replace(new RegExp(BT, "g"), "").replace(/^#{2,3} /gm, "");
        if (vis.replace(new RegExp(BT, "g"), "") !== stripped) leaked.push(`${i.id}.${f}:내용변형`);
      }
    }
    expect(checked).toBeGreaterThan(300);
    expect(leaked).toEqual([]);
  });

  it("볼드가 실제로 존재하는 항목이 다수다 (변경이 무의미하지 않다)", () => {
    const withBold = t.items.filter((i) =>
      ["d", "tip", "detail"].some((f) => String(i[f] ?? "").includes("**"))).length;
    expect(withBold).toBeGreaterThan(100);
  });

  it("watchpoint — 마커 짝이 맞는 줄은 강조로 렌더된다", () => {
    const wps = Object.values(rp).filter((v) => v && typeof v === "object")
      .flatMap((v) => v.watchpoints ?? []);
    const even = wps.filter((w) => !((w.match(/\*\*/g) || []).length % 2));
    expect(even.length).toBeGreaterThan(50);
    for (const w of even) {
      const out = html({ text: w });
      if (w.includes("**")) expect(out).toContain("<strong");
      expect(out).not.toContain("**");
    }
  });

  it("watchpoint — 홀수 마커 데이터가 남아 있지 않다", () => {
    const wps = Object.values(rp).filter((v) => v && typeof v === "object")
      .flatMap((v) => v.watchpoints ?? []);
    const odd = wps.filter((w) => (w.match(/\*\*/g) || []).length % 2);
    // 짝 없는 마커의 렌더 동작은 위 단위 테스트에서 별도로 검증한다.
    // 실데이터에서는 데이터 결함 자체가 0건이어야 한다.
    expect(odd).toEqual([]);
  });
});

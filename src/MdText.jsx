// mdParse 의 노드 트리를 React 노드로 렌더한다. dangerouslySetInnerHTML 을 쓰지 않는다.
//
// 부모가 whiteSpace: "pre-line" 이면 줄바꿈은 CSS 가 처리하므로 개행 문자를 그대로 흘린다
// (detail 이 그렇다). d·tip·watchpoint 는 한 덩어리 문장이라 block=false 로 쓴다.
import { parseInline, parseBlocks } from "./mdParse";

const MONO = "'JetBrains Mono',monospace";

function Inline({ nodes, mono }) {
  return nodes.map((n, k) => {
    if (typeof n === "string") return n;
    if (n.code !== undefined)
      return (
        <code
          key={k}
          style={{ fontFamily: mono, fontSize: "0.92em", padding: "0 3px", borderRadius: 3, background: "rgba(127,127,127,0.14)" }}
        >
          {n.code}
        </code>
      );
    return (
      <strong key={k} style={{ fontWeight: 800 }}>
        <Inline nodes={n.b} mono={mono} />
      </strong>
    );
  });
}

/**
 * text — 렌더할 원문. block — `## 헤더` 를 처리할지(detail 전용).
 * 짝 없는 마커는 파서가 리터럴로 남기므로 화면에 그대로 보인다 — 데이터 결함을 숨기지 않는다.
 */
export default function MdText({ text, block = false, mono = MONO }) {
  if (typeof text !== "string" || !text) return null;
  if (!block) return <Inline nodes={parseInline(text)} mono={mono} />;
  const lines = parseBlocks(text);
  return lines.map((ln, k) => {
    const nl = k < lines.length - 1 ? "\n" : "";
    if (ln.h)
      return (
        <span key={k}>
          <strong style={{ fontWeight: 900, fontSize: ln.h === 2 ? "1.06em" : "1em", letterSpacing: "-0.01em" }}>
            <Inline nodes={ln.nodes} mono={mono} />
          </strong>
          {nl}
        </span>
      );
    return (
      <span key={k}>
        <Inline nodes={ln.nodes} mono={mono} />
        {nl}
      </span>
    );
  });
}

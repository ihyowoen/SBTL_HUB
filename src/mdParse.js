// 노출 필드용 경량 마크다운 파서 (순수 — React 의존 없음, node 로 직접 테스트 가능).
//
// 배경 — 트래커 데이터는 `**강조**`·`## 헤더`·`` `코드` `` 를 의도적으로 써 왔는데 앱에는 마크다운
// 렌더러가 없었다. App.jsx 가 d·tip·detail·watchpoint 를 React 생 텍스트로 렌더해서 마커가
// 사용자 화면에 **별표 그대로** 보였다. 실측(2026-09-01): `**` 2,815개(117항목 + watchpoints 313),
// `##` 504개(88항목), 백틱 98개.
//
// 왜 스트립이 아니라 렌더러인가 — 마커를 지우면 강조 정보가 영구 손실되고 다음 run 이 다시 넣는다
// (밀도 높은 카드에서 핵심 사실이 튀어야 하는 것이 이 도구의 값이다). 항목 필드의 마커 짝이
// 0건 어긋나 있어 변환이 안전하다는 점도 렌더러 쪽 근거다.
//
// 범위 — `**볼드**` / `## ### 헤더` / `` `코드` `` 만. `•` 불릿 1,656개는 실제 유니코드 문자라
// 이미 정상 표시되고, `-` 불릿·표·단일 `*` 는 평문으로도 읽히므로 건드리지 않는다.
//
// 원칙 — 짝이 안 맞는 마커는 **지우지 않고 리터럴로 남긴다.** 데이터 결함을 렌더러가 숨기면
// validator 가 잡을 것도 못 잡는다(region_policy watchpoint 10줄이 실제로 홀수다).

const BOLD = '**';
const CODE = '`';

/**
 * 인라인 파서. 반환 노드: string | {b: node[]} | {code: string}
 * 볼드 안 백틱 중첩(실측 16건)이 있어 볼드 내용을 재귀 파싱한다.
 */
export function parseInline(text) {
  if (typeof text !== 'string' || !text) return [];
  const out = [];
  let i = 0, buf = '';
  const flush = () => { if (buf) { out.push(buf); buf = ''; } };
  while (i < text.length) {
    const isBold = text.startsWith(BOLD, i);
    const isCode = !isBold && text[i] === CODE;
    if (!isBold && !isCode) { buf += text[i++]; continue; }
    if (isBold) {
      const end = text.indexOf(BOLD, i + BOLD.length);
      if (end === -1) { buf += BOLD; i += BOLD.length; continue; }      // 짝 없음 → 리터럴
      const inner = text.slice(i + BOLD.length, end);
      if (!inner) { buf += BOLD + BOLD; i = end + BOLD.length; continue; }  // **** → 리터럴
      flush();
      out.push({ b: parseInline(inner) });
      i = end + BOLD.length;
      continue;
    }
    const end = text.indexOf(CODE, i + 1);
    if (end === -1) { buf += CODE; i += 1; continue; }                  // 짝 없음 → 리터럴
    const inner = text.slice(i + 1, end);
    if (!inner) { buf += CODE + CODE; i = end + 1; continue; }
    flush();
    out.push({ code: inner });
    i = end + 1;
  }
  flush();
  return out;
}

/**
 * 블록 파서 — 줄 단위로 `## `/`### ` 헤더를 분리하고 나머지는 인라인.
 * 반환: [{h?: 2|3, nodes: node[]}]
 * 줄 단위가 안전한 근거 — 항목 필드에서 줄을 쪼개도 마커 짝이 깨지는 조각이 0건이다(실측 703조각).
 */
export function parseBlocks(text) {
  if (typeof text !== 'string' || !text) return [];
  return text.split('\n').map((line) => {
    const m = /^(#{2,3})\s+(.*)$/.exec(line);
    if (m) return { h: m[1].length, nodes: parseInline(m[2]) };
    return { nodes: parseInline(line) };
  });
}

/** 테스트·감사용 — 노드 트리에서 보이는 문자열만 뽑는다(마커가 사라졌는지 확인). */
export function visibleText(nodes) {
  return nodes.map((n) => {
    if (typeof n === 'string') return n;
    if (n.code !== undefined) return n.code;
    return visibleText(n.b);
  }).join('');
}

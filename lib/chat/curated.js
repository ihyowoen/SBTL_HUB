// ============================================================================
// Curated analysis generators — card.g 기반 (LLM 미사용)
// ============================================================================
// why / analysis 모드는 큐레이터가 작성한 card.g를 원본 그대로 내보낸다.
// LLM 재해석은 voice·정확도를 희석시키므로 curated 경로를 기본으로 사용한다.
// summary 모드만 해외 원문 번역/요약이 필요하므로 llm.js를 거친다.
// ============================================================================

export function generateWhyImportant(card) {
  const { T, sub, g } = card || {};
  const body = String(g || "").trim();
  if (body) {
    return `⚡ 왜 중요한가\n\n${body}`;
  }
  return `⚡ 왜 중요한가\n\n${sub || T || "아직 분석이 등록되지 않은 카드야."}`;
}

export function generateKoreanSummary(card) {
  const { T, sub, g, src, d } = card || {};
  let factual = g || "";
  if (factual.includes("—")) factual = factual.split("—")[0].trim();
  return [
    `📰 요약`,
    T || "",
    sub || "",
    factual || "",
    src ? `출처: ${src}${d ? " · " + d : ""}` : "",
  ].filter(Boolean).join("\n");
}

export function generateDeepAnalysis(card) {
  const { T, sub, g, r, s, src } = card || {};
  const regionPerspective = {
    US: "FEOC 준수 여부와 45X 크레딧 확보가 시장 접근을 좌우해. Section 301 관세와 맞물려 비중국 공급망 재편을 가속화하고 있어.",
    EU: "Battery Regulation 여권 의무화(2027)와 CBAM 본격 시행을 앞두고 규제 준수 비용이 진입 장벽으로 작용해.",
    CN: "과잉설비 기반 저가 공세와 흑연·리튬 수출 통제가 맞물려 글로벌 공급망 재편의 핵심 변수야.",
    KR: "ESS 안전기준 강화와 용량시장 입찰 확대가 국내 시장 구조를 바꾸고 있어. 수출 규제 대응과 내수 성장을 동시에 고려해야 해.",
    JP: "GX 20조엔 투자와 METI 보조금이 ESS 시장을 본격 열고 있어. 계통유연성 조정력 수요가 구체화되고 있어.",
  };
  const signalDepth = {
    t: "구조적 전환 신호 — 업계 전반의 방향을 바꿀 수 있는 변화야. 즉각적인 전략 검토가 필요해.",
    h: "고임팩트 신호 — 단기(3~6개월) 내 대응 조치가 필요해.",
    m: "중기 관찰 대상 — 12개월 이상의 추세 변화로 연결될 수 있어.",
    i: "배경 정보 — 맥락 이해와 중장기 추적에 활용해.",
  };
  const watchpointByRegion = {
    US: ["MACR 기준 변화", "Section 301 관세 갱신 여부", "Treasury FEOC 가이드라인"],
    EU: ["Battery Passport 파일럿 일정", "CBAM 전환기 종료 후 실제 부과", "CRM Act 광물 목록 업데이트"],
    CN: ["흑연 수출허가 실제 운용", "LFP 설비 과잉 조정 신호", "제3국 우회 수출 규모"],
    KR: ["ESS 안전기준 개정 시행일", "용량시장 입찰 결과", "배터리 여권 국내 적용 로드맵"],
    JP: ["METI 보조금 2차 공모 시기", "GX 채권 집행 진도", "계통용 ESS 접속 규칙 개정"],
  };
  const wp = watchpointByRegion[r] || ["공급망 변화", "규제 동향", "시장 가격 추이"];
  return [
    `🔍 분석`,
    g || sub || T,
    regionPerspective[r] ? `\n[지역 맥락] ${regionPerspective[r]}` : "",
    `\n[시그널 강도] ${signalDepth[s] || "추가 관찰이 필요해."}`,
    `\n[관전 포인트]\n• ${wp.join("\n• ")}`,
    src ? `\n출처: ${src}` : "",
  ].filter(Boolean).join("\n");
}

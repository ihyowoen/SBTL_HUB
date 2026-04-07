import fs from "node:fs/promises";
import path from "node:path";

export const REGION_KR_LABEL = { US: "미국", KR: "한국", CN: "중국", EU: "유럽", JP: "일본", GL: "글로벌", NA: "북미" };

export const REGION_POLICY = {
  US: {
    title: "미국 정책",
    policies: [
      { name: "IRA / FEOC", desc: "IRA §45X·§48E 제조·투자 세액공제 — FEOC 규정으로 중국산 배터리·소재 사용 시 크레딧 박탈. MACR 55% 기준(2026) 적용 중." },
      { name: "관세 (Section 301)", desc: "대중국 배터리셀 관세 54~58%. BOS 부품에도 §232 관세 50% 별도 → 실질 80%+ 차단벽." },
      { name: "제조 인센티브", desc: "45X 첨단제조 크레딧으로 미국 내 셀·모듈·광물 가공 공장 유치. 2030년 MACR 85% 목표." },
      { name: "ESS / 전력", desc: "ITC(§48E) standalone ESS 30~50% + 커뮤니티 보너스. FERC Order 2222로 분산자원 시장참여 확대." },
    ],
    why: "미국 에너지 전환 정책은 K-배터리에 기회이자 리스크 — FEOC 준수 여부가 시장 접근 자체를 결정한다.",
    watchpoints: ["Treasury proposed regulation Q2 발표 여부", "Section 301 관세 8월 만료·연장 결정", "45X MACR 2027 기준 60% 전환 대비"],
  },
  EU: {
    title: "유럽 정책",
    policies: [
      { name: "Battery Regulation", desc: "2027년부터 배터리 여권(Battery Passport) 의무화. 탄소발자국 등급 공개, 재활용률 의무 부과." },
      { name: "CBAM", desc: "탄소국경조정메커니즘 — 수입품에 EU 탄소가격 부과. 배터리 소재·철강·알루미늄 대상." },
      { name: "CRM Act", desc: "핵심원자재법 — 리튬·코발트·니켈 등 전략광물 EU 내 가공 40%, 재활용 25% 목표." },
      { name: "보조금", desc: "IPCEI 배터리 프로젝트 + 각국 개별 보조금. Northvolt 사태 이후 보조금 심사 강화 추세." },
    ],
    why: "EU는 규제 중심 접근 — 규정 준수 비용이 시장 진입 장벽이 되므로 조기 대응이 핵심이다.",
    watchpoints: ["Battery Passport 파일럿 일정", "CBAM 전환기 종료(2026.12) 이후 본 부과 시작", "CRM Act 광물 목록 업데이트"],
  },
  CN: {
    title: "중국 정책",
    policies: [
      { name: "산업정책", desc: "국가 차원 배터리 산업 육성. CATL·BYD 등 대형사 보조금·세제 혜택. 내수 EV 보급 세계 1위 유지." },
      { name: "공급망 통제", desc: "흑연·리튬·희토류 수출 통제 강화. 가공 단계 독점적 지위를 지렛대로 활용." },
      { name: "가격 경쟁", desc: "LFP 셀 가격 $50/kWh 이하 진입. 과잉설비 기반 저가 공세로 글로벌 시장 점유율 확대." },
      { name: "수출 전략", desc: "BESS 수출 급증 — 미국 관세 우회 위해 모로코·헝가리 등 제3국 가공기지 확대." },
    ],
    why: "중국은 가격과 공급망을 동시에 장악 — 비중국 플레이어의 생존 전략 수립에 가장 큰 변수다.",
    watchpoints: ["흑연 수출허가제 실제 운용 강도", "LFP 과잉설비 조정 신호", "제3국 우회 수출 규모 추이"],
  },
  KR: {
    title: "한국 정책",
    policies: [
      { name: "ESS 정책", desc: "산업부 ESS 안전기준 개정 + 대규모 ESS 실증사업. 화재 안전 인증 강화." },
      { name: "입찰 / 조달", desc: "한전 ESS 용량시장 입찰. 재생에너지 연계 ESS 의무화 확대." },
      { name: "실증 / R&D", desc: "전고체·리튬황 차세대 배터리 국가 R&D. K-배터리 2030 로드맵 추진." },
      { name: "규제 방향", desc: "EU Battery Regulation 대응 — 배터리 여권 국내 도입 검토. 재활용 의무 강화 로드맵." },
    ],
    why: "K-배터리의 본거지 — 내수 ESS 시장 성장과 수출 규제 대응을 동시에 준비해야 한다.",
    watchpoints: ["ESS 안전기준 개정안 시행 시점", "용량시장 ESS 입찰 결과", "배터리 여권 국내 적용 로드맵 발표"],
  },
  JP: {
    title: "일본 정책",
    policies: [
      { name: "GX (Green Transformation)", desc: "GX 추진법 기반 20조엔 투자. 배터리·수소·원자력 포함한 에너지 전환 가속." },
      { name: "배터리 지원", desc: "METI 대규모 축전시스템 보조금 (보조율 33~66%). 도쿄도 별도 20억엔 지원." },
      { name: "전력정책", desc: "재생에너지 주력전원화 + 계통유연성 확보. ESS를 조정력 수단으로 본격 활용." },
    ],
    why: "일본은 에너지 안보 관점에서 ESS를 전략자산화 — 보조금 규모가 시장 형성 속도를 결정한다.",
    watchpoints: ["METI 축전 보조금 2차 공모 시기", "GX 채권 발행·집행 진도", "계통용 ESS 접속 규칙 개정"],
  },
  GL: {
    title: "글로벌 공통",
    policies: [
      { name: "공급망 재편", desc: "미·중 디커플링 가속. 중간재 가공 거점이 동남아·중동·아프리카로 분산." },
      { name: "광물 확보 경쟁", desc: "리튬·니켈·코발트·흑연 확보전. 자원국 수출 규제 확대 추세." },
    ],
    why: "글로벌 밸류체인 재편은 모든 지역 정책의 배경이 된다 — 공급망 지도가 바뀌고 있다.",
    watchpoints: ["인도네시아 니켈 수출 정책 변화", "칠레·아르헨티나 리튬 국유화 동향"],
  },
  NA: {
    title: "미국 정책",
    policies: [
      { name: "IRA / FEOC", desc: "IRA §45X·§48E 제조·투자 세액공제 — FEOC 규정으로 중국산 배터리·소재 사용 시 크레딧 박탈. MACR 55% 기준(2026) 적용 중." },
      { name: "관세 (Section 301)", desc: "대중국 배터리셀 관세 54~58%. BOS 부품에도 §232 관세 50% 별도 → 실질 80%+ 차단벽." },
    ],
    why: "미국 에너지 전환 정책은 K-배터리에 기회이자 리스크 — FEOC 준수 여부가 시장 접근 자체를 결정한다.",
    watchpoints: ["Treasury proposed regulation Q2 발표 여부", "Section 301 관세 8월 만료·연장 결정"],
  },
};

export const BRAVE_KEYWORDS = /(실시간|외부|원문|링크|기사\s*검색|brave|외부\s*기사|최신\s*기사|검색해|찾아줘.*기사|뉴스\s*링크|외부\s*링크)/i;

export function fmtDate(date) {
  if (!date) return "-";
  const s = String(date).trim();
  const m = s.match(/^(\d{4})[.-](\d{2})[.-](\d{2})/);
  if (m) return `${m[1]}.${m[2]}.${m[3]}`;
  return s;
}

export function kstToday() {
  const now = new Date();
  const kst = new Date(now.getTime() + (now.getTimezoneOffset() + 540) * 60000);
  return `${kst.getFullYear()}.${String(kst.getMonth() + 1).padStart(2, "0")}.${String(kst.getDate()).padStart(2, "0")}`;
}

export function toCardView(card) {
  return {
    title: card?.T || "",
    subtitle: card?.sub || "",
    signal: card?.s || "i",
    url: card?.url || "",
    region: card?.r || "",
    date: card?.d || "",
    source: card?.src || "",
    gist: card?.g || "",
  };
}

export function toLinkView(link) {
  return {
    title: link?.title || "",
    description: link?.description || "",
    url: link?.url || "",
  };
}

function projectRoot() {
  return process.cwd();
}

async function readJsonFile(absPath, fallback) {
  try {
    const raw = await fs.readFile(absPath, "utf8");
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export async function loadKnowledge() {
  const root = projectRoot();
  const cardsPath = path.join(root, "public", "data", "cards.json");
  const faqPath = path.join(root, "public", "data", "faq.json");
  const trackerPath = path.join(root, "public", "data", "tracker_data.json");

  const [cardsRaw, faqRaw, trackerRaw] = await Promise.all([
    readJsonFile(cardsPath, []),
    readJsonFile(faqPath, []),
    readJsonFile(trackerPath, { meta: {}, items: [] }),
  ]);

  const cards = Array.isArray(cardsRaw) ? cardsRaw : (cardsRaw?.cards || []);
  const faq = Array.isArray(faqRaw) ? faqRaw : [];
  const tracker = {
    meta: trackerRaw?.meta || {},
    items: Array.isArray(trackerRaw?.items) ? trackerRaw.items : [],
    sources: trackerRaw?.sources || {},
  };

  return { cards, faq, tracker };
}

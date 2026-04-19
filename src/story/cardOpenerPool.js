// src/story/cardOpenerPool.js
// ============================================================================
// Opener Pool + Rule Matcher + Few-shot 선택
// ============================================================================
// 배터리 상담소 재설계 Phase 1 (2026-04-19).
//
// 책임:
//   1. 카드 → opener 카테고리 분류 (classifyCard)
//   2. 카드 → entity set 추출 (extractEntities) — weighted retrieve에서도 재사용
//   3. 카테고리 × pool에서 few-shot 샘플 N개 추출 (pickFewShotExamples)
//   4. LLM 실패 시 fallback opener 하나 반환 (pickFallbackOpener)
//
// Pool의 역할 = LLM voice anchor (출력 자체가 아니라 few-shot 교사).
// Pool이 그대로 UI에 노출되는 건 LLM 호출 실패 시의 graceful fallback 뿐.
//
// 재설계 원칙 (Claire 2026-04-19 확정):
//   - 반말, 끊어 읽힘
//   - 2~3문장 + 미끼 hint 한 줄로 끝
//   - "X가 아니라 Y" 대립 구조 금지 (Claire 극혐)
//   - AI 공식 템플릿 금지 ("이 카드는…", "이 이슈는…")
//   - 미끼 = 질문 아님. 여지 ("여기서 걸리는 건 —", "해석이 두 갈래 나뉠 건데 —")
// ============================================================================

// ─── Entity patterns ───────────────────────────────────────────────────────
// 텍스트 기반 회사 매칭 regex. classifyCard + weighted retrieve 공용.
// 필요 시 Phase 1.5에서 확장 (현재 MVP는 배터리 셀/소재 Top-N + 주요 OEM).
export const ENTITY_PATTERNS = {
  LG:        /LG에너지솔루션|LG엔솔|LGES|LG\s*Energy\s*Solution/i,
  SAMSUNG:   /삼성SDI|Samsung\s*SDI/i,
  SK:        /SK온|SK\s*On|SK이노베이션|SK\s*Innovation/i,
  CATL:      /CATL|寧德時代|닝더|닝데시다이/i,
  BYD:       /BYD|比亞迪|비야디/i,
  POSCO_FM:  /포스코퓨처엠|POSCO\s*Future\s*M/i,
  ECOPRO:    /에코프로|EcoPro/i,
  LGCHEM:    /LG화학|LG\s*Chem/i,
  TESLA:     /테슬라|Tesla/i,
  FORD:      /\bFord\b|포드/,
  GM:        /\bGM\b|General\s*Motors|지엠/,
  VW:        /폭스바겐|Volkswagen|\bVW\b/i,
  HONDA:     /혼다|Honda/i,
  TOYOTA:    /토요타|Toyota/i,
  NORTHVOLT: /노스볼트|Northvolt/i,
  STELLANTIS:/스텔란티스|Stellantis/i,
};

const K_BATTERY_KEYS = ['LG', 'SAMSUNG', 'SK'];
const CN_BATTERY_KEYS = ['CATL', 'BYD'];

// 카드 텍스트 합성 — regex 매칭용. title + sub + gate + fact + implication[].
function getCardText(card) {
  if (!card) return '';
  const parts = [
    card.title || card.T || '',
    card.sub || '',
    card.gate || card.g || '',
    card.fact || '',
  ];
  if (Array.isArray(card.implication)) {
    parts.push(card.implication.filter(Boolean).join(' '));
  } else if (card.implication) {
    parts.push(String(card.implication));
  }
  return parts.filter(Boolean).join(' ');
}

// ─── extractEntities ───────────────────────────────────────────────────────
export function extractEntities(card) {
  const text = getCardText(card);
  const hits = new Set();
  if (!text) return hits;
  for (const [key, re] of Object.entries(ENTITY_PATTERNS)) {
    if (re.test(text)) hits.add(key);
  }
  return hits;
}

// ─── classifyCard ──────────────────────────────────────────────────────────
// 우선순위 높은 카테고리부터 매칭. 매칭 결과에 따라 opener pool + task 지시가 달라짐.
export function classifyCard(card) {
  if (!card) return 'default';
  const cat = String(card.cat || '').toLowerCase();
  const region = String(card.region || card.r || '').toUpperCase();
  const text = getCardText(card);
  const entities = extractEntities(card);

  // 1. M&A/JV (구조적 거래 — 가장 특징적이라 우선)
  if (/합작|JV|M&A|인수|매각|청산|해지|분사|스핀오프|spin-?off|merger|acquisition/i.test(text)) {
    return 'ma_jv';
  }

  // 2. 중국 셀 업체 중심
  for (const k of CN_BATTERY_KEYS) if (entities.has(k)) return 'catl_cn';

  // 3. K-3사 중심
  for (const k of K_BATTERY_KEYS) if (entities.has(k)) return 'kbattery';

  // 4. 정책 (region 분기)
  if (cat === 'policy' || cat === 'macro' || /정책|규제|법안|보조금|관세|tariff|regulation|policy/i.test(text)) {
    if (region === 'EU') return 'policy_eu';
    if (region === 'KR') return 'policy_kr';
    return 'policy_other';
  }

  // 5. ESS
  if (cat === 'ess' || /\bESS\b|\bBESS\b|그리드\s*스토리지|계통\s*(연계|저장)|축전지/i.test(text)) {
    return 'ess';
  }

  // 6. 기술
  if (cat === 'tech' || /전고체|나트륨|실리콘\s*음극|양산|파일럿|TRL|리튬\s*황|solid-?state|sodium-?ion/i.test(text)) {
    return 'tech';
  }

  return 'default';
}

// ─── OPENER_POOLS ──────────────────────────────────────────────────────────
// 각 카테고리 2-3개. LLM few-shot 교사용.
// Voice: 반말, 끊어 읽힘, 미끼로 끝남, 카드 요약 반복 없음, "X가 아니라 Y" 없음.
// ※ Claire voice 교정 예정 (Phase 1 리뷰 단계).
export const OPENER_POOLS = {
  policy_eu: [
    { id: 'eu-01', text: '유럽 칼춤 또 도네. 타이밍이 묘한데 — 앞뒤 조치랑 세트로 봐야 그림 나와.' },
    { id: 'eu-02', text: '이거 발표 시점이 관건이야. 전 분기 배터리법 수정안이랑 묶이면 해석 달라져.' },
    { id: 'eu-03', text: '유럽은 표 정치 계절이라 제조업 민심 안 건드리고는 못 가. 여기서 걸리는 건 —' },
  ],
  policy_kr: [
    { id: 'kr-01', text: '국내 정책 타이밍 읽어야 해. 연말 예산이나 부처 재편 시그널이랑 같이 봐야겠어.' },
    { id: 'kr-02', text: '산업부 움직임은 항상 업계 요청이 먼저 있었나 봐야 해. 뒤가 궁금한데 —' },
    { id: 'kr-03', text: '국내 정책은 보조금 쪽부터 파고들어야 그림 보여. 여기서 눈여겨볼 건 —' },
  ],
  policy_other: [
    { id: 'po-01', text: '지역 바뀌면 해석 축도 바뀌어. 이 나라 내 정책 사이클이랑 같이 봐야 해.' },
    { id: 'po-02', text: '이 지역 정책은 원래 예고가 먼저 떨어지는 곳이야. 뒤에 뭐가 붙을지가 관건인데 —' },
  ],
  catl_cn: [
    { id: 'catl-01', text: 'CATL 또 CATL. 이번 각도가 좀 달라 — 직전 파트너십 건이랑 같은 결로 봐야 해.' },
    { id: 'catl-02', text: '중국 쪽 숫자는 일단 의심부터. 여기서 걸리는 건 —' },
    { id: 'catl-03', text: 'BYD·CATL 이중 체제가 동시에 움직일 땐 뒤에 정부 의중 있어. 어느 라인이냐가 중요해.' },
  ],
  kbattery: [
    { id: 'kb-01', text: '우리 쪽 플레이어야. 해석이 두 갈래 나뉠 건데 — 재무냐 포트폴리오냐야.' },
    { id: 'kb-02', text: '이 숫자, 분기 단위로 읽으면 답 달라져. 직전 공시랑 비교하면 —' },
    { id: 'kb-03', text: 'K-3사 동향은 고객사 OEM 로드맵이랑 묶어 봐야 해. 여기서 걸리는 건 —' },
  ],
  tech: [
    { id: 'tech-01', text: '기술 건이네. 양산까지 얼마 남았을까 — TRL 얘기 먼저 해야 해.' },
    { id: 'tech-02', text: '실험실 스펙이랑 양산 스펙은 다른 얘기야. 여기서 유의할 건 —' },
    { id: 'tech-03', text: '성능 숫자보다 공정 난이도가 더 궁금한 대목인데 —' },
  ],
  ma_jv: [
    { id: 'mj-01', text: 'JV 결별은 보통 정치 냄새 먼저인데, 여긴 경제 논리가 더 세 보여.' },
    { id: 'mj-02', text: '숫자 뒤에 회계 의도 있어. 뭘 털려는 건지가 포인트인데 —' },
    { id: 'mj-03', text: '매각가 자체가 시그널이야. 이 수준이면 급한 쪽이 누구냐가 바로 보여.' },
  ],
  ess: [
    { id: 'ess-01', text: 'ESS야. 수익성 구조부터 볼까, 입찰 환경부터 볼까.' },
    { id: 'ess-02', text: '그리드 연계 ESS는 정책 비중이 커. 여기서 걸리는 건 보조금 구조인데 —' },
    { id: 'ess-03', text: 'ESS 수주는 단가보다 계약 구조가 먼저 — 여기서 눈여겨볼 건 —' },
  ],
  default: [
    { id: 'def-01', text: '이 건 들고 왔네. 여기서 걸리는 건 타이밍이야 — 앞 흐름이랑 묶어 봐야 해.' },
    { id: 'def-02', text: '숫자는 숫자대로, 문맥은 문맥대로 봐야 해. 어느 축이 더 궁금한지 —' },
    { id: 'def-03', text: '이 카테고리는 한 번에 끊기 어려워. 각도 하나 먼저 잡자 —' },
  ],
};

// ─── pickFewShotExamples ───────────────────────────────────────────────────
// 해당 category pool에서 N개 샘플 반환.
// recentUsedIds에 있는 opener는 배제. 만약 배제 결과 0개면 recent 무시하고 전체 사용.
export function pickFewShotExamples(category, recentUsedIds = [], count = 3) {
  const primaryPool = OPENER_POOLS[category] || OPENER_POOLS.default;
  const recentSet = new Set(recentUsedIds || []);
  let candidates = primaryPool.filter((o) => !recentSet.has(o.id));
  if (candidates.length === 0) candidates = primaryPool;

  // 간단 shuffle (Fisher-Yates 대신 sort, 결과 품질 차이 무시)
  const shuffled = [...candidates].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, shuffled.length));
}

// ─── pickFallbackOpener ────────────────────────────────────────────────────
// LLM 호출 실패 시 graceful fallback용 단일 opener.
// LLM 성공 시에는 이 함수 결과는 UI에 절대 노출되지 않음.
export function pickFallbackOpener(category, recentUsedIds = []) {
  const picks = pickFewShotExamples(category, recentUsedIds, 1);
  return picks[0] || OPENER_POOLS.default[0];
}

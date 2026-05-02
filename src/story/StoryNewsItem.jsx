import { memo, useEffect, useMemo, useRef, useState } from 'react';
import { normalizeCard } from './normalizeCard';

// ============================================================================
// 배터리 상담소 재설계 Phase 1 (2026-04-19)
// ----------------------------------------------------------------------------
// 변경점:
//   - 버튼 wording: "이 카드로 계속 물어보기" → "📋 상담 접수"
//   - 버튼 상시 노출: 브리프(핵심만/콕짚기) 펴지 않아도 footer에 항상 있음
//   - callback: onAskChatbot(promptString) → onSubmitConsultation(rawCard)
// ----------------------------------------------------------------------------
// 2026-04-20: 상담 횟수 hint 제거 (per-browser localStorage 카운터라
// 다수 사용자 환경에선 의미 없고 혼란 유발. consultationHint prop은
// 호환성 위해 시그니처에 유지하되 렌더링 안 함.)
// 2026-04-30: 뉴스 이미지 UX 보정
//   - featured 카드는 magazine lead 유지
//   - 일반 뉴스 카드는 compact magazine 구조: 상단 와이드 이미지 + 하단 본문
//   - CSS background-image 대신 <img> + onError fallback chain 사용
//   - 이미지 실패/차단/지연 시 검정 패널 대신 branded gradient fallback 노출
// 2026-05-01: 트래커 신규 항목 카테고리 매처 보강 (NA-012~016, EU-016, CN-016/017, JP-011)
//   - AVIATION 카테고리 신규 추가 (KR-010 ICAO + JP-011 MLIT + CN-016 파워뱅크 cluster)
//   - POLICY: USMCA, Section 232/301/122, IEEPA 추가
//   - MINING: critical minerals, 핵심광물, price floor, plurilateral 추가
//   - BATTERY: 파워뱅크, power bank, 보조배터리 추가
//   - RECYCLE: removability, 분리·교체, Article 11 추가
// 2026-05-01b: 이미지 중복 회피 고도화
//   - Layer 1: 풀 내 중복 4개 제거 (RECYCLE -1, GRID -3) → 158 unique 슬롯
//   - Layer 2: assignCardCoverImages export — 같은 페이지 카드 간 unique 보장
//   - 카테고리 풀 부족 시 DEFAULT 풀로 fallback, 그래도 부족하면 hash collision 허용
//   - 부모 컴포넌트(Home/NewsDesk)에서 cards.map 전에 한 번 호출해서 cover prop 전달
// 2026-05-01c: 컴포넌트·접근성 고도화
//   - React.memo wrap — NewsDesk 60개 카드 re-render 비용 차단
//   - <img alt> 의미 있는 텍스트로 변경 (스크린리더 + SEO)
// 2026-05-02: dedup prop 보존 fix
//   - 일반 카드(featured=false)에서도 coverImage prop을 항상 우선 사용
//   - 기존: `featured && coverImage`만 풀 prefix → 일반 카드는 prop 무시하고 hash 재선택
//   - 부모(Home/NewsDesk)의 assignCardCoverImages unique 배정이 자식까지 전달되지 않던 버그
//   - 수정: imagePool/imageStartIndex 둘 다 coverImage 있으면 0번 위치에 prop 사진 사용
// 2026-05-02b: 이미지 풀 cross-pool 중복 정리 + 자식 onError 점프 제거 (정석 fix)
//   - 풀 위생 (Layer 1): 158 → 165 슬롯, cross-pool 중복 24 → 0, ID 중복 0, 차단 URL 0
//     · 11개 풀 × 15장 균등화, RECYCLE처럼 self-contained 풀 구조
//     · 차단됐던 photo-1548613053(GRID), photo-1466611653911(MINING/GRID/AVIATION),
//       photo-1509391366360(GRID/AVIATION) 모두 제거
//   - 자식 onError 점프 제거 (구조적 fix): imageOffset++ → 부모 dedup 결과를 자식이 깨던 버그 차단
//     · 기존: ad-blocker 차단 → 자식이 풀 안 다음 사진 점프 → cross-pool 중복 사진과 collision
//     · 현재: 차단된 사진은 gradient placeholder로 자연 fallback, 부모 dedup 100% 보존
//   - 사용자별 ad-blocker 환경 차이가 자연스럽게 수용됨 (각자 환경에서 일관됨)
// 2026-05-02c: ORB 차단 5개 사진 → 신규 5개로 1:1 swap (165 슬롯 유지)
//   - DevTools에서 net::ERR_BLOCKED_BY_ORB 확인된 사진들 (Chrome 보안 기능, ad-blocker 아님)
//   - Unsplash 측 응답: HTTP 403 + Content-Type: text/plain → Chrome ORB가 image 응답 아니라고 판단
//   - swap (1:1 위치 매칭, 풀 사이즈 변경 없음):
//     · FACTORY#12: photo-1581092583537 → photo-1513828583688
//     · MINING#3:   photo-1502120963564 → photo-1605371924599
//     · GRID#3:     photo-1513689408657 → photo-1511556532299
//     · GRID#11:    photo-1509390234032 → photo-1501612046469
//     · GRID#12:    photo-1593010729792 → photo-1534398079543
//   - audit: 165장, cross-pool 중복 0, ID 중복 0, 차단 5개 모두 제거
// ============================================================================

const SIG_COLORS = { top: '#F85149', high: '#D29922', mid: '#388BFD', info: '#7D8590', t: '#F85149', h: '#D29922', m: '#388BFD', i: '#7D8590' };
const SIG_LABELS = { top: 'TOP', high: 'HIGH', mid: 'MID', info: 'INFO', t: 'TOP', h: 'HIGH', m: 'MID', i: 'INFO' };
const REG_FLAG = { US: '🇺🇸', KR: '🇰🇷', EU: '🇪🇺', CN: '🇨🇳', JP: '🇯🇵', GL: '🌐', NA: '🇺🇸', 'US/KR': '🇺🇸' };
const THINK_MS = 700;

const IMAGE_POOLS = {
  POLICY: [
    'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1447069387593-a5de0862481e?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1521790797524-b2497295b8a0?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1575517111478-7f6afd0973db?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1523293182030-d79043224701?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1505664194779-8beaceb93744?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1560179707-f14e90ef3623?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1521834311110-85f09629471f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1520607162513-3224339890f8?auto=format&fit=crop&w=600&q=80'
  ],
  FINANCE: [
    'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1633156189777-41d13d474421?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1535320971260-19f223a3176d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1526303328184-c7e6c0c53462?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1518186414747-d74c24729c43?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1565514020179-026fbdd6123e?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1611974717131-fda6f8e75294?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1553729459-efe14ef6055d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1543286386-713bdd548da4?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1520694478166-daaaaec95b69?auto=format&fit=crop&w=600&q=80'
  ],
  FACTORY: [
    'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1616423640778-28d1b53229bd?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1580982555313-09470b19d45e?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1542744095-2ad4870bf002?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1553152531-b98a2fc8d3bf?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1590486803833-ffc6f0861f36?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1604871000636-074fa5117945?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1563906661-2825633802ce?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1513828583688-c52646db42da?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1531206715517-5ca0ba15525a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1508873535684-277a3cbcc4e8?auto=format&fit=crop&w=600&q=80'
  ],
  AUTO: [
    'https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1617704548623-340376564e68?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1580273916550-e323be2ae537?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1591836335805-4c0177757913?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1553265027-29066ca94c03?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1562141961-b5d1852de29a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1510766314828-3ca917d04671?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1517524008410-d4484e913961?auto=format&fit=crop&w=600&q=80'
  ],
  BATTERY: [
    'https://images.unsplash.com/photo-1620800615556-91eecfc5108f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1594818379496-da1e345b0dc3?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1548333341-97d216272bb0?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1490184588517-f42caacd8711?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1559811814-e2c5c320148a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1595190611357-63d91144a72d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1503762687835-129cc7a277e5?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1531945034005-4498e88599fb?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1664262104533-3d077465f242?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1616432655021-36ba9ebf32b8?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1605647540924-852290f6b0d5?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1674480928236-47b24d773c33?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1581092334651-4f7ebce35c91?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1617838596634-1c0ebdc0fc24?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1662991040510-410a8dd10451?auto=format&fit=crop&w=600&q=80'
  ],
  TECH: [
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1517433670267-08bbd4be890f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1581093588401-fbb62a02f120?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1555664424-778a1e5e1b48?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1484557985045-bed8eb15629f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1531297172869-c8d196f0ba82?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1535223289827-42f1e9919769?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1580894732230-28045934522f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1526628953301-3e58b16b1427?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1614332287897-cdc485fa562d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1581092780795-1f9e2ed37851?auto=format&fit=crop&w=600&q=80'
  ],
  MINING: [
    'https://images.unsplash.com/photo-1578319439584-104c94d37305?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1605371924599-2d0365da26f5?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1523992527425-4198441fd3a4?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1495556650867-99590cea3657?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1604604994333-e5e3170cc3fb?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1516192511155-072048598717?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1501700493788-fa1a4fc0f270?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1473186578172-c141e6798ee4?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1622322306764-7c9b0e25ed4b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1511520668743-d892d4df780b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1599388371360-1e5af3a68132?auto=format&fit=crop&w=600&q=80'
  ],
  RECYCLE: [
    'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1604187351574-c7550fd415ca?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1533038590840-1cde6b66b721?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1516992654410-9309d4587e94?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1595273670150-bd0c3c392e46?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1517404212738-1976fe78ce50?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1591193022657-3932782fe24b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1542601906970-30f95e5944b1?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1532187863486-abf9d39d9992?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1503596476-1c12a8ba09a9?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1495461199391-8c39ab674295?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1503669698509-c9c922ed283f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1563453392212-326f5e854473?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1528190336454-13cd56b45b5a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1547842777-628d6c701768?auto=format&fit=crop&w=600&q=80'
  ],
  GRID: [
    'https://images.unsplash.com/photo-1497440001374-f26997328c1b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1466096115517-bceecbfb6fde?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1511556532299-8f662fc26c06?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1521618755572-156ae0cdd74d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1464306208223-e0b4495a5553?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1490333341-97d216272bb0?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1472086851167-9366e6c1e592?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1620916297397-a4a5402a3c6c?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1501504905252-473c47e087f8?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1554418651-70309daf9ade?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1501612046469-8d76b1009193?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1534398079543-7ae6d016b86a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1528657063073-4ea21213032d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=600&q=80'
  ],
  AVIATION: [
    'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1542296332-2e4473faf563?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1556388158-158ea5ccacbd?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1530521954074-e64f6810b32d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1519677100203-a0e668c92439?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1583773937330-aae4a9bdadbf?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1518066000714-58c45f1a2c0a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1569154941061-e231b4732ef1?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1503925529457-3f3607dd29a1?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1511210204856-42ee950b73c4?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1456221191079-052a65b63487?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1516709848520-22c60a48b556?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1499699480645-56041a8041ce?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1570535313982-f5d68d0af7d0?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1474302770737-173ee21bab63?auto=format&fit=crop&w=600&q=80'
  ],
  DEFAULT: [
    'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1557683316-973673baf926?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1533035353720-f1c6a75cd8ab?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1510511459019-5deeec7138db?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1551021794-01cb121c2780?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1451187863213-d1bcbaae3cfd?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1523961131990-5ea7c61b2107?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1553484771-047a44eee2cb?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1557682250-33bd709cbe85?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1604147495798-57beb5d6af73?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1516110833967-0b5716ca1387?auto=format&fit=crop&w=600&q=80'
  ],
};

function theme(dark = true) {
  return dark
    ? {
        card: '#161B26',
        card2: '#1C2333',
        tx: '#E6EDF3',
        sub: '#9198A1',
        brd: '#21293A',
        cyan: '#58A6FF',
        soft: 'rgba(255,255,255,0.03)',
        shadow: '0 4px 20px rgba(0,0,0,0.3)',
      }
    : {
        card: '#FFFFFF',
        card2: '#FFFFFF',
        tx: '#1A1A2A',
        sub: '#57606A',
        brd: '#E0E3EA',
        cyan: '#0969DA',
        soft: 'rgba(9,105,218,0.03)',
        shadow: '0 4px 16px rgba(0,0,0,0.08)',
      };
}

function fmtDate(date) {
  if (!date) return '-';
  const s = String(date).trim();
  const m = s.match(/^(\d{4})[.-](\d{2})[.-](\d{2})/);
  if (m) return `${m[1]}.${m[2]}.${m[3]}`;
  return s;
}

function uniqueLines(...values) {
  const seen = new Set();
  const out = [];
  values
    .map((value) => String(value || '').trim())
    .filter(Boolean)
    .forEach((value) => {
      const key = value.replace(/\s+/g, ' ').toLowerCase();
      if (seen.has(key)) return;
      seen.add(key);
      out.push(value);
    });
  return out;
}

function hashSeed(value) {
  const seed = String(value || 'story-news-card');
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash << 5) - hash + seed.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function imageCategoryFor(card) {
  const text = [card?.id, card?.title, card?.T, card?.sub, card?.subtitle, card?.gate, card?.g, card?.source, card?.src, card?.region, card?.r]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();

  // AVIATION을 가장 먼저 — 항공·파워뱅크 키워드가 다른 카테고리에 빼앗기지 않게
  if (/(항공|기내|공항|영공|항공편|국토교통|파워뱅크|보조배터리|이동\s*보조\s*배터리|airline|airport|flight|aircraft|aviation|cabin|in.?flight|power.?bank|icao|mlit)/.test(text)) return 'AVIATION';
  if (/(재활용|리사이클|폐배터리|회수|재사용|재제조|순환|분리.교체|removability|article\s*11|recycl|second\s*life|reuse|black\s*mass|블랙매스)/.test(text)) return 'RECYCLE';
  if (/(광산|광물|리튬|니켈|코발트|흑연|망간|채굴|제련|원자재|자원|희토류|핵심광물|critical\s*minerals|price\s*floor|가격하한|plurilateral|rare\s*earth|mineral|mining|graphite|lithium|nickel|cobalt)/.test(text)) return 'MINING';
  if (/(계통|전력망|재생에너지|태양광|풍력|변전소|ESS|BESS|grid|신재생|전력|유틸리티|송전|배전|storage|renewable|solar|wind)/.test(text)) return 'GRID';
  if (/(ira|feoc|crma|cbam|usmca|section\s*232|section\s*301|section\s*122|ieepa|보조금|관세|규제|정부|정책|법안|재무부|백악관|세액공제|공시|입법|의회|산업부|환경부|mou|협력|tariff|subsidy|regulation|policy)/.test(text)) return 'POLICY';
  if (/(실적|이익|영업이익|매출|주가|투자|m&a|상장|자금|조달|금융|적자|흑자|ipo|margin|ebitda|funding|capex|재무|감가|손상|회계|계약|공급계약)/.test(text)) return 'FINANCE';
  if (/(공장|양산|생산|가동|캐파|capa|증설|설비|수율|라인|plant|factory|manufacturing|gigafactory|준공|착공|라인)/.test(text)) return 'FACTORY';
  if (/(테슬라|전기차|ev|완성차|현대차|기아|bmw|자동차|주행|포드|gm|폭스바겐|toyota|honda|충전|charging|dc 충전|46시리즈)/.test(text)) return 'AUTO';
  if (/(배터리|lfp|전고체|양극재|음극재|분리막|전해액|셀|니켈|코발트|흑연|catl|byd|엔솔|sdi|sk온|파우치|모듈)/.test(text)) return 'BATTERY';
  if (/(기술|r&d|특허|연구|개발|혁신|차세대|파일럿|테스트|ai|software|data|semiconductor|반도체)/.test(text)) return 'TECH';
  return 'DEFAULT';
}

/**
 * 카드 리스트에 unique cover image를 배정.
 *
 * 보장사항:
 *   1. 같은 페이지(같은 cards 배열)에서 같은 이미지가 두 번 나오지 않음 — 풀 크기 충분 시
 *   2. 카드 식별자(id/title/date) 기반 hash로 시작점 결정 — 같은 카드는 안정적으로 같은 이미지
 *   3. 카테고리 풀이 다 사용되면 DEFAULT 풀로 fallback, 그래도 부족하면 hash 기반 (collision 허용)
 *
 * @param {Array} cards - normalize 안 한 raw card 객체 리스트
 * @param {Object} [options]
 * @param {Iterable<string>} [options.alreadyUsed] - 외부에서 이미 사용된 이미지 (sticky 카드 등)
 * @returns {Array<string>} cards와 같은 길이의 cover image URL 리스트 (1:1 대응)
 */
export function assignCardCoverImages(cards, options = {}) {
  if (!Array.isArray(cards) || cards.length === 0) return [];
  const used = new Set(options.alreadyUsed || []);
  const result = new Array(cards.length);

  cards.forEach((card, idx) => {
    const category = imageCategoryFor(card);
    const pool = IMAGE_POOLS[category] || IMAGE_POOLS.DEFAULT;
    const seedParts = [
      card?.id,
      card?.d || card?.date,
      card?.T || card?.title,
      card?.src || card?.source,
      category,
    ].filter(Boolean);
    const seed = seedParts.length ? seedParts.join('|') : `card-${idx}`;
    const startIdx = pool.length ? hashSeed(seed) % pool.length : 0;

    // 1. 카테고리 풀에서 unique 시도
    for (let i = 0; i < pool.length; i += 1) {
      const candidate = pool[(startIdx + i) % pool.length];
      if (!used.has(candidate)) {
        used.add(candidate);
        result[idx] = candidate;
        return;
      }
    }

    // 2. DEFAULT 풀로 fallback
    const fallback = IMAGE_POOLS.DEFAULT;
    for (let i = 0; i < fallback.length; i += 1) {
      const candidate = fallback[(startIdx + i) % fallback.length];
      if (!used.has(candidate)) {
        used.add(candidate);
        result[idx] = candidate;
        return;
      }
    }

    // 3. 마지막 폴백: hash 기반 (collision 허용)
    result[idx] = pool[startIdx] || fallback[startIdx % fallback.length];
  });

  return result;
}

function makeBriefLines(card, mode) {
  const summary = uniqueLines(card.fact, card.sub, card.gate, card.title);
  const insight = uniqueLines(card.implicationText, card.gate, card.fact);
  if (mode === 'summary') {
    return summary.slice(0, 2).map((line, idx) => (idx === 0 ? line : `중요한 건 ${line}`));
  }
  return insight.slice(0, 2).map((line, idx) => (idx === 0 ? `강차장식으로 보면 ${line}` : line));
}

function MetaPill({ children, dark, maxWidth }) {
  const t = theme(dark);
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      fontSize: 10,
      color: t.sub,
      fontWeight: 700,
      background: dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)',
      padding: '4px 8px',
      borderRadius: 6,
      maxWidth,
      whiteSpace: maxWidth ? 'nowrap' : 'normal',
      overflow: maxWidth ? 'hidden' : 'visible',
      textOverflow: maxWidth ? 'ellipsis' : 'clip',
    }}>
      {children}
    </span>
  );
}

function SigPill({ sig, label }) {
  return (
    <span style={{
      fontSize: 10,
      fontWeight: 900,
      color: '#fff',
      background: sig,
      padding: '4px 8px',
      borderRadius: 6,
      letterSpacing: '0.5px',
    }}>
      {label}
    </span>
  );
}

function OverlayPill({ children, maxWidth }) {
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      fontSize: 10,
      fontWeight: 700,
      color: 'rgba(255,255,255,0.95)',
      background: 'rgba(0,0,0,0.48)',
      backdropFilter: 'blur(8px)',
      padding: '4px 8px',
      borderRadius: 6,
      maxWidth,
      whiteSpace: maxWidth ? 'nowrap' : 'normal',
      overflow: maxWidth ? 'hidden' : 'visible',
      textOverflow: maxWidth ? 'ellipsis' : 'clip',
    }}>
      {children}
    </span>
  );
}

function StoryNewsItem({
  card,
  dark,
  onSubmitConsultation,
  coverImage = '',
  featured = false,
  // eslint-disable-next-line no-unused-vars
  consultationHint = null,
}) {
  const t = theme(dark);
  const c = useMemo(() => normalizeCard(card), [card]);
  const [activeMode, setActiveMode] = useState(null);
  const [thinkingMode, setThinkingMode] = useState(null);
  const [showSources, setShowSources] = useState(false);
  const timerRef = useRef(null);
  const signalKey = String(c.signal || 'info').toLowerCase();
  const sig = SIG_COLORS[signalKey] || SIG_COLORS.info;
  const sigLabel = SIG_LABELS[signalKey] || 'INFO';
  const regionFlag = REG_FLAG[c.region] || '🌐';
  const sourceText = c.source || card?.src || card?.source || '';
  const sourceUrl = c.primaryUrl || card?.primaryUrl || card?.primary_url || card?.url || (Array.isArray(card?.urls) ? card.urls[0] : '') || '';
  const factSources = useMemo(() => {
    const list = Array.isArray(card?.fact_sources) ? card.fact_sources : [];
    // 형식 검증 — claim + source_url + source_quote 모두 있는 항목만
    return list.filter(s => s && typeof s === 'object' && s.source_url && (s.claim || s.source_quote));
  }, [card?.fact_sources]);
  const hasSources = factSources.length > 0;
  const layout = featured ? 'lead' : 'plain';
  const lines = activeMode ? makeBriefLines(c, activeMode) : [];
  const imageCategory = useMemo(() => imageCategoryFor({ ...card, ...c }), [card, c]);
  const imagePool = useMemo(() => {
    const pool = IMAGE_POOLS[imageCategory] || IMAGE_POOLS.DEFAULT;
    // coverImage prop이 있으면 항상 첫 후보로 사용 (featured 무관) —
    // 부모 컴포넌트의 assignCardCoverImages dedup 결과가 자식까지 그대로 전달되도록.
    const candidates = coverImage ? [coverImage, ...pool] : pool;
    return Array.from(new Set(candidates.filter(Boolean)));
  }, [imageCategory, coverImage]);

  const imageStartIndex = useMemo(() => {
    // coverImage prop이 있으면 항상 첫번째(index 0)부터 — 부모가 unique 배정한 사진을 보존.
    // prop이 없을 때만 hash 기반 fallback (단독 사용/풀 fallback 시).
    if (coverImage) return 0;
    const seed = [card?.id, c.date, c.title, c.source, imageCategory]
      .filter(Boolean)
      .join('|');
    return imagePool.length ? hashSeed(seed) % imagePool.length : 0;
  }, [coverImage, card?.id, c.date, c.title, c.source, imageCategory, imagePool]);

  const [imageOffset, setImageOffset] = useState(0);
  const [imageLoaded, setImageLoaded] = useState(false);

  useEffect(() => {
    setImageOffset(0);
    setImageLoaded(false);
  }, [imageStartIndex, imageCategory]);

  const hasImageCandidate = imagePool.length > 0 && imageOffset < imagePool.length;
  const imageSrc = hasImageCandidate
    ? imagePool[(imageStartIndex + imageOffset) % imagePool.length]
    : null;

  useEffect(() => () => {
    if (timerRef.current) window.clearTimeout(timerRef.current);
  }, []);

  const openBrief = (mode) => {
    if (activeMode === mode && !thinkingMode) {
      setActiveMode(null);
      return;
    }
    if (timerRef.current) window.clearTimeout(timerRef.current);
    setActiveMode(null);
    setThinkingMode(mode);
    timerRef.current = window.setTimeout(() => {
      setThinkingMode(null);
      setActiveMode(mode);
    }, THINK_MS);
  };

  const handleSubmit = () => {
    if (typeof onSubmitConsultation === 'function') {
      onSubmitConsultation(card);
    }
  };

  const footerPadding = layout === 'lead' ? '12px 16px 16px' : '0 16px 16px';
  const briefMode = thinkingMode || activeMode;
  const briefAccent = briefMode === 'summary' ? t.cyan : '#A855F7';

  const renderVisualImage = (height) => (
    <div
      style={{
        position: 'relative',
        height,
        overflow: 'hidden',
        background: `radial-gradient(circle at 15% 20%, ${sig}44, transparent 34%), linear-gradient(135deg, #172033, #1C2333 55%, #24314A)`,
      }}
    >
      {imageSrc ? (
        <img
          key={imageSrc}
          src={imageSrc}
          alt={`${(c.title || card?.T || imageCategory).slice(0, 60)} 관련 이미지`}
          loading="lazy"
          decoding="async"
          onLoad={() => setImageLoaded(true)}
          onError={() => {
            // 2026-05-02b 정석 fix: 풀 점프 제거.
            // 기존: imageOffset++ 로 풀 안 다음 사진 점프 → cross-pool 중복 사진 만나면 부모 dedup 깨짐
            // 현재: ad-blocker 차단 사진은 gradient placeholder로 fallback (renderVisualImage에 이미 구현)
            setImageLoaded(false);
          }}
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition: 'center',
            opacity: imageLoaded ? 1 : 0,
            transition: 'opacity 180ms ease',
          }}
        />
      ) : (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'rgba(255,255,255,0.72)',
            fontSize: 11,
            fontWeight: 900,
            letterSpacing: '0.08em',
            fontFamily: "'JetBrains Mono',monospace",
          }}
        >
          {imageCategory} SIGNAL
        </div>
      )}
    </div>
  );

  return (
    <div style={{ background: t.card2, borderRadius: 16, border: `1px solid ${t.brd}`, overflow: 'hidden', boxShadow: t.shadow, marginBottom: 12 }}>
      <div style={{ height: 4, background: sig }} />

      {layout === 'lead' ? (
        <div style={{ position: 'relative' }}>
          {renderVisualImage(240)}
          <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.08) 0%, rgba(0,0,0,0.38) 42%, rgba(13,17,23,0.95) 100%)' }} />
          <div style={{ position: 'absolute', top: 12, left: 14, right: 14, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10 }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              <SigPill sig={sig} label={sigLabel} />
              <OverlayPill>{regionFlag} {c.region}</OverlayPill>
              <OverlayPill>{fmtDate(c.date)}</OverlayPill>
            </div>
            {sourceText ? <OverlayPill maxWidth={100}>{sourceText}</OverlayPill> : null}
          </div>
          <div style={{ position: 'absolute', bottom: 16, left: 16, right: 16 }}>
            <h3 style={{ margin: 0, color: '#fff', fontSize: 20, lineHeight: 1.35, fontWeight: 900, textShadow: '0 2px 4px rgba(0,0,0,0.6)' }}>
              {c.title || card?.T || '제목 없음'}
            </h3>
            {c.sub ? (
              <p style={{ margin: '8px 0 0', color: 'rgba(255,255,255,0.86)', fontSize: 13, lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {c.sub}
              </p>
            ) : null}
          </div>
        </div>
      ) : (
        <>
          <div style={{ position: 'relative' }}>
            {renderVisualImage(136)}
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.10) 0%, rgba(0,0,0,0.18) 48%, rgba(13,17,23,0.62) 100%)' }} />
            <div style={{ position: 'absolute', top: 10, left: 12, right: 12, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                <SigPill sig={sig} label={sigLabel} />
                <OverlayPill>{regionFlag} {c.region}</OverlayPill>
              </div>
              {sourceText ? <OverlayPill maxWidth={100}>{sourceText}</OverlayPill> : null}
            </div>
            <div style={{ position: 'absolute', bottom: 10, left: 12 }}>
              <OverlayPill>{fmtDate(c.date)}</OverlayPill>
            </div>
          </div>
          <div style={{ padding: 16 }}>
            <h3 style={{ margin: 0, color: t.tx, fontSize: 16, lineHeight: 1.4, fontWeight: 800, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
              {c.title || card?.T || '제목 없음'}
            </h3>
            {c.sub ? (
              <p style={{ margin: '6px 0 0', color: t.sub, fontSize: 12, lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {c.sub}
              </p>
            ) : null}
          </div>
        </>
      )}

      <div style={{ padding: footerPadding, display: 'flex', flexDirection: 'column', gap: 14 }}>
        
        {layout !== 'lead' && <div style={{ height: 1, background: t.brd, margin: '0 -20px 4px' }} />}

        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
          
          <div style={{ display: 'flex', gap: 8, flex: '1 1 100%' }}>
            <button 
              onClick={() => openBrief('summary')} 
              aria-pressed={activeMode === 'summary'}
              style={{ 
                flex: 1, 
                borderRadius: 14, 
                border: activeMode === 'summary' ? `1.5px solid ${t.cyan}` : `1px solid ${t.brd}`, 
                background: activeMode === 'summary' ? (dark ? 'rgba(88,166,255,0.18)' : 'rgba(9,105,218,0.08)') : (dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)'), 
                color: activeMode === 'summary' ? t.cyan : t.tx, 
                padding: '10px 12px', 
                minHeight: '44px', 
                fontSize: 13, 
                fontWeight: 800, 
                cursor: 'pointer', 
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)', 
                whiteSpace: 'nowrap',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8
              }}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
              요점만
            </button>
            <button 
              onClick={() => openBrief('insight')} 
              aria-pressed={activeMode === 'insight'}
              style={{ 
                flex: 1, 
                borderRadius: 14, 
                border: activeMode === 'insight' ? '1.5px solid #A855F7' : `1px solid ${t.brd}`, 
                background: activeMode === 'insight' ? 'rgba(168,85,247,0.18)' : (dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)'), 
                color: activeMode === 'insight' ? '#A855F7' : t.tx, 
                padding: '10px 12px', 
                minHeight: '44px', 
                fontSize: 13, 
                fontWeight: 800, 
                cursor: 'pointer', 
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)', 
                whiteSpace: 'nowrap',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8
              }}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="7.5 4.21 12 6.81 16.5 4.21"/><polyline points="7.5 19.79 7.5 14.6 3 12"/><polyline points="21 12 16.5 14.6 16.5 19.79"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
              왜 중요?
            </button>
          </div>

          <div style={{ display: 'flex', gap: 10, flex: '1 1 100%', justifyContent: 'flex-end' }}>
            {sourceUrl && (
              <button
                onClick={() => window.open(sourceUrl, '_blank', 'noopener,noreferrer')}
                style={{ 
                  flex: 1, 
                  borderRadius: 14, 
                  border: `1.5px solid ${t.brd}`, 
                  background: t.card, 
                  color: t.sub, 
                  padding: '10px 16px', 
                  minHeight: '46px', 
                  fontSize: 13, 
                  fontWeight: 800, 
                  cursor: 'pointer', 
                  whiteSpace: 'nowrap', 
                  textAlign: 'center',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 6
                }}
              >
                원문 보기 ↗
              </button>
            )}
            <button
              onClick={handleSubmit}
              aria-label="이 카드를 배터리 상담소에 제출"
              style={{
                flex: sourceUrl ? 1.8 : 'none',
                width: sourceUrl ? 'auto' : '100%',
                borderRadius: 14,
                border: 'none',
                background: t.cyan,
                color: '#000',
                padding: '12px 18px',
                minHeight: '46px',
                fontSize: 13,
                fontWeight: 900,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                boxShadow: `0 5px 15px ${dark ? 'rgba(88,166,255,0.4)' : 'rgba(9,105,218,0.4)'}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 8,
                transform: 'translateY(-2px)'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>
              상담 접수
            </button>
          </div>
        </div>

        {hasSources && (
          <button
            type="button"
            onClick={() => setShowSources((prev) => !prev)}
            aria-expanded={showSources}
            style={{
              alignSelf: 'flex-start',
              background: 'transparent',
              border: 'none',
              padding: '4px 0',
              color: t.sub,
              fontSize: 11,
              fontWeight: 700,
              cursor: 'pointer',
              fontFamily: "'JetBrains Mono',monospace",
              display: 'flex',
              alignItems: 'center',
              gap: 5,
              letterSpacing: '0.02em',
            }}
          >
            <span style={{ fontSize: 12 }}>{showSources ? '▾' : '▸'}</span>
            <span>📰 다중 출처 {factSources.length}건</span>
          </button>
        )}

        {hasSources && showSources && (
          <div style={{
            marginTop: 4,
            padding: '14px 16px',
            background: dark ? 'rgba(88,166,255,0.04)' : 'rgba(9,105,218,0.025)',
            borderRadius: 12,
            border: `1px solid ${dark ? 'rgba(88,166,255,0.12)' : 'rgba(9,105,218,0.10)'}`,
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
          }}>
            <div style={{
              fontSize: 10,
              color: t.sub,
              fontFamily: "'JetBrains Mono',monospace",
              letterSpacing: '0.04em',
              fontWeight: 700,
              textTransform: 'uppercase',
            }}>
              카드 fact를 받친 원문 인용 — 직접 확인용
            </div>
            {factSources.map((src, i) => {
              const host = (() => {
                try { return new URL(src.source_url).hostname.replace(/^www\./, ''); }
                catch { return src.source_url; }
              })();
              return (
                <div key={i} style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 6,
                  paddingBottom: i < factSources.length - 1 ? 12 : 0,
                  borderBottom: i < factSources.length - 1 ? `1px solid ${dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}` : 'none',
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    flexWrap: 'wrap',
                  }}>
                    <span style={{
                      fontSize: 9,
                      fontWeight: 800,
                      color: t.cyan,
                      background: dark ? 'rgba(88,166,255,0.14)' : 'rgba(45,90,142,0.10)',
                      padding: '2px 7px',
                      borderRadius: 999,
                      fontFamily: "'JetBrains Mono',monospace",
                    }}>
                      {host}
                    </span>
                    {src.fetched_at ? (
                      <span style={{
                        fontSize: 9,
                        color: t.sub,
                        fontFamily: "'JetBrains Mono',monospace",
                      }}>
                        {String(src.fetched_at).slice(0, 10)}
                      </span>
                    ) : null}
                  </div>
                  {src.claim ? (
                    <div style={{
                      fontSize: 12,
                      color: t.tx,
                      lineHeight: 1.55,
                      fontWeight: 600,
                    }}>
                      {src.claim}
                    </div>
                  ) : null}
                  {src.source_quote ? (
                    <div style={{
                      fontSize: 11,
                      color: t.sub,
                      lineHeight: 1.7,
                      paddingLeft: 10,
                      borderLeft: `2px solid ${dark ? 'rgba(88,166,255,0.25)' : 'rgba(9,105,218,0.20)'}`,
                      fontStyle: 'italic',
                      wordBreak: 'keep-all',
                    }}>
                      “{src.source_quote}”
                    </div>
                  ) : null}
                  <a
                    href={src.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      fontSize: 10,
                      color: t.cyan,
                      textDecoration: 'none',
                      fontFamily: "'JetBrains Mono',monospace",
                      alignSelf: 'flex-start',
                      letterSpacing: '0.02em',
                    }}
                  >
                    원문 ↗
                  </a>
                </div>
              );
            })}
          </div>
        )}

        {(thinkingMode || activeMode) && (
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            gap: 14, 
            marginTop: 8, 
            padding: 20, 
            background: dark ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.04)', 
            borderRadius: 18, 
            border: `1.5px solid ${t.brd}`,
            boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.1)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{ position: 'absolute', top: -40, right: -40, width: 100, height: 100, background: briefAccent, filter: 'blur(60px)', opacity: 0.15, pointerEvents: 'none' }} />

            {thinkingMode ? (
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
                <div style={{ position: 'relative', flexShrink: 0 }}>
                  <div style={{ width: 40, height: 40, borderRadius: '50%', background: briefAccent, color: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15, fontWeight: 900 }}>강</div>
                  <div style={{ position: 'absolute', inset: -3, borderRadius: '50%', border: `2px solid ${briefAccent}`, animation: 'spin 2s linear infinite', opacity: 0.5 }} />
                </div>
                <div style={{ flex: 1, background: t.card, borderRadius: '4px 18px 18px 18px', border: `1px solid ${t.brd}`, padding: '16px 20px', color: t.sub, fontSize: 14, lineHeight: 1.6, fontWeight: 500 }}>
                  카드 분석 중입니다...
                </div>
              </div>
            ) : lines.map((line, idx) => (
              <div key={`${activeMode}-${idx}`} style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
                <div style={{ flexShrink: 0, width: 40, height: 40, borderRadius: '50%', background: briefAccent, color: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15, fontWeight: 900, boxShadow: `0 4px 10px ${briefMode === 'summary' ? 'rgba(88,166,255,0.4)' : 'rgba(168,85,247,0.4)'}` }}>강</div>
                <div style={{ flex: 1, background: t.card, borderRadius: '4px 18px 18px 18px', border: `1px solid ${t.brd}`, padding: '16px 20px', color: t.tx, fontSize: 15, lineHeight: 1.75, wordBreak: 'keep-all', boxShadow: '0 4px 8px rgba(0,0,0,0.06)', fontWeight: 500 }}>
                  {line}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}} />
    </div>
  );
}

/**
 * memo wrap — NewsDesk에서 60개 카드가 한 번에 렌더링될 때
 * 부모 re-render 시 불필요한 자식 re-render 방지.
 * props가 같으면 (특히 card·coverImage·dark) skip.
 */
export default memo(StoryNewsItem);

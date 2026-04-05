# Enhanced Red-Team Audit — Current State

## 목적
이 문서는 현재 `SBTL_HUB`의 구현 상태를 **냉정하게 까보고**, 
무엇이 해결되었고 무엇이 아직 미완인지, 그리고 **다음 수정 라운드에서 정확히 무엇을 고쳐야 하는지**를 한 번에 보이도록 정리한 audit 문서다.

이 문서는 단순 칭찬용이 아니다.
기준은 다음과 같다.

- build success 중심 평가 금지
- 실제 배포본 UX 기준
- 버튼 라벨과 실제 동작 일치 여부
- 내부 카드 / 외부 기사 / 분석 레이어 구분 여부
- "덜 망가짐"을 "완료"로 착각하지 않기

---

# 0. 전체 판정
## 결론 한 줄
**회복은 됐지만, 마감은 아니다.**

현재 제품은 예전처럼 노골적으로 망가진 상태는 벗어났다.
하지만 여전히:
- 강한 분석형 intelligence assistant
보다는
- 정리된 규칙 기반 뉴스/카드 보조도구
에 더 가깝다.

즉,
- 방향은 많이 바로잡혔음 ✅
- 아직 완전히 끝난 건 아님 ❌

---

# 1. PASS — 확실히 좋아진 것

## 1.1 별도 Translator 탭 없음
이건 맞다.
예전처럼 번역기를 독립 제품처럼 빼지 않고,
기존 뉴스/AI 흐름 안에서 처리하려는 방향은 옳다.

### 판정
**PASS**

### 왜 맞는가
사용자 니즈는 범용 번역기 사용이 아니라,
**허브 안 외국 뉴스를 이해하는 것**이기 때문이다.

---

## 1.2 Internal / External dual-mode 구조 복구
현재는 다시 다음 두 모드가 공존한다.

- `오늘 핵심 카드` → 내부 카드 기반
- `외부 기사 링크 검색` → Brave 기반 외부 기사

결과에도 source badge가 붙는다.

- `📋 내부 카드 기반`
- `🔗 외부 기사 링크`

### 판정
**PASS**

### 왜 중요한가
우리가 원한 건 Brave 삭제가 아니라,
**내부 카드 조회와 외부 기사 검색을 분리해서 공존**시키는 구조였기 때문이다.

---

## 1.3 웹툰 카드 URL 복구
허브 안 시리즈 메타데이터에 EP.1 / EP.2 / BONUS URL이 명시적으로 들어갔다.
즉 최소한 허브 안 카드 클릭이 `undefined`로 죽는 문제는 정리됐다.

### 판정
**PASS**

### 단서
이건 허브 레벨 링크 복구 기준이다.
실제 HTML 내 next-link 흐름은 배포본에서 별도로 확인해야 한다.

---

## 1.4 Policy Tracker 지역 설명 레이어 추가
이건 좋은 개선이다.
Tracker가 단순 일정판에서 벗어나,
지역 카드 클릭 시 정책 설명 패널을 여는 구조가 들어갔다.

### 판정
**PASS**

### 왜 좋은가
기본 화면은 가볍게 유지하면서,
정책 설명은 on-demand로 여는 구조이기 때문이다.
이건 우리가 원한 방향과 일치한다.

---

## 1.5 region-aware latestCards 개선
예전에는 전체 latest date를 먼저 잡고 region filter를 나중에 해버려서,
`오늘 미국 뉴스 3개` 같은 요청이 어처구니없이 오래된 카드로 밀리는 구조였다.

현재는 region pool 안에서 latest를 계산하는 방향으로 고쳐져 있다.

### 판정
**PASS**

### 왜 중요한가
이건 retrieval 정확도의 핵심이다.
뉴스 제품에서 region/date handling이 틀리면 신뢰도가 바로 깨진다.

---

# 2. PARTIAL — 좋아졌지만 아직 임시방편인 것

## 2.1 `한국어 요약` vs `왜 중요한지`
좋아진 점은 있다.
예전처럼 두 버튼이 완전히 같은 내용은 아니다.

하지만 현재 분리는 아직 **진짜 기능 분리**라기보다,
한정된 필드를 억지로 갈라쓴 heuristic에 가깝다.

현재 인상은 대체로 이렇다.
- `한국어 요약` = title/subtitle + gist 일부 조합
- `왜 중요한지` = gist 뒷부분 분리

### 판정
**PARTIAL**

### 왜 아직 부족한가
우리가 원한 건 아래의 명확한 역할 분리다.

- `한국어 요약` = 기사 내용 중심의 한국어 렌더링
- `왜 중요한지` = relevance gate / implication layer
- `AI 해설` = 더 깊은 on-demand 분석

즉 지금은 **같은 재료를 잘라서 다르게 보이게 한 수준**이고,
아직 **다른 기능 제품**으로 분리된 건 아니다.

### 다음 라운드에서 고칠 것
- `왜 중요한지`는 전략적 의미 중심으로 고정
- `한국어 요약`은 기사형 요약으로 고정
- `AI 해설`은 별도 분석 prompt 결과로 분리

---

## 2.2 챗봇 문맥 저장은 생겼지만, 문맥 활용은 약함
현재는 다음 정도를 기억하려는 구조가 있다.
- qType
- region
- date
- cards
- links
- query

이건 좋은 시작이다.

하지만 실제로 강한 문맥형 대화가 되려면,
아래 같은 후속 질의를 robust하게 받아야 한다.

- `첫 번째 링크 다시 보여줘`
- `방금 그 기사만 번역해줘`
- `직전 외부 기사 기준으로 왜 중요한지 말해줘`
- `이 카드랑 관련된 미국 기사 더 찾아줘`

### 판정
**PARTIAL**

### 왜 아직 부족한가
문맥을 저장하는 것과,
그 문맥을 **객체 수준으로 해석해 후속 행동으로 연결하는 것**은 다르다.

현재는 전자는 조금 있고, 후자는 아직 약하다.

### 다음 라운드에서 고칠 것
- `first / second / previous / that article` 같은 지시어 처리
- lastContext 안에서 selected object 개념 추가
- 직전 external result / internal card를 구분 저장

---

## 2.3 최신성은 좋아졌지만 general search recency discipline은 미완
`latestCards()`는 많이 좋아졌다.
하지만 `searchCards()`는 여전히 relevance 위주다.

즉,
- region/date-specific news routing은 개선됨
- general search는 여전히 키워드 score에 치우칠 수 있음

### 판정
**PARTIAL**

### 왜 문제인가
뉴스 허브에서 generic query조차 최신성 감각이 약하면,
사용자는 또 “왜 자꾸 예전 카드가 떠?”라고 느낄 수 있다.

### 다음 라운드에서 고칠 것
- `searchCards()`에 recency tie-break 추가
- score 동률 또는 유사 score 시 최신 날짜 우선

---

# 3. FAIL — 아직 핵심적으로 안 된 것

## 3.1 고도화된 analysis prompt 실제 통합 안 됨
이게 가장 큰 미완이다.

현재 시스템은 여전히 대체로 아래 조합이다.
- intent classification
- deterministic retrieval
- hard-coded formatting
- field recombination

즉 지금은:
- 검색형/라우팅형 assistant
에 가깝지,
- 진짜 on-demand analysis layer
가 붙은 제품은 아니다.

### 판정
**FAIL**

### 왜 중요한가
우리가 여러 번 정리한 핵심은 이것이었다.

#### Retrieval layer
- cards
- tracker
- Brave links
- selected content object
- metadata

#### Analysis layer
사용자가 명시적으로 요청할 때만 실행
- `왜 중요한지`
- `AI 해설`
- `한국어 요약`
- region policy explanation

이 분리가 아직 실제 구현에서 명확히 보이지 않는다.

### 다음 라운드에서 고칠 것
- `api/analysis.js` 같은 전용 route 또는 equivalent layer 추가
- 입력: content object + metadata
- 출력: relevance gate / summary / implication / analyst note
- 기본 카드에는 상시 붙이지 말고 on-demand만 실행

---

## 3.2 Brave 운영 에러 처리 약함
현재 dual-mode는 복구되었지만,
Brave가 죽었을 때의 운영 UX는 여전히 약하다.

### 문제
Brave API가 다음을 반환해도
- 401
- 403
- 429
- provider error payload

현재 구조에선 사용자/운영자가 정확한 실패 원인을 알기 어렵다.

즉 사용자는 여전히 이렇게 느낄 수 있다.
- "Brave가 또 안 되는 것 같은데?"

### 판정
**FAIL**

### 다음 라운드에서 고칠 것
- server에서 `response.ok` 체크
- status-aware error payload 반환
- frontend에서 no-result / auth-failure / rate-limit / config-error 구분
- 실패 이유를 조용히 삼키지 않기

---

## 3.3 Policy UI는 좋아졌지만 ChatBot policy intelligence는 아직 약함
Tracker UI 쪽 지역 설명은 좋아졌다.
하지만 챗봇이 정책 질문을 받았을 때는 여전히 얕다.

현재 중심은 대체로:
- 일정 리스트
- 관련 카드
정도다.

하지만 사용자가 진짜 원하는 질문은 이런 거다.
- `미국 정책 설명해줘`
- `EU 정책 구조를 쉽게 설명해줘`
- `한국 ESS 정책에서 지금 봐야 할 포인트는 뭐야?`

이 질문에는 단순 일정/카드보다,
- 정책 개요
- 왜 중요한지
- watchpoint
- 관련 카드/링크
가 함께 나와야 한다.

### 판정
**FAIL**

### 다음 라운드에서 고칠 것
- Tracker의 `REGION_POLICY` 로직 일부를 ChatBot에도 재사용
- region policy 질문 시 overview + why + watchpoints + cards 출력

---

# 4. 항목별 최종 판정표

## PASS
- separate Translator tab 없음
- internal/external dual-mode 복구
- source badge 복구
- 웹툰 카드 URL 복구
- Policy Tracker 지역 설명 패널 추가
- region-aware latestCards 개선

## PARTIAL
- `한국어 요약` vs `왜 중요한지` 분리됐지만 heuristic 수준
- 챗봇 문맥 저장은 있으나 객체 수준 후속 대화는 약함
- general search recency discipline 미완

## FAIL
- enhanced analysis prompt 실제 통합 안 됨
- Brave 운영 에러 처리 약함
- ChatBot policy intelligence 약함

---

# 5. 우선순위별 수정 라운드

## P0 — 다음 라운드에서 반드시 고칠 것
### 1) 진짜 on-demand analysis layer 구현
대상:
- `왜 중요한지`
- `AI 해설`
- `한국어 요약`
- 지역 정책 설명 패널

### 2) Brave 에러 처리 강화
- `response.ok` 체크
- status-aware 에러 반환
- frontend에서 실패 유형 구분

### 3) `왜 중요한지` / `한국어 요약` / `AI 해설` 기능 분리 강화
서로 다른 콘텐츠 제품으로 만들어야 함.

---

## P1 — 곧이어 고칠 것
### 4) `searchCards()` recency tie-break 추가

### 5) 객체 수준 후속 질의 강화
예:
- 첫 번째 링크
- 방금 기사
- 그 카드
- 직전 external result

### 6) 챗봇 policy 설명 강화
Tracker UI의 지역정책 설명 로직을 챗봇 응답에도 반영

---

# 6. 최종 harsh conclusion
예전보다 좋아진 건 맞다.
하지만 **좋아졌다고 끝난 건 아니다.**

현재 상태를 미화하면 안 된다.
정확한 평가는 이거다.

- 제품은 더 이상 노골적으로 망가져 있지 않다
- 하지만 아직 진짜 분석형 제품도 아니다
- 지금은 잘 정돈된 규칙형 뉴스 assistant에 가깝다

즉,
**good recovery, incomplete finish.**

이 상태를 "완료"로 사인오프하면 안 된다.
다음 라운드가 반드시 더 필요하다.

# Future Card Standard — Full Schema Locked

이 문서는 **앞으로 생성될 카드**에 대한 고정 기준이다.
과거 legacy compact 구조 설명이 아니라, 신규 카드 생성·검수·병합의 기준만 잠근다.

---

## 1. 신규 카드 표준

앞으로의 신규 카드는 **full schema only** 로 본다.

```json
{
  "id": "...",
  "region": "KR|US|CN|JP|EU|GL",
  "date": "YYYY-MM-DD",
  "cat": "...",
  "signal": "top|high|mid",
  "title": "...",
  "sub": "...",
  "gate": "...",
  "fact": "...",
  "implication": ["...", "..."],
  "urls": ["..."]
}
```

신규 payload에서는 compact legacy 필드(`s / r / d / T / g`)를 사용하지 않는다.

---

## 2. 필드 작성 기준

### title
- 한 줄만 읽어도 구조적 의미가 보여야 함
- 단순 기사 제목 복붙 금지
- 해석은 가능하지만 과장 금지

### sub
- 사건 요약
- 누가 / 무엇을 / 어느 정도 규모로 했는지
- 본문을 대신하지 말고 핵심 사건만 짧게 정리

### gate
- 왜 지금 중요한지 한 문장으로 설명
- 공급망 / 정책 / 수익성 / 경쟁구도 / 자본시장 관점의 의미를 분명히 써야 함
- 기사 요약 반복 금지

### fact
- 핵심 근거와 사실관계를 2~4문장으로 정리
- 숫자, 일정, 주체, 자산, 정책 변화 등 검증 가능한 근거를 우선 반영
- 근거가 약하면 과장하지 말고 정보 경계를 분명히 표시

### implication
- 전략적 의미 / 관전 포인트를 bullet array로 정리
- 누가 수혜/노출되는지, 무엇을 더 봐야 하는지, 어떤 구조 변화가 시작되는지 설명
- fact 반복 금지

### signal
- top: 정말 상단에 올릴 톱 시그널
- high: 높은 중요도
- mid: 의미는 있으나 톱은 아님

---

## 3. Region Label Rule — Locked

region은 기사 출처 국가가 아니라 **사건의 직접 무대**로 붙인다.

- KR / US / CN / JP는 해당 국가가 직접 무대일 때만 사용한다.
- 유럽 개별 국가 사건과 EU 제도 뉴스는 EU로 묶는다.
- 두 개 이상 국가가 동등하게 핵심이면 GL로 처리한다.
- 현재 배지 체계 밖 국가(예: 캐나다, 호주, 인도네시아, 중동 국가 등)는 GL로 처리한다.
- 애매하면 GL로 붙인다.

절대 하지 말 것:
- 출처 국가로 region 붙이기
- 기사에 등장한 기업 국적으로 region 붙이기

---

## 4. Prompt 운영 원칙

### Prompt A
- discard / merge 결정이 가능한 유일한 단계
- spec_id / region / representative_date / representative_source / category / signal / strategic_lens / urls / why_now / market_relevance를 결정
- region은 반드시 locked rule 적용

### Prompt B
- passed spec를 받아 카드 문안 작성
- drop / merge / category 변경 / signal 변경 금지

### Prompt C
- 최종 red-team review 및 formatter
- 최종 production output은 **full schema only**
- compact legacy 필드로 다시 직렬화하지 않음
- `gate`, `fact`, `implication`을 하나의 gist-like field로 붕괴시키지 않음

---

## 5. Workflow 운영 원칙

- triage raw를 바로 merge 하지 않는다.
- safe payload는 편집이 끝난 카드만 담는다.
- 한 번에 너무 많이 넣지 않는다.
- 논쟁성 카드 / 중복 의심 카드는 소량 batch로 나눈다.
- 최신 main 기준에서만 병합한다.
- 배포 확인은 main + production 기준으로 본다.

---

## 6. 실전 체크리스트

### merge 전
- [ ] payload가 full schema 기준인가
- [ ] 기존 cards와 의미 중복 없는가
- [ ] nav/landing/PR 제거됐는가
- [ ] date / gate / fact / implication / urls가 비어 있지 않은가

### merge 후
- [ ] JSON 파싱 성공
- [ ] total 예상치 일치
- [ ] 신규 카드 실제 존재
- [ ] 기존 핵심 카드 손실 없음
- [ ] 앱에서 숫자 반영 확인

### deploy 후
- [ ] GitHub main 숫자 확인
- [ ] Vercel success 확인
- [ ] production 화면 확인
- [ ] 캐시 이슈 여부 확인

---

## 7. 최종 원칙

**앞으로 생성되는 카드는 full schema 기준으로만 작성·검수·병합한다.**
legacy compact 사고는 신규 카드 운영 기준에서 제거한다.
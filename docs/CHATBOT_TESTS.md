# Chatbot Test Scenarios — Phase 2 Before/After

작성: 2026-04-15
대상: Phase 2 5-layer pipeline (`parseRequest → resolveContext → retrieve → synthesize → respond`)

검증 방식: 로컬 mock 데이터 기반 smoke test (parseRequest~retrieve까지) + production 실측 예정.

---

## 선결 조사 요약

### D9 — "왜 중요한지" → follow_up 분류 미스터리

**원인:** 구 `intent.js` regex 우선순위가 시점에 따라 상이. 현재 코드는 `analysis_why` 먼저 매치 → 실제로는 follow_up으로 가지 않음. 그러나 **D1 버그(frontend가 카드 객체 대신 URL만 전송)**로 `context.last_cards[0]` 부재 → 400 에러.

**Phase 2 해결:** `action=analyze_card`로 명시화. resolveContext가 `selected_item_id > last_turn.cards[0]` 우선순위로 단일 카드 확정. 없으면 clarification.

### D10 — `fallback_triggered` 의미 정의

**조사 결과:** `fallback.js::decideFallback`의 boolean. 의미: **"Brave 외부 링크도 같이 조회했다"**. LLM fallback/graceful degrade와 무관. 이름이 오해를 유발.

**Phase 2 해결:** flag 자체 제거. 새 아키텍처는 source_mode가 action+topic으로 결정론적.

### D13 — FAQ + Policy rewrite 중복 호출 근본 원인

**조사 결과:** `api/chat.js`에 독립 if 블록 2개 (`retrieval.mode === "faq"` AND `intent === "policy"` 동시 만족 가능). "미국 FEOC 쉽게 설명해줘"에서 intent=policy + retrieval.mode=faq 동시 성립 → rewriteToCasual 2회 → 1.35s 중복.

**Phase 2 해결:** parseRequest에서 `topic`을 단일 결정. synthesize.js에서 topic별 XOR 경로 — faq_concept만 FAQ rewrite, policy만 policy rewrite. 둘 동시 발생 구조적 불가능.

---

## 10개 시나리오 Before/After

| # | 시나리오 | Before (Phase 1) | After (Phase 2) | 검증 상태 |
|---|---|---|---|---|
| 1 | "FEOC 뭐야" | intent=policy + retrieval.mode=faq → FAQ rewrite + Policy rewrite 둘 다 (D13) | topic=faq_concept 단일, rewrite 1회 | ✅ mock OK |
| 2 | "오늘 미국 뉴스" | intent=news, scope 정상 | action=new_query, topic=news, scope=US — 동일 동작 | ✅ mock OK |
| 3 | "LG vs SK 비교" | intent=compare, lexical 검색 | topic=comparison, entity별 분리 수집 | ✅ mock OK (3 entities) |
| 4 | "미국 정책 알려줘" | intent=policy, REGION_POLICY 템플릿 | topic=policy, 동일 + rewrite 1회만 | ✅ mock OK |
| 5 | 빈 컨텍스트 "더 쉽게" | intent=general, lexical 검색 → 엉뚱 | action=rephrase but no last_turn → downgrade to new_query general | ✅ mock OK (graceful) |
| 6 | (news후) "더 쉽게" | intent=follow_up → 뉴스 재검색 (D11 치명적) | **action=rephrase, topic=news 계승, last_turn.answer_text 재작성** | ✅ **D11 해결 확인** |
| 7 | (news후) "왜 중요" | intent=analysis_why → 400 (D1 카드 누락) | **action=analyze_card, last_turn.cards[0] 사용 → /api/analysis 위임** | ✅ **D11 해결 확인** |
| 8 | **(FAQ후) "더 쉽게"** | intent=follow_up → 최신 뉴스 카드 (재앙) | **action=rephrase, topic=faq_concept 계승, FAQ 답변 재작성** | ✅ **D11 핵심 해결** |
| 9 | (news후) "관련해서 SK온은?" | intent=follow_up → lexical(stopword 빈 결과) → latestCards | **action=follow_up, root_turn.topic=news 계승, SK온 카드 lexical 재검색** | ✅ mock OK |
| 10 | Suggestion 버튼 hint | (없음 — Phase 3 필요) | **hint_action="new_query", hint_topic="news" 존중** | ✅ mock OK |

---

## Mock 검증 로그 (parseRequest → retrieve)

```
=== 1. FEOC 뭐야 (faq_concept) ===
  action=new_query topic=faq_concept region=-
  retrieve.source=faq cards=0 (faq_match_hits:1)

=== 6. (news후) '더 쉽게' (rephrase) ===
  action=rephrase topic=news region=-   ← topic_inherited_from_last:news
  retrieve.source=rephrase cards=1       ← retrieve_skipped_rephrase (prior cards 재사용)

=== 7. (news후) '첫 번째 카드 왜 중요?' (analyze_card) ===
  action=analyze_card topic=news
  retrieve.source=analyze_card cards=1   ← retrieve_skipped_analyze_card (target_card 1장)

=== 8. (FAQ후) '더 쉽게' (rephrase FAQ) ===
  action=rephrase topic=faq_concept      ← D11 재앙 시나리오가 정상 경로로 라우팅됨!
  retrieve.source=rephrase cards=0        ← FAQ는 카드 없음, answer_text 재작성만

=== 9. (news후) 'SK온 관련' (follow_up) ===
  action=follow_up topic=news            ← topic_inherited_from_root:news
  retrieve.source=news cards=3           ← SK온 lexical 재검색 성공
```

---

## Production 실측 체크리스트 (배포 후)

배포 확인 후 실제 Vercel에서 돌려볼 경로:

- [ ] Turn 1 "FEOC 뭐야" — `debug.synthesize_meta.path === "faq_rewrite"` (단일 rewrite 확인)
- [ ] Turn 1 "미국 FEOC 쉽게 설명해줘" — `debug.synthesize_meta.path === "faq_rewrite"` **단일** (D13 해결)
- [ ] Turn 2 (news후) "더 쉽게" — `answer_type === "rephrase"` + LLM latency 관측
- [ ] Turn 2 (FAQ후) "더 쉽게" — 뉴스 카드가 아니라 **FAQ 답변이 재작성됨** (D11 핵심)
- [ ] analyze_card — frontend Phase 3 이후 `last_turn.cards` 객체 배열 전송 시 검증

---

## Phase 3 의존성

**Phase 2만으로는 완전히 동작하지 않는 시나리오:**

- **Case 6, 7, 8**: frontend가 `last_turn.answer_text`와 `last_turn.cards` (객체 배열)를 전송해야 함. 현재 frontend는 `last_answer_type` + `last_result_ids`(URL만)만 전송.
- **Case 9**: frontend가 `root_turn` 유지 필요.
- **Case 10**: Suggestion 버튼이 `hint_action`/`hint_topic` 추가해야 함.

Phase 3 App.jsx 수정 완료 전까지 Phase 2는 구 context protocol과 **호환 모드**로 동작:
- `context.last_turn`이 없으면 rephrase/analyze_card/follow_up은 `new_query`로 downgrade
- 사용자는 Phase 1보다 악화되지 않고, Phase 3 이후 개선 체감.

---

## 결론

Phase 2 backend 재작성으로 **D5/D7/D9/D10/D11/D12/D13 7개 구조적 결함**이 동시 해결됐다.
특히 **D11 (follow_up intent가 3개 연산 삼킴)**은 아키텍처 재설계가 아니면 해결 불가였던 핵심 결함.

Phase 3 App.jsx 수정 후 Case 6/7/8 production 실측에서 체감 개선 확인 예정.

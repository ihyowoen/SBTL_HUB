# SBTL 카드 운영 WF vFinal

## 목적
이 문서는 SBTL 카드 추가/수정/검수 작업의 최종 운영 흐름을 고정하기 위한 기준 문서다.
목표는 다음과 같다.

- triage 결과를 맹신하지 않고 사람 검수 기준을 명확히 유지
- `cards.json` 기준본 혼선을 제거
- payload 생성과 GitHub 실행을 분리하여 오염을 줄임
- merge 전후 로컬 정리까지 포함한 반복 가능한 운영 루틴을 고정

---

## 핵심 운영 원칙

- **Current cards baseline = GitHub `main` only**
- 업로드된 `cards.json` 파일은 기준본으로 사용하지 않음
- cards 관련 모든 판단은 항상 GitHub `main`의 `public/data/cards.json`과 비교
- 파이프라인 결과는 시작점일 뿐, 최종 판정은 사람이 수행
- payload는 검증 완료 후에만 생성
- GitHub 반영 전에는 반드시 `diff`와 `total count`를 확인

현재 GitHub `main`의 `public/data/cards.json` 기준본은 `updated: 2026-04-06`, `total: 298`로 확인된다. 참조 시에는 항상 최신 `main`을 다시 확인한다. fileciteturn131file0

---

## 전체 흐름

1. 새 triage 입력 잠금
2. GitHub `main`의 `public/data/cards.json` 최신본 확인
3. A/B/C + enhanced red team audit line by line
4. GitHub `main` cards.json 기준 semantic dedupe / merge / strengthen review
5. ADD 확정 카드만 payload generate
6. 로컬 merge → diff → total count 검증
7. Copilot용 PR/merge prompt 작성 및 GitHub 실행
8. merge 후 local cleanup

---

## 0. 입력 잠금

### 입력 파일
- `triage_output_*.json`
- `review_candidates_*.json` (있을 경우 보조 입력)
- GitHub `main`의 `public/data/cards.json`

### 원칙
- 이번 라운드의 유일한 입력 파일 세트를 먼저 잠근다.
- `review_candidates`는 **rescue 전용 보조 입력**으로만 사용한다.
- cards 관련 기준본은 항상 GitHub `main`이다.
- 태그, keyword score, gate 결과는 참고만 하고 절대 기준으로 사용하지 않는다.

---

## 1. A/B/C + enhanced red team audit

이 단계에서는 triage를 **line by line**로 다시 검토한다.
아직 payload는 만들지 않는다.

### 검토 항목
- 제목
- snippet / summary
- 원문 URL
- 기사 날짜
- source 성격
- 산업 직접성
- 카드화 적합성
- merge-safe 여부

### A. 직접성
배터리 / ESS / 소재 / 충전 / 정책 / 공급망에 **직접 연결**되는가.

### B. 카드 적합성
카드로 만들 만큼 아래 중 하나 이상이 살아 있는가.
- 실행 이벤트
- 숫자 / 규모 / 용량
- 정책 변화
- 공급망 구조 의미
- 산업 전략 시사점

### C. merge-safe
아래 조건을 충족하는가.
- 날짜 이상 없음
- 랜딩 / 허브 / 백과 / 방법론 페이지 아님
- 과도한 홍보성 아님
- 기존 cards와 충돌 / 중복 위험 낮음
- 원문 URL이 명확함

### Hard-stop
아래 하나라도 걸리면 즉시 `DROP`.
- 원문 날짜 이상
- 재인용 / 시의성 문제
- 랜딩 / 허브 / 백과 / 방법론 페이지
- 원문 URL 불명확
- 기존 cards.json과 사실상 동일 이벤트
- 제목은 세지만 본문이 약함

### 판정 결과
이 단계의 산출물은 아래 3개만 허용.
- `ADD`
- `HOLD`
- `DROP`

---

## 2. GitHub `main` cards.json 기준 dedupe / merge / strengthen review

이 단계에서는 triage 통과 후보를 GitHub `main` 기준 cards와 대조한다.
질문은 하나다.

**이 이벤트를 새 카드로 넣는가, 기존 카드에 흡수하는가, 아니면 버리는가?**

### 확인 항목
- 동일 URL 중복
- 같은 이벤트의 다른 기사
- support article 여부
- 기존 카드 보강 가능성
- merge 카드로 묶는 것이 더 적절한지
- 제목만 다르고 사실상 같은 이벤트인지

### 판정 결과
- `NEW_CARD`
- `MERGE_INTO_EXISTING`
- `DROP`

### 명칭 원칙
이 단계는 단순 duplicate check가 아니라:

**semantic dedupe / merge / strengthen review**

로 이해한다.

---

## 3. Payload generation

이제서야 payload를 생성한다.

### 생성 원칙
- `ADD` 또는 `NEW_CARD` 확정분만 payload 생성
- raw URL 없는 카드 생성 금지
- `HOLD` 상태는 생성 금지
- support article 여러 개면 merge 카드 허용
- payload는 가능하면 **작은 batch**로 유지
- 날짜 / 원문 / 중복 문제가 남아 있으면 생성 금지

### 금지 사항
- guessed URL 사용 금지
- memory 기반 카드 문구 재구성 금지
- dedupe review 전에 카드 생성 금지

### 산출물
- `merge_cards.py` 호환 raw payload
- payload 안에는 확정 카드만 포함

---

## 4. 로컬 반영

### 실행 순서
1. 로컬 repo 최신화
2. backup 생성
3. `merge_cards.py` 실행
4. `git diff -- public/data/cards.json` 확인
5. total count 확인
6. 이상 없을 때만 다음 단계 진행

### 확인 포인트
- 예상한 카드만 반영되었는가
- total count가 맞는가
- 기존 카드가 의도치 않게 손상되지 않았는가

### 원칙
이 단계에서 조금이라도 이상하면 **push 금지**.

---

## 5. GitHub 실행

### 실행 원칙
- 새 branch 생성
- 원칙적으로 `public/data/cards.json`만 커밋
- PR 생성
- PR 본문에 아래를 반드시 기록

### PR 본문 필수 항목
- added cards
- merged cards
- dropped / skipped cards
- why
- final total count

### 주의
- GitHub 실행은 **approved payload / approved diff** 기반으로만 진행
- local state가 검증되기 전에는 PR 생성 금지

---

## 6. Copilot용 실행 프롬프트 규칙

Copilot에게는 아래 문구를 항상 포함한다.

- do not guess URLs
- do not regenerate card text from memory
- do not create cards before dedupe review
- only use approved payload / approved cards.json diff
- create PR only after actual local state is confirmed

### 목적
Copilot이
- 임의 재구성
- guessed source 사용
- summary 기반 카드 생성
- 검증 전 PR 생성
을 하지 못하도록 강제한다.

---

## 7. Post-merge local cleanup

merge 후 로컬 정리는 **필수**다.
다음 세션 혼선을 막기 위해 반드시 수행한다.

### 정리 항목
- `git switch main`
- `git pull`
- payload helper json 삭제
- `Zone.Identifier` 삭제
- backup 파일 삭제
- `git status` clean 확인

### 예시 명령어
```bash
git switch main
git pull
rm -f *.Zone.Identifier
rm -f merge_cards_raw_payload*.json
rm -f ~/cards.json.before_*.backup
git status
```

마지막 `git status`가 clean이어야 다음 세션 시작 준비가 끝난다.

---

## 운영 중 자주 발생하는 실수

### 1. 업로드한 cards 파일을 기준본으로 착각
해결:
- 항상 GitHub `main`의 `public/data/cards.json`만 기준으로 사용

### 2. triage tag/gate를 최종 판정처럼 사용
해결:
- 파이프라인 결과는 참고값일 뿐, line by line 재검토 필수

### 3. dedupe review 전에 payload 생성
해결:
- payload 생성 전 `semantic dedupe / merge / strengthen review`를 반드시 먼저 수행

### 4. 날짜가 애매한 기사 강행 추가
해결:
- recency / reprint / stale risk가 있으면 `DROP` 또는 `HOLD`

### 5. merge 후 로컬 정리 누락
해결:
- cleanup을 WF 마지막 고정 단계로 넣고 반드시 수행

---

## 세션 시작용 한 줄 요약

새 triage를 기준으로 A/B/C + enhanced red team audit를 하고, GitHub `main` `public/data/cards.json`을 기준본으로 semantic dedupe / merge review 후, 확정 카드만 payload 생성 → 로컬 diff 검증 → PR 생성 → merge 후 local cleanup까지 진행한다.

# CARD_WORKFLOW_VFINAL Addendum — 2026-04-07

이 문서는 `docs/CARD_WORKFLOW_VFINAL.md`의 보완 규칙을 추가로 잠그기 위한 addendum이다.
기존 본문을 대체하지 않고, 운영 중 새로 확정된 정책을 명시한다.

---

## 1. Helper payload policy

### 핵심 원칙
- helper payload json은 **작업용 산출물**이다.
- helper payload json은 **cards 기준본이 아니다**.
- 최종 기준본은 항상 GitHub `main`의 `public/data/cards.json`이다.

### 운영 표준
- 기본값: helper payload는 repo 영구 보관 대상이 아님
- 예외: 실행 편의상 repo에 일시적으로 둘 수 있음
- 원칙: cards 반영이 끝나면 삭제 또는 정리 여부를 결정

### 금지
- helper payload를 다음 라운드의 기준본처럼 사용
- payload 파일만 보고 현재 cards 상태를 판단
- payload 파일이 repo에 있다는 이유로 `cards.json`보다 더 신뢰

---

## 2. Execution role split

### Assistant
- triage 검토
- A/B/C 판정
- enhanced red team audit
- semantic dedupe / merge / strengthen 판단
- payload 설계
- Copilot / Claude용 실행 문구 작성

### Copilot / Claude (GitHub web)
- branch / PR / merge 보조
- GitHub 상 파일 확인
- PR 본문 정리
- **로컬 파일 삭제 / 이동 / cleanup 직접 수행은 불가**

### Copilot / Claude (local workspace / VS Code / CLI)
- local merge 보조
- backup 생성 보조
- helper payload 정리
- `Zone.Identifier` 삭제
- `git switch main` / `git pull` / `git status` 정리 보조

### GitHub `main`
- cards 기준본
- 최종 운영 기준 상태

---

## 3. Cleanup guardrails

### 실행 전제
- `public/data/cards.json`이 main에 반영되기 전에는 helper payload 삭제 금지
- merge 전 cleanup 금지
- cleanup은 merge 이후에만 수행

### cleanup 후 필수 보고
- 삭제한 payload 파일 목록
- 삭제한 backup 파일 목록
- `git status` 결과

### 권장 명령어
```bash
git switch main
git pull
rm -f *.Zone.Identifier
rm -f merge_cards_raw_payload*.json
rm -f ~/cards.json.before_*.backup
git status
```

---

## 4. 운영 해석 원칙

- payload가 repo에 있어도 기준본은 아니다
- repo root에 helper 파일이 있어도, 운영 판단은 항상 `main` cards.json 기준
- GitHub web Copilot과 local workspace Copilot/Claude는 역할이 다르다
- cleanup은 '정리'이지 '증거 인멸'이 아니다. 삭제 전후 상태를 항상 명확히 남긴다.

---

## 5. 세션용 짧은 기억 문구

- 기준본 = GitHub `main` cards.json
- payload = 작업용 산출물
- GitHub web Copilot = PR/merge 보조
- local Claude/Copilot = cleanup 가능

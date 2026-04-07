# OPERATIONS Addendum — Card Execution & Copilot Prompts (2026-04-07)

이 문서는 `docs/OPERATIONS.md`의 보완 실행 규칙이다.
특히 아래 3가지를 명확히 하기 위해 작성한다.

- helper payload 운영 방식
- GitHub web / local workspace 실행 역할 분리
- Copilot / Claude에게 실제로 어떤 문구를 넣어야 하는지

---

## 1. 실행 역할 구분

### GitHub web Copilot / Claude
할 수 있는 것:
- branch / PR / merge 보조
- GitHub 파일 상태 확인
- PR body 정리

못 하는 것:
- 로컬 파일 삭제
- 로컬 payload 이동
- 로컬 backup 삭제
- `git switch main`, `git pull`, `rm`, `git status` 직접 실행

### Local workspace Copilot / Claude (VS Code / CLI)
할 수 있는 것:
- `merge_cards.py` 실행 보조
- payload 파일 정리
- backup 삭제
- `Zone.Identifier` 삭제
- `git switch main`, `git pull`, `git status` 실행 보조

---

## 2. Helper payload 운영 원칙

- helper payload는 작업용 파일이다
- helper payload는 cards 기준본이 아니다
- 기준본은 항상 GitHub `main`의 `public/data/cards.json`
- helper payload는 작업 완료 후 정리하는 것이 기본 운영 표준

### 실무 판단
- 이번 라운드 작업 중에는 repo에 잠시 둘 수 있음
- 그러나 장기적으로는 repo root에 쌓이지 않게 관리하는 것이 더 좋음
- 최종 반영 판단은 항상 `cards.json` diff와 total count 기준으로 한다

---

## 3. Copilot / Claude에 넣는 문구 템플릿

아래는 상황별로 그대로 붙여넣을 수 있는 실행 문구다.

### A. 카드 PR 생성용
```text
Use the approved payload only.

Rules:
- do not guess URLs
- do not regenerate card text from memory
- do not add HOLD or DROP items
- use GitHub `main` `public/data/cards.json` as the baseline
- only use the approved payload / approved cards.json diff

GitHub task:
1. create a new branch for this card addition
2. commit only `public/data/cards.json`
3. open a PR against `main`
4. include added / held / dropped items clearly in the PR body
5. tell me the branch name, PR URL, and final total count
```

### B. 로컬 cleanup용
```text
Use the current local repo and clean up helper files after the cards PR is safely merged.

Cleanup rules:
- keep only the final repo state needed for operation
- remove temporary payload helper json files
- remove `*.Zone.Identifier`
- remove temporary backup files like `~/cards.json.before_*`
- switch back to `main`
- pull latest `main`
- confirm `git status` is clean

Important:
- do not delete real source files used by the app
- do not touch `public/data/cards.json` if it is not already merged
- tell me exactly what was deleted
```

### C. helper payload를 repo에서 정리할 때
```text
The cards work is already merged.
Please clean up helper payload artifacts now.

Do this:
1. remove temporary payload helper json files
2. remove `*.Zone.Identifier`
3. remove temporary backup files
4. switch to `main`
5. pull latest `main`
6. report deleted files and final `git status`

Do not delete app source files.
Do not touch `public/data/cards.json` unless it is already merged and clean.
```

---

## 4. 로컬 명령어 예시

### cards 반영 후 cleanup
```bash
git switch main
git pull
rm -f *.Zone.Identifier
rm -f merge_cards_raw_payload*.json
rm -f ~/cards.json.before_*.backup
git status
```

### 작업 전 상태 확인
```bash
git branch --show-current
git status
git pull
```

### cards 반영 전 검증
```bash
python merge_cards.py <payload.json>
git diff -- public/data/cards.json
```

---

## 5. 운영상 guardrail

- GitHub web Copilot에게 로컬 cleanup을 기대하면 안 된다
- cleanup은 반드시 merge 이후에만 수행한다
- `public/data/cards.json`이 아직 main에 반영되지 않았다면 helper 삭제 금지
- helper payload가 repo에 남아 있어도 기준본처럼 취급 금지

---

## 6. 짧은 운영 기억 문구

- 기준본 = GitHub `main` cards.json
- payload = 작업용 파일
- GitHub web Copilot = PR/merge 보조
- local Claude/Copilot = cleanup 가능

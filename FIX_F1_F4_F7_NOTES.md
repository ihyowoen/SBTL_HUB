# F1~F4 + F7 Applied — 2026-04-14

이 commit이 적용한 것과 남은 것.

## ✅ Applied in this commit

### F1. `.gitignore` 확장
- `.env`, `.env.local`, `.env.*.local` 추가 (secret leak 방어)
- `*.Zone.Identifier` (Windows 다운로드 메타)
- `~*.backup`, `~*.before_*` (merge_cards.py 백업 패턴)

### F2. `.env.example` 신설
- 기존 `env.example` 파일은 repo에 실존하지 않았음 (이전 audit의 혼선)
- `BRAVE_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` 3종 템플릿 제공
- `VITE_` prefix 금지 경고 명시

### F3. `vercel.json` dead route 제거
- `/api/brave`, `/api/claude`, `/api/translate` 3개 자체 매핑 rewrite 삭제
- `/api/claude`는 실파일 없었음 (dead)
- `/api/translate`는 파일은 있으나 미호출 (dead feature — 차후 삭제 검토)
- SPA fallback rewrite만 유지

## ⚠️ Requires manual action (Claude 못 함)

### F7. `merge_cards_raw_payload_20260407_safe_2cards.json` 삭제
- 내용 검토 완료: Electra + Neoen 2개 카드, 이미 cards.json에 merge됨
- 민감 정보 없음 — 안전하게 삭제 가능
- **GitHub MCP는 파일 삭제 기능 없음.** 로컬에서 실행:
  ```bash
  git rm merge_cards_raw_payload_20260407_safe_2cards.json
  git commit -m "chore: remove stale helper payload (OPERATIONS addendum §1 compliance)"
  git push
  ```

### `download` 파일 삭제 (#36)
- 34바이트, .gitignore 템플릿 오인 저장분
- 같은 이유로 Claude가 직접 삭제 불가:
  ```bash
  git rm download
  git commit -m "chore: remove misnamed 'download' artifact"
  git push
  ```

## 🔜 Next (별도 commit 권장)

### F4. `tracker_data.json` URL 오타 — 대용량 파일 (82KB, 50 items)
- `english.motir.go.kr` → `english.motie.go.kr`
- `www.thelec.net` → `www.thelec.kr`
- 두 줄짜리 변경이지만 전체 JSON 재업로드 필요
- 다음 tracker 업데이트 사이클에 함께 묶는 것 권장 (토큰 효율)

### F5. `src/App.jsx` NewsDesk c.k 포함 — 대용량 파일 (~75KB)
- 5줄 패치지만 전체 파일 재업로드 필요
- App.jsx 리팩터 시점에 함께 처리 권장
- 또는 로컬 str_replace 후 commit (사용자 작업)

### F6. `cards.json` 편집 정리 — 초대용량 (237KB, 337 cards)
- Jackery 카드 1장, 중복 카드 2장, URL 공란 1장 삭제 = 총 4장
- 다음 cards merge 사이클(W6 pipeline)에 함께 처리 권장
- 사용자 triage 워크플로에서 직접 삭제

## Commit
- SHA: (이 commit)
- Audit 참조: `ENHANCED_RED_TEAM_FULLSTACK_AUDIT_20260414.md`
- 계획 참조: `FIX_PROPOSAL_20260414.md`

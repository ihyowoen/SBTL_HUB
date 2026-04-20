#!/usr/bin/env python3
"""
apply_session_agenda.py — 배터리 상담소: 세션 hook agenda

목적:
- opener가 선언한 hook들을 세션 내 **미사용 상태면 계속** 유지
- 유저가 탭한 hook은 usedTopicsRef에 마킹 → 다음 턴부터 사라짐
- followup response에서 "미사용 opener hooks + 서버 hardcoded hooks" 병합 렌더

5개 surgical 패치:
  1. ChatBot 내부 ref 2개 추가 (sessionHooksRef, usedTopicsRef)
  2. composeSessionSuggestions helper 추가
  3. startConsultation에서 opener 응답 시 sessionHooksRef 설정 + usedTopics 리셋
  4. sendConsultFollowup에서 uiMsg.suggestions를 compose로 재합성
  5. runSuggestion에서 탭한 topic을 usedTopics에 마킹

Usage:
    python3 scripts/apply_session_agenda.py           # dry-run
    python3 scripts/apply_session_agenda.py --apply   # 실제 쓰기
"""
from __future__ import annotations

import argparse
import difflib
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_JSX = REPO_ROOT / "src" / "App.jsx"
BACKUP = REPO_ROOT / "src" / "App.jsx.session_agenda.bak"


def fail(msg: str) -> None:
    print(f"\n❌ {msg}", file=sys.stderr)
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"✓ {msg}")


# ═══════════════════════════════════════════════════════════════════════════
# PATCH 1 — ref 2개 추가 (currentConsultRef 직후)
# ═══════════════════════════════════════════════════════════════════════════
P1_BEFORE = '''  // 현재 active consultation — 후속 유저 메시지는 이 consultation followup으로 처리
  const currentConsultRef = useRef(null);

  const isLoading = loadingMode !== "none";'''

P1_AFTER = '''  // 현재 active consultation — 후속 유저 메시지는 이 consultation followup으로 처리
  const currentConsultRef = useRef(null);
  // 세션 hook agenda — opener가 선언한 hook을 유저가 탭할 때까지 유지
  const sessionHooksRef = useRef([]);          // [{label, hint_action, hint_topic}]
  const usedTopicsRef = useRef(new Set());     // Set<string> (hint_topic)

  // 미사용 opener hook + 서버 hook dedupe 병합 (label 기준)
  const composeSessionSuggestions = (serverSugs = []) => {
    const carried = sessionHooksRef.current.filter(
      (h) => h && h.hint_topic && !usedTopicsRef.current.has(h.hint_topic)
    );
    const seen = new Set();
    const out = [];
    for (const s of [...carried, ...(serverSugs || [])]) {
      if (s?.label && !seen.has(s.label)) {
        out.push(s);
        seen.add(s.label);
      }
    }
    return out;
  };

  const isLoading = loadingMode !== "none";'''


# ═══════════════════════════════════════════════════════════════════════════
# PATCH 2 — startConsultation opener 응답 시 sessionHooksRef 세팅
# ═══════════════════════════════════════════════════════════════════════════
P2_BEFORE = '''      await ceremonyWait(t0);
      updateContextFromResponse(data);
      const uiMsg = toUiMessage(data);
      setMsgs((prev) => [...prev, uiMsg]);

      if (init.consultationId) {
        appendMessage(init.consultationId, {
          role: "assistant",
          content: data?.answer || "",
          opener: true,
        });
      }'''

P2_AFTER = '''      await ceremonyWait(t0);
      updateContextFromResponse(data);
      // 세션 agenda 초기화: opener가 선언한 hook을 sessionHooksRef에 저장
      const openerSuggestions = Array.isArray(data?.suggestions) ? data.suggestions : [];
      sessionHooksRef.current = openerSuggestions.filter((s) => s && s.hint_topic);
      usedTopicsRef.current = new Set();
      const uiMsg = toUiMessage(data);
      setMsgs((prev) => [...prev, uiMsg]);

      if (init.consultationId) {
        appendMessage(init.consultationId, {
          role: "assistant",
          content: data?.answer || "",
          opener: true,
        });
      }'''


# ═══════════════════════════════════════════════════════════════════════════
# PATCH 3 — sendConsultFollowup에서 suggestions 재합성
# ═══════════════════════════════════════════════════════════════════════════
P3_BEFORE = '''      await ceremonyWait(t0);
      updateContextFromResponse(data);
      setMsgs((prev) => [...prev, toUiMessage(data)]);
      if (consult.id) appendMessage(consult.id, { role: "assistant", content: data?.answer || "" });'''

P3_AFTER = '''      await ceremonyWait(t0);
      updateContextFromResponse(data);
      // followup: 세션 agenda (미사용 opener hook) + 서버 hook 병합
      const uiMsg = toUiMessage(data);
      uiMsg.suggestions = composeSessionSuggestions(data?.suggestions);
      setMsgs((prev) => [...prev, uiMsg]);
      if (consult.id) appendMessage(consult.id, { role: "assistant", content: data?.answer || "" });'''


# ═══════════════════════════════════════════════════════════════════════════
# PATCH 4 — runSuggestion에서 탭한 topic 추적
# ═══════════════════════════════════════════════════════════════════════════
P4_BEFORE = '''  const runSuggestion = (suggestion) => {
    const label = typeof suggestion === "string" ? suggestion : (suggestion?.label || "");
    const hint = typeof suggestion === "object" ? suggestion : null;
    const map = {'''

P4_AFTER = '''  const runSuggestion = (suggestion) => {
    const label = typeof suggestion === "string" ? suggestion : (suggestion?.label || "");
    const hint = typeof suggestion === "object" ? suggestion : null;
    // 세션 agenda 탭 추적 — consultation 세션일 때만 의미 있음
    const tappedTopic = hint?.hint_topic;
    if (tappedTopic && currentConsultRef.current) {
      usedTopicsRef.current.add(tappedTopic);
    }
    const map = {'''


# ─── 적용 helpers ─────────────────────────────────────────────────────────
def apply_replace(content: str, before: str, after: str, label: str) -> str:
    count = content.count(before)
    if count == 0:
        first = before.split('\n')[0][:80]
        fail(f"[{label}] Before 매칭 0회. 첫 줄: {first!r}")
    if count > 1:
        fail(f"[{label}] Before 매칭 {count}회 — 모호함")
    ok(f"[{label}] 1 match → 적용")
    return content.replace(before, after, 1)


# ─── 메인 ──────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="실제 쓰기")
    args = parser.parse_args()

    if not APP_JSX.exists():
        fail(f"App.jsx 없음: {APP_JSX}")

    print(f"📂 Repo: {REPO_ROOT}")
    print(f"📄 App.jsx: {APP_JSX.stat().st_size:,} bytes")
    print(f"🔧 Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print()

    original = APP_JSX.read_text(encoding="utf-8")
    content = original

    steps = [
        ("P1 refs + composeSessionSuggestions", (P1_BEFORE, P1_AFTER)),
        ("P2 startConsultation opener agenda", (P2_BEFORE, P2_AFTER)),
        ("P3 sendConsultFollowup compose", (P3_BEFORE, P3_AFTER)),
        ("P4 runSuggestion mark used", (P4_BEFORE, P4_AFTER)),
    ]

    for label, (before, after) in steps:
        content = apply_replace(content, before, after, label)

    print()
    print(f"✅ 모든 patch 적용 ({len(original):,} → {len(content):,}자)")

    # diff 통계
    orig_lines = original.splitlines(keepends=True)
    new_lines = content.splitlines(keepends=True)
    diff_lines = list(difflib.unified_diff(
        orig_lines, new_lines,
        fromfile="src/App.jsx (before)",
        tofile="src/App.jsx (after)",
        n=2))
    added = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))
    print(f"📊 diff: +{added}줄 / -{removed}줄")

    if not args.apply:
        diff_file = REPO_ROOT / "scripts" / "session_agenda.diff"
        diff_file.parent.mkdir(exist_ok=True)
        diff_file.write_text("".join(diff_lines), encoding="utf-8")
        print()
        print("⚠️  DRY-RUN 완료 — 파일 변경 없음.")
        print(f"   diff 저장: {diff_file.relative_to(REPO_ROOT)}")
        print("   실제 적용: python3 scripts/apply_session_agenda.py --apply")
        return

    # 실제 적용
    print()
    print("💾 쓰기 중...")
    shutil.copy2(APP_JSX, BACKUP)
    ok(f"backup: {BACKUP.relative_to(REPO_ROOT)}")
    APP_JSX.write_text(content, encoding="utf-8")
    ok(f"write: {APP_JSX.relative_to(REPO_ROOT)}")

    print()
    print("🎉 완료. 다음 단계:")
    print("   1. git add -A && git commit -m \"feat(consult): 세션 hook agenda — 미사용 opener hook 유지\"")
    print("   2. git push origin phase1-consult-redesign")
    print("   3. Vercel preview URL에서 테스트 — opener hook 3개 → 하나 탭 → 나머지 2개가 다음 턴에도 보여야 함")


if __name__ == "__main__":
    main()

#!/bin/bash
# ============================================
# SBTL Card Merge & Push Script
# Usage: ./merge_and_push.sh <branch-name>
# Example: ./merge_and_push.sh cards/w7-run-20260415
# ============================================

set -e

BRANCH="$1"
if [ -z "$BRANCH" ]; then
  echo "❌ 사용법: ./merge_and_push.sh <branch-name>"
  echo "   예시: ./merge_and_push.sh cards/w7-run-20260415"
  exit 1
fi

# Extract run name for payload path (e.g. cards/w7-run-20260415 → w7_20260415)
RUN_ID=$(echo "$BRANCH" | sed 's|cards/||' | sed 's/-run-/_/')
PAYLOAD="docs/card_payloads/payload_${RUN_ID}.json"
TODAY=$(date +%Y.%m.%d)

echo "🔄 [1/7] main 동기화..."
git fetch --all
git switch main
git pull origin main

echo "🔄 [2/7] 브랜치 이동 + rebase..."
git switch "$BRANCH"
git rebase main

# Check payload exists
if [ ! -f "$PAYLOAD" ]; then
  echo "❌ 페이로드 파일 없음: $PAYLOAD"
  echo "   다른 경로라면: ./merge_and_push.sh <branch> <payload-path>"
  exit 1
fi

echo "💾 [3/7] 백업..."
cp public/data/cards.json ~/cards_before_merge.backup

BEFORE=$(python3 -c "import json; d=json.load(open('public/data/cards.json')); print(d.get('total', len(d.get('cards',[]))))")
echo "   현재: ${BEFORE}건"

echo "🔀 [4/7] 머지 실행..."
python3 merge_cards.py "$PAYLOAD"

echo "📅 [5/7] updated 날짜 패치..."
python3 -c "
import json
with open('public/data/cards.json','r') as f: d=json.load(f)
d['updated']='${TODAY}'
with open('public/data/cards.json','w') as f: json.dump(d,f,ensure_ascii=False)
print(f'   total={d[\"total\"]}, updated={d[\"updated\"]}')
"

AFTER=$(python3 -c "import json; d=json.load(open('public/data/cards.json')); print(d['total'])")
ADDED=$((AFTER - BEFORE))

echo ""
echo "✅ [6/7] 검증: ${BEFORE} → ${AFTER} (+${ADDED}건)"
echo ""

read -p "👉 커밋+푸시 진행? (y/n) " CONFIRM
if [ "$CONFIRM" != "y" ]; then
  echo "⏸ 중단. 백업: ~/cards_before_merge.backup"
  exit 0
fi

echo "🚀 [7/7] 커밋 + 푸시..."
git add public/data/cards.json
git commit -m "cards: +${ADDED} cards (${BEFORE}→${AFTER})"
git push origin "$BRANCH"

echo ""
echo "✅ 완료! GitHub에서 PR 머지 후:"
echo "   git switch main && git pull && git branch -d ${BRANCH}"
echo ""
echo "🗑 백업 삭제: rm -f ~/cards_before_merge.backup"

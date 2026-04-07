# 2026-04-07 rechecked merge payload

## Baseline
- repo: `ihyowoen/SBTL_HUB`
- target file: `public/data/cards.json`
- baseline source: GitHub `main`
- working rule: conservative add only

## Approved add set (8)
1. SNE EV demand recovery / oil shock
2. MSS CBAM infrastructure support notice
3. Global EV battery usage + K-battery share decline
4. KR EV bus subsidy redesign / anti-China guardrail
5. BYD Korea 10k cumulative sales
6. Top Material turnkey line to Türkiye battery company
7. SK On anode-material performance tech
8. Chungbuk recycling / safe-process infrastructure cluster

## Explicit exclusions
- `캘리포니아, 전력비용 기업 부담으로 전환…데이터센터 ESS 도입 필수화`
  - existing URL already present in `cards.json`
- `SK온, 파우치 통합 각형 셀 상반기 개발 완료 목표`
  - existing URL already present in `cards.json`
- `영국, 폐배터리 첫 가치 평가 기준 마련…ABI 지수 공개`
  - stale / previously removed from main on recency rule
- MCEE CBAM manual and ImpactON CBAM manual book article
  - same policy cluster; prefer the MSS operational support notice for new addition
- YNA/SNE duplicate EV recovery theme
  - keep SNE as stronger source card for same-day add

## Merge note
This payload is locked as the safe add set after corrected shortlist review.

# Legacy Related Dangling Manifest — 2026-07-23

## Scope

- Baseline checked: **1,250 cards**
- Affected legacy cards: **13**
- Dangling Related edges: **14**
- Current-run 35 new cards: **not affected**

These are pre-existing baseline defects. They are not silently removed or guessed in the workflow-hardening PR.

## Manifest

| Card | Title | Missing Related IDs |
|---|---|---|
| `2026-04-27_KR_10` | 엔켐 유럽 전해액 전략 재편 | `2026-04-22_KR_05` |
| `2026-04-27_JP_01` | Nippon Shokubai 중국 LiFSI 증설 | `2026-04-22_KR_05` |
| `2026-04-27_CN_22` | 후난 스마트 터키 BESS 모듈 라인 | `2026-04-22_GL_03` |
| `2026-04-27_CN_18` | 풍운T9L·궈쉬안 LFP 셀 | `2026-04-22_KR_05` |
| `2026-04-27_CN_15` | CATL·Jianlong 산업 EV 협력 | `2026-04-23_CN_05` |
| `2026-04-27_CN_08` | 둥관 LiB 기업 단속 | `2026-04-22_CN_05` |
| `2026-04-16_KR_07` | 대전 GPU 데이터센터 기공 | `2026-04-15_KR_03` |
| `2026-04-16_CN_05` | 엔리파워 반고체 2GWh 기지 | `2026-04-16_CN_04` |
| `2026-04-15_US_04` | Aqua Metals Sierra ARC 완공 | `W6R1_03` |
| `2026-04-15_KR_02` | KIND 일본 고압 BESS 투자 | `2026-04-22_GL_03` |
| `2026-04-15_CN_02` | 쥐성에너지 전고체 생산 일정 | `2026-04-16_CN_04` |
| `2026-04-15_CN_01` | CATL 광물 자회사·1Q·M&A | `2026-04-16_US_01`, `2026-04-16_CN_03` |
| `2026-04-14_CN_01` | TaiLan 전고체 배터리 납품 | `2026-04-16_CN_04` |

## Required remediation per edge

1. Search repository history, prior `cards.json` versions and prior replacement artifacts for the missing ID.
2. Compare actor, project/policy, location, event date, execution stage and factual anchor.
3. Restore a surviving production ID only when direct lineage is proved.
4. When the old relation was invalid, obsolete or unresolvable, remove it and record an item-specific reason.
5. Run `validation_scripts/related_lifecycle_check.py` against the complete candidate before merge.

## Prohibition

- Do not retarget by title similarity alone.
- Do not invent a replacement ID.
- Do not delete the edge without an audit row.
- Do not mix this legacy remediation into new-card workflow changes without explicit review.

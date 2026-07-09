# SBTL LLM 에디토리얼 프롬프트 — 최종본 매니페스트

**갱신**: 2026-06-23 | **위치**: `releases/2026-03-03/out/LLM_Prompt/` (로컬=정본, GitHub main outdated)

## 파이프라인 흐름
`newsletter_expanded → 0.1→0.2→0.3 (→0.2R/0.3R) → 0.4 → 0.5 → 0.6 → 0.7 → 0.8 → 0.9 (→1.0/1.1)`

## 단계 프롬프트 (14)
| 단계 | 파일 | 줄 | 역할 |
|---|---|---|---|
| 0.1 | 01_PROMPT_0_1_Stage_A.md | 2267 | Stage A — 입력 스토리 on-scope 선별·실행앵커 |
| 0.2 | 02_PROMPT_0_2_Stage_B_r0.md | 2159 | Stage B — 카드 초안 + fact_sources 생성 |
| 0.3 | 03_PROMPT_0_3_Stage_C_r0.md | 1623 | Stage C — FACT_DISCIPLINE 검증·수용 |
| 0.2R | 04_PROMPT_0_2R_Stage_B_Revise.md | 914 | Stage B 재작성 |
| 0.3R | 05_PROMPT_0_3R_Stage_C_Revise.md | 840 | Stage C 재검증 |
| 0.4 | 06_PROMPT_0_4_Baseline_Revalidation.md | 1569 | Baseline 재검증·dedup ★URL패치 |
| 0.5 | 07_PROMPT_0_5_Evidence_QC.md | 2270 | 증거 완전성·source-claim QC ★URL패치(주축) |
| 0.6 | 08_PROMPT_0_6_Content_Polish.md | 2054 | 콘텐츠·언어 폴리시 ★URL패치(전파) |
| 0.7 | 09_PROMPT_0_7_Final_QC.md | 1929 | 최종 발행QC ★URL패치(미러게이트) |
| 0.8 | 10_PROMPT_0_8_GitHub_Merge_Prep.md | 1762 | GitHub 머지 준비 |
| 0.9 | 11_PROMPT_0_9_Production_Verification.md | 1282 | 운영 검증 |
| 1.0 | 12_PROMPT_1_0_Remediation.md | 1059 | 교정 |
| 1.1 | 13_PROMPT_1_1_Retrospective.md | 1698 | 회고 |
| 0.1P | 14_PROMPT_0_1P_Review_Pool_Promotion.md | 188 | 리뷰풀 승격 |

## 거버넌스 문서 (9)
| 문서 | 줄 |
|---|---|
| FACT_DISCIPLINE.md | 217 |
| PROMPT_ABC_DEFAULT_MODE.md | 1218 |
| PROMPT_ABC_SUPPORTING_RULES.md | 1105 |
| FUTURE_CARD_STANDARD_FULL_SCHEMA.md | 187 |
| CARD_ID_STANDARD.md | 108 |
| SCHEMA_CONTRACT_STAGE_LINEAGE.md | 170 |
| WORKFLOW.md | 1435 |
| OPERATIONS.md | 1429 |
| POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md | 1175 |

## 적용 패치
### `SOURCE_URL_RESOLUTION_INTEGRITY_20260622` (4파일: 0.4/0.5/0.6/0.7)
source_url 해상 검증 3축 추가 — CHECK1 canonical 완전성(절단/generic 차단), CHECK2 기사 해상, CHECK3 prefix 전파. 공유필드 `source_url_resolution_summary`, 4 reason-code, 0.7 미러게이트 `BLOCKED_SOURCE_URL_RESOLUTION_FAIL`, post-0.7 augmentation 금지.
**검증**: 구조(감사) + 기능(focused dry-run: EFP-01/02 차단·정상통과) + 실파이프라인(Stage A→0.7: 57/57 canonical, 오탐 0, 0.7 라이브 WebFetch로 CHECK2). 백업: `.backups_urlres_20260622/`.

## 배포 상태
- ✅ 로컬 정본 4파일 패치 적용·검증 완료
- ⚠️ **GitHub main 미반영** (프롬프트가 'main에서 읽어라'고 명시 → 운영 반영하려면 로컬→main push 필요, 수동)

## 정리 내역 (2026-06-23)
- Zone.Identifier(윈도우 ADS) 25개 제거
- 패치 .bak 4개 → `.backups_urlres_20260622/` 이동

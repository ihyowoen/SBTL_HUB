# SBTL LLM 에디토리얼 프롬프트 — 최종본 매니페스트

**갱신**: 2026-07-19 | **정본**: GitHub `main`의 본 디렉터리와 canonical/upload manifest

## 파이프라인 흐름

`newsletter_expanded → 0.1→0.2→0.3 (→0.2R/0.3R) → 0.4 → 0.5 → 0.6 → 0.7 → 0.8 → 0.9 (→1.0/1.1)`

## 단계 프롬프트 (14)

| 단계 | 파일 | 역할 |
|---|---|---|
| 0.1 | 01_PROMPT_0_1_Stage_A.md | Stage A — 입력 스토리 on-scope 선별·실행앵커 |
| 0.2 | 02_PROMPT_0_2_Stage_B_r0.md | Stage B — 카드 초안 + fact_sources 생성 |
| 0.3 | 03_PROMPT_0_3_Stage_C_r0.md | Stage C — FACT_DISCIPLINE 검증·수용 |
| 0.2R | 04_PROMPT_0_2R_Stage_B_Revise.md | Stage B 재작성 |
| 0.3R | 05_PROMPT_0_3R_Stage_C_Revise.md | Stage C 재검증 |
| 0.4 | 06_PROMPT_0_4_Baseline_Revalidation.md | Baseline 재검증·dedup |
| 0.5 | 07_PROMPT_0_5_Evidence_QC.md | 증거 완전성·source-claim QC |
| 0.6 | 08_PROMPT_0_6_Content_Polish.md | 콘텐츠·언어 폴리시 |
| 0.7 | 09_PROMPT_0_7_Final_QC.md | 최종 발행 QC |
| 0.8 | 10_PROMPT_0_8_GitHub_Merge_Prep.md | GitHub merge 준비 |
| 0.9 | 11_PROMPT_0_9_Production_Verification.md | 운영 검증 |
| 1.0 | 12_PROMPT_1_0_Remediation.md | 교정 |
| 1.1 | 13_PROMPT_1_1_Retrospective.md | 회고 |
| 0.1P | 14_PROMPT_0_1P_Review_Pool_Promotion.md | 리뷰풀 승격 |

## 거버넌스 문서 (9)

- `docs/FACT_DISCIPLINE.md`
- `docs/PROMPT_ABC_DEFAULT_MODE.md`
- `docs/PROMPT_ABC_SUPPORTING_RULES.md`
- `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md`
- `docs/CARD_ID_STANDARD.md`
- `docs/SCHEMA_CONTRACT_STAGE_LINEAGE.md`
- `docs/WORKFLOW.md`
- `docs/OPERATIONS.md`
- `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`

## 필수 Integrity Override

### `DATE_STORYID_RELATED_INTEGRITY_V1`

다음 파일은 canonical prompt package와 업로드 패키지에서 **필수 구성요소**다.

- override: `00_DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_V1.md`
- registry: `DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_MANIFEST.json`
- Stage A addendum: `01_PROMPT_0_1_Stage_A_HARDENING_ADDENDUM_V1.md`
- Prompt 0.5 addendum: `07_PROMPT_0_5_Evidence_QC_HARDENING_ADDENDUM_V1.md`
- Prompt 0.6 addendum: `08_PROMPT_0_6_Content_Polish_HARDENING_ADDENDUM_V1.md`
- Prompt 0.7 addendum: `09_PROMPT_0_7_Final_QC_HARDENING_ADDENDUM_V1.md`
- Prompt 0.8 addendum: `10_PROMPT_0_8_GitHub_Merge_Prep_HARDENING_ADDENDUM_V1.md`
- Prompt 0.9 addendum: `11_PROMPT_0_9_Production_Verification_HARDENING_ADDENDUM_V1.md`

Prompt assembler나 업로드 도구는 위 override·registry·해당 단계 addendum을 생략해서는 안 된다. 생략 시 날짜 역할 분리, cross-run story-ID 충돌 격리, related 계보 검증이 적용되지 않은 것으로 간주한다.

핵심 강제사항:

1. `event_date`, `source_published_date`, `discovery_or_ingestion_date` 분리
2. story ID를 단독 identity 근거로 사용 금지
3. Stage A에서는 related 후보만 제안하고 production `related[]`는 수정 금지
4. 미확정 과거 related 참조는 lineage 검색 전 삭제 금지
5. 0.5~0.9에서 claim·quote·날짜·ID·related 무결성을 독립 재검증

## 필수 Validator (3)

- `validation_scripts/date_role_alignment_check.py`
- `validation_scripts/story_id_lineage_check.py`
- `validation_scripts/related_lineage_check.py`

Validator는 canonical/upload manifest에 등록된 구성요소이며, override manifest가 적용 범위를 정의한다.

## 기존 적용 패치

### `SOURCE_URL_RESOLUTION_INTEGRITY_20260622`

0.4~0.7에서 canonical URL 완전성, 기사 해상, prefix 전파를 검증한다.

### `SEARCH_BEFORE_DELETE_20260712_V1`

`SEARCH_BEFORE_DELETE_OVERRIDE_MANIFEST.json`에 등록된 필수 충돌 override다. 원칙은 `Find first. Verify second. Integrate third. Delete only last.`다.

## 배포 상태

- ✅ branch `agent/prompt-date-storyid-related-integrity`에 override·addendum·validator 등록
- ✅ `LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json` 등록
- ✅ `UPLOAD_MANIFEST.json` 등록
- ✅ 전용 `DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_MANIFEST.json` 등록
- ⚠️ PR #191 merge 전까지 GitHub `main`에는 미적용

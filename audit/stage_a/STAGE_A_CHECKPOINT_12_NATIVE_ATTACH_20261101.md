# Stage A 체크포인트 #12 — 70개 사전 판단을 네이티브 산출물에 무손실 연결

**작성 기준:** 2026-11-01 UTC / **검증 기준 `main`:** `805c2718d6daf40a219ae94242d9687e33ac3e88`  
**Stage A 전체 상태:** `HOLD_FOR_FULL_0_1P_ADJUDICATION`  
**관련 집행:** Stage B 신규 진입 없음, Full/Related/production 변경 없음.

## 1. 실제 처리 범위

2026-10-27의 정식 1,330행 Stage A 재심사 산출물
`STAGE_A_REASSESSED_1330_20261027.json`(SHA256
`b64e4f99f97a872203a4224aed5017697894637391930410577efbcdc35ba8c6`)
을 변경 불가능한 모본으로 취급하여, 기존의 사전 판단 54개와 16개를 각
Source ID의 `decision_ledger` 및 기존 Review/WATCH 파티션 원장에
`pre_native_0_1P_judgment_attachment_20261101`이라는 **비권위 필드**로 연결했다.
모본 또는 기존 판단 필드를 덮어쓰지 않았으며, 새로운 strict 판정을 생성하지 않았다.

| 구분 | 결과 |
|---|---:|
| 원래 Source ID | 1,330개 보존 |
| 기존 개별 0.1P 판정 이력 | 45개 보존 |
| 사전 판단 입력 | 16 + 54 = 70개 연결 |
| 신규 70개와 기존 45개 중복 | 0 |
| 신규 70개 배치 위치 | Review 65 / WATCH 5 |
| 네이티브 기존 strict | 8개 그대로 |
| 정식 0.1P 추가 완료 | 0개 |
| 정식 0.1P 미완료 | 1,285개 그대로 |
| 신규 Stage B 권한 | 없음 |

예비 판단의 독립성 검사는 70개 중 집행 신뢰도 PASS 16 / REVIEW 54,
독립 카드성 FAIL 48 / REVIEW 22를 기록한다. 이것은 **사전 판단** 분류로서
정식 Stage A 통과/탈락이나 Related 처분 확정을 의미하지 않는다.

## 2. 두 네이티브 검사 직접 재실행

잠금된 `main` 저장소의 실제 스크립트를 변경 없이 실행했다.

```bash
python validation_scripts/stage_artifact_contract_check.py A STAGE_A_1330_NATIVE_70_PRENATIVE_ATTACHED_20261101.json
# exit=0, status=PASS, stage=A, item_count=8, missing_count=0, findings=[]

python validation_scripts/stage_lineage_contract_check.py stage_a STAGE_A_1330_NATIVE_70_PRENATIVE_ATTACHED_20261101.json
# exit=0, RESULT: PASS_STAGE_A_SCHEMA_CONTRACT
```

**주의:** 위 PASS는 변동 없는 기존 strict 8개와 정식 산출물 껍질·계보에 대한
검증이다. 두 검사가 새로 연결된 70개의 사전 판단을 정식 승격으로 승인하는
것은 아니다. `strict_passed_spec`는 수정하지 않았다.

## 3. 독립 무손실 확인

별도 검증 스크립트가 모든 추가 필드를 제거한 후 **정식 산출물의 기존 전 필드**를
모본과 심층 비교했다. 1,330개 결정행의 ID·순서·원본 URL·내용·점수·집행
및 Related 게이트, 4개 파티션과 strict 배열은 모두 불변이었다.
70개 판단은 원본 54/16 파일과 값이 같고, 각 해당 Source ID의
`decision_ledger` 및 파티션에 정확히 1회씩 연결됐다. 별도 QC 결과
`PASS_ADDITIVE_ATTACHMENT_ONLY`.

Drive에 업로드한 **7개 파일 모두 재다운로드 SHA256이 로컬 원본과 일치**했다.

## 4. 보존 결과

| 산출물 | Drive | SHA256 |
|---|---|---|
| 1,330행 네이티브 결합본 64 MB | [전체 산출물](https://drive.google.com/file/d/1-Ni-5CRYmvFA07rIqzcb_x0TFDg3EZqu/view) | `e42097f6f17495ff24550b2c72dba9d5874e7a835090c95cae4881750116d109` |
| 70개 원문 사전 판단·Source ID 매핑 | [70건 게이트 원장](https://drive.google.com/file/d/1Dbs7U55Uasz-7PBf7mQBD1I8iuTWdJMl/view) | `749e87794277cd06095a5038b5a419bdf80d503b7ad56d8bfdb96952b169e3dd` |
| 통합 QC | [QC 보고](https://drive.google.com/file/d/1Km344eCibpTYXjwiEjtIymZRdYeLd99s/view) | `5df6c295273e7c20c47e7d008ee23bb1e3d4690153e2d16029f4a69d93950c5a` |
| 독립 무손실 QC | [독립 검증](https://drive.google.com/file/d/1-_e394xC6ezZ9cf45DrEHqsRP3AZXWHM/view) | `1a7812f271fd3a504353d0126d9c52086e2094726a1d2adb1c83373d22eb8959` |
| 네이티브 검사 결과 | [네이티브 PASS 영수증](https://drive.google.com/file/d/1xS3zsi7aRNXQ4XAGavQwh6IKcmmPCTq1/view) | `abe25217861a16cfeea3f0df25d1ef44852553652a4eba1f9d5e17f260220d12` |
| 재현 생성 코드 | [빌드 스크립트](https://drive.google.com/file/d/15OGiKzvZ-gLg_f0m9lLGPlzLgX6LDfx-/view) | `90a63495cd4b3e48419dd27515ce2a1598001aa89c7dec3fd68552d0efbcd0d9` |
| 독립 QC 코드 | [검증 스크립트](https://drive.google.com/file/d/1PysYICUNeVg_I8TjMyp1gAKuPxOV-NbF/view) | `ecad05e4025d991135281ca021ba7c05956409d003e9cf21acaf1975d54aa5ec` |

감사 소형 산출물은 GitHub `audit/stage-a-event-family-20261101` 브랜치의
`audit/stage_a/`에 추가 누적한다. 대용량 64 MB 본문은 Drive에 보존하고,
GitHub에서 전체 해시와 링크를 검증 가능하게 관리한다.

## 5. 남은 승인 병목

Source ID 70개를 정식 0.1P 완료로 간주할 수 없다. 각 출처의 원문 범위,
경제행위 단위, Full 1,676건에 대한 의미적 선후·중복 관계, 초기 발행일,
신규 정보와 판단 변화 및 V4 점수/캡 검토를 정식으로 완결해야 한다.
나머지 1,285개 전체에 대해 개별 판정·처분을 완료한 후 Stage A 전체 마감을
판단해야 한다. 기사 수·Stage B 진입을 아직 고정하지 않는다.

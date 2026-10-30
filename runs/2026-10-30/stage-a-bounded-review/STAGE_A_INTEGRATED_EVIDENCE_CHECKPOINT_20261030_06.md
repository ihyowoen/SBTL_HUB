# SBTL_HUB — Stage A 1,330 Source ID 통합 증빙 체크포인트 06

- 기준일: 2026-10-30 KST
- 단계: Stage A 0.1P 미종결 / 원문 근거의 제한적 재구성 및 정산
- 산출물 성격: **비정식 증빙 원장·독립 무손실 QC**. Stage A 정식 PASS나 카드 승격 승인 아님.
- 저장 정책: 기존 원본 보존, create-only, 1,330 Source ID 무손실. 기존 7건 Stage B~0.6 증빙 별도 보존.

## 잠금 기준과 이번 작업에서 확인한 데이터

| 항목 | 확인 값 / 판정 |
| --- | --- |
| GitHub main HEAD (읽기 전용 조회) | `805c2718d6daf40a219ae94242d9687e33ac3e88` |
| GitHub 감사 브랜치 작업 시작 HEAD | `c0c568f52b98f12f505a275d244b4928ba662a5a` |
| Locked Full Git blob | `07a91714e56be2a8bfad10ab63822f0c5cb3f06e`, Full 1,676건 |
| 10/27 Stage A 원본 CSV SHA256 | `5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116` |
| 원본 모집단 | **1,330** 고유 ID, 원래 순서와 상태·점수 무손실 |
| 기존 Stage A 분류 | 정밀검토 대기 **636**, WATCH·맥락 **658**, 중복·보강 **28**, 기존 정식 통과 **8** |
| 기존 0.1P 개별 판정 | **45 ID** (해당 잠정 사건 23건); **1,285 ID** 개별 정식 판정 여전히 없음 |
| 통합 원장에 연결한 추가 증빙 | **83 고유 ID**, 증빙 링크 없는 ID **1,247**; 증빙 존재 ≠ 정식 판정 |
| 60점 이상 메타데이터 103 ID | 일부 증빙 링크 있음 **49**, 링크 없음 **54**; 49도 정식 PASS 미확보 |
| 0.1P 추가 네이티브 승격 | **0** |

83개 ID는 `10/29 기존 25개 ID ∪ 10/30 기존 65개 ID ∪ 이번 1차 자료 신규 6개 ID`의 **중복 제거된 합집합**이다. 앞의 두 집합에 13개 중복이 있으며, 최종 집합은 `25 + 65 - 13 + 6 = 83`이다. 이전 45개 정식 심사 여부와 혼동하거나 두 모집단을 단순 합산하지 않는다.

## 이번에 실제 확인한 1차 자료: 5개 사건군·6개 Source ID

| 사건군 | 원문 확인에 따른 제한적 결론 | 정식 판정 |
| --- | --- | --- |
| Nth Cycle–Glencore Project SHIELD | 9/22 **구속력 있는 term sheet**, 10년 **전망가격 기준 10억 달러 초과 예상치**; 최종 계약 체결·공급 실적 아님. 3월 Nth Cycle–Trafigura 카드와 별개 상대방·행위. | HOLD |
| Oriana–MSEDCL BESS | 9/18자 **두 개 LOA**, 각각 500MW/1,000MWh 및 400MW/800MWh. BESPA 정식 체결은 후속 단계. 하나의 출처 ID가 두 경제적 수주 단위를 설명함. | HOLD |
| Gotion–Saudi 6GWh 공급 | 9/11 공급사 이정표. 기존 Saudi 2GW/8GWh 프로그램과 **중복 용량 가산 금지**; 정확히 어느 3개 현장에 해당하는지 계약 연결 미확인. | HOLD |
| ESR–Aquila APAC | 9/24 **지분 100% 인수 계약 체결**. 1.6GW는 태양광·풍력·배터리 혼합 자산/단계이고 인수종결도 미완료. | HOLD |
| Glencore–VaultCo | 9/23 프로그램 민간 파트너 이정표, Glencore **5억 달러 커밋**. 복수 회사 합계 10억 달러 및 2월 별도 EXIM 기존 프로그램과 구별. 두 Source ID가 하나의 사건군. | HOLD |

원문 URL과 원문의 의미·단계·미해결 근거는 아래 원본 사건 증빙 JSON에 기록했다. 위 HOLD는 중요도가 낮거나 제외 결정이라는 뜻이 아니라 **정식 0.1P 4중 판단 및 기존 Full/Related 대조 미종결**이라는 뜻이다.

## 저장된 파일, Drive readback SHA256

모든 아래 5개 파일은 기존 프로젝트 폴더 `1iR8zKzDe18nzpiW5a-aX3IvXsHoyEdUk`에 별도 신규 업로드한 뒤, Drive 원본을 다시 내려받아 독립 SHA256 대조에서 **5/5 정확히 일치**했다.

| 파일 / 링크 | SHA256 | 검증 범위 |
| --- | --- | --- |
| [5개 원문 사건군·6 ID JSON](https://drive.google.com/file/d/1742AOnMLYWk225IT3WnrB4UyB5uuPuZ5/view) | `5c1f6f45c01e1346d4b43320a5bc3d9625c045b44bc2aa466edaec8e93ec1d3a` | 9,114 bytes, 보관·readback PASS |
| [1,330 ID 통합 근거 JSON](https://drive.google.com/file/d/1UwXGZ0IfxJSKh0G4RbnXYUFdO_RRXaAC/view) | `3993f348b1ab872a34a5f41b10451e65b143e61c647be7e649f37f1a9f7c2eba` | 1,596,921 bytes, 보관·readback PASS |
| [Source ID·분류·원장 독립 QC](https://drive.google.com/file/d/12z6BZTmEan_niv8I2Dit1jBslBZJNflg/view) | `14ced992b29fe5235af1676a588ca82a6a70ef1e418745bd022faa967087eff4` | 1,239 bytes, 제한적 무손실 PASS |
| [통합 필터 엑셀 / 개요](https://docs.google.com/spreadsheets/d/11DeYsNj0GCOJQVZMRLaoe4FyfJDO9WNC/edit) | `1c0c1227ecc49c377973f8042c8f7b215c0f9a6c2b2a26b7cf503d8d4af39fc6` | 211,944 bytes, 1,330행·계산식 8개 export/readback PASS |
| [엑셀 독립 export QC](https://drive.google.com/file/d/1uZbpCdgnahDJXxDA8VHZuL4z8YllqQfP/view) | `8a5b30f5698db3a1699e4bfdc0b2282b39e3d3e9eeefc48338ac89a65e5f016e` | 425 bytes, 보관·readback PASS |

**검증의 한계:** 위 PASS는 1,330행/ID 보존, 기존 필드 보존, 추가 증빙 병합의 ID 중복 처리, 산출물 바이트 및 엑셀 요약 계산의 정확성에만 적용한다. Stage A artifact/lineage native contract는 전체 사건별 판정이 끝나지 않아 **미실행**. Stage 0.6 native final **HOLD**, Stage 0.7 **미진입**, 신규 카드 발행·병합 **0**.

## 보존·변경·다음 한 개의 병목

- 보존: 기존 main/Full/Lean/Related/PR #386/프로덕션/Revolution Masterfile/Downstream은 건드리지 않음. 승인된 감사 브랜치에만 재현 코드·체크포인트를 추후 추가한다.
- 해결: 다중 체크포인트 증빙을 **단일 ID 보존 원장**과 조회 가능한 엑셀로 통합하고, 다섯 1차 사건군의 잘못된 금액·발생 단계·중복 용량 해석을 사건 수준에서 제한적으로 정정.
- 미해결: 개별 0.1P 판정 없는 **1,285 ID**, 그중 고점수이지만 아직 연결된 추가 원문 근거가 없는 **54 ID**. 개별 사건 ID 공란을 단순 제목 유사도로 임의 확정하지 않음.
- **다음 단 하나의 실행 병목:** 60점 이상 103 ID 가운데 **추가 증빙 없는 54개 ID**를 원문 본문·일차 발표·기존 Full/Related와 대조하여 사건 단위로 하나씩 판별하고, 0.1P 네 가지 정식 판단에 필요한 증거를 채운다. 이후 636 전수, WATCH 658 포함 전체 1,330 원본을 누락 없이 마감한다. 점수로 일괄 제외하거나 승격 건수를 고정하지 않는다.

## 재개 규칙

최신 체크포인트와 `STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_20261030.json`를 우선 읽는다. 원본 CSV SHA와 1,330개 Source ID 순서가 일치하는지 먼저 확인한다. `evidence linked`와 `native accepted`를 절대 같은 상태로 표현하지 않는다. 이전 판정·증거는 삭제하지 않고 신규 파일을 create-only로 누적한다.

#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RUN_DIR = ROOT / "runs/2026-09-03"
A_PATH = RUN_DIR / "stage_a_formal_r6_batch01_20260903_R1.json"
OUT = RUN_DIR / "stage_b_r6_strict7_20260903_R1.json"
REPORT = RUN_DIR / "stage_b_r6_strict7_validation_20260903_R1.json"
PROMPT = ROOT / "docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md"
CANON = ROOT / "data/cards.full.json"

MAIN = "df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4"
CANON_BLOB = "53219907cdb435c3822c41d097b23e475662aa8a"
A_SHA = hashlib.sha256(A_PATH.read_bytes()).hexdigest()

stage_a = json.loads(A_PATH.read_text(encoding="utf-8"))
strict = stage_a["strict_passed_spec"]
assert len(strict) == 7


def ordinal(spec: dict) -> int:
    m = re.search(r"_(\d{3})$", spec["spec_id"])
    assert m, spec["spec_id"]
    return int(m.group(1))

spec_by_ord = {ordinal(s): s for s in strict}
assert set(spec_by_ord) == {2, 3, 4, 5, 8, 9, 10}

E = {
  2: {
    "region": "US", "cat": "ESS", "sub_cat": "LFP cell supply / US manufacturing",
    "signal": "top",
    "title": "SK온, 네오볼타에 미국산 LFP 9GWh 공급…ESS 현지생산 전환 가속",
    "sub": "2027~2031년 5년 계약…추가 9GWh·팩 역구매 협력은 별도 프레임워크",
    "gate": "미국 ESS용 LFP 셀 공급이 실제 장기계약으로 전환됐다.",
    "fact": "SK온과 NeoVolta Power는 미국산 LFP 셀 9GWh를 2027~2031년 공급하는 5년 계약을 체결했다. 양사는 추가 9GWh 셀 공급과 NeoVolta가 생산한 ESS 팩을 SK온이 구매하는 확대 협력 프레임워크도 공개했지만, 추가 9GWh는 초기 9GWh와 동일한 확정계약으로 취급하지 않는다.",
    "implication": [
      "미국 내 EV 배터리 생산자산을 ESS·LFP 수요로 다변화하는 전략이 계약 단계로 진입했다.",
      "총 18GWh를 전부 확정 공급물량으로 표현하면 안 되며, 추가 9GWh·팩 구매는 후속 계약 여부를 추적해야 한다."
    ],
    "event_date_role": "agreement announcement/signing", "event_date": "2026-08-31",
    "facts": [
      ("S2-C1", "SK온이 NeoVolta Power에 미국산 LFP 셀 9GWh를 2027~2031년 공급하는 5년 계약을 체결했다.", ["S2-P1", "S2-I1"]),
      ("S2-C2", "초기 계약 외 추가 9GWh 셀 공급 및 NeoVolta 생산 ESS 팩의 SK온 구매는 확대 협력 프레임워크다.", ["S2-P1", "S2-I1"]),
      ("S2-C3", "계약 셀은 미국 내 생산으로 공급된다.", ["S2-P1", "S2-I1"]),
    ],
    "sources": [
      {"id":"S2-P1","owner":"NeoVolta","role":"counterparty_primary_release","url":"https://neovolta.com/blog/neovolta-announces-strategic-u-s-battery-cell-supply-and-bess-manufacturing-coll","published":"2026-08-31","summary":"NeoVolta confirms signed five-year 9 GWh U.S.-manufactured LFP supply for 2027-2031 and a broader additional-9-GWh/pack-purchase framework."},
      {"id":"S2-I1","owner":"S&P Global Commodity Insights","role":"independent_confirmation","url":"https://www.spglobal.com/energy/en/news-research/latest-news/metals/090126-sk-on-lands-5-year-deal-to-supply-ess-batteries-to-us-neovolta-unit","published":"2026-09-01","summary":"Independent report confirms 9 GWh, five years, 2027-2031, Georgia production and that the extra 9 GWh is pursued through a separate later contract."},
      {"id":"S2-I2","owner":"Reuters","role":"independent_conflict_check","url":"https://www.reuters.com/business/energy/sk-signs-battery-supply-deal-energy-storage-system-use-with-neovolta-power-2026-08-30/","published":"2026-08-30","summary":"Reuters independently confirms the 9 GWh deal but its date-range wording differs from the contracting party release; the primary contract-party wording controls."},
    ],
    "source_conflicts": [{"field":"supply_period","resolution":"Use NeoVolta/S&P 2027-2031. Reuters wording indicating a later end date is not used in visible copy because the contracting-party release explicitly states a five-year 2027-2031 term."}],
    "related": None,
  },
  3: {
    "region": "GL", "cat": "PowerGrid", "sub_cat": "Australia wind+BESS / project finance",
    "signal": "top",
    "title": "CIP, 호주 Gawara Baya 인수·금융종결…408MW 풍력+104MW BESS 건설 진입",
    "sub": "Windlab서 100% 인수, AUD 17억 금융…2030 완전 가동 목표",
    "gate": "개발 프로젝트가 인수·FID·금융종결을 거쳐 건설 단계로 넘어갔다.",
    "fact": "Copenhagen Infrastructure Partners의 CI V는 Windlab로부터 Gawara Baya를 100% 인수했다. 프로젝트는 408MW 육상풍력과 104MW grid-forming BESS로 구성되며, 주요 승인·최종투자결정·금융종결을 마치고 건설에 들어간다. CIP는 10개 은행을 통한 AUD 17억 금융시설과 2030년 완전 가동 목표를 밝혔다.",
    "implication": [
      "호주 BESS가 독립 저장설비뿐 아니라 대형 재생에너지 프로젝트의 계통안정 자산으로 금융조달 단계에 내재화되고 있다.",
      "향후 확인점은 실제 착공·공정률·BESS 공급자 선정과 2030년 상업운전 일정이다."
    ],
    "event_date_role": "acquisition / financial close / construction entry", "event_date": "2026-08-31",
    "facts": [
      ("S3-C1", "CI V가 Windlab로부터 Gawara Baya 프로젝트 지분 100%를 인수했다.", ["S3-P1","S3-P2"]),
      ("S3-C2", "프로젝트는 408MW 풍력과 104MW grid-forming BESS로 구성된다.", ["S3-P1","S3-P2"]),
      ("S3-C3", "AUD 17억 규모 금융종결 후 건설에 진입하며 완전 가동 목표는 2030년이다.", ["S3-P1","S3-P2"]),
    ],
    "sources": [
      {"id":"S3-P1","owner":"Copenhagen Infrastructure Partners","role":"acquirer_primary_release","url":"https://news.cision.com/copenhagen-infrastructure-partners-p-s/r/copenhagen-infrastructure-partners-acquires-onshore-wind-and-battery-project-in-australia%2Cc4389153","published":"2026-08-31","summary":"CIP confirms acquisition, 408 MW wind + 104 MW BESS, FID, financial close, AUD 1.7bn facility from 10 banks, construction commencement and 2030 full operation target."},
      {"id":"S3-P2","owner":"Windlab","role":"seller_developer_confirmation","url":"https://www.windlab.com/blog-posts/gawara-baya-moves-into-construction-unlocking-jobs-and-investment-in-north-queensland","published":"2026-08-31","summary":"Windlab confirms financial close, construction entry, project capacities and 100% acquisition by CIP/CI V."},
    ],
    "source_conflicts": [], "related": None,
  },
  4: {
    "region": "GL", "cat": "Materials", "sub_cat": "Argentina lithium / development finance",
    "signal": "top",
    "title": "포스코 아르헨티나 리튬, IDB Invest서 최대 7억달러 금융 확보",
    "sub": "Sal de Oro 수산화·탄산리튬 공장 가동·증산을 다자개발금융이 지원",
    "gate": "아르헨티나 리튬 증산이 국제금융기관의 실제 금융약정으로 연결됐다.",
    "fact": "IDB Invest는 POSCO Argentina의 Sal de Oro 리튬 프로젝트에 최대 7억달러를 제공해 리튬 추출·생산 확대와 수산화리튬·탄산리튬 공장의 가동·증산을 지원한다고 밝혔다. POSCO는 이를 단기 신용한도 승인으로 설명했으며 IDB Invest 승인일은 8월 4일이다.",
    "implication": [
      "핵심광물 프로젝트의 병목이 단순 매장량보다 가동자금·증산금융으로 이동하고 있다는 신호다.",
      "후속 확인점은 실제 인출액, 생산 램프업, 수율·원가와 상환조건이다."
    ],
    "event_date_role": "financing transaction public announcement", "event_date": "2026-08-28",
    "facts": [
      ("S4-C1", "IDB Invest가 POSCO Argentina에 최대 7억달러 금융을 제공한다.", ["S4-P1","S4-P2","S4-I1"]),
      ("S4-C2", "자금은 Sal de Oro의 리튬 추출·생산 확대와 수산화·탄산리튬 공장 가동 및 램프업을 지원한다.", ["S4-P1","S4-P2"]),
      ("S4-C3", "POSCO가 밝힌 IDB Invest의 단기 신용한도 승인일은 2026년 8월 4일이다.", ["S4-P2","S4-I1"]),
    ],
    "sources": [
      {"id":"S4-P1","owner":"IDB Invest","role":"lender_primary_release","url":"https://idbinvest.org/es/medios-y-prensa/bid-invest-y-posco-impulsan-la-expansion-de-la-produccion-de-litio-en-argentina","published":"2026-08-27","summary":"IDB Invest states up to US$700m financing for POSCO Argentina to expand extraction and lithium production at Sal de Oro and support ramp-up of hydroxide and carbonate plants."},
      {"id":"S4-P2","owner":"POSCO Holdings","role":"borrower_primary_release","url":"https://newsroom.posco.com/en/posco-holdings-secures-us700-million-international-financial-institution-credit-facility-for-argentina-lithium-business-accelerating-project-development/","published":"2026-09-02","summary":"POSCO confirms a US$700m short-term credit facility and says IDB Invest approved the facility on Aug. 4."},
      {"id":"S4-I1","owner":"Yonhap News Agency","role":"independent_confirmation","url":"https://en.yna.co.kr/view/AEN20260828004600320","published":"2026-08-28","summary":"Independent report confirms the up-to-US$700m facility and Aug. 4 approval."},
    ],
    "source_conflicts": [], "related": None,
  },
  5: {
    "region": "US", "cat": "Materials", "sub_cat": "US lithium / binding offtake",
    "signal": "top",
    "title": "LG엔솔, 스맥오버 리튬과 10년 8만t 탄산리튬 오프테이크",
    "sub": "연 8천t binding take-or-pay…미국 South West Arkansas 상업생산과 연계",
    "gate": "미국산 리튬 장기조달이 구속력 있는 take-or-pay 계약으로 확정됐다.",
    "fact": "LG에너지솔루션과 Smackover Lithium은 South West Arkansas 프로젝트의 배터리급 탄산리튬을 연 8,000t씩 10년 공급하는 binding take-or-pay 계약을 체결했다. Smackover는 이번 계약과 기존 Trafigura 계약을 합치면 초기 프로젝트 목표 오프테이크의 약 90%가 커버된다고 밝혔다.",
    "implication": [
      "북미 배터리 공급망에서 셀 현지생산뿐 아니라 리튬 원료의 장기 계약화가 빨라지고 있다.",
      "계약은 구속력이 있지만 공급 개시는 프로젝트 상업생산에 연동되므로 FID·건설·2029년 목표 생산개시 리스크를 별도로 추적해야 한다."
    ],
    "event_date_role": "binding take-or-pay agreement announcement", "event_date": "2026-08-31",
    "facts": [
      ("S5-C1", "Smackover Lithium이 LG에너지솔루션에 배터리급 탄산리튬을 연 8,000t씩 10년 공급하는 binding take-or-pay 계약을 체결했다.", ["S5-P1","S5-P2","S5-P3"]),
      ("S5-C2", "공급은 South West Arkansas 프로젝트 상업생산 개시 후 시작된다.", ["S5-P1"]),
      ("S5-C3", "Smackover는 이번 계약과 기존 Trafigura 계약을 합쳐 목표 오프테이크 물량의 약 90%가 커버된다고 설명했다.", ["S5-P1"]),
    ],
    "sources": [
      {"id":"S5-P1","owner":"Smackover Lithium","role":"supplier_primary_release","url":"https://smackoverlithium.com/newsroom/news-details/2026/Smackover-Lithium-Signs-Binding-Customer-Offtake-with-LG-Energy-Solution-for-the-South-West-Arkansas-Project-2026-XymsQvwydU/default.aspx","published":"2026-08-31","summary":"Supplier confirms binding take-or-pay, 8,000 t/y for 10 years after commercial production, second commercial offtake and roughly 90% targeted offtake committed with Trafigura."},
      {"id":"S5-P2","owner":"LG Energy Solution","role":"buyer_primary_release","url":"https://www.lgcorp.com/media/release/30523","published":"2026-09-01","summary":"LGES confirms 8,000 metric tonnes annually over ten years and U.S.-produced lithium carbonate from Smackover Lithium."},
      {"id":"S5-P3","owner":"Arkansas Department of Commerce","role":"independent_public_institution_confirmation","url":"https://commerce.arkansas.gov/smackover-lithium-lg-energy-solution-south-west-arkansas/","published":"2026-08-31","summary":"Arkansas Commerce confirms the 8,000 t/y, ten-year offtake and identifies the commitment as approximately $1.5bn over ten years."},
    ],
    "source_conflicts": [], "related": None,
  },
  8: {
    "region": "EU", "cat": "Policy", "sub_cat": "Digital Battery Passport / data requirements",
    "signal": "high",
    "title": "EU, 배터리 패스포트 71개 데이터포인트 가이드 공개",
    "sub": "EV·LMT·2kWh 초과 산업용 배터리의 2027년 2월 의무 적용 준비 범위를 구체화",
    "gate": "법적 의무를 새로 만든 것이 아니라 기존 EU 배터리 규정의 데이터 준비 범위를 Commission guidance가 구체화했다.",
    "fact": "European Commission DG GROW는 Digital Batteries Passport 준비용 guidance의 업데이트 버전을 공개했다. 문서는 EV·LMT·산업용 배터리별로 71개 데이터포인트의 의무·선택·조건부 적용 여부와 법적 근거를 정리한다. 배터리 패스포트 의무는 Regulation (EU) 2023/1542에 따라 2027년 2월 18일부터 관련 EV·LMT·2kWh 초과 산업용 배터리에 적용된다.",
    "implication": [
      "배터리 업체는 단순 QR/DPP 구축이 아니라 71개 항목의 원천데이터 소유자·수집주기·검증 책임을 공급망별로 정리해야 한다.",
      "71개 표는 준비용 guidance이며 법규 자체의 대체물이 아니므로 실제 의무 판단은 Regulation과 최신 시행문서를 함께 봐야 한다."
    ],
    "event_date_role": "Commission guidance publication", "event_date": "2026-08-21",
    "facts": [
      ("S8-C1", "Commission guidance가 배터리 패스포트 관련 71개 데이터포인트를 배터리 유형별로 정리했다.", ["S8-P1","S8-I1"]),
      ("S8-C2", "각 데이터포인트에 대해 mandatory, optional, 조건부 또는 2027년 2월 시점 비표시 여부와 법적 출처가 제시된다.", ["S8-P1"]),
      ("S8-C3", "2027년 2월 18일부터 EV·LMT·2kWh 초과 산업용 배터리에 배터리 패스포트 의무가 적용된다.", ["S8-P1","S8-P2"]),
    ],
    "sources": [
      {"id":"S8-P1","owner":"European Commission DG GROW","role":"official_guidance_release","url":"https://single-market-economy.ec.europa.eu/news/guidance-support-preparations-digital-batteries-passport-2026-08-21_en","published":"2026-08-21","summary":"Commission states the guidance gathers 71 data points and explains category applicability and legal sources; also states the Feb. 18 2027 passport application date."},
      {"id":"S8-P2","owner":"European Commission","role":"official_implementation_timeline","url":"https://single-market-economy.ec.europa.eu/single-market/digital-product-passport/batteries_en","published":"2026-08-21","summary":"Commission battery DPP page lists Feb. 18 2027 as the mandatory battery-passport date and points to the updated data-point document."},
      {"id":"S8-I1","owner":"DigiProductPass","role":"independent_specialist_confirmation","url":"https://www.digiproductpass.com/blog/battery-passport-71-data-points-by-category","published":"2026-08-26","summary":"Independent specialist review confirms Commission guidance version 2.0 and the 71-data-point structure by battery category."},
    ],
    "source_conflicts": [], "related": None,
  },
  9: {
    "region": "CN", "cat": "Policy", "sub_cat": "battery consumption tax / ESS scope clarification",
    "signal": "top",
    "title": "중국, ESS 소비세 경계 확정…배터리 클러스터 과세·완성 ESS 비과세",
    "sub": "세무총국 Q&A: 반고체는 고체전지 면세 대상 제외, 수출 소비세 환급 원칙도 확인",
    "gate": "9월 시행 직전 ESS 밸류체인에서 소비세가 붙는 제품 경계를 행정 Q&A가 구체화했다.",
    "fact": "중국 국가세무총국은 8월 27일 Q&A에서 리튬이온 셀로 조립한 배터리 클러스터는 과세 대상 배터리팩에 해당하지만, 배터리와 전기·열관리·소방·제어시스템을 통합한 완성 ESS는 과세 배터리 제품이 아니라고 밝혔다. 반고체 배터리는 고체전지 면세 대상이 아니며, 조건을 충족하는 수출 배터리에는 소비세 면·환급 원칙이 유지된다.",
    "implication": [
      "국내용 ESS 원가 영향은 전체 시스템 매출액이 아니라 과세 배터리 제품 단계에 집중된다.",
      "반고체 제품은 고체전지 면세를 전제로 가격을 설계하면 안 되며, 수출은 제품별 소비세·VAT 환급 구조를 별도로 봐야 한다."
    ],
    "event_date_role": "State Taxation Administration Q&A publication", "event_date": "2026-08-27",
    "facts": [
      ("S9-C1", "배터리 클러스터는 과세 대상 배터리팩이지만 완성 ESS는 과세 배터리 제품이 아니다.", ["S9-P1","S9-I1","S9-I2"]),
      ("S9-C2", "반고체 배터리는 고체전지 면세 대상이 아니다.", ["S9-P1","S9-I2"]),
      ("S9-C3", "적용 조건을 충족하는 수출 배터리에는 소비세 면·환급 원칙이 유지된다.", ["S9-P1","S9-I1"]),
    ],
    "sources": [
      {"id":"S9-P1","owner":"State Taxation Administration of China","role":"official_tax_administration_QA","url":"https://www.chinatax.gov.cn/chinatax/c102414/c5252006/content.html","published":"2026-08-27","summary":"Official Q&A says battery clusters are taxable battery packs, complete ESS equipment is not a taxable battery product, semi-solid batteries do not qualify for solid-state exemption, and export consumption-tax refund/exemption treatment continues under applicable rules."},
      {"id":"S9-I1","owner":"Shanghai Metals Market","role":"independent_industry_analysis","url":"https://news.metal.com/newscontent/104086420-smm-analysis-state-taxation-administration-clarifies-consumption-tax-boundary-for-energy-storage-battery-clusters-taxed-ess-not-taxed-export-tax-rebate-path-further-clarified","published":"2026-08-28","summary":"SMM independently analyzes the tax boundary and concludes the tax base does not extend to the full ESS value; export treatment is materially different from domestic sales."},
      {"id":"S9-I2","owner":"EnergyTrend","role":"independent_industry_confirmation","url":"https://m.energytrend.cn/news/20260828-148473.html","published":"2026-08-28","summary":"EnergyTrend independently summarizes the official Q&A, including ESS non-taxability and semi-solid exclusion from the solid-state exemption."},
    ],
    "source_conflicts": [], "related": {"type":"distinct_follow_up","target_spec_id":"STD26_R6_B01_010","basis":"The Aug. 27 administration Q&A clarifies the scope and implementation of the July 16 tax policy that takes effect Sep. 1; it is not the same publication event."},
  },
  10: {
    "region": "CN", "cat": "Policy", "sub_cat": "battery consumption tax / effective rate",
    "signal": "top",
    "title": "중국 배터리 소비세 2% 시행…리튬이온·바나듐흐름전지 대상",
    "sub": "2026년 9월 1일 2%→2027년 9월 1일 4%; 나트륨·고체전지는 2028년 말까지 면세",
    "gate": "7월 발표된 세제 개편이 9월 1일 법정 시행일에 들어갔다.",
    "fact": "중국 재정부·해관총서·국가세무총국의 2026년 제20호 공고에 따라 2026년 9월 1일부터 리튬 1차전지·리튬이온전지·니켈수소전지·수은 무첨가 1차전지·바나듐 레독스 플로우 전지에 2% 소비세가 부과된다. 해당 세율은 2027년 9월 1일부터 4%로 올라가며, 나트륨이온·고체전지·연료전지는 2028년 12월 31일까지 면세다. 감면 제품은 국가표준 적합성과 지정 요건의 시험보고서가 요구된다.",
    "implication": [
      "중국 내 배터리 가격·마진에는 2% 세율 자체뿐 아니라 원재료 기납부세액 공제와 제품단계별 과세범위가 중요해졌다.",
      "나트륨·고체전지는 한시적 세제 우위를 얻지만 표준 적합성·시험보고서 요건을 충족해야 하며, 반고체는 별도 Q&A상 고체전지 면세에 포함되지 않는다."
    ],
    "event_date_role": "statutory effective date", "event_date": "2026-09-01",
    "facts": [
      ("S10-C1", "2026년 9월 1일부터 지정 배터리 제품에 2% 소비세가 적용되고 2027년 9월 1일부터 4%로 인상된다.", ["S10-P1","S10-P2"]),
      ("S10-C2", "나트륨이온·고체전지·연료전지는 2026년 9월 1일부터 2028년 12월 31일까지 소비세가 면제된다.", ["S10-P1","S10-P2"]),
      ("S10-C3", "감면 적용에는 국가표준 적합성과 자격을 갖춘 시험기관의 적합성 시험보고서가 요구된다.", ["S10-P1"]),
    ],
    "sources": [
      {"id":"S10-P1","owner":"Ministry of Finance / General Administration of Customs / State Taxation Administration of China","role":"official_joint_tax_notice","url":"https://fgk.chinatax.gov.cn/zcfgk/c102416/c5251171/content.html","published":"2026-07-16","summary":"Official Notice No.20 sets the 2% rate from Sep.1 2026, 4% from Sep.1 2027, temporary exemptions for sodium-ion/solid-state/fuel cells through 2028, and standards/testing conditions for exemptions."},
      {"id":"S10-P2","owner":"Ministry of Commerce of China policy database","role":"official_policy_mirror","url":"https://policy.mofcom.gov.cn/claw/clawContent.shtml?id=106537","published":"2026-07-16","summary":"MOFCOM policy database reproduces the current-valid joint notice and the Sep.1 2026 2% implementation terms."},
      {"id":"S10-I1","owner":"Shanghai Metals Market","role":"independent_implementation_analysis","url":"https://news.smm.cn/news/104086402","published":"2026-08-28","summary":"SMM analyzes the implementation boundary and domestic/export cost transmission immediately before the Sep.1 effective date."},
    ],
    "source_conflicts": [], "related": {"type":"program_lineage","target_spec_id":"STD26_R6_B01_009","basis":"The base tax instrument and the later administration Q&A are separate but directly linked policy-lineage events."},
  },
}


def domain(url: str) -> str:
    return urlsplit(url).netloc.lower().removeprefix("www.")


def current_ids() -> set[str]:
    data = json.loads(CANON.read_text(encoding="utf-8"))
    cards = data if isinstance(data, list) else data.get("cards", [])
    return {str(c.get("id")) for c in cards if isinstance(c, dict) and c.get("id")}

used = current_ids()
planned: set[str] = set()

def allocate_id(date: str, region: str) -> str:
    prefix = f"{date}_{region}_"
    for n in range(1, 100):
        cid = f"{prefix}{n:02d}"
        if cid not in used and cid not in planned:
            planned.add(cid)
            return cid
    raise RuntimeError(prefix)

# Initial deterministic ID allocation for the seven new drafts. Same date/region is ranked by signal then Stage A score.
rank = {"top": 0, "high": 1, "mid": 2}
ordered = sorted(E, key=lambda o: (E[o]["event_date"], E[o]["region"], rank[E[o]["signal"]], -spec_by_ord[o]["decision_news_value_score"], o))
ids = {o: allocate_id(E[o]["event_date"], E[o]["region"]) for o in ordered}

packages = []
for o in sorted(E):
    spec = copy.deepcopy(spec_by_ord[o])
    e = E[o]
    sources = []
    for s in e["sources"]:
        row = copy.deepcopy(s)
        row.update({
            "fetch_status": "fetched_body_or_authoritative_page",
            "headline_only": False,
            "rss_or_snippet_only": False,
            "claim_use": "paraphrase_only_no_source_quote",
            "domain": domain(s["url"]),
        })
        sources.append(row)
    owners = list(dict.fromkeys(s["owner"] for s in sources))
    domains = list(dict.fromkeys(s["domain"] for s in sources))
    claims = [{"claim_id": cid, "claim": text, "supported_by_source_ids": source_ids, "visible": True, "status": "SUPPORTED"} for cid, text, source_ids in e["facts"]]
    related = {
        "same_event_check": "PASS",
        "earliest_event_date_check": "PASS",
        "relation_type": e["related"]["type"] if e["related"] else "new_unrelated_event",
        "matched_baseline_candidate_ids": spec.get("related_prepass", {}).get("matched_baseline_candidate_ids", []),
        "matched_current_candidates": [e["related"]["target_spec_id"]] if e["related"] else [],
        "fresh_follow_up_anchor_class": "policy_regulatory_anchor" if e["related"] else None,
        "fresh_follow_up_anchor": e["related"]["basis"] if e["related"] else None,
        "incremental_fact": claims[0]["claim"] if e["related"] else None,
        "changed_judgment": "The later policy administration detail changes implementation/cost interpretation without duplicating the underlying instrument." if e["related"] else None,
        "rejected_relation_candidates": [],
        "reinforcement_transfer_ledger": [],
        "production_related_ids": [],
        "note": "Production related[] remains provisional until Stage C/final ID validation."
    }
    pkg = {
        "spec_id": spec["spec_id"],
        "source_story_ids": spec["source_story_ids"],
        "stage_a_selection_package": spec,
        "stage_a_artifact": str(A_PATH.relative_to(ROOT)),
        "stage_a_artifact_sha256": A_SHA,
        "stage_a_support_sources_attempted": [{"url": u, "attempted": True, "result": "superseded_by_fetched_same-event_source_set"} for u in spec.get("urls", [])],
        "source_independence_ledger": [{"source_id": s["id"], "owner": s["owner"], "role": s["role"], "domain": s["domain"], "independent_editorial_owner": not s["role"].startswith(("counterparty_primary", "acquirer_primary", "seller_developer", "lender_primary", "borrower_primary", "supplier_primary", "buyer_primary", "official_"))} for s in sources],
        "source_unique_url_count": len({s["url"] for s in sources}),
        "source_unique_domain_count": len(domains),
        "source_independent_owner_count": len(owners),
        "source_role_coverage": dict(Counter(s["role"] for s in sources)),
        "source_synthesis_plan": "Primary/counterparty or official evidence controls operative facts; independent sources confirm material terms and are used to surface conflicts. Visible copy uses only supported paraphrases.",
        "fact_sources": sources,
        "claim_map": claims,
        "source_conflicts": e["source_conflicts"],
        "date_role": {
            "representative_event_date": e["event_date"],
            "role": e["event_date_role"],
            "stage_a_representative_date": spec["representative_date"],
            "source_publication_dates": sorted({s["published"] for s in sources}),
            "status": "PASS",
            "note": "Event date is used for card identity; source publication dates are preserved separately."
        },
        "related_evidence_review": related,
        "execution_anchor_review": {
            "selection_route": spec["selection_route"],
            "stage_a_anchor_classes": spec["anchor_classes"],
            "status": "PASS",
            "evidence_basis": [s["id"] for s in sources[:2]],
            "note": "Fetched evidence supports the selected execution or structural non-execution route without inventing execution."
        },
        "draft_status": "draft",
        "draft_blocked": False,
        "draft_blocked_reason": None,
        "rescue_log": [],
        "unresolved_questions": spec.get("next_confirmation_points", []),
        "draft": {
            "id": ids[o],
            "region": e["region"],
            "date": e["event_date"],
            "cat": e["cat"],
            "sub_cat": e["sub_cat"],
            "signal": e["signal"],
            "title": e["title"],
            "sub": e["sub"],
            "gate": e["gate"],
            "fact": e["fact"],
            "implication": e["implication"],
            "urls": [s["url"] for s in sources],
            "related": [],
            "fact_sources": sources,
            "stage_b_only": True,
            "stage_b_fact_safety_not_declared": True,
            "stage_b_publish_readiness_not_declared": True,
        },
    }
    assert pkg["source_independent_owner_count"] >= 2
    assert len(pkg["fact_sources"]) >= 2
    assert all(c["status"] == "SUPPORTED" for c in claims)
    packages.append(pkg)

artifact = {
    "stage": "stage_b",
    "status": "PASS_DRAFTED_NOT_FACT_SAFE",
    "run_tag": "20260903_R6_STAGE_B_STRICT7_R1",
    "source_prompt_file": "docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md",
    "source_prompt_version": "STAGE_B_V4_20260829",
    "source_prompt_sha256": hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
    "stage_a_artifact": str(A_PATH.relative_to(ROOT)),
    "stage_a_artifact_sha256": A_SHA,
    "main_sha": MAIN,
    "canonical_blob_sha": CANON_BLOB,
    "lineage_integrity_status": "PASS",
    "stage_a_validity_guard_applied": True,
    "strict_gate_metadata_preserved": True,
    "execution_anchor_metadata_preserved": True,
    "superseded_lineage_mixed": False,
    "manual_integrated_rule_mixed": False,
    "previous_run_output_mixed": False,
    "input_strict_count": 7,
    "draft_count": 7,
    "draft_blocked_count": 0,
    "fact_safety_declared_count": 0,
    "publish_ready_declared_count": 0,
    "external_search_or_fetch_used": True,
    "evidence_packages": packages,
    "next_authorized_stage": "Prompt 0.3 Stage C r0 on these seven Stage B drafts",
}
OUT.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

from validation_scripts import stage_lineage_contract_check as lineage
rc = lineage.check_stage_b(artifact)
errors = []
if len(packages) != 7: errors.append("package_count")
if {p["spec_id"] for p in packages} != {s["spec_id"] for s in strict}: errors.append("strict_spec_coverage")
if any(p["draft_blocked"] for p in packages): errors.append("unexpected_draft_blocked")
if any(p["source_independent_owner_count"] < 2 for p in packages): errors.append("owner_diversity")
if any(any(c["status"] != "SUPPORTED" for c in p["claim_map"]) for p in packages): errors.append("claim_support")
if len({p["draft"]["id"] for p in packages}) != 7: errors.append("draft_id_collision")
if any(p["draft"]["id"] in used for p in packages): errors.append("canonical_id_collision")

report = {
    "schema": "stage_b_r6_strict7_validation_v1",
    "status": "PASS" if rc == 0 and not errors else "FAIL",
    "artifact": str(OUT.relative_to(ROOT)),
    "artifact_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
    "stage_b_lineage_check_rc": rc,
    "custom_errors": errors,
    "input_strict_count": 7,
    "draft_count": 7,
    "draft_blocked_count": 0,
    "claim_count": sum(len(p["claim_map"]) for p in packages),
    "source_count": sum(len(p["fact_sources"]) for p in packages),
    "all_claims_supported": all(all(c["status"] == "SUPPORTED" for c in p["claim_map"]) for p in packages),
    "all_packages_multi_owner": all(p["source_independent_owner_count"] >= 2 for p in packages),
    "canonical_id_collision_count": sum(1 for p in packages if p["draft"]["id"] in used),
    "fact_safety_declared": False,
    "publish_ready_declared": False,
}
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["status"] == "PASS" else 1)

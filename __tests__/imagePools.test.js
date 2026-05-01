/**
 * 이미지 시스템 회귀 테스트 (vitest)
 *
 * 다음 sweep에서 풀 추가/매처 보강할 때 부작용 즉시 감지하기 위한 안전망.
 *
 * 실행:
 *   npm test
 *   npm run test:watch
 */
import { describe, it, expect } from 'vitest';
import {
  // imageCategoryFor와 IMAGE_POOLS는 module 내부지만 helper export로 충분히 검증 가능
  assignCardCoverImages,
} from '../src/story/StoryNewsItem.jsx';

describe('assignCardCoverImages: 같은 페이지 내 dedup 보장', () => {
  it('카드 4개 모두 다른 이미지를 받아야 한다 (Home 시나리오)', () => {
    const cards = [
      { id: 'c1', title: 'IRA FEOC 발효', region: 'NA' },
      { id: 'c2', title: 'EU Battery Regulation 시행', region: 'EU' },
      { id: 'c3', title: 'CATL 가격 인하', region: 'CN' },
      { id: 'c4', title: 'LG에너지솔루션 실적', region: 'KR' },
    ];
    const covers = assignCardCoverImages(cards);
    expect(covers).toHaveLength(4);
    expect(new Set(covers).size).toBe(4);
  });

  it('같은 카테고리 카드 8개도 unique 보장 (POLICY 풀 15개)', () => {
    const cards = Array.from({ length: 8 }, (_, i) => ({
      id: `policy-${i}`,
      title: `IRA 정책 ${i}`,
      region: 'NA',
    }));
    const covers = assignCardCoverImages(cards);
    expect(covers).toHaveLength(8);
    expect(new Set(covers).size).toBe(8);
  });

  it('같은 카테고리 카드 30개 — 풀(15) 부족 시 DEFAULT(15)로 fallback해서 unique 30개 가능', () => {
    const cards = Array.from({ length: 30 }, (_, i) => ({
      id: `policy-${i}`,
      title: `IRA 정책 ${i}`,
      region: 'NA',
    }));
    const covers = assignCardCoverImages(cards);
    expect(covers).toHaveLength(30);
    // POLICY(15) + DEFAULT(15) = 30 → 모두 unique 가능
    expect(new Set(covers).size).toBe(30);
  });

  it('같은 카테고리 31개 이상 — 풀 부족 시 collision 허용 (graceful degradation)', () => {
    const cards = Array.from({ length: 50 }, (_, i) => ({
      id: `policy-${i}`,
      title: `IRA 정책 ${i}`,
      region: 'NA',
    }));
    const covers = assignCardCoverImages(cards);
    expect(covers).toHaveLength(50);
    // 풀 부족 → 일부 collision 허용. 처음 30개는 unique 보장.
    expect(new Set(covers.slice(0, 30)).size).toBe(30);
  });

  it('빈 배열 처리', () => {
    expect(assignCardCoverImages([])).toEqual([]);
    expect(assignCardCoverImages(null)).toEqual([]);
    expect(assignCardCoverImages(undefined)).toEqual([]);
  });

  it('alreadyUsed 옵션 — 외부 사용 이미지를 회피한다', () => {
    const cards = [
      { id: 'c1', title: 'IRA FEOC', region: 'NA' },
      { id: 'c2', title: 'EU Battery', region: 'EU' },
    ];
    const firstCovers = assignCardCoverImages(cards);

    // 첫 번째 결과를 alreadyUsed로 넘기면 다른 이미지 받아야 함
    const secondCovers = assignCardCoverImages(cards, {
      alreadyUsed: firstCovers,
    });
    secondCovers.forEach((url) => {
      expect(firstCovers).not.toContain(url);
    });
  });

  it('같은 카드는 안정적으로 같은 이미지를 받는다 (stable seed)', () => {
    const card = { id: 'stable-test', title: 'Test card', region: 'NA' };
    const result1 = assignCardCoverImages([card])[0];
    const result2 = assignCardCoverImages([card])[0];
    expect(result1).toBe(result2);
  });
});

describe('카테고리 매처 회귀 (imageCategoryFor 키워드)', () => {
  // assignCardCoverImages 결과가 카테고리 풀에서 나오는지로 매처 동작 간접 검증
  // (imageCategoryFor 자체는 export 안 됐지만 결과로 검증 가능)

  // 각 카테고리 풀의 첫 번째 URL을 anchor로 사용해서 매처 동작 확인
  // 풀 변경 시 이 anchor를 업데이트하면 됨
  const CATEGORY_ANCHORS = {
    POLICY: 'photo-1589829085413-56de8ae18c73',
    AVIATION: 'photo-1436491865332-7a61a109cc05', // KR-010, JP-011, CN-016 cluster
    RECYCLE: 'photo-1532996122724-e3c354a0b15b',
    MINING: 'photo-1578319439584-104c94d37305',
  };

  it('항공 키워드 → AVIATION 풀 (KR-010, JP-011 cluster)', () => {
    const cases = [
      { id: 'kr-010', title: 'ICAO 기내 보조배터리 규제', region: 'KR' },
      { id: 'jp-011', title: 'MLIT 항공기 모바일배터리', region: 'JP' },
      { id: 'cn-016', title: 'GB 47372 파워뱅크 강제표준', region: 'CN' },
    ];
    cases.forEach((card) => {
      const cover = assignCardCoverImages([card])[0];
      expect(cover).toContain(CATEGORY_ANCHORS.AVIATION);
    });
  });

  it('Critical Minerals 키워드 → MINING 풀', () => {
    const card = {
      id: 'na-012',
      title: 'U.S.-Japan Critical Minerals Action Plan',
      region: 'NA',
    };
    const cover = assignCardCoverImages([card])[0];
    expect(cover).toContain(CATEGORY_ANCHORS.MINING);
  });

  it('USMCA / Section 232 / IEEPA → POLICY 풀', () => {
    const cases = [
      { id: 'na-014', title: 'USMCA 6년 검토', region: 'NA' },
      { id: 'na-015', title: 'BIS Section 232 critical minerals', region: 'NA' },
      // IEEPA는 단독으로 POLICY로 가야 함
      { id: 'na-003', title: 'IEEPA 관세 SCOTUS 위헌 판결', region: 'NA' },
    ];
    cases.forEach((card) => {
      const cover = assignCardCoverImages([card])[0];
      expect(cover).toContain(CATEGORY_ANCHORS.POLICY);
    });
  });

  it('Article 11 / 분리·교체 / removability → RECYCLE 풀', () => {
    const cases = [
      { id: 'eu-016', title: 'EU 휴대용 배터리 분리·교체 의무 면제', region: 'EU' },
      { id: 'eu-016b', title: 'Article 11 위임행위 의견수렴', region: 'EU' },
    ];
    cases.forEach((card) => {
      const cover = assignCardCoverImages([card])[0];
      expect(cover).toContain(CATEGORY_ANCHORS.RECYCLE);
    });
  });
});

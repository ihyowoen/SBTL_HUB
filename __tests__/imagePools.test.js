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
  assignCardCoverImages,
  imageCategoryFor,
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

  it('3단계 폴백 레이어도 앞선 이미지와 겹치지 않게 배정한다', () => {
    const cards = [
      { id: 'f1', title: 'Greenbushes lithium mine earnings', region: 'GL' },
      { id: 'f2', title: 'EU battery policy update', region: 'EU' },
      { id: 'f3', title: 'ESS grid project', region: 'US' },
      { id: 'f4', title: 'Battery factory ramp-up', region: 'KR' },
    ];
    const used = new Set();
    const all = [];
    for (let depth = 0; depth < 3; depth += 1) {
      const layer = assignCardCoverImages(cards, { alreadyUsed: used });
      layer.forEach((url) => { used.add(url); all.push(url); });
    }
    expect(all).toHaveLength(12);
    expect(new Set(all).size).toBe(12);
  });
});

describe('카테고리 매처 회귀 (imageCategoryFor 키워드)', () => {
  it('항공 키워드 → AVIATION (KR-010, JP-011, CN-016 cluster)', () => {
    const cases = [
      { id: 'kr-010', title: 'ICAO 기내 보조배터리 규제', region: 'KR' },
      { id: 'jp-011', title: 'MLIT 항공기 모바일배터리', region: 'JP' },
      { id: 'cn-016', title: 'GB 47372 파워뱅크 강제표준', region: 'CN' },
    ];
    cases.forEach((card) => expect(imageCategoryFor(card)).toBe('AVIATION'));
  });

  it('Critical Minerals 키워드 → MINING', () => {
    expect(imageCategoryFor({
      id: 'na-012',
      title: 'U.S.-Japan Critical Minerals Action Plan',
      region: 'NA',
    })).toBe('MINING');
  });

  it('USMCA / Section 232 / IEEPA → POLICY', () => {
    const cases = [
      { id: 'na-014', title: 'USMCA 6년 검토', region: 'NA' },
      { id: 'na-015', title: 'BIS Section 232 조치', region: 'NA' },
      { id: 'na-003', title: 'IEEPA 관세 SCOTUS 위헌 판결', region: 'NA' },
    ];
    cases.forEach((card) => expect(imageCategoryFor(card)).toBe('POLICY'));
  });

  it('Article 11 / 분리·교체 / removability → RECYCLE', () => {
    const cases = [
      { id: 'eu-016', title: 'EU 휴대용 배터리 분리·교체 의무 면제', region: 'EU' },
      { id: 'eu-016b', title: 'Article 11 위임행위 의견수렴', region: 'EU' },
      { id: 'eu-016c', title: 'Portable battery removability guidance', region: 'EU' },
    ];
    cases.forEach((card) => expect(imageCategoryFor(card)).toBe('RECYCLE'));
  });
});

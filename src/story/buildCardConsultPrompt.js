import { normalizeCard } from './normalizeCard';

export function buildCardConsultPrompt(card) {
  const c = normalizeCard(card);
  const parts = [
    '[카드 상담 요청]',
    `제목: ${c.title || '-'}`,
    `무슨 일이야: ${c.fact || '-'}`,
    `그래서 어떻게 돼: ${c.gate || '-'}`,
    `강차장 코멘트: ${c.implicationText || '-'}`,
  ];

  if (c.primaryUrl) parts.push(`원문: ${c.primaryUrl}`);
  parts.push('');
  parts.push('이 카드의 핵심, 실무 영향, 다음 체크포인트를 강차장 톤으로 설명해줘.');

  return parts.join('\n');
}

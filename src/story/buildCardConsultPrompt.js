import { normalizeCard } from './normalizeCard';

export function buildCardConsultPrompt(card) {
  const c = normalizeCard(card);

  const lines = [
    '[카드상담]',
    '이 카드 기준으로만 설명해줘. 무슨 일인지, 왜 중요한지, 다음 체크포인트 2개만 말해줘.',
    `카드 제목: ${c.title || '-'}`,
  ];

  if (c.primaryUrl) lines.push(`카드 URL: ${c.primaryUrl}`);
  return lines.join('\n');
}

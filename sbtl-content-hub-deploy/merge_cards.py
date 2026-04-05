"""
SBTL 카드 병합 스크립트
========================
사용법:
  python merge_cards.py cards_w6.json

이렇게 하면:
1. public/data/cards.json (기존) + cards_w6.json (신규) 병합
2. 중복 제거 + 날짜순 정렬
3. public/data/cards.json 에 저장
4. GitHub에 올리면 끝!
"""

import json, re, sys, os

def build_compact(c):
    """원본 카드를 compact 포맷으로 변환"""
    sig = c.get('signal','mid').lower()[0]
    urls = c.get('urls', [])
    url = urls[0] if urls else ''
    fact = c.get('fact','')
    source = ''
    m = re.match(r'^(.+?)에 따르면', fact)
    if m:
        source = m.group(1).strip()[:30]
    
    kws = set()
    for field in ['title','gate','sub']:
        text = c.get(field, '')
        kws.update(re.findall(r'[가-힣]{2,}', text))
        kws.update(w.lower() for w in re.findall(r'[A-Za-z][A-Za-z0-9]{1,}', text))
    
    return {
        's': sig,
        'r': c.get('region',''),
        'd': c.get('date',''),
        'T': c.get('title',''),
        'sub': c.get('sub','')[:100],
        'src': source,
        'url': url,
        'k': c.get('keys', list(kws))[:10],
        'g': c.get('gate','')[:120] if sig in ('t','h') else c.get('gate','')[:60],
    }

def main():
    if len(sys.argv) < 2:
        print("사용법: python merge_cards.py <새 카드 파일>")
        print("예시: python merge_cards.py cards_w6.json")
        sys.exit(1)
    
    new_file = sys.argv[1]
    existing_file = "public/data/cards.json"
    
    # 기존 카드 로드
    existing_cards = []
    if os.path.exists(existing_file):
        with open(existing_file, encoding='utf-8') as f:
            data = json.load(f)
            existing_cards = data.get('cards', data) if isinstance(data, dict) else data
        print(f"기존: {len(existing_cards)}건")
    else:
        print("기존 cards.json 없음 — 새로 생성합니다")
    
    # 새 카드 로드
    with open(new_file, encoding='utf-8') as f:
        new_data = json.load(f)
    new_cards = new_data if isinstance(new_data, list) else new_data.get('cards', [])
    print(f"신규: {len(new_cards)}건")
    
    # 신규 카드를 compact 포맷으로 변환
    new_compact = []
    for c in new_cards:
        if 'T' in c:  # 이미 compact 포맷
            new_compact.append(c)
        else:  # 원본 포맷
            if 'signal' in c:
                c['signal'] = c['signal'].lower()
            new_compact.append(build_compact(c))
    
    # 중복 제거 (제목 앞 35자 기준)
    seen = set()
    merged = []
    for c in existing_cards:
        key = c.get('T','')[:35].lower().replace(" ","")
        if key not in seen:
            seen.add(key)
            merged.append(c)
    
    added = 0
    for c in new_compact:
        key = c.get('T','')[:35].lower().replace(" ","")
        if key not in seen:
            seen.add(key)
            merged.append(c)
            added += 1
    
    # 날짜순 정렬 (최신 먼저)
    merged.sort(key=lambda c: c.get('d',''), reverse=True)
    
    # 저장
    output = {"updated": new_cards[0].get('date', '') if new_cards else '', "total": len(merged), "cards": merged}
    with open(existing_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
    
    print(f"\n✅ 병합 완료!")
    print(f"   추가: {added}건")
    print(f"   중복: {len(new_compact) - added}건")
    print(f"   합계: {len(merged)}건")
    print(f"   저장: {existing_file}")
    print(f"\n👉 이제 GitHub에 {existing_file} 올리면 끝!")

if __name__ == "__main__":
    main()

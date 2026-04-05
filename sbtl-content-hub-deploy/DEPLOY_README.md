# SBTL Content Hub — Policy Tracker 배포 가이드

## 파일 구조
```
public/
├── data/
│   └── tracker_data.json    ← 50건 트래커 데이터 (83KB)
└── tracker.html             ← 독립 실행 인터랙티브 HTML (85KB)

tools/
├── render_tracker.js        ← JSON → HTML 재생성 스크립트
└── SKILL.md                 ← Claude 업데이트 프로토콜
```

## 배포 방법

### 방법 1: 독립 HTML 페이지 (가장 간단)
1. `public/tracker.html`을 GitHub `sbtl-content-hub-deploy/public/` 에 복사
2. git push → Vercel 자동 배포
3. `https://sbtl-hub.vercel.app/tracker.html` 로 접근 가능
4. Content Hub 내 탭에서 iframe 또는 링크로 연결

### 방법 2: JSON 데이터 로드 (React 통합)
1. `public/data/tracker_data.json`을 GitHub `public/data/`에 복사
2. React 컴포넌트에서 fetch로 로드:
```jsx
const [trackerData, setTrackerData] = useState(null);
useEffect(() => {
  fetch('/data/tracker_data.json')
    .then(r => r.json())
    .then(d => setTrackerData(d));
}, []);
```

## 데이터 업데이트 워크플로우
1. Claude.ai에서 "트래커 업데이트" 실행
2. 업데이트된 `tracker_data.json` 다운로드
3. GitHub `public/data/tracker_data.json` 덮어쓰기
4. (선택) 로컬에서 `node tools/render_tracker.js` → HTML 재생성
5. git push → Vercel 자동 배포

## 현재 데이터 현황 (2026.04.05)
- **총 50건** (NA 9 · EU 13 · CN 10 · KR 9 · JP 9)
- ACTIVE 23 · UPCOMING 12 · WATCH 11 · DONE 4
- 각 아이템: 기본정보 + 검증(lastChecked) + 팁(tip) + 디테일(detail, collapse/expand)

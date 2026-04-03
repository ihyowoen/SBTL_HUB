# SBTL 콘텐츠 허브

Battery · ESS · EV Supply Chain Intelligence

## 로컬 실행

```bash
npm install
npm run dev
```

브라우저에서 http://localhost:5173 열기

## Vercel 배포 (3단계)

### 1단계: GitHub에 올리기
1. github.com에서 새 저장소 생성 (예: sbtl-hub)
2. 이 폴더를 올리기:
```bash
git init
git add .
git commit -m "SBTL Content Hub v1"
git remote add origin https://github.com/YOUR_USERNAME/sbtl-hub.git
git push -u origin main
```

### 2단계: Vercel 연결
1. vercel.com 가입 (GitHub 계정으로 로그인)
2. "New Project" 클릭
3. 방금 만든 GitHub 저장소 선택
4. "Deploy" 클릭 — 끝!

### 3단계: 카톡 공유
배포 완료되면 URL이 나옴 (예: sbtl-hub.vercel.app)
이 링크를 카톡으로 공유하면 됨!

## 홈 화면에 앱처럼 설치
1. 모바일 크롬/사파리에서 URL 열기
2. 공유 버튼 → "홈 화면에 추가"
3. 앱처럼 아이콘이 생김!

## 구조
```
sbtl-hub/
├── index.html          ← HTML 진입점
├── package.json        ← 의존성
├── vite.config.js      ← 빌드 설정
├── public/
│   └── manifest.json   ← PWA 설정
└── src/
    ├── main.jsx        ← React 진입점
    └── App.jsx         ← 앱 전체 (222KB, 카드 DB 포함)
```

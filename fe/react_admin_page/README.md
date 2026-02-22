Supabase를 활용한 가구 중고거래 플랫폼의 관리자 페이지입니다. 모바일 최적화된 UI로 가구 관리와 고객 문의를 효율적으로 처리할 수 있습니다.

## 🚀 주요 기능

### 가구 관리
- **가구 목록 조회**: 페이지네이션과 필터링 지원
- **상세 정보 보기**: 가구의 모든 정보를 한눈에 확인
- **정보 수정**: 가구 정보를 실시간으로 수정
- **판매 상태 관리**: 판매중/판매완료 상태 변경
- **가구 삭제**: 불필요한 가구 정보 삭제

### 문의 관리
- **문의 목록 조회**: 처리 상태별 필터링 지원
- **문의 상세 보기**: 문의 내용과 첨부파일 확인
- **상태 관리**: 처리 대기/처리 중/처리 완료 상태 변경
- **첨부파일 다운로드**: 고객이 업로드한 파일 다운로드
- **이메일 답장**: 원클릭 이메일 답장 기능

### 대시보드
- **통계 정보**: 전체 가구 수, 판매 완료 수, 문의 수 등
- **빠른 접근**: 주요 기능으로의 빠른 이동

## 🛠️ 기술 스택

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router DOM
- **Database**: Supabase
- **Icons**: Lucide React
- **Date Handling**: date-fns

## 📱 모바일 최적화

- 모바일 화면 크기(375px) 기준으로 최적화
- 터치 친화적인 UI/UX
- 반응형 네비게이션
- 모바일에서도 편리한 데이터 관리

## 🚀 시작하기

### 1. 프로젝트 클론 및 의존성 설치

```bash
npm install
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 Supabase 정보를 입력하세요:

```env
VITE_SUPABASE_URL=your_supabase_url_here
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 `http://localhost:3000`으로 접속하세요.

### 4. 프로덕션 빌드

```bash
npm run build
```

## 📊 데이터베이스 구조

### furniture 테이블
- 가구 상품 정보 저장
- 이미지 URL 배열 지원
- 판매 상태 관리
- 지역별, 가격대별 필터링 지원

### contacts 테이블
- 고객 문의 정보 저장
- 처리 상태 관리 (pending, processing, completed)

### contact_attachments 테이블
- 문의 첨부파일 정보 저장
- 파일 다운로드 기능 지원

## 🎨 UI/UX 특징

- **모바일 우선 설계**: 375px 기준 최적화
- **직관적인 네비게이션**: 햄버거 메뉴와 사이드바
- **상태별 색상 구분**: 처리 상태를 색상으로 구분
- **빠른 액션**: 원클릭 상태 변경 및 이메일 답장
- **반응형 카드 레이아웃**: 정보를 깔끔하게 정리

## 📁 프로젝트 구조

```
src/
├── components/          # 재사용 가능한 컴포넌트
│   └── Layout.tsx      # 메인 레이아웃
├── lib/                # 유틸리티 및 API 함수
│   ├── supabase.ts     # Supabase 클라이언트
│   ├── furniture.ts    # 가구 관련 API
│   ├── contact.ts      # 문의 관련 API
│   └── storage.ts      # 파일 스토리지 API
├── pages/              # 페이지 컴포넌트
│   ├── Dashboard.tsx   # 대시보드
│   ├── FurnitureList.tsx    # 가구 목록
│   ├── FurnitureDetail.tsx  # 가구 상세
│   ├── ContactList.tsx      # 문의 목록
│   └── ContactDetail.tsx    # 문의 상세
├── App.tsx             # 메인 앱 컴포넌트
├── main.tsx           # 앱 진입점
└── index.css          # 글로벌 스타일
```

## 🔧 주요 기능 상세

### 필터링 및 검색
- 가구: 판매 상태, 상품 상태, 지역, 가격대별 필터링
- 문의: 처리 상태별 필터링
- 실시간 검색 기능

### 페이지네이션
- 10개씩 페이지 단위로 데이터 로딩
- 이전/다음 버튼으로 페이지 이동

### 상태 관리
- 실시간 상태 업데이트
- 상태 변경 시 즉시 UI 반영

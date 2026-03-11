# 바람난 도시 (Windy City) — AI 작업 컨텍스트 문서

> 이 문서는 AI(Claude, Cursor, Copilot 등)에게 프로젝트 전체 맥락을 전달하기 위한 텍스트 기반 명세서입니다.
> 작성일: 2026-03-11

---

## SECTION 1: 프로젝트 개요

### 서비스 정의
바람난 도시는 살사, 바차타, 스윙, 탱고 등 커플댄스 커뮤니티를 위한 지도 기반 이벤트·장소 탐색 웹 서비스다.
인스타그램, 네이버 카페, 카카오채널에 흩어진 댄스 이벤트·장소 정보를 하나의 플랫폼으로 통합하는 것이 핵심 목적이다.

- 서비스 URL: https://windycity.co.kr
- 도메인: windycity.co.kr, www.windycity.co.kr (HTTPS 적용 완료)

### 타겟 사용자
- 입문 댄서: 내 근처 학원·이벤트 탐색, 난이도 확인이 필요한 초보자
- 레귤러 댄서: 매주 소셜 파티 일정을 빠르게 확인하는 활성 댄서
- 여행 댄서: 출장·여행 중 현지 댄스 씬을 탐색하는 사용자
- 주최자·강사: 이벤트·수업을 등록하고 홍보 채널을 단일화하려는 운영자

### 핵심 가치
- 여러 채널을 뒤지지 않아도 되는 원스톱 탐색
- 지도 기반으로 "내 근처"를 직관적으로 확인
- 날짜·장르·난이도 필터로 나에게 맞는 이벤트 즉시 필터링
- 반복 이벤트(매주 정기 소셜 파티) 자동 표시

---

## SECTION 2: 인프라 및 기술 스택

### 서버 환경
- 클라우드: OCI (Oracle Cloud Infrastructure), 리전 ap-osaka-1
- 인스턴스: VM.Standard.A1.Flex (ARM64/aarch64), 4 OCPU, 24GB RAM
- OS: Ubuntu 24.04
- 퍼블릭 IP: 217.142.229.136

### 환경 분리 (동일 서버 내 dev/prod 분리)
- Dev 디렉토리: ~/windy-city-dev, 브랜치 develop, 포트 8000, DB windycity_dev, 환경변수 .env.dev
- Prod 디렉토리: ~/windy-city, 브랜치 main, 포트 8001, DB windycity, 환경변수 .env

### 웹 서버 및 서비스 관리
- Nginx: 리버스 프록시 (80/443 → uvicorn:8001), HTTP→HTTPS 리다이렉트
- HTTPS: Let's Encrypt (certbot, 자동 갱신 구성)
- systemd: windycity.service로 Prod 앱 자동 시작·재시작 관리

### 배포 방법
- Dev 실행: cd ~/windy-city-dev && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000
- Prod 배포: cd ~/windy-city && git pull && cd frontend && npm run build && sudo systemctl restart windycity
- VS Code SFTP 익스텐션으로 로컬 편집 즉시 서버 반영 (uploadOnSave: true)

### 백엔드 스택
- 프레임워크: Python FastAPI
- ORM: SQLAlchemy
- DB: MariaDB
- 인증: JWT (python-jose) + bcrypt 4.0.1 (passlib)
- 이메일: Gmail SMTP (smtplib)
- 마이그레이션: alembic 미사용, ALTER TABLE 직접 실행

### 프론트엔드 스택
- 프레임워크: Vue 3 (Composition API) + Vite
- 지도: 카카오맵 API (autoload=false + window.kakao.maps.load() 패턴)
- 빌드: frontend/npm run build → static/ 디렉토리 출력
- 서빙: FastAPI StaticFiles로 / 마운트

---

## SECTION 3: 백엔드 파일 구조

```
main.py          # FastAPI 앱 진입점, 라우터 등록, 정적 파일 서빙
database.py      # MariaDB 연결, SQLAlchemy 세션
models.py        # DB 모델 (SQLAlchemy)
schemas.py       # Pydantic 요청/응답 스키마
auth.py          # JWT 토큰 생성/검증, 비밀번호 해싱
email_utils.py   # Gmail SMTP 인증 메일 발송
routers/
  auth.py        # 인증 API
  events.py      # 이벤트 CRUD + 미디어 API
  venues.py      # 장소 CRUD + 미디어 API
```

---

## SECTION 4: DB 스키마

### users 테이블
- id: INT PK
- email: VARCHAR(255) UNIQUE
- hashed_password: VARCHAR(255) NULL (소셜 로그인은 null)
- nickname: VARCHAR(100)
- is_organizer: BOOL (이벤트/장소 등록 권한)
- is_verified: BOOL (이메일 인증 여부)
- verify_code: VARCHAR(6) (인증 완료 후 null)
- verify_code_expires: DATETIME (코드 만료 시각, 10분)
- provider: VARCHAR(10) (email / kakao / naver / google)
- provider_id: VARCHAR(100) (소셜 로그인용 ID)
- created_at: DATETIME

### venues 테이블 (장소)
- id: INT PK
- venue_type: ENUM(club, academy, practice_room)
- name: VARCHAR(255)
- description: TEXT
- address: VARCHAR(500)
- latitude: FLOAT
- longitude: FLOAT
- phone: VARCHAR(50)
- website: VARCHAR(500)
- sns_links: JSON (예: {"instagram": "...", "kakao": "..."})
- business_hours: JSON (예: {"mon": "18:00-02:00"})
- floor_type: VARCHAR(50) (우드/타일/대리석)
- capacity: INT
- has_parking: BOOL
- parking_info: VARCHAR(255)
- cover_charge: VARCHAR(255) (클럽 전용: 입장료)
- has_bar: BOOL (클럽 전용)
- rental_fee: VARCHAR(255) (연습실 전용: 대관료)
- has_mirror: BOOL (연습실 전용)
- has_sound_system: BOOL (연습실 전용)
- area_sqm: FLOAT (연습실 전용: 면적 ㎡)
- has_trial_class: BOOL (학원 전용)
- trial_class_fee: VARCHAR(100) (학원 전용)
- extra_info: JSON
- owner_id: INT FK→users
- created_at: DATETIME
- updated_at: DATETIME

### venue_dance_genres 테이블 (장소-춤종류 다대다)
- venue_id: INT FK (PK)
- dance_genre: ENUM (PK)

### events 테이블 (이벤트)
- id: INT PK
- title: VARCHAR(255)
- description: TEXT
- location_name: VARCHAR(255)
- address: VARCHAR(500)
- latitude: FLOAT
- longitude: FLOAT
- start_date: DATETIME
- end_date: DATETIME NULL
- event_type: ENUM(social, workshop, festival, regular_class, performance, practice, other)
- venue_id: INT FK→venues NULL (등록된 장소와 연결, 선택)
- price: VARCHAR(255)
- early_bird_price: VARCHAR(255)
- difficulty: ENUM NULL (beginner, elementary, intermediate, advanced, all_level)
- instructor_name: VARCHAR(255) (워크샵/수업 전용)
- max_participants: INT
- requires_partner: BOOL
- dj_name: VARCHAR(255) (소셜 파티 전용)
- has_pre_lesson: BOOL
- dress_code: VARCHAR(255)
- is_recurring: BOOL (반복 이벤트 여부)
- recurrence_rule: JSON (예: {"day_of_week": "fri", "frequency": "weekly"})
- extra_info: JSON
- organizer_id: INT FK→users
- created_at: DATETIME
- updated_at: DATETIME

### event_dance_genres 테이블 (이벤트-춤종류 다대다)
- event_id: INT FK (PK)
- dance_genre: ENUM (PK)

### media 테이블 (이벤트/장소 공용 미디어)
- id: INT PK
- entity_type: VARCHAR(20) ("venue" 또는 "event")
- entity_id: INT (대상 ID)
- media_type: VARCHAR(20) ("image" 또는 "video")
- url: VARCHAR(1000) (이미지 경로 또는 영상 URL)
- thumbnail_url: VARCHAR(1000) NULL (영상 썸네일용)
- sort_order: INT
- created_at: DATETIME

### Enum 정의
- DanceGenre: salsa, bachata, kizomba, zouk, tango, merengue, other
  - 추가 예정: swing, waltz
- EventType: social, workshop, festival, regular_class, performance, practice, other
- VenueType: club, academy, practice_room
- DifficultyLevel: beginner, elementary, intermediate, advanced, all_level

---

## SECTION 5: 기존 API 목록

### 인증 API (/api/auth)
- POST /register: 회원가입, 인증코드 이메일 발송 (인증 불필요)
- POST /verify-email: 이메일 인증 코드 확인, JWT 발급 (인증 불필요)
- POST /resend-code: 인증 코드 재발송 (인증 불필요)
- POST /login: 로그인, JWT 발급 (인증 불필요)
- GET /me: 내 정보 조회 (인증 필요)

### 이벤트 API (/api/events)
- GET /: 이벤트 목록 조회, 필터: date_from, date_to, event_type, dance_genre, venue_id, difficulty (인증 불필요)
- POST /: 이벤트 등록 (인증 필요)
- GET /{id}: 이벤트 상세 (인증 불필요)
- PUT /{id}: 이벤트 수정, 본인만 (인증 필요)
- DELETE /{id}: 이벤트 삭제, 본인만 (인증 필요)
- POST /{id}/media: 미디어 추가, 본인만 (인증 필요)
- DELETE /{id}/media/{media_id}: 미디어 삭제, 본인만 (인증 필요)

### 장소 API (/api/venues)
- GET /: 장소 목록 조회, 필터: venue_type, dance_genre (인증 불필요)
- POST /: 장소 등록 (인증 필요)
- GET /{id}: 장소 상세 (인증 불필요)
- PUT /{id}: 장소 수정, 본인만 (인증 필요)
- DELETE /{id}: 장소 삭제, 본인만 (인증 필요)
- POST /{id}/media: 미디어 추가, 본인만 (인증 필요)
- DELETE /{id}/media/{media_id}: 미디어 삭제, 본인만 (인증 필요)

---

## SECTION 6: 프론트엔드 파일 구조

```
frontend/src/
  main.js                   # Vue 앱 진입점
  App.vue                   # 루트 컴포넌트 (전체 상태 관리, 모달 조율)
  components/
    TopBar.vue              # 상단 바 (로고, 장소검색, 로그인, 필터)
    KakaoMap.vue            # 지도 컴포넌트 (마커, 클릭 이벤트)
    Sidebar.vue             # 이벤트/장소 목록 패널
    PickLocationBar.vue     # 지도 위치 선택 모드 오버레이
    AuthModal.vue           # 로그인/회원가입/이메일인증 모달
    CreateEventModal.vue    # 이벤트 등록 모달
    CreateVenueModal.vue    # 장소 등록 모달
    EventDetailModal.vue    # 이벤트 상세 모달
    VenueDetailModal.vue    # 장소 상세 모달
  composables/
    useAuth.js              # 인증 상태/액션 (로그인, 로그아웃, 세션 복원)
    useEvents.js            # 이벤트 목록 상태/API 호출
    useVenues.js            # 장소 목록 상태/API 호출
  utils/
    api.js                  # fetch 래퍼, 날짜 포맷 유틸
    constants.js            # 레이블 상수, 필터 옵션, 카테고리 색상
  assets/
    style.css               # 전체 스타일 (다크 테마 기반)
```

---

## SECTION 7: 화면 레이아웃 명세

### 전체 레이아웃 구조
- PC (1024px 이상): TopBar(1줄 56px) + 지도(좌 70%) + 사이드바(우 30%) 고정 분할
- 태블릿 (768~1023px): TopBar + 지도(상 60%) + 사이드바(하 40%) 수직 분할
- 모바일 (768px 미만): TopBar + 지도(풀스크린) + 바텀시트(사이드바를 아래서 올라오는 패널로 처리)

### TopBar 명세
- 역할: 지도 네비게이션 전용 (콘텐츠 검색 아님)
- 구성: 로고("바람난 도시") | 위치 검색창 | 로그인 버튼
- 검색창 placeholder: "📍 지도 위치 이동 (강남역, 홍대 등...)"
- 검색 동작: 카카오 Places.keywordSearch() + Geocoder.addressSearch() 병렬 실행
- 디바운스: 300ms
- 결과: 드롭다운 최대 7개, 중복 좌표 제거, 선택 시 지도 panTo() 이동
- 키보드 지원: 방향키 위아래로 선택, Enter 확인, ESC 닫기
- 레이아웃: 기존 2줄에서 1줄로 변경 (높이 56px)
- 기존에 있던 이벤트 필터(날짜/유형/장르)는 TopBar에서 제거하고 Sidebar로 이동

### 카테고리 바 명세
- 역할: 지도 마커 및 사이드바 목록 표시 제어
- 위치: TopBar 바로 아래 또는 지도 좌상단 오버레이
- 구성: 토글 칩(pill) 버튼 4개
  - 클럽 (색상 #9b59b6, 보라)
  - 학원 (색상 #3498db, 파랑)
  - 연습실 (색상 #2ecc71, 초록)
  - 이벤트 (색상 #e74c3c, 빨강)
- 상태: 활성 = 채워진 색상 배경 + 흰 텍스트 / 비활성 = 아웃라인 + 회색 텍스트
- 동작: 토글 시 지도 마커 즉시 표시/숨김 + 사이드바 리스트 연동 필터링
- 기본값: 4개 모두 활성

### 사이드바 명세

사이드바는 두 가지 모드로 동작한다.

#### 지도 탐색 모드 (기본 모드)
- 진입 조건: 검색어 없음 (초기 상태 또는 검색어 삭제 후)
- 헤더 표시: 현재 지역명 + 날짜 범위 (예: "마포구 · 이번 주 [날짜 변경]")
- 지역명: 카카오 역지오코딩으로 현재 지도 중심 좌표의 행정구역명 표시
- 콘텐츠: 현재 지도 영역(bounds) 내 이벤트 + 장소 통합 리스팅
- 기본 날짜 필터: 오늘 ~ 7일 후 (이번 주), 사용자가 변경 가능
- 정렬: 이벤트는 날짜 임박순, 장소는 지도 중심 거리순
- 건수 표시: "이벤트 N건 · 장소 N건"
- 지도 연동: 지도 드래그/줌 변경 시 사이드바 목록 자동 갱신 (idle 이벤트)
- 빈 상태: 아이콘 + "이 지역에 등록된 이벤트가 없어요" 메시지 + 이벤트 등록 유도 버튼 표시

#### 검색 모드
- 진입 조건: 사이드바 검색창에 1글자 이상 입력
- 헤더 표시: 검색창 (포커스 상태)
- 콘텐츠: 이벤트 + 장소 통합 검색 결과 (타입 뱃지로 구분)
- 검색 대상: 이벤트명, 장소명, 강사명, 주소, 장르
- 정렬: 관련도순 (제목 일치 > 설명 포함, 임박 이벤트 가산점)
- 지도 연동: 검색 결과 아이템의 좌표로 지도 마커 표시 (bounds 무시)
- 모드 복귀: 검색어 삭제 또는 ESC 입력 시 지도 탐색 모드로 복귀
- 디바운스: 300ms

#### 사이드바 검색창 명세
- 위치: 사이드바 상단 고정
- placeholder: "🔍 이벤트, 장소, 강사 이름으로 검색..."
- API: GET /api/search?q={keyword}
- 최소 입력: 1글자 이상 (한글 조합 중 제외)

---

## SECTION 8: 카드 컴포넌트 명세

### 이벤트 카드 표시 정보
- 대표 이미지 (없을 경우 장르별 기본 그라데이션 배경 + 이모지)
- 이벤트 유형 뱃지 (소셜파티 / 워크샵 / 페스티벌 / 정기수업 / 공연 / 연습)
- 제목
- 장소명
- 날짜·시간
- 장르 태그 (복수 표시)
- 난이도 (beginner / 중급 / 전체 레벨 등)
- 가격 (무료 / 금액)
- 클릭 동작: 이벤트 상세 모달 열림 + 지도 해당 위치로 panTo

### 장소 카드 표시 정보
- 대표 이미지
- 장소 유형 뱃지 (클럽 / 학원 / 연습실)
- 이름
- 주소
- 장르 태그
- 운영 상태 (영업중 / 영업종료)
- 클릭 동작: 장소 상세 모달 열림 + 이 장소에서 열리는 예정 이벤트 표시

### 통합 검색 결과 카드
- 이벤트와 장소가 섞인 결과를 하나의 리스트로 표시
- 각 카드 좌상단에 타입 뱃지로 구분 (이벤트 / 클럽 / 학원 / 연습실)
- 탭 전환 없이 한 번에 모든 결과 표시

---

## SECTION 9: 신규 기능 명세

### 기능 1: 통합 검색 API
- 엔드포인트: GET /api/search
- 쿼리 파라미터: q (검색어), lat (위도, 선택), lng (경도, 선택), limit (기본 20)
- 검색 대상: events.title, events.description, events.instructor_name, venues.name, venues.address
- 응답 형식: 이벤트와 장소가 혼합된 배열, 각 아이템에 item_type 필드("event" / "venue") 포함
- 정렬: 제목 완전 일치 > 제목 부분 일치 > 설명 포함 순, 이벤트는 start_date 임박순 가산

### 기능 2: 이번 주 이벤트 기본 필터
- 현재 GET /api/events/ 에 date_from, date_to 파라미터가 존재함
- 프론트엔드에서 앱 초기 로드 시 date_from=오늘, date_to=7일후를 기본값으로 전달
- 사이드바 헤더의 "날짜 변경" 버튼으로 범위 변경 가능

### 기능 3: 이미지 업로드
- 업로드 방식: 프론트엔드에서 multipart/form-data로 서버 전송 → 서버 로컬 저장 → URL을 media 테이블에 저장
- 저장 경로: static/uploads/ (FastAPI StaticFiles로 그대로 서빙)
- 엔드포인트: POST /api/upload/image (신규 추가 필요)
- 허용 포맷: JPG, PNG, WEBP
- 최대 파일 크기: 5MB
- 응답: 업로드된 이미지 URL 반환 (예: /static/uploads/abc123.jpg)
- 이벤트 최대 이미지 수: 5장
- 장소 최대 이미지 수: 10장
- 표시 순서: sort_order 필드로 관리

### 기능 4: 북마크/관심 저장
- 대상: 이벤트, 장소 모두 가능
- 저장 방식: 카드 우상단 하트 아이콘 클릭
- 미로그인 시: 로그인 유도 모달 표시
- 저장된 북마크: "내 저장 목록" 탭에서 확인
- 신규 테이블 필요: bookmarks (id, user_id FK, entity_type, entity_id, created_at)
- 엔드포인트 추가 필요:
  - POST /api/events/{id}/bookmark
  - DELETE /api/events/{id}/bookmark
  - POST /api/venues/{id}/bookmark
  - DELETE /api/venues/{id}/bookmark
  - GET /api/users/me/bookmarks

### 기능 5: 반복 이벤트 UI
- DB 스키마에 is_recurring, recurrence_rule 컬럼이 이미 존재함
- 이벤트 등록 폼에 "반복 이벤트" 토글 추가 필요
- 반복 설정 UI: 요일 선택 (월화수목금토일), 주기 선택 (매주 / 격주 / 매월)
- recurrence_rule 저장 형식 예시: {"day_of_week": "fri", "frequency": "weekly"}
- 캘린더/리스트에 반복 이벤트 자동 전개하여 표시

### 기능 6: 이벤트·장소 수정/삭제 UI
- API는 PUT /api/events/{id}, DELETE /api/events/{id} 등 이미 완성됨
- 프론트엔드 UI만 추가하면 됨
- 이벤트 상세 모달에서 본인 이벤트일 경우 "수정" / "삭제" 버튼 표시
- 수정: 등록 폼과 동일한 모달을 기존 데이터로 프리필해서 열기
- 삭제: 확인 다이얼로그 표시 후 API 호출

---

## SECTION 10: 디자인 시스템

### 색상 팔레트
- 배경 base: #0f0f1a (짙은 네이비블랙, 클럽 조명 분위기)
- 배경 card: #1e1e2e (카드, 사이드바 배경)
- 배경 elevated: #2a2a3e (모달, 드롭다운)
- 강조 primary: #ff4d6d (핫핑크/코랄, CTA 버튼, 활성 상태)
- 강조 secondary: #a855f7 (퍼플, 살사 무드 포인트)
- 텍스트 primary: #e2e8f0 (주요 텍스트)
- 텍스트 secondary: #94a3b8 (부가 정보)
- 보더: #2d2d42 (카드 테두리)

### 카테고리 마커 색상
- 클럽: #9b59b6 (보라)
- 학원: #3498db (파랑)
- 연습실: #2ecc71 (초록)
- 이벤트: #e74c3c (빨강)

### 지도 스타일
- 카카오맵 기본 스타일이 밝아서 다크 UI와 충돌함
- CSS filter로 다크 처리 적용: filter: invert(90%) hue-rotate(180deg) brightness(0.85)

---

## SECTION 11: 현재 구현 상태

### 완료된 기능
- 서버 인프라 (OCI, Nginx, HTTPS, systemd)
- dev/prod 환경 분리
- 회원가입·로그인 (이메일 인증 포함)
- 이벤트 CRUD (API + 프론트엔드)
- 장소 CRUD (API + 프론트엔드)
- 미디어 API (URL 기반, 백엔드만)
- 카카오맵 지도 연동 (마커, 클릭, 위치 선택)
- 장소/주소 검색으로 지도 위치 이동
- 카테고리 필터 (지도 마커 + 사이드바 연동)
- 이벤트 필터 (날짜/유형/장르)
- 사이드바 지도 영역(bounds) 연동
- 반응형 UI (모바일 대응)

### 백엔드만 완료, 프론트엔드 UI 미구현
- 미디어 등록/삭제 (이미지·영상 URL 첨부)
- 이벤트 수정 UI (API: PUT /api/events/{id} 완성)
- 이벤트 삭제 UI (API: DELETE /api/events/{id} 완성)
- 장소 수정 UI (API: PUT /api/venues/{id} 완성)
- 장소 삭제 UI (API: DELETE /api/venues/{id} 완성)

### 완전 미구현
- 소셜 로그인 (카카오/네이버/Google) — DB 스키마와 카카오 앱키 준비만 완료
- 이미지 직접 업로드 UI 및 R2 연동
- 통합 검색 (이벤트+장소 혼합 결과)
- 반복 이벤트 등록/관리 UI
- 북마크/관심 저장
- 주최자 대시보드
- 이번 주 이벤트 기본 필터 (프론트엔드 기본값 처리)
- 지도 다크 스타일 적용
- TopBar 1줄 통합 및 카테고리 토글 칩 버튼 교체
- 사이드바 통합 검색창 및 이중 모드(탐색/검색)
- 빈 상태(empty state) 디자인
- 모바일 바텀시트 패턴

---

## SECTION 12: 개발 백로그 (우선순위 순)

### P1 — 즉시 작업 (핵심 완성)

B-001: 이미지 업로드 UI
- 작업 범위: Frontend + Backend
- 설명: 이벤트/장소 등록 폼에 이미지 첨부 기능 추가. 서버 로컬 저장 (static/uploads/).
- 관련 파일: CreateEventModal.vue, CreateVenueModal.vue, 신규 routers/upload.py

B-002: 이벤트 수정 UI
- 작업 범위: Frontend
- 설명: 이벤트 상세 모달에서 본인 이벤트일 경우 수정 버튼 표시, 기존 데이터 프리필 폼 열기
- 관련 파일: EventDetailModal.vue, CreateEventModal.vue (수정 모드 추가)

B-003: 이벤트 삭제 UI
- 작업 범위: Frontend
- 설명: 삭제 확인 다이얼로그 후 DELETE /api/events/{id} 호출
- 관련 파일: EventDetailModal.vue

B-004: 장소 수정 UI
- 작업 범위: Frontend
- 설명: 장소 상세 모달에서 본인 장소일 경우 수정 버튼 표시, 기존 데이터 프리필 폼 열기
- 관련 파일: VenueDetailModal.vue, CreateVenueModal.vue (수정 모드 추가)

B-005: 장소 삭제 UI
- 작업 범위: Frontend
- 설명: 삭제 확인 다이얼로그 후 DELETE /api/venues/{id} 호출
- 관련 파일: VenueDetailModal.vue

B-006: TopBar 1줄 통합
- 작업 범위: Frontend
- 설명: 기존 2줄 구조를 1줄로 변경. 이벤트 필터 제거 (사이드바로 이동). 높이 56px.
- 관련 파일: TopBar.vue

B-007: 카테고리 토글 칩 버튼
- 작업 범위: Frontend
- 설명: 체크박스+레이블 형태를 pill 토글 버튼 스타일로 교체
- 관련 파일: TopBar.vue 또는 별도 CategoryBar.vue 분리

B-008: 사이드바 검색창 추가
- 작업 범위: Frontend
- 설명: 사이드바 상단에 통합 검색 입력창 추가. 입력 시 검색 모드로 전환.
- 관련 파일: Sidebar.vue

B-009: 통합 검색 API
- 작업 범위: Backend
- 설명: GET /api/search?q= 엔드포인트 신규 구현. 이벤트+장소 혼합 결과 반환.
- 관련 파일: 신규 routers/search.py

B-010: 사이드바 이중 모드 (탐색/검색)
- 작업 범위: Frontend
- 설명: 검색어 없을 때 지도 탐색 모드, 검색어 있을 때 검색 결과 모드로 자동 전환
- 관련 파일: Sidebar.vue, useEvents.js, useVenues.js

B-011: 이번 주 이벤트 기본 필터
- 작업 범위: Frontend
- 설명: 앱 초기 로드 시 date_from=오늘, date_to=7일후를 기본값으로 적용
- 관련 파일: useEvents.js, Sidebar.vue

B-012: 빈 상태(empty state) UI
- 작업 범위: Frontend
- 설명: 이벤트/장소가 없을 때 아이콘+메시지+등록 유도 버튼 표시
- 관련 파일: Sidebar.vue

### P2 — 중요 (P1 완료 후)

B-013: 반복 이벤트 등록 UI
- 작업 범위: Frontend
- 설명: 이벤트 등록 폼에 반복 설정 UI 추가 (DB 스키마 is_recurring, recurrence_rule 이미 완성)
- 관련 파일: CreateEventModal.vue

B-014: 반복 이벤트 캘린더 전개
- 작업 범위: Backend + Frontend
- 설명: recurrence_rule을 기반으로 향후 이벤트 자동 생성 또는 가상 전개하여 표시

B-015: 북마크/관심 저장
- 작업 범위: Full-stack
- 설명: 이벤트·장소 하트 버튼, bookmarks 테이블 신규 생성, 내 저장 목록 탭
- 신규 테이블: bookmarks (id, user_id, entity_type, entity_id, created_at)

B-016: 주최자 대시보드
- 작업 범위: Full-stack
- 설명: 내 이벤트·장소 목록 관리 페이지, 조회수 확인, 수정·삭제 일괄 관리

B-017: 이벤트 상세 외부 링크
- 작업 범위: Full-stack
- 설명: 인스타그램, 카카오채널, 티켓 구매 링크 입력 필드 및 상세 화면 표시
- events 테이블에 컬럼 추가 필요: instagram_url, kakao_url, ticket_url

B-018: 색상 및 무드 리디자인
- 작업 범위: Frontend
- 설명: 배경색 네이비블랙(#0f0f1a), 강조색 핫핑크(#ff4d6d)/퍼플(#a855f7)로 전체 스타일 교체
- 관련 파일: assets/style.css

B-019: 지도 다크 필터
- 작업 범위: Frontend
- 설명: 카카오맵 컨테이너에 CSS filter 적용으로 다크 처리
- 관련 파일: KakaoMap.vue

B-020: 모바일 바텀시트
- 작업 범위: Frontend
- 설명: 모바일에서 사이드바를 바텀시트(아래서 올라오는 패널) 패턴으로 교체
- 관련 파일: Sidebar.vue, App.vue, style.css

B-021: 스윙·왈츠 장르 추가
- 작업 범위: Backend + Frontend
- 설명: DanceGenre Enum에 swing, waltz 추가, DB ALTER, 프론트 상수 업데이트

B-022: 현재 지역명 표시
- 작업 범위: Frontend
- 설명: 카카오 역지오코딩으로 지도 중심 좌표의 행정구역명을 사이드바 헤더에 표시
- 관련 파일: Sidebar.vue, KakaoMap.vue

### P3 — 성장 (P2 완료 후)

B-023: 카카오 소셜 로그인 — OAuth 연동 (DB·앱키 준비 완료)
B-024: 네이버 소셜 로그인 — OAuth 연동
B-025: 구글 소셜 로그인 — OAuth 연동
B-026: 장소 리뷰·평점 — 플로어/음향/분위기 별점, 한줄 리뷰
B-027: 강사 프로필 페이지 — 강사 등록, 이벤트 연결, SNS 링크
B-028: 주최자 팔로우 — 팔로우한 주최자의 새 이벤트 알림
B-029: D-1 알림 — 북마크 이벤트 하루 전 이메일/카카오 알림
B-030: 이벤트 제보 기능 — 일반 사용자 제보, 관리자 승인 후 등록
B-031: 연습 파트너 찾기 — 지역·장르별 연습 파트너 구인 게시판
B-032: 캘린더 뷰 — 주간/월간 캘린더로 이벤트 탐색
B-033: 관리자 페이지 — 전체 콘텐츠·유저 관리, 주최자 승인
B-034: PWA 지원 — 모바일 홈 화면 추가, 오프라인 기본 동작

---

## SECTION 13: AI 작업 지시 가이드

이 문서를 받은 AI가 작업할 때 참고할 원칙들이다.

### 작업 시작 전 필수 확인
- 작업 시작 전 TODO.md를 반드시 읽어 현재 단계와 우선순위를 파악한다
- TODO.md의 상태 표기: ✅ 완료 / 🚧 진행중 / ⬜ 미착수 / ⏸ 보류
- 작업이 완료되면 TODO.md의 해당 항목을 ✅로 업데이트한다

### 코딩 스타일
- 백엔드: Python FastAPI 관례를 따르며, 라우터는 routers/ 디렉토리에 분리한다
- 프론트엔드: Vue 3 Composition API + script setup 문법을 사용한다
- API 호출은 utils/api.js의 fetch 래퍼를 통해 처리한다
- 상태 관리는 composables/ 패턴을 따른다 (useAuth, useEvents, useVenues 등)
- DB 변경 시 alembic 미사용, ALTER TABLE SQL문을 직접 제시한다

### 작업 요청 예시 형식
"B-008: 사이드바 검색창 추가 작업을 해줘"처럼 백로그 ID를 명시하면 이 문서의 해당 항목을 참고하여 구현한다.

### 주의 사항
- 카카오맵 API는 autoload=false 패턴을 반드시 유지한다 (window.kakao.maps.load() 콜백 사용)
- DB 마이그레이션은 Alembic을 사용하지 않으므로 ALTER TABLE SQL문을 명시적으로 제공한다
- 인증이 필요한 API는 반드시 Authorization: Bearer {token} 헤더를 확인한다
- is_organizer가 True인 사용자만 이벤트·장소를 등록·수정·삭제할 수 있다
- 본인이 등록한 이벤트·장소만 수정·삭제 가능하다 (organizer_id / owner_id 검증)

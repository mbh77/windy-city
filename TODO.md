# 바람난 도시 — 작업 TODO

> 마지막 업데이트: 2026-03-23
> 상태 표기: ✅ 완료 / 🚧 진행중 / ⬜ 미착수 / ⏸ 보류

---

## ✅ 완료된 작업

- ✅ 서버 인프라 구성 (OCI, Nginx, HTTPS, systemd)
- ✅ dev/prod 환경 분리 (포트, DB, 브랜치)
- ✅ 회원가입·로그인 (이메일 인증, JWT)
- ✅ 이벤트 CRUD API (`/api/events`)
- ✅ 장소 CRUD API (`/api/venues`)
- ✅ 미디어 API — URL 기반 등록/삭제 (`/api/events/{id}/media`, `/api/venues/{id}/media`)
- ✅ 카카오맵 연동 (SVG 마커, 인포윈도우, 클릭 이벤트)
- ✅ 위치 선택 모드 (지도 클릭 → 좌표 + 역지오코딩)
- ✅ 장소/주소 검색 → 지도 이동 (TopBar, 카카오 keywordSearch + addressSearch 병렬)
- ✅ 카테고리 필터 (클럽/학원/연습실/이벤트 토글, 마커·사이드바 연동)
- ✅ 이벤트 필터 (날짜/유형/장르)
- ✅ 사이드바 지도 영역(bounds) 연동
- ✅ 이벤트 등록 모달 (CreateEventModal)
- ✅ 장소 등록 모달 (CreateVenueModal)
- ✅ 이벤트 상세 모달 (EventDetailModal)
- ✅ 장소 상세 모달 (VenueDetailModal)
- ✅ 인증 모달 (AuthModal — 로그인/회원가입/이메일인증 3단계)
- ✅ 반응형 UI (모바일 768px)
- ✅ **B-002/003** 이벤트 수정/삭제 UI
- ✅ **B-004/005** 장소 수정/삭제 UI
- ✅ **B-006** TopBar 1줄 통합
- ✅ **B-007** 카테고리 토글 칩 버튼 (CategoryBar.vue)
- ✅ **B-008/009/010** 통합 검색 API + 사이드바 검색창 + 이중 모드
- ✅ **B-011** 이번 주 이벤트 기본 필터 + 날짜 범위 변경 UI
- ✅ **B-012** 빈 상태 UI (탭별 메시지)
- ✅ **B-001** 이미지 업로드 (서버 로컬 + 슬라이더 + 전체화면 뷰어)
- ✅ **B-013/014** 반복 이벤트 등록/표시 + 요일 필터
- ✅ **B-020** 모바일 바텀시트 (50dvh 고정)
- ✅ ~~마커 클러스터링~~ → 제거 (지도가 비어 보이는 문제), 숫자 뱃지 방식으로 대체
- ✅ 마커 말풍선 (PC: 호버, 모바일: 터치 → 재터치로 상세)
- ✅ 지도 내 검색 토글
- ✅ 모바일 상세 모달 하단 50% 표시
- ✅ 이미지 PNG→JPG 자동 변환 + 3MB 제한
- ✅ 시간 KST 기준 저장 (UTC 변환 제거)
- ✅ Vue Router 도입 (`/`, `/about`, `/feedback`)
- ✅ TopBar 개선 — 로그인 아이콘/아바타, 햄버거 메뉴
- ✅ About 페이지 (`/about`) — 서비스 소개, 이용약관, 개인정보처리방침, 사업자 정보
- ✅ 제보/제안 기능 (`/feedback`) — 폼 입력 → 관리자 메일 발송
- ✅ 온보딩 화면 — 첫 방문 시 서비스 소개 + UI 가이드 (localStorage 1회)
- ✅ SEO 메타 태그 — title, description, Open Graph
- ✅ 회원가입 시 is_organizer 기본 true (모든 사용자 이벤트/장소 등록 가능)
- ✅ 이벤트 상세 "주최" → "작성자" 변경
- ✅ 설명 줄바꿈 적용 (white-space: pre-wrap)
- ✅ 댄스 장르 추가 (lindy_hop, balboa, blues, west_coast_swing) — DB + models + constants
- ✅ TopBar 공통 배치 — 모든 페이지(게시판, About 등)에서 TopBar 표시, 검색창은 메인만
- ✅ 로고 클릭 시 홈 이동 + 로고 이미지 적용
- ✅ 회원 탈퇴 기능 — DELETE /api/auth/me, 작성물 유지 + "탈퇴한 사용자" 표시
- ✅ 인증 메일 리뉴얼 — 발신자/제목 "바람난 도시", 로고 이미지 삽입, 색상 통일
- ✅ 회원 탈퇴 고스트 계정 패턴 — 탈퇴 시 콘텐츠를 ghost 계정으로 이전 후 회원 레코드 완전 삭제
- ✅ 온보딩 리뉴얼 — 로고 이미지 적용, 색상 통일, 버튼 "시작하기"로 단순화
- ✅ OG 이미지 생성 — 카톡 공유 시 로고 썸네일 표시
- ✅ SPA 라우팅 fallback — 게시판 등 서브 페이지 새로고침 시 404 해결
- ✅ 이벤트/장소 설명 마크다운 렌더링 — 상세 모달 + 등록/수정 미리보기
- ✅ 이벤트/장소 설명 YouTube/Instagram 임베드
- ✅ 말풍선 이미지 표시 — 마커 말풍선에 대표 이미지 + 장르 정보
- ✅ 말풍선 클릭 → 상세 보기 연결
- ✅ 사이드바 리스트 이미지 — 대표 이미지 또는 카테고리 마커 이미지 표시
- ✅ 내 위치 이동 버튼 — 지도 우상단, 네트워크 기반 위치, 로딩 표시
- ✅ 검색 이동 시 적정 줌 레벨 자동 조정
- ✅ 동일 좌표 이벤트 숫자 뱃지 — 겹치는 이벤트 수 표시 + 클릭 시 목록 말풍선
- ✅ 상세 주소 입력 — events/venues에 address_detail 컬럼 추가
- ✅ 가입 시 주최자 권한 기본 부여 (is_organizer = True)

---

## P-UX — UX 개선 (이벤트/장소 등록·상세 페이지 전환)

> 기존 모달 → 전용 페이지로 전환. 지도 모달은 간략 보기로 유지, 깊이 있는 보기/편집은 별도 페이지.

### 이벤트 날짜/시간 분리
- ✅ **UX-012** DB 스키마 변경 — `start_date`/`end_date` → `event_date`/`event_end_date`/`start_time`/`end_time` (dev DB 완료)
- ✅ **UX-013** 백엔드 API 수정 — models, schemas, routers/events.py, routers/search.py
- ✅ **UX-014** 프론트 기존 화면 날짜 대응 — EventDetailModal에서 새 날짜 구조(event_date + start_time/end_time) 표시
- ✅ **UX-015** 프론트 상세/목록 표시 — formatTime() 유틸 추가, 시:분까지만 표시

### 상세 페이지
- ✅ **UX-001** 이벤트 상세 페이지 (`/events/:id`) — views/events/EventDetailView.vue
- ✅ **UX-002** 장소 상세 페이지 (`/venues/:id`) — views/venues/VenueDetailView.vue
- ⬜ **UX-003** 이벤트 목록 페이지 (`/events`) — 게시판형 목록, 필터/정렬
- ⬜ **UX-004** 장소 목록 페이지 (`/venues`) — 게시판형 목록, 필터/정렬
- ✅ **UX-005** 지도 모달 → 상세 페이지 연결 — EventDetailModal, VenueDetailModal에 "상세 보기" 링크
- ✅ **UX-016** 상세 페이지 → 지도 연결 — "지도에서 보기" 버튼, 클릭 시 지도에서 해당 이벤트 선택

### 등록/수정 전용 페이지
- ✅ **UX-006** 이벤트 등록 페이지 (`/events/new`) — 2단계 폼 + 미니맵 + 마크다운 툴바
  - ✅ 기본 구조, 미니맵, 위치 검색, 마크다운 에디터, 이미지 첨부
  - ✅ 2단계 유형별 추가 필드 (소셜 파티/워크샵 정보)
  - ✅ 2단계 반복 이벤트 설정 (주기/요일/휴강일/보강일)
- ✅ **UX-007** 이벤트 수정 페이지 (`/events/:id/edit`) — 라우팅 + 동작 테스트 완료
- ✅ **UX-008** 장소 등록 페이지 (`/venues/new`) — 2단계 폼 + 미니맵 + 마크다운 + 유형별 필드
- ✅ **UX-009** 장소 수정 페이지 (`/venues/:id/edit`) — VenueWriteView 공용, 라우팅 완료

### 기존 모달 정리
- ✅ **UX-010** EventDetailModal 간소화 — 수정 → router-link, 불필요 정보 제거
- ✅ **UX-010-2** VenueDetailModal 간소화 — 수정 → router-link, 표시 순서 상세 페이지와 통일
- ✅ **UX-011** 기존 등록 모달 전부 제거
  - ✅ CreateEventModal 제거 (MainView 관련 코드 정리)
  - ✅ CreateVenueModal 제거 (MainView 관련 코드 정리)
  - ✅ PickLocationBar 제거 (위치 선택 모드 불필요)

### 코드 정리
- ✅ views 폴더 구조 정리 — board/, events/, venues/ 하위 폴더 분리
- ✅ `utils/markdown.js` — renderMarkdown 공통화 (9개 파일 중복 제거)
- ✅ `composables/useImageUpload.js` — 이미지 업로드/삭제/저장 공통화
- ✅ `composables/useLocationSearch.js` — 카카오 장소 검색 공통화
- ✅ `composables/useMarkdownEditor.js` — 마크다운 툴바 (B/I/링크/이미지/영상) 공통화
- ✅ 전역 CSS 분리 — style.css → base/layout/topbar/sidebar/map/modal/form/badges/markdown.css
- ✅ scoped CSS 중복 제거 — write/dialog/markdown 스타일을 전역으로 통합 (EventWriteView, PostWriteView, PostDetailView)
- ✅ `post-title`/`post-meta`/`post-body`/`post-actions` 스타일 전역화 (layout.css)
- ✅ `formatTime()` 유틸 추가 — 시간 HH:MM 포맷 (api.js)
- ✅ 마크다운 연속 빈 줄 보존 — `\n{3,}` → `<br>` 변환 (markdown.js)
- ✅ 용어 통일 — "이벤트" → "강습·행사", "정규수업" → "강습", 기본 유형 regular_class

---

## P2 — 사용성 개선

- ⬜ **B-015** 북마크/관심 저장 — 하트 버튼, bookmarks 테이블 신규, 내 저장 목록 탭
  - DB: 신규 `bookmarks` 테이블 (id, user_id, entity_type, entity_id, created_at)
  - API: POST/DELETE `/api/events/{id}/bookmark`, `GET /api/users/me/bookmarks` 등
- ⬜ **B-016** 주최자 대시보드 — 내 이벤트·장소 목록 관리, 수정·삭제 일괄 관리
- ⬜ **B-017** 이벤트 외부 링크 — 인스타그램/카카오채널/티켓 링크 입력·표시
  - DB: events 테이블에 `instagram_url`, `kakao_url`, `ticket_url` 컬럼 추가
- ✅ **B-018** 색상/무드 리디자인 — 웜톤 라이트 테마 + 로고 이미지 적용
- ✅ **B-021** 추가 장르 확장 — lindy_hop/balboa/blues/west_coast_swing 추가 완료
- ✅ **B-022** 현재 지역명 표시 — 카카오 역지오코딩으로 지도 우하단에 행정구역명 오버레이
- ✅ **B-036** 동일 좌표 이벤트 숫자 뱃지 + 클릭 시 목록 말풍선 (InfoWindow 스크롤 제약 있음)
- ✅ **B-037** 마커 이미지 교체 — Canvas 원형 클리핑 + 카테고리별 커스텀 이미지 + 칩 버튼 색상 통일
- ✅ **B-038** 말풍선 클릭 → 상세 보기 연결 — 글로벌 함수 방식으로 해결

---

## P-ADMIN — 관리자 페이지

### Phase 1: 기반 구축
- ✅ **A-001** 관리자 권한 시스템
  - DB: users 테이블에 `is_admin` 컬럼 추가 (dev/prod 완료)
  - 백엔드: `get_current_admin` 검증 함수, `/me` 응답에 is_admin 포함
  - 프론트: 햄버거 메뉴에 관리자 항목 표시, `/admin` 라우트
  - 관리자는 모든 이벤트/장소 수정/삭제 가능
  - 금지 닉네임 검증 (admin, 관리자 등)

### Phase 2: 대시보드 (통계)
- ⬜ **A-002** 방문자 추적 시스템
  - DB: `visit_logs` 테이블 (id, ip, path, user_agent, visited_at)
  - 백엔드: 미들웨어로 페이지 요청 기록
- ⬜ **A-003** 대시보드 통계 API + UI
  - API: `GET /api/admin/stats` (오늘/주간/월간 방문자, 총 회원/이벤트/장소 수)
  - 프론트: AdminView.vue 대시보드 탭 (숫자 카드 + 간단 차트)
  - 최근 가입자, 최근 등록 이벤트/장소 목록

### Phase 3: 회원 관리
- ✅ **A-004** 회원 목록 API + UI
  - API: `GET /api/admin/users` (검색, 페이징)
  - 프론트: 회원 탭 (이메일, 닉네임, 인증여부, 주최자여부, 가입일)
- ✅ **A-005** 회원 권한 관리
  - API: `PUT /api/admin/users/{id}` (is_organizer 토글)
  - API: `DELETE /api/admin/users/{id}` (게시물 없는 계정 삭제)
  - 프론트: 주최자 ON/OFF 토글 + 삭제 버튼 (관리자 계정 삭제 불가)

### Phase 4: 콘텐츠 관리
- ✅ **A-006** 이벤트 관리 API + UI
  - API: `GET /api/admin/events` (전체 이벤트, 검색/페이징)
  - API: `DELETE /api/admin/events/{id}` (관리자 삭제, 미디어 파일 포함)
  - 프론트: 이벤트 탭 (제목, 장소, 유형, 시작일, 작성자, 삭제)
- ✅ **A-007** 장소 관리 API + UI
  - API: `GET /api/admin/venues` (전체 장소, 검색/페이징)
  - API: `DELETE /api/admin/venues/{id}` (관리자 삭제, 미디어 파일 포함)
  - 프론트: 장소 탭 (이름, 유형, 주소, 등록자, 삭제)

### Phase 5: 운영 도구
- ⬜ **A-008** 이벤트/장소 승인 시스템 — 등록 시 관리자 승인 후 공개
- ⬜ **A-009** 신고/제보 관리 — 사용자 신고 접수, 관리자 처리
- ⬜ **A-010** 공지사항/배너 관리 — 메인 화면 공지 표시

---

## P-BOARD — 게시판 (공지사항 + 열린 플로어)

### Phase 1: DB + 백엔드 API
- ✅ **BD-001** DB 테이블 생성 (posts, comments — dev/prod 완료)
- ✅ **BD-002** models.py + schemas.py 추가 (Post, Comment 모델 + 스키마)
- ✅ **BD-003** 게시글 CRUD API (`routers/posts.py`)
- ✅ **BD-004** 댓글 API (작성/삭제)

### Phase 2~4: 프론트 — 목록 + 상세 + 작성/수정
- ✅ **BD-005** 게시판 목록 UI (`views/BoardView.vue`, 검색, 페이징)
- ✅ **BD-006** 글 상세 UI (`views/PostDetailView.vue`, 수정/삭제 버튼)
- ✅ **BD-007** 댓글 UI (목록, 입력, 삭제)
- ✅ **BD-008** 글 작성 UI (`views/PostWriteView.vue`, 미리보기 토글, 마크다운 안내)
- ✅ **BD-009** 글 수정 UI (기존 데이터 프리필, editMode)

### Phase 5: 마크다운 + 미디어 렌더링
- ✅ **BD-010** 마크다운 라이브러리 설치 (`marked` + `DOMPurify`)
  - 글 상세 + 미리보기에서 마크다운 → HTML 렌더링
  - XSS 방지 (`DOMPurify`)
- ✅ **BD-011** 미디어 자동 임베드
  - YouTube URL → `<iframe>` 플레이어 자동 변환
  - Instagram 릴스 URL → 임베드 변환
  - 이미지 마크다운 `![](url)` → `<img>` 렌더링
- ✅ **BD-012** 글 작성 툴바 컴포넌트
  - 📷 이미지 업로드 버튼 (파일 선택 → 업로드 → URL 삽입)
  - ▶️ 영상 URL 입력 다이얼로그
  - **B** 굵게, *I* 기울임 버튼
  - 미리보기 토글 (작성 ↔ 미리보기 전환)

### Phase 6: 게시판 기능 보강
- ✅ **BD-013** 조회수
  - DB: posts 테이블에 `view_count` INT DEFAULT 0 컬럼 추가
  - 백엔드: 상세 조회 시 view_count +1 (중복 방지는 추후)
  - 프론트: 목록·상세에 조회수 표시
- ✅ **BD-014** 댓글 수정
  - 백엔드: `PUT /api/posts/{post_id}/comments/{comment_id}` 추가
  - 프론트: 댓글 수정 버튼 + 인라인 편집 UI
- ✅ **BD-015** 공지 상단 고정
  - DB: posts 테이블에 `is_pinned` TINYINT(1) DEFAULT 0 컬럼 추가
  - 백엔드: 공지 작성/수정 시 is_pinned 저장 (관리자만), 목록 API에서 고정 공지 별도 반환
  - 프론트: 공지 작성 시 "상단 고정" 체크박스, 자유게시판에서도 고정 공지 상단 표시
  - 고정 공지는 별도 스타일로 구분 (배경색, 📌 아이콘)

---

## P-OPS — 서비스 안정성 확보

### Phase 1: 데이터 보호 (최우선)
- ✅ **OPS-001** DB 자동 백업
  - 크론잡: mysqldump 매일 1회 실행 → 로컬 백업 디렉토리 저장
  - 보관 정책: 최근 7일치 유지, 이전 파일 자동 삭제
  - 선택: OCI Object Storage로 원격 백업 (서버 장애 대비)
- ✅ **OPS-002** uploads 파일 백업
  - 크론잡: uploads/ 디렉토리 tar 압축 → 백업 디렉토리 저장
  - 주기: 주 1회 (이미지는 변경 빈도 낮음)
- ✅ **OPS-003** 백업 복원 테스트
  - 백업 파일로 실제 복원 가능한지 1회 검증

### Phase 2: 모니터링
- ⬜ **OPS-004** 서버 다운 알림
  - 외부 모니터링 서비스 (UptimeRobot 무료) 연동
  - HTTPS 엔드포인트 주기적 체크 → 다운 시 이메일/슬랙 알림
- ⬜ **OPS-005** 헬스체크 API
  - `GET /api/health` — 앱 + DB 연결 상태 확인 엔드포인트
  - 모니터링 서비스가 이 엔드포인트를 체크
- ⬜ **OPS-006** 디스크/메모리 알림
  - 크론잡: 디스크 사용률 90% 이상 시 이메일 알림
  - uploads 폴더 용량 모니터링

### Phase 3: 보안 강화
- ⬜ **OPS-007** API rate limiting
  - FastAPI 미들웨어로 IP당 요청 제한 (예: 분당 60회)
  - 로그인 시도 제한 (예: 5회 실패 시 5분 차단)
- ⬜ **OPS-008** CORS 설정 점검
  - 허용 도메인을 windycity.co.kr로 제한
- ⬜ **OPS-009** 보안 헤더 추가
  - Nginx: X-Frame-Options, X-Content-Type-Options, CSP 등

### Phase 4: 배포 안정화
- ⬜ **OPS-010** 배포 스크립트 자동화
  - deploy.sh: git pull → npm install → build → restart를 한 번에
  - 빌드 실패 시 자동 롤백 (이전 빌드 보관)
- ⬜ **OPS-011** 무중단 배포 검토
  - uvicorn 워커 graceful restart 또는 블루-그린 배포

---

## P-ADS — 수익화 (Google AdSense)

### Phase 1: 가입 및 승인
- ✅ **ADS-001** AdSense 가입 신청
  - Google AdSense 사이트에서 windycity.co.kr 등록 (2026-03-22)
  - 승인 심사 대기 중 (1~14일)
- ✅ **ADS-002** 승인 확인 코드 + ads.txt 삽입
  - `<script>` 코드를 `frontend/index.html`의 `<head>`에 삽입
  - `static/ads.txt` 생성 (dev/prod)
  - GDPR 동의 메시지 설정 완료

### Phase 2: 광고 배치
- ⬜ **ADS-003** 사이드바 하단 광고
  - Sidebar.vue 리스트 하단에 AdSense 배너 배치
- ⬜ **ADS-004** 게시판 목록 광고
  - BoardView.vue 글 목록 사이에 네이티브 광고 삽입
- ⬜ **ADS-005** 상세 모달 하단 광고
  - EventDetailModal.vue / VenueDetailModal.vue 하단에 배너

### Phase 3: 최적화
- ⬜ **ADS-006** 모바일 광고 위치 조정
  - 바텀시트, 상세 모달 등 모바일 레이아웃에 맞는 광고 크기/위치 최적화
- ⬜ **ADS-007** 광고 수익 모니터링
  - AdSense 대시보드에서 노출/클릭/수익 추이 확인
  - 위치별 성과 비교 → 저성과 위치 제거 또는 변경

---

## P3 — 성장

- ⬜ **B-023** 카카오 소셜 로그인 — OAuth 연동 (DB·앱키 준비 완료)
- ⬜ **B-024** 네이버 소셜 로그인 — OAuth 연동
- ⬜ **B-025** 구글 소셜 로그인 — OAuth 연동
- ⬜ **B-026** 장소 리뷰·평점 — 플로어/음향/분위기 별점, 한줄 리뷰
- ⬜ **B-027** 강사 프로필 페이지 — 강사 등록, 이벤트 연결, SNS 링크
- ⬜ **B-028** 주최자 팔로우 — 팔로우한 주최자의 새 이벤트 알림
- ⬜ **B-029** D-1 알림 — 북마크 이벤트 하루 전 이메일/카카오 알림
- ⬜ **B-030** 이벤트 제보 기능 — 일반 사용자 제보, 관리자 승인 후 등록
- ⬜ **B-031** 연습 파트너 찾기 — 지역·장르별 연습 파트너 구인 게시판
- ⬜ **B-032** 캘린더 뷰 — 주간/월간 캘린더로 이벤트 탐색
- ⬜ **B-034** PWA 지원 — 모바일 홈 화면 추가, 오프라인 기본 동작
- ⬜ **B-035** 검색 효율화 — DB 인덱스 (1단계), FULLTEXT (2단계), 검색엔진  (3단계)
- ⬜ **B-036** 강남, 홍대, 부산, 광주 주요 거점 바로 이동 버튼 맵 좌측 배치


# 바람난 도시 (Windy City)

커플댄스 커뮤니티를 위한 지도 기반 강습·행사·장소 탐색 웹 서비스입니다.

**https://windycity.co.kr** — 실제 운영 중인 서비스입니다.

살사, 바차타, 키좀바, 주크, 탱고, 린디합, 웨스트코스트 스윙 등 커플댄스 정보는 인스타그램, 네이버 카페, 카카오 채널에 흩어져 있습니다. 어디에서 무슨 파티가 열리는지 알려면 채널 여러 개를 매번 뒤져야 합니다. 이 프로젝트는 그 정보를 하나의 지도 위로 모으는 것을 목적으로 시작했습니다.

---

## 주요 기능

### 지도 기반 탐색
- 카카오맵 위에 클럽 · 동호회 · 연습실 · 강습/행사를 카테고리별 커스텀 마커로 표시
- 지도를 움직이면 현재 화면 영역(bounds) 안의 항목만 사이드바 목록에 자동 갱신
- 좌표가 겹치는 마커는 숫자 뱃지로 묶어 표시
- 장소·주소 검색으로 지도 위치 이동 (카카오 Places + Geocoder 병렬 호출, 300ms 디바운스)

### 이벤트 · 장소 관리
- 이벤트/장소 등록 · 수정 · 삭제 (본인 소유만 가능)
- 이벤트 유형(소셜파티 / 워크샵 / 페스티벌 / 정기수업 / 공연 / 연습), 장르 복수 선택, 난이도 7단계
- 매주 반복되는 정기 소셜 파티를 위한 반복 이벤트(`is_recurring`, `recurrence_rule`) 지원
- 장소 유형별 상이한 속성 관리 — 클럽(입장료, 바 유무), 연습실(대관료, 거울, 음향, 면적), 학원(체험 수업)
- 이미지 업로드, 슬라이더, 전체화면 뷰어, 모바일 스와이프

### 검색 · 북마크
- 이벤트와 장소를 하나의 결과로 반환하는 통합 검색 API (`item_type` 필드로 구분)
- 사이드바 이중 모드 — 검색어가 없으면 지도 탐색 모드, 입력하면 검색 결과 모드로 자동 전환
- 이벤트/장소 북마크 및 내 저장 목록

### 커뮤니티
- 게시판 (공지사항 / 자유게시판), 마크다운 작성, 고정 공지, 조회수
- 게시글 · 이벤트 · 장소 각각에 댓글

### 계정
- 이메일 회원가입 + 인증 코드 발송 (10분 만료), JWT 인증
- 카카오 · 네이버 소셜 로그인
- 동일 이메일이라도 가입 경로가 다르면 별도 계정으로 취급 (`UNIQUE(email, provider)`)
- 관리자 페이지 — 회원 · 이벤트 · 장소 관리

### 운영
- 봇 대응 메타태그 서버사이드 주입, `robots.txt`, DB에서 동적 생성하는 `sitemap.xml`
- 헬스체크 API (`GET /api/health`, DB 연결 확인 포함) + UptimeRobot 5분 주기 모니터링
- DB 일 단위 백업, 업로드 파일 주 단위 백업

---

## 기술 스택

| 구분 | 사용 기술 |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | MariaDB |
| 인증 | JWT (python-jose), bcrypt (passlib), 카카오·네이버 OAuth |
| Frontend | Vue 3 (Composition API, `<script setup>`), Vue Router, Vite |
| 지도 | 카카오맵 JavaScript SDK |
| 기타 | Pillow (이미지 변환), marked + DOMPurify (마크다운), Gmail SMTP |
| 인프라 | Oracle Cloud (ARM64 Ubuntu 24.04), Nginx, Let's Encrypt, systemd |

---

## 구조

프론트엔드를 Vite로 빌드해 `static/`에 출력하고, FastAPI가 API와 정적 파일을 함께 서빙하는 단일 서버 구성입니다. Nginx가 앞단에서 HTTPS를 처리하고 uvicorn으로 리버스 프록시합니다.

```
브라우저
   │  HTTPS
   ▼
 Nginx  ──리버스 프록시──▶  uvicorn (FastAPI)
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
              /api/*  REST API        static/  (Vue 빌드 결과)
                     │
                     ▼
              SQLAlchemy ──▶ MariaDB
```

### 디렉토리

```
main.py            FastAPI 진입점, 라우터 등록, SPA fallback, robots/sitemap
database.py        SQLAlchemy 엔진 및 세션
models.py          DB 모델 (User, Venue, Event, Media, Post, Comment, Bookmark …)
schemas.py         Pydantic 요청/응답 스키마
auth.py            JWT 발급·검증, 비밀번호 해싱
email_utils.py     인증 메일 발송
routers/
  auth.py          회원가입, 이메일 인증, 로그인, 소셜 로그인, 회원 탈퇴
  events.py        이벤트 CRUD, 미디어, 댓글
  venues.py        장소 CRUD, 미디어, 댓글
  posts.py         게시판 CRUD, 댓글
  bookmarks.py     북마크 등록·해제·조회
  search.py        이벤트+장소 통합 검색
  upload.py        이미지 업로드
  admin.py         관리자 전용 회원·콘텐츠 관리
  feedback.py      피드백 접수
  health.py        헬스체크

frontend/src/
  App.vue          루트 컴포넌트
  router/          Vue Router 라우트 정의
  views/           페이지 단위 컴포넌트 (events, venues, board, admin …)
  components/      KakaoMap, Sidebar, TopBar, 각종 모달
  composables/     useAuth, useEvents, useVenues, useBookmarks 등 상태·API 로직
  utils/           fetch 래퍼, 상수, 마크다운 처리
  assets/styles/   기능별로 분리한 CSS
```

---

## API

모든 엔드포인트는 `/api` 하위에 있습니다. 인증이 필요한 요청은 `Authorization: Bearer {token}` 헤더를 사용합니다.

### 인증 `/api/auth`
| Method | Path | 설명 |
|---|---|---|
| POST | `/register` | 회원가입, 인증 코드 메일 발송 |
| POST | `/verify-email` | 인증 코드 확인 후 JWT 발급 |
| POST | `/resend-code` | 인증 코드 재발송 |
| GET | `/check-nickname` | 닉네임 중복 확인 |
| POST | `/login` | 로그인 |
| GET | `/me` | 내 정보 조회 |
| DELETE | `/me` | 회원 탈퇴 |
| POST | `/kakao`, `/naver` | 소셜 로그인 |
| POST | `/social/register` | 소셜 최초 가입 시 추가 정보 등록 |

### 이벤트 `/api/events` · 장소 `/api/venues`
| Method | Path | 설명 |
|---|---|---|
| GET | `/` | 목록 조회 (날짜, 유형, 장르, 난이도 필터) |
| GET | `/list` | 리스트 페이지용 조회 |
| POST | `/` | 등록 |
| GET | `/{id}` | 상세 조회 |
| PUT | `/{id}` | 수정 (소유자만) |
| DELETE | `/{id}` | 삭제 (소유자만) |
| POST | `/{id}/media` | 미디어 추가 |
| DELETE | `/{id}/media/{media_id}` | 미디어 삭제 |
| GET · POST · PUT · DELETE | `/{id}/comments` | 댓글 |

### 그 외
| Method | Path | 설명 |
|---|---|---|
| GET | `/api/search?q=` | 이벤트 + 장소 통합 검색 |
| POST | `/api/upload/image` | 이미지 업로드 |
| POST · DELETE | `/api/bookmarks/{entity_type}/{entity_id}` | 북마크 등록·해제 |
| GET | `/api/bookmarks/me`, `/me/details` | 내 북마크 |
| GET · POST · PUT · DELETE | `/api/posts` | 게시판 |
| GET · PUT · DELETE | `/api/admin/users`, `/events`, `/venues` | 관리자 |
| GET | `/api/health` | 헬스체크 |

전체 스펙은 서버 실행 후 `/docs`(Swagger UI)에서 확인할 수 있습니다.

---

## 구현하며 다뤄야 했던 것들

**이벤트와 장소의 이질적인 속성**
클럽에는 입장료와 바 유무가, 연습실에는 대관료와 거울·음향·면적이, 학원에는 체험 수업 정보가 필요합니다. 유형마다 테이블을 나누면 조회가 복잡해지고, 컬럼을 전부 합치면 대부분이 NULL이 됩니다. 공통 속성은 컬럼으로 두고 유형별 속성은 nullable 컬럼과 `extra_info` JSON 컬럼으로 처리했습니다.

**반복 이벤트**
정기 소셜 파티는 매주 같은 요일에 열립니다. 인스턴스를 미리 생성해 두면 원본 수정 시 동기화 문제가 생기므로, `recurrence_rule`을 JSON으로 저장하고 조회 시점에 전개하는 방식을 택했습니다.

**지도와 목록의 동기화**
지도를 드래그하거나 확대할 때마다 목록을 갱신해야 하는데, 이동 중에 매번 요청하면 과도한 호출이 발생합니다. 카카오맵 `idle` 이벤트를 기준으로 지도가 멈춘 시점에만 bounds를 읽어 조회하도록 했습니다.

**통합 검색 응답 스키마**
이벤트와 장소는 필드 구성이 다른데 한 리스트로 내려줘야 했습니다. 각 아이템에 `item_type` 판별 필드를 두고 프론트에서 분기해 렌더링하도록 설계했습니다.

**이미지 용량**
PNG 원본을 그대로 저장하면 용량이 커집니다. 업로드 시 Pillow로 JPEG 변환하고, 품질을 90부터 단계적으로 낮추며 3MB 이하가 될 때까지 재인코딩합니다. 투명 배경은 흰색으로 합성합니다.

**SPA와 SEO**
Vue Router의 history 모드는 서버에서 모든 경로를 `index.html`로 넘겨야 하는데, 그러면 크롤러가 빈 페이지를 봅니다. User-Agent로 봇을 판별해 메타태그를 서버에서 주입하고, `sitemap.xml`은 DB의 이벤트·장소·게시글을 읽어 동적으로 생성합니다.

---

## 실행

### 백엔드

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env 작성
# DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
# SECRET_KEY, SMTP 계정, 카카오·네이버 OAuth 키

uvicorn main:app --reload --port 8000
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev     # 개발 서버, /api 요청은 localhost:8000으로 프록시
npm run build   # ../static 으로 빌드, FastAPI가 서빙
```

---

## 개발 현황

운영 중이며 기능을 계속 추가하고 있습니다. 남은 작업과 진행 상태는 [TODO.md](TODO.md)에 정리해 두었습니다.

주요 예정 작업

- 주최자 대시보드 (내 이벤트·장소 일괄 관리)
- 구글 소셜 로그인
- 장소 리뷰·평점, 강사 프로필
- 북마크 이벤트 D-1 알림
- 캘린더 뷰, PWA 지원
- API rate limiting, 보안 헤더, 배포 스크립트 자동화

---

## 라이선스

개인 프로젝트입니다.


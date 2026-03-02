# Windy City (바람난 도시) 프로젝트

## 서비스 개요
살사 댄스 이벤트를 지도 기반으로 찾을 수 있는 웹 서비스.
GTA 맵처럼 지도에서 실시간으로 이벤트를 확인할 수 있는 느낌.

## 사용자 유형
- **이벤트 주최자**: 로그인 후 이벤트 등록/수정/삭제
- **일반 사용자**: 로그인 없이 지도에서 이벤트 조회 및 필터링

## 핵심 기능
- 지도에서 위치 핀 찍어서 이벤트 등록
- 이벤트 날짜/기간 설정
- 이벤트 정보 입력 (제목, 설명, 장소명, 주소 등)
- 지도에서 이벤트 실시간 확인
- 필터링 (날짜, 지역, 이벤트 유형 등)

## 기술 스택
- **Backend**: Python FastAPI
- **Database**: MariaDB
- **Web Server**: Nginx (예정)
- **Server**: OCI Ubuntu 24.04 (VM.Standard.A1.Flex, 4 OCPU, 24GB RAM)
- **지도 API**: 카카오맵 (예정)

## 개발 방식
- **개발 주체**: OCI 서버 (코드 작성 후 SFTP로 즉시 업로드 → 서버에서 실행/테스트)
- **로컬 역할**: VS Code + Claude Code로 코드 작성만 담당
- **로컬 DB 없음**: 모든 DB 작업은 서버 MariaDB 사용
- **테스트**: 브라우저에서 서버 IP로 직접 확인

## 프로젝트 구조
- `main.py` - FastAPI 앱 진입점
- `database.py` - DB 연결 설정 (MariaDB, .env 참조)
- `models.py` - SQLAlchemy DB 모델
- `schemas.py` - Pydantic 요청/응답 스키마
- `auth.py` - JWT 인증 유틸리티
- `routers/` - API 라우터
  - `routers/events.py` - 이벤트 CRUD API
  - `routers/auth.py` - 로그인/회원가입 API
- `static/` - 프론트엔드 파일 (HTML, CSS, JS)
- `.env` - 서버 환경변수 (Git 제외, 서버에만 존재)
- `.env.example` - 환경변수 템플릿 (Git 포함)

## DB 스키마
### users (사용자)
- id, email, hashed_password, nickname, is_organizer, created_at

### events (이벤트)
- id, title, description, location_name, address
- latitude, longitude (지도 좌표)
- start_date, end_date, event_type
- organizer_id (users 외래키)
- created_at

## 서버 정보
- **퍼블릭 IP**: 217.142.229.136
- **리전**: ap-osaka-1 (Japan Central)
- **가용성 도메인**: AD-1
- **결함 도메인**: FD-3
- **인스턴스**: VM.Standard.A1.Flex (ARM64/aarch64)
- **OS**: Canonical Ubuntu 24.04
- **VCN**: vcn-windy-city-server
- **기본 SSH 사용자**: ubuntu

## 개발 환경
- **로컬**: macOS (Apple Silicon)
- **에디터**: VS Code + SFTP 익스텐션 (uploadOnSave: true)
- **AI 도구**: Claude Code + MCP (filesystem, sqlite)
- **형상 관리**: GitHub (git@github.com-mbh77:mbh77/windy-city.git)
- **SSH 키**: ~/.ssh/id_ed25519 (github.com-mbh77 호스트 설정)
- **DB 클라이언트**: DBeaver (SSH 터널링으로 서버 MariaDB 접속)

## 배포 정보
- 포트: 8000 (uvicorn)
- 실행 명령: `cd ~/windy-city && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000`

## 주의사항
- ARM64(aarch64) 환경 호환 패키지 사용
- 코드는 항상 한국어 주석 작성
- `.env` 파일은 서버에만 존재, Git에 올리지 않음
- SECRET_KEY는 반드시 .env에서 관리
- MariaDB 접속은 SSH 터널링 사용 (3306 포트 외부 미개방)

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
- **Database**: SQLite (현재) / MariaDB (전환 검토)
- **Web Server**: Nginx
- **Server**: OCI Ubuntu 24.04 (VM.Standard.A1.Flex, 4 OCPU, 24GB RAM)
- **지도 API**: 카카오맵

## 프로젝트 구조
- `main.py` - FastAPI 앱 진입점
- `database.py` - DB 연결 설정
- `models.py` - SQLAlchemy DB 모델
- `schemas.py` - Pydantic 요청/응답 스키마
- `routers/` - API 라우터
  - `routers/events.py` - 이벤트 CRUD API
  - `routers/auth.py` - 로그인/회원가입 API
- `static/` - 프론트엔드 파일 (HTML, CSS, JS)

## DB 스키마
### users (사용자)
- id, email, password, nickname, is_organizer, created_at

### events (이벤트)
- id, title, description, location_name, address
- latitude, longitude (지도 좌표)
- start_date, end_date
- organizer_id (users 외래키)
- created_at

## 배포
- 서버 IP: 217.142.229.136
- 리전: ap-osaka-1
- 가용성 도메인: AD-1
- 결함 도메인: FD-3
- SFTP 자동 업로드 (uploadOnSave: true)
- 서버에서 uvicorn으로 실행
- 포트: 8000

## 주의사항
- ARM64(aarch64) 환경 호환 패키지 사용
- 이미지: Canonical-Ubuntu-24.04-aarch64-2026.01.29-0
- 인스턴스 모양: VM.Standard.A1.Flex (4 OCPU, 24GB RAM, 4Gbps)
- 기본 SSH 사용자: ubuntu
- VCN: vcn-windy-city-server
- SQLite 파일 위치: ~/windy-city/windy-city.db
- 코드는 항상 한국어 주석 작성

## DB 운영 방향 (초안)
- 현재 운영 DB는 SQLite 유지 (개발/초기 운영 단순화 목적)
- 서버 자원 증설로 MariaDB 전환 검토 가능 상태
- 아직 확정되지 않은 항목:
  - MariaDB 버전
  - 배포 형태 (단일 인스턴스 직접 설치 vs 컨테이너)
  - 백업 정책(주기/보관 기간)
  - 모니터링 항목(커넥션 수, 슬로우 쿼리, 디스크 사용량)
- 전환 확정 시 정리할 내용:
  - SQLAlchemy 연결 문자열 표준화 (`DATABASE_URL`)
  - 의존성 드라이버 확정 (`pymysql` 또는 `mariadb`)
  - 기존 SQLite 데이터 마이그레이션 방식
  - 롤백 절차(문제 발생 시 SQLite 복귀)

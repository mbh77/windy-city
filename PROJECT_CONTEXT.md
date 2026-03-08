# 프로젝트 컨텍스트: Windy City (바람난 도시)

## 1. 프로젝트 개요
- **목적**: 살사 댄스 이벤트를 지도 기반으로 조회/등록하는 웹 서비스.
- **주요 특징**: 실시간 이벤트 핀 확인, 필터링 기능 (날짜, 지역, 유형), 이벤트 주최자 관리 시스템.

## 2. 개발 및 운영 환경 (Single Server Strategy)
이 프로젝트는 OCI(Oracle Cloud Infrastructure) 인스턴스 하나에서 개발(Dev)과 운영(Prod) 환경을 모두 운용합니다.

- **서버 사양**: Ubuntu 24.04 (ARM64), 4 OCPU, 24GB RAM
- **서버 IP**: 217.142.229.136
- **환경 분리 전략**:
  | 구분 | 환경 (Environment) | 디렉토리 경로 | 포트 | DB 스키마 |
  | :--- | :--- | :--- | :--- | :--- |
  | **Dev** | Development | `~/windy-city-dev` | 8000 | `windycity_dev` |
  | **Prod** | Production | `~/windy-city` | 80/8001 | `windycity` |

## 3. 기술 스택
- **Backend**: Python FastAPI
- **Database**: MariaDB (SQLAlchemy ORM 사용)
- **Web Server**: Nginx (Prod 환경 역방향 프록시 예정)
- **Frontend**: Static HTML/JS/CSS (카카오맵 API 연동 예정)
- **Auth**: JWT (JSON Web Token)

## 4. 개발 워크플로우 (Claude Code 필수 지침)
1. **작업 위치**: 모든 개발 작업은 `~/windy-city-dev` 디렉토리 내에서 수행합니다.
2. **개발 방식**: VS Code Remote-SSH를 통해 서버에 직접 접속하여 작업하며, Claude Code 및 MCP 또한 서버 환경에서 구동됩니다.
3. **DB 접속**: 서버 내부 로컬 호스트(`127.0.0.1:3306`)를 통해 MariaDB에 접속합니다. 외부 노출은 금지됩니다.
4. **언어 정책**: 모든 코드 내 주석 및 관련 문서는 **한국어**로 작성합니다.
5. **형상 관리**: `develop` 브랜치에서 작업 후 검증이 완료되면 `main` 브랜치로 병합하여 Prod 환경에 반영합니다.

## 5. 프로젝트 구조 (예정)
- `main.py`: FastAPI 엔트리포인트
- `database.py`: DB 연결 및 세션 관리 (`.env` 참조)
- `models.py`: SQLAlchemy 모델 정의
- `schemas.py`: Pydantic 모델 정의
- `routers/`: API 엔드포인트 분리 (events.py, auth.py)
- `static/`: 프론트엔드 정적 파일
- `.env`: 환경변수 관리 (Git 제외, 서버별 개별 존재)

## 6. 주의 사항
- **ARM64 호환성**: 패키지 설치 시 `aarch64` 환경임을 고려해야 합니다.
- **보안**: `SECRET_KEY` 등 민감 정보는 반드시 `.env`에서 로드하며, `.env.example`을 통해 템플릿만 공유합니다.
- **실시간성**: 지도 기반 서비스이므로 위도/경도 데이터의 유효성을 엄격히 체크합니다.
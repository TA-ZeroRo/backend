# ZeroRo Backend

환경 보호 앱 ZeroRo의 백엔드 API 서버입니다.

## 프로젝트 구조

```
backend/
├── app/                      # FastAPI 메인 애플리케이션
│   ├── __init__.py
│   ├── main.py              # 앱 시작점
│   ├── api/                 # API 엔드포인트
│   │   ├── __init__.py
│   │   ├── util/            # API 유틸리티
│   │   │   ├── __init__.py
│   │   │   ├── exception.py # API 예외 처리 함수 모음
│   │   │   └── util.py      # 유틸리티 함수
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py    # API 라우터 등록
│   │       └── endpoints/   # 기능별 엔드포인트
│   │           ├── __init__.py
│   │           ├── campaign.py      # 캠페인 관리
│   │           ├── character.py     # AI 캐릭터
│   │           ├── community.py     # 커뮤니티 (게시글, 댓글)
│   │           ├── leaderboard.py   # 리더보드
│   │           ├── like.py          # 좋아요 기능
│   │           ├── mission.py       # 미션 관리
│   │           ├── point.py         # 포인트 시스템
│   │           ├── report.py        # 월간 보고서
│   │           ├── users.py         # 사용자 관리
│   │           └── verification.py  # 활동 인증
│   ├── core/                # 핵심 설정
│   │   ├── __init__.py
│   │   └── config.py        # 환경변수, 시크릿 키 등 설정 관리
│   ├── repository/          # 데이터 접근 계층 (Repository Pattern)
│   │   ├── __init__.py
│   │   ├── base_repository.py     # BaseRepository 클래스
│   │   ├── campaign_repository.py
│   │   ├── community_repository.py
│   │   ├── leaderboard_repository.py
│   │   ├── like_repository.py
│   │   ├── mission_repository.py
│   │   ├── report_repository.py
│   │   └── user_repository.py
│   ├── schemas/             # Pydantic 스키마 관리
│   │   ├── __init__.py
│   │   ├── campaign_schemas.py
│   │   ├── community_schemas.py
│   │   ├── leaderboard_schemas.py
│   │   ├── like_schemas.py
│   │   ├── mission_schemas.py
│   │   ├── report_schemas.py
│   │   └── user_schemas.py
│   └── services/            # 비즈니스 로직 계층
│       ├── __init__.py
│       ├── campaign_service.py
│       ├── community_service.py
│       ├── leaderboard_service.py
│       ├── like_service.py
│       ├── mission_service.py
│       ├── report_service.py
│       ├── user_service.py
│       └── verification_service.py
├── requirements.txt          # 프로젝트 의존성 패키지 목록
└── README.md                # 프로젝트 문서
```

## 환경 변수 설정

### 로컬 개발 환경

1. `.env` 파일을 생성하고 다음 환경 변수들을 설정하세요:

```bash
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

## 설치 및 실행

### 로컬 환경

```bash
# Python 3.10+ 설치 확인
python --version
# 만약 Python 3.10+ 아니라면, pip 최신화
python -m pip install --upgrade pip

# venv 생성
python -m venv venv

# 활성화
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행 (TA-ZeroRo\backend 디렉토리에서) 
fastapi dev app/main.py
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 주요 기능

### 핵심 기능
- **사용자 관리** (`users.py`): 사용자 프로필, 지역, 연속 활동일 관리
- **캠페인 관리** (`campaign.py`): 환경 캠페인 목록 조회, 지역/카테고리별 필터링
- **미션 시스템** (`mission.py`): 사용자별 미션 조회, 상태 관리 (진행중/검증중/완료/실패)
- **월간 보고서** (`report.py`): 월간 활동 요약, 캠페인 신청, 미션 완료, 포인트 증감 분석

### 커뮤니티 기능
- **커뮤니티** (`community.py`): 게시글 작성/수정/삭제, 댓글 관리
- **좋아요** (`like.py`): 게시글 좋아요/취소 기능
- **리더보드** (`leaderboard.py`): 지역별/전체 사용자 랭킹 시스템

### 검증 및 보상
- **활동 인증** (`verification.py`): 사진, 퀴즈, 소감문을 통한 환경 보호 활동 검증
- **포인트 시스템** (`point.py`): 활동 보상, 포인트 히스토리 관리
- **AI 캐릭터** (`character.py`): 환경 관련 AI 캐릭터 생성 및 상호작용

## 보안

- API 키는 절대로 코드에 하드코딩하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다
- 환경 변수를 통해 안전하게 API 키를 관리합니다

## 기술 스택

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **AI**: Google Gemini API
- **Language**: Python 3.10

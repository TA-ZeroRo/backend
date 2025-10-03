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
│   │       ├── router.py
│   │       └── endpoints/   # 기능별 엔드포인트
│   │           ├── __init__.py
│   │           ├── character.py
│   │           ├── community.py
│   │           ├── leaderboard.py
│   │           ├── point.py
│   │           ├── users.py
│   │           └── verification.py
│   ├── core/                # 핵심 설정
│   │   ├── __init__.py
│   │   └── config.py        # 환경변수, 시크릿 키 등 설정 관리
│   ├── repository/          # 데이터 접근 계층 (Repository Pattern)
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── character_repository.py
│   │   ├── community_repository.py
│   │   ├── point_repository.py
│   │   └── ...
│   ├── schemas/             # Pydantic 스키마 관리
│   │   ├── __init__.py
│   │   ├── user_schemas.py
│   │   ├── character_schemas.py
│   │   ├── community_schemas.py
│   │   └── ...
│   └── services/            # 비즈니스 로직 (리팩토링됨)
│       ├── __init__.py
│       ├── user_service.py      # 통합된 사용자 서비스
│       ├── character_service.py # 통합된 캐릭터 서비스
│       ├── community_service.py # 통합된 커뮤니티 서비스
│       ├── point_service.py     # 통합된 포인트 서비스
│       ├── verification_service.py # 통합된 검증 서비스
│       └── leaderboard_service.py  # 통합된 리더보드 서비스
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

# 개발 서버 실행
fastapi dev
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 주요 기능

- **사용자 관리**: 사용자 프로필, 포인트 시스템
- **인증 시스템**: 사진, 퀴즈, 소감문을 통한 환경 보호 활동 인증
- **AI 캐릭터**: 환경 관련 AI 캐릭터 생성 및 상호작용
- **커뮤니티**: 게시글 작성, 댓글, 좋아요 기능
- **리더보드**: 사용자 랭킹 시스템
- **이미지 처리**: 환경 보호 활동 이미지 검증

## 보안

- API 키는 절대로 코드에 하드코딩하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다
- 환경 변수를 통해 안전하게 API 키를 관리합니다

## 기술 스택

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **AI**: Google Gemini API
- **Language**: Python 3.10

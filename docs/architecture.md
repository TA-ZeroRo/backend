# Backend Architecture

## 📋 목차
- [개요](#개요)
- [아키텍처 패턴](#아키텍처-패턴)
- [레이어 구조](#레이어-구조)
- [디렉토리 구조](#디렉토리-구조)
- [주요 설계 원칙](#주요-설계-원칙)

---

## 개요

Zeroro 백엔드는 **FastAPI** 기반의 RESTful API 서버로, **Supabase**(PostgreSQL)를 데이터베이스로 사용합니다.

### 기술 스택

| 항목 | 기술 |
|------|------|
| Framework | FastAPI |
| Database | Supabase (PostgreSQL) |
| Language | Python 3.x |
| AI/ML | Google Gemini API, Sentence Transformers |
| Validation | Pydantic |
| Server | Uvicorn (ASGI) |

---

## 아키텍처 패턴

### Layered Architecture (계층형 아키텍처)

```
┌─────────────────────────────────────┐
│      Presentation Layer (API)       │  <- FastAPI Routers
├─────────────────────────────────────┤
│      Business Logic Layer           │  <- Services
├─────────────────────────────────────┤
│      Data Access Layer              │  <- Repositories
├─────────────────────────────────────┤
│      Data Source                    │  <- Supabase (PostgreSQL)
└─────────────────────────────────────┘
```

### 주요 특징

1. **단방향 의존성**: 상위 레이어 → 하위 레이어
2. **관심사의 분리 (Separation of Concerns)**: 각 레이어는 명확한 책임을 가짐
3. **Repository Pattern**: 데이터 액세스 로직을 추상화

---

## 레이어 구조

### 1. API Layer (Presentation)

**위치**: `app/api/v1/endpoints/`

**책임**:
- HTTP 요청/응답 처리
- 입력 유효성 검증 (Pydantic)
- 에러 핸들링
- Service 계층 호출

**예시**:
```python
# community.py
@router.post("/posts")
async def create_community_post(post_data: PostCreate):
    try:
        return await community_service.create_post(post_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Service Layer (Business Logic)

**위치**: `app/services/`

**책임**:
- 비즈니스 로직 처리
- 여러 Repository 조합
- 데이터 변환 및 검증
- 트랜잭션 관리

**예시**:
```python
# like_service.py
async def create_like(self, user_id: UUID, post_id: int):
    # 1. 중복 체크 (비즈니스 규칙)
    existing_like = await self.like_repo.get_like_by_user_and_post(user_id, post_id)
    if existing_like:
        raise HTTPException(status_code=409, detail="이미 좋아요를 눌렀습니다.")

    # 2. 좋아요 생성
    created_like = await self.like_repo.create_like(like_data)

    # 3. 게시글 좋아요 수 증가 (여러 Repository 조합)
    await self.community_repo.increment_likes(post_id)

    return {"message": "좋아요가 성공적으로 추가되었습니다.", "like": created_like}
```

### 3. Repository Layer (Data Access)

**위치**: `app/repository/`

**책임**:
- 데이터베이스 CRUD 작업
- 쿼리 실행
- Supabase API 호출
- 데이터 매핑

**예시**:
```python
# community_repository.py
async def increment_likes(self, post_id: int) -> bool:
    """Supabase RPC 함수로 좋아요 수 증가"""
    response = (
        self.supabase
        .rpc("increment_likes", {"post_id": post_id})
        .execute()
    )
    return response.data is not None
```

### 4. Schema Layer (Data Validation)

**위치**: `app/schemas/`

**책임**:
- 요청/응답 데이터 모델 정의
- Pydantic을 사용한 타입 검증
- 직렬화/역직렬화

**예시**:
```python
# community_schemas.py
class PostCreate(BaseModel):
    title: str
    user_id: UUID
    content: str
    image_url: Optional[str] = None
```

---

## 디렉토리 구조

```
Back-End/
├── app/
│   ├── main.py                     # FastAPI 앱 진입점
│   │
│   ├── api/                        # API 레이어
│   │   ├── v1/
│   │   │   ├── router.py          # 라우터 통합
│   │   │   └── endpoints/         # 엔드포인트별 라우터
│   │   │       ├── users.py
│   │   │       ├── community.py
│   │   │       ├── like.py
│   │   │       ├── point.py
│   │   │       ├── character.py
│   │   │       ├── leaderboard.py
│   │   │       └── verification.py
│   │   └── util/                  # 유틸리티
│   │
│   ├── services/                   # 비즈니스 로직
│   │   ├── user_service.py
│   │   ├── community_service.py
│   │   ├── like_service.py
│   │   ├── point_service.py
│   │   ├── character_service.py
│   │   ├── leaderboard_service.py
│   │   └── verification_service.py
│   │
│   ├── repository/                 # 데이터 액세스
│   │   ├── base_repository.py     # BaseRepository (공통 CRUD)
│   │   ├── user_repository.py
│   │   ├── community_repository.py
│   │   ├── like_repository.py
│   │   ├── point_repository.py
│   │   ├── character_repository.py
│   │   └── leaderboard_repository.py
│   │
│   ├── schemas/                    # Pydantic 스키마
│   │   ├── user_schemas.py
│   │   ├── community_schemas.py
│   │   ├── like_schemas.py
│   │   ├── point_schemas.py
│   │   ├── character_schemas.py
│   │   └── leaderboard_schemas.py
│   │
│   └── core/                       # 핵심 설정
│       └── config.py               # 환경 변수 관리
│
├── requirements.txt                # 패키지 의존성
└── .env                            # 환경 변수 (gitignore)
```

---

## 주요 설계 원칙

### 1. Repository Pattern

모든 데이터 액세스는 Repository를 통해 이루어집니다.

```python
# BaseRepository - 공통 CRUD 메서드 제공
class BaseRepository:
    async def find_by_id(self, table: str, id_value: str)
    async def find_all(self, table: str, filters: Optional[Dict])
    async def create(self, table: str, data: Dict)
    async def update(self, table: str, id_value: str, data: Dict)
    async def delete(self, table: str, id_value: str)
```

각 도메인별 Repository는 BaseRepository를 상속받아 도메인 특화 메서드를 추가합니다.

### 2. 관심사의 분리 (Separation of Concerns)

**예시**: Community와 Like의 분리

- **Community 모듈**: 게시글, 댓글 관리
- **Like 모듈**: 좋아요 관리 (독립적으로 확장 가능)
- **연결 지점**: LikeService가 CommunityRepository의 `increment_likes()`/`decrement_likes()` 호출

```
Like Service
    ↓ (생성 시)
LikeRepository.create_like()
    ↓
CommunityRepository.increment_likes()  ← Supabase RPC
```

### 3. Supabase RPC 사용

동시성 문제 해결을 위해 원자적 업데이트가 필요한 경우 Supabase RPC 함수를 사용합니다.

```python
# ❌ 동시성 문제 발생 가능
post = await get_post(post_id)
new_count = post["likes_count"] + 1
await update_post(post_id, {"likes_count": new_count})

# ✅ DB 레벨에서 원자적 실행
await supabase.rpc("increment_likes", {"post_id": post_id})
```

### 4. 단방향 의존성

```
API Layer
    ↓
Service Layer
    ↓
Repository Layer
    ↓
Database
```

- 하위 레이어는 상위 레이어를 알지 못함
- Repository는 Service를 호출하지 않음
- Service는 API를 호출하지 않음

### 5. 환경 변수 관리

모든 민감한 설정은 `.env` 파일에서 관리합니다.

```python
# app/core/config.py
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

---

## 모듈별 책임

| 모듈 | 책임 |
|------|------|
| **Users** | 사용자 CRUD, 프로필 관리 |
| **Community** | 게시글, 댓글 CRUD |
| **Like** | 좋아요 생성/삭제, 좋아요 상태 조회 |
| **Point** | 포인트 로그 생성, 날짜별 조회 |
| **Character** | AI 캐릭터 응답 생성, 환경 관련성 분석 |
| **Leaderboard** | 리더보드 순위 조회 |
| **Verification** | 이미지 검증, 행동 인증, 퀴즈 생성 |

---

## API 버전 관리

현재 API 버전: `v1`

```
/api/v1/users
/api/v1/community
/api/v1/like
/api/v1/point
...
```

향후 Breaking Change가 필요한 경우 `v2`를 추가하여 하위 호환성을 유지합니다.

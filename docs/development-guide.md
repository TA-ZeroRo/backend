# Backend Development Guide

## 📋 목차
- [환경 설정](#환경-설정)
- [프로젝트 구조](#프로젝트-구조)
- [개발 워크플로우](#개발-워크플로우)
- [코딩 컨벤션](#코딩-컨벤션)
- [새로운 기능 추가하기](#새로운-기능-추가하기)
- [테스트](#테스트)
- [배포](#배포)

---

## 환경 설정

### 필수 요구사항

- Python 3.10+
- pip
- Supabase 계정
- Google Gemini API 키

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd zeroro/Back-End
```

### 2. 가상 환경 생성 (권장)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env` 파일 생성:

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

**중요**: `.env` 파일은 절대 Git에 커밋하지 마세요!

### 5. 서버 실행

**개발 모드** (Hot reload):
```bash
fastapi dev app/main.py
```

**프로덕션 모드**:
```bash
fastapi run app/main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 6. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 프로젝트 구조

```
Back-End/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── api/                 # API 엔드포인트
│   ├── services/            # 비즈니스 로직
│   ├── repository/          # 데이터 액세스
│   ├── schemas/             # Pydantic 모델
│   └── core/                # 설정 및 유틸리티
├── requirements.txt         # 패키지 의존성
└── .env                     # 환경 변수
```

자세한 내용은 [architecture.md](./architecture.md)를 참고하세요.

---

## 개발 워크플로우

### 1. 브랜치 전략

```
main          - 프로덕션 코드
develop       - 개발 브랜치
feature/*     - 새로운 기능
bugfix/*      - 버그 수정
```

### 2. 개발 사이클

1. **이슈 생성** (GitHub Issues)
2. **브랜치 생성**: `git checkout -b feature/issue-123`
3. **코드 작성** + **테스트**
4. **커밋**: 의미 있는 커밋 메시지 작성
5. **푸시** + **Pull Request 생성**
6. **코드 리뷰**
7. **머지**

---

## 코딩 컨벤션

### 파일 및 디렉토리 명명

- **파일명**: `snake_case.py` (예: `user_service.py`)
- **클래스명**: `PascalCase` (예: `UserService`)
- **함수/변수명**: `snake_case` (예: `get_user_by_id`)
- **상수**: `UPPER_SNAKE_CASE` (예: `GEMINI_API_KEY`)

### Docstring

모든 public 함수와 클래스에는 docstring을 작성합니다.

```python
async def get_user_by_id(user_id: UUID) -> Dict[str, Any]:
    """
    사용자 ID로 사용자 정보를 조회합니다.

    Parameters:
    - user_id (UUID): 사용자 ID

    Returns:
    - Dict[str, Any]: 사용자 정보

    Raises:
    - HTTPException: 사용자를 찾을 수 없는 경우
    """
```

### Type Hints

모든 함수 매개변수와 반환 값에 타입 힌트를 사용합니다.

```python
async def create_post(self, post_data: PostCreate) -> Dict[str, Any]:
    ...
```

### 에러 핸들링

```python
@router.post("/posts")
async def create_post(post_data: PostCreate):
    try:
        return await community_service.create_post(post_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Import 순서

```python
# 1. 표준 라이브러리
from typing import Optional, Dict, Any
from uuid import UUID

# 2. 서드파티 라이브러리
from fastapi import APIRouter, HTTPException

# 3. 로컬 모듈
from app.services.user_service import UserService
from app.schemas.user_schemas import UserCreate
```

---

## 새로운 기능 추가하기

### 예시: `Article` 모듈 추가

#### 1. Schema 정의

`app/schemas/article_schemas.py`:
```python
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class ArticleCreate(BaseModel):
    title: str
    user_id: UUID
    content: str
    image_url: Optional[str] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
```

#### 2. Repository 생성

`app/repository/article_repository.py`:
```python
from typing import Optional, List, Dict, Any
from app.repository.base_repository import BaseRepository

class ArticleRepository(BaseRepository):
    TABLE_NAME = "articles"

    async def get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        return await self.find_by_id(self.TABLE_NAME, str(article_id))

    async def get_all_articles(self) -> List[Dict[str, Any]]:
        return await self.find_all(self.TABLE_NAME)

    async def create_article(self, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.create(self.TABLE_NAME, article_data)

    async def update_article(self, article_id: int, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.update(self.TABLE_NAME, str(article_id), article_data)

    async def delete_article(self, article_id: int) -> bool:
        return await self.delete(self.TABLE_NAME, str(article_id))
```

#### 3. Service 생성

`app/services/article_service.py`:
```python
from fastapi import HTTPException
from typing import Dict, Any, List
from app.repository.article_repository import ArticleRepository
from app.schemas.article_schemas import ArticleCreate, ArticleUpdate

class ArticleService:
    def __init__(self):
        self.article_repo = ArticleRepository()

    async def get_all_articles(self) -> Dict[str, List[Dict[str, Any]]]:
        articles = await self.article_repo.get_all_articles()
        return {"articles": articles}

    async def create_article(self, article_data: ArticleCreate) -> Dict[str, Any]:
        insert_data = {
            "title": article_data.title,
            "user_id": str(article_data.user_id),
            "content": article_data.content
        }

        if article_data.image_url:
            insert_data["image_url"] = article_data.image_url

        created_article = await self.article_repo.create_article(insert_data)
        if not created_article:
            raise HTTPException(status_code=500, detail="아티클 생성에 실패했습니다.")

        return {"article": created_article}

    async def update_article(self, article_id: int, article_data: ArticleUpdate) -> Dict[str, Any]:
        update_data = {k: v for k, v in article_data.model_dump().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="업데이트할 데이터가 없습니다.")

        updated_article = await self.article_repo.update_article(article_id, update_data)
        if not updated_article:
            raise HTTPException(status_code=500, detail="아티클 수정에 실패했습니다.")

        return {"article": updated_article}

    async def delete_article(self, article_id: int) -> Dict[str, str]:
        success = await self.article_repo.delete_article(article_id)
        if not success:
            raise HTTPException(status_code=500, detail="아티클 삭제에 실패했습니다.")

        return {"message": "아티클이 성공적으로 삭제되었습니다."}
```

#### 4. API Endpoint 생성

`app/api/v1/endpoints/article.py`:
```python
from fastapi import APIRouter, HTTPException
from app.services.article_service import ArticleService
from app.schemas.article_schemas import ArticleCreate, ArticleUpdate

router = APIRouter()
article_service = ArticleService()

@router.get("/")
async def get_articles():
    """모든 아티클을 가져옵니다."""
    try:
        return await article_service.get_all_articles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_article(article_data: ArticleCreate):
    """새로운 아티클을 생성합니다."""
    try:
        return await article_service.create_article(article_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{article_id}")
async def update_article(article_id: int, article_data: ArticleUpdate):
    """아티클을 수정합니다."""
    try:
        return await article_service.update_article(article_id, article_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{article_id}")
async def delete_article(article_id: int):
    """아티클을 삭제합니다."""
    try:
        return await article_service.delete_article(article_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 5. Router 등록

`app/api/v1/router.py`:
```python
from fastapi import APIRouter
from app.api.v1.endpoints import article, community, ...  # article 추가

router = APIRouter()
router.include_router(article.router, prefix="/article")  # 추가
router.include_router(community.router, prefix="/community")
...
```

#### 6. 테스트

```bash
# 서버 실행
fastapi dev app/main.py

# Swagger UI에서 테스트: http://localhost:8000/docs
```

---

## 테스트

### 단위 테스트 (TODO)

```bash
pytest tests/
```

### API 테스트

1. **Swagger UI**: http://localhost:8000/docs
2. **Postman**: API 콜렉션 import
3. **curl**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/users/{user_id}"
   ```

---

## 배포

### 프로덕션 서버 실행

```bash
fastapi run app/main.py
```

### 환경 변수 확인

프로덕션 환경에서는 다음 환경 변수가 설정되어야 합니다:
- `GEMINI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### CORS 설정

프로덕션 도메인을 `app/main.py`의 `origins`에 추가:

```python
origins = [
    "http://localhost",
    "https://localhost:8000",
    "https://your-production-domain.com"  # 추가
]
```

---

## 자주 하는 실수

### ❌ Service에서 직접 Supabase 호출

```python
# 잘못된 예
class UserService:
    def __init__(self):
        self.supabase = create_client(...)  # ❌
```

```python
# 올바른 예
class UserService:
    def __init__(self):
        self.user_repo = UserRepository()  # ✅
```

### ❌ Repository에서 비즈니스 로직 처리

```python
# 잘못된 예 (Repository에서 중복 체크)
async def create_user(self, user_data):
    if await self.check_duplicate_email(user_data["email"]):  # ❌
        raise HTTPException(...)
```

```python
# 올바른 예 (Service에서 중복 체크)
async def create_user(self, user_data: UserCreate):
    if await self.user_repo.get_by_email(user_data.email):  # ✅
        raise HTTPException(...)
    return await self.user_repo.create_user(...)
```

### ❌ .env 파일 커밋

```bash
# .gitignore에 추가 필수
.env
```

---

## 도움말

- **Architecture**: [architecture.md](./architecture.md)
- **API Reference**: [api-reference.md](./api-reference.md)
- **Database Schema**: [database-schema.md](./database-schema.md)
- **FastAPI 공식 문서**: https://fastapi.tiangolo.com/
- **Supabase 공식 문서**: https://supabase.com/docs

# API Reference

## 📋 목차
- [Base URL](#base-url)
- [인증](#인증)
- [공통 응답 형식](#공통-응답-형식)
- [API 엔드포인트](#api-엔드포인트)
  - [Users](#users)
  - [Community](#community)
  - [Like](#like)
  - [Point](#point)
  - [Character](#character)
  - [Leaderboard](#leaderboard)
  - [Verification](#verification)

---

## Base URL

```
http://localhost:8000/api/v1
```

프로덕션: `https://your-domain.com/api/v1`

---

## 인증

현재 버전에서는 인증이 구현되지 않았습니다. (TODO)

---

## 공통 응답 형식

### 성공 응답

```json
{
  "message": "성공 메시지",
  "data": { ... }
}
```

### 에러 응답

```json
{
  "detail": "에러 메시지"
}
```

### HTTP 상태 코드

| 코드 | 의미 |
|------|------|
| 200 | 성공 |
| 201 | 생성 성공 |
| 400 | 잘못된 요청 |
| 404 | 리소스를 찾을 수 없음 |
| 409 | 중복 (Conflict) |
| 500 | 서버 에러 |

---

## API 엔드포인트

---

## Users

사용자 관리 API

### 1. 사용자 생성

**Endpoint**: `POST /users/`

**Request Body**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "user_img": "https://example.com/avatar.jpg"
}
```

**Response** (200):
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "user_img": "https://example.com/avatar.jpg",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### 2. 사용자 조회

**Endpoint**: `GET /users/{user_id}`

**Path Parameters**:
- `user_id` (UUID): 사용자 ID

**Response** (200):
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "user_img": "https://example.com/avatar.jpg",
    "total_point": 150,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### 3. 사용자 수정

**Endpoint**: `PUT /users/{user_id}`

**Path Parameters**:
- `user_id` (UUID): 사용자 ID

**Request Body** (모두 선택사항):
```json
{
  "username": "new_username",
  "email": "new_email@example.com",
  "user_img": "https://example.com/new_avatar.jpg"
}
```

**Response** (200):
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "new_username",
    ...
  }
}
```

---

### 4. 사용자 삭제

**Endpoint**: `DELETE /users/{user_id}`

**Path Parameters**:
- `user_id` (UUID): 사용자 ID

**Response** (200):
```json
{
  "message": "사용자가 성공적으로 삭제되었습니다."
}
```

---

## Community

커뮤니티 게시글 및 댓글 관리 API

### 게시글 API

#### 1. 게시글 목록 조회

**Endpoint**: `GET /community/posts`

**Query Parameters**:
- `offset` (int, 필수): 페이지네이션 시작 인덱스 (0부터 시작)
- `user_id` (UUID, 선택): 특정 사용자의 게시글만 필터링

**Request Example**:
```
GET /community/posts?offset=0&user_id=550e8400-e29b-41d4-a716-446655440000
```

**Response** (200):
```json
{
  "posts": [
    {
      "id": 1,
      "title": "제로 웨이스트 시작하기",
      "content": "오늘부터 텀블러를 사용하기 시작했어요!",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "likes_count": 15,
      "image_url": "https://example.com/image.jpg",
      "created_at": "2024-01-01T00:00:00Z",
      "profiles": {
        "username": "john_doe",
        "user_img": "https://example.com/avatar.jpg"
      }
    },
    ...
  ]
}
```

**Notes**:
- 한 번에 10개의 게시글을 반환합니다.
- `offset=0`: 1~10번째 게시글
- `offset=10`: 11~20번째 게시글

---

#### 2. 게시글 생성

**Endpoint**: `POST /community/posts`

**Request Body**:
```json
{
  "title": "제로 웨이스트 시작하기",
  "content": "오늘부터 텀블러를 사용하기 시작했어요!",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "image_url": "https://example.com/image.jpg"  // 선택사항
}
```

**Response** (200):
```json
{
  "post": {
    "id": 1,
    "title": "제로 웨이스트 시작하기",
    "content": "오늘부터 텀블러를 사용하기 시작했어요!",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "likes_count": 0,
    "image_url": "https://example.com/image.jpg",
    "created_at": "2024-01-01T00:00:00Z",
    "profiles": {
      "username": "john_doe",
      "user_img": "https://example.com/avatar.jpg"
    }
  }
}
```

---

#### 3. 게시글 수정

**Endpoint**: `PUT /community/posts/{post_id}`

**Path Parameters**:
- `post_id` (int): 게시글 ID

**Request Body** (모두 선택사항):
```json
{
  "title": "수정된 제목",
  "content": "수정된 내용",
  "image_url": "https://example.com/new_image.jpg"
}
```

**Response** (200):
```json
{
  "post": {
    "id": 1,
    "title": "수정된 제목",
    ...
  }
}
```

---

#### 4. 게시글 삭제

**Endpoint**: `DELETE /community/posts/{post_id}`

**Path Parameters**:
- `post_id` (int): 게시글 ID

**Response** (200):
```json
{
  "message": "게시글이 성공적으로 삭제되었습니다."
}
```

---

### 댓글 API

#### 1. 댓글 목록 조회

**Endpoint**: `GET /community/posts/{post_id}/comments`

**Path Parameters**:
- `post_id` (int): 게시글 ID

**Response** (200):
```json
{
  "comments": [
    {
      "id": 1,
      "post_id": 1,
      "content": "좋은 실천이네요!",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2024-01-01T00:00:00Z",
      "profiles": {
        "username": "jane_doe",
        "user_img": "https://example.com/avatar2.jpg"
      }
    },
    ...
  ]
}
```

---

#### 2. 댓글 생성

**Endpoint**: `POST /community/posts/{post_id}/comments`

**Path Parameters**:
- `post_id` (int): 게시글 ID

**Request Body**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "좋은 실천이네요!"
}
```

**Response** (200):
```json
{
  "comment": {
    "id": 1,
    "post_id": 1,
    "content": "좋은 실천이네요!",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2024-01-01T00:00:00Z",
    "profiles": {
      "username": "jane_doe",
      "user_img": "https://example.com/avatar2.jpg"
    }
  }
}
```

---

#### 3. 댓글 수정

**Endpoint**: `PUT /community/posts/{post_id}/comments/{comment_id}`

**Path Parameters**:
- `post_id` (int): 게시글 ID
- `comment_id` (int): 댓글 ID

**Request Body**:
```json
"수정된 댓글 내용"
```

**Note**: Request Body는 단순 문자열입니다.

**Response** (200):
```json
{
  "comment": {
    "id": 1,
    "content": "수정된 댓글 내용",
    ...
  }
}
```

---

#### 4. 댓글 삭제

**Endpoint**: `DELETE /community/posts/{post_id}/comments/{comment_id}`

**Path Parameters**:
- `post_id` (int): 게시글 ID
- `comment_id` (int): 댓글 ID

**Response** (200):
```json
{
  "message": "댓글이 성공적으로 삭제되었습니다."
}
```

---

## Like

게시글 좋아요 관리 API

### 1. 좋아요 추가

**Endpoint**: `POST /like`

**Query Parameters**:
- `post_id` (int): 게시글 ID
- `user_id` (UUID): 사용자 ID

**Request Example**:
```
POST /like?post_id=1&user_id=550e8400-e29b-41d4-a716-446655440000
```

**Response** (200):
```json
{
  "message": "좋아요가 성공적으로 추가되었습니다.",
  "like": {
    "id": 1,
    "post_id": 1,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Error** (409):
```json
{
  "detail": "이미 좋아요를 눌렀습니다."
}
```

**Notes**:
- 좋아요 추가 시 게시글의 `likes_count`가 자동으로 증가합니다.

---

### 2. 좋아요 삭제

**Endpoint**: `DELETE /like`

**Query Parameters**:
- `post_id` (int): 게시글 ID
- `user_id` (UUID): 사용자 ID

**Request Example**:
```
DELETE /like?post_id=1&user_id=550e8400-e29b-41d4-a716-446655440000
```

**Response** (200):
```json
{
  "message": "좋아요가 성공적으로 삭제되었습니다."
}
```

**Error** (404):
```json
{
  "detail": "좋아요를 찾을 수 없습니다."
}
```

**Notes**:
- 좋아요 삭제 시 게시글의 `likes_count`가 자동으로 감소합니다.

---

### 3. 사용자가 좋아요한 게시글 ID 목록 조회

**Endpoint**: `GET /like`

**Query Parameters**:
- `user_id` (UUID): 사용자 ID
- `post_ids` (List[int]): 확인할 게시글 ID 목록

**Request Example**:
```
GET /like?user_id=550e8400-e29b-41d4-a716-446655440000&post_ids=1&post_ids=2&post_ids=3
```

**Response** (200):
```json
{
  "liked_post_ids": [1, 3]
}
```

**Use Case**:
- 게시글 목록을 표시할 때, 사용자가 어떤 게시글에 좋아요를 눌렀는지 확인
- 프론트엔드에서 좋아요 버튼 상태를 표시하는 데 사용

---

## Point

사용자 포인트 관리 API

### 1. 포인트 로그 생성

**Endpoint**: `POST /point/{user_id}`

**Path Parameters**:
- `user_id` (UUID): 사용자 ID

**Query Parameters**:
- `point` (int): 추가할 포인트 값

**Request Example**:
```
POST /point/550e8400-e29b-41d4-a716-446655440000?point=50
```

**Response** (200):
```json
{
  "message": "포인트 로그가 성공적으로 생성되었습니다.",
  "log": {
    "id": 1,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "point": 50,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Notes**:
- 포인트 로그 생성 시 사용자의 `total_point`가 자동으로 업데이트됩니다.

---

### 2. 사용자 포인트 로그 조회 (날짜별)

**Endpoint**: `GET /point/{user_id}`

**Path Parameters**:
- `user_id` (UUID): 사용자 ID

**Response** (200):
```json
[
  {
    "date": "2024-01-01",
    "score": 100
  },
  {
    "date": "2024-01-02",
    "score": 50
  },
  ...
]
```

**Notes**:
- 날짜별로 포인트 합계를 반환합니다.
- 프론트엔드에서 그래프로 표시하는 데 사용됩니다.

---

## Character

AI 캐릭터 관련 API

### 1. 환경 관련성 분석

**Endpoint**: `POST /character/generate`

**Query Parameters**:
- `text` (str): 분석할 텍스트

**Request Example**:
```
POST /character/generate?text=오늘 텀블러를 사용했어요
```

**Response** (200):
```json
{
  "result": {
    "is_related": true,
    "confidence": 0.95,
    "category": "재사용",
    "response": "정말 좋은 실천이에요! 텀블러 사용은 일회용 컵을 줄이는 가장 쉬운 방법이랍니다."
  }
}
```

**Notes**:
- Google Gemini API를 사용하여 텍스트가 환경과 관련이 있는지 분석합니다.
- AI 캐릭터의 응답을 생성합니다.

---

## Leaderboard

리더보드 순위 API

### 1. 리더보드 순위 조회

**Endpoint**: `GET /leaderboard/ranking`

**Response** (200):
```json
{
  "rankings": [
    {
      "rank": 1,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john_doe",
      "user_img": "https://example.com/avatar.jpg",
      "total_point": 1500
    },
    {
      "rank": 2,
      "user_id": "660e8400-e29b-41d4-a716-446655440001",
      "username": "jane_doe",
      "user_img": "https://example.com/avatar2.jpg",
      "total_point": 1200
    },
    ...
  ]
}
```

**Notes**:
- `total_point` 기준 내림차순으로 정렬됩니다.

---

## Verification

이미지 및 행동 인증 API

### 1. 이미지 인증

**Endpoint**: `POST /verification/image`

**Request Type**: `multipart/form-data`

**Form Fields**:
- `image` (File): 업로드할 이미지 파일 (JPEG, PNG, 최대 10MB)
- `main_category_index` (int): 메인 카테고리 인덱스
- `sub_category_index` (int): 서브 카테고리 인덱스

**Request Example** (curl):
```bash
curl -X POST "http://localhost:8000/api/v1/verification/image" \
  -F "image=@/path/to/image.jpg" \
  -F "main_category_index=0" \
  -F "sub_category_index=1"
```

**Response** (200):
```json
{
  "result": {
    "verified": true,
    "confidence": 0.92,
    "message": "인증에 성공했습니다."
  }
}
```

**Error** (400):
```json
{
  "detail": "유효한 이미지 파일이 아닙니다. (지원 형식: JPEG, PNG)"
}
```

**Notes**:
- Sentence Transformers를 사용하여 이미지를 분석합니다.
- 카테고리에 맞는 이미지인지 검증합니다.

---

### 2. 행동 인증 생성

**Endpoint**: `POST /verification/behavior`

**Request Body**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "behavior_type": "recycle",
  "description": "플라스틱 분리수거"
}
```

**Response** (200):
```json
{
  "result": {
    "id": 1,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "behavior_type": "recycle",
    "description": "플라스틱 분리수거",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

### 3. O/X 퀴즈 생성

**Endpoint**: `POST /verification/quiz`

**Response** (200):
```json
{
  "result": {
    "question": "플라스틱 뚜껑도 분리수거해야 한다.",
    "answer": true,
    "explanation": "플라스틱 뚜껑은 본체와 분리하여 각각 분리수거해야 합니다."
  }
}
```

**Notes**:
- Google Gemini API를 사용하여 환경 관련 O/X 퀴즈를 생성합니다.

---

## 통합 테스트 예제

### 게시글 작성 → 좋아요 → 댓글 작성 워크플로우

```bash
# 1. 게시글 작성
curl -X POST "http://localhost:8000/api/v1/community/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "제로 웨이스트 시작",
    "content": "오늘부터 텀블러 사용!",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
# 응답: post_id = 1

# 2. 좋아요 추가
curl -X POST "http://localhost:8000/api/v1/like?post_id=1&user_id=660e8400-e29b-41d4-a716-446655440001"

# 3. 댓글 작성
curl -X POST "http://localhost:8000/api/v1/community/posts/1/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "content": "좋은 실천이네요!"
  }'
```

---

## Swagger UI

모든 API는 Swagger UI에서 테스트할 수 있습니다:
```
http://localhost:8000/docs
```

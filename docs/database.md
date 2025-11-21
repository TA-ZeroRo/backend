# Database Schema Analysis & Migration Guide

> **작성일**: 2025-10-10
> **대상 프로젝트**: Zeroro (Frontend Riverpod + Supabase)
> **목적**: Frontend Domain Model과 Supabase DB 스키마 간의 차이점 분석 및 동기화 가이드

---

## 📊 개요

본 문서는 `frontend/lib/domain/model/` 디렉토리의 모델들과 Supabase의 실제 DB 스키마를 비교하여, 마이그레이션 및 동기화가 필요한 항목들을 정리한 문서입니다.

### Supabase 프로젝트 정보

- **Project ID**: `aldghxocvhbscghaztfk`
- **Region**: `ap-northeast-2` (Seoul)
- **Database**: PostgreSQL 17.6.1
- **Status**: ACTIVE_HEALTHY

---

## 1. 모델별 상세 비교 분석

### 1.1 Profile Model

#### Frontend Model (`profile_model.dart`)

```dart
class Profile {
  final String userId;
  final String username;
  final String? userImg;
  final int totalPoints;
  final int continuousDays;
  final DateTime? birthDate;      // ⚠️ DB에 없음
  final String? region;            // ⚠️ DB에 없음
}
```

#### Supabase Schema (`profiles` table)

```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY,
  username TEXT UNIQUE,
  total_points INTEGER DEFAULT 0,
  continuous_days INTEGER DEFAULT 0,
  last_active_at TIMESTAMPTZ,    -- ⚠️ 모델에 없음
  created_at TIMESTAMPTZ DEFAULT NOW(),
  user_img TEXT
);
```

#### 🔧 필요한 변경사항

**DB 스키마 수정:**

```sql
ALTER TABLE profiles
  ADD COLUMN birth_date DATE,
  ADD COLUMN region TEXT;
```

**Frontend 모델 수정:**

```dart
class Profile {
  // ... 기존 필드 ...
  final DateTime? lastActiveAt;  // 추가
  final DateTime createdAt;      // 추가
}
```

---

### 1.2 Post Model

#### Frontend Model (`post.dart`)

```dart
@freezed
abstract class Post with _$Post {
  const factory Post({
    required int id,
    required String userId,
    required String title,
    required String content,
    String? imageUrl,
    required int likesCount,
    required String createdAt,
    required String username,
    String? userImg,
    // ⚠️ commentsCount 누락
  }) = _Post;
}
```

#### Supabase Schema (`posts` table)

```sql
CREATE TABLE posts (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  image_url TEXT,
  likes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,  -- ⚠️ 모델에 없음
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 🔧 필요한 변경사항

**Frontend 모델 수정:**

```dart
@freezed
abstract class Post with _$Post {
  const factory Post({
    // ... 기존 필드 ...
    @Default(0) int commentsCount,  // 추가
  }) = _Post;
}
```

---

### 1.3 Comment Model

#### Frontend Model (`comment.dart`)

```dart
@freezed
abstract class Comment with _$Comment {
  const factory Comment({
    required int id,
    required int postId,
    required String userId,
    required String content,
    required DateTime createdAt,
    required String username,
    String? userImg,
  }) = _Comment;
}
```

#### Supabase Schema (`comments` table)

```sql
CREATE TABLE comments (
  id BIGSERIAL PRIMARY KEY,
  post_id BIGINT NOT NULL REFERENCES posts(id),
  user_id UUID NOT NULL REFERENCES profiles(id),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### ✅ 상태

- 구조적으로 일치
- `username`, `userImg`는 JOIN을 통해 가져오는 필드 (정상)

---

### 1.4 Conversation Model ⚠️ **구조 불일치**

#### Frontend Model (`conversation.dart`)

```dart
@freezed
abstract class Conversation with _$Conversation {
  const factory Conversation({
    required String id,
    required String title,              // ⚠️ DB에 없음
    required List<ChatMessage> messages, // ⚠️ 별도 테이블로 분리됨
    required DateTime lastUpdated,
  }) = _Conversation;
}
```

#### Supabase Schema (`conversations` table)

```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,              -- ⚠️ UUID 타입으로 변경 필요
  character_id TEXT,                  -- ⚠️ 모델에 없음
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 메시지는 별도 테이블
CREATE TABLE conversation_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id),
  role TEXT CHECK (role IN ('user', 'model')),
  parts JSONB NOT NULL,  -- MessagePart 배열
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 🔧 필요한 변경사항

**1. DB 스키마 수정:**

```sql
-- conversations 테이블 수정
ALTER TABLE conversations
  ADD COLUMN title TEXT,
  ALTER COLUMN user_id TYPE UUID USING user_id::uuid;

-- user_id를 UUID로 안전하게 변경하는 마이그레이션
-- (기존 데이터가 있다면 데이터 마이그레이션 필요)
```

**2. Frontend 모델 완전 재구성:**

```dart
@freezed
abstract class Conversation with _$Conversation {
  const factory Conversation({
    required String id,
    required String userId,         // 추가
    String? characterId,            // 추가
    required String title,
    required DateTime createdAt,    // 추가
    required DateTime updatedAt,    // lastUpdated → updatedAt
    // messages는 별도 로드
  }) = _Conversation;

  factory Conversation.fromJson(Map<String, dynamic> json) =>
      _$ConversationFromJson(json);
}
```

---

### 1.5 ChatMessage Model ⚠️ **완전히 다른 구조**

#### Frontend Model (`chat_message.dart`)

```dart
@freezed
abstract class ChatMessage with _$ChatMessage {
  const factory ChatMessage({
    required String id,
    required String text,        // ⚠️ DB에는 parts 구조
    required String sender,      // ⚠️ DB에는 role
    required DateTime timestamp,
    required bool isUser,        // ⚠️ DB에는 role로 구분
    String? fileUrl,
    String? fileName,
  }) = _ChatMessage;
}
```

#### Supabase Schema (`conversation_messages`)

```sql
CREATE TABLE conversation_messages (
  id UUID PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES conversations(id),
  role TEXT CHECK (role IN ('user', 'model')),  -- 'user' | 'model'
  parts JSONB NOT NULL,  -- [{type: 'text', text: '...'}, {type: 'image', url: '...'}]
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Parts JSONB 구조 예시:**

```json
[
  { "type": "text", "text": "Hello, how are you?" },
  { "type": "image", "url": "https://..." },
  { "type": "audio", "url": "https://..." }
]
```

#### 🔧 필요한 변경사항

**Frontend 모델 완전 재설계:**

```dart
// 1. MessagePart 유니온 타입 정의
@freezed
abstract class MessagePart with _$MessagePart {
  const factory MessagePart.text(String text) = TextPart;
  const factory MessagePart.image(String url) = ImagePart;
  const factory MessagePart.audio(String url) = AudioPart;

  factory MessagePart.fromJson(Map<String, dynamic> json) {
    switch (json['type']) {
      case 'text':
        return MessagePart.text(json['text']);
      case 'image':
        return MessagePart.image(json['url']);
      case 'audio':
        return MessagePart.audio(json['url']);
      default:
        throw UnimplementedError('Unknown type: ${json['type']}');
    }
  }

  Map<String, dynamic> toJson();
}

// 2. ChatMessage 재구성
@freezed
abstract class ChatMessage with _$ChatMessage {
  const factory ChatMessage({
    required String id,
    required String conversationId,
    required String role,  // 'user' or 'model'
    required List<MessagePart> parts,
    required DateTime createdAt,
  }) = _ChatMessage;

  factory ChatMessage.fromJson(Map<String, dynamic> json) =>
      _$ChatMessageFromJson(json);
}

// 3. Convenience factory (기존 코드 호환성 유지)
extension ChatMessageX on ChatMessage {
  static ChatMessage fromText({
    required String id,
    required String conversationId,
    required String text,
    required bool isUser,
  }) {
    return ChatMessage(
      id: id,
      conversationId: conversationId,
      role: isUser ? 'user' : 'model',
      parts: [MessagePart.text(text)],
      createdAt: DateTime.now(),
    );
  }

  // 텍스트 추출 헬퍼
  String? get firstText {
    final textPart = parts.whereType<TextPart>().firstOrNull;
    return textPart?.text;
  }

  bool get isUser => role == 'user';
}
```

---

### 1.6 ChatSummary Model

#### Frontend Model (`chat_summary.dart`)

```dart
@freezed
abstract class ChatSummary with _$ChatSummary {
  const factory ChatSummary({
    required String id,
    required String title,
    required String preview,
    required DateTime lastMessageTime,
  }) = _ChatSummary;
}
```

#### ⚠️ DB 테이블 없음

**해결 방법:**

**Option 1: DB View 생성**

```sql
CREATE VIEW chat_summaries AS
SELECT
  c.id,
  c.title,
  COALESCE(
    (SELECT cm.parts->0->>'text'
     FROM conversation_messages cm
     WHERE cm.conversation_id = c.id
     ORDER BY cm.created_at DESC
     LIMIT 1
    ),
    'No messages'
  ) AS preview,
  COALESCE(
    (SELECT cm.created_at
     FROM conversation_messages cm
     WHERE cm.conversation_id = c.id
     ORDER BY cm.created_at DESC
     LIMIT 1
    ),
    c.created_at
  ) AS last_message_time
FROM conversations c;
```

**Option 2: Frontend에서 조합**

```dart
// Repository에서 join query로 가져오기
Future<List<ChatSummary>> getChatSummaries(String userId) async {
  final response = await supabase
    .from('conversations')
    .select('''
      id,
      title,
      updated_at,
      conversation_messages!inner(parts, created_at)
    ''')
    .eq('user_id', userId)
    .order('updated_at', ascending: false);

  return response.map((row) {
    final messages = row['conversation_messages'] as List;
    final lastMessage = messages.isNotEmpty ? messages.first : null;

    return ChatSummary(
      id: row['id'],
      title: row['title'] ?? 'New Chat',
      preview: lastMessage?['parts']?[0]?['text'] ?? 'No messages',
      lastMessageTime: DateTime.parse(
        lastMessage?['created_at'] ?? row['updated_at']
      ),
    );
  }).toList();
}
```

---

### 1.7 CampaignRecruiting Model

#### Frontend Model (`campaign_recruiting.dart`)

```dart
@freezed
abstract class CampaignRecruiting with _$CampaignRecruiting {
  const factory CampaignRecruiting({
    required int id,
    required String userId,
    required String username,
    String? userImg,
    required String title,
    required int recruitmentCount,
    required String campaignName,
    required String requirements,
    String? url,
    required String createdAt,
  }) = _CampaignRecruiting;
}
```

#### ⚠️ DB 테이블 없음

#### 🔧 필요한 변경사항

**DB 테이블 생성:**

```sql
CREATE TABLE campaign_recruiting (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id),
  title TEXT NOT NULL,
  recruitment_count INTEGER NOT NULL,
  campaign_name TEXT NOT NULL,
  requirements TEXT NOT NULL,
  url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_campaign_recruiting_user_id ON campaign_recruiting(user_id);
CREATE INDEX idx_campaign_recruiting_created_at ON campaign_recruiting(created_at DESC);
```

---

### 1.8 QuizQuestion Model

#### Frontend Model (`quiz_question.dart`)

```dart
class QuizQuestion {
  final String question;
  final String answer;      // 'O' or 'X' only
  final String explanation;
}
```

#### Supabase Schema (`quiz` table)

```sql
CREATE TABLE quiz (
  id BIGSERIAL PRIMARY KEY,
  question TEXT NOT NULL,
  options JSONB,           -- ⚠️ 모델에 없음 (객관식용)
  correct_answer TEXT NOT NULL,
  explanation TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 🔧 필요한 변경사항

**Frontend 모델 확장:**

```dart
@freezed
abstract class QuizQuestion with _$QuizQuestion {
  const factory QuizQuestion({
    required int id,
    required String question,
    List<String>? options,        // null이면 OX 퀴즈, 있으면 객관식
    required String correctAnswer,
    required String explanation,
    required DateTime createdAt,
  }) = _QuizQuestion;

  factory QuizQuestion.fromJson(Map<String, dynamic> json) =>
      _$QuizQuestionFromJson(json);
}

// OX 퀴즈 전용 팩토리
extension QuizQuestionX on QuizQuestion {
  static QuizQuestion ox({
    required int id,
    required String question,
    required bool correctAnswer,
    required String explanation,
    required DateTime createdAt,
  }) {
    return QuizQuestion(
      id: id,
      question: question,
      options: null,
      correctAnswer: correctAnswer ? 'O' : 'X',
      explanation: explanation,
      createdAt: createdAt,
    );
  }

  bool get isOXQuiz => options == null;
}
```

---

## 2. Frontend에는 없지만 DB에 있는 테이블

### 2.1 activity_log

```sql
CREATE TABLE activity_log (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id),
  action_type TEXT NOT NULL,
  points_earned INTEGER NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**생성 필요한 모델:**

```dart
@freezed
abstract class ActivityLog with _$ActivityLog {
  const factory ActivityLog({
    required int id,
    required String userId,
    required String actionType,
    required int pointsEarned,
    Map<String, dynamic>? metadata,
    required DateTime createdAt,
  }) = _ActivityLog;

  factory ActivityLog.fromJson(Map<String, dynamic> json) =>
      _$ActivityLogFromJson(json);
}
```

**활용 예시:**

```dart
// 활동 로그 조회
final logs = await supabase
  .from('activity_log')
  .select()
  .eq('user_id', userId)
  .order('created_at', ascending: false)
  .limit(50);

// 특정 액션의 포인트 합계
final totalPoints = await supabase
  .rpc('get_points_by_action', params: {
    'p_user_id': userId,
    'p_action_type': 'verification_success'
  });
```

---

### 2.2 article

```sql
CREATE TABLE article (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  topic TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**생성 필요한 모델:**

```dart
@freezed
abstract class Article with _$Article {
  const factory Article({
    required int id,
    required String title,
    required String content,
    String? topic,
    required DateTime createdAt,
  }) = _Article;

  factory Article.fromJson(Map<String, dynamic> json) =>
      _$ArticleFromJson(json);
}
```

**활용 시나리오:**

- 환경 관련 아티클/뉴스 제공
- 교육 콘텐츠 관리

---

### 2.3 characters

```sql
CREATE TABLE characters (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id),
  name TEXT,
  image_url TEXT,
  generation_prompt TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**생성 필요한 모델:**

```dart
@freezed
abstract class Character with _$Character {
  const factory Character({
    required int id,
    required String userId,
    String? name,
    String? imageUrl,
    String? generationPrompt,
    required DateTime createdAt,
  }) = _Character;

  factory Character.fromJson(Map<String, dynamic> json) =>
      _$CharacterFromJson(json);
}
```

**활용 시나리오:**

- AI 캐릭터 생성 기능
- 사용자별 커스텀 캐릭터 관리
- `conversations.character_id`와 연결

---

### 2.4 likes

```sql
CREATE TABLE likes (
  id BIGSERIAL PRIMARY KEY,
  post_id BIGINT REFERENCES posts(id),
  user_id UUID REFERENCES profiles(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(post_id, user_id)  -- 중복 방지
);
```

**생성 필요한 모델:**

```dart
@freezed
abstract class Like with _$Like {
  const factory Like({
    required int id,
    int? postId,
    String? userId,
    required DateTime createdAt,
  }) = _Like;

  factory Like.fromJson(Map<String, dynamic> json) =>
      _$LikeFromJson(json);
}
```

**Repository 예시:**

```dart
// 좋아요 추가
Future<void> addLike(int postId, String userId) async {
  await supabase.from('likes').insert({
    'post_id': postId,
    'user_id': userId,
  });

  // posts 테이블의 likes_count 증가
  await supabase.rpc('increment_likes_count', params: {
    'post_id': postId,
  });
}

// 좋아요 취소
Future<void> removeLike(int postId, String userId) async {
  await supabase
    .from('likes')
    .delete()
    .eq('post_id', postId)
    .eq('user_id', userId);

  await supabase.rpc('decrement_likes_count', params: {
    'post_id': postId,
  });
}

// 사용자의 좋아요 여부 확인
Future<bool> hasLiked(int postId, String userId) async {
  final result = await supabase
    .from('likes')
    .select()
    .eq('post_id', postId)
    .eq('user_id', userId)
    .maybeSingle();

  return result != null;
}
```

---

### 2.5 point_log

```sql
CREATE TABLE point_log (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id),
  point INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**생성 필요한 모델:**

```dart
@freezed
abstract class PointLog with _$PointLog {
  const factory PointLog({
    required int id,
    String? userId,
    int? point,
    required DateTime createdAt,
  }) = _PointLog;

  factory PointLog.fromJson(Map<String, dynamic> json) =>
      _$PointLogFromJson(json);
}
```

**활용 시나리오:**

- `ChartData` 모델의 데이터 소스
- 포인트 내역 조회
- 통계 차트 생성

**Repository 예시:**

```dart
// 일별 포인트 집계 (ChartData로 변환)
Future<List<ChartData>> getDailyPoints(
  String userId,
  DateTime startDate,
  DateTime endDate,
) async {
  final logs = await supabase
    .from('point_log')
    .select()
    .eq('user_id', userId)
    .gte('created_at', startDate.toIso8601String())
    .lte('created_at', endDate.toIso8601String())
    .order('created_at');

  // 날짜별로 그룹화
  final Map<DateTime, int> dailyPoints = {};
  for (final log in logs) {
    final date = DateTime.parse(log['created_at']).toLocal();
    final dateOnly = DateTime(date.year, date.month, date.day);
    dailyPoints[dateOnly] = (dailyPoints[dateOnly] ?? 0) + (log['point'] ?? 0);
  }

  return dailyPoints.entries
    .map((e) => ChartData(date: e.key, score: e.value))
    .toList()
    ..sort((a, b) => a.date.compareTo(b.date));
}
```

---

### 2.6 suggest_behavior

```sql
CREATE TABLE suggest_behavior (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**생성 필요한 모델:**

```dart
@freezed
abstract class SuggestBehavior with _$SuggestBehavior {
  const factory SuggestBehavior({
    required int id,
    String? userId,
    required String content,
    required DateTime createdAt,
  }) = _SuggestBehavior;

  factory SuggestBehavior.fromJson(Map<String, dynamic> json) =>
      _$SuggestBehaviorFromJson(json);
}
```

**활용 시나리오:**

- AI가 추천하는 친환경 행동 제안
- 사용자 맞춤 미션 생성

---

### 2.7 banners

```sql
CREATE TABLE banners (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  image_url TEXT NOT NULL,
  link_url TEXT NOT NULL,
  "order" INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  click_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**생성 필요한 모델:**

```dart
@freezed
abstract class Banner with _$Banner {
  const factory Banner({
    required int id,
    required String title,
    required String imageUrl,
    required String linkUrl,
    @Default(0) int order,
    @Default(true) bool isActive,
    @Default(0) int clickCount,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) = _Banner;

  factory Banner.fromJson(Map<String, dynamic> json) =>
      _$BannerFromJson(json);
}
```

**Repository 예시:**

```dart
// 활성화된 배너 목록 조회 (순서대로)
Future<List<Banner>> getActiveBanners() async {
  final response = await supabase
    .from('banners')
    .select()
    .eq('is_active', true)
    .order('order');

  return response
    .map((json) => Banner.fromJson(json))
    .toList();
}

// 배너 클릭 카운트 증가
Future<void> incrementBannerClick(int bannerId) async {
  await supabase.rpc('increment_banner_clicks', params: {
    'banner_id': bannerId,
  });
}
```

---

## 3. 로컬 전용 모델 (DB 동기화 불필요)

### 3.1 AppSettings

```dart
class AppSettings {
  final bool isDarkMode;
  final bool notificationsEnabled;
  final String language;
}
```

- ✅ 로컬 SharedPreferences/Hive 저장
- DB 동기화 불필요

---

### 3.2 VerificationResult

```dart
class VerificationResult {
  final bool isValid;
  final double confidence;
  final String reason;
}
```

- ✅ API 응답 전용 모델
- 임시 데이터이므로 DB 저장 불필요

---

### 3.3 ChartData

```dart
class ChartData {
  final DateTime date;
  final int score;
}
```

- ✅ `point_log` 테이블에서 파생된 뷰 모델
- UI 표시 전용

---

## 4. 마이그레이션 우선순위 및 실행 계획

### Phase 1: 긴급 (Core 기능)

**영향도**: 🔴 High - 즉시 처리 필요

1. **Conversation & ChatMessage 재구성**

   - 채팅 기능의 핵심
   - DB 구조와 완전히 다름
   - 예상 작업 시간: 4-6시간

2. **Profile 테이블 확장**

   ```sql
   ALTER TABLE profiles
     ADD COLUMN birth_date DATE,
     ADD COLUMN region TEXT;
   ```

   - 사용자 프로필 완성도
   - 예상 작업 시간: 30분

3. **Post 모델 업데이트**
   ```dart
   @Default(0) int commentsCount,
   ```
   - 댓글 수 표시 필수
   - 예상 작업 시간: 15분

---

### Phase 2: 중요 (기능 확장)

**영향도**: 🟡 Medium - 1-2주 내 처리

4. **campaign_recruiting 테이블 생성**

   - 캠페인 모집 기능 구현
   - 예상 작업 시간: 2시간

5. **Like 시스템 구현**

   - 좋아요 기능 완성
   - 모델 + Repository 구현
   - 예상 작업 시간: 3시간

6. **QuizQuestion 확장**

   - 객관식 퀴즈 지원
   - 예상 작업 시간: 1시간

7. **PointLog 모델 생성**
   - ChartData 연동
   - 포인트 이력 관리
   - 예상 작업 시간: 2시간

---

### Phase 3: 선택 (부가 기능)

**영향도**: 🟢 Low - 필요 시 추가

8. **ActivityLog 모델**
9. **Article 모델**
10. **Character 모델**
11. **SuggestBehavior 모델**
12. **Banner 모델**

각 모델당 예상 작업 시간: 1-2시간

---

## 5. DB 마이그레이션 스크립트

### 5.1 profiles 테이블 확장

```sql
-- Migration: add_profile_fields
-- Created: 2025-10-10

ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS birth_date DATE,
  ADD COLUMN IF NOT EXISTS region TEXT;

-- Index for region-based queries
CREATE INDEX IF NOT EXISTS idx_profiles_region ON profiles(region);

COMMENT ON COLUMN profiles.birth_date IS '사용자 생년월일';
COMMENT ON COLUMN profiles.region IS '사용자 거주 지역';
```

---

### 5.2 conversations 테이블 수정

```sql
-- Migration: update_conversations_schema
-- Created: 2025-10-10

-- 1. title 컬럼 추가
ALTER TABLE conversations
  ADD COLUMN IF NOT EXISTS title TEXT DEFAULT 'New Chat';

-- 2. user_id를 TEXT에서 UUID로 변경
-- 주의: 기존 데이터가 UUID 형식인지 확인 필요
ALTER TABLE conversations
  ALTER COLUMN user_id TYPE UUID USING user_id::uuid;

-- 3. Foreign Key 추가
ALTER TABLE conversations
  ADD CONSTRAINT fk_conversations_user_id
  FOREIGN KEY (user_id) REFERENCES profiles(id);

-- 4. Index 생성
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);

COMMENT ON COLUMN conversations.title IS '대화 제목';
```

---

### 5.3 campaign_recruiting 테이블 생성

```sql
-- Migration: create_campaign_recruiting
-- Created: 2025-10-10

CREATE TABLE IF NOT EXISTS campaign_recruiting (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  recruitment_count INTEGER NOT NULL CHECK (recruitment_count > 0),
  campaign_name TEXT NOT NULL,
  requirements TEXT NOT NULL,
  url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_campaign_recruiting_user_id ON campaign_recruiting(user_id);
CREATE INDEX idx_campaign_recruiting_created_at ON campaign_recruiting(created_at DESC);

-- Comments
COMMENT ON TABLE campaign_recruiting IS '캠페인 모집 게시글';
COMMENT ON COLUMN campaign_recruiting.recruitment_count IS '모집 인원';
COMMENT ON COLUMN campaign_recruiting.requirements IS '참여 요건';
```

---

### 5.4 likes 테이블 Unique 제약조건 추가

```sql
-- Migration: add_likes_unique_constraint
-- Created: 2025-10-10

-- 중복 좋아요 방지
CREATE UNIQUE INDEX IF NOT EXISTS idx_likes_post_user
  ON likes(post_id, user_id);

-- 성능 개선 인덱스
CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);
CREATE INDEX IF NOT EXISTS idx_likes_created_at ON likes(created_at DESC);
```

---

### 5.5 유용한 Database Functions

#### 5.5.1 좋아요 카운트 자동 업데이트

```sql
-- Function: increment_likes_count
CREATE OR REPLACE FUNCTION increment_likes_count(post_id BIGINT)
RETURNS VOID AS $$
BEGIN
  UPDATE posts
  SET likes_count = likes_count + 1
  WHERE id = post_id;
END;
$$ LANGUAGE plpgsql;

-- Function: decrement_likes_count
CREATE OR REPLACE FUNCTION decrement_likes_count(post_id BIGINT)
RETURNS VOID AS $$
BEGIN
  UPDATE posts
  SET likes_count = GREATEST(0, likes_count - 1)
  WHERE id = post_id;
END;
$$ LANGUAGE plpgsql;
```

#### 5.5.2 댓글 카운트 자동 업데이트 (Trigger)

```sql
-- Function: update_comments_count
CREATE OR REPLACE FUNCTION update_comments_count()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE posts
    SET comments_count = comments_count + 1
    WHERE id = NEW.post_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE posts
    SET comments_count = GREATEST(0, comments_count - 1)
    WHERE id = OLD.post_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger
DROP TRIGGER IF EXISTS trigger_update_comments_count ON comments;
CREATE TRIGGER trigger_update_comments_count
AFTER INSERT OR DELETE ON comments
FOR EACH ROW
EXECUTE FUNCTION update_comments_count();
```

#### 5.5.3 사용자 활동 로그 자동 기록

```sql
-- Function: log_activity
CREATE OR REPLACE FUNCTION log_activity(
  p_user_id UUID,
  p_action_type TEXT,
  p_points_earned INTEGER,
  p_metadata JSONB DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
  INSERT INTO activity_log (user_id, action_type, points_earned, metadata)
  VALUES (p_user_id, p_action_type, p_points_earned, p_metadata);

  -- 포인트 로그에도 기록
  IF p_points_earned IS NOT NULL AND p_points_earned > 0 THEN
    INSERT INTO point_log (user_id, point)
    VALUES (p_user_id, p_points_earned);

    -- 프로필 총 포인트 업데이트
    UPDATE profiles
    SET total_points = total_points + p_points_earned
    WHERE id = p_user_id;
  END IF;
END;
$$ LANGUAGE plpgsql;
```

#### 5.5.4 일별 포인트 집계

```sql
-- Function: get_daily_points
CREATE OR REPLACE FUNCTION get_daily_points(
  p_user_id UUID,
  p_start_date TIMESTAMPTZ,
  p_end_date TIMESTAMPTZ
)
RETURNS TABLE(date DATE, total_points BIGINT) AS $$
BEGIN
  RETURN QUERY
  SELECT
    DATE(created_at) AS date,
    SUM(point)::BIGINT AS total_points
  FROM point_log
  WHERE user_id = p_user_id
    AND created_at >= p_start_date
    AND created_at < p_end_date
  GROUP BY DATE(created_at)
  ORDER BY date;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. Repository 구현 가이드

### 6.1 Base Repository 패턴

```dart
abstract class BaseRepository<T> {
  final SupabaseClient supabase;
  final String tableName;

  BaseRepository(this.supabase, this.tableName);

  Future<List<T>> getAll();
  Future<T?> getById(dynamic id);
  Future<T> create(Map<String, dynamic> data);
  Future<T> update(dynamic id, Map<String, dynamic> data);
  Future<void> delete(dynamic id);
}
```

### 6.2 ConversationRepository 예시

```dart
class ConversationRepository extends BaseRepository<Conversation> {
  ConversationRepository(SupabaseClient supabase)
    : super(supabase, 'conversations');

  @override
  Future<List<Conversation>> getAll() async {
    final response = await supabase
      .from(tableName)
      .select()
      .order('updated_at', ascending: false);

    return response
      .map((json) => Conversation.fromJson(json))
      .toList();
  }

  Future<List<Conversation>> getByUserId(String userId) async {
    final response = await supabase
      .from(tableName)
      .select()
      .eq('user_id', userId)
      .order('updated_at', ascending: false);

    return response
      .map((json) => Conversation.fromJson(json))
      .toList();
  }

  Future<List<ChatMessage>> getMessages(String conversationId) async {
    final response = await supabase
      .from('conversation_messages')
      .select()
      .eq('conversation_id', conversationId)
      .order('created_at');

    return response
      .map((json) => ChatMessage.fromJson(json))
      .toList();
  }

  Future<void> addMessage(ChatMessage message) async {
    await supabase.from('conversation_messages').insert({
      'conversation_id': message.conversationId,
      'role': message.role,
      'parts': message.parts.map((p) => p.toJson()).toList(),
    });

    // updated_at 갱신
    await supabase
      .from(tableName)
      .update({'updated_at': DateTime.now().toIso8601String()})
      .eq('id', message.conversationId);
  }
}
```

---

## 7. DTO (Data Transfer Object) 가이드

### 7.1 PostDTO 예시

```dart
@freezed
class PostDTO with _$PostDTO {
  const factory PostDTO({
    required int id,
    required String user_id,
    required String title,
    required String content,
    String? image_url,
    required int likes_count,
    required int comments_count,
    required String created_at,
  }) = _PostDTO;

  factory PostDTO.fromJson(Map<String, dynamic> json) =>
      _$PostDTOFromJson(json);
}

// DTO → Domain Model 변환
extension PostDTOX on PostDTO {
  Post toDomain({
    required String username,
    String? userImg,
  }) {
    return Post(
      id: id,
      userId: user_id,
      title: title,
      content: content,
      imageUrl: image_url,
      likesCount: likes_count,
      commentsCount: comments_count,
      createdAt: created_at,
      username: username,
      userImg: userImg,
    );
  }
}

// Domain Model → DTO 변환
extension PostX on Post {
  PostDTO toDTO() {
    return PostDTO(
      id: id,
      user_id: userId,
      title: title,
      content: content,
      image_url: imageUrl,
      likes_count: likesCount,
      comments_count: commentsCount,
      created_at: createdAt,
    );
  }
}
```

---

## 8. Supabase RLS (Row Level Security) 권장 설정

### 8.1 profiles 테이블

```sql
-- RLS 활성화
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 정책: 모든 사용자는 자신의 프로필만 수정 가능
CREATE POLICY "Users can update own profile"
ON profiles FOR UPDATE
USING (auth.uid() = id);

-- 정책: 모든 사용자는 다른 사용자의 프로필 조회 가능
CREATE POLICY "Profiles are viewable by everyone"
ON profiles FOR SELECT
USING (true);
```

### 8.2 posts 테이블

```sql
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 조회: 모두 가능
CREATE POLICY "Posts are viewable by everyone"
ON posts FOR SELECT
USING (true);

-- 작성: 로그인한 사용자만
CREATE POLICY "Users can create posts"
ON posts FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- 수정: 작성자만
CREATE POLICY "Users can update own posts"
ON posts FOR UPDATE
USING (auth.uid() = user_id);

-- 삭제: 작성자만
CREATE POLICY "Users can delete own posts"
ON posts FOR DELETE
USING (auth.uid() = user_id);
```

### 8.3 conversations 테이블

```sql
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 대화만 조회/수정 가능
CREATE POLICY "Users can manage own conversations"
ON conversations FOR ALL
USING (auth.uid() = user_id);
```

### 8.4 likes 테이블

```sql
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;

-- 조회: 모두 가능
CREATE POLICY "Likes are viewable by everyone"
ON likes FOR SELECT
USING (true);

-- 작성: 자신의 좋아요만
CREATE POLICY "Users can create own likes"
ON likes FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- 삭제: 자신의 좋아요만
CREATE POLICY "Users can delete own likes"
ON likes FOR DELETE
USING (auth.uid() = user_id);
```

---

## 9. 테스트 데이터 생성 스크립트

### 9.1 샘플 프로필

```sql
INSERT INTO profiles (id, username, user_img, total_points, continuous_days, region)
VALUES
  ('00000000-0000-0000-0000-000000000001', 'eco_warrior', 'https://example.com/user1.jpg', 1500, 30, '서울'),
  ('00000000-0000-0000-0000-000000000002', 'green_hero', 'https://example.com/user2.jpg', 2300, 45, '부산'),
  ('00000000-0000-0000-0000-000000000003', 'planet_saver', NULL, 850, 15, '대구');
```

### 9.2 샘플 포스트

```sql
INSERT INTO posts (user_id, title, content, likes_count, comments_count)
VALUES
  ('00000000-0000-0000-0000-000000000001', '오늘의 제로웨이스트 챌린지!', '장바구니 들고 마트 다녀왔어요', 42, 5),
  ('00000000-0000-0000-0000-000000000002', '텀블러 사용 1년 달성', '일회용 컵 365개 줄였어요!', 89, 12);
```

### 9.3 샘플 퀴즈

```sql
INSERT INTO quiz (question, correct_answer, explanation)
VALUES
  ('플라스틱은 자연 분해되는데 500년 이상 걸린다', 'O', '플라스틱은 500-1000년이 지나야 분해됩니다.'),
  ('종이컵은 100% 재활용 가능하다', 'X', '종이컵은 내부 플라스틱 코팅 때문에 재활용이 어렵습니다.');
```

---

## 10. 마이그레이션 체크리스트

### ✅ Phase 1 (긴급)

- [ ] `profiles` 테이블에 `birth_date`, `region` 추가
- [ ] `conversations` 테이블에 `title` 추가 및 `user_id` UUID 변환
- [ ] `Conversation` 모델 재구성 (userId, characterId, createdAt 추가)
- [ ] `ChatMessage` 모델 완전 재설계 (role, parts 구조)
- [ ] `MessagePart` 유니온 타입 구현
- [ ] `Post` 모델에 `commentsCount` 추가

### ✅ Phase 2 (중요)

- [ ] `campaign_recruiting` 테이블 생성
- [ ] `CampaignRecruiting` 모델 및 Repository 구현
- [ ] `likes` 테이블에 Unique 제약조건 추가
- [ ] `Like` 모델 및 Repository 구현
- [ ] `QuizQuestion` 모델 확장 (객관식 지원)
- [ ] `PointLog` 모델 및 Repository 구현
- [ ] ChartData ↔ PointLog 연동

### ✅ Phase 3 (선택)

- [ ] `ActivityLog` 모델 구현
- [ ] `Article` 모델 구현
- [ ] `Character` 모델 구현
- [ ] `SuggestBehavior` 모델 구현
- [ ] `Banner` 모델 구현

### ✅ 공통 작업

- [ ] 모든 새 모델에 대한 DTO 생성
- [ ] Repository 인터페이스 및 구현체 작성
- [ ] RLS 정책 설정
- [ ] Database Functions 생성
- [ ] Trigger 설정
- [ ] 테스트 데이터 생성
- [ ] API 엔드포인트 구현 (backend)

---

## 11. 참고 자료

### Supabase 관련

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL Functions](https://www.postgresql.org/docs/current/sql-createfunction.html)

### Flutter/Dart 관련

- [Freezed Package](https://pub.dev/packages/freezed)
- [Riverpod Docs](https://riverpod.dev/)
- [Clean Architecture Guide](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

## 변경 이력

| 날짜       | 작성자 | 변경 내용                           |
| ---------- | ------ | ----------------------------------- |
| 2025-10-10 | Claude | 초안 작성 - Supabase DB 스키마 분석 |

---

**문서 종료**

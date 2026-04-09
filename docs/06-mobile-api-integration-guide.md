# 6. Mobile API Integration Guide

> Complete endpoint catalog, DTO contracts, request/response mapping, and error-handling patterns for the mobile client.

---

## 6.1 API Overview

### 6.1.1 Base Configuration

| Property | Value |
|----------|-------|
| Base URL (Production) | `https://api.example.com/v1` |
| Base URL (Staging) | `https://api-staging.example.com/v1` |
| Base URL (Development) | `https://api-dev.example.com/v1` |
| Protocol | HTTPS (TLS 1.3) |
| Content-Type | `application/json` |
| API Versioning | URL path (`/v1/`, `/v2/`) |
| Rate Limiting | 100 requests/minute per user; 1,000 requests/minute per device |
| Max Request Body | 5 MB |
| Pagination | Cursor-based for lists; `?cursor={next_cursor}&limit={n}` |

### 6.1.2 Authentication

| Header | Value | Description |
|--------|-------|-------------|
| `Authorization` | `Bearer {access_token}` | JWT access token (15-min expiry) |
| `X-App-Version` | `2.1.0` | Client app version |
| `X-Platform` | `ios` / `android` | Client platform |
| `X-Device-Id` | UUID | Unique device identifier |
| `X-Request-Id` | UUID | Unique request identifier for tracing |
| `Accept-Language` | `en-US` | Client locale for localized responses |

### 6.1.3 Standard Response Envelope

```json
// Success response
{
  "status": "success",
  "data": { /* resource data */ },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}

// Paginated response
{
  "status": "success",
  "data": [ /* array of items */ ],
  "pagination": {
    "cursor": "eyJpZCI6MTAwfQ==",
    "has_more": true,
    "total": 150
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}

// Error response
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is already registered",
    "details": [
      {
        "field": "email",
        "message": "An account with this email already exists",
        "code": "EMAIL_TAKEN"
      }
    ]
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

---

## 6.2 Endpoints by Flow

### 6.2.1 Authentication Endpoints

#### POST `/auth/signup`

Create a new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecureP@ss1",
  "language_learning": "es",
  "language_native": "en",
  "daily_goal": "regular",
  "timezone": "America/New_York"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "usr_abc123",
      "name": "John Doe",
      "email": "john@example.com",
      "username": "johndoe123",
      "avatar_url": null,
      "created_at": "2024-01-15T10:30:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJSUzI1NiIs...",
      "refresh_token": "rt_xyz789...",
      "expires_in": 900
    }
  }
}
```

**Errors:**
| Code | HTTP Status | Description |
|------|------------|-------------|
| `EMAIL_TAKEN` | 409 | Email already registered |
| `INVALID_PASSWORD` | 422 | Password doesn't meet requirements |
| `INVALID_EMAIL` | 422 | Email format invalid |

---

#### POST `/auth/login`

Authenticate existing user.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecureP@ss1"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "usr_abc123",
      "name": "John Doe",
      "email": "john@example.com",
      "username": "johndoe123",
      "avatar_url": "https://cdn.example.com/avatars/usr_abc123.jpg",
      "is_premium": false,
      "created_at": "2024-01-15T10:30:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJSUzI1NiIs...",
      "refresh_token": "rt_xyz789...",
      "expires_in": 900
    }
  }
}
```

**Errors:**
| Code | HTTP Status | Description |
|------|------------|-------------|
| `INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `ACCOUNT_LOCKED` | 403 | Too many failed attempts |
| `ACCOUNT_DISABLED` | 403 | Account suspended |

---

#### POST `/auth/refresh`

Refresh access token.

**Request:**
```json
{
  "refresh_token": "rt_xyz789..."
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "refresh_token": "rt_new789...",
    "expires_in": 900
  }
}
```

---

#### POST `/auth/forgot-password`

Request password reset email.

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "message": "If an account exists with this email, a reset link has been sent."
  }
}
```

---

#### POST `/auth/reset-password`

Set new password using reset token.

**Request:**
```json
{
  "token": "rst_abc123...",
  "new_password": "NewSecureP@ss2"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "message": "Password has been reset successfully."
  }
}
```

---

#### POST `/auth/social`

Authenticate via social provider.

**Request:**
```json
{
  "provider": "google",
  "id_token": "eyJhbGciOiJSUzI1NiIs...",
  "nonce": "abc123"
}
```

**Response (200 OK or 201 Created):**
Same as `/auth/login` response.

---

### 6.2.2 User Profile Endpoints

#### GET `/users/me`

Get current user's full profile.

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "usr_abc123",
    "name": "John Doe",
    "username": "johndoe123",
    "email": "john@example.com",
    "avatar_url": "https://cdn.example.com/avatars/usr_abc123.jpg",
    "bio": "Learning Spanish! 🇪🇸",
    "location": "New York",
    "is_premium": false,
    "premium_expires_at": null,
    "total_xp": 5420,
    "current_streak": 15,
    "longest_streak": 42,
    "gems": 350,
    "hearts": 5,
    "hearts_max": 5,
    "next_heart_at": null,
    "daily_goal": "regular",
    "daily_goal_xp": 20,
    "today_xp": 16,
    "courses": [
      {
        "language": "es",
        "from_language": "en",
        "xp": 3200,
        "level": 8,
        "skills_completed": 24,
        "skills_total": 78
      },
      {
        "language": "fr",
        "from_language": "en",
        "xp": 2220,
        "level": 6,
        "skills_completed": 18,
        "skills_total": 72
      }
    ],
    "streak_freeze_count": 2,
    "profile_visibility": "public",
    "created_at": "2024-01-15T10:30:00Z",
    "timezone": "America/New_York"
  }
}
```

---

#### PUT `/users/me`

Update user profile.

**Request:**
```json
{
  "name": "John Doe",
  "username": "johndoe",
  "bio": "Learning Spanish and French!",
  "location": "New York",
  "daily_goal": "serious",
  "profile_visibility": "friends_only"
}
```

**Response (200 OK):** Updated user object.

---

#### PUT `/users/me/avatar`

Upload avatar image.

**Request:** `multipart/form-data` with `avatar` file field.

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "avatar_url": "https://cdn.example.com/avatars/usr_abc123_v2.jpg"
  }
}
```

---

### 6.2.3 Course & Skill Tree Endpoints

#### GET `/courses/{language}/tree`

Get the full skill tree for a course.

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "course_id": "es_from_en",
    "language": "es",
    "from_language": "en",
    "sections": [
      {
        "id": "sec_1",
        "name": "Basics",
        "order": 1,
        "checkpoint": null,
        "skills": [
          {
            "id": "skill_greetings",
            "name": "Greetings",
            "icon_url": "https://cdn.example.com/icons/greetings.svg",
            "order": 1,
            "crown_level": 3,
            "crown_max": 5,
            "lessons_completed": 10,
            "lessons_total": 19,
            "is_legendary": false,
            "legendary_completed": false,
            "strength": 0.85,
            "words": ["hola", "buenos días", "adiós", "gracias", "por favor"],
            "tips_available": true,
            "state": "in_progress"
          },
          {
            "id": "skill_basics1",
            "name": "Basics 1",
            "icon_url": "https://cdn.example.com/icons/basics1.svg",
            "order": 2,
            "crown_level": 5,
            "crown_max": 5,
            "lessons_completed": 19,
            "lessons_total": 19,
            "is_legendary": true,
            "legendary_completed": true,
            "strength": 0.92,
            "words": ["el", "la", "un", "una", "es", "soy"],
            "tips_available": true,
            "state": "completed"
          }
        ]
      },
      {
        "id": "sec_2",
        "name": "Travel",
        "order": 2,
        "checkpoint": {
          "id": "cp_1",
          "completed": true,
          "questions": 15,
          "passing_score": 80
        },
        "skills": [ /* ... */ ]
      }
    ]
  }
}
```

---

#### GET `/skills/{skill_id}/tips`

Get grammar tips and notes for a skill.

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "skill_id": "skill_greetings",
    "title": "Greetings — Tips & Notes",
    "content_markdown": "## Formal vs. Informal Greetings\n\nIn Spanish, there are two ways to address someone...\n\n| Formal | Informal |\n|--------|----------|\n| usted | tú |\n...",
    "updated_at": "2024-01-10T08:00:00Z"
  }
}
```

---

### 6.2.4 Lesson & Exercise Endpoints

#### GET `/skills/{skill_id}/lessons/{crown_level}/{lesson_number}`

Get exercises for a specific lesson.

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "lesson_id": "les_abc123",
    "skill_id": "skill_greetings",
    "crown_level": 3,
    "lesson_number": 2,
    "exercises": [
      {
        "id": "ex_001",
        "type": "MULTIPLE_CHOICE",
        "difficulty": 3,
        "prompt": {
          "text": "Translate this sentence:",
          "sentence": "Le chat est noir",
          "audio_url": "https://cdn.example.com/audio/fr/le_chat_est_noir.mp3",
          "image_url": null
        },
        "options": [
          {"id": "opt_a", "text": "The dog is black"},
          {"id": "opt_b", "text": "The cat is black"},
          {"id": "opt_c", "text": "The cat is white"},
          {"id": "opt_d", "text": "The bird is black"}
        ],
        "correct_option_id": "opt_b",
        "metadata": {
          "target_words": ["chat", "noir"],
          "grammar_point": "adjective_agreement"
        }
      },
      {
        "id": "ex_002",
        "type": "WORD_BANK",
        "difficulty": 3,
        "prompt": {
          "text": "Translate this sentence:",
          "sentence": "The cat is black",
          "audio_url": null,
          "image_url": null
        },
        "word_bank": [
          {"id": "wb_1", "text": "Le"},
          {"id": "wb_2", "text": "chat"},
          {"id": "wb_3", "text": "est"},
          {"id": "wb_4", "text": "noir"},
          {"id": "wb_5", "text": "chien"},
          {"id": "wb_6", "text": "blanc"}
        ],
        "accepted_answers": [
          ["wb_1", "wb_2", "wb_3", "wb_4"]
        ],
        "metadata": {
          "target_words": ["chat", "noir"],
          "grammar_point": "basic_sentence_structure"
        }
      },
      {
        "id": "ex_003",
        "type": "LISTENING",
        "difficulty": 3,
        "prompt": {
          "text": "Type what you hear:",
          "audio_url": "https://cdn.example.com/audio/fr/bonjour_comment_allez_vous.mp3",
          "audio_slow_url": "https://cdn.example.com/audio/fr/bonjour_comment_allez_vous_slow.mp3"
        },
        "accepted_answers": [
          "Bonjour, comment allez-vous?",
          "Bonjour, comment allez-vous ?",
          "Bonjour comment allez-vous"
        ],
        "typo_tolerance": 1,
        "metadata": {
          "target_words": ["bonjour", "comment", "allez-vous"],
          "grammar_point": "formal_questions"
        }
      },
      {
        "id": "ex_004",
        "type": "SPEAKING",
        "difficulty": 3,
        "prompt": {
          "text": "Say this sentence:",
          "sentence": "Bonjour, comment allez-vous?",
          "audio_url": "https://cdn.example.com/audio/fr/bonjour_comment_allez_vous.mp3"
        },
        "expected_tokens": ["bonjour", "comment", "allez", "vous"],
        "passing_threshold": 0.7,
        "metadata": {
          "target_words": ["bonjour", "comment", "allez-vous"]
        }
      },
      {
        "id": "ex_005",
        "type": "MATCHING",
        "difficulty": 2,
        "pairs": [
          {"id": "pair_1", "left": "cat", "right": "chat"},
          {"id": "pair_2", "left": "dog", "right": "chien"},
          {"id": "pair_3", "left": "black", "right": "noir"},
          {"id": "pair_4", "left": "white", "right": "blanc"},
          {"id": "pair_5", "left": "house", "right": "maison"}
        ],
        "metadata": {
          "target_words": ["chat", "chien", "noir", "blanc", "maison"]
        }
      }
    ],
    "new_vocabulary": ["chat", "noir"],
    "review_vocabulary": ["bonjour", "comment", "maison"]
  }
}
```

---

#### POST `/lessons/complete`

Submit lesson completion results.

**Request:**
```json
{
  "lesson_id": "les_abc123",
  "skill_id": "skill_greetings",
  "crown_level": 3,
  "lesson_number": 2,
  "exercises": [
    {
      "exercise_id": "ex_001",
      "is_correct": true,
      "response_time_ms": 4500,
      "answer": "opt_b",
      "is_retry": false
    },
    {
      "exercise_id": "ex_002",
      "is_correct": true,
      "response_time_ms": 8200,
      "answer": ["wb_1", "wb_2", "wb_3", "wb_4"],
      "is_retry": false
    },
    {
      "exercise_id": "ex_003",
      "is_correct": false,
      "response_time_ms": 12000,
      "answer": "Bonjour, comment allez vous",
      "is_retry": false
    },
    {
      "exercise_id": "ex_003",
      "is_correct": true,
      "response_time_ms": 9000,
      "answer": "Bonjour, comment allez-vous?",
      "is_retry": true
    }
  ],
  "xp_earned": 145,
  "accuracy": 0.867,
  "duration_seconds": 312,
  "combo_max": 8,
  "completed_at": "2024-01-15T14:30:00Z",
  "client_timestamp": "2024-01-15T14:30:00Z"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "xp_earned": 145,
    "total_xp": 5565,
    "accuracy": 0.867,
    "streak_status": {
      "current_streak": 16,
      "daily_goal_met": true,
      "today_xp": 161
    },
    "skill_progress": {
      "skill_id": "skill_greetings",
      "crown_level": 3,
      "lessons_completed": 11,
      "lessons_total": 19,
      "crown_earned": false
    },
    "achievements_earned": [],
    "league_xp_update": {
      "league": "gold",
      "weekly_xp": 620,
      "rank": 5
    }
  }
}
```

---

### 6.2.5 Placement Test Endpoints

#### POST `/placement/start`

Start a new placement test.

**Request:**
```json
{
  "language": "es",
  "from_language": "en"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "session_id": "pt_sess_abc123",
    "first_question": {
      "id": "ptq_001",
      "type": "MULTIPLE_CHOICE",
      "difficulty": 2.0,
      "prompt": { /* ... */ },
      "options": [ /* ... */ ],
      "correct_option_id": "opt_b"
    }
  }
}
```

---

#### POST `/placement/answer`

Submit answer and get next question.

**Request:**
```json
{
  "session_id": "pt_sess_abc123",
  "question_id": "ptq_001",
  "answer": "opt_b",
  "response_time_ms": 3200
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "next_question": {
      "id": "ptq_002",
      "type": "FILL_BLANK",
      "difficulty": 2.5,
      "prompt": { /* ... */ },
      "options": [ /* ... */ ]
    },
    "progress": 0.12,
    "is_complete": false
  }
}
```

---

#### POST `/placement/complete`

Complete placement test and get results.

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "level": 3,
    "cefr_equivalent": "B1",
    "skills_unlocked": 18,
    "xp_earned": 65,
    "questions_answered": 22,
    "duration_seconds": 340
  }
}
```

---

### 6.2.6 Streak & XP Endpoints

#### GET `/users/me/streak`

Get current streak data.

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "current_streak": 15,
    "longest_streak": 42,
    "streak_start_date": "2024-01-01",
    "last_activity_date": "2024-01-15",
    "daily_goal_met_today": true,
    "today_xp": 25,
    "daily_goal_xp": 20,
    "streak_freeze_count": 2,
    "calendar": [
      {"date": "2024-01-13", "xp": 30, "goal_met": true, "freeze_used": false},
      {"date": "2024-01-14", "xp": 0, "goal_met": false, "freeze_used": true},
      {"date": "2024-01-15", "xp": 25, "goal_met": true, "freeze_used": false}
    ]
  }
}
```

---

### 6.2.7 Leaderboard Endpoints

#### GET `/leaderboard`

Get current league leaderboard.

**Query Parameters:** `league` (optional), `type` (`league` | `friends`)

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "league": "gold",
    "week_start": "2024-01-08T00:00:00Z",
    "week_end": "2024-01-14T23:59:59Z",
    "users": [
      {
        "rank": 1,
        "user_id": "usr_xyz789",
        "name": "Maria",
        "avatar_url": "https://cdn.example.com/avatars/usr_xyz789.jpg",
        "xp": 1250,
        "is_premium": true,
        "is_current_user": false
      },
      {
        "rank": 5,
        "user_id": "usr_abc123",
        "name": "John Doe",
        "avatar_url": "https://cdn.example.com/avatars/usr_abc123.jpg",
        "xp": 620,
        "is_premium": false,
        "is_current_user": true
      }
    ],
    "promotion_zone": [1, 10],
    "demotion_zone": [26, 30],
    "total_users": 30
  }
}
```

---

### 6.2.8 Shop Endpoints

#### GET `/shop/items`

Get available shop items.

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "gems_balance": 350,
    "categories": [
      {
        "name": "Power-Ups",
        "items": [
          {
            "id": "item_heart_refill",
            "name": "Heart Refill",
            "description": "Restore all hearts to full",
            "icon_url": "https://cdn.example.com/shop/heart_refill.png",
            "cost_gems": 450,
            "type": "consumable",
            "available": true
          },
          {
            "id": "item_streak_freeze",
            "name": "Streak Freeze",
            "description": "Protect your streak for one day",
            "icon_url": "https://cdn.example.com/shop/streak_freeze.png",
            "cost_gems": 200,
            "type": "consumable",
            "available": true,
            "owned_count": 2,
            "max_count": 2
          }
        ]
      }
    ]
  }
}
```

---

#### POST `/shop/purchase`

Purchase a shop item.

**Request:**
```json
{
  "item_id": "item_streak_freeze",
  "quantity": 1
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "item_id": "item_streak_freeze",
    "gems_spent": 200,
    "gems_remaining": 150,
    "item_count": 3
  }
}
```

---

### 6.2.9 Notification Endpoints

#### POST `/notifications/register`

Register device for push notifications.

**Request:**
```json
{
  "token": "fcm_token_abc123...",
  "platform": "ios",
  "device_id": "device_uuid_xyz"
}
```

---

#### GET `/notifications`

Get in-app notification feed.

**Response (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "notif_001",
      "type": "achievement",
      "title": "Achievement Unlocked!",
      "body": "You earned 'Week Warrior'!",
      "deep_link": "app://achievement/ach_week_warrior",
      "read": false,
      "created_at": "2024-01-15T12:00:00Z"
    },
    {
      "id": "notif_002",
      "type": "league",
      "title": "Leaderboard Update",
      "body": "You moved up to #3 in Gold League!",
      "deep_link": "app://leaderboard",
      "read": true,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "cursor": "eyJpZCI6MTAwfQ==",
    "has_more": true,
    "total": 24
  }
}
```

---

#### PUT `/notifications/settings`

Update notification preferences.

**Request:**
```json
{
  "lesson_reminders": true,
  "reminder_time": "09:00",
  "streak_reminders": true,
  "leaderboard_updates": true,
  "friend_activity": false,
  "promotions": false,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "07:00"
}
```

---

## 6.3 DTOs (Data Transfer Objects)

### 6.3.1 Dart DTO Definitions

```dart
// Auth DTOs
@freezed
class SignupRequest with _$SignupRequest {
  const factory SignupRequest({
    required String name,
    required String email,
    required String password,
    required String languageLearning,
    required String languageNative,
    required String dailyGoal,
    required String timezone,
  }) = _SignupRequest;

  factory SignupRequest.fromJson(Map<String, dynamic> json) =>
      _$SignupRequestFromJson(json);
}

@freezed
class AuthResponse with _$AuthResponse {
  const factory AuthResponse({
    required UserDto user,
    required TokensDto tokens,
  }) = _AuthResponse;

  factory AuthResponse.fromJson(Map<String, dynamic> json) =>
      _$AuthResponseFromJson(json);
}

@freezed
class TokensDto with _$TokensDto {
  const factory TokensDto({
    required String accessToken,
    required String refreshToken,
    required int expiresIn,
  }) = _TokensDto;

  factory TokensDto.fromJson(Map<String, dynamic> json) =>
      _$TokensDtoFromJson(json);
}

// User DTOs
@freezed
class UserDto with _$UserDto {
  const factory UserDto({
    required String id,
    required String name,
    required String email,
    required String username,
    String? avatarUrl,
    String? bio,
    String? location,
    required bool isPremium,
    DateTime? premiumExpiresAt,
    required int totalXp,
    required int currentStreak,
    required int longestStreak,
    required int gems,
    required int hearts,
    required int heartsMax,
    DateTime? nextHeartAt,
    required String dailyGoal,
    required int dailyGoalXp,
    required int todayXp,
    required List<CourseDto> courses,
    required int streakFreezeCount,
    required String profileVisibility,
    required DateTime createdAt,
    required String timezone,
  }) = _UserDto;

  factory UserDto.fromJson(Map<String, dynamic> json) =>
      _$UserDtoFromJson(json);
}

// Course DTOs
@freezed
class CourseDto with _$CourseDto {
  const factory CourseDto({
    required String language,
    required String fromLanguage,
    required int xp,
    required int level,
    required int skillsCompleted,
    required int skillsTotal,
  }) = _CourseDto;

  factory CourseDto.fromJson(Map<String, dynamic> json) =>
      _$CourseDtoFromJson(json);
}

// Skill Tree DTOs
@freezed
class SkillTreeDto with _$SkillTreeDto {
  const factory SkillTreeDto({
    required String courseId,
    required String language,
    required String fromLanguage,
    required List<SectionDto> sections,
  }) = _SkillTreeDto;

  factory SkillTreeDto.fromJson(Map<String, dynamic> json) =>
      _$SkillTreeDtoFromJson(json);
}

@freezed
class SectionDto with _$SectionDto {
  const factory SectionDto({
    required String id,
    required String name,
    required int order,
    CheckpointDto? checkpoint,
    required List<SkillDto> skills,
  }) = _SectionDto;

  factory SectionDto.fromJson(Map<String, dynamic> json) =>
      _$SectionDtoFromJson(json);
}

@freezed
class SkillDto with _$SkillDto {
  const factory SkillDto({
    required String id,
    required String name,
    required String iconUrl,
    required int order,
    required int crownLevel,
    required int crownMax,
    required int lessonsCompleted,
    required int lessonsTotal,
    required bool isLegendary,
    required bool legendaryCompleted,
    required double strength,
    required List<String> words,
    required bool tipsAvailable,
    required String state,
  }) = _SkillDto;

  factory SkillDto.fromJson(Map<String, dynamic> json) =>
      _$SkillDtoFromJson(json);
}

// Exercise DTOs
@freezed
class ExerciseDto with _$ExerciseDto {
  const factory ExerciseDto({
    required String id,
    required String type,
    required int difficulty,
    required ExercisePromptDto prompt,
    List<OptionDto>? options,
    String? correctOptionId,
    List<WordBankTileDto>? wordBank,
    List<List<String>>? acceptedAnswers,
    int? typoTolerance,
    List<MatchPairDto>? pairs,
    List<String>? expectedTokens,
    double? passingThreshold,
    required Map<String, dynamic> metadata,
  }) = _ExerciseDto;

  factory ExerciseDto.fromJson(Map<String, dynamic> json) =>
      _$ExerciseDtoFromJson(json);
}

@freezed
class ExercisePromptDto with _$ExercisePromptDto {
  const factory ExercisePromptDto({
    required String text,
    String? sentence,
    String? audioUrl,
    String? audioSlowUrl,
    String? imageUrl,
  }) = _ExercisePromptDto;

  factory ExercisePromptDto.fromJson(Map<String, dynamic> json) =>
      _$ExercisePromptDtoFromJson(json);
}

// Lesson Submission DTOs
@freezed
class LessonSubmissionDto with _$LessonSubmissionDto {
  const factory LessonSubmissionDto({
    required String lessonId,
    required String skillId,
    required int crownLevel,
    required int lessonNumber,
    required List<ExerciseResultDto> exercises,
    required int xpEarned,
    required double accuracy,
    required int durationSeconds,
    required int comboMax,
    required DateTime completedAt,
    required DateTime clientTimestamp,
  }) = _LessonSubmissionDto;

  factory LessonSubmissionDto.fromJson(Map<String, dynamic> json) =>
      _$LessonSubmissionDtoFromJson(json);
}

@freezed
class ExerciseResultDto with _$ExerciseResultDto {
  const factory ExerciseResultDto({
    required String exerciseId,
    required bool isCorrect,
    required int responseTimeMs,
    required dynamic answer,
    required bool isRetry,
  }) = _ExerciseResultDto;

  factory ExerciseResultDto.fromJson(Map<String, dynamic> json) =>
      _$ExerciseResultDtoFromJson(json);
}
```

### 6.3.2 DTO to Domain Entity Mapping

```dart
extension UserDtoMapper on UserDto {
  User toDomain() {
    return User(
      id: id,
      name: name,
      email: email,
      username: username,
      avatarUrl: avatarUrl,
      bio: bio,
      location: location,
      isPremium: isPremium,
      totalXp: totalXp,
      currentStreak: currentStreak,
      longestStreak: longestStreak,
      gems: gems,
      hearts: hearts,
      dailyGoal: DailyGoal.fromString(dailyGoal),
      todayXp: todayXp,
      courses: courses.map((c) => c.toDomain()).toList(),
      streakFreezeCount: streakFreezeCount,
    );
  }
}

extension ExerciseDtoMapper on ExerciseDto {
  Exercise toDomain() {
    return Exercise(
      id: id,
      type: ExerciseType.fromString(type),
      difficulty: difficulty,
      prompt: prompt.toDomain(),
      options: options?.map((o) => o.toDomain()).toList(),
      correctOptionId: correctOptionId,
      wordBank: wordBank?.map((w) => w.toDomain()).toList(),
      acceptedAnswers: acceptedAnswers,
      pairs: pairs?.map((p) => p.toDomain()).toList(),
    );
  }
}
```

---

## 6.4 Error Handling Patterns

### 6.4.1 Error Code Catalog

| HTTP Status | Error Code | Description | Client Action |
|-------------|------------|-------------|---------------|
| 400 | `BAD_REQUEST` | Malformed request body | Fix request and retry |
| 401 | `UNAUTHORIZED` | Invalid or expired access token | Refresh token and retry |
| 401 | `TOKEN_EXPIRED` | Access token expired | Refresh token and retry |
| 401 | `INVALID_CREDENTIALS` | Wrong email/password | Show error to user |
| 403 | `FORBIDDEN` | Insufficient permissions | Show error to user |
| 403 | `ACCOUNT_LOCKED` | Account locked due to security | Show contact support dialog |
| 403 | `PREMIUM_REQUIRED` | Feature requires subscription | Show upgrade prompt |
| 404 | `NOT_FOUND` | Resource doesn't exist | Remove from local cache; show error |
| 409 | `CONFLICT` | Resource already exists (e.g., email taken) | Show specific error to user |
| 422 | `VALIDATION_ERROR` | Input validation failed | Show field-level errors |
| 429 | `RATE_LIMITED` | Too many requests | Retry after `Retry-After` header |
| 500 | `INTERNAL_ERROR` | Server error | Retry with exponential backoff |
| 502 | `BAD_GATEWAY` | Upstream server error | Retry with exponential backoff |
| 503 | `SERVICE_UNAVAILABLE` | Service temporarily down | Retry with exponential backoff; show maintenance message if extended |

### 6.4.2 Error Response Parsing

```dart
class ApiErrorParser {
  static AppError parse(DioException exception) {
    final response = exception.response;
    if (response == null) {
      return NetworkError();
    }

    final body = response.data as Map<String, dynamic>?;
    final errorData = body?['error'] as Map<String, dynamic>?;
    final code = errorData?['code'] as String? ?? 'UNKNOWN';
    final message = errorData?['message'] as String? ?? 'An unknown error occurred';
    final details = (errorData?['details'] as List?)
        ?.map((d) => ValidationDetail.fromJson(d))
        .toList();

    switch (response.statusCode) {
      case 401:
        if (code == 'INVALID_CREDENTIALS') {
          return ClientError(
            statusCode: 401,
            serverMessage: message,
            userMessage: 'Invalid email or password. Please try again.',
          );
        }
        return AuthError();

      case 403:
        if (code == 'PREMIUM_REQUIRED') {
          return PremiumRequiredError(feature: message);
        }
        return ClientError(
          statusCode: 403,
          serverMessage: message,
          userMessage: message,
        );

      case 409:
        return ClientError(
          statusCode: 409,
          serverMessage: message,
          userMessage: _mapConflictError(code),
        );

      case 422:
        return ValidationError(
          fieldErrors: {
            for (final detail in details ?? [])
              detail.field: detail.message,
          },
        );

      case 429:
        final retryAfter = response.headers.value('Retry-After');
        return RateLimitError(
          retryAfterSeconds: int.tryParse(retryAfter ?? '60') ?? 60,
        );

      default:
        if (response.statusCode! >= 500) {
          return ServerError(statusCode: response.statusCode!);
        }
        return ClientError(
          statusCode: response.statusCode!,
          serverMessage: message,
          userMessage: message,
        );
    }
  }

  static String _mapConflictError(String code) {
    switch (code) {
      case 'EMAIL_TAKEN':
        return 'An account with this email already exists. Try logging in instead.';
      case 'USERNAME_TAKEN':
        return 'This username is already taken. Please choose another.';
      default:
        return 'A conflict occurred. Please try again.';
    }
  }
}
```

### 6.4.3 Retry Decision Matrix

```dart
class RetryDecision {
  static bool shouldRetry(AppError error, int currentAttempt) {
    if (currentAttempt >= 3) return false;

    if (error is NetworkError) return true;
    if (error is TimeoutError) return true;
    if (error is ServerError) return error.statusCode >= 500;
    if (error is RateLimitError) return true;
    if (error is AuthError) return currentAttempt == 0; // Only retry once after token refresh

    return false;
  }

  static Duration getBackoffDelay(int attempt) {
    // Exponential backoff with jitter
    final baseDelay = Duration(seconds: math.pow(2, attempt).toInt());
    final jitter = Duration(milliseconds: Random().nextInt(1000));
    return baseDelay + jitter;
  }
}
```

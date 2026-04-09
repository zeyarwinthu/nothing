# 1. API Specification

## 1.1 Overview & Versioning Strategy

### Overview

This document defines the complete REST API surface for the Duolingo-style learning platform. All endpoints are served over HTTPS and return JSON responses. The API is designed for consumption by mobile clients (iOS, Android), the web application, and third-party integrations.

### Base URL

```
Production:  https://api.lingolearn.com
Staging:     https://api-staging.lingolearn.com
Development: https://api-dev.lingolearn.com
```

### Versioning Strategy

- **URL-based versioning**: `/api/v1/`, `/api/v2/`
- Major version changes introduce breaking changes
- Minor/patch changes are backward-compatible within the same major version
- Deprecated endpoints return a `Sunset` header with the retirement date
- Minimum 6-month deprecation window before removal
- Version negotiation via `Accept` header is supported as a fallback:
  ```
  Accept: application/vnd.lingolearn.v1+json
  ```

### Common Headers

| Header            | Required | Description                                    |
|-------------------|----------|------------------------------------------------|
| `Authorization`   | Yes*     | `Bearer <JWT token>` (*except public endpoints)|
| `Content-Type`    | Yes      | `application/json`                             |
| `Accept-Language` | No       | ISO 639-1 language code (e.g., `en`, `es`)     |
| `X-Request-Id`    | No       | Client-generated UUID for request tracing       |
| `X-Device-Id`     | No       | Unique device identifier                        |
| `X-App-Version`   | No       | Client app version string                       |
| `X-Platform`      | No       | `ios`, `android`, `web`                         |

---

## 1.2 Authentication & Authorization

### Authentication Flow

The platform uses JWT (JSON Web Tokens) signed with RS256 for authentication.

#### Token Types

| Token          | Lifetime | Purpose                     |
|----------------|----------|-----------------------------|
| Access Token   | 15 min   | API request authorization    |
| Refresh Token  | 30 days  | Obtain new access tokens     |
| Device Token   | 90 days  | Remember trusted devices     |

#### JWT Payload Structure

```json
{
  "sub": "usr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "user@example.com",
  "displayName": "LinguaLearner",
  "roles": ["user"],
  "premiumTier": "free",
  "iat": 1700000000,
  "exp": 1700000900,
  "iss": "lingolearn-auth",
  "aud": "lingolearn-api"
}
```

### Endpoints

#### POST `/api/v1/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "displayName": "LinguaLearner",
  "age": 25,
  "nativeLanguage": "en",
  "targetLanguage": "es",
  "dailyGoalMinutes": 15,
  "timezone": "America/New_York",
  "acceptedTerms": true
}
```

**Response (201 Created):**
```json
{
  "data": {
    "userId": "usr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "user@example.com",
    "displayName": "LinguaLearner",
    "accessToken": "eyJhbGciOiJSUzI1NiIs...",
    "refreshToken": "rft_x9y8z7w6v5u4t3s2r1q0",
    "expiresIn": 900
  }
}
```

**Validation Rules:**
- `email`: Valid email format, unique
- `password`: Min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit, 1 special char
- `displayName`: 3–30 chars, alphanumeric + underscores
- `age`: Must be ≥ 13 (COPPA compliance)
- `targetLanguage`: Must be a supported language code

#### POST `/api/v1/auth/login`

Authenticate an existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "deviceId": "dev_abc123",
  "platform": "ios"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "userId": "usr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "accessToken": "eyJhbGciOiJSUzI1NiIs...",
    "refreshToken": "rft_x9y8z7w6v5u4t3s2r1q0",
    "expiresIn": 900,
    "profile": {
      "displayName": "LinguaLearner",
      "avatarUrl": "https://cdn.lingolearn.com/avatars/usr_a1b2c3.png",
      "premiumTier": "free",
      "currentStreak": 15,
      "totalXp": 4520,
      "gems": 340,
      "hearts": 5
    }
  }
}
```

#### POST `/api/v1/auth/refresh`

Refresh an expired access token.

**Request Body:**
```json
{
  "refreshToken": "rft_x9y8z7w6v5u4t3s2r1q0"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "accessToken": "eyJhbGciOiJSUzI1NiIs...",
    "refreshToken": "rft_newtoken123456",
    "expiresIn": 900
  }
}
```

#### POST `/api/v1/auth/logout`

Invalidate the current session.

**Request Body:**
```json
{
  "refreshToken": "rft_x9y8z7w6v5u4t3s2r1q0",
  "allDevices": false
}
```

**Response (200 OK):**
```json
{
  "data": {
    "message": "Successfully logged out"
  }
}
```

#### POST `/api/v1/auth/forgot-password`

Initiate password reset.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "message": "If an account exists with this email, a reset link has been sent."
  }
}
```

#### POST `/api/v1/auth/reset-password`

Complete password reset with token.

**Request Body:**
```json
{
  "token": "rst_abc123def456",
  "newPassword": "NewSecureP@ss456"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "message": "Password has been reset successfully."
  }
}
```

#### POST `/api/v1/auth/oauth/{provider}`

Authenticate via third-party OAuth (Google, Apple, Facebook).

**Request Body:**
```json
{
  "idToken": "google_id_token_here",
  "provider": "google",
  "deviceId": "dev_abc123"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "userId": "usr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "accessToken": "eyJhbGciOiJSUzI1NiIs...",
    "refreshToken": "rft_x9y8z7w6v5u4t3s2r1q0",
    "expiresIn": 900,
    "isNewUser": true
  }
}
```

### Authorization Roles

| Role        | Description                                  |
|-------------|----------------------------------------------|
| `user`      | Standard user, can learn and interact         |
| `premium`   | Premium subscriber with additional features   |
| `moderator` | Can moderate community content                |
| `admin`     | Full platform administration access           |
| `system`    | Internal service-to-service calls             |

### Role-Based Access Matrix

| Endpoint Pattern            | user | premium | moderator | admin |
|-----------------------------|------|---------|-----------|-------|
| `/api/v1/lessons/*`         | ✓    | ✓       | ✓         | ✓     |
| `/api/v1/premium/*`         | ✗    | ✓       | ✗         | ✓     |
| `/api/v1/moderation/*`      | ✗    | ✗       | ✓         | ✓     |
| `/api/v1/admin/*`           | ✗    | ✗       | ✗         | ✓     |

---

## 1.3 User Management Endpoints

### GET `/api/v1/users/me`

Get the authenticated user's profile.

**Response (200 OK):**
```json
{
  "data": {
    "userId": "usr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "user@example.com",
    "displayName": "LinguaLearner",
    "avatarUrl": "https://cdn.lingolearn.com/avatars/usr_a1b2c3.png",
    "nativeLanguage": "en",
    "bio": "Learning Spanish for travel!",
    "joinedAt": "2024-01-15T10:30:00Z",
    "premiumTier": "free",
    "stats": {
      "totalXp": 4520,
      "currentStreak": 15,
      "longestStreak": 42,
      "gems": 340,
      "hearts": 5,
      "lingots": 120,
      "lessonsCompleted": 156,
      "wordsLearned": 834,
      "timeSpentMinutes": 2340
    },
    "activeCourses": [
      {
        "courseId": "crs_spanish_en",
        "fromLanguage": "en",
        "targetLanguage": "es",
        "progress": 0.45,
        "currentLevel": 12,
        "crowns": 48
      }
    ],
    "settings": {
      "dailyGoalMinutes": 15,
      "soundEnabled": true,
      "notificationsEnabled": true,
      "reminderTime": "09:00",
      "timezone": "America/New_York"
    }
  }
}
```

### PATCH `/api/v1/users/me`

Update user profile.

**Request Body:**
```json
{
  "displayName": "SpanishMaster",
  "bio": "¡Hola! Learning Spanish every day!",
  "dailyGoalMinutes": 20,
  "timezone": "America/Chicago"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "userId": "usr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "displayName": "SpanishMaster",
    "bio": "¡Hola! Learning Spanish every day!",
    "updatedAt": "2024-06-15T14:30:00Z"
  }
}
```

### PUT `/api/v1/users/me/avatar`

Upload a new avatar image.

**Request:** `multipart/form-data` with `avatar` field (JPEG/PNG, max 5MB)

**Response (200 OK):**
```json
{
  "data": {
    "avatarUrl": "https://cdn.lingolearn.com/avatars/usr_a1b2c3_v2.png"
  }
}
```

### DELETE `/api/v1/users/me`

Delete user account (soft delete with 30-day recovery window).

**Request Body:**
```json
{
  "password": "SecureP@ss123",
  "reason": "no_longer_needed"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "message": "Account scheduled for deletion. You have 30 days to recover your account.",
    "deletionDate": "2024-07-15T14:30:00Z"
  }
}
```

### GET `/api/v1/users/{userId}/public-profile`

Get another user's public profile.

**Response (200 OK):**
```json
{
  "data": {
    "userId": "usr_f1e2d3c4-b5a6-7890-abcd-ef1234567890",
    "displayName": "PolyglotPat",
    "avatarUrl": "https://cdn.lingolearn.com/avatars/usr_f1e2d3.png",
    "joinedAt": "2023-06-10T08:00:00Z",
    "stats": {
      "totalXp": 15200,
      "currentStreak": 120,
      "coursesActive": 3,
      "lessonsCompleted": 520
    },
    "achievements": [
      {
        "achievementId": "ach_wildfire",
        "name": "Wildfire",
        "description": "Reach a 7-day streak",
        "earnedAt": "2023-06-18T10:00:00Z"
      }
    ]
  }
}
```

---

## 1.4 Course & Language Endpoints

### GET `/api/v1/languages`

List all available languages.

**Response (200 OK):**
```json
{
  "data": [
    {
      "code": "es",
      "name": "Spanish",
      "nativeName": "Español",
      "flagEmoji": "🇪🇸",
      "availableFrom": ["en", "pt", "fr", "de"],
      "totalLearners": 34500000,
      "status": "stable"
    },
    {
      "code": "fr",
      "name": "French",
      "nativeName": "Français",
      "flagEmoji": "🇫🇷",
      "availableFrom": ["en", "es", "de"],
      "totalLearners": 21000000,
      "status": "stable"
    }
  ]
}
```

### GET `/api/v1/courses`

List all available courses for the user's native language.

**Query Parameters:**
| Parameter      | Type   | Default | Description                     |
|----------------|--------|---------|---------------------------------|
| `fromLanguage` | string | user's  | Source language                  |
| `status`       | string | `stable`| `stable`, `beta`, `hatching`    |

**Response (200 OK):**
```json
{
  "data": [
    {
      "courseId": "crs_spanish_en",
      "fromLanguage": "en",
      "targetLanguage": "es",
      "title": "Spanish",
      "description": "Learn Spanish from English",
      "totalSkills": 120,
      "totalLessons": 480,
      "estimatedHours": 150,
      "status": "stable",
      "totalLearners": 34500000
    }
  ]
}
```

### POST `/api/v1/courses/{courseId}/enroll`

Enroll in a new course.

**Response (201 Created):**
```json
{
  "data": {
    "enrollmentId": "enr_abc123def456",
    "courseId": "crs_spanish_en",
    "enrolledAt": "2024-06-15T14:30:00Z",
    "currentSkillId": "skl_basics_1",
    "message": "Welcome to Spanish! Let's start with the basics."
  }
}
```

### GET `/api/v1/courses/{courseId}/skill-tree`

Get the full skill tree for a course.

**Response (200 OK):**
```json
{
  "data": {
    "courseId": "crs_spanish_en",
    "sections": [
      {
        "sectionId": "sec_beginner",
        "title": "Beginner",
        "order": 1,
        "skills": [
          {
            "skillId": "skl_basics_1",
            "title": "Basics 1",
            "description": "Learn basic greetings and introductions",
            "iconUrl": "https://cdn.lingolearn.com/skills/basics1.svg",
            "order": 1,
            "totalLessons": 5,
            "totalCrowns": 5,
            "status": "unlocked",
            "userProgress": {
              "lessonsCompleted": 3,
              "crownsEarned": 1,
              "lastPracticed": "2024-06-14T18:00:00Z",
              "strengthPercent": 85
            },
            "prerequisites": []
          },
          {
            "skillId": "skl_basics_2",
            "title": "Basics 2",
            "description": "Expand your basic vocabulary",
            "iconUrl": "https://cdn.lingolearn.com/skills/basics2.svg",
            "order": 2,
            "totalLessons": 5,
            "totalCrowns": 5,
            "status": "locked",
            "userProgress": null,
            "prerequisites": ["skl_basics_1"]
          }
        ]
      }
    ]
  }
}
```

---

## 1.5 Lesson & Exercise Endpoints

### GET `/api/v1/skills/{skillId}/lessons`

Get lessons for a specific skill.

**Response (200 OK):**
```json
{
  "data": {
    "skillId": "skl_basics_1",
    "lessons": [
      {
        "lessonId": "lsn_basics1_01",
        "order": 1,
        "type": "standard",
        "status": "completed",
        "xpReward": 10,
        "completedAt": "2024-06-10T14:00:00Z"
      },
      {
        "lessonId": "lsn_basics1_02",
        "order": 2,
        "type": "standard",
        "status": "available",
        "xpReward": 10,
        "completedAt": null
      }
    ]
  }
}
```

### POST `/api/v1/lessons/{lessonId}/start`

Start a lesson session.

**Response (200 OK):**
```json
{
  "data": {
    "sessionId": "ses_abc123def456",
    "lessonId": "lsn_basics1_02",
    "exercises": [
      {
        "exerciseId": "ex_001",
        "type": "translate",
        "order": 1,
        "prompt": "Translate this sentence",
        "sourceText": "The boy eats an apple",
        "sourceLanguage": "en",
        "targetLanguage": "es",
        "hints": [
          {"word": "boy", "translation": "niño"},
          {"word": "eats", "translation": "come"},
          {"word": "apple", "translation": "manzana"}
        ],
        "acceptedAnswers": [
          "El niño come una manzana"
        ]
      },
      {
        "exerciseId": "ex_002",
        "type": "multipleChoice",
        "order": 2,
        "prompt": "Select the correct translation",
        "sourceText": "el gato",
        "options": [
          {"id": "opt_a", "text": "the dog"},
          {"id": "opt_b", "text": "the cat"},
          {"id": "opt_c", "text": "the bird"},
          {"id": "opt_d", "text": "the fish"}
        ],
        "correctOptionId": "opt_b"
      },
      {
        "exerciseId": "ex_003",
        "type": "listenAndType",
        "order": 3,
        "prompt": "Type what you hear",
        "audioUrl": "https://cdn.lingolearn.com/audio/es/buenos_dias.mp3",
        "targetLanguage": "es",
        "acceptedAnswers": [
          "Buenos días",
          "buenos dias"
        ]
      },
      {
        "exerciseId": "ex_004",
        "type": "matchPairs",
        "order": 4,
        "prompt": "Match the pairs",
        "pairs": [
          {"left": "hola", "right": "hello"},
          {"left": "adiós", "right": "goodbye"},
          {"left": "gracias", "right": "thank you"},
          {"left": "por favor", "right": "please"}
        ]
      },
      {
        "exerciseId": "ex_005",
        "type": "fillInTheBlank",
        "order": 5,
        "prompt": "Complete the sentence",
        "sentence": "Yo ___ una manzana",
        "options": ["como", "comes", "come", "comen"],
        "correctAnswer": "como"
      },
      {
        "exerciseId": "ex_006",
        "type": "speak",
        "order": 6,
        "prompt": "Read this sentence aloud",
        "text": "Buenos días, ¿cómo estás?",
        "language": "es",
        "referenceAudioUrl": "https://cdn.lingolearn.com/audio/es/como_estas.mp3"
      }
    ],
    "totalExercises": 6,
    "heartsRemaining": 5,
    "bonusXpAvailable": true,
    "startedAt": "2024-06-15T14:30:00Z"
  }
}
```

### POST `/api/v1/sessions/{sessionId}/answer`

Submit an answer for an exercise.

**Request Body:**
```json
{
  "exerciseId": "ex_001",
  "answer": "El niño come una manzana",
  "timeSpentMs": 12500
}
```

**Response (200 OK):**
```json
{
  "data": {
    "correct": true,
    "correctAnswer": "El niño come una manzana",
    "alternativeAnswers": [
      "El chico come una manzana"
    ],
    "xpEarned": 10,
    "explanation": null,
    "exercisesRemaining": 5,
    "heartsRemaining": 5,
    "streakBonus": false,
    "comboCount": 1
  }
}
```

**Response for incorrect answer (200 OK):**
```json
{
  "data": {
    "correct": false,
    "userAnswer": "El niño comer una manzana",
    "correctAnswer": "El niño come una manzana",
    "explanation": "'Come' is the correct conjugation of 'comer' for 'él/ella' (he/she).",
    "exercisesRemaining": 5,
    "heartsRemaining": 4,
    "comboCount": 0
  }
}
```

### POST `/api/v1/sessions/{sessionId}/complete`

Complete a lesson session.

**Request Body:**
```json
{
  "sessionId": "ses_abc123def456",
  "completedExercises": 6,
  "correctAnswers": 5,
  "incorrectAnswers": 1,
  "totalTimeMs": 180000,
  "heartsUsed": 1
}
```

**Response (200 OK):**
```json
{
  "data": {
    "sessionId": "ses_abc123def456",
    "result": "passed",
    "xpEarned": 15,
    "bonusXp": 5,
    "totalXpEarned": 20,
    "gemsEarned": 2,
    "accuracy": 0.83,
    "newTotalXp": 4540,
    "streakExtended": true,
    "currentStreak": 16,
    "crownsProgress": {
      "skillId": "skl_basics_1",
      "currentCrown": 2,
      "progressToNextCrown": 0.6
    },
    "achievements": [
      {
        "achievementId": "ach_sharpshooter",
        "name": "Sharpshooter",
        "description": "Complete 5 lessons without losing a heart"
      }
    ],
    "dailyGoalProgress": {
      "goalMinutes": 15,
      "completedMinutes": 8,
      "completed": false
    }
  }
}
```

### POST `/api/v1/skills/{skillId}/practice`

Start a practice session for a skill (spaced repetition).

**Response (200 OK):** Same structure as lesson start, but with exercises selected based on spaced repetition algorithm targeting weak areas.

---

## 1.6 Progress & XP Endpoints

### GET `/api/v1/users/me/progress`

Get overall learning progress.

**Response (200 OK):**
```json
{
  "data": {
    "totalXp": 4540,
    "level": 12,
    "xpToNextLevel": 460,
    "xpForCurrentLevel": 540,
    "courses": [
      {
        "courseId": "crs_spanish_en",
        "targetLanguage": "es",
        "overallProgress": 0.45,
        "skillsCompleted": 54,
        "totalSkills": 120,
        "crownsEarned": 162,
        "totalCrowns": 600,
        "wordsLearned": 834,
        "totalWords": 2100
      }
    ],
    "weeklyXp": [
      {"date": "2024-06-09", "xp": 50},
      {"date": "2024-06-10", "xp": 30},
      {"date": "2024-06-11", "xp": 45},
      {"date": "2024-06-12", "xp": 20},
      {"date": "2024-06-13", "xp": 55},
      {"date": "2024-06-14", "xp": 40},
      {"date": "2024-06-15", "xp": 20}
    ]
  }
}
```

### GET `/api/v1/users/me/progress/daily`

Get daily XP progress for goal tracking.

**Response (200 OK):**
```json
{
  "data": {
    "date": "2024-06-15",
    "goalMinutes": 15,
    "completedMinutes": 8,
    "xpEarned": 20,
    "lessonsCompleted": 1,
    "practiceSessionsCompleted": 0,
    "goalMet": false,
    "goalStreak": 15
  }
}
```

### GET `/api/v1/users/me/xp-history`

Get historical XP data.

**Query Parameters:**
| Parameter  | Type   | Default   | Description              |
|------------|--------|-----------|--------------------------|
| `period`   | string | `week`    | `day`, `week`, `month`   |
| `startDate`| string | -7 days   | ISO 8601 date            |
| `endDate`  | string | today     | ISO 8601 date            |

**Response (200 OK):**
```json
{
  "data": {
    "entries": [
      {
        "date": "2024-06-15",
        "totalXp": 20,
        "sources": [
          {"type": "lesson", "xp": 15, "count": 1},
          {"type": "practice", "xp": 5, "count": 1}
        ]
      }
    ],
    "summary": {
      "totalXp": 260,
      "averageDailyXp": 37,
      "activeDays": 7,
      "bestDay": {"date": "2024-06-13", "xp": 55}
    }
  }
}
```

---

## 1.7 Streak Endpoints

### GET `/api/v1/users/me/streak`

Get current streak information.

**Response (200 OK):**
```json
{
  "data": {
    "currentStreak": 16,
    "longestStreak": 42,
    "todayCompleted": true,
    "streakFreezeAvailable": 2,
    "streakFreezeUsedToday": false,
    "lastActivityDate": "2024-06-15",
    "streakStartDate": "2024-05-30",
    "timezone": "America/New_York",
    "streakSociety": {
      "qualified": true,
      "currentWeekDays": 5,
      "requiredDays": 7
    },
    "milestones": [
      {"days": 7, "achieved": true, "reward": {"gems": 10}},
      {"days": 14, "achieved": true, "reward": {"gems": 20}},
      {"days": 30, "achieved": false, "reward": {"gems": 50}},
      {"days": 50, "achieved": false, "reward": {"gems": 100}},
      {"days": 100, "achieved": false, "reward": {"gems": 250}}
    ]
  }
}
```

### POST `/api/v1/users/me/streak/freeze`

Use a streak freeze to protect the streak.

**Response (200 OK):**
```json
{
  "data": {
    "streakFreezeUsed": true,
    "streakPreserved": true,
    "freezesRemaining": 1,
    "currentStreak": 16
  }
}
```

---

## 1.8 Leaderboard Endpoints

### GET `/api/v1/leaderboards/weekly`

Get the user's current weekly leaderboard.

**Query Parameters:**
| Parameter | Type   | Default    | Description                                |
|-----------|--------|------------|--------------------------------------------|
| `league`  | string | user's     | `bronze`, `silver`, `gold`, `sapphire`, `ruby`, `emerald`, `amethyst`, `pearl`, `obsidian`, `diamond` |

**Response (200 OK):**
```json
{
  "data": {
    "leagueId": "lg_gold_2024w24",
    "league": "gold",
    "weekStart": "2024-06-10T00:00:00Z",
    "weekEnd": "2024-06-16T23:59:59Z",
    "promotionZone": 10,
    "demotionZone": 5,
    "rankings": [
      {
        "rank": 1,
        "userId": "usr_xyz789",
        "displayName": "TopLearner",
        "avatarUrl": "https://cdn.lingolearn.com/avatars/usr_xyz789.png",
        "xpThisWeek": 1250,
        "isCurrentUser": false,
        "premiumBadge": true
      },
      {
        "rank": 5,
        "userId": "usr_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "displayName": "LinguaLearner",
        "avatarUrl": "https://cdn.lingolearn.com/avatars/usr_a1b2c3.png",
        "xpThisWeek": 260,
        "isCurrentUser": true,
        "premiumBadge": false
      }
    ],
    "totalParticipants": 30,
    "userPosition": {
      "rank": 5,
      "zone": "safe",
      "xpToPromotion": 200,
      "xpAboveDemotion": 80
    }
  }
}
```

---

## 1.9 Shop & In-App Purchase Endpoints

### GET `/api/v1/shop/items`

List all available shop items.

**Response (200 OK):**
```json
{
  "data": [
    {
      "itemId": "itm_streak_freeze",
      "name": "Streak Freeze",
      "description": "Protect your streak for one day of inactivity",
      "price": {"gems": 200},
      "maxOwnable": 2,
      "currentOwned": 1,
      "iconUrl": "https://cdn.lingolearn.com/shop/streak_freeze.svg",
      "category": "power_up"
    },
    {
      "itemId": "itm_heart_refill",
      "name": "Heart Refill",
      "description": "Refill all your hearts",
      "price": {"gems": 350},
      "maxOwnable": null,
      "currentOwned": 0,
      "iconUrl": "https://cdn.lingolearn.com/shop/heart_refill.svg",
      "category": "power_up"
    },
    {
      "itemId": "itm_double_or_nothing",
      "name": "Double or Nothing",
      "description": "Earn double gems if you maintain a 7-day streak",
      "price": {"gems": 50},
      "maxOwnable": 1,
      "currentOwned": 0,
      "iconUrl": "https://cdn.lingolearn.com/shop/double.svg",
      "category": "wager"
    }
  ]
}
```

### POST `/api/v1/shop/purchase`

Purchase an item from the shop.

**Request Body:**
```json
{
  "itemId": "itm_streak_freeze",
  "quantity": 1
}
```

**Response (200 OK):**
```json
{
  "data": {
    "purchaseId": "pur_abc123",
    "itemId": "itm_streak_freeze",
    "gemsSpent": 200,
    "gemsRemaining": 140,
    "currentOwned": 2
  }
}
```

### GET `/api/v1/subscriptions/plans`

List available premium subscription plans.

**Response (200 OK):**
```json
{
  "data": [
    {
      "planId": "plan_super_monthly",
      "name": "Super Duolingo",
      "interval": "monthly",
      "price": {
        "amount": 12.99,
        "currency": "USD"
      },
      "features": [
        "No ads",
        "Unlimited hearts",
        "Unlimited skill practice",
        "Streak repair",
        "Progress quizzes",
        "Mastery quiz"
      ]
    },
    {
      "planId": "plan_super_annual",
      "name": "Super Duolingo (Annual)",
      "interval": "yearly",
      "price": {
        "amount": 83.99,
        "currency": "USD"
      },
      "monthlyEquivalent": 7.00,
      "savingsPercent": 46,
      "features": [
        "All monthly features",
        "Annual savings"
      ]
    },
    {
      "planId": "plan_family",
      "name": "Family Plan",
      "interval": "monthly",
      "price": {
        "amount": 19.99,
        "currency": "USD"
      },
      "maxMembers": 6,
      "features": [
        "All Super features for up to 6 family members"
      ]
    }
  ]
}
```

---

## 1.10 Notification Endpoints

### GET `/api/v1/notifications`

Get user notifications.

**Query Parameters:**
| Parameter | Type    | Default | Description              |
|-----------|---------|---------|--------------------------|
| `page`    | integer | 1       | Page number              |
| `limit`   | integer | 20      | Items per page           |
| `unread`  | boolean | false   | Filter unread only       |

**Response (200 OK):**
```json
{
  "data": {
    "notifications": [
      {
        "notificationId": "ntf_abc123",
        "type": "streak_reminder",
        "title": "Don't lose your streak! 🔥",
        "body": "You haven't practiced today. Complete a lesson to keep your 16-day streak!",
        "createdAt": "2024-06-15T18:00:00Z",
        "read": false,
        "actionUrl": "/learn",
        "imageUrl": "https://cdn.lingolearn.com/notifications/streak.svg"
      },
      {
        "notificationId": "ntf_def456",
        "type": "leaderboard_update",
        "title": "Leaderboard Update 📊",
        "body": "You moved up to rank #5 in the Gold League!",
        "createdAt": "2024-06-15T12:00:00Z",
        "read": true,
        "actionUrl": "/leaderboard"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "hasMore": true
    },
    "unreadCount": 3
  }
}
```

### PATCH `/api/v1/notifications/{notificationId}/read`

Mark a notification as read.

**Response (200 OK):**
```json
{
  "data": {
    "notificationId": "ntf_abc123",
    "read": true
  }
}
```

### POST `/api/v1/notifications/read-all`

Mark all notifications as read.

**Response (200 OK):**
```json
{
  "data": {
    "markedCount": 3
  }
}
```

### PUT `/api/v1/users/me/notification-preferences`

Update notification preferences.

**Request Body:**
```json
{
  "pushEnabled": true,
  "emailEnabled": true,
  "streakReminders": true,
  "leaderboardUpdates": true,
  "friendActivity": true,
  "promotions": false,
  "reminderTime": "09:00",
  "quietHoursStart": "22:00",
  "quietHoursEnd": "07:00"
}
```

---

## 1.11 Achievement & Badge Endpoints

### GET `/api/v1/users/me/achievements`

Get all achievements for the current user.

**Response (200 OK):**
```json
{
  "data": {
    "achievements": [
      {
        "achievementId": "ach_wildfire",
        "name": "Wildfire",
        "description": "Reach a 7-day streak",
        "iconUrl": "https://cdn.lingolearn.com/achievements/wildfire.svg",
        "category": "streak",
        "tier": "bronze",
        "earned": true,
        "earnedAt": "2024-06-05T10:00:00Z",
        "progress": 1.0
      },
      {
        "achievementId": "ach_sage",
        "name": "Sage",
        "description": "Earn 1000 XP",
        "iconUrl": "https://cdn.lingolearn.com/achievements/sage.svg",
        "category": "xp",
        "tier": "gold",
        "earned": true,
        "earnedAt": "2024-05-20T15:30:00Z",
        "progress": 1.0
      },
      {
        "achievementId": "ach_photogenic",
        "name": "Photogenic",
        "description": "Upload a profile photo",
        "iconUrl": "https://cdn.lingolearn.com/achievements/photogenic.svg",
        "category": "profile",
        "tier": null,
        "earned": false,
        "earnedAt": null,
        "progress": 0
      }
    ],
    "totalEarned": 12,
    "totalAvailable": 45
  }
}
```

---

## 1.12 Friend & Social Endpoints

### GET `/api/v1/friends`

Get the user's friend list.

**Response (200 OK):**
```json
{
  "data": {
    "friends": [
      {
        "userId": "usr_friend1",
        "displayName": "PolyglotPat",
        "avatarUrl": "https://cdn.lingolearn.com/avatars/usr_friend1.png",
        "currentStreak": 42,
        "totalXp": 15200,
        "xpThisWeek": 340,
        "isActive": true,
        "lastActive": "2024-06-15T12:00:00Z"
      }
    ],
    "totalFriends": 8
  }
}
```

### POST `/api/v1/friends/invite`

Send a friend request.

**Request Body:**
```json
{
  "userId": "usr_friend2"
}
```

**Response (201 Created):**
```json
{
  "data": {
    "requestId": "freq_abc123",
    "status": "pending",
    "sentAt": "2024-06-15T14:30:00Z"
  }
}
```

### POST `/api/v1/friends/requests/{requestId}/accept`

Accept a friend request.

### POST `/api/v1/friends/requests/{requestId}/decline`

Decline a friend request.

### DELETE `/api/v1/friends/{userId}`

Remove a friend.

---

## 1.13 Settings & Preferences Endpoints

### GET `/api/v1/users/me/settings`

Get all user settings.

**Response (200 OK):**
```json
{
  "data": {
    "dailyGoalMinutes": 15,
    "soundEnabled": true,
    "speakingExercises": true,
    "listeningExercises": true,
    "motivationalMessages": true,
    "autoPlayAudio": true,
    "darkMode": false,
    "hapticFeedback": true,
    "language": "en",
    "timezone": "America/New_York",
    "privacySettings": {
      "profilePublic": true,
      "showOnLeaderboard": true,
      "allowFriendRequests": true
    }
  }
}
```

### PATCH `/api/v1/users/me/settings`

Update user settings.

**Request Body:** Partial object with any settings fields to update.

---

## 1.14 Admin Endpoints

### GET `/api/v1/admin/users`

List all users (admin only).

**Query Parameters:**
| Parameter   | Type    | Default | Description                     |
|-------------|---------|---------|----------------------------------|
| `page`      | integer | 1       | Page number                      |
| `limit`     | integer | 50      | Items per page (max 100)         |
| `search`    | string  | -       | Search by name or email          |
| `status`    | string  | -       | `active`, `suspended`, `deleted` |
| `premium`   | boolean | -       | Filter by premium status         |
| `sortBy`    | string  | `createdAt` | Sort field                   |
| `sortOrder` | string  | `desc`  | `asc` or `desc`                  |

### POST `/api/v1/admin/users/{userId}/suspend`

Suspend a user account.

**Request Body:**
```json
{
  "reason": "Terms of service violation",
  "duration": "7d",
  "notifyUser": true
}
```

### GET `/api/v1/admin/analytics/overview`

Get platform analytics overview.

**Response (200 OK):**
```json
{
  "data": {
    "totalUsers": 2450000,
    "dailyActiveUsers": 340000,
    "monthlyActiveUsers": 890000,
    "premiumSubscribers": 125000,
    "averageSessionMinutes": 8.5,
    "averageLessonsPerDay": 2.3,
    "retentionRate7Day": 0.65,
    "retentionRate30Day": 0.42,
    "topLanguages": [
      {"language": "es", "learners": 850000},
      {"language": "fr", "learners": 520000},
      {"language": "ja", "learners": 380000}
    ]
  }
}
```

### POST `/api/v1/admin/courses`

Create a new course (admin only).

### PUT `/api/v1/admin/courses/{courseId}/skills/{skillId}`

Update a skill in a course.

### POST `/api/v1/admin/courses/{courseId}/skills/{skillId}/exercises`

Add exercises to a skill.

---

## 1.15 Error Codes & Error Response Schema

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request body contains invalid fields.",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_FORMAT"
      }
    ],
    "requestId": "req_abc123def456",
    "timestamp": "2024-06-15T14:30:00Z",
    "documentation": "https://docs.lingolearn.com/errors/VALIDATION_ERROR"
  }
}
```

### Error Code Reference

| HTTP Status | Error Code                | Description                                           |
|-------------|---------------------------|-------------------------------------------------------|
| 400         | `VALIDATION_ERROR`        | Request body or parameters are invalid                 |
| 400         | `INVALID_ANSWER_FORMAT`   | Answer format doesn't match exercise type              |
| 401         | `UNAUTHORIZED`            | Missing or invalid authentication token                |
| 401         | `TOKEN_EXPIRED`           | Access token has expired                               |
| 401         | `INVALID_REFRESH_TOKEN`   | Refresh token is invalid or expired                    |
| 403         | `FORBIDDEN`               | User lacks permission for this action                  |
| 403         | `PREMIUM_REQUIRED`        | Feature requires premium subscription                  |
| 403         | `NO_HEARTS_REMAINING`     | No hearts remaining (free tier)                        |
| 403         | `ACCOUNT_SUSPENDED`       | User account is suspended                              |
| 404         | `NOT_FOUND`               | Requested resource not found                           |
| 404         | `COURSE_NOT_FOUND`        | Specified course does not exist                        |
| 404         | `LESSON_NOT_FOUND`        | Specified lesson does not exist                        |
| 404         | `SKILL_LOCKED`            | Skill is not yet unlocked                              |
| 409         | `ALREADY_ENROLLED`        | User already enrolled in this course                   |
| 409         | `DUPLICATE_EMAIL`         | Email address already registered                       |
| 409         | `SESSION_IN_PROGRESS`     | A lesson session is already active                     |
| 422         | `INSUFFICIENT_GEMS`       | Not enough gems for purchase                           |
| 422         | `MAX_ITEMS_OWNED`         | Maximum number of this item already owned              |
| 429         | `RATE_LIMIT_EXCEEDED`     | Too many requests                                      |
| 500         | `INTERNAL_ERROR`          | Unexpected server error                                |
| 503         | `SERVICE_UNAVAILABLE`     | Service temporarily unavailable                        |

---

## 1.16 Rate Limiting Headers

All responses include rate limiting headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1700001000
X-RateLimit-RetryAfter: 60
```

### Rate Limits by Endpoint Category

| Category            | Requests/Minute | Burst |
|---------------------|-----------------|-------|
| Authentication      | 10              | 5     |
| Lessons/Exercises   | 60              | 20    |
| User Profile        | 30              | 10    |
| Social              | 30              | 10    |
| Shop/Purchases      | 20              | 5     |
| Admin               | 120             | 40    |
| General (default)   | 100             | 30    |

---

## 1.17 Pagination Convention

All list endpoints support cursor-based or offset-based pagination:

### Offset-Based (default)

**Request:**
```
GET /api/v1/notifications?page=2&limit=20
```

**Response includes:**
```json
{
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 95,
    "totalPages": 5,
    "hasMore": true
  }
}
```

### Cursor-Based (for large datasets)

**Request:**
```
GET /api/v1/leaderboards/weekly?cursor=eyJyYW5rIjo1MH0&limit=30
```

**Response includes:**
```json
{
  "pagination": {
    "cursor": "eyJyYW5rIjo4MH0",
    "limit": 30,
    "hasMore": true
  }
}
```

---

## 1.18 Example Payloads

### Complete Lesson Flow

```
1. GET  /api/v1/courses/crs_spanish_en/skill-tree     → View available skills
2. GET  /api/v1/skills/skl_basics_1/lessons            → View lessons in a skill
3. POST /api/v1/lessons/lsn_basics1_02/start           → Start a lesson
4. POST /api/v1/sessions/ses_abc123/answer              → Submit each answer
5. POST /api/v1/sessions/ses_abc123/complete            → Complete the lesson
6. GET  /api/v1/users/me/progress                       → View updated progress
```

### User Registration Flow

```
1. POST /api/v1/auth/register                          → Create account
2. GET  /api/v1/courses                                 → Browse courses
3. POST /api/v1/courses/crs_spanish_en/enroll           → Enroll in course
4. GET  /api/v1/courses/crs_spanish_en/skill-tree       → View skill tree
5. POST /api/v1/lessons/lsn_basics1_01/start            → Start first lesson
```

### Daily Session Flow

```
1. POST /api/v1/auth/login                             → Authenticate
2. GET  /api/v1/users/me                                → Load profile & stats
3. GET  /api/v1/users/me/streak                         → Check streak status
4. GET  /api/v1/users/me/progress/daily                 → Check daily goal
5. GET  /api/v1/leaderboards/weekly                     → View leaderboard
6. POST /api/v1/lessons/{lessonId}/start                → Start lesson
7. POST /api/v1/sessions/{sessionId}/answer (x N)      → Complete exercises
8. POST /api/v1/sessions/{sessionId}/complete           → Finish lesson
```

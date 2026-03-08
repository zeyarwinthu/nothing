# 5. Entity & Database Schema Documentation

## 5.1 Entity-Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    users     │       │   courses    │       │   skills     │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │       │ id (PK)      │
│ email        │       │ from_lang    │       │ course_id(FK)│
│ password_hash│       │ target_lang  │       │ section_id   │
│ display_name │       │ title        │       │ title        │
│ avatar_url   │       │ status       │       │ order_index  │
│ native_lang  │       │ total_skills │       │ total_lessons│
│ premium_tier │       │ total_lessons│       │ total_crowns │
│ created_at   │       │ created_at   │       │ icon_url     │
│ updated_at   │       │ updated_at   │       │ created_at   │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       │                      │                      │
       │    ┌─────────────────┘                      │
       │    │                                        │
       ▼    ▼                                        │
┌──────────────┐       ┌──────────────┐              │
│ enrollments  │       │skill_prereqs │              │
├──────────────┤       ├──────────────┤              │
│ id (PK)      │       │ skill_id(FK) │◄─────────────┘
│ user_id (FK) │       │ prereq_id(FK)│
│ course_id(FK)│       └──────────────┘
│ enrolled_at  │
│ current_skill│       ┌──────────────┐       ┌──────────────┐
│ status       │       │   lessons    │       │  exercises   │
└──────────────┘       ├──────────────┤       ├──────────────┤
                       │ id (PK)      │       │ id (PK)      │
       ┌───────────────│ skill_id(FK) │       │ lesson_id(FK)│
       │               │ order_index  │───────│ type         │
       │               │ type         │       │ order_index  │
       │               │ xp_reward    │       │ prompt       │
       │               │ created_at   │       │ source_text  │
       │               └──────────────┘       │ correct_ans  │
       │                                      │ difficulty   │
       │                                      │ created_at   │
       │                                      └──────────────┘
       │
       │               ┌──────────────┐       ┌──────────────┐
       │               │lesson_sessions│      │session_answers│
       │               ├──────────────┤       ├──────────────┤
       └──────────────►│ id (PK)      │       │ id (PK)      │
                       │ user_id (FK) │       │ session_id(FK│
                       │ lesson_id(FK)│───────│ exercise_id  │
                       │ started_at   │       │ user_answer  │
                       │ completed_at │       │ is_correct   │
                       │ status       │       │ time_spent_ms│
                       │ xp_earned    │       │ created_at   │
                       │ hearts_used  │       └──────────────┘
                       │ accuracy     │
                       └──────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│user_progress │       │  xp_history  │       │   streaks    │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │       │ id (PK)      │
│ user_id (FK) │       │ user_id (FK) │       │ user_id (FK) │
│ course_id(FK)│       │ amount       │       │ current_count│
│ total_xp     │       │ source_type  │       │ longest_count│
│ level        │       │ source_id    │       │ start_date   │
│ crowns_earned│       │ earned_at    │       │ last_activity│
│ words_learned│       │ course_id    │       │ freeze_count │
│ updated_at   │       └──────────────┘       │ updated_at   │
└──────────────┘                              └──────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  leagues     │       │league_members│       │leaderboard_  │
├──────────────┤       ├──────────────┤       │history       │
│ id (PK)      │       │ id (PK)      │       ├──────────────┤
│ name         │       │ league_id(FK)│       │ id (PK)      │
│ tier         │       │ user_id (FK) │       │ user_id (FK) │
│ week_start   │       │ weekly_xp    │       │ league_id(FK)│
│ week_end     │       │ rank         │       │ week         │
│ promotion_ct │       │ joined_at    │       │ final_rank   │
│ demotion_ct  │       └──────────────┘       │ xp_total     │
└──────────────┘                              │ promoted     │
                                              └──────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ achievements │       │user_achievmts│       │  shop_items  │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │       │ id (PK)      │
│ name         │       │ user_id (FK) │       │ name         │
│ description  │       │ achievement  │       │ description  │
│ icon_url     │       │   _id (FK)   │       │ price_gems   │
│ category     │       │ earned_at    │       │ max_ownable  │
│ tier         │       │ progress     │       │ category     │
│ criteria_json│       └──────────────┘       │ icon_url     │
└──────────────┘                              │ is_active    │
                                              └──────────────┘
┌──────────────┐       ┌──────────────┐
│  purchases   │       │ inventory    │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ user_id (FK) │       │ user_id (FK) │
│ item_id (FK) │       │ item_id (FK) │
│ gems_spent   │       │ quantity     │
│ purchased_at │       │ updated_at   │
└──────────────┘       └──────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ friendships  │       │friend_request│       │notifications │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │       │ id (PK)      │
│ user_id (FK) │       │ sender_id(FK)│       │ user_id (FK) │
│ friend_id(FK)│       │ receiver_id  │       │ type         │
│ created_at   │       │   (FK)       │       │ title        │
└──────────────┘       │ status       │       │ body         │
                       │ created_at   │       │ is_read      │
                       └──────────────┘       │ action_url   │
                                              │ created_at   │
┌──────────────┐       ┌──────────────┐       └──────────────┘
│subscriptions │       │refresh_tokens│
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ user_id (FK) │       │ user_id (FK) │
│ plan_id      │       │ token_hash   │
│ status       │       │ device_id    │
│ started_at   │       │ expires_at   │
│ expires_at   │       │ created_at   │
│ platform     │       │ revoked_at   │
│ receipt_data │       └──────────────┘
└──────────────┘

┌──────────────┐       ┌──────────────┐
│ word_strength│       │ word_bank    │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ user_id (FK) │       │ word         │
│ word_id (FK) │       │ translation  │
│ strength     │       │ language     │
│ last_seen    │       │ part_of_speech│
│ next_review  │       │ difficulty   │
│ review_count │       │ audio_url    │
│ ease_factor  │       │ course_id(FK)│
└──────────────┘       └──────────────┘
```

---

## 5.2 Table Definitions & Field Descriptions

### `users`

Core user account table.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key (UUID)                         |
| `email`         | VARCHAR(255)     | No       | -                | Unique email address                       |
| `password_hash` | VARCHAR(255)     | Yes      | NULL             | bcrypt password hash (null for OAuth-only) |
| `display_name`  | VARCHAR(30)      | No       | -                | User's display name                        |
| `avatar_url`    | VARCHAR(500)     | Yes      | NULL             | CDN URL for avatar image                   |
| `native_language`| VARCHAR(5)      | No       | 'en'             | ISO 639-1 native language code             |
| `bio`           | VARCHAR(500)     | Yes      | NULL             | User biography                             |
| `age`           | TINYINT UNSIGNED | No       | -                | User's age at registration                 |
| `premium_tier`  | ENUM             | No       | 'free'           | `free`, `super`, `family`                  |
| `role`          | ENUM             | No       | 'user'           | `user`, `moderator`, `admin`               |
| `status`        | ENUM             | No       | 'active'         | `active`, `suspended`, `deleted`           |
| `gems`          | INT UNSIGNED     | No       | 0                | Current gem balance                        |
| `hearts`        | TINYINT UNSIGNED | No       | 5                | Current hearts (max 5 for free)            |
| `hearts_refill_at`| DATETIME       | Yes      | NULL             | Next heart regeneration time               |
| `email_verified`| BOOLEAN          | No       | FALSE            | Email verification status                  |
| `last_login_at` | DATETIME         | Yes      | NULL             | Last successful login                      |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Account creation timestamp                 |
| `updated_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Last modification timestamp                |
| `deleted_at`    | DATETIME         | Yes      | NULL             | Soft delete timestamp                      |

### `courses`

Language course definitions.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `from_language` | VARCHAR(5)       | No       | -                | Source language code                        |
| `target_language`| VARCHAR(5)      | No       | -                | Target language code                        |
| `title`         | VARCHAR(100)     | No       | -                | Course title                               |
| `description`   | TEXT             | Yes      | NULL             | Course description                         |
| `total_skills`  | INT UNSIGNED     | No       | 0                | Total number of skills                     |
| `total_lessons` | INT UNSIGNED     | No       | 0                | Total number of lessons                    |
| `estimated_hours`| INT UNSIGNED    | No       | 0                | Estimated hours to complete                |
| `status`        | ENUM             | No       | 'hatching'       | `hatching`, `beta`, `stable`               |
| `total_learners`| INT UNSIGNED     | No       | 0                | Count of enrolled learners                 |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Creation timestamp                         |
| `updated_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Last modification timestamp                |

### `enrollments`

User enrollment in courses.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `course_id`     | CHAR(36)         | No       | -                | FK → courses.id                            |
| `current_skill_id`| CHAR(36)       | Yes      | NULL             | FK → skills.id (current active skill)      |
| `status`        | ENUM             | No       | 'active'         | `active`, `paused`, `completed`            |
| `enrolled_at`   | DATETIME         | No       | CURRENT_TIMESTAMP| Enrollment timestamp                       |
| `completed_at`  | DATETIME         | Yes      | NULL             | Course completion timestamp                |

### `skills`

Individual skills within a course (nodes in the skill tree).

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `course_id`     | CHAR(36)         | No       | -                | FK → courses.id                            |
| `section_id`    | VARCHAR(100)     | No       | -                | Section grouping identifier                |
| `title`         | VARCHAR(100)     | No       | -                | Skill title                                |
| `description`   | TEXT             | Yes      | NULL             | Skill description                          |
| `icon_url`      | VARCHAR(500)     | Yes      | NULL             | Icon CDN URL                               |
| `order_index`   | INT UNSIGNED     | No       | 0                | Display order within section               |
| `total_lessons` | INT UNSIGNED     | No       | 0                | Number of lessons in this skill            |
| `total_crowns`  | TINYINT UNSIGNED | No       | 5                | Max crowns achievable (typically 5)        |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Creation timestamp                         |
| `updated_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Modification timestamp                     |

### `skill_prerequisites`

Defines skill unlock dependencies.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `skill_id`      | CHAR(36)         | No       | -                | FK → skills.id (the skill to unlock)       |
| `prerequisite_id`| CHAR(36)        | No       | -                | FK → skills.id (required skill)            |

**Primary Key:** (`skill_id`, `prerequisite_id`)

### `lessons`

Individual lessons within a skill.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `skill_id`      | CHAR(36)         | No       | -                | FK → skills.id                             |
| `order_index`   | INT UNSIGNED     | No       | 0                | Lesson order within skill                  |
| `type`          | ENUM             | No       | 'standard'       | `standard`, `practice`, `test`, `story`    |
| `xp_reward`     | INT UNSIGNED     | No       | 10               | Base XP reward for completion              |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Creation timestamp                         |

### `exercises`

Exercise content within lessons.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `lesson_id`     | CHAR(36)         | No       | -                | FK → lessons.id                            |
| `type`          | ENUM             | No       | -                | `translate`, `multiple_choice`, `listen_type`, `speak`, `match_pairs`, `fill_blank`, `tap_order` |
| `order_index`   | INT UNSIGNED     | No       | 0                | Exercise order in lesson                   |
| `prompt`        | VARCHAR(500)     | No       | -                | Exercise instruction text                  |
| `source_text`   | TEXT             | Yes      | NULL             | Source text (for translation exercises)    |
| `source_language`| VARCHAR(5)      | Yes      | NULL             | Source text language                        |
| `target_language`| VARCHAR(5)      | Yes      | NULL             | Target response language                    |
| `correct_answer`| TEXT             | No       | -                | Primary correct answer                     |
| `alternatives_json`| JSON          | Yes      | NULL             | Alternative correct answers (JSON array)   |
| `options_json`  | JSON             | Yes      | NULL             | Multiple choice options (JSON array)       |
| `hints_json`    | JSON             | Yes      | NULL             | Hint data (JSON object)                    |
| `audio_url`     | VARCHAR(500)     | Yes      | NULL             | Audio file URL for listening exercises     |
| `image_url`     | VARCHAR(500)     | Yes      | NULL             | Image URL for visual exercises             |
| `difficulty`    | TINYINT UNSIGNED | No       | 1                | Difficulty level (1–5)                     |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Creation timestamp                         |

### `lesson_sessions`

Active and completed lesson sessions.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key (session ID)                   |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `lesson_id`     | CHAR(36)         | No       | -                | FK → lessons.id                            |
| `status`        | ENUM             | No       | 'in_progress'    | `in_progress`, `completed`, `abandoned`, `failed` |
| `started_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Session start time                         |
| `completed_at`  | DATETIME         | Yes      | NULL             | Session completion time                    |
| `xp_earned`     | INT UNSIGNED     | No       | 0                | Total XP earned in this session            |
| `bonus_xp`      | INT UNSIGNED     | No       | 0                | Bonus XP (perfect lesson, etc.)            |
| `accuracy`      | DECIMAL(5,4)     | Yes      | NULL             | Percentage accuracy (0.0000–1.0000)        |
| `hearts_used`   | TINYINT UNSIGNED | No       | 0                | Hearts lost during this session            |
| `exercises_total`| INT UNSIGNED    | No       | 0                | Total exercises in this session            |
| `exercises_correct`| INT UNSIGNED  | No       | 0                | Number of correct answers                  |
| `duration_ms`   | INT UNSIGNED     | Yes      | NULL             | Total session duration in milliseconds     |

### `session_answers`

Individual answer records within a session.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `session_id`    | CHAR(36)         | No       | -                | FK → lesson_sessions.id                    |
| `exercise_id`   | CHAR(36)         | No       | -                | FK → exercises.id                          |
| `user_answer`   | TEXT             | No       | -                | The user's submitted answer                |
| `is_correct`    | BOOLEAN          | No       | -                | Whether the answer was correct             |
| `time_spent_ms` | INT UNSIGNED     | No       | 0                | Time spent on this exercise (ms)           |
| `attempt_number`| TINYINT UNSIGNED | No       | 1                | Attempt number (for retries)               |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Answer submission time                     |

### `user_progress`

User progress per course.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `course_id`     | CHAR(36)         | No       | -                | FK → courses.id                            |
| `total_xp`      | INT UNSIGNED     | No       | 0                | Total XP earned in this course             |
| `level`         | INT UNSIGNED     | No       | 1                | Current level                              |
| `crowns_earned` | INT UNSIGNED     | No       | 0                | Total crowns earned                        |
| `skills_completed`| INT UNSIGNED   | No       | 0                | Number of completed skills                 |
| `words_learned` | INT UNSIGNED     | No       | 0                | Number of unique words learned             |
| `lessons_completed`| INT UNSIGNED  | No       | 0                | Total lessons completed                    |
| `time_spent_minutes`| INT UNSIGNED | No       | 0                | Total time spent (minutes)                 |
| `updated_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Last update timestamp                      |

**Unique Constraint:** (`user_id`, `course_id`)

### `xp_history`

Detailed XP earning history.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `amount`        | INT              | No       | -                | XP amount (can be negative for corrections)|
| `source_type`   | ENUM             | No       | -                | `lesson`, `practice`, `bonus`, `achievement`, `challenge` |
| `source_id`     | CHAR(36)         | Yes      | NULL             | ID of the source (session, achievement, etc.)|
| `course_id`     | CHAR(36)         | Yes      | NULL             | FK → courses.id                            |
| `earned_at`     | DATETIME         | No       | CURRENT_TIMESTAMP| When XP was earned                         |

### `streaks`

User streak tracking.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id (UNIQUE)                     |
| `current_count` | INT UNSIGNED     | No       | 0                | Current streak day count                   |
| `longest_count` | INT UNSIGNED     | No       | 0                | All-time longest streak                    |
| `start_date`    | DATE             | Yes      | NULL             | Current streak start date                  |
| `last_activity_date`| DATE         | Yes      | NULL             | Last date with qualifying activity         |
| `freeze_count`  | TINYINT UNSIGNED | No       | 0                | Available streak freezes (max 2)           |
| `timezone`      | VARCHAR(50)      | No       | 'UTC'            | User's timezone for streak evaluation      |
| `updated_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Last modification                          |

### `leagues`

Weekly leaderboard league instances.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `tier`          | ENUM             | No       | -                | `bronze`...`diamond` (10 tiers)            |
| `week_start`    | DATE             | No       | -                | Monday of the league week                  |
| `week_end`      | DATE             | No       | -                | Sunday of the league week                  |
| `promotion_count`| INT UNSIGNED    | No       | 10               | Top N users promoted                       |
| `demotion_count`| INT UNSIGNED     | No       | 5                | Bottom N users demoted                     |
| `max_members`   | INT UNSIGNED     | No       | 30               | Maximum members in this group              |
| `status`        | ENUM             | No       | 'active'         | `active`, `completed`, `archived`          |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Creation timestamp                         |

### `league_memberships`

User membership in weekly league groups.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `league_id`     | CHAR(36)         | No       | -                | FK → leagues.id                            |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `weekly_xp`     | INT UNSIGNED     | No       | 0                | XP earned this week                        |
| `final_rank`    | INT UNSIGNED     | Yes      | NULL             | Final ranking (set at week end)            |
| `promoted`      | BOOLEAN          | Yes      | NULL             | Whether user was promoted                  |
| `demoted`       | BOOLEAN          | Yes      | NULL             | Whether user was demoted                   |
| `joined_at`     | DATETIME         | No       | CURRENT_TIMESTAMP| When user joined this league group         |

### `achievements`

Achievement definitions.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `name`          | VARCHAR(100)     | No       | -                | Achievement name                           |
| `description`   | TEXT             | No       | -                | Achievement description                    |
| `icon_url`      | VARCHAR(500)     | Yes      | NULL             | Icon CDN URL                               |
| `category`      | ENUM             | No       | -                | `streak`, `xp`, `lesson`, `social`, `profile`, `special` |
| `tier`          | ENUM             | Yes      | NULL             | `bronze`, `silver`, `gold`, `legendary`    |
| `criteria_json` | JSON             | No       | -                | Achievement criteria (JSON)                |
| `reward_gems`   | INT UNSIGNED     | No       | 0                | Gem reward on unlock                       |
| `is_active`     | BOOLEAN          | No       | TRUE             | Whether achievement is currently available |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Creation timestamp                         |

### `user_achievements`

User's earned achievements.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `achievement_id`| CHAR(36)         | No       | -                | FK → achievements.id                       |
| `earned_at`     | DATETIME         | No       | CURRENT_TIMESTAMP| When the achievement was earned             |
| `progress`      | DECIMAL(5,4)     | No       | 0.0000           | Progress toward achievement (0.0–1.0)      |

**Unique Constraint:** (`user_id`, `achievement_id`)

### `shop_items`

Shop item catalog.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `name`          | VARCHAR(100)     | No       | -                | Item name                                  |
| `description`   | TEXT             | Yes      | NULL             | Item description                           |
| `price_gems`    | INT UNSIGNED     | No       | -                | Price in gems                              |
| `max_ownable`   | INT UNSIGNED     | Yes      | NULL             | Max quantity ownable (null = unlimited)     |
| `category`      | ENUM             | No       | -                | `power_up`, `cosmetic`, `wager`, `boost`   |
| `icon_url`      | VARCHAR(500)     | Yes      | NULL             | Item icon CDN URL                          |
| `is_active`     | BOOLEAN          | No       | TRUE             | Whether item is currently available         |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Creation timestamp                         |

### `inventory`

User's owned items.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `item_id`       | CHAR(36)         | No       | -                | FK → shop_items.id                         |
| `quantity`      | INT UNSIGNED     | No       | 0                | Quantity owned                             |
| `updated_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Last modification                          |

**Unique Constraint:** (`user_id`, `item_id`)

### `purchases`

Purchase transaction history.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `item_id`       | CHAR(36)         | No       | -                | FK → shop_items.id                         |
| `quantity`      | INT UNSIGNED     | No       | 1                | Quantity purchased                         |
| `gems_spent`    | INT UNSIGNED     | No       | -                | Total gems spent                           |
| `purchased_at`  | DATETIME         | No       | CURRENT_TIMESTAMP| Purchase timestamp                         |

### `notifications`

In-app and push notification records.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `type`          | VARCHAR(50)      | No       | -                | Notification type (e.g., `streak_reminder`)|
| `title`         | VARCHAR(255)     | No       | -                | Notification title                         |
| `body`          | TEXT             | No       | -                | Notification body text                     |
| `is_read`       | BOOLEAN          | No       | FALSE            | Read status                                |
| `action_url`    | VARCHAR(500)     | Yes      | NULL             | Deep link URL                              |
| `image_url`     | VARCHAR(500)     | Yes      | NULL             | Notification image URL                     |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Creation timestamp                         |

### `notification_preferences`

User notification preference settings.

| Column                 | Type        | Nullable | Default | Description                        |
|------------------------|-------------|----------|---------|------------------------------------|
| `id`                   | CHAR(36)    | No       | UUID()  | Primary key                        |
| `user_id`              | CHAR(36)    | No       | -       | FK → users.id (UNIQUE)             |
| `push_enabled`         | BOOLEAN     | No       | TRUE    | Push notifications enabled         |
| `email_enabled`        | BOOLEAN     | No       | TRUE    | Email notifications enabled        |
| `streak_reminders`     | BOOLEAN     | No       | TRUE    | Streak reminder notifications      |
| `leaderboard_updates`  | BOOLEAN     | No       | TRUE    | Leaderboard change notifications   |
| `friend_activity`      | BOOLEAN     | No       | TRUE    | Friend activity notifications      |
| `promotions`           | BOOLEAN     | No       | FALSE   | Promotional notifications          |
| `reminder_time`        | TIME        | No       | '09:00' | Daily reminder time                |
| `quiet_hours_start`    | TIME        | Yes      | '22:00' | Quiet hours start                  |
| `quiet_hours_end`      | TIME        | Yes      | '07:00' | Quiet hours end                    |
| `updated_at`           | DATETIME    | No       | NOW()   | Last modification                  |

### `subscriptions`

Premium subscription records.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `plan_id`       | VARCHAR(50)      | No       | -                | Subscription plan identifier               |
| `status`        | ENUM             | No       | 'active'         | `trial`, `active`, `cancelled`, `expired`, `past_due` |
| `platform`      | ENUM             | No       | -                | `ios`, `android`, `web`, `gift`            |
| `started_at`    | DATETIME         | No       | -                | Subscription start time                    |
| `expires_at`    | DATETIME         | No       | -                | Subscription expiry time                   |
| `cancelled_at`  | DATETIME         | Yes      | NULL             | Cancellation time                          |
| `receipt_data`  | TEXT             | Yes      | NULL             | App Store / Play Store receipt             |
| `external_id`   | VARCHAR(255)     | Yes      | NULL             | External subscription ID (Stripe, etc.)    |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Record creation timestamp                  |

### `refresh_tokens`

JWT refresh token storage.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `token_hash`    | VARCHAR(255)     | No       | -                | SHA-256 hash of the refresh token          |
| `device_id`     | VARCHAR(100)     | Yes      | NULL             | Associated device identifier               |
| `expires_at`    | DATETIME         | No       | -                | Token expiry time                          |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Token creation time                        |
| `revoked_at`    | DATETIME         | Yes      | NULL             | Token revocation time (null = active)      |

### `word_bank`

Vocabulary words for all courses.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `word`          | VARCHAR(100)     | No       | -                | The word in target language                |
| `translation`   | VARCHAR(100)     | No       | -                | Translation in source language             |
| `language`      | VARCHAR(5)       | No       | -                | Target language code                       |
| `part_of_speech`| ENUM             | No       | -                | `noun`, `verb`, `adjective`, `adverb`, `preposition`, `conjunction`, `pronoun`, `other` |
| `difficulty`    | TINYINT UNSIGNED | No       | 1                | Difficulty level (1–5)                     |
| `audio_url`     | VARCHAR(500)     | Yes      | NULL             | Pronunciation audio URL                    |
| `course_id`     | CHAR(36)         | No       | -                | FK → courses.id                            |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Creation timestamp                         |

### `word_strength`

Spaced repetition tracking per user per word.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `word_id`       | CHAR(36)         | No       | -                | FK → word_bank.id                          |
| `strength`      | DECIMAL(3,2)     | No       | 1.00             | Current word strength (0.00–1.00)          |
| `last_seen`     | DATETIME         | No       | CURRENT_TIMESTAMP| Last time word was practiced               |
| `next_review`   | DATETIME         | No       | -                | Scheduled next review time (SM-2)          |
| `review_count`  | INT UNSIGNED     | No       | 0                | Total number of times reviewed             |
| `correct_count` | INT UNSIGNED     | No       | 0                | Number of correct answers                  |
| `ease_factor`   | DECIMAL(4,2)     | No       | 2.50             | SM-2 ease factor                           |
| `interval_days` | INT UNSIGNED     | No       | 1                | Current review interval in days            |

**Unique Constraint:** (`user_id`, `word_id`)

### `friendships`

Mutual friend relationships.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `user_id`       | CHAR(36)         | No       | -                | FK → users.id                              |
| `friend_id`     | CHAR(36)         | No       | -                | FK → users.id                              |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Friendship creation timestamp              |

**Unique Constraint:** (`user_id`, `friend_id`)

### `friend_requests`

Pending friend requests.

| Column          | Type             | Nullable | Default          | Description                                |
|-----------------|------------------|----------|------------------|--------------------------------------------|
| `id`            | CHAR(36)         | No       | UUID()           | Primary key                                |
| `sender_id`     | CHAR(36)         | No       | -                | FK → users.id                              |
| `receiver_id`   | CHAR(36)         | No       | -                | FK → users.id                              |
| `status`        | ENUM             | No       | 'pending'        | `pending`, `accepted`, `declined`          |
| `created_at`    | DATETIME         | No       | CURRENT_TIMESTAMP| Request creation timestamp                 |
| `responded_at`  | DATETIME         | Yes      | NULL             | Response timestamp                         |

---

## 5.3 Relationships

### Foreign Key Relationships

| Parent Table       | Child Table           | Foreign Key         | On Delete    | Cardinality  |
|--------------------|-----------------------|---------------------|--------------|--------------|
| `users`            | `enrollments`         | `user_id`           | CASCADE      | 1:N          |
| `courses`          | `enrollments`         | `course_id`         | RESTRICT     | 1:N          |
| `courses`          | `skills`              | `course_id`         | CASCADE      | 1:N          |
| `skills`           | `skill_prerequisites` | `skill_id`          | CASCADE      | 1:N          |
| `skills`           | `skill_prerequisites` | `prerequisite_id`   | CASCADE      | 1:N          |
| `skills`           | `lessons`             | `skill_id`          | CASCADE      | 1:N          |
| `lessons`          | `exercises`           | `lesson_id`         | CASCADE      | 1:N          |
| `users`            | `lesson_sessions`     | `user_id`           | CASCADE      | 1:N          |
| `lessons`          | `lesson_sessions`     | `lesson_id`         | RESTRICT     | 1:N          |
| `lesson_sessions`  | `session_answers`     | `session_id`        | CASCADE      | 1:N          |
| `exercises`        | `session_answers`     | `exercise_id`       | RESTRICT     | 1:N          |
| `users`            | `user_progress`       | `user_id`           | CASCADE      | 1:N          |
| `courses`          | `user_progress`       | `course_id`         | RESTRICT     | 1:N          |
| `users`            | `xp_history`          | `user_id`           | CASCADE      | 1:N          |
| `users`            | `streaks`             | `user_id`           | CASCADE      | 1:1          |
| `leagues`          | `league_memberships`  | `league_id`         | CASCADE      | 1:N          |
| `users`            | `league_memberships`  | `user_id`           | CASCADE      | 1:N          |
| `users`            | `user_achievements`   | `user_id`           | CASCADE      | 1:N          |
| `achievements`     | `user_achievements`   | `achievement_id`    | RESTRICT     | 1:N          |
| `users`            | `inventory`           | `user_id`           | CASCADE      | 1:N          |
| `shop_items`       | `inventory`           | `item_id`           | RESTRICT     | 1:N          |
| `users`            | `purchases`           | `user_id`           | CASCADE      | 1:N          |
| `users`            | `notifications`       | `user_id`           | CASCADE      | 1:N          |
| `users`            | `notification_preferences` | `user_id`      | CASCADE      | 1:1          |
| `users`            | `subscriptions`       | `user_id`           | CASCADE      | 1:N          |
| `users`            | `refresh_tokens`      | `user_id`           | CASCADE      | 1:N          |
| `users`            | `friendships`         | `user_id`           | CASCADE      | 1:N          |
| `users`            | `friendships`         | `friend_id`         | CASCADE      | 1:N          |
| `users`            | `word_strength`       | `user_id`           | CASCADE      | 1:N          |
| `word_bank`        | `word_strength`       | `word_id`           | RESTRICT     | 1:N          |
| `courses`          | `word_bank`           | `course_id`         | CASCADE      | 1:N          |

---

## 5.4 Indexing Strategy

### Primary Indexes

Every table has a primary key index on `id` (CHAR(36) UUID).

### Secondary Indexes

| Table                   | Index Name                    | Columns                              | Type     | Purpose                              |
|-------------------------|-------------------------------|--------------------------------------|----------|--------------------------------------|
| `users`                 | `idx_users_email`             | `email`                              | UNIQUE   | Login lookup, duplicate check        |
| `users`                 | `idx_users_display_name`      | `display_name`                       | INDEX    | User search                          |
| `users`                 | `idx_users_status`            | `status`                             | INDEX    | Filter active/suspended users        |
| `users`                 | `idx_users_premium_tier`      | `premium_tier`                       | INDEX    | Premium user queries                 |
| `enrollments`           | `idx_enroll_user_course`      | `user_id`, `course_id`              | UNIQUE   | Prevent duplicate enrollment         |
| `enrollments`           | `idx_enroll_user`             | `user_id`                            | INDEX    | User's courses lookup                |
| `skills`                | `idx_skills_course_order`     | `course_id`, `order_index`          | INDEX    | Skill tree ordering                  |
| `lessons`               | `idx_lessons_skill_order`     | `skill_id`, `order_index`           | INDEX    | Lesson ordering within skill         |
| `exercises`             | `idx_exercises_lesson_order`  | `lesson_id`, `order_index`          | INDEX    | Exercise ordering within lesson      |
| `lesson_sessions`       | `idx_sessions_user`           | `user_id`, `status`                 | INDEX    | Active session lookup                |
| `lesson_sessions`       | `idx_sessions_user_date`      | `user_id`, `started_at`            | INDEX    | Session history queries              |
| `session_answers`       | `idx_answers_session`         | `session_id`                         | INDEX    | Session answer lookup                |
| `user_progress`         | `idx_progress_user_course`    | `user_id`, `course_id`             | UNIQUE   | Progress per course                  |
| `xp_history`            | `idx_xp_user_date`            | `user_id`, `earned_at`             | INDEX    | XP history timeline                  |
| `xp_history`            | `idx_xp_course_date`          | `course_id`, `earned_at`           | INDEX    | Course XP analytics                  |
| `streaks`               | `idx_streaks_user`            | `user_id`                            | UNIQUE   | User streak lookup                   |
| `streaks`               | `idx_streaks_last_activity`   | `last_activity_date`                | INDEX    | Batch streak evaluation              |
| `league_memberships`    | `idx_league_user`             | `league_id`, `user_id`             | UNIQUE   | Prevent duplicate membership         |
| `league_memberships`    | `idx_league_xp`               | `league_id`, `weekly_xp` DESC      | INDEX    | Leaderboard ranking queries          |
| `user_achievements`     | `idx_achievement_user`        | `user_id`, `achievement_id`        | UNIQUE   | Prevent duplicate achievement        |
| `inventory`             | `idx_inventory_user_item`     | `user_id`, `item_id`               | UNIQUE   | Inventory lookup                     |
| `notifications`         | `idx_notif_user_created`      | `user_id`, `created_at` DESC       | INDEX    | Notification feed                    |
| `notifications`         | `idx_notif_user_unread`       | `user_id`, `is_read`               | INDEX    | Unread count                         |
| `refresh_tokens`        | `idx_refresh_token_hash`      | `token_hash`                         | UNIQUE   | Token lookup                         |
| `refresh_tokens`        | `idx_refresh_user`            | `user_id`                            | INDEX    | User's tokens                        |
| `subscriptions`         | `idx_sub_user_status`         | `user_id`, `status`                 | INDEX    | Active subscription check            |
| `word_strength`         | `idx_ws_user_word`            | `user_id`, `word_id`               | UNIQUE   | Word strength lookup                 |
| `word_strength`         | `idx_ws_user_next_review`     | `user_id`, `next_review`           | INDEX    | Spaced repetition queue              |
| `friendships`           | `idx_friend_user`             | `user_id`, `friend_id`             | UNIQUE   | Friendship check                     |
| `friend_requests`       | `idx_freq_receiver_status`    | `receiver_id`, `status`             | INDEX    | Pending request inbox                |

---

## 5.5 Data Retention Rules

| Data Category           | Retention Period  | Action After Retention              |
|-------------------------|-------------------|-------------------------------------|
| Active user data        | Indefinite        | Retained while account active       |
| Soft-deleted accounts   | 30 days           | Hard delete after recovery period   |
| Session answers         | 1 year            | Aggregated, raw data purged         |
| XP history              | 2 years           | Aggregated into monthly summaries   |
| Notifications           | 90 days           | Deleted                             |
| Expired refresh tokens  | 7 days            | Hard deleted                        |
| Leaderboard history     | 1 year            | Archived to cold storage            |
| Analytics events        | 6 months          | Aggregated, raw data purged         |
| Audit logs              | 3 years           | Archived to cold storage            |
| Password reset tokens   | 1 hour            | Hard deleted on expiry              |
| Abandoned sessions      | 7 days            | Status changed to `abandoned`       |

### Data Purge Job

A daily `DataRetentionJob` runs at 03:00 UTC:

```sql
-- Purge expired refresh tokens
DELETE FROM refresh_tokens
WHERE expires_at < DATE_SUB(NOW(), INTERVAL 7 DAY)
   OR revoked_at < DATE_SUB(NOW(), INTERVAL 7 DAY);

-- Purge old notifications
DELETE FROM notifications
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- Hard delete accounts past recovery window
DELETE FROM users
WHERE status = 'deleted'
  AND deleted_at < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- Archive old session data
INSERT INTO session_answers_archive
SELECT * FROM session_answers
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);

DELETE FROM session_answers
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

---

## 5.6 Migration Strategy

### Migration Tool

Entity Framework Core Migrations managed via CLI:

```bash
# Create a new migration
dotnet ef migrations add AddWordStrengthTable

# Apply migrations
dotnet ef database update

# Generate SQL script for review
dotnet ef migrations script --output migration.sql
```

### Migration Rules

1. **Never drop columns in production** — add new columns, deprecate old ones
2. **All migrations must be backward-compatible** — old code must work with new schema
3. **Large table migrations use online schema change** (e.g., `pt-online-schema-change`)
4. **All migrations are reviewed by 2 engineers** before applying to production
5. **Rollback scripts** must be prepared for every migration
6. **Data migrations** are separate from schema migrations
7. **Index additions** are performed as non-blocking operations

### Schema Version Tracking

```sql
-- EF Core maintains __EFMigrationsHistory
CREATE TABLE `__EFMigrationsHistory` (
    `MigrationId` VARCHAR(150) NOT NULL PRIMARY KEY,
    `ProductVersion` VARCHAR(32) NOT NULL
);
```

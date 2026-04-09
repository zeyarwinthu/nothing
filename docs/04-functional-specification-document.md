# 4. Functional Specification Document (FSD)

## 4.1 Features & User Flows

### Feature Map

| Feature Area        | Features                                                                   |
|---------------------|----------------------------------------------------------------------------|
| Authentication      | Register, Login, OAuth, Password Reset, Logout, Device Management          |
| Onboarding          | Language Selection, Proficiency Test, Daily Goal Setting, First Lesson      |
| Learning            | Skill Tree, Lessons, Practice, Timed Challenges, Stories                   |
| Exercises           | Translate, Multiple Choice, Listening, Speaking, Fill-in-Blank, Matching   |
| Progression         | XP, Crowns, Levels, Skill Strength                                         |
| Gamification        | Streaks, Hearts, Gems, Achievements, Leaderboards                          |
| Social              | Friends, Follow, Activity Feed, Classroom                                  |
| Shop                | Streak Freeze, Heart Refill, Power-ups, Outfits                            |
| Premium             | Super Duolingo, Family Plan, Ad-free, Unlimited Hearts                     |
| Settings            | Daily Goal, Notifications, Sound, Privacy, Language                        |
| Admin               | User Management, Content Management, Analytics Dashboard                   |

### User Flow 1: New User Onboarding

```
┌─────────────┐    ┌────────────┐    ┌──────────────┐    ┌──────────┐
│ Landing Page│───►│ Select     │───►│ Why are you  │───►│ Select   │
│ / App Open  │    │ Language   │    │ learning?    │    │ Daily    │
└─────────────┘    └────────────┘    └──────────────┘    │ Goal     │
                                                          └────┬─────┘
                                                               │
                   ┌────────────┐    ┌──────────────┐    ┌─────▼─────┐
                   │ Complete!  │◄───│ First Lesson │◄───│ Placement │
                   │ Dashboard  │    │ (Guided)     │    │ Test?     │
                   └────────────┘    └──────────────┘    └───────────┘
```

**Steps:**
1. User opens the app or lands on the website
2. Selects the language they want to learn
3. Optionally answers "Why are you learning?" (personalization)
4. Chooses daily practice goal (5, 10, 15, or 20 minutes)
5. Takes optional placement test or starts from Basics 1
6. Completes first guided lesson with tutorials
7. Prompted to create account (or continues as guest with limited features)
8. Lands on the main dashboard with skill tree visible

### User Flow 2: Daily Learning Session

```
┌──────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
│ Open App │───►│Dashboard │───►│ Select     │───►│ Start    │
│          │    │ (Streak, │    │ Skill/     │    │ Lesson   │
│          │    │  Goal)   │    │ Practice   │    │          │
└──────────┘    └──────────┘    └────────────┘    └────┬─────┘
                                                       │
┌──────────┐    ┌──────────┐    ┌────────────┐    ┌────▼─────┐
│ Summary  │◄───│ Streak + │◄───│ XP Earned │◄───│ Complete │
│ + XP Bar │    │ Achieve. │    │ Animation │    │ Exercises│
└──────────┘    └──────────┘    └────────────┘    └──────────┘
```

**Steps:**
1. User opens the app
2. Dashboard shows current streak, daily goal progress, and skill tree
3. User selects a skill or taps "Practice" for spaced repetition review
4. Lesson begins with a series of 6–20 exercises
5. Each exercise provides immediate feedback (correct/incorrect)
6. Incorrect answers cost hearts (free tier) or show corrections (premium)
7. Upon completion, XP is awarded with animations
8. Streak is updated, achievements checked, leaderboard position recalculated
9. Daily goal progress bar updates

### User Flow 3: Streak Management

```
                              ┌────────────────┐
                              │ User completes │
                              │ at least 1     │
                              │ lesson today   │
                              └───────┬────────┘
                                      │
                              ┌───────▼────────┐
                         ┌────│ Has activity   │────┐
                         │Yes │ today?         │ No │
                         │    └────────────────┘    │
                         │                          │
                  ┌──────▼──────┐           ┌───────▼───────┐
                  │ Streak +1   │           │ Check streak  │
                  │ Continue    │           │ freeze        │
                  └─────────────┘           └───────┬───────┘
                                                    │
                                            ┌───────▼───────┐
                                       ┌────│ Has freeze?   │────┐
                                       │Yes │               │ No │
                                       │    └───────────────┘    │
                                       │                         │
                                ┌──────▼──────┐          ┌──────▼──────┐
                                │ Apply freeze│          │ Streak = 0  │
                                │ Streak kept │          │ Notify user │
                                └─────────────┘          └─────────────┘
```

### User Flow 4: Shop Purchase

```
┌──────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
│ Open     │───►│ Browse   │───►│ Select     │───►│ Confirm  │
│ Shop     │    │ Items    │    │ Item       │    │ Purchase │
└──────────┘    └──────────┘    └────────────┘    └────┬─────┘
                                                       │
                                ┌────────────┐    ┌────▼─────┐
                                │ Item Added │◄───│ Deduct   │
                                │ to Inventory│   │ Gems     │
                                └────────────┘    └──────────┘
```

### User Flow 5: Leaderboard Interaction

```
┌──────────┐    ┌──────────┐    ┌────────────┐
│ View     │───►│ See      │───►│ Tap user   │
│ League   │    │ Rankings │    │ profile    │
└──────────┘    └──────────┘    └────────────┘

End of Week:
┌─────────────┐    ┌──────────┐    ┌────────────┐
│ Weekly      │───►│ Top 10:  │───►│ Promoted   │
│ Reset       │    │ Promote  │    │ to next    │
│ (Monday)    │    │ Bottom 5:│    │ league     │
└─────────────┘    │ Demote   │    └────────────┘
                   └──────────┘
```

---

## 4.2 Business Rules

### Authentication Rules

| Rule ID | Rule                                                                     |
|---------|--------------------------------------------------------------------------|
| AUTH-01 | Users must be at least 13 years old to register (COPPA compliance)        |
| AUTH-02 | Passwords must contain ≥ 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special |
| AUTH-03 | After 5 failed login attempts, account is locked for 15 minutes           |
| AUTH-04 | Refresh tokens are rotated on each use (old token invalidated)            |
| AUTH-05 | Password reset links expire after 1 hour                                  |
| AUTH-06 | OAuth accounts can set a password later to enable email/password login     |

### Learning Rules

| Rule ID  | Rule                                                                    |
|----------|-------------------------------------------------------------------------|
| LEARN-01 | Each lesson contains 6–20 exercises depending on skill difficulty       |
| LEARN-02 | Free tier users have 5 hearts; each wrong answer costs 1 heart          |
| LEARN-03 | Hearts regenerate 1 every 4 hours (max 5)                               |
| LEARN-04 | Premium users have unlimited hearts                                      |
| LEARN-05 | A lesson is passed if the user completes all exercises                   |
| LEARN-06 | Failed exercises may be repeated within the same session                 |
| LEARN-07 | Typos are tolerated if the Levenshtein distance is ≤ 1 and meaning unchanged |
| LEARN-08 | Accents and capitalization are generally not required for correctness     |
| LEARN-09 | Multiple valid translations are accepted for each exercise               |
| LEARN-10 | Practice sessions use spaced repetition to target weak words             |
| LEARN-11 | Skills must be completed in order (prerequisites enforced)               |
| LEARN-12 | New exercise types are introduced gradually as user progresses           |

### Gamification Rules

| Rule ID  | Rule                                                                    |
|----------|-------------------------------------------------------------------------|
| GAM-01   | Base XP for completing a lesson: 10 XP                                  |
| GAM-02   | Bonus XP for perfect lesson (no mistakes): +5 XP                        |
| GAM-03   | Combo bonus: consecutive correct answers increase XP multiplier          |
| GAM-04   | Daily XP bonus for first lesson: +5 XP                                  |
| GAM-05   | Streak counts only if user completes ≥ 1 lesson per calendar day (user TZ) |
| GAM-06   | Streak freeze protects streak for 1 missed day; max 2 owned             |
| GAM-07   | Streak freezes are consumed automatically at EOD evaluation              |
| GAM-08   | Leaderboard groups contain 30 users of similar activity level            |
| GAM-09   | Top 10 in a league are promoted; bottom 5 are demoted                    |
| GAM-10   | Leagues (ascending): Bronze, Silver, Gold, Sapphire, Ruby, Emerald, Amethyst, Pearl, Obsidian, Diamond |
| GAM-11   | Gems are earned through lessons (2/lesson), achievements, and milestones |
| GAM-12   | XP doublers (from shop) last for 15 minutes from activation             |

### Subscription Rules

| Rule ID  | Rule                                                                    |
|----------|-------------------------------------------------------------------------|
| SUB-01   | Free trial lasts 14 days for new users                                   |
| SUB-02   | Premium benefits apply immediately upon subscription                     |
| SUB-03   | Cancellation takes effect at the end of the billing period               |
| SUB-04   | Family plan supports up to 6 members                                     |
| SUB-05   | Family members must be invited by the plan owner                         |
| SUB-06   | Family members retain data if removed but lose premium features          |
| SUB-07   | Subscription status is verified via App Store / Play Store receipts      |

---

## 4.3 Acceptance Criteria

### AC-001: User Registration

```gherkin
Feature: User Registration

Scenario: Successful registration with email
  Given a new user with valid email and password
  When they submit the registration form
  Then an account is created
  And a verification email is sent
  And a JWT access token is returned
  And the user is enrolled in their chosen course

Scenario: Registration with existing email
  Given an email that already exists in the system
  When a new user tries to register with that email
  Then a 409 DUPLICATE_EMAIL error is returned
  And no duplicate account is created

Scenario: Registration with weak password
  Given a password that does not meet complexity requirements
  When the user submits registration
  Then a 400 VALIDATION_ERROR is returned
  And the specific password requirements are listed

Scenario: Underage registration
  Given a user who enters age < 13
  When they submit the registration form
  Then a 403 error is returned with COPPA compliance message
  And no account is created
```

### AC-002: Lesson Completion

```gherkin
Feature: Lesson Completion

Scenario: Complete lesson with all correct answers
  Given a user starts a lesson with 10 exercises
  When they answer all 10 correctly
  Then the lesson is marked as completed
  And 15 XP is awarded (10 base + 5 perfect bonus)
  And their streak is extended
  And crown progress is updated

Scenario: Complete lesson with mistakes (free tier)
  Given a free tier user starts a lesson with 5 hearts
  When they answer 2 exercises incorrectly
  Then their hearts decrease from 5 to 3
  And 10 XP is awarded (base only, no bonus)
  And the lesson is still completed

Scenario: Run out of hearts
  Given a free tier user with 1 heart remaining
  When they answer an exercise incorrectly
  Then their hearts reach 0
  And the lesson session ends
  And they are prompted to wait, buy hearts, or upgrade

Scenario: Premium user makes mistakes
  Given a premium user starts a lesson
  When they answer exercises incorrectly
  Then no hearts are deducted
  And they can continue the lesson indefinitely
```

### AC-003: Streak System

```gherkin
Feature: Streak Management

Scenario: Extend streak with daily activity
  Given a user with a 15-day streak
  When they complete at least 1 lesson today
  Then their streak increases to 16

Scenario: Streak broken without freeze
  Given a user with a 15-day streak and 0 streak freezes
  When they do not complete any lesson by EOD (user timezone)
  Then their streak resets to 0
  And a "streak_lost" notification is sent

Scenario: Streak protected by freeze
  Given a user with a 15-day streak and 1 streak freeze
  When they do not complete any lesson by EOD
  Then the streak freeze is consumed
  And their streak remains at 15
  And a "streak_frozen" notification is sent

Scenario: Streak milestone reward
  Given a user reaches a 30-day streak
  Then they receive 50 gems as a milestone reward
  And an achievement is unlocked
```

### AC-004: Leaderboard

```gherkin
Feature: Weekly Leaderboard

Scenario: User earns XP and ranking updates
  Given a user in the Gold league with 200 XP this week
  When they earn 20 more XP
  Then their weekly XP updates to 220
  And their leaderboard ranking is recalculated

Scenario: Weekly promotion
  Given a user finishes in the top 10 of Gold league
  When the weekly reset occurs on Monday
  Then they are promoted to Sapphire league
  And they receive a "leaderboard_promotion" notification

Scenario: Weekly demotion
  Given a user finishes in the bottom 5 of Gold league
  When the weekly reset occurs on Monday
  Then they are demoted to Silver league
  And they receive a "leaderboard_demotion" notification
```

### AC-005: Shop Purchase

```gherkin
Feature: Shop Purchase

Scenario: Successful gem purchase
  Given a user with 300 gems
  When they purchase a Streak Freeze for 200 gems
  Then 200 gems are deducted
  And the user has 100 gems remaining
  And the Streak Freeze is added to their inventory

Scenario: Insufficient gems
  Given a user with 100 gems
  When they try to purchase a Streak Freeze for 200 gems
  Then a 422 INSUFFICIENT_GEMS error is returned
  And no gems are deducted

Scenario: Maximum inventory reached
  Given a user with 2 Streak Freezes (max)
  When they try to purchase another
  Then a 422 MAX_ITEMS_OWNED error is returned
```

---

## 4.4 Edge Cases

### Authentication Edge Cases

| Edge Case                                    | Expected Behavior                                          |
|----------------------------------------------|------------------------------------------------------------|
| User registers, doesn't verify email         | Account created but limited; reminder email after 24h      |
| Simultaneous login from 2 devices            | Both sessions valid; each gets own token pair               |
| Token refresh during active lesson           | Lesson continues; token refreshed transparently             |
| OAuth provider returns different email        | Link accounts if same user; create new account otherwise    |
| Password reset while logged in               | All existing sessions are invalidated                       |
| Account deleted, then tries to register again | Within 30 days: option to restore; after: fresh account    |

### Learning Edge Cases

| Edge Case                                    | Expected Behavior                                          |
|----------------------------------------------|------------------------------------------------------------|
| App closed during lesson                     | Session saved; user can resume within 30 min               |
| Network loss during answer submission        | Client queues answer; retries on reconnect                 |
| Two devices submit answers for same session  | First answer accepted; second gets SESSION_CONFLICT error  |
| User finishes all lessons in a course        | "Course Complete" badge awarded; practice mode unlocked    |
| Lesson content updated while user mid-lesson | Current session uses old content; new content on next start|
| User submits answer after session timeout    | 410 SESSION_EXPIRED error; must restart lesson             |

### Gamification Edge Cases

| Edge Case                                    | Expected Behavior                                          |
|----------------------------------------------|------------------------------------------------------------|
| User changes timezone                        | Streak evaluated on new timezone starting next day         |
| Streak freeze used + user completes lesson   | Freeze not consumed (activity detected before EOD eval)    |
| User in top 10 AND bottom 5 (tiny league)    | Promotion takes priority                                    |
| Two users tied for last promotion slot       | Both promoted (generous policy)                             |
| XP earned at exactly midnight                | Attributed to the day based on user's timezone              |
| User's timezone observes DST change          | Streak evaluator handles DST; no double/missed days        |
| Gem balance goes negative (race condition)   | Transaction fails; operation rolled back                    |

### System Edge Cases

| Edge Case                                    | Expected Behavior                                          |
|----------------------------------------------|------------------------------------------------------------|
| RabbitMQ down                                | Events buffered in memory; retried when connection restores|
| Redis down                                   | Fallback to direct MySQL reads; higher latency accepted    |
| MySQL primary failover                       | Automatic failover to replica; ~30 second write interruption|
| CDN cache stale                              | Serve stale content; background refresh                     |
| Deployment during peak hours                 | Rolling deployment ensures zero-downtime                    |
| Background job takes longer than expected    | Job timeout at 2x expected duration; alert triggered        |

---

## 4.5 User Stories

### Epic: User Onboarding

| Story ID | As a...    | I want to...                              | So that...                                    | Priority |
|----------|------------|-------------------------------------------|-----------------------------------------------|----------|
| US-001   | New user   | Sign up with my email and password        | I can start learning a language               | P0       |
| US-002   | New user   | Sign up with Google/Apple/Facebook        | I can register quickly without a new password | P0       |
| US-003   | New user   | Choose my target language                 | I learn the language I'm interested in        | P0       |
| US-004   | New user   | Take a placement test                     | I start at the right difficulty level          | P1       |
| US-005   | New user   | Set my daily learning goal                | I have a realistic practice schedule           | P1       |

### Epic: Core Learning

| Story ID | As a...    | I want to...                              | So that...                                    | Priority |
|----------|------------|-------------------------------------------|-----------------------------------------------|----------|
| US-010   | Learner    | See my skill tree                         | I know what topics to study next              | P0       |
| US-011   | Learner    | Start a lesson                            | I can learn new vocabulary and grammar         | P0       |
| US-012   | Learner    | Get immediate feedback on my answers      | I learn from my mistakes right away           | P0       |
| US-013   | Learner    | Practice previously learned skills        | I reinforce my knowledge with spaced repetition| P0       |
| US-014   | Learner    | See hints during exercises                | I can figure out the answer when stuck        | P1       |
| US-015   | Learner    | Complete speaking exercises               | I practice pronunciation                       | P1       |
| US-016   | Learner    | Learn through different exercise types    | I engage with the material in varied ways      | P1       |
| US-017   | Learner    | Resume a lesson I left partway            | I don't lose my progress                       | P1       |

### Epic: Gamification & Motivation

| Story ID | As a...    | I want to...                              | So that...                                    | Priority |
|----------|------------|-------------------------------------------|-----------------------------------------------|----------|
| US-020   | Learner    | See my daily streak count                 | I'm motivated to practice every day           | P0       |
| US-021   | Learner    | Earn XP for completing lessons            | I feel a sense of progression                  | P0       |
| US-022   | Learner    | Compete on weekly leaderboards            | I'm motivated by friendly competition          | P0       |
| US-023   | Learner    | Earn achievements and badges              | I'm rewarded for milestones                    | P1       |
| US-024   | Learner    | Use streak freezes                        | My streak is protected when I'm busy           | P1       |
| US-025   | Learner    | See my level and progress bar             | I know how close I am to the next level        | P1       |

### Epic: Social Features

| Story ID | As a...    | I want to...                              | So that...                                    | Priority |
|----------|------------|-------------------------------------------|-----------------------------------------------|----------|
| US-030   | Learner    | Add friends                               | I can see their progress and compete           | P1       |
| US-031   | Learner    | See my friends' activity                  | I'm motivated by their progress                | P1       |
| US-032   | Learner    | Share my achievements                     | I can celebrate milestones with friends         | P2       |

### Epic: Premium & Monetization

| Story ID | As a...    | I want to...                              | So that...                                    | Priority |
|----------|------------|-------------------------------------------|-----------------------------------------------|----------|
| US-040   | Free user  | See the benefits of premium               | I can make an informed upgrade decision        | P0       |
| US-041   | Free user  | Purchase a premium subscription           | I get unlimited hearts and no ads              | P0       |
| US-042   | Premium    | Have unlimited hearts                     | I can practice without interruption             | P0       |
| US-043   | Premium    | Use the app without ads                   | I have an uninterrupted learning experience    | P0       |
| US-044   | Premium    | Start a family plan                       | My family members can learn too                | P2       |

### Epic: Settings & Account

| Story ID | As a...    | I want to...                              | So that...                                    | Priority |
|----------|------------|-------------------------------------------|-----------------------------------------------|----------|
| US-050   | User       | Update my profile and avatar              | I personalize my account                       | P1       |
| US-051   | User       | Configure notification preferences        | I only get notifications I want               | P1       |
| US-052   | User       | Change my daily goal                      | I can adjust based on my schedule              | P1       |
| US-053   | User       | Delete my account                         | My data is removed per my request              | P1       |
| US-054   | User       | Export my data                            | I comply with GDPR and have my data            | P2       |

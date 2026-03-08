# 1. Mobile App Flow Documentation

> Complete flow-by-flow documentation of every user journey in the Duolingo-style learning platform.

---

## 1.1 Onboarding Flow

### Overview

The onboarding flow is the first experience a new user encounters. It is designed to be frictionless, engaging, and informative — collecting the minimum data needed to personalize the learning experience while building excitement.

### Flow Diagram

```
App Launch (first time)
  → Welcome Screen
    → Language Selection
      → Learning Motivation
        → Daily Goal Selection
          → Experience Level
            → [Optional] Placement Test Prompt
              → Account Creation Prompt
                → Home Screen
```

### Step-by-Step

#### 1.1.1 Welcome Screen

| Property | Detail |
|----------|--------|
| Screen Name | `WelcomeScreen` |
| Trigger | App launched for the first time (no stored auth token) |
| Layout | Full-screen illustration with animated mascot, tagline ("Learn a language for free, forever"), and single CTA |
| Primary CTA | "Get Started" button (full-width, green, 56dp height) |
| Secondary CTA | "I Already Have an Account" text link |
| Animation | Mascot character (owl) enters with a spring animation (300ms, cubic-bezier 0.34, 1.56, 0.64, 1) |
| Analytics Event | `onboarding_welcome_viewed` |

#### 1.1.2 Language Selection

| Property | Detail |
|----------|--------|
| Screen Name | `LanguageSelectionScreen` |
| Trigger | User taps "Get Started" |
| Layout | Scrollable grid (2 columns) of language cards, each showing flag icon + language name |
| Data Source | Static asset list of 40+ supported languages bundled in-app |
| Selection Behavior | Single-select; tapping a card highlights it with a green border (2dp) and checkmark overlay |
| Primary CTA | "Continue" button (disabled until selection made) |
| Back Navigation | System back / top-left back arrow → returns to Welcome Screen |
| Analytics Event | `onboarding_language_selected { language: string }` |

**Supported Languages (initial set):**
Spanish, French, German, Japanese, Korean, Chinese (Mandarin), Italian, Portuguese, Russian, Hindi, Arabic, Turkish, Dutch, Swedish, Polish, Norwegian, Danish, Irish, Welsh, Greek, Hebrew, Vietnamese, Indonesian, Thai, Czech, Romanian, Hungarian, Ukrainian, Finnish, Swahili, Navajo, Hawaiian, Latin, Esperanto, High Valyrian, Klingon, Catalan, Guarani, Yiddish, Scottish Gaelic.

#### 1.1.3 Learning Motivation

| Property | Detail |
|----------|--------|
| Screen Name | `MotivationScreen` |
| Trigger | User taps "Continue" from Language Selection |
| Layout | List of motivation options with icon + label |
| Options | "Travel", "Career", "School", "Brain Training", "Culture", "Family & Friends", "Other" |
| Selection Behavior | Single-select with radio-button style selection |
| Primary CTA | "Continue" |
| Analytics Event | `onboarding_motivation_selected { motivation: string }` |

#### 1.1.4 Daily Goal Selection

| Property | Detail |
|----------|--------|
| Screen Name | `DailyGoalScreen` |
| Trigger | User taps "Continue" from Motivation |
| Layout | Four vertically stacked cards with goal level |
| Options | Casual (5 min/day, 10 XP), Regular (10 min/day, 20 XP), Serious (15 min/day, 30 XP), Intense (20 min/day, 50 XP) |
| Default Selection | "Regular" is pre-selected |
| Card Design | Each card shows emoji icon, goal name, time commitment, and XP target |
| Primary CTA | "Continue" |
| Analytics Event | `onboarding_goal_selected { goal: string, xp_target: int }` |

#### 1.1.5 Experience Level

| Property | Detail |
|----------|--------|
| Screen Name | `ExperienceLevelScreen` |
| Trigger | User taps "Continue" from Daily Goal |
| Layout | Three large cards stacked vertically |
| Options | "I'm New" (starts at Skill 1, Level 1), "I Know Some" (triggers Placement Test), "I'm Advanced" (triggers Placement Test) |
| Primary CTA | Card tap navigates directly |
| Analytics Event | `onboarding_experience_selected { level: string }` |

#### 1.1.6 Placement Test Prompt (Conditional)

| Property | Detail |
|----------|--------|
| Screen Name | `PlacementTestPromptScreen` |
| Trigger | User selected "I Know Some" or "I'm Advanced" |
| Layout | Informational card explaining the placement test (5 minutes, ~15 questions), with mascot encouragement |
| Primary CTA | "Start Placement Test" → navigates to Placement Test Flow (§1.3) |
| Secondary CTA | "Skip" → starts at Skill 1 |
| Analytics Event | `onboarding_placement_prompt_viewed` |

#### 1.1.7 Account Creation Prompt

| Property | Detail |
|----------|--------|
| Screen Name | `AccountPromptScreen` |
| Trigger | Completion of Experience Level selection or Placement Test |
| Layout | "Create a profile to save your progress" message, with mascot holding a "save" icon |
| Primary CTA | "Create Profile" → navigates to Signup Flow (§1.2) |
| Secondary CTA | "Later" → proceeds to Home Screen with anonymous session (stored locally, 7-day expiration warning) |
| Anonymous Session | Progress stored in local DB; periodic prompts to create account (after lesson 3, lesson 7, first streak milestone) |
| Analytics Event | `onboarding_account_prompt_response { action: "create" | "skip" }` |

### Onboarding State Persistence

- Onboarding progress is stored locally using `SharedPreferences` key `onboarding_step` (int 0–7).
- If the app is killed mid-onboarding, the user resumes at the last completed step.
- Completed onboarding sets `onboarding_complete = true`; subsequent launches skip onboarding.

---

## 1.2 Login & Signup

### Overview

The authentication flow supports email/password, Google Sign-In, Apple Sign-In, and Facebook Login. It includes account creation, login, and password recovery sub-flows.

### Flow Diagram

```
Auth Entry Point
  ├── Sign Up
  │     ├── Email + Password
  │     ├── Google Sign-In
  │     ├── Apple Sign-In
  │     └── Facebook Login
  ├── Log In
  │     ├── Email + Password
  │     ├── Google Sign-In
  │     ├── Apple Sign-In
  │     └── Facebook Login
  └── Forgot Password
        → Email Input
          → Reset Email Sent Confirmation
            → New Password Entry (via deep link)
```

### 1.2.1 Signup Screen

| Property | Detail |
|----------|--------|
| Screen Name | `SignupScreen` |
| Layout | Form with name, email, password fields; social auth buttons; terms checkbox |
| Validations | Name: 2–50 chars, no special chars. Email: RFC 5322 format. Password: 8+ chars, 1 uppercase, 1 number, 1 special char |
| Real-time Validation | Each field validates on blur and shows inline error below the field |
| Password Strength Indicator | Visual bar (red → yellow → green) below password field |
| Social Auth | Google, Apple (iOS only), Facebook — each triggers platform OAuth flow |
| Primary CTA | "Create Account" — disabled until all validations pass |
| Loading State | Button shows spinner; all fields disabled during API call |
| Success | API returns JWT + refresh token → stored in secure storage → navigate to Home |
| Error States | "Email already exists" → show inline error with "Log in instead" link. Network error → show snackbar with retry. Server error → show generic error dialog |
| Analytics Events | `signup_started { method: string }`, `signup_completed { method: string }`, `signup_failed { method: string, error: string }` |

### 1.2.2 Login Screen

| Property | Detail |
|----------|--------|
| Screen Name | `LoginScreen` |
| Layout | Email + password fields; social auth buttons; "Forgot Password?" link; "Sign Up" link |
| Validations | Email: non-empty, valid format. Password: non-empty |
| Primary CTA | "Log In" |
| Error States | "Invalid credentials" → shake animation on form + inline error. Account locked → show dialog with support link. Network error → snackbar with retry |
| Biometric Login | If biometrics enabled in settings and device supports it, show fingerprint/Face ID button |
| Analytics Events | `login_started { method: string }`, `login_completed { method: string }`, `login_failed { method: string, error: string }` |

### 1.2.3 Forgot Password Flow

| Property | Detail |
|----------|--------|
| Screen Name | `ForgotPasswordScreen` |
| Layout | Single email input field with instruction text |
| Primary CTA | "Send Reset Link" |
| Success State | Show confirmation screen with email icon animation + "Check your email" message |
| Deep Link | Email contains link `https://app.example.com/reset-password?token={token}` → opens `ResetPasswordScreen` |
| Reset Password Screen | Two password fields (new + confirm), same validation as signup |
| Token Expiry | 1 hour; expired token shows "Link expired" screen with "Resend" option |
| Analytics Events | `password_reset_requested`, `password_reset_completed`, `password_reset_failed { error: string }` |

### 1.2.4 Token Management

| Property | Detail |
|----------|--------|
| Access Token | JWT, 15-minute expiry, stored in `FlutterSecureStorage` |
| Refresh Token | Opaque token, 30-day expiry, stored in `FlutterSecureStorage` |
| Token Refresh | Automatic via HTTP interceptor when 401 received; queues concurrent requests |
| Logout | Clears all tokens, resets local user state, navigates to Welcome Screen |
| Session Expiry | If refresh token expired, show "Session expired" dialog → navigate to Login |

---

## 1.3 Placement Test Flow

### Overview

The placement test adaptively determines the user's proficiency level and unlocks appropriate skills on the skill tree. It consists of 15–25 questions of increasing difficulty, ending when the algorithm has enough confidence in the user's level.

### Flow Diagram

```
Placement Test Prompt
  → Placement Test Instructions
    → Question 1 (easy)
      → Question 2 (adjusted difficulty)
        → ... (adaptive loop)
          → Results Screen
            → Skill Tree (with unlocked skills)
```

### 1.3.1 Test Instructions Screen

| Property | Detail |
|----------|--------|
| Screen Name | `PlacementTestInstructionsScreen` |
| Layout | Mascot with speech bubble, bullet-point list of instructions |
| Instructions | "Answer as many as you can", "Don't worry about mistakes", "It gets harder as you go", "Takes about 5 minutes" |
| Primary CTA | "Start Test" |
| No Back Navigation | Back button hidden; "Skip Test" link at bottom |

### 1.3.2 Question Screen (During Test)

| Property | Detail |
|----------|--------|
| Screen Name | `PlacementTestQuestionScreen` |
| Layout | Progress bar at top (percentage-based, not question-count), question prompt, answer area |
| Question Types | Translation (L2→L1), multiple choice, fill-in-the-blank |
| Timer | No visible timer, but server records response time per question |
| Answer Submission | Immediate feedback suppressed — answer recorded silently, advance to next |
| No Lives System | Mistakes don't cost lives; they affect placement level only |
| Skip Option | "I don't know" button at bottom — treated as incorrect, moves to next question |
| Adaptive Logic | Server-side IRT (Item Response Theory); difficulty adjusts based on previous answers |
| Exit Confirmation | If user tries to exit: "Are you sure? Your progress will be lost." dialog |

### 1.3.3 Results Screen

| Property | Detail |
|----------|--------|
| Screen Name | `PlacementTestResultsScreen` |
| Layout | Animated results reveal: level badge (A1–C2 CEFR equivalent), number of skills unlocked, XP earned |
| Animation | Badge scales up with particle burst, skill count animates incrementally |
| Data | `{ level: int (1-6), skills_unlocked: int, xp_earned: int }` |
| Primary CTA | "Continue to Course" → Home Screen with skills unlocked |
| Analytics Events | `placement_test_completed { level: int, questions_answered: int, duration_seconds: int }` |

---

## 1.4 Home Screen Flow

### Overview

The home screen is the central hub of the application. It shows the user's current course progress, daily goal status, active streak, and provides access to all major features. The layout is vertically scrollable with the skill tree as the primary content area.

### Screen Layout (Top to Bottom)

```
┌─────────────────────────────────┐
│  [Flag] Spanish     [Streak🔥7] │  ← Top Bar
│  [Gems💎 350]     [Hearts❤️ 5]  │
├─────────────────────────────────┤
│  Daily Goal: ████████░░  16/20  │  ← Progress Banner
├─────────────────────────────────┤
│                                 │
│       ○  Skill Node 1           │
│      / \                        │
│     ○   ○  Skill Nodes 2-3     │  ← Skill Tree
│      \ /                        │  (scrollable)
│       ○  Skill Node 4           │
│       |                         │
│       ○  Checkpoint             │
│       |                         │
│      ...                        │
│                                 │
├─────────────────────────────────┤
│  [Home] [Leaderboard] [Shop]    │  ← Bottom Tab Bar
│  [Profile]                      │
└─────────────────────────────────┘
```

### 1.4.1 Top App Bar

| Element | Detail |
|---------|--------|
| Course Flag | Tappable flag icon for active language; tap opens course switcher bottom sheet |
| Streak Counter | Fire emoji + streak count; tap opens Streak Detail modal |
| Gem Counter | Gem icon + count; tap navigates to Shop |
| Heart Counter | Heart icon + count (max 5); tap opens Heart Refill options |
| Super Duolingo Badge | If subscribed, show shield icon with glow effect |

### 1.4.2 Daily Goal Progress Banner

| Property | Detail |
|----------|--------|
| Layout | Horizontal progress bar with XP fraction text |
| Behavior | Updates in real-time as XP is earned |
| Completion | When goal is met, bar turns gold and shows celebration animation (confetti burst) |
| Tap Action | Opens Daily Goal Detail bottom sheet (shows goal breakdown by activity) |

### 1.4.3 Skill Tree

| Property | Detail |
|----------|--------|
| Layout | Vertically scrollable path of skill nodes connected by lines |
| Node States | Locked (gray, padlock icon), Available (colored, pulsing glow), In Progress (colored, crown level indicator 1–5), Completed (gold, checkmark), Legendary (purple, star) |
| Node Tap (Available/In Progress) | Opens Skill Detail bottom sheet → "Start Lesson" CTA |
| Node Tap (Locked) | Shows tooltip "Complete [prerequisite skill] to unlock" |
| Checkpoint Nodes | Appear every 8–10 skills; larger node; tap opens Checkpoint Test (5-question mini-test unlocking next section) |
| Scroll Position | Persisted locally; on launch, auto-scrolls to first available skill |
| Pull-to-Refresh | Syncs latest course data from API |

### 1.4.4 Course Switcher

| Property | Detail |
|---------|--------|
| Trigger | Tap course flag in top bar |
| Layout | Bottom sheet with list of enrolled courses + "Add Course" button |
| Course Card | Flag, language name, current level, XP count |
| Add Course | Navigates to Language Selection (same as onboarding) |
| Switch Course | Tap a course card → dismiss sheet, reload home with new course data |

### 1.4.5 Bottom Tab Bar

| Tab | Icon | Destination |
|-----|------|-------------|
| Home | House | Home Screen (skill tree) |
| Leaderboard | Trophy | Leaderboard Screen |
| Shop | Gem | Shop Screen |
| Profile | Avatar | Profile Screen |

---

## 1.5 Lesson Flow

### Overview

The lesson flow is the core learning experience. Each lesson consists of 10–20 exercises of varying types, with real-time feedback, a lives system, XP scoring, and a results summary. Lessons are designed to take 3–8 minutes.

### Flow Diagram

```
Skill Detail Bottom Sheet
  → Lesson Loading (prefetch exercises)
    → Exercise 1
      → [Correct] Celebration + Next Exercise
      → [Incorrect] Correction + Queue for Retry → Next Exercise
        → Exercise 2
          → ...
            → [All Exercises Complete]
              → Lesson Complete Screen
                → Home Screen (updated progress)

  → [Lives = 0]
    → Out of Lives Screen
      → [Refill with Gems] → Resume Lesson
      → [Watch Ad] → Resume Lesson (free tier)
      → [Wait] → Home Screen
```

### 1.5.1 Lesson Loading

| Property | Detail |
|----------|--------|
| Screen Name | `LessonLoadingScreen` |
| Duration | 1–3 seconds while exercises are fetched/generated |
| Layout | Animated mascot with loading indicator |
| Prefetch | Download all exercise assets (audio, images) for the lesson |
| Offline | If exercises were pre-cached, skip loading screen entirely |
| Error | If fetch fails: "Couldn't load lesson" dialog with "Retry" and "Go Back" options |

### 1.5.2 Exercise Screen (General Structure)

```
┌─────────────────────────────────┐
│  [X]   ████████░░░░  7/15       │  ← Close + Progress Bar
├─────────────────────────────────┤
│                                 │
│  Exercise Prompt                │  ← Varies by type
│                                 │
│  ─────────────────────────────  │
│                                 │
│  Answer Area                    │  ← Varies by type
│                                 │
├─────────────────────────────────┤
│        [ CHECK ]                │  ← Submit Button
│  ❤️ ❤️ ❤️ ❤️ ❤️                     │  ← Lives Indicator
└─────────────────────────────────┘
```

| Element | Detail |
|---------|--------|
| Close Button (X) | Top-left; tap shows "Are you sure? You'll lose progress" confirmation dialog |
| Progress Bar | Segmented bar showing exercise completion (filled segments = completed exercises) |
| Check Button | Disabled until answer is provided; green when active |
| Lives Indicator | 5 hearts; one lost per incorrect answer (free tier only; Super users have unlimited) |

### 1.5.3 Exercise Types

#### Multiple Choice (Translation)

| Property | Detail |
|----------|--------|
| Prompt | "Translate this sentence" + sentence in target language (with audio playback) |
| Options | 3–4 cards with L1 translations |
| Selection | Single-select; tap highlights card |
| Audio | Auto-plays sentence audio on screen load; tap speaker icon to replay |

#### Word Bank (Sentence Construction)

| Property | Detail |
|----------|--------|
| Prompt | "Translate this sentence" + L1 sentence |
| Answer Area | Empty slots at top; word bank tiles at bottom |
| Interaction | Tap tile to add to answer; tap placed tile to remove; drag to reorder |
| Keyboard Option | "Use keyboard" toggle switches to free-text input |

#### Fill in the Blank

| Property | Detail |
|----------|--------|
| Prompt | Sentence with one blank (underlined space) |
| Options | 3–4 word options below the sentence |
| Selection | Tap to fill blank; tap again to deselect |

#### Listening Exercise

| Property | Detail |
|----------|--------|
| Prompt | "Type what you hear" + auto-playing audio |
| Answer Area | Text input field with L2 keyboard |
| Audio Controls | Normal speed button, slow speed (tortoise) button |
| Typo Tolerance | Minor typos accepted with "Pay attention to the accents!" warning |

#### Speaking Exercise

| Property | Detail |
|----------|--------|
| Prompt | "Say this sentence" + text of sentence to speak |
| Interaction | Tap microphone button to start recording; tap again to stop |
| Feedback | Speech-to-text comparison with highlighted correct/incorrect words |
| Skip Option | "Can't speak now" button skips without penalty |
| Permission | Requires microphone permission; if denied, exercise type is skipped |

#### Matching Exercise

| Property | Detail |
|----------|--------|
| Prompt | "Match the pairs" |
| Layout | Two columns of tiles (L1 left, L2 right) |
| Interaction | Tap one tile, then tap its match; correct pairs animate out with green flash; incorrect pairs show red shake |
| Completion | All pairs matched = exercise complete |

#### Character Exercise (for character-based languages)

| Property | Detail |
|----------|--------|
| Prompt | "Select the correct character" + audio pronunciation |
| Options | Grid of 6–9 characters |
| Used For | Japanese (Hiragana/Katakana), Korean (Hangul), Chinese, Arabic, Hindi |

### 1.5.4 Answer Feedback

#### Correct Answer

| Property | Detail |
|----------|--------|
| Visual | Bottom bar slides up in green with "Correct!" text and checkmark icon |
| Audio | Success chime (150ms) |
| Haptic | Light impact feedback |
| XP Display | "+10 XP" with sparkle animation |
| Auto-Advance | After 1.2 seconds, automatically transitions to next exercise |
| Manual Advance | "Continue" button for immediate advancement |

#### Incorrect Answer

| Property | Detail |
|----------|--------|
| Visual | Bottom bar slides up in red with "Correct answer: [answer]" |
| Audio | Error tone (200ms) |
| Haptic | Medium impact feedback |
| Heart Loss | Heart icon animates (shrink + fade) — one heart deducted |
| Retry Queue | Incorrect exercise is added to end of lesson queue for retry |
| Manual Advance | "Continue" button to proceed |

### 1.5.5 Out of Lives

| Property | Detail |
|----------|--------|
| Trigger | Lives reach 0 during a lesson |
| Screen | Modal overlay with sad mascot, "You ran out of hearts!" |
| Option 1 | "Refill Hearts" — costs 450 gems → resumes lesson with 5 hearts |
| Option 2 | "Watch an Ad" — 30-second rewarded video → resumes with 1 heart (free tier, max 3 per day) |
| Option 3 | "Practice to Earn Hearts" — navigates to Practice mode (review of mastered content, earns 1 heart per completion) |
| Option 4 | "No Thanks" → exits to Home Screen (lesson progress lost) |
| Timer | Hearts regenerate: 1 heart per 5 hours (max 5). Timer shown on screen |
| Super Duolingo | Unlimited hearts; this screen is never shown |

### 1.5.6 Lesson Complete Screen

| Property | Detail |
|----------|--------|
| Screen Name | `LessonCompleteScreen` |
| Layout | Animated results with confetti/fireworks |
| Metrics Shown | XP earned (animated counter), accuracy percentage, time spent, streak status |
| Combo Bonus | If ≥3 correct in a row during lesson, bonus XP (+5 per combo level, max +25) |
| No-Mistake Bonus | If 100% accuracy, show "Perfect!" badge + 5 bonus XP |
| Crown Progress | If lesson completes a crown level, show crown animation (level 1→2→3→4→5) |
| Share CTA | "Share your progress" button → opens system share sheet with branded image |
| Primary CTA | "Continue" → returns to Home Screen |
| Analytics Event | `lesson_completed { skill_id: string, crown_level: int, xp_earned: int, accuracy: float, duration_seconds: int, exercise_count: int }` |

---

## 1.6 XP & Streak Flow

### Overview

XP (Experience Points) and streaks are the core motivation mechanics. XP is earned through lessons, practice, and bonus activities. Streaks track consecutive days of meeting the daily XP goal.

### 1.6.1 XP System

| Source | XP Amount |
|--------|-----------|
| Regular Lesson | 10–15 XP base + accuracy bonus (0–5 XP) + combo bonus (0–25 XP) |
| Practice Session | 10 XP (fixed) |
| Placement Test | 20–100 XP (based on level achieved) |
| Story Completion | 20 XP |
| Checkpoint Test | 30 XP |
| Legendary Level | 40 XP |
| Streak Bonus | +1 XP per day of active streak (cap at +20) |
| Double XP Power-Up | 2× all XP for 15 minutes (purchasable in shop) |
| Friend Quest | 10–50 XP (varies by quest) |

### 1.6.2 Daily Goal

| Property | Detail |
|----------|--------|
| Goal Options | Casual (10 XP), Regular (20 XP), Serious (30 XP), Intense (50 XP) |
| Reset Time | User's local midnight |
| Progress Tracking | Real-time counter on home screen |
| Goal Completion | Triggers celebration animation + streak increment (if not already counted today) |
| Goal Change | Can be changed in Settings; takes effect next day |

### 1.6.3 Streak System

| Property | Detail |
|----------|--------|
| Definition | Number of consecutive calendar days the user met their daily XP goal |
| Display | Fire emoji + number in top bar, with pulsing animation at milestones |
| Streak Freeze | Power-up that protects one missed day; auto-consumed at midnight if goal not met |
| Streak Repair | After streak loss, option to repair for gems (cost increases with streak length: 200 + streak_days × 5 gems, max 1000) |
| Milestones | 7, 14, 30, 50, 100, 200, 365 days — each triggers special animation and badge |
| Weekend Amulet | Friday-purchasable power-up protecting Saturday and Sunday |
| Streak Society | At 7+ day streak, user joins "Streak Society" — visible badge on profile |

### 1.6.4 Streak Detail Modal

| Property | Detail |
|----------|--------|
| Trigger | Tap streak counter in top bar |
| Layout | Calendar view of current month with fire icons on active days, freeze icons on protected days, X on missed days |
| Streak Freeze Status | Shows owned freeze count and "Get Streak Freeze" button (200 gems) |
| History | Shows longest streak ever achieved |

---

## 1.7 Skill Tree Navigation

### Overview

The skill tree is the primary course structure. It represents the learning path as a vertical sequence of skill nodes organized into sections separated by checkpoint nodes.

### 1.7.1 Skill Node Structure

| Property | Detail |
|----------|--------|
| Visual | Circular node (56dp diameter) with skill icon |
| Crown Levels | 0 (locked) → 1 (introduced, purple) → 2 (green) → 3 (blue) → 4 (yellow) → 5 (gold, mastered) |
| Legendary Level | Available after crown 5; purple node with star icon; 4 challenge sessions with no hints |
| Crown Level Indicator | Small crown icon with number overlay below the node |
| Skill Name | Label below node |
| Lessons per Level | Level 1: 3 lessons, Level 2: 3 lessons, Level 3: 4 lessons, Level 4: 4 lessons, Level 5: 5 lessons |

### 1.7.2 Node States

| State | Visual | Tap Behavior |
|-------|--------|--------------|
| Locked | Gray, padlock overlay | Toast: "Complete [Prerequisite] to unlock" |
| Available | Colored (per crown level), subtle bounce animation | Opens Skill Detail Bottom Sheet |
| Current | Same as available + glowing ring animation | Opens Skill Detail Bottom Sheet |
| Completed (Gold) | Gold with checkmark | Opens Skill Detail Bottom Sheet (for practice) |
| Cracked | Gold with crack lines (needs refresh due to decay) | Opens Skill Detail Bottom Sheet with "Practice" CTA |
| Legendary | Purple with star | Opens Legendary Challenge prompt |

### 1.7.3 Skill Detail Bottom Sheet

| Property | Detail |
|----------|--------|
| Trigger | Tap on an available/in-progress/completed skill node |
| Layout | Skill icon, skill name, crown level indicator, lesson list |
| Lesson List | Numbered lessons (Lesson 1, 2, 3...) with completion status (checkmark or empty circle) |
| Primary CTA | "Start" (next incomplete lesson) or "Practice" (if all complete) |
| Secondary Info | Words taught in this skill, tips & notes link |
| Tips & Notes | Tap opens grammar/vocabulary explanation screen (markdown-rendered content) |

### 1.7.4 Checkpoint Nodes

| Property | Detail |
|----------|--------|
| Frequency | Every 8–12 skills |
| Visual | Larger node (72dp), castle/tower icon |
| Test Format | 15 questions covering all skills in the preceding section |
| Passing | Must score ≥80%; failure allows retry |
| Reward | 30 XP + unlock next section of skill tree |
| Bypass | Cannot be skipped; must be completed to access subsequent skills |

### 1.7.5 Skill Decay (Cracked Skills)

| Property | Detail |
|----------|--------|
| Trigger | Spaced repetition algorithm flags skill for review (typically 2–4 weeks after last practice) |
| Visual | Gold node develops "crack" lines overlay |
| Notification | In-app banner: "Your [Skill Name] needs practice!" |
| Practice | Completing one practice session restores the skill |
| Impact | Cracked skills don't affect progression; they're review prompts |

---

## 1.8 Leaderboards

### Overview

The leaderboard system uses a league-based competitive structure inspired by sports leagues. Users are grouped into weekly cohorts and compete for promotion, maintenance, or relegation based on XP earned.

### 1.8.1 League Structure

| League | Tier | Promotion Threshold | Demotion Threshold |
|--------|------|--------------------|--------------------|
| Bronze | 1 | Top 10 advance | N/A (lowest) |
| Silver | 2 | Top 10 advance | Bottom 5 demoted |
| Gold | 3 | Top 10 advance | Bottom 5 demoted |
| Sapphire | 4 | Top 10 advance | Bottom 5 demoted |
| Ruby | 5 | Top 10 advance | Bottom 5 demoted |
| Emerald | 6 | Top 10 advance | Bottom 5 demoted |
| Amethyst | 7 | Top 10 advance | Bottom 5 demoted |
| Pearl | 8 | Top 10 advance | Bottom 5 demoted |
| Obsidian | 9 | Top 10 advance | Bottom 5 demoted |
| Diamond | 10 | Top 3 enter tournament | Bottom 5 demoted |

### 1.8.2 Leaderboard Screen

| Property | Detail |
|----------|--------|
| Screen Name | `LeaderboardScreen` |
| Tab | "Leaderboard" in bottom tab bar |
| Layout | League badge at top, scrollable ranked list of 30 users |
| User Row | Rank number, avatar, display name, XP for the week, promotion/demotion zone highlighting |
| Promotion Zone | Top 10 rows highlighted in green |
| Danger Zone | Bottom 5 rows highlighted in red |
| Current User | Always visible (sticky row if scrolled off-screen), highlighted with blue border |
| Refresh | Auto-refreshes every 5 minutes; pull-to-refresh available |
| Week Timer | Countdown to end of week (resets Sunday at midnight UTC) |

### 1.8.3 End-of-Week Results

| Property | Detail |
|----------|--------|
| Trigger | Monday at 00:00 UTC |
| Screen | Full-screen celebration or commiseration overlay on next app open |
| Promotion | Confetti animation, new league badge reveal, "+1 League" XP bonus (50 XP) |
| Maintained | Neutral message: "You stayed in [League]. Keep it up!" |
| Demotion | Subdued animation, league badge change, encouragement message |
| Analytics Event | `leaderboard_week_completed { league: string, rank: int, promoted: bool, demoted: bool, xp_earned: int }` |

### 1.8.4 Friend Leaderboard

| Property | Detail |
|----------|--------|
| Toggle | Segmented control at top: "League" / "Friends" |
| Data Source | Friends list from social connections |
| Layout | Same ranked list format but filtered to friends |
| Empty State | "Add friends to compete!" with invite button |

---

## 1.9 Rewards & Achievements

### Overview

The rewards system provides long-term motivation through achievements, badges, and milestone celebrations.

### 1.9.1 Achievement Categories

| Category | Examples |
|----------|----------|
| Streak | "Week Warrior" (7-day), "Streak Legend" (365-day) |
| XP | "XP Beginner" (100 XP total), "XP Master" (50,000 XP) |
| Lessons | "First Lesson", "Century" (100 lessons), "Thousand" (1,000 lessons) |
| Accuracy | "Perfectionist" (10 perfect lessons), "Sharpshooter" (100 perfect lessons) |
| Social | "Friendly" (add first friend), "Popular" (10 friends) |
| Course | "First Crown", "Golden Tree" (all skills gold), "Legendary" (first legendary level) |
| League | "Bronze Medal", "Diamond Champion" |
| Special | "Night Owl" (lesson at 2 AM), "Early Bird" (lesson before 6 AM), "Weekend Warrior" (lessons every weekend for a month) |

### 1.9.2 Achievement Detail

| Property | Detail |
|----------|--------|
| Screen Name | `AchievementsScreen` |
| Access | Profile → Achievements tab |
| Layout | Grid of achievement badges (earned = colored, unearned = gray silhouette) |
| Tap Behavior | Opens achievement detail modal: name, description, date earned (or progress if unearned) |
| Earned Animation | When first earned: full-screen overlay with badge animation, confetti, "+[X] XP" |
| Badge Display | Earned badges can be pinned to profile (max 3 pinned) |

### 1.9.3 Daily Rewards

| Property | Detail |
|----------|--------|
| Trigger | First app open each day (after daily reset) |
| Layout | Treasure chest animation that opens to reveal reward |
| Rewards | Day 1: 5 gems, Day 2: 10 gems, Day 3: chest (random 15–50 gems), Day 4: streak freeze, Day 5: 25 gems, Day 6: double XP boost, Day 7: super chest (50–100 gems + power-up) |
| Streak Multiplier | If streak ≥7, daily reward amounts increase by 50% |
| Miss a Day | Resets daily reward cycle to Day 1 |

---

## 1.10 Shop & Currency Flow

### Overview

The shop allows users to spend gems (earned through gameplay or purchased) on power-ups, cosmetics, and other items.

### 1.10.1 Currency Types

| Currency | Earn Method | Use |
|----------|-------------|-----|
| Gems | Lessons, achievements, daily rewards, purchase | Shop items, streak repair, heart refill |
| Hearts | Time regeneration (1/5hrs), ads, purchase, practice | Required to attempt lessons (free tier) |

### 1.10.2 Shop Screen

| Property | Detail |
|----------|--------|
| Screen Name | `ShopScreen` |
| Tab | "Shop" in bottom tab bar |
| Layout | Gem balance at top, categorized item grid |
| Categories | Power-Ups, Heart Refills, Streak Items, Outfits, Super Duolingo |

### 1.10.3 Shop Items

| Item | Cost | Effect |
|------|------|--------|
| Heart Refill | 450 gems | Restores hearts to 5 |
| Streak Freeze | 200 gems | Protects one missed day |
| Double XP Boost | 200 gems | 2× XP for 15 minutes |
| Timer Boost | 100 gems | Extra 30 seconds on timed challenges |
| Weekend Amulet | 200 gems | Protects streak for Saturday + Sunday |
| Mascot Outfit | 100–500 gems | Cosmetic outfit for owl mascot |

### 1.10.4 Gem Purchase (IAP)

| Package | Price (USD) | Gems | Bonus |
|---------|-------------|------|-------|
| Handful | $1.99 | 200 | — |
| Pouch | $5.99 | 700 | +100 bonus |
| Sack | $11.99 | 1,500 | +300 bonus |
| Chest | $23.99 | 3,500 | +1,000 bonus |
| Treasure | $47.99 | 8,000 | +3,000 bonus |

### 1.10.5 Super Duolingo (Subscription)

| Feature | Detail |
|---------|--------|
| Price | $12.99/month or $79.99/year |
| Benefits | Unlimited hearts, no ads, unlimited streak repair, progress quizzes, mastery quizzes, monthly streak reward, Super badge on profile |
| Trial | 14-day free trial for new subscribers |
| Family Plan | $119.99/year for up to 6 members |
| Billing | Through App Store / Google Play subscription APIs |
| Cancellation | Managed through platform subscription settings; access until end of billing period |

---

## 1.11 Notifications Flow

### Overview

Notifications serve as the primary re-engagement mechanism. They include push notifications, in-app messages, and email nudges.

### 1.11.1 Push Notification Types

| Type | Trigger | Message Example | Frequency |
|------|---------|-----------------|-----------|
| Streak Reminder | 2 hours before midnight if goal not met | "Don't lose your 15-day streak! 🔥" | Daily (max 1) |
| Lesson Reminder | User-configured time | "Time for your daily Spanish lesson!" | Daily |
| Streak Lost | Streak broken at midnight | "Oh no! Your streak was lost 😢" | Once |
| League Update | Rank change in leaderboard | "You moved up to #3 in Silver League!" | Max 2/day |
| Friend Activity | Friend passes user in XP | "Maria just passed you! Time to practice?" | Max 1/day |
| Achievement | Achievement unlocked | "🏆 You earned 'Week Warrior'!" | On event |
| Comeback | User inactive for 2+ days | "We miss you! Your Spanish skills are getting rusty" | Day 2, 5, 14, 30 of inactivity, then stop |
| Streak Freeze Used | Streak freeze auto-consumed | "Your Streak Freeze saved your streak! ❄️" | On event |
| Sale/Promotion | Marketing campaign | "50% off Super Duolingo this weekend!" | Max 1/week |

### 1.11.2 Notification Scheduling

| Property | Detail |
|----------|--------|
| Preferred Time | User sets preferred reminder time in Settings (default: 9:00 AM local) |
| Smart Timing | ML model adjusts delivery time based on when user typically opens app |
| Quiet Hours | No notifications between 10 PM and 7 AM local time (configurable) |
| Rate Limiting | Max 3 push notifications per day across all types |
| Unsubscribe | Per-type toggles in Settings → Notifications |

### 1.11.3 In-App Messages

| Type | Trigger | Display |
|------|---------|---------|
| Streak at Risk | Opens app after 6 PM without meeting goal | Top banner (yellow): "Complete your daily goal to keep your streak!" |
| Practice Suggestion | Opens app, all lessons current | Card on home: "Practice [weakest skill] to keep it strong" |
| Friend Challenge | Friend sends challenge | Modal: "Maria challenged you to earn 50 XP today!" |
| Super Upsell | After losing hearts 3 times in a week | Bottom sheet: "Never run out of hearts with Super Duolingo" |
| Review Prompt | After 7th consecutive day of use | Alert dialog: "Enjoying the app? Rate us!" (shown once, respects "Don't ask again") |

### 1.11.4 Notification Permission Flow

| Property | Detail |
|----------|--------|
| Timing | Requested after first lesson completion (not on first launch) |
| Pre-Permission | Custom screen explaining benefits before OS prompt: "Get reminders to keep your streak alive!" |
| If Denied | App continues without push; shows in-app banner suggesting to enable in Settings |
| Deep Link | Notification tap deep-links to relevant screen (e.g., streak reminder → lesson start) |

---

## 1.12 Offline Mode Behavior

### Overview

The app provides a robust offline experience by pre-downloading lesson content. Users can complete lessons, earn XP, and maintain streaks while offline. Progress syncs when connectivity is restored.

### 1.12.1 Content Pre-Downloading

| Property | Detail |
|----------|--------|
| Auto-Download | Next 3 lessons in current skill are automatically cached |
| WiFi-Only Option | Settings toggle: "Download on WiFi only" (default: on) |
| Manual Download | Long-press skill node → "Download for Offline" downloads all lessons in that skill |
| Storage Indicator | Settings → Storage shows offline content size (typically 50–200 MB per course) |
| Storage Limit | Configurable max offline storage (default: 500 MB); LRU eviction for old content |

### 1.12.2 Offline Capabilities

| Feature | Offline Support |
|---------|----------------|
| Complete Lessons | ✅ Full support |
| Earn XP | ✅ Tracked locally, synced later |
| Maintain Streak | ✅ Recorded locally with timestamp |
| Practice Sessions | ✅ Uses cached content |
| Audio Playback | ✅ If pre-downloaded |
| Speech Exercises | ⚠️ Limited (on-device STT if available, otherwise skipped) |
| Leaderboard | ❌ View cached; no live updates |
| Shop Purchases | ❌ Requires connectivity |
| Social Features | ❌ Requires connectivity |
| Profile Updates | ❌ Queued for sync |

### 1.12.3 Sync on Reconnect

| Property | Detail |
|----------|--------|
| Detection | `connectivity_plus` package monitors network state changes |
| Trigger | Automatic sync when connectivity restored (WiFi or cellular) |
| Sync Order | 1. Auth token refresh → 2. Upload progress → 3. Upload XP/streak → 4. Download new content → 5. Refresh leaderboard |
| Conflict Resolution | Server timestamp wins for leaderboard/social; client timestamp wins for progress/XP (ensures user credit) |
| Queue | Offline actions stored in `SyncQueue` table in local DB; processed FIFO on reconnect |
| Retry | Failed sync items retried with exponential backoff (1s, 2s, 4s, 8s, max 60s) |
| User Feedback | Subtle sync indicator in top bar during sync; success toast on completion |

### 1.12.4 Offline Indicator

| Property | Detail |
|----------|--------|
| Display | Banner at top of screen: "You're offline. Your progress will sync when you're back online." |
| Color | Gray background, airplane icon |
| Dismissable | No (persistent while offline) |
| Behavior | Automatically hidden when connectivity restored |

---

## 1.13 Settings & Profile Flow

### Overview

Settings and profile management provide control over account, preferences, notifications, and privacy.

### 1.13.1 Profile Screen

| Property | Detail |
|----------|--------|
| Screen Name | `ProfileScreen` |
| Tab | "Profile" in bottom tab bar |
| Layout | Avatar, display name, join date, stats summary, followed by tabbed sections |
| Stats | Total XP, current streak, longest streak, courses studied, league, achievements count |
| Tabs | "Statistics", "Achievements", "Friends" |
| Edit | Tap avatar or "Edit Profile" button → Profile Edit Screen |

### 1.13.2 Profile Edit Screen

| Property | Detail |
|----------|--------|
| Screen Name | `ProfileEditScreen` |
| Fields | Avatar (camera/gallery picker), display name, username, bio (140 chars max), location (optional) |
| Avatar Upload | Cropped to circle, max 5 MB, compressed to 400×400 px |
| Save | "Save" button in top-right; loading indicator during API call |
| Validation | Username: 3–20 chars, alphanumeric + underscores, unique check via API on blur |

### 1.13.3 Settings Screen

| Property | Detail |
|----------|--------|
| Screen Name | `SettingsScreen` |
| Access | Profile → gear icon in top-right |
| Sections | Account, Notifications, General, Accessibility, Privacy, About |

#### Account Section

| Setting | Detail |
|---------|--------|
| Email | View/change email (requires password confirmation) |
| Password | Change password (current + new + confirm) |
| Connected Accounts | Link/unlink Google, Apple, Facebook |
| Subscription | View/manage Super Duolingo status |
| Delete Account | Red button; requires password confirmation; 30-day grace period |

#### Notifications Section

| Setting | Detail |
|---------|--------|
| Lesson Reminders | Toggle + time picker |
| Streak Reminders | Toggle |
| Leaderboard Updates | Toggle |
| Friend Activity | Toggle |
| Promotions | Toggle |
| Quiet Hours | Toggle + start/end time pickers |

#### General Section

| Setting | Detail |
|---------|--------|
| Daily Goal | Picker: Casual, Regular, Serious, Intense |
| Sound Effects | Toggle |
| Listening Exercises | Toggle (disable if in quiet environment) |
| Speaking Exercises | Toggle |
| Animations | Toggle (reduced motion) |
| Download on WiFi Only | Toggle |
| App Language | Picker (language of UI, independent of learning language) |

#### Accessibility Section

| Setting | Detail |
|---------|--------|
| High Contrast Mode | Toggle |
| Font Size | Slider (Small, Default, Large, Extra Large) |
| Screen Reader Optimization | Toggle (simplifies UI for TalkBack/VoiceOver) |
| Colorblind Mode | Picker: None, Protanopia, Deuteranopia, Tritanopia |
| Haptic Feedback | Toggle |

#### Privacy Section

| Setting | Detail |
|---------|--------|
| Profile Visibility | Public / Friends Only / Private |
| Leaderboard Participation | Toggle |
| Activity Sharing | Toggle (share progress with friends) |
| Data Export | Button → request data export (GDPR compliance) |
| Analytics Opt-Out | Toggle |

#### About Section

| Setting | Detail |
|---------|--------|
| App Version | Display current version + build number |
| Terms of Service | Opens WebView |
| Privacy Policy | Opens WebView |
| Open Source Licenses | Opens licenses list screen |
| Support | Opens help center or email compose |

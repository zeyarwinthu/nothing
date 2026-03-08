# 6. Business Logic Documentation

## 6.1 Lesson Progression Logic

### Skill Unlocking

Skills are organized in a tree structure. Each skill has zero or more prerequisites. A skill becomes **unlocked** when ALL prerequisites are completed (at least 1 crown earned).

```
Algorithm: CanUnlockSkill(userId, skillId)
─────────────────────────────────────────
1. Fetch prerequisites for skillId from skill_prerequisites table
2. If no prerequisites exist → skill is unlocked (root skill)
3. For each prerequisite:
   a. Check if user has earned ≥ 1 crown for that skill
   b. If ANY prerequisite is incomplete → skill remains LOCKED
4. If ALL prerequisites are complete → skill is UNLOCKED
```

### Skill States

| State          | Condition                                                         | Visual     |
|----------------|-------------------------------------------------------------------|------------|
| `locked`       | Prerequisites not met                                              | Gray/dim   |
| `unlocked`     | Prerequisites met, no progress                                     | Colored    |
| `in_progress`  | At least 1 lesson completed, < 1 crown                            | Partially filled |
| `crown_1`      | All lessons completed once (crown 1)                               | 1 crown    |
| `crown_2–4`    | All lessons completed at higher difficulty                         | 2–4 crowns |
| `crown_5`      | Legendary crown earned (most difficult)                            | Gold/legend|
| `cracked`      | Skill strength decayed below 50%                                   | Cracked icon|

### Crown Progression

Each skill has 5 crown levels. Each crown requires completing all lessons at increasing difficulty:

| Crown Level | Difficulty    | Exercise Changes                                  | XP Multiplier |
|-------------|---------------|---------------------------------------------------|---------------|
| Crown 1     | Basic         | Word bank provided, multiple choice heavy          | 1.0x          |
| Crown 2     | Easy          | Fewer hints, some free-text translation            | 1.0x          |
| Crown 3     | Medium        | No word bank, more free-text                       | 1.0x          |
| Crown 4     | Hard          | Mostly free-text, listening, fewer hints           | 1.0x          |
| Crown 5     | Legendary     | All free-text, no hints, harder sentences          | 2.0x          |

### Lesson Exercise Selection

```
Algorithm: GenerateExerciseSet(lessonId, crownLevel, userId)
─────────────────────────────────────────────────────────────
1. Fetch all exercises for lessonId
2. Filter exercises appropriate for crownLevel difficulty
3. Apply adaptive difficulty based on user's word_strength:
   a. Include 60% exercises for weak words (strength < 0.5)
   b. Include 30% exercises for medium words (0.5 ≤ strength < 0.8)
   c. Include 10% exercises for strong words (strength ≥ 0.8)
4. Randomize order
5. Ensure variety of exercise types (no more than 2 consecutive of same type)
6. Return 6–20 exercises based on crown level:
   - Crown 1: 6–8 exercises
   - Crown 2: 8–10 exercises
   - Crown 3: 10–12 exercises
   - Crown 4: 12–15 exercises
   - Crown 5: 15–20 exercises
```

---

## 6.2 XP System

### XP Sources

| Source               | Base XP | Conditions                          | Max Per Day |
|----------------------|---------|-------------------------------------|-------------|
| Lesson completion    | 10 XP   | Complete all exercises               | No limit    |
| Perfect lesson bonus | +5 XP   | Zero mistakes in the lesson          | No limit    |
| First lesson of day  | +5 XP   | First lesson completed today         | Once        |
| Practice session     | 5–10 XP | Based on performance                 | No limit    |
| Streak milestone     | 10–50 XP| At milestone days (7, 14, 30, etc.) | Per milestone|
| Achievement unlock   | 5–50 XP | Based on achievement tier            | Per achieve.|
| XP Doubler (active)  | 2x      | Active for 15 minutes                | Per purchase|
| Combo bonus          | +1–5 XP | Consecutive correct answers          | Per session |
| Timed challenge      | 5–40 XP | Based on correct answers in time     | No limit    |

### XP Calculation Algorithm

```
Algorithm: CalculateSessionXP(session)
──────────────────────────────────────
Input: Completed lesson session object

baseXp = session.Lesson.XpReward            // Usually 10

// Perfect bonus
perfectBonus = 0
IF session.Accuracy == 1.0 THEN
    perfectBonus = 5

// First lesson of day bonus
dailyBonus = 0
IF IsFirstLessonToday(session.UserId) THEN
    dailyBonus = 5

// Combo bonus (consecutive correct answers)
comboBonus = CalculateComboBonus(session.Answers)
// 3 in a row: +1, 5 in a row: +2, 8 in a row: +3, 10+: +5

// XP Doubler check
multiplier = 1
IF HasActiveXpDoubler(session.UserId) THEN
    multiplier = 2

// Crown level multiplier (Crown 5 = Legendary)
crownMultiplier = 1.0
IF session.CrownLevel == 5 THEN
    crownMultiplier = 2.0

totalXp = (baseXp + perfectBonus + dailyBonus + comboBonus)
          * multiplier * crownMultiplier

RETURN FLOOR(totalXp)
```

### Level Progression

XP maps to levels with increasing thresholds:

| Level Range | XP Per Level | Cumulative XP to Reach |
|-------------|-------------|------------------------|
| 1–5         | 60 XP       | 0–300 XP               |
| 6–10        | 100 XP      | 300–800 XP             |
| 11–15       | 150 XP      | 800–1,550 XP           |
| 16–20       | 200 XP      | 1,550–2,550 XP         |
| 21–25       | 300 XP      | 2,550–4,050 XP         |
| 26–30       | 400 XP      | 4,050–6,050 XP         |
| 31+         | 500 XP      | 6,050+ XP              |

```
Algorithm: CalculateLevel(totalXp)
──────────────────────────────────
level = 1
xpRemaining = totalXp

thresholds = [
  (5, 60), (10, 100), (15, 150),
  (20, 200), (25, 300), (30, 400)
]

FOR EACH (maxLevel, xpPerLevel) IN thresholds:
    levelsInRange = maxLevel - level + 1
    xpForRange = levelsInRange * xpPerLevel
    IF xpRemaining < xpForRange THEN
        level += FLOOR(xpRemaining / xpPerLevel)
        RETURN level
    xpRemaining -= xpForRange
    level = maxLevel + 1

// Level 31+
level += FLOOR(xpRemaining / 500)
RETURN level
```

---

## 6.3 Streak Logic

### Core Streak Rules

1. A user's streak increases by 1 for each consecutive calendar day they complete at least 1 lesson
2. "Calendar day" is determined by the user's configured timezone
3. If a user misses a day and has a streak freeze, the freeze is consumed and the streak is preserved
4. If a user misses a day without a freeze, the streak resets to 0
5. Streaks are evaluated by a background job at 00:05 UTC

### Streak Evaluation Algorithm

```
Algorithm: EvaluateStreak(userId)
────────────────────────────────
// Runs daily at 00:05 UTC

1. Fetch user's streak record and timezone
2. Determine yesterday's date in user's timezone
3. Check if user had qualifying activity yesterday:
   a. Query lesson_sessions WHERE user_id = userId
      AND DATE(completed_at AT TIME ZONE userTZ) = yesterday
      AND status = 'completed'

4. IF activity exists:
   a. Streak already extended (handled in real-time on lesson complete)
   b. No action needed

5. IF no activity:
   a. Check if streak freeze is available (freeze_count > 0)
   b. IF freeze available:
      - Decrement freeze_count by 1
      - Keep current_count unchanged
      - Publish "StreakFrozen" event
      - Log: "Streak freeze applied for {userId}"
   c. IF no freeze:
      - Set current_count = 0
      - Set start_date = NULL
      - Publish "StreakBroken" event
      - Send "streak_lost" notification
      - Log: "Streak broken for {userId}, was {previousCount} days"

6. Update longest_count = MAX(longest_count, current_count)
```

### Real-Time Streak Extension

When a user completes a lesson, the streak is extended in real-time:

```
Algorithm: ExtendStreak(userId)
──────────────────────────────
1. Fetch user's streak record
2. Get today's date in user's timezone
3. IF last_activity_date == today:
   → Already counted, no change
4. IF last_activity_date == yesterday:
   → Consecutive day, current_count += 1
5. IF last_activity_date < yesterday:
   → Gap exists (freeze may have covered), current_count = 1
   → Set start_date = today
6. Set last_activity_date = today
7. Update longest_count = MAX(longest_count, current_count)
8. Publish "StreakExtended" event
9. Check streak milestones and award gems if applicable
```

### Streak Milestones & Rewards

| Milestone (days) | Gem Reward | Achievement                    |
|-------------------|-----------|--------------------------------|
| 3                 | 5         | -                              |
| 7                 | 10        | Wildfire (Bronze)              |
| 14                | 20        | -                              |
| 30                | 50        | Wildfire (Silver)              |
| 50                | 100       | -                              |
| 100               | 250       | Wildfire (Gold)                |
| 200               | 500       | -                              |
| 365               | 1000      | Wildfire (Legendary)           |

### Streak Freeze Rules

- Maximum 2 streak freezes in inventory at any time
- Cost: 200 gems each from the shop
- Consumed automatically during nightly evaluation (not manually activated)
- Only 1 freeze can be consumed per missed day
- Cannot protect against 2+ consecutive missed days (1 freeze per day)
- Premium users earn 1 free freeze per month

---

## 6.4 Leaderboards

### League System

10 leagues in ascending order:

| Tier | League    | Icon Color | Group Size | Promotion Slots | Demotion Slots |
|------|-----------|------------|------------|-----------------|----------------|
| 1    | Bronze    | 🟤 Brown   | 30         | 10              | 0 (lowest)     |
| 2    | Silver    | ⚪ Silver  | 30         | 10              | 5              |
| 3    | Gold      | 🟡 Gold    | 30         | 10              | 5              |
| 4    | Sapphire  | 🔵 Blue    | 30         | 10              | 5              |
| 5    | Ruby      | 🔴 Red     | 30         | 10              | 5              |
| 6    | Emerald   | 🟢 Green   | 30         | 10              | 5              |
| 7    | Amethyst  | 🟣 Purple  | 30         | 10              | 5              |
| 8    | Pearl     | ⚪ White   | 30         | 10              | 5              |
| 9    | Obsidian  | ⚫ Black   | 30         | 10              | 5              |
| 10   | Diamond   | 💎 Diamond | 30         | 0 (highest)     | 5              |

### Group Assignment Algorithm

```
Algorithm: AssignLeagueGroup(userId, tier)
──────────────────────────────────────────
// Runs when user is promoted/demoted or first joins

1. Find an existing league group for the target tier and current week
   with < 30 members
2. IF found:
   → Add user to that group
3. IF no group available:
   → Create a new league group for this tier/week
   → Add user as first member
4. Create league_membership record
5. Initialize weekly_xp = 0
```

### Weekly XP Tracking

Leaderboard XP is tracked in Redis using sorted sets for real-time ranking:

```
Redis Key: leaderboard:{leagueId}:weekly
Type: Sorted Set
Score: weekly XP
Member: userId

Commands:
  ZINCRBY leaderboard:lg_gold_2024w24:weekly 20 usr_a1b2c3
  ZREVRANGE leaderboard:lg_gold_2024w24:weekly 0 29 WITHSCORES
  ZREVRANK leaderboard:lg_gold_2024w24:weekly usr_a1b2c3
```

### Weekly Reset Algorithm

```
Algorithm: WeeklyLeaderboardReset()
───────────────────────────────────
// Runs Monday 00:00 UTC

FOR EACH active league group:

  1. Get final rankings from Redis sorted set
  2. Store rankings in leaderboard_history table

  3. Determine promotions (top N users):
     FOR rank 1 to promotion_count:
       - Mark user as promoted
       - Calculate new tier = current_tier + 1 (cap at Diamond)
       - Send "leaderboard_promotion" notification

  4. Determine demotions (bottom N users):
     FOR rank (total - demotion_count + 1) to total:
       - Mark user as demoted
       - Calculate new tier = current_tier - 1 (floor at Bronze)
       - Send "leaderboard_demotion" notification

  5. Safe zone (middle users):
     - Remain in current tier

  6. Delete Redis sorted set for completed week
  7. Mark league group as "completed"
  8. Create new league groups for next week
  9. Assign all users to new groups based on new tiers
```

### Tie-Breaking Rules

1. If users tie in XP, the user who reached that XP first ranks higher
2. For promotion ties at the boundary: both users are promoted (generous)
3. For demotion ties at the boundary: neither user is demoted (generous)

---

## 6.5 Skill Tree Logic

### Tree Structure

The skill tree is a directed acyclic graph (DAG) organized into sections:

```
Section: Beginner
├── Basics 1 (no prerequisites)
├── Basics 2 (requires: Basics 1)
├── Greetings (requires: Basics 1)
├── Food (requires: Basics 2)
└── Animals (requires: Basics 2, Greetings)

Section: Intermediate
├── Travel (requires: Food, Animals)
├── Shopping (requires: Travel)
├── Past Tense (requires: Travel)
└── Subjunctive (requires: Past Tense)

Section: Advanced
├── Business (requires: Shopping, Subjunctive)
├── Literature (requires: Subjunctive)
└── Idioms (requires: Business, Literature)
```

### Skill Strength & Decay

Each skill has a strength value that decays over time based on spaced repetition:

```
Algorithm: CalculateSkillStrength(userId, skillId)
──────────────────────────────────────────────────
1. Fetch all words associated with this skill
2. For each word, get the user's word_strength record
3. Skill strength = average of all word strengths

Word strength decay formula (simplified SM-2):
  strength = initial_strength * e^(-t / (interval * ease_factor))

  Where:
  - t = days since last review
  - interval = current review interval
  - ease_factor = user's ease factor for this word (default 2.5)
```

### Practice Session Generation

When a user practices a skill, exercises are generated targeting weak words:

```
Algorithm: GeneratePracticeSession(userId, skillId)
───────────────────────────────────────────────────
1. Fetch words for this skill ordered by strength ASC
2. Select top 10 weakest words
3. For each word:
   a. Select 1–3 exercises that test this word
   b. Vary exercise types
4. Shuffle exercises
5. Return session with 10–15 exercises
6. After completion, update word_strength using SM-2:
   IF correct:
     ease_factor = max(1.3, ease_factor + 0.1)
     interval = interval * ease_factor
     strength = 1.0
   IF incorrect:
     ease_factor = max(1.3, ease_factor - 0.2)
     interval = 1
     strength = max(0, strength - 0.2)
   next_review = now + interval days
```

---

## 6.6 Gamification Rules

### Achievement System

Achievements are defined with JSON criteria and evaluated by the Gamification Service:

```json
{
  "achievementId": "ach_sharpshooter",
  "name": "Sharpshooter",
  "criteria": {
    "type": "consecutive_perfect_lessons",
    "threshold": 5,
    "scope": "any_course"
  }
}
```

### Achievement Categories & Examples

| Category | Achievement          | Criteria                              | Tier     | Gem Reward |
|----------|---------------------|---------------------------------------|----------|------------|
| Streak   | Wildfire            | 7-day streak                          | Bronze   | 10         |
| Streak   | Wildfire            | 30-day streak                         | Silver   | 50         |
| Streak   | Wildfire            | 100-day streak                        | Gold     | 250        |
| Streak   | Wildfire            | 365-day streak                        | Legendary| 1000       |
| XP       | Scholar             | Earn 100 total XP                     | Bronze   | 5          |
| XP       | Scholar             | Earn 1,000 total XP                   | Silver   | 20         |
| XP       | Scholar             | Earn 10,000 total XP                  | Gold     | 100        |
| Lesson   | Sharpshooter        | 5 perfect lessons in a row            | Silver   | 20         |
| Lesson   | Marathon            | Complete 50 lessons                   | Bronze   | 10         |
| Lesson   | Marathon            | Complete 500 lessons                  | Gold     | 100        |
| Social   | Friendly            | Add 3 friends                         | Bronze   | 5          |
| Social   | Social Butterfly    | Add 20 friends                        | Silver   | 25         |
| League   | Champion            | Finish #1 in any league               | Silver   | 50         |
| League   | Diamond Member      | Reach Diamond league                  | Gold     | 200        |
| Profile  | Photogenic          | Upload a profile photo                | -        | 5          |
| Special  | Weekend Warrior     | Complete lessons on Sat and Sun       | Bronze   | 10         |
| Special  | Night Owl           | Complete a lesson after 10 PM         | -        | 5          |

### Achievement Evaluation

```
Algorithm: EvaluateAchievements(userId, event)
──────────────────────────────────────────────
// Called after relevant events (lesson complete, XP earned, etc.)

1. Fetch all non-earned achievements for the user
2. For each achievement:
   a. Parse criteria from criteria_json
   b. Evaluate based on criteria type:
      - "total_xp": Check user's total XP
      - "streak_days": Check current streak
      - "consecutive_perfect_lessons": Count recent perfect lessons
      - "total_lessons": Count completed lessons
      - "friend_count": Count friends
      - "league_rank": Check leaderboard position
      - "league_tier": Check current league tier
   c. Update progress percentage
   d. IF criteria met:
      - Create user_achievement record
      - Award gem reward
      - Publish "AchievementEarned" event
      - Send push notification
```

---

## 6.7 Reward System

### Gem Economy

Gems are the primary virtual currency. Sources and sinks:

**Gem Sources:**

| Source                    | Amount    | Frequency           |
|---------------------------|-----------|---------------------|
| Lesson completion         | 2 gems    | Per lesson           |
| Daily goal met            | 3 gems    | Daily                |
| Streak milestones         | 5–1000    | Per milestone        |
| Achievement unlock        | 5–200     | Per achievement      |
| Leaderboard top 3         | 10–30     | Weekly               |
| Daily quest completion    | 5 gems    | Daily                |
| Ad watching (free tier)   | 3 gems    | Up to 5/day          |
| Referral bonus            | 50 gems   | Per successful referral|
| Welcome bonus             | 500 gems  | Once                 |

**Gem Sinks:**

| Item                      | Cost      | Notes                |
|---------------------------|-----------|----------------------|
| Streak Freeze             | 200 gems  | Max 2 in inventory   |
| Heart Refill              | 350 gems  | Refills all 5 hearts |
| Double or Nothing wager   | 50 gems   | Win 100 or lose 50   |
| XP Doubler (15 min)       | 200 gems  | 2x XP for 15 min     |
| Timed Challenge entry     | 20 gems   | Optional entry fee    |
| Avatar outfit             | 100–500   | Cosmetic only        |

### Gem Transaction Safety

All gem transactions use database transactions with optimistic locking:

```csharp
public async Task<PurchaseResult> PurchaseItemAsync(
    string userId, string itemId, int quantity)
{
    using var transaction = await _context.Database
        .BeginTransactionAsync(IsolationLevel.RepeatableRead);

    try
    {
        var user = await _context.Users
            .Where(u => u.Id == userId)
            .FirstAsync();

        var item = await _context.ShopItems.FindAsync(itemId);
        var totalCost = item.PriceGems * quantity;

        // Check sufficient balance
        if (user.Gems < totalCost)
            return PurchaseResult.InsufficientGems();

        // Check max ownable
        var owned = await _context.Inventory
            .Where(i => i.UserId == userId && i.ItemId == itemId)
            .Select(i => i.Quantity)
            .FirstOrDefaultAsync();

        if (item.MaxOwnable.HasValue &&
            owned + quantity > item.MaxOwnable.Value)
            return PurchaseResult.MaxOwned();

        // Deduct gems
        user.Gems -= totalCost;

        // Update inventory
        var inventory = await _context.Inventory
            .FirstOrDefaultAsync(i =>
                i.UserId == userId && i.ItemId == itemId);

        if (inventory == null)
        {
            inventory = new Inventory
            {
                UserId = userId, ItemId = itemId, Quantity = quantity
            };
            _context.Inventory.Add(inventory);
        }
        else
        {
            inventory.Quantity += quantity;
        }

        // Record purchase
        _context.Purchases.Add(new Purchase
        {
            UserId = userId,
            ItemId = itemId,
            Quantity = quantity,
            GemsSpent = totalCost
        });

        await _context.SaveChangesAsync();
        await transaction.CommitAsync();

        return PurchaseResult.Success(user.Gems);
    }
    catch
    {
        await transaction.RollbackAsync();
        throw;
    }
}
```

---

## 6.8 Leveling System

### Level Calculation

Levels are derived from total XP across all courses:

```
Algorithm: GetUserLevel(totalXp)
────────────────────────────────
level = 1
remainingXp = totalXp

tiers = [
    { maxLevel: 5,  xpPerLevel: 60  },
    { maxLevel: 10, xpPerLevel: 100 },
    { maxLevel: 15, xpPerLevel: 150 },
    { maxLevel: 20, xpPerLevel: 200 },
    { maxLevel: 25, xpPerLevel: 300 },
    { maxLevel: 30, xpPerLevel: 400 },
]

FOR EACH tier IN tiers:
    levelsInTier = tier.maxLevel - level + 1
    xpForTier = levelsInTier * tier.xpPerLevel

    IF remainingXp < tier.xpPerLevel:
        BREAK  // Not enough for next level

    IF remainingXp < xpForTier:
        levelsEarned = FLOOR(remainingXp / tier.xpPerLevel)
        level += levelsEarned
        remainingXp -= levelsEarned * tier.xpPerLevel
        BREAK

    level = tier.maxLevel + 1
    remainingXp -= xpForTier

// Level 31+
IF remainingXp >= 500:
    level += FLOOR(remainingXp / 500)

RETURN {
    level: level,
    xpInCurrentLevel: remainingXp % xpPerCurrentLevel,
    xpForNextLevel: xpPerCurrentLevel,
    progressPercent: (remainingXp % xpPerCurrentLevel) / xpPerCurrentLevel
}
```

### Level-Up Rewards

| Level | Reward                    |
|-------|---------------------------|
| 5     | 10 gems, Bronze badge     |
| 10    | 25 gems, Silver badge     |
| 15    | 50 gems                   |
| 20    | 100 gems, Gold badge      |
| 25    | 150 gems                  |
| 30    | 250 gems, Diamond badge   |
| 40    | 500 gems                  |
| 50    | 1000 gems, Legendary badge|

---

## 6.9 Hearts / Lives System

### Heart Rules (Free Tier Only)

| Rule                        | Value                                       |
|-----------------------------|---------------------------------------------|
| Maximum hearts              | 5                                           |
| Hearts lost per mistake     | 1                                           |
| Heart regeneration rate     | 1 heart every 4 hours                       |
| Heart refill cost           | 350 gems (restores all 5)                   |
| Practice mode hearts        | Not required (free practice always available)|
| Premium users               | Unlimited (hearts system bypassed)           |

### Heart Regeneration Algorithm

```
Algorithm: GetCurrentHearts(userId)
───────────────────────────────────
1. Fetch user.hearts and user.hearts_refill_at
2. IF user.premium_tier != 'free':
   → Return 999 (unlimited)
3. IF user.hearts == 5:
   → Return 5 (no regeneration needed)
4. Calculate regenerated hearts:
   elapsed = NOW - hearts_refill_at
   regenCount = FLOOR(elapsed / 4 hours)
   currentHearts = MIN(5, user.hearts + regenCount)
5. IF currentHearts changed:
   → Update user.hearts = currentHearts
   → IF currentHearts < 5:
     → Set hearts_refill_at = hearts_refill_at + (regenCount * 4 hours)
   → ELSE:
     → Set hearts_refill_at = NULL
6. Return currentHearts
```

### Heart Loss During Lesson

```
Algorithm: ProcessIncorrectAnswer(userId, sessionId)
───────────────────────────────────────────────────
1. IF user is premium → skip heart deduction, return
2. Get current hearts (with regeneration check)
3. IF hearts > 0:
   → Deduct 1 heart
   → IF hearts was 5 (full) AND hearts_refill_at IS NULL:
     → Set hearts_refill_at = NOW (start regeneration timer)
   → Continue lesson
4. IF hearts == 0:
   → End lesson session (status = 'failed')
   → Return response with options:
     a. Wait for heart regeneration (show timer)
     b. Buy heart refill (350 gems)
     c. Watch an ad (restore 1 heart)
     d. Upgrade to premium (unlimited hearts)
```

---

## 6.10 Monetization Logic

### Free vs. Premium Feature Matrix

| Feature                    | Free Tier      | Super Duolingo | Family Plan    |
|----------------------------|----------------|----------------|----------------|
| Lessons                    | ✓              | ✓              | ✓              |
| Hearts                     | 5 (regenerate) | Unlimited      | Unlimited      |
| Ads                        | Yes            | No             | No             |
| Streak Repair              | No             | Yes            | Yes            |
| Practice Mistakes          | No             | Yes            | Yes            |
| Mastery Quiz               | No             | Yes            | Yes            |
| Progress Quiz              | No             | Yes            | Yes            |
| Offline Learning           | No             | Yes            | Yes            |
| Members                    | 1              | 1              | Up to 6        |
| Monthly Cost               | Free           | $12.99         | $19.99         |

### Subscription State Machine

```
                    ┌──────────┐
           ┌───────│   New    │───────┐
           │       └──────────┘       │
           │                          │
           ▼                          ▼
    ┌──────────┐               ┌──────────┐
    │  Trial   │──────────────►│  Active  │
    │ (14 days)│               │          │
    └────┬─────┘               └─────┬────┘
         │                           │
         │ (no payment)              │ (cancel)
         │                           │
         ▼                           ▼
    ┌──────────┐               ┌──────────┐
    │ Expired  │◄──────────────│Cancelled │
    │          │  (end of      │(active   │
    │          │   billing     │ until    │
    │          │   period)     │ period   │
    └──────────┘               │ ends)    │
         │                     └──────────┘
         │ (re-subscribe)
         │
         ▼
    ┌──────────┐
    │  Active  │
    └──────────┘
```

### Trial Management

```
Algorithm: ManageTrialSubscription(userId)
──────────────────────────────────────────
1. On registration, check if user is eligible for trial:
   - No previous subscription history
   - Not a restored account
2. IF eligible:
   - Create subscription with status = 'trial'
   - Set expires_at = NOW + 14 days
   - Grant premium features immediately
3. At trial expiry:
   - IF user has added payment method:
     → Convert to 'active' subscription
     → Charge payment method
   - IF no payment method:
     → Set status = 'expired'
     → Revert to free tier
     → Send "trial_expired" notification
```

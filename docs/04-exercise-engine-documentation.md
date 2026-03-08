# 4. Exercise Engine Documentation

> Core learning engine powering lesson experiences: exercise types, scoring logic, progression, retry mechanics, and adaptive difficulty.

---

## 4.1 Exercise Types

### 4.1.1 Exercise Type Registry

| Type ID | Name | Input Modality | Output Modality | Difficulty Range |
|---------|------|---------------|-----------------|-----------------|
| `MULTIPLE_CHOICE` | Multiple Choice | Tap | Visual | 1–5 |
| `WORD_BANK` | Word Bank (Sentence Build) | Tap/Drag | Visual | 2–5 |
| `FILL_BLANK` | Fill in the Blank | Tap | Visual | 2–5 |
| `LISTENING` | Listening Comprehension | Type | Audio + Visual | 2–5 |
| `SPEAKING` | Speaking | Voice | Audio | 3–5 |
| `MATCHING` | Match Pairs | Tap | Visual | 1–3 |
| `TRANSLATION_FREE` | Free Translation | Type | Visual | 3–5 |
| `CHARACTER_SELECT` | Character Selection | Tap | Audio + Visual | 1–3 |
| `STORY_CHOICE` | Story Dialogue Choice | Tap | Visual | 2–4 |

### 4.1.2 Multiple Choice

**Purpose:** Test recognition and comprehension of vocabulary and grammar.

```
┌─────────────────────────────────┐
│  Translate this sentence:       │
│                                 │
│  "Le chat est noir"             │
│  🔊 [Play Audio]               │
│                                 │
│  ┌───────────────────────────┐  │
│  │ A) The dog is black       │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ B) The cat is black  ✓   │  │ ← Correct
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ C) The cat is white       │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ D) The bird is black      │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

| Property | Detail |
|----------|--------|
| Prompt Formats | L2→L1 translation, L1→L2 translation, image→word, audio→word |
| Option Count | 3 (easy), 4 (medium/hard) |
| Distractor Generation | Same word class, related meaning, common confusion pairs |
| Audio | Auto-play L2 sentence on load; replay on speaker tap |
| Selection | Single-select; selected option highlighted with border |
| Scoring | Correct first try: full points. Correct on retry: half points |

**State Machine:**

```
Idle → OptionSelected → Submitted → Correct / Incorrect → Transition
```

### 4.1.3 Word Bank (Sentence Construction)

**Purpose:** Test productive sentence formation with scaffolded word choices.

```
┌─────────────────────────────────┐
│  Translate this sentence:       │
│  "The cat is black"             │
│                                 │
│  Answer:                        │
│  ┌─────┐ ┌──────┐ ┌─────┐      │
│  │ Le  │ │ chat │ │ est │ ___  │  ← Answer slots
│  └─────┘ └──────┘ └─────┘      │
│                                 │
│  Word Bank:                     │
│  ┌──────┐ ┌──────┐ ┌─────────┐ │
│  │ noir │ │ bleu │ │ cheval  │ │  ← Available tiles
│  └──────┘ └──────┘ └─────────┘ │
│  ┌──────┐                       │
│  │ vert │                       │
│  └──────┘                       │
│                                 │
│  [Use Keyboard]                 │
└─────────────────────────────────┘
```

| Property | Detail |
|----------|--------|
| Word Count | 5–8 tiles in bank (includes 2–3 distractors) |
| Interaction | Tap tile → animates to next empty answer slot. Tap placed tile → returns to bank |
| Reorder | Drag placed tiles to reorder |
| Keyboard Mode | Toggle to free-text input (full credit if answer matches) |
| Answer Validation | Exact match against accepted answers list (multiple correct orderings possible) |
| Typo Handling | In keyboard mode: Levenshtein distance ≤ 1 accepted with warning |

**Accepted Answers Example:**

```json
{
  "accepted_answers": [
    "Le chat est noir",
    "Le chat est noir."
  ],
  "nearly_correct": [
    "Le chat est noire"  // Gender agreement error → specific feedback
  ]
}
```

### 4.1.4 Fill in the Blank

**Purpose:** Test recall of specific vocabulary in context.

```
┌─────────────────────────────────┐
│  Complete the sentence:         │
│                                 │
│  "El gato es ______"            │
│                                 │
│  ┌─────────┐  ┌─────────┐      │
│  │  negro  │  │  rojo   │      │
│  └─────────┘  └─────────┘      │
│  ┌─────────┐  ┌─────────┐      │
│  │  gato   │  │  grande │      │
│  └─────────┘  └─────────┘      │
└─────────────────────────────────┘
```

| Property | Detail |
|----------|--------|
| Blank Count | 1 (single blank per exercise) |
| Context | Full sentence with one word replaced by underline |
| Options | 3–4 word choices (1 correct, 2–3 distractors) |
| Selection | Tap to fill blank; tap filled blank to clear |
| Hint | After incorrect attempt, first letter of correct answer shown |

### 4.1.5 Listening Comprehension

**Purpose:** Test audio comprehension and L2 spelling.

```
┌─────────────────────────────────┐
│  Type what you hear:            │
│                                 │
│       🔊  [Play]                │
│       🐢  [Slow]                │
│                                 │
│  ┌───────────────────────────┐  │
│  │ _________________________│  │  ← Text input
│  └───────────────────────────┘  │
│                                 │
│  [Can't listen now]             │
└─────────────────────────────────┘
```

| Property | Detail |
|----------|--------|
| Audio | Auto-plays at normal speed on load |
| Speed Controls | Normal speed (1×) and slow speed (0.5×) buttons |
| Input | Free-text input with L2 keyboard layout |
| Validation | Case-insensitive; accent-insensitive (with warning); punctuation optional |
| Typo Tolerance | Levenshtein distance ≤ 1 char per word accepted with "Watch the spelling!" message |
| Skip Option | "Can't listen now" skips without penalty; exercise type disabled for rest of session |

### 4.1.6 Speaking Exercise

**Purpose:** Test pronunciation and speaking confidence.

```
┌─────────────────────────────────┐
│  Say this sentence:             │
│                                 │
│  "Bonjour, comment allez-vous?" │
│                                 │
│       ┌─────────────┐           │
│       │     🎤      │           │  ← Microphone button
│       │   [Tap to   │           │
│       │    speak]   │           │
│       └─────────────┘           │
│                                 │
│  [Can't speak now]              │
└─────────────────────────────────┘
```

| Property | Detail |
|----------|--------|
| Permission | Requires microphone permission; prompt on first use |
| Recording | Tap to start; tap again to stop (or 5-second silence auto-stop) |
| Processing | On-device speech-to-text where available; server-side fallback |
| Scoring | Word-level comparison: correct words highlighted green, missed/incorrect in red |
| Passing Threshold | ≥70% of words recognized correctly |
| Retry | Up to 3 attempts per exercise |
| Skip | "Can't speak now" skips without penalty; disables speaking for session |
| Offline | Uses on-device STT if available; otherwise exercise is skipped |

### 4.1.7 Matching Exercise

**Purpose:** Reinforce vocabulary association through pair matching.

```
┌─────────────────────────────────┐
│  Match the pairs:               │
│                                 │
│  ┌─────────┐    ┌─────────┐    │
│  │  cat    │    │  gato   │    │
│  └─────────┘    └─────────┘    │
│  ┌─────────┐    ┌─────────┐    │
│  │  dog    │    │  perro  │    │
│  └─────────┘    └─────────┘    │
│  ┌─────────┐    ┌─────────┐    │
│  │  house  │    │  casa   │    │
│  └─────────┘    └─────────┘    │
│  ┌─────────┐    ┌─────────┐    │
│  │  water  │    │  agua   │    │
│  └─────────┘    └─────────┘    │
│  ┌─────────┐    ┌─────────┐    │
│  │  tree   │    │  árbol  │    │
│  └─────────┘    └─────────┘    │
└─────────────────────────────────┘
```

| Property | Detail |
|----------|--------|
| Pair Count | 5 pairs (easy), 6 pairs (medium), 8 pairs (hard) |
| Column Layout | L1 words on left, L2 words on right (shuffled independently) |
| Interaction | Tap left tile to select, tap right tile to attempt match |
| Correct Match | Both tiles flash green and animate out (shrink + fade, 300ms) |
| Incorrect Match | Both tiles flash red and shake (300ms); deselect |
| Completion | All pairs matched; scored based on total incorrect attempts |
| Timer | Optional timed variant: 60 seconds for completion |

### 4.1.8 Free Translation

**Purpose:** Test productive translation ability with no scaffolding.

```
┌─────────────────────────────────┐
│  Translate this sentence:       │
│                                 │
│  "The children are playing      │
│   in the park."                 │
│                                 │
│  ┌───────────────────────────┐  │
│  │ _________________________│  │
│  │ _________________________│  │  ← Multi-line text input
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

| Property | Detail |
|----------|--------|
| Input | Multi-line text input with L2 keyboard |
| Validation | Checked against list of accepted translations (typically 3–10 variants) |
| Fuzzy Matching | Normalized comparison: case-insensitive, accent-flexible, punctuation-optional |
| Nearly Correct | Levenshtein distance ≤ 2 per word with specific error feedback |
| Scoring | Full credit for accepted match; partial credit for nearly correct (70%) |

### 4.1.9 Character Selection

**Purpose:** Teach character-based writing systems (Japanese, Korean, Chinese, Arabic, Hindi).

```
┌─────────────────────────────────┐
│  Select the correct character:  │
│                                 │
│  🔊 "ka"                        │
│                                 │
│  ┌─────┐  ┌─────┐  ┌─────┐     │
│  │  あ  │  │  か  │  │  さ  │     │
│  └─────┘  └─────┘  └─────┘     │
│  ┌─────┐  ┌─────┐  ┌─────┐     │
│  │  た  │  │  な  │  │  は  │     │
│  └─────┘  └─────┘  └─────┘     │
│  ┌─────┐  ┌─────┐  ┌─────┐     │
│  │  ま  │  │  や  │  │  ら  │     │
│  └─────┘  └─────┘  └─────┘     │
└─────────────────────────────────┘
```

| Property | Detail |
|----------|--------|
| Audio | Auto-plays romanized pronunciation; replay on tap |
| Options | 6 (easy) or 9 (medium/hard) character tiles |
| Grid | 2×3 or 3×3 grid layout |
| Distractor Selection | Visually similar characters and phonetically similar characters |

---

## 4.2 Scoring Logic

### 4.2.1 Base XP Calculation

```
Base XP per exercise:
  - Correct on first attempt:    10 XP
  - Correct on retry (end of lesson): 5 XP
  - Incorrect:                     0 XP

Lesson XP = Σ(exercise XP) + Combo Bonus + Accuracy Bonus + Streak Bonus
```

### 4.2.2 Combo System

```
Combo multiplier activates after 3 consecutive correct answers:

  Combo Level 1 (3 in a row):    +5 XP bonus
  Combo Level 2 (5 in a row):   +10 XP bonus
  Combo Level 3 (8 in a row):   +15 XP bonus
  Combo Level 4 (12 in a row):  +20 XP bonus
  Combo Level 5 (15+ in a row): +25 XP bonus (max)

Combo resets to 0 on any incorrect answer.
```

### 4.2.3 Accuracy Bonus

```
Lesson accuracy = correct_first_attempt / total_exercises × 100

  100% accuracy: +5 XP "Perfect!" bonus
  90%+ accuracy: +3 XP "Great!" bonus
  80%+ accuracy: +1 XP "Good!" bonus
  <80%:           No bonus
```

### 4.2.4 Streak Bonus

```
Daily streak adds passive XP bonus to every lesson:

  Streak 1–6 days:     +0 XP
  Streak 7–13 days:    +1 XP per lesson
  Streak 14–29 days:   +2 XP per lesson
  Streak 30–89 days:   +3 XP per lesson
  Streak 90–179 days:  +5 XP per lesson
  Streak 180–364 days: +10 XP per lesson
  Streak 365+ days:    +20 XP per lesson
```

### 4.2.5 Power-Up Multipliers

| Power-Up | Effect | Duration | Stacking |
|----------|--------|----------|----------|
| Double XP | 2× all XP earned | 15 minutes | Does not stack with itself |
| Combo Start | Start lesson at combo level 2 | 1 lesson | N/A |

### 4.2.6 XP Calculation Example

```
Scenario: 15-exercise lesson, 13 correct first attempt, 2 wrong (retried and correct)
User has 30-day streak, no power-ups.

Base XP: (13 × 10) + (2 × 5) = 140 XP
Combo Bonus: Longest streak was 8 → Level 3 = +15 XP
Accuracy: 13/15 = 86.7% → +1 XP
Streak Bonus: 30 days → +3 XP

Total: 140 + 15 + 1 + 3 = 159 XP
```

### 4.2.7 Crown Level XP Requirements

| Crown Level | Lessons | XP Range per Level |
|-------------|---------|-------------------|
| Level 1 (Introduced) | 3 lessons | ~45–60 XP |
| Level 2 | 3 lessons | ~45–60 XP |
| Level 3 | 4 lessons | ~60–80 XP |
| Level 4 | 4 lessons | ~60–80 XP |
| Level 5 (Mastered) | 5 lessons | ~75–100 XP |
| Legendary | 4 challenge sessions | ~120–160 XP |

---

## 4.3 Lesson Progression Logic

### 4.3.1 Lesson Structure

```dart
class Lesson {
  final String id;
  final String skillId;
  final int crownLevel;
  final int lessonNumber;
  final List<Exercise> exercises;       // 10-20 exercises
  final List<String> newVocabulary;     // Words introduced in this lesson
  final List<String> reviewVocabulary;  // Words from previous lessons for reinforcement
}
```

### 4.3.2 Exercise Ordering Within a Lesson

Exercises follow a pedagogical progression:

```
Phase 1: Introduction (exercises 1–4)
  - Multiple choice (L2→L1): See new word, recognize meaning
  - Character selection (for character-based languages)
  - Matching pairs: Reinforce new vocabulary

Phase 2: Reinforcement (exercises 5–10)
  - Fill in the blank: Recall in context
  - Word bank: Construct sentences
  - Listening: Hear and identify

Phase 3: Production (exercises 11–15)
  - Free translation: Produce target language
  - Speaking: Pronounce correctly
  - Mixed review of all new + some review vocabulary

Phase 4: Retry Queue (if any)
  - Previously incorrect exercises re-presented
  - Shuffled to avoid position memory
```

### 4.3.3 Exercise Selection Algorithm

```python
def select_exercises(skill, crown_level, lesson_number):
    # Get vocabulary for this lesson
    new_words = skill.get_new_words(lesson_number)
    review_words = skill.get_review_words(lesson_number, count=3)

    exercises = []

    # Phase 1: Introduction (simple recognition)
    for word in new_words:
        exercises.append(generate_multiple_choice(word, difficulty=crown_level))
        if skill.has_characters:
            exercises.append(generate_character_select(word))

    # Phase 2: Reinforcement
    all_words = new_words + review_words
    shuffle(all_words)
    for word in all_words[:5]:
        exercise_type = weighted_random_choice({
            'fill_blank': 0.3,
            'word_bank': 0.3,
            'listening': 0.2,
            'matching': 0.2,
        })
        exercises.append(generate_exercise(exercise_type, word, crown_level))

    # Phase 3: Production
    for word in new_words:
        exercise_type = weighted_random_choice({
            'translation_free': 0.3 if crown_level >= 3 else 0.0,
            'word_bank': 0.3,
            'speaking': 0.2 if crown_level >= 2 else 0.0,
            'listening': 0.2,
        })
        exercises.append(generate_exercise(exercise_type, word, crown_level))

    # Ensure minimum 10, maximum 20 exercises
    exercises = exercises[:20] if len(exercises) > 20 else exercises
    while len(exercises) < 10:
        exercises.append(generate_review_exercise(review_words, crown_level))

    return exercises
```

### 4.3.4 Lesson Completion Criteria

```
A lesson is "complete" when:
  1. All exercises (including retry queue) have been answered correctly
  2. OR the user has answered all original exercises + retry exercises
     (retry exercises that are wrong again are logged but don't block completion)

Maximum retry cycles: 2
  - First cycle: Wrong answers retried once
  - Second cycle: Still-wrong answers retried once more
  - After 2 retry cycles: Lesson completes; unmastered items flagged for next session
```

### 4.3.5 Progress Tracking

```dart
class LessonProgress {
  final String lessonId;
  final int currentExerciseIndex;
  final int totalExercises;
  final int correctCount;
  final int incorrectCount;
  final int livesRemaining;
  final int xpEarned;
  final int comboCount;
  final int maxCombo;
  final List<String> retryExerciseIds;
  final DateTime startedAt;

  double get accuracy => correctCount / (correctCount + incorrectCount);
  bool get isComplete => currentExerciseIndex >= totalExercises && retryExerciseIds.isEmpty;
  double get progressPercentage => currentExerciseIndex / (totalExercises + retryExerciseIds.length);
}
```

---

## 4.4 Retry Logic

### 4.4.1 Immediate Retry Queue

When a user answers an exercise incorrectly:

1. The exercise is marked as incorrect
2. The exercise ID is added to the `retryQueue`
3. The lesson continues with the next exercise
4. After all original exercises are completed, retry exercises are presented

```dart
class RetryManager {
  final List<Exercise> _retryQueue = [];
  int _retryRound = 0;
  static const maxRetryRounds = 2;

  void addToRetry(Exercise exercise) {
    _retryQueue.add(exercise.copyWith(isRetry: true));
  }

  List<Exercise> getRetryExercises() {
    if (_retryRound >= maxRetryRounds) return [];
    _retryRound++;
    final exercises = List<Exercise>.from(_retryQueue);
    _retryQueue.clear();
    exercises.shuffle(); // Randomize order
    return exercises;
  }

  bool get hasRetries => _retryQueue.isNotEmpty && _retryRound < maxRetryRounds;
}
```

### 4.4.2 Retry Exercise Modification

Retry exercises are modified to provide additional scaffolding:

| Original Type | Retry Modification |
|---------------|-------------------|
| Free Translation | Downgrades to Word Bank (adds word tiles) |
| Word Bank | Adds hint: first word pre-filled |
| Fill in the Blank | Reduces options from 4 to 3; correct answer visually highlighted |
| Listening | Plays audio at slow speed by default |
| Speaking | Shows phonetic pronunciation guide |
| Multiple Choice | Eliminates one incorrect option |

### 4.4.3 Spaced Repetition Integration

Incorrect exercises feed into the long-term spaced repetition system:

```dart
class SpacedRepetitionService {
  /// Updates the SRS metadata for a vocabulary item based on exercise outcome
  Future<void> recordOutcome({
    required String wordId,
    required bool correct,
    required Duration responseTime,
  }) async {
    final item = await _repository.getSRSItem(wordId);

    if (correct) {
      // Increase interval using SM-2 algorithm variant
      final newEaseFactor = item.easeFactor + (0.1 - (5 - _qualityScore(responseTime)) * (0.08 + (5 - _qualityScore(responseTime)) * 0.02));
      final newInterval = item.interval * newEaseFactor;
      await _repository.updateSRSItem(
        wordId,
        interval: newInterval.clamp(1.0, 365.0),
        easeFactor: newEaseFactor.clamp(1.3, 2.5),
        nextReview: DateTime.now().add(Duration(days: newInterval.round())),
      );
    } else {
      // Reset interval (word needs re-learning)
      await _repository.updateSRSItem(
        wordId,
        interval: 1.0,
        easeFactor: (item.easeFactor - 0.2).clamp(1.3, 2.5),
        nextReview: DateTime.now().add(const Duration(days: 1)),
      );
    }
  }

  int _qualityScore(Duration responseTime) {
    // Map response time to quality (0-5 scale, SM-2 algorithm)
    if (responseTime < const Duration(seconds: 3)) return 5;  // Instant recall
    if (responseTime < const Duration(seconds: 6)) return 4;  // Quick recall
    if (responseTime < const Duration(seconds: 10)) return 3; // Slow recall
    if (responseTime < const Duration(seconds: 15)) return 2; // Hesitant
    return 1; // Very slow
  }
}
```

### 4.4.4 Practice Mode (Review/Strengthen)

Available when all lessons in a skill are complete:

| Property | Detail |
|----------|--------|
| Exercise Source | SRS algorithm selects weakest items across the skill |
| Exercise Count | 10 exercises (fixed) |
| Lives | Not consumed (practice doesn't use lives) |
| XP | Fixed 10 XP per completed practice session |
| Skill Strength | Restores strength of practiced items (fixes "cracked" skill) |
| Heart Earning | Completing practice earns 1 heart (if below max) |

---

## 4.5 Adaptive Difficulty Rules

### 4.5.1 Difficulty Parameters

Each exercise has a difficulty level (1–5) that controls:

| Parameter | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|-----------|---------|---------|---------|---------|---------|
| Option count (MC) | 3 | 3 | 4 | 4 | 4 |
| Distractor similarity | Low | Medium | High | Very High | Expert |
| Sentence length | 2–4 words | 3–6 words | 5–8 words | 7–12 words | 8–15 words |
| Word bank distractors | 1 | 2 | 3 | 4 | 5 |
| Audio speed | Slow | Normal | Normal | Normal | Fast |
| Typo tolerance | High (≤2) | Medium (≤1) | Low (≤1) | Strict (0) | Strict (0) |
| Hints available | Yes | Yes | Limited | No | No |
| Time pressure | None | None | Gentle | Moderate | Strict |

### 4.5.2 Difficulty Mapping to Crown Levels

| Crown Level | Base Difficulty | Range |
|-------------|----------------|-------|
| Crown 1 | 1 | 1–2 |
| Crown 2 | 2 | 1–3 |
| Crown 3 | 3 | 2–4 |
| Crown 4 | 4 | 3–5 |
| Crown 5 | 4 | 3–5 |
| Legendary | 5 | 4–5 |

### 4.5.3 Within-Lesson Adaptive Adjustment

The difficulty adjusts within a single lesson based on real-time performance:

```python
def adjust_difficulty(current_difficulty, recent_results):
    """
    recent_results: list of last 5 exercise outcomes
    Each outcome: { correct: bool, response_time_ms: int }
    """
    correct_count = sum(1 for r in recent_results if r['correct'])
    avg_response_time = mean(r['response_time_ms'] for r in recent_results)

    # Performance score: 0.0 (struggling) to 1.0 (excelling)
    accuracy_score = correct_count / len(recent_results)
    speed_score = 1.0 - min(avg_response_time / 15000, 1.0)  # 15s = slow
    performance = 0.7 * accuracy_score + 0.3 * speed_score

    if performance >= 0.85:
        # User is excelling: increase difficulty
        return min(current_difficulty + 1, 5)
    elif performance <= 0.4:
        # User is struggling: decrease difficulty
        return max(current_difficulty - 1, 1)
    else:
        # User is in the zone: maintain difficulty
        return current_difficulty
```

### 4.5.4 Exercise Type Distribution by Difficulty

| Difficulty | Recognition (%) | Production (%) | Audio (%) | Speaking (%) |
|------------|-----------------|----------------|-----------|-------------|
| 1 | 60% | 20% | 15% | 5% |
| 2 | 40% | 30% | 20% | 10% |
| 3 | 25% | 35% | 25% | 15% |
| 4 | 15% | 40% | 25% | 20% |
| 5 | 10% | 40% | 25% | 25% |

### 4.5.5 Skill Decay Model

Skills decay over time using a memory model inspired by the Ebbinghaus forgetting curve:

```python
def calculate_strength(last_practiced, initial_strength, ease_factor):
    """
    Returns skill strength from 0.0 (forgotten) to 1.0 (fresh).

    last_practiced: datetime of last practice
    initial_strength: strength after last practice (typically 1.0)
    ease_factor: individual learning factor (1.3 to 2.5)
    """
    days_since = (now() - last_practiced).days
    half_life = ease_factor * 14  # Base half-life of ~14-35 days

    strength = initial_strength * (0.5 ** (days_since / half_life))

    return max(strength, 0.0)

# Thresholds:
# strength >= 0.75: Skill is strong (gold node)
# 0.5 <= strength < 0.75: Skill is weakening (shows subtle indicator)
# strength < 0.5: Skill is cracked (crack overlay, practice nudge)
```

### 4.5.6 Placement Test Adaptive Algorithm

The placement test uses a simplified Item Response Theory (IRT) model:

```python
def placement_test_algorithm():
    """
    Adaptive test that estimates user ability level.
    Uses 3-parameter logistic IRT model.
    """
    ability_estimate = 0.0  # Start at middle
    standard_error = 1.0
    questions_asked = 0

    while standard_error > 0.3 and questions_asked < 25:
        # Select question at estimated ability level
        question = select_question_near_difficulty(ability_estimate)

        # Present question and get response
        is_correct = present_question(question)
        questions_asked += 1

        # Update ability estimate using maximum likelihood
        ability_estimate = update_ability(
            ability_estimate,
            question.difficulty,
            question.discrimination,
            question.guessing_parameter,
            is_correct
        )

        # Update standard error
        standard_error = calculate_standard_error(
            ability_estimate, questions_asked
        )

    # Map ability estimate to skill tree position
    skills_to_unlock = map_ability_to_skills(ability_estimate)
    cefr_level = map_ability_to_cefr(ability_estimate)

    return PlacementResult(
        ability=ability_estimate,
        cefr_level=cefr_level,
        skills_unlocked=skills_to_unlock,
        questions_answered=questions_asked,
    )
```

### 4.5.7 Anti-Gaming Measures

| Measure | Implementation |
|---------|---------------|
| Answer Pattern Detection | If user answers all exercises in <1 second each, flag for review |
| Random Option Ordering | Multiple choice options shuffled every presentation |
| Varied Retry | Retry exercises use different distractor sets |
| IP/Device Rate Limiting | Max 1,000 XP per day per device (detect bots) |
| Time-Based Validation | Exercise responses with <500ms response time are logged but not counted for adaptive difficulty |

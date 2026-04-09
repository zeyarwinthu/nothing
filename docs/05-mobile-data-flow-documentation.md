# 5. Mobile Data Flow Documentation

> End-to-end data architecture: how data moves between UI, BLoC, repositories, API, and local storage. Syncing logic, error handling, and background refresh patterns.

---

## 5.1 Data Flow Architecture

### 5.1.1 Architectural Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         UI Layer                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │
│  │ Screen     │  │ Screen     │  │ Screen     │                 │
│  │ Widget     │  │ Widget     │  │ Widget     │                 │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘                 │
│        │               │               │                         │
│  ┌─────▼───────────────▼───────────────▼──────┐                  │
│  │              BLoC Layer                     │                  │
│  │  Events → Business Logic → States          │                  │
│  └─────────────────┬──────────────────────────┘                  │
│                    │                                              │
│  ┌─────────────────▼──────────────────────────┐                  │
│  │           Repository Layer                  │                  │
│  │  ┌──────────────────┐  ┌────────────────┐  │                  │
│  │  │ Remote DataSource │  │ Local DataSource│  │                  │
│  │  └────────┬─────────┘  └───────┬────────┘  │                  │
│  └───────────┼────────────────────┼────────────┘                  │
│              │                    │                                │
└──────────────┼────────────────────┼────────────────────────────────┘
               │                    │
        ┌──────▼──────┐     ┌──────▼──────┐
        │   REST API  │     │  Local DB   │
        │   Server    │     │  (Hive)     │
        └─────────────┘     └─────────────┘
```

### 5.1.2 Unidirectional Data Flow

```
User Action
    │
    ▼
UI dispatches Event to BLoC
    │
    ▼
BLoC processes Event
    │
    ├── Calls Use Case / Repository method
    │       │
    │       ├── Check connectivity
    │       │       │
    │       │       ├── Online: Call Remote DataSource → Cache result in Local DataSource
    │       │       │
    │       │       └── Offline: Read from Local DataSource → Queue action if write operation
    │       │
    │       └── Return Result<T> (Success or Failure)
    │
    ▼
BLoC emits new State
    │
    ▼
UI rebuilds with new State
```

### 5.1.3 Data Flow by Operation Type

#### Read Operations (GET)

```
Strategy: Cache-First with Background Refresh

1. BLoC requests data from Repository
2. Repository checks Local DataSource for cached data
3a. Cache HIT + not expired:
    → Return cached data immediately
    → Optionally trigger background refresh
3b. Cache HIT + expired:
    → Return cached data immediately (stale)
    → Trigger foreground API call
    → Update cache and emit new state with fresh data
3c. Cache MISS:
    → Show loading state
    → Call Remote DataSource
    → Cache response in Local DataSource
    → Return fresh data
```

#### Write Operations (POST/PUT/DELETE)

```
Strategy: Optimistic Update with Sync Queue

1. BLoC requests write from Repository
2. Repository applies change to Local DataSource immediately (optimistic)
3. BLoC emits success state (UI updates immediately)
4a. Online:
    → Repository sends request to Remote DataSource
    → Success: Confirm optimistic update; update cache with server response
    → Failure: Revert optimistic update; emit error state; add to retry queue
4b. Offline:
    → Repository adds operation to SyncQueue
    → When online: SyncQueue processes pending operations (§5.2)
```

### 5.1.4 Detailed Flow Examples

#### Lesson Completion Flow

```
User taps "Check" on final exercise
    │
    ▼
ExerciseBloc.add(AnswerSubmitted(answer))
    │
    ▼
ExerciseBloc._onAnswerSubmitted:
    │
    ├── Validate answer (correct/incorrect)
    ├── Update local progress: xp, accuracy, combo
    ├── If incorrect: add to retry queue
    │
    ├── If lesson complete:
    │     │
    │     ▼
    │   LessonBloc.add(LessonCompleted(result))
    │     │
    │     ▼
    │   LessonBloc._onLessonCompleted:
    │     │
    │     ├── Update local progress DB
    │     │     └── progressBox.put(skillId, updatedProgress)
    │     │
    │     ├── Update local XP
    │     │     └── userBox.put('xp', currentXP + earnedXP)
    │     │
    │     ├── Check daily goal completion
    │     │     └── If met: update streak, emit DailyGoalMet
    │     │
    │     ├── Submit to API (if online)
    │     │     POST /lessons/complete
    │     │     Body: { lesson_id, skill_id, xp_earned, accuracy,
    │     │             duration_seconds, exercises: [...] }
    │     │
    │     ├── If offline: queue submission
    │     │     └── syncQueueBox.add(SyncAction.lessonComplete(result))
    │     │
    │     └── Emit LessonCompleteState(result)
    │           │
    │           ▼
    │         LessonCompleteScreen displays results
    │
    └── Else: emit next ExerciseState
```

#### Streak Update Flow

```
App opens / Daily goal met
    │
    ▼
StreakBloc.add(CheckStreak())
    │
    ▼
StreakBloc._onCheckStreak:
    │
    ├── Read local streak data
    │     └── streakBox.get('current_streak')
    │
    ├── Calculate streak status:
    │     │
    │     ├── Today's XP >= daily goal?
    │     │     Yes → Streak maintained/extended
    │     │     No  → Check if midnight passed without goal
    │     │             Yes → Check streak freeze
    │     │                     Has freeze → Use freeze, maintain streak
    │     │                     No freeze  → Streak broken
    │     │             No  → Streak still active (day not over)
    │     │
    │     └── Update local streak data
    │
    ├── Sync with server (if online):
    │     GET /users/me/streak
    │     Compare: server streak vs. local streak
    │     Resolution: Take higher streak count (favor user)
    │
    └── Emit StreakState(days, isActive, freezeCount)
```

---

## 5.2 Syncing Logic

### 5.2.1 Sync Queue Architecture

```dart
@HiveType(typeId: 10)
class SyncAction extends HiveObject {
  @HiveField(0)
  final String id;            // UUID

  @HiveField(1)
  final SyncActionType type;  // enum: lessonComplete, xpUpdate, streakUpdate, progressUpdate, profileUpdate

  @HiveField(2)
  final String endpoint;      // API endpoint

  @HiveField(3)
  final String method;        // POST, PUT, DELETE

  @HiveField(4)
  final Map<String, dynamic> payload;

  @HiveField(5)
  final DateTime createdAt;

  @HiveField(6)
  final int retryCount;       // Number of failed attempts

  @HiveField(7)
  final DateTime? lastAttempt;

  @HiveField(8)
  final SyncStatus status;    // pending, inProgress, completed, failed
}
```

### 5.2.2 Sync Manager

```dart
class SyncManager {
  final Box<SyncAction> _syncQueue;
  final ApiClient _apiClient;
  final ConnectivityService _connectivity;
  bool _isSyncing = false;

  /// Start sync process when connectivity is restored
  Future<void> sync() async {
    if (_isSyncing) return;
    if (!await _connectivity.isConnected) return;

    _isSyncing = true;

    try {
      // Phase 1: Refresh auth token
      await _refreshTokenIfNeeded();

      // Phase 2: Process sync queue (FIFO)
      final pendingActions = _syncQueue.values
          .where((a) => a.status == SyncStatus.pending)
          .toList()
        ..sort((a, b) => a.createdAt.compareTo(b.createdAt));

      for (final action in pendingActions) {
        await _processAction(action);
      }

      // Phase 3: Pull latest data from server
      await _pullLatestData();

    } finally {
      _isSyncing = false;
    }
  }

  Future<void> _processAction(SyncAction action) async {
    try {
      action.status = SyncStatus.inProgress;
      await action.save();

      final response = await _apiClient.request(
        action.endpoint,
        method: action.method,
        data: action.payload,
      );

      action.status = SyncStatus.completed;
      await action.save();

      // Clean up completed actions
      await action.delete();

    } on ApiException catch (e) {
      action.retryCount++;
      action.lastAttempt = DateTime.now();

      if (action.retryCount >= 5 || e.isClientError) {
        // Permanent failure: log and remove
        action.status = SyncStatus.failed;
        await _logSyncFailure(action, e);
        await action.delete();
      } else {
        // Transient failure: retry later
        action.status = SyncStatus.pending;
      }
      await action.save();
    }
  }

  Future<void> _pullLatestData() async {
    // Pull in priority order
    await Future.wait([
      _pullUserProfile(),
      _pullCourseProgress(),
      _pullLeaderboard(),
      _pullStreakData(),
    ]);
  }
}
```

### 5.2.3 Conflict Resolution Rules

| Data Type | Conflict Scenario | Resolution Strategy |
|-----------|-------------------|---------------------|
| Lesson Progress | Completed offline and online with different results | Server wins for timestamp; client wins for XP (credit user) |
| XP Total | Local XP differs from server | Take maximum (always favor user) |
| Streak | Local says active, server says broken | Server wins if server has proof of inactivity; otherwise local wins |
| User Profile | Edited offline | Client wins (last-write-wins with client timestamp) |
| Skill Tree State | Skills unlocked differently | Union of unlocked skills (merge both) |
| Leaderboard | Cached rank differs from server | Server wins (authoritative) |
| Shop Balance | Gems count differs | Server wins (authoritative for currency) |
| Settings | Changed offline | Client wins (user intent) |

### 5.2.4 Sync Triggers

| Trigger | Sync Type | Priority |
|---------|-----------|----------|
| App launch (foreground) | Full sync | High |
| Network restored (was offline) | Queue processing + selective pull | High |
| Lesson completed | Immediate push (or queue if offline) | Critical |
| XP earned | Batch push (every 5 minutes) | Medium |
| Pull-to-refresh | Selective pull for current screen | Medium |
| Background fetch (iOS) | Lightweight sync (streak, XP) | Low |
| Timer (every 15 minutes while app is active) | Heartbeat sync | Low |

### 5.2.5 Sync Status Indicators

| State | UI Indicator |
|-------|-------------|
| Syncing | Subtle rotating arrow icon in top bar |
| Sync complete | Brief checkmark animation (300ms, then fade) |
| Sync failed | Yellow warning icon; tap shows retry option |
| Offline + pending | Cloud with up-arrow icon; badge count of pending actions |

---

## 5.3 Error Handling

### 5.3.1 Error Classification

```dart
sealed class AppError {
  String get userMessage;
  bool get isRetryable;
}

class NetworkError extends AppError {
  final String userMessage = 'No internet connection';
  final bool isRetryable = true;
}

class TimeoutError extends AppError {
  final String userMessage = 'Request timed out. Please try again.';
  final bool isRetryable = true;
}

class ServerError extends AppError {
  final int statusCode;
  final String userMessage = 'Something went wrong. Please try again later.';
  final bool isRetryable = true; // For 5xx errors
}

class ClientError extends AppError {
  final int statusCode;
  final String serverMessage;
  final String userMessage; // Mapped from server error code
  final bool isRetryable = false; // For 4xx errors
}

class AuthError extends AppError {
  final String userMessage = 'Your session has expired. Please log in again.';
  final bool isRetryable = false;
}

class ValidationError extends AppError {
  final Map<String, String> fieldErrors;
  final String userMessage = 'Please check your input.';
  final bool isRetryable = false;
}

class CacheError extends AppError {
  final String userMessage = 'Unable to load cached data.';
  final bool isRetryable = false;
}
```

### 5.3.2 Error Handling by Layer

#### Repository Layer

```dart
class RepositoryErrorHandler {
  Future<Result<T>> safeApiCall<T>(Future<T> Function() apiCall) async {
    try {
      final result = await apiCall();
      return Result.success(result);
    } on DioException catch (e) {
      switch (e.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.receiveTimeout:
        case DioExceptionType.sendTimeout:
          return Result.failure(TimeoutError());
        case DioExceptionType.connectionError:
          return Result.failure(NetworkError());
        case DioExceptionType.badResponse:
          return _handleHttpError(e.response!);
        default:
          return Result.failure(ServerError(statusCode: 0));
      }
    } on HiveError catch (e) {
      return Result.failure(CacheError());
    } catch (e) {
      return Result.failure(ServerError(statusCode: 0));
    }
  }

  Result<T> _handleHttpError<T>(Response response) {
    final statusCode = response.statusCode!;
    if (statusCode == 401) return Result.failure(AuthError());
    if (statusCode == 422) {
      final errors = _parseValidationErrors(response.data);
      return Result.failure(ValidationError(fieldErrors: errors));
    }
    if (statusCode >= 400 && statusCode < 500) {
      return Result.failure(ClientError(
        statusCode: statusCode,
        serverMessage: response.data['message'] ?? 'Unknown error',
        userMessage: _mapServerError(response.data['code']),
      ));
    }
    return Result.failure(ServerError(statusCode: statusCode));
  }
}
```

#### BLoC Layer

```dart
// BLoC error handling pattern
class LessonBloc extends Bloc<LessonEvent, LessonState> {
  Future<void> _onLessonStarted(LessonStarted event, Emitter<LessonState> emit) async {
    emit(const LessonState.loading());

    final result = await _getLessonUseCase(event.skillId);

    result.when(
      success: (lesson) {
        emit(LessonState.exerciseActive(
          exercise: lesson.exercises.first,
          currentIndex: 0,
          totalExercises: lesson.exercises.length,
          lives: _userLives,
          xpEarned: 0,
          retryQueue: [],
        ));
      },
      failure: (error) {
        if (error is NetworkError) {
          // Try loading cached lesson
          _tryLoadCachedLesson(event.skillId, emit);
        } else {
          emit(LessonState.error(message: error.userMessage));
        }
      },
    );
  }
}
```

#### UI Layer

```dart
// UI error handling pattern
BlocConsumer<LessonBloc, LessonState>(
  listener: (context, state) {
    if (state is LessonError) {
      if (state.error.isRetryable) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(state.error.userMessage),
            action: SnackBarAction(
              label: 'Retry',
              onPressed: () => context.read<LessonBloc>().add(const LessonEvent.retry()),
            ),
          ),
        );
      } else {
        showDialog(
          context: context,
          builder: (_) => ErrorDialog(
            message: state.error.userMessage,
            onDismiss: () => Navigator.pop(context),
          ),
        );
      }
    }
  },
  builder: (context, state) => state.when(
    loading: () => const LoadingWidget(),
    exerciseActive: (exercise, ...) => ExerciseWidget(exercise: exercise),
    error: (message) => ErrorWidget(message: message, onRetry: () { /* ... */ }),
    // ...other states
  ),
);
```

### 5.3.3 Retry Strategy

| Error Type | Retry Strategy | Max Retries | Backoff |
|-----------|---------------|-------------|---------|
| Network error | Auto-retry on reconnect | 3 | Exponential (2s, 4s, 8s) |
| Timeout | Auto-retry | 2 | Linear (5s, 10s) |
| Server error (5xx) | Auto-retry | 3 | Exponential (2s, 4s, 8s) |
| Client error (4xx) | No auto-retry | 0 | N/A |
| Auth error (401) | Token refresh + retry | 1 | Immediate |
| Rate limit (429) | Auto-retry after Retry-After header | 1 | Per Retry-After header |

### 5.3.4 Graceful Degradation

| Failure | Degraded Experience |
|---------|-------------------|
| User profile API fails | Show cached profile; disable edit |
| Leaderboard API fails | Show cached leaderboard with "Last updated X minutes ago" |
| Lesson fetch fails (cached available) | Use cached lesson; mark as offline |
| Lesson fetch fails (no cache) | Show error with retry; suggest offline download |
| Audio CDN fails | Skip audio; show text-only with "Audio unavailable" label |
| Image CDN fails | Show placeholder with retry |
| Push notification registration fails | Silent retry on next app launch |
| Analytics fails | Silent failure; events queued for next batch |

---

## 5.4 Background Refresh

### 5.4.1 iOS Background Fetch

```dart
class BackgroundFetchService {
  static const fetchInterval = Duration(hours: 1);

  Future<void> initialize() async {
    // Configure background fetch
    await Workmanager().initialize(callbackDispatcher);

    // Register periodic task
    await Workmanager().registerPeriodicTask(
      'com.app.backgroundSync',
      'backgroundSync',
      frequency: fetchInterval,
      constraints: Constraints(
        networkType: NetworkType.connected,
        requiresBatteryNotLow: true,
      ),
    );

    // Register one-off task for content pre-download
    await Workmanager().registerOneOffTask(
      'com.app.contentPreload',
      'contentPreload',
      constraints: Constraints(
        networkType: NetworkType.unmetered, // WiFi only
        requiresBatteryNotLow: true,
        requiresCharging: false,
      ),
    );
  }
}

@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    switch (task) {
      case 'backgroundSync':
        return await _performBackgroundSync();
      case 'contentPreload':
        return await _performContentPreload();
      default:
        return false;
    }
  });
}

Future<bool> _performBackgroundSync() async {
  try {
    // Lightweight sync operations only
    await _syncStreak();
    await _syncXP();
    await _processOfflineQueue();
    await _checkForNewContent();
    return true;
  } catch (e) {
    return false;
  }
}

Future<bool> _performContentPreload() async {
  try {
    // Download next 3 lessons for current skill
    await _preDownloadManager.preDownloadLessons(count: 3);
    return true;
  } catch (e) {
    return false;
  }
}
```

### 5.4.2 Silent Push Notification Refresh

```dart
class SilentPushHandler {
  /// Handles data-only push notifications for background data refresh
  Future<void> handleDataMessage(RemoteMessage message) async {
    final type = message.data['type'];

    switch (type) {
      case 'content_update':
        // New lesson content available
        await _courseRepository.refreshCourseStructure();
        break;
      case 'streak_reminder':
        // Update streak status
        await _streakRepository.refreshStreak();
        // Schedule local notification if goal not met
        if (!await _hasMetDailyGoal()) {
          await _scheduleStreakReminder();
        }
        break;
      case 'leaderboard_update':
        // Refresh leaderboard data
        await _leaderboardRepository.refreshLeaderboard();
        break;
      case 'friend_activity':
        // Update friend activity feed
        await _socialRepository.refreshFriendActivity();
        break;
    }
  }
}
```

### 5.4.3 Token Refresh Strategy

```dart
class TokenRefreshService {
  static const tokenRefreshThreshold = Duration(minutes: 2);

  /// Proactively refresh token if it expires soon
  Future<void> checkAndRefreshToken() async {
    final accessToken = await _secureStorage.getAccessToken();
    if (accessToken == null) return;

    final payload = _decodeJWT(accessToken);
    final expiry = DateTime.fromMillisecondsSinceEpoch(payload['exp'] * 1000);
    final timeUntilExpiry = expiry.difference(DateTime.now());

    if (timeUntilExpiry < tokenRefreshThreshold) {
      await _refreshToken();
    }
  }

  /// Called periodically (every 5 minutes) while app is active
  void startPeriodicRefresh() {
    Timer.periodic(const Duration(minutes: 5), (_) {
      checkAndRefreshToken();
    });
  }
}
```

### 5.4.4 Data Freshness Requirements

| Data Type | Max Stale Time | Refresh Trigger |
|-----------|---------------|-----------------|
| User profile | 1 hour | App launch, profile view |
| Streak data | 5 minutes | App launch, lesson complete, timer |
| Daily goal progress | Real-time (local) | Every XP change |
| Skill tree | 24 hours | App launch, pull-to-refresh |
| Leaderboard | 5 minutes | Tab view, pull-to-refresh, timer |
| Shop items | 1 hour | Tab view, pull-to-refresh |
| Notifications | 15 minutes | App launch, pull-to-refresh, push |
| Friend activity | 30 minutes | Profile view, pull-to-refresh |

### 5.4.5 Battery Optimization

| Strategy | Implementation |
|----------|---------------|
| Batch network calls | Group multiple API calls per sync cycle instead of individual calls |
| Respect battery level | Skip non-critical background work when battery < 15% |
| WiFi preference | Large downloads (audio, images) only on WiFi by default |
| Exponential backoff | Increase sync interval after repeated failures |
| Debounce writes | Batch XP updates (every 5 minutes) instead of per-exercise |
| Suspend on low memory | Reduce cache size and pause pre-downloads on memory pressure |

# 3. Mobile Technical Specification

> Architecture, framework decisions, and implementation details for the Flutter-based Duolingo-style learning platform.

---

## 3.1 Framework & Tooling

### 3.1.1 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Flutter | 3.24+ (stable channel) |
| Language | Dart | 3.5+ |
| Minimum iOS | 15.0 | |
| Minimum Android | API 24 (Android 7.0) | |
| IDE | Android Studio / VS Code | |
| CI/CD | GitHub Actions + Fastlane | |
| Code Generation | `build_runner`, `freezed`, `json_serializable` | |
| Linting | `flutter_lints` (strict) + custom rules | |
| Testing | `flutter_test`, `mockito`, `bloc_test`, `integration_test` | |

### 3.1.2 Project Structure

```
lib/
├── app/
│   ├── app.dart                    # MaterialApp / CupertinoApp root
│   ├── router.dart                 # GoRouter configuration
│   └── theme/
│       ├── app_theme.dart          # ThemeData definitions
│       ├── colors.dart             # Brand color constants
│       ├── typography.dart         # Text styles
│       └── dimensions.dart         # Spacing, sizing constants
├── core/
│   ├── di/
│   │   └── injection.dart          # GetIt service locator setup
│   ├── network/
│   │   ├── api_client.dart         # Dio HTTP client
│   │   ├── interceptors/
│   │   │   ├── auth_interceptor.dart
│   │   │   ├── retry_interceptor.dart
│   │   │   └── logging_interceptor.dart
│   │   └── api_exception.dart      # Custom exception types
│   ├── storage/
│   │   ├── secure_storage.dart     # FlutterSecureStorage wrapper
│   │   ├── local_db.dart           # Hive / Isar database
│   │   └── preferences.dart        # SharedPreferences wrapper
│   ├── utils/
│   │   ├── extensions.dart
│   │   ├── validators.dart
│   │   └── date_utils.dart
│   └── constants/
│       ├── api_endpoints.dart
│       └── storage_keys.dart
├── features/
│   ├── auth/
│   │   ├── data/
│   │   │   ├── models/              # Freezed data classes
│   │   │   ├── repositories/        # Repository implementations
│   │   │   └── datasources/         # Remote + local data sources
│   │   ├── domain/
│   │   │   ├── entities/            # Domain entities
│   │   │   ├── repositories/        # Repository interfaces
│   │   │   └── usecases/            # Use case classes
│   │   └── presentation/
│   │       ├── bloc/                # BLoC classes + events + states
│   │       ├── screens/             # Screen widgets
│   │       └── widgets/             # Feature-specific widgets
│   ├── onboarding/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   ├── home/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   ├── lesson/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   ├── exercise/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   │       ├── bloc/
│   │       │   ├── exercise_bloc.dart
│   │       │   ├── exercise_event.dart
│   │       │   └── exercise_state.dart
│   │       ├── screens/
│   │       │   └── exercise_screen.dart
│   │       └── widgets/
│   │           ├── multiple_choice_widget.dart
│   │           ├── word_bank_widget.dart
│   │           ├── fill_blank_widget.dart
│   │           ├── listening_widget.dart
│   │           ├── speaking_widget.dart
│   │           └── matching_widget.dart
│   ├── leaderboard/
│   ├── shop/
│   ├── profile/
│   ├── notifications/
│   └── settings/
├── shared/
│   ├── widgets/
│   │   ├── app_button.dart
│   │   ├── app_text_field.dart
│   │   ├── loading_indicator.dart
│   │   ├── error_widget.dart
│   │   ├── empty_state.dart
│   │   ├── progress_bar.dart
│   │   └── celebration_overlay.dart
│   ├── animations/
│   │   ├── confetti_animation.dart
│   │   ├── particle_system.dart
│   │   └── spring_animation.dart
│   └── models/
│       ├── paginated_response.dart
│       └── result.dart             # Result<T> type (Success/Failure)
└── main.dart
```

### 3.1.3 CI/CD Pipeline

```yaml
# .github/workflows/ci.yaml
name: CI
on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24.0'
          channel: 'stable'
      - run: flutter pub get
      - run: dart analyze --fatal-infos
      - run: dart format --set-exit-if-changed .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
      - run: flutter pub get
      - run: flutter test --coverage
      - uses: codecov/codecov-action@v4

  build-android:
    needs: [analyze, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
      - run: flutter build apk --release

  build-ios:
    needs: [analyze, test]
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
      - run: flutter build ios --release --no-codesign
```

### 3.1.4 Build Flavors

| Flavor | API Base URL | Features |
|--------|-------------|----------|
| `dev` | `https://api-dev.example.com/v1` | Debug logging, mock payments, test ads |
| `staging` | `https://api-staging.example.com/v1` | Production-like, sandbox payments |
| `production` | `https://api.example.com/v1` | Full features, real payments, real ads |

---

## 3.2 State Management

### 3.2.1 Architecture Pattern

The app uses **BLoC (Business Logic Component)** as the primary state management pattern, implemented with the `flutter_bloc` package. This provides:

- Clear separation of UI and business logic
- Testable business logic via event/state streams
- Predictable state transitions
- Easy debugging with `BlocObserver`

### 3.2.2 BLoC Structure

Each feature follows this BLoC pattern:

```dart
// events
@freezed
class LessonEvent with _$LessonEvent {
  const factory LessonEvent.started({required String skillId}) = LessonStarted;
  const factory LessonEvent.answerSubmitted({required Answer answer}) = AnswerSubmitted;
  const factory LessonEvent.nextExercise() = NextExercise;
  const factory LessonEvent.lessonExited() = LessonExited;
}

// states
@freezed
class LessonState with _$LessonState {
  const factory LessonState.initial() = LessonInitial;
  const factory LessonState.loading() = LessonLoading;
  const factory LessonState.exerciseActive({
    required Exercise exercise,
    required int currentIndex,
    required int totalExercises,
    required int lives,
    required int xpEarned,
    required List<Exercise> retryQueue,
  }) = ExerciseActive;
  const factory LessonState.answerResult({
    required bool isCorrect,
    required String? correctAnswer,
    required int xpDelta,
    required int livesRemaining,
  }) = AnswerResult;
  const factory LessonState.outOfLives({
    required int gemsBalance,
    required Duration nextHeartIn,
  }) = OutOfLives;
  const factory LessonState.completed({
    required LessonResult result,
  }) = LessonCompleted;
  const factory LessonState.error({required String message}) = LessonError;
}
```

### 3.2.3 BLoC Hierarchy

```
AppBloc (global)
├── AuthBloc (global — manages auth state)
├── UserBloc (global — user profile & preferences)
├── ConnectivityBloc (global — network state)
├── NotificationBloc (global — in-app notifications)
│
├── HomeBloc (scoped to Home tab)
│   ├── SkillTreeBloc (scoped to skill tree widget)
│   └── DailyGoalBloc (scoped to daily goal widget)
│
├── LessonBloc (scoped to lesson flow)
│   └── ExerciseBloc (scoped to individual exercise)
│
├── LeaderboardBloc (scoped to Leaderboard tab)
├── ShopBloc (scoped to Shop tab)
├── ProfileBloc (scoped to Profile tab)
└── SettingsBloc (scoped to Settings screen)
```

### 3.2.4 State Persistence

| State | Persistence | Storage |
|-------|------------|---------|
| Auth tokens | Persistent | `FlutterSecureStorage` |
| User profile | Persistent + cache | Local DB (Hive) + API |
| Course progress | Persistent + sync | Local DB + API |
| Lesson in-progress | Session only | In-memory (BLoC) |
| Exercise answers | Session only | In-memory |
| Offline action queue | Persistent | Local DB |
| Settings/preferences | Persistent | `SharedPreferences` |
| Onboarding state | Persistent | `SharedPreferences` |
| Cache metadata | Persistent | Local DB |

### 3.2.5 Global State Provider Setup

```dart
// main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await configureDependencies(); // GetIt setup

  runApp(
    MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => getIt<AuthBloc>()..add(const AuthEvent.checkStatus())),
        BlocProvider(create: (_) => getIt<UserBloc>()),
        BlocProvider(create: (_) => getIt<ConnectivityBloc>()..add(const ConnectivityEvent.monitor())),
        BlocProvider(create: (_) => getIt<NotificationBloc>()),
      ],
      child: const App(),
    ),
  );
}
```

---

## 3.3 API Integration

### 3.3.1 HTTP Client Configuration

```dart
// core/network/api_client.dart
class ApiClient {
  late final Dio _dio;

  ApiClient({
    required String baseUrl,
    required AuthInterceptor authInterceptor,
    required RetryInterceptor retryInterceptor,
    required LoggingInterceptor loggingInterceptor,
  }) {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 10),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-App-Version': AppConfig.version,
        'X-Platform': Platform.isIOS ? 'ios' : 'android',
        'X-Device-Id': AppConfig.deviceId,
      },
    ))
      ..interceptors.addAll([
        authInterceptor,
        retryInterceptor,
        loggingInterceptor,
      ]);
  }
}
```

### 3.3.2 Auth Interceptor

```dart
class AuthInterceptor extends Interceptor {
  final SecureStorage _storage;
  final Dio _tokenRefreshDio; // Separate Dio instance to avoid interceptor loop
  final _refreshLock = Lock();

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _storage.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Queue concurrent requests; only one refresh at a time
      await _refreshLock.synchronized(() async {
        final newToken = await _refreshToken();
        if (newToken != null) {
          err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
          final response = await _tokenRefreshDio.fetch(err.requestOptions);
          handler.resolve(response);
          return;
        }
      });
      handler.reject(err); // Refresh failed; propagate 401
    } else {
      handler.next(err);
    }
  }

  Future<String?> _refreshToken() async {
    final refreshToken = await _storage.getRefreshToken();
    if (refreshToken == null) return null;

    try {
      final response = await _tokenRefreshDio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });
      final newAccessToken = response.data['access_token'];
      final newRefreshToken = response.data['refresh_token'];
      await _storage.saveTokens(newAccessToken, newRefreshToken);
      return newAccessToken;
    } catch (_) {
      await _storage.clearTokens();
      return null;
    }
  }
}
```

### 3.3.3 Retry Interceptor

```dart
class RetryInterceptor extends Interceptor {
  static const maxRetries = 3;
  static const retryableStatusCodes = [408, 429, 500, 502, 503, 504];

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    final statusCode = err.response?.statusCode;
    if (statusCode != null && retryableStatusCodes.contains(statusCode)) {
      for (var attempt = 1; attempt <= maxRetries; attempt++) {
        final delay = Duration(seconds: math.pow(2, attempt).toInt()); // 2s, 4s, 8s
        await Future.delayed(delay);

        try {
          final response = await Dio().fetch(err.requestOptions);
          handler.resolve(response);
          return;
        } catch (retryErr) {
          if (attempt == maxRetries) {
            handler.reject(err);
            return;
          }
        }
      }
    }
    handler.next(err);
  }
}
```

### 3.3.4 Repository Pattern

```dart
// Abstract repository interface (domain layer)
abstract class LessonRepository {
  Future<Result<Lesson>> getLesson(String skillId, int crownLevel);
  Future<Result<LessonResult>> submitLessonResult(LessonSubmission submission);
  Future<Result<List<Exercise>>> getExercises(String lessonId);
}

// Concrete implementation (data layer)
class LessonRepositoryImpl implements LessonRepository {
  final LessonRemoteDataSource _remote;
  final LessonLocalDataSource _local;
  final ConnectivityService _connectivity;

  @override
  Future<Result<Lesson>> getLesson(String skillId, int crownLevel) async {
    if (await _connectivity.isConnected) {
      try {
        final lesson = await _remote.getLesson(skillId, crownLevel);
        await _local.cacheLesson(lesson);
        return Result.success(lesson);
      } on ApiException catch (e) {
        // Try local cache on API failure
        final cached = await _local.getCachedLesson(skillId, crownLevel);
        if (cached != null) return Result.success(cached);
        return Result.failure(e.message);
      }
    } else {
      final cached = await _local.getCachedLesson(skillId, crownLevel);
      if (cached != null) return Result.success(cached);
      return Result.failure('No internet connection and no cached lesson available');
    }
  }
}
```

---

## 3.4 Local Storage Strategy

### 3.4.1 Storage Technologies

| Technology | Use Case | Data |
|-----------|----------|------|
| `FlutterSecureStorage` | Sensitive data | Auth tokens, user credentials |
| `Hive` (NoSQL) | Structured data with fast read | Course data, lessons, exercises, user progress, offline queue |
| `SharedPreferences` | Simple key-value | Settings, flags, onboarding state, last sync timestamp |
| File System (`path_provider`) | Binary files | Cached audio, images, downloaded content |

### 3.4.2 Hive Box Schema

```dart
// Hive boxes
const String userBox = 'user_box';
const String courseBox = 'course_box';
const String lessonBox = 'lesson_box';
const String exerciseBox = 'exercise_box';
const String progressBox = 'progress_box';
const String syncQueueBox = 'sync_queue_box';
const String cacheMetaBox = 'cache_meta_box';

// Example: Progress model
@HiveType(typeId: 0)
class ProgressModel extends HiveObject {
  @HiveField(0)
  final String skillId;

  @HiveField(1)
  final int crownLevel;

  @HiveField(2)
  final int lessonsCompleted;

  @HiveField(3)
  final int totalLessons;

  @HiveField(4)
  final DateTime lastPracticed;

  @HiveField(5)
  final double strengthScore; // 0.0 - 1.0, used for skill decay
}
```

### 3.4.3 Secure Storage Keys

```dart
class SecureStorageKeys {
  static const accessToken = 'access_token';
  static const refreshToken = 'refresh_token';
  static const userId = 'user_id';
  static const biometricEnabled = 'biometric_enabled';
  static const encryptionKey = 'db_encryption_key';
}
```

### 3.4.4 SharedPreferences Keys

```dart
class PreferenceKeys {
  static const onboardingComplete = 'onboarding_complete';
  static const onboardingStep = 'onboarding_step';
  static const selectedLanguage = 'selected_language';
  static const dailyGoal = 'daily_goal';
  static const soundEnabled = 'sound_enabled';
  static const listeningEnabled = 'listening_enabled';
  static const speakingEnabled = 'speaking_enabled';
  static const animationsEnabled = 'animations_enabled';
  static const wifiOnlyDownload = 'wifi_only_download';
  static const reminderTime = 'reminder_time';
  static const lastSyncTimestamp = 'last_sync_timestamp';
  static const appLanguage = 'app_language';
  static const highContrastMode = 'high_contrast_mode';
  static const fontSize = 'font_size';
  static const colorblindMode = 'colorblind_mode';
  static const darkMode = 'dark_mode';
}
```

### 3.4.5 Data Migration Strategy

```dart
class DatabaseMigrator {
  static Future<void> migrate(int fromVersion, int toVersion) async {
    for (var v = fromVersion + 1; v <= toVersion; v++) {
      switch (v) {
        case 2:
          await _migrateV1ToV2(); // Add strengthScore to progress
          break;
        case 3:
          await _migrateV2ToV3(); // Add legendary level support
          break;
      }
    }
  }
}
```

---

## 3.5 Offline Caching

### 3.5.1 Cache Architecture

```
┌─────────────────────────────┐
│        UI Layer             │
├─────────────────────────────┤
│      Repository Layer       │
│  ┌─────────┐  ┌──────────┐ │
│  │ Remote   │  │  Local   │ │
│  │ Source   │  │  Source   │ │
│  └────┬─────┘  └────┬─────┘ │
│       │              │       │
│  ┌────▼──────────────▼────┐ │
│  │   Cache Strategy       │ │
│  │   (Cache-First /       │ │
│  │    Network-First /     │ │
│  │    Stale-While-        │ │
│  │    Revalidate)         │ │
│  └────────────────────────┘ │
└─────────────────────────────┘
```

### 3.5.2 Cache Strategies by Data Type

| Data Type | Strategy | TTL | Rationale |
|-----------|----------|-----|-----------|
| Course structure (skill tree) | Cache-first, background refresh | 24 hours | Changes infrequently; fast load critical |
| Lesson exercises | Cache-first | 7 days | Content is static once created |
| User progress | Network-first with cache fallback | 1 hour | Need latest data, but cache for offline |
| Leaderboard | Network-first | 5 minutes | Highly dynamic; stale data is acceptable briefly |
| User profile | Stale-while-revalidate | 1 hour | Show cached immediately, refresh in background |
| Audio files | Cache-first (permanent until evicted) | 30 days | Large files; avoid re-download |
| Images | Cache-first with LRU eviction | 14 days | Moderate size; CDN handles versioning |
| Shop items | Network-first | 1 hour | Pricing/availability may change |

### 3.5.3 Cache Eviction Policy

```dart
class CacheManager {
  static const maxCacheSize = 500 * 1024 * 1024; // 500 MB default

  Future<void> evictIfNeeded() async {
    final currentSize = await _calculateCacheSize();
    if (currentSize > maxCacheSize) {
      // LRU eviction: remove least recently accessed items
      final items = await _getAllCacheEntries();
      items.sort((a, b) => a.lastAccessed.compareTo(b.lastAccessed));

      var freedBytes = 0;
      for (final item in items) {
        await _deleteEntry(item);
        freedBytes += item.sizeBytes;
        if (currentSize - freedBytes <= maxCacheSize * 0.8) break; // Free until 80% capacity
      }
    }
  }
}
```

### 3.5.4 Pre-Download Manager

```dart
class PreDownloadManager {
  /// Downloads next N lessons in the current skill for offline use
  Future<void> preDownloadLessons({int count = 3}) async {
    final nextLessons = await _getNextUndownloadedLessons(count);
    for (final lesson in nextLessons) {
      await _downloadLesson(lesson);
      await _downloadAudioAssets(lesson);
      await _downloadImageAssets(lesson);
    }
  }

  /// Downloads an entire skill for offline use
  Future<void> downloadSkillForOffline(String skillId) async {
    final skill = await _repository.getSkill(skillId);
    for (final lesson in skill.lessons) {
      await _downloadLesson(lesson);
    }
    await _markSkillAsOffline(skillId);
  }

  /// Checks WiFi-only preference before downloading
  Future<bool> _shouldDownload() async {
    final wifiOnly = _prefs.getBool(PreferenceKeys.wifiOnlyDownload) ?? true;
    if (wifiOnly) {
      final connectivity = await _connectivity.checkConnectivity();
      return connectivity == ConnectivityResult.wifi;
    }
    return await _connectivity.isConnected;
  }
}
```

---

## 3.6 Push Notifications

### 3.6.1 Architecture

```
┌───────────────────────┐
│   Backend Server      │
│   ┌──────────────┐    │
│   │ Notification  │    │
│   │ Scheduler     │    │
│   └──────┬───────┘    │
└──────────┼────────────┘
           │
    ┌──────▼───────┐
    │  FCM / APNs  │
    └──────┬───────┘
           │
    ┌──────▼───────────────┐
    │  Mobile App           │
    │  ┌─────────────────┐  │
    │  │ FirebaseMessaging│  │
    │  └────────┬────────┘  │
    │  ┌────────▼────────┐  │
    │  │ NotificationBloc │  │
    │  └────────┬────────┘  │
    │  ┌────────▼────────┐  │
    │  │ Local Notif.     │  │
    │  │ (scheduled)      │  │
    │  └─────────────────┘  │
    └───────────────────────┘
```

### 3.6.2 FCM Setup

```dart
class PushNotificationService {
  final FirebaseMessaging _fcm = FirebaseMessaging.instance;

  Future<void> initialize() async {
    // Request permission (iOS)
    final settings = await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      // Get FCM token
      final token = await _fcm.getToken();
      await _registerToken(token!);

      // Listen for token refresh
      _fcm.onTokenRefresh.listen(_registerToken);

      // Subscribe to topics
      await _fcm.subscribeToTopic('all_users');
      await _fcm.subscribeToTopic('platform_${Platform.isIOS ? 'ios' : 'android'}');
    }

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Handle background/terminated tap
    FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);

    // Check if app was opened from terminated state via notification
    final initialMessage = await _fcm.getInitialMessage();
    if (initialMessage != null) {
      _handleNotificationTap(initialMessage);
    }
  }

  void _handleForegroundMessage(RemoteMessage message) {
    // Show in-app notification banner (not system notification)
    getIt<NotificationBloc>().add(NotificationEvent.received(
      title: message.notification?.title ?? '',
      body: message.notification?.body ?? '',
      data: message.data,
    ));
  }

  void _handleNotificationTap(RemoteMessage message) {
    final deepLink = message.data['deep_link'];
    if (deepLink != null) {
      getIt<AppRouter>().navigate(deepLink);
    }
  }

  Future<void> _registerToken(String token) async {
    await getIt<ApiClient>().post('/notifications/register', data: {
      'token': token,
      'platform': Platform.isIOS ? 'ios' : 'android',
      'device_id': await _getDeviceId(),
    });
  }
}
```

### 3.6.3 Local Notifications (Scheduled Reminders)

```dart
class LocalNotificationService {
  final FlutterLocalNotificationsPlugin _plugin = FlutterLocalNotificationsPlugin();

  Future<void> scheduleReminder({
    required TimeOfDay time,
    required String title,
    required String body,
  }) async {
    await _plugin.zonedSchedule(
      0, // notification ID
      title,
      body,
      _nextInstanceOfTime(time),
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'lesson_reminder',
          'Lesson Reminders',
          channelDescription: 'Daily lesson reminder notifications',
          importance: Importance.high,
          priority: Priority.high,
        ),
        iOS: DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
      matchDateTimeComponents: DateTimeComponents.time, // Repeat daily
      androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
    );
  }
}
```

### 3.6.4 Notification Topic Subscriptions

| Topic | Subscribers | Content |
|-------|------------|---------|
| `all_users` | All users | App updates, maintenance windows |
| `platform_ios` / `platform_android` | Platform-specific | Platform-specific updates |
| `league_{league_id}` | Users in league | League-wide events |
| `course_{language}` | Users studying language | Course updates, new content |
| `premium` | Super Duolingo subscribers | Premium-only notifications |

---

## 3.7 Deep Linking

### 3.7.1 URL Scheme

| Platform | Scheme |
|----------|--------|
| Custom URL | `duolearn://` |
| Universal Links (iOS) | `https://app.example.com/` |
| App Links (Android) | `https://app.example.com/` |

### 3.7.2 Deep Link Routes

| URL | Target Screen | Parameters |
|-----|---------------|------------|
| `app.example.com/lesson/{skill_id}` | Lesson Loading | `skill_id` |
| `app.example.com/leaderboard` | Leaderboard | — |
| `app.example.com/profile/{user_id}` | Profile | `user_id` |
| `app.example.com/shop` | Shop | — |
| `app.example.com/streak` | Streak Detail | — |
| `app.example.com/achievement/{id}` | Achievement Detail | `id` |
| `app.example.com/invite/{code}` | Friend Invite | `code` |
| `app.example.com/reset-password` | Reset Password | `token` (query param) |
| `app.example.com/challenge/{id}` | Friend Challenge | `id` |
| `app.example.com/subscribe` | Subscription Screen | — |

### 3.7.3 GoRouter Configuration

```dart
final router = GoRouter(
  initialLocation: '/home',
  redirect: (context, state) {
    final isLoggedIn = context.read<AuthBloc>().state is Authenticated;
    final isOnboarding = state.matchedLocation.startsWith('/onboarding');
    final isAuth = state.matchedLocation.startsWith('/auth');

    if (!isLoggedIn && !isOnboarding && !isAuth) {
      return '/welcome';
    }
    return null;
  },
  routes: [
    GoRoute(path: '/welcome', builder: (_, __) => const WelcomeScreen()),
    GoRoute(path: '/auth/login', builder: (_, __) => const LoginScreen()),
    GoRoute(path: '/auth/signup', builder: (_, __) => const SignupScreen()),
    GoRoute(
      path: '/auth/reset-password',
      builder: (_, state) => ResetPasswordScreen(
        token: state.uri.queryParameters['token']!,
      ),
    ),

    // Onboarding
    GoRoute(path: '/onboarding/language', builder: (_, __) => const LanguageSelectionScreen()),
    GoRoute(path: '/onboarding/motivation', builder: (_, __) => const MotivationScreen()),
    GoRoute(path: '/onboarding/goal', builder: (_, __) => const DailyGoalScreen()),
    GoRoute(path: '/onboarding/level', builder: (_, __) => const ExperienceLevelScreen()),

    // Tab shell
    ShellRoute(
      builder: (_, __, child) => TabShell(child: child),
      routes: [
        GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
        GoRoute(path: '/leaderboard', builder: (_, __) => const LeaderboardScreen()),
        GoRoute(path: '/shop', builder: (_, __) => const ShopScreen()),
        GoRoute(
          path: '/profile',
          builder: (_, __) => const ProfileScreen(),
          routes: [
            GoRoute(path: 'edit', builder: (_, __) => const ProfileEditScreen()),
            GoRoute(path: 'achievements', builder: (_, __) => const AchievementsScreen()),
            GoRoute(path: 'friends', builder: (_, __) => const FriendsScreen()),
            GoRoute(path: 'statistics', builder: (_, __) => const StatisticsScreen()),
          ],
        ),
        GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
      ],
    ),

    // Lesson flow (outside tab shell)
    GoRoute(
      path: '/lesson/:skillId',
      builder: (_, state) => LessonLoadingScreen(
        skillId: state.pathParameters['skillId']!,
      ),
    ),
    GoRoute(path: '/lesson/exercise', builder: (_, __) => const ExerciseScreen()),
    GoRoute(path: '/lesson/complete', builder: (_, __) => const LessonCompleteScreen()),

    // Placement test
    GoRoute(path: '/placement/instructions', builder: (_, __) => const PlacementInstructionsScreen()),
    GoRoute(path: '/placement/question', builder: (_, __) => const PlacementQuestionScreen()),
    GoRoute(path: '/placement/results', builder: (_, __) => const PlacementResultsScreen()),
  ],
);
```

### 3.7.4 Deferred Deep Linking

```dart
class DeferredDeepLinkService {
  /// Handles deep links that arrive when app is not installed
  /// (user installs from link → app opens and processes original link)
  Future<void> handleDeferredDeepLink() async {
    // Firebase Dynamic Links or platform-specific deferred deep link
    final PendingDynamicLinkData? data =
        await FirebaseDynamicLinks.instance.getInitialLink();

    if (data != null) {
      _processLink(data.link);
    }

    FirebaseDynamicLinks.instance.onLink.listen((dynamicLinkData) {
      _processLink(dynamicLinkData.link);
    });
  }

  void _processLink(Uri link) {
    getIt<AppRouter>().navigate(link.path + '?' + link.query);
  }
}
```

---

## 3.8 Analytics Events

### 3.8.1 Analytics Architecture

```dart
abstract class AnalyticsService {
  Future<void> logEvent(String name, Map<String, dynamic> parameters);
  Future<void> setUserProperty(String name, String value);
  Future<void> setUserId(String userId);
  Future<void> logScreenView(String screenName);
}

class AnalyticsServiceImpl implements AnalyticsService {
  final FirebaseAnalytics _firebase;
  final MixpanelAnalytics _mixpanel; // Optional secondary analytics
  final bool _userOptedIn;

  @override
  Future<void> logEvent(String name, Map<String, dynamic> parameters) async {
    if (!_userOptedIn) return;

    await Future.wait([
      _firebase.logEvent(name: name, parameters: parameters),
      _mixpanel.track(name, properties: parameters),
    ]);
  }
}
```

### 3.8.2 Event Taxonomy

#### Navigation Events

| Event | Parameters | Trigger |
|-------|-----------|---------|
| `screen_view` | `screen_name`, `screen_class` | Every screen navigation |
| `tab_switch` | `from_tab`, `to_tab` | Bottom tab bar tap |
| `deep_link_opened` | `url`, `source` | Deep link navigation |

#### Onboarding Events

| Event | Parameters | Trigger |
|-------|-----------|---------|
| `onboarding_started` | — | Welcome screen viewed |
| `onboarding_language_selected` | `language` | Language selected |
| `onboarding_motivation_selected` | `motivation` | Motivation selected |
| `onboarding_goal_selected` | `goal`, `xp_target` | Daily goal selected |
| `onboarding_experience_selected` | `level` | Experience level selected |
| `onboarding_completed` | `duration_seconds`, `took_placement` | Onboarding finished |
| `onboarding_abandoned` | `last_step`, `duration_seconds` | App closed during onboarding |

#### Auth Events

| Event | Parameters | Trigger |
|-------|-----------|---------|
| `signup_started` | `method` | Signup form opened |
| `signup_completed` | `method` | Account created |
| `signup_failed` | `method`, `error` | Signup error |
| `login_started` | `method` | Login form opened |
| `login_completed` | `method` | Login successful |
| `login_failed` | `method`, `error` | Login error |
| `logout` | — | User logged out |
| `password_reset_requested` | — | Reset link sent |

#### Lesson Events

| Event | Parameters | Trigger |
|-------|-----------|---------|
| `lesson_started` | `skill_id`, `crown_level`, `lesson_number` | Lesson begins |
| `exercise_started` | `exercise_type`, `exercise_id` | Exercise displayed |
| `exercise_answered` | `exercise_type`, `is_correct`, `response_time_ms` | Answer submitted |
| `lesson_completed` | `skill_id`, `crown_level`, `xp_earned`, `accuracy`, `duration_seconds` | Lesson finished |
| `lesson_abandoned` | `skill_id`, `exercises_completed`, `reason` | Lesson exited early |
| `out_of_lives` | `gems_balance` | Lives reach 0 |
| `lives_refilled` | `method` (gems/ad/practice) | Hearts restored |

#### Engagement Events

| Event | Parameters | Trigger |
|-------|-----------|---------|
| `streak_extended` | `streak_days` | Daily goal met |
| `streak_lost` | `previous_streak` | Streak broken |
| `streak_repaired` | `streak_days`, `gems_spent` | Streak repaired |
| `streak_freeze_used` | `streak_days` | Streak freeze consumed |
| `achievement_earned` | `achievement_id`, `achievement_name` | Achievement unlocked |
| `daily_reward_claimed` | `day`, `reward_type`, `amount` | Daily reward opened |

#### Commerce Events

| Event | Parameters | Trigger |
|-------|-----------|---------|
| `shop_item_purchased` | `item_id`, `item_name`, `gems_spent` | Gem purchase in shop |
| `iap_started` | `product_id`, `price` | In-app purchase initiated |
| `iap_completed` | `product_id`, `price`, `transaction_id` | Purchase successful |
| `iap_failed` | `product_id`, `error` | Purchase failed |
| `subscription_started` | `plan`, `trial` | Subscription activated |
| `subscription_cancelled` | `plan`, `reason` | Subscription cancelled |

#### Social Events

| Event | Parameters | Trigger |
|-------|-----------|---------|
| `friend_added` | `method` (search/invite/suggestion) | Friend added |
| `friend_removed` | — | Friend removed |
| `leaderboard_viewed` | `league`, `rank` | Leaderboard opened |
| `progress_shared` | `share_type`, `platform` | Share button tapped |

### 3.8.3 User Properties

| Property | Type | Example |
|----------|------|---------|
| `user_id` | String | `usr_abc123` |
| `account_type` | String | `free` / `premium` |
| `current_streak` | Int | `15` |
| `total_xp` | Int | `5420` |
| `active_course` | String | `spanish` |
| `courses_count` | Int | `2` |
| `league` | String | `gold` |
| `device_type` | String | `phone` / `tablet` |
| `app_version` | String | `2.1.0` |
| `days_since_install` | Int | `45` |
| `lessons_completed` | Int | `87` |
| `daily_goal` | String | `regular` |

# 7. Performance & Optimization

> Strategies for keeping the app fast, lean, and battery-friendly: caching, lazy loading, image optimization, and network efficiency.

---

## 7.1 Caching Strategy

### 7.1.1 Multi-Layer Cache Architecture

```
┌────────────────────────────────────────────────┐
│                 Application                     │
│                                                │
│  Layer 1: In-Memory Cache (LRU Map)            │
│  ┌────────────────────────────────────────┐    │
│  │ Hot data: current lesson, active user   │    │
│  │ profile, today's streak, leaderboard    │    │
│  │ TTL: Session duration or 5 minutes      │    │
│  │ Max size: 50 MB                         │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  Layer 2: Disk Cache (Hive / Isar)             │
│  ┌────────────────────────────────────────┐    │
│  │ Warm data: course tree, completed       │    │
│  │ lessons, exercise content, user progress │    │
│  │ TTL: Per data type (1 hour – 30 days)   │    │
│  │ Max size: 500 MB (configurable)         │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  Layer 3: File Cache (path_provider)           │
│  ┌────────────────────────────────────────┐    │
│  │ Binary assets: audio files, images,     │    │
│  │ downloaded lesson packs                 │    │
│  │ TTL: 14–30 days, LRU eviction          │    │
│  │ Max size: Included in Layer 2 budget    │    │
│  └────────────────────────────────────────┘    │
│                                                │
└────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────┐
│  Layer 4: CDN / Server Cache                   │
│  ┌────────────────────────────────────────┐    │
│  │ Static assets via CDN with long cache   │    │
│  │ API responses with ETag/Last-Modified   │    │
│  │ Cache-Control headers honored           │    │
│  └────────────────────────────────────────┘    │
└────────────────────────────────────────────────┘
```

### 7.1.2 In-Memory Cache Implementation

```dart
class InMemoryCache<T> {
  final int maxSize;
  final Duration defaultTtl;
  final _cache = LinkedHashMap<String, _CacheEntry<T>>();

  InMemoryCache({this.maxSize = 100, this.defaultTtl = const Duration(minutes: 5)});

  T? get(String key) {
    final entry = _cache[key];
    if (entry == null) return null;
    if (entry.isExpired) {
      _cache.remove(key);
      return null;
    }
    // Move to end (most recently used)
    _cache.remove(key);
    _cache[key] = entry;
    return entry.value;
  }

  void put(String key, T value, {Duration? ttl}) {
    if (_cache.length >= maxSize) {
      // Evict least recently used (first entry)
      _cache.remove(_cache.keys.first);
    }
    _cache[key] = _CacheEntry(value, ttl ?? defaultTtl);
  }

  void invalidate(String key) => _cache.remove(key);
  void clear() => _cache.clear();
}

class _CacheEntry<T> {
  final T value;
  final DateTime expiresAt;

  _CacheEntry(this.value, Duration ttl) : expiresAt = DateTime.now().add(ttl);

  bool get isExpired => DateTime.now().isAfter(expiresAt);
}
```

### 7.1.3 HTTP Response Caching

```dart
class HttpCacheInterceptor extends Interceptor {
  final InMemoryCache<Response> _memoryCache;
  final Box<CachedResponse> _diskCache;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    if (options.method != 'GET') {
      handler.next(options);
      return;
    }

    final cacheKey = _generateCacheKey(options);

    // Check in-memory cache first
    final memCached = _memoryCache.get(cacheKey);
    if (memCached != null) {
      handler.resolve(memCached);
      return;
    }

    // Check disk cache
    final diskCached = _diskCache.get(cacheKey);
    if (diskCached != null && !diskCached.isExpired) {
      final response = diskCached.toResponse(options);
      _memoryCache.put(cacheKey, response);
      handler.resolve(response);
      return;
    }

    // Add ETag/Last-Modified for conditional requests
    if (diskCached != null) {
      if (diskCached.etag != null) {
        options.headers['If-None-Match'] = diskCached.etag;
      }
      if (diskCached.lastModified != null) {
        options.headers['If-Modified-Since'] = diskCached.lastModified;
      }
    }

    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (response.requestOptions.method == 'GET') {
      final cacheKey = _generateCacheKey(response.requestOptions);

      if (response.statusCode == 304) {
        // Not modified: refresh disk cache TTL, serve cached
        final cached = _diskCache.get(cacheKey);
        if (cached != null) {
          cached.refreshTtl();
          handler.resolve(cached.toResponse(response.requestOptions));
          return;
        }
      }

      // Cache the new response
      final ttl = _parseCacheControl(response.headers);
      final cached = CachedResponse(
        data: response.data,
        statusCode: response.statusCode!,
        etag: response.headers.value('ETag'),
        lastModified: response.headers.value('Last-Modified'),
        ttl: ttl,
      );
      _diskCache.put(cacheKey, cached);
      _memoryCache.put(cacheKey, response, ttl: ttl);
    }

    handler.next(response);
  }

  String _generateCacheKey(RequestOptions options) {
    return '${options.method}:${options.uri}';
  }

  Duration _parseCacheControl(Headers headers) {
    final cacheControl = headers.value('Cache-Control');
    if (cacheControl != null) {
      final maxAge = RegExp(r'max-age=(\d+)').firstMatch(cacheControl);
      if (maxAge != null) {
        return Duration(seconds: int.parse(maxAge.group(1)!));
      }
    }
    return const Duration(minutes: 5); // Default TTL
  }
}
```

### 7.1.4 Cache Invalidation Strategy

| Trigger | Invalidation Scope |
|---------|-------------------|
| Lesson completed | Skill progress cache, daily XP cache, streak cache |
| Profile updated | User profile cache |
| Shop purchase | Gems balance cache, shop items cache |
| Course switched | Skill tree cache (new course), leaderboard cache |
| Pull-to-refresh | Screen-specific cache (e.g., leaderboard) |
| App update | All caches (version change triggers full clear) |
| Logout | All caches and secure storage |
| Force refresh (server push) | Specific cache identified in push payload |

### 7.1.5 Cache Size Management

```dart
class CacheSizeManager {
  static const defaultMaxCacheBytes = 500 * 1024 * 1024; // 500 MB

  Future<CacheStats> getCacheStats() async {
    final audioSize = await _calculateDirectorySize(_audioCacheDir);
    final imageSize = await _calculateDirectorySize(_imageCacheDir);
    final dbSize = await _calculateHiveBoxSize();
    final totalSize = audioSize + imageSize + dbSize;

    return CacheStats(
      audioBytes: audioSize,
      imageBytes: imageSize,
      databaseBytes: dbSize,
      totalBytes: totalSize,
      maxBytes: defaultMaxCacheBytes,
      usagePercent: totalSize / defaultMaxCacheBytes,
    );
  }

  Future<void> clearCache({bool keepUserData = true}) async {
    await _clearDirectory(_audioCacheDir);
    await _clearDirectory(_imageCacheDir);
    if (!keepUserData) {
      await _clearHiveBoxes();
    }
  }

  Future<void> trimCacheTo(int targetBytes) async {
    final stats = await getCacheStats();
    if (stats.totalBytes <= targetBytes) return;

    final bytesToFree = stats.totalBytes - targetBytes;
    var freed = 0;

    // Priority 1: Old audio files (largest, least frequently accessed)
    freed += await _evictOldestFiles(_audioCacheDir, bytesToFree - freed);
    if (freed >= bytesToFree) return;

    // Priority 2: Old images
    freed += await _evictOldestFiles(_imageCacheDir, bytesToFree - freed);
    if (freed >= bytesToFree) return;

    // Priority 3: Old database entries
    freed += await _evictOldDbEntries(bytesToFree - freed);
  }
}
```

---

## 7.2 Lazy Loading

### 7.2.1 Deferred Widget Loading

```dart
/// Lazy-load heavy widgets only when they're about to be visible
class LazyWidget extends StatefulWidget {
  final Widget Function() builder;
  final Widget placeholder;

  const LazyWidget({
    required this.builder,
    this.placeholder = const SizedBox.shrink(),
  });

  @override
  State<LazyWidget> createState() => _LazyWidgetState();
}

class _LazyWidgetState extends State<LazyWidget> {
  Widget? _child;
  bool _isVisible = false;

  @override
  Widget build(BuildContext context) {
    return VisibilityDetector(
      key: Key(widget.hashCode.toString()),
      onVisibilityChanged: (info) {
        if (info.visibleFraction > 0 && !_isVisible) {
          _isVisible = true;
          setState(() {
            _child = widget.builder();
          });
        }
      },
      child: _child ?? widget.placeholder,
    );
  }
}
```

### 7.2.2 Skill Tree Lazy Rendering

The skill tree can contain 80+ nodes. Only visible nodes are rendered:

```dart
class SkillTreeWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        // Sliver-based rendering: only builds visible items
        SliverList(
          delegate: SliverChildBuilderDelegate(
            (context, index) {
              final section = sections[index];
              return SkillSectionWidget(
                section: section,
                onSkillTap: _handleSkillTap,
              );
            },
            childCount: sections.length,
          ),
        ),
      ],
    );
  }
}

class SkillSectionWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Section header
        Text(section.name, style: Theme.of(context).textTheme.titleLarge),

        // Only render nodes that are in/near viewport
        ...section.skills.map((skill) => RepaintBoundary(
          child: SkillNodeWidget(skill: skill),
        )),

        // Checkpoint (if present)
        if (section.checkpoint != null)
          CheckpointNodeWidget(checkpoint: section.checkpoint!),
      ],
    );
  }
}
```

### 7.2.3 Deferred Feature Imports

```dart
// Use Dart deferred loading for heavy feature modules
import 'package:app/features/speech/speech_engine.dart' deferred as speech;
import 'package:app/features/story/story_engine.dart' deferred as story;

class ExerciseFactory {
  Future<Widget> createExercise(Exercise exercise) async {
    switch (exercise.type) {
      case ExerciseType.speaking:
        await speech.loadLibrary(); // Load only when needed
        return speech.SpeakingExerciseWidget(exercise: exercise);

      case ExerciseType.story:
        await story.loadLibrary();
        return story.StoryExerciseWidget(exercise: exercise);

      default:
        return BasicExerciseWidget(exercise: exercise);
    }
  }
}
```

### 7.2.4 Data Lazy Loading

```dart
class PaginatedListBloc<T> extends Bloc<PaginatedEvent, PaginatedState<T>> {
  static const pageSize = 20;
  String? _nextCursor;

  Future<void> _onLoadMore(LoadMore event, Emitter emit) async {
    if (state.isLoadingMore || !state.hasMore) return;

    emit(state.copyWith(isLoadingMore: true));

    final result = await _repository.getPage(
      cursor: _nextCursor,
      limit: pageSize,
    );

    result.when(
      success: (page) {
        _nextCursor = page.cursor;
        emit(state.copyWith(
          items: [...state.items, ...page.items],
          hasMore: page.hasMore,
          isLoadingMore: false,
        ));
      },
      failure: (error) {
        emit(state.copyWith(isLoadingMore: false, error: error));
      },
    );
  }
}

// In the UI: trigger load when approaching end of list
class PaginatedListView<T> extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return NotificationListener<ScrollNotification>(
      onNotification: (notification) {
        if (notification.metrics.pixels >=
            notification.metrics.maxScrollExtent - 200) {
          context.read<PaginatedListBloc<T>>().add(const LoadMore());
        }
        return false;
      },
      child: ListView.builder(
        itemCount: items.length + (hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == items.length) {
            return const LoadingIndicator(); // Loading spinner at bottom
          }
          return itemBuilder(items[index]);
        },
      ),
    );
  }
}
```

---

## 7.3 Image Optimization

### 7.3.1 Image Format Strategy

| Use Case | Format | Reasoning |
|----------|--------|-----------|
| Skill icons | SVG | Scalable, tiny file size (~1–5 KB) |
| Avatar photos | WebP | 25–35% smaller than JPEG, transparency support |
| Illustrations | WebP with fallback PNG | Good compression, wide support |
| Animations (mascot) | Lottie JSON | Vector-based, small, scriptable |
| Audio waveforms | Generated at runtime | No image file needed |

### 7.3.2 Resolution Buckets

```dart
class ImageUrlHelper {
  /// Generate optimized image URL based on device pixel ratio
  static String optimizedUrl(String baseUrl, {required double devicePixelRatio, required int logicalWidth}) {
    final physicalWidth = (logicalWidth * devicePixelRatio).round();

    // Snap to nearest bucket to maximize CDN cache hits
    final bucket = _snapToBucket(physicalWidth);

    // URL pattern: /images/{width}/{path}
    return baseUrl.replaceFirst('/images/', '/images/$bucket/');
  }

  static int _snapToBucket(int width) {
    const buckets = [200, 400, 600, 800, 1200, 1600];
    return buckets.firstWhere((b) => b >= width, orElse: () => buckets.last);
  }
}
```

| Bucket | Use Case | Typical Size |
|--------|----------|-------------|
| 200px | Thumbnails, list avatars | 5–15 KB |
| 400px | Card images, grid items | 15–40 KB |
| 600px | Half-width images | 30–60 KB |
| 800px | Full-width images (phone) | 50–100 KB |
| 1200px | Full-width images (tablet) | 80–150 KB |
| 1600px | Full-screen images | 100–200 KB |

### 7.3.3 Progressive Image Loading

```dart
class ProgressiveImage extends StatelessWidget {
  final String imageUrl;
  final String? thumbnailUrl;
  final double width;
  final double height;

  @override
  Widget build(BuildContext context) {
    return CachedNetworkImage(
      imageUrl: imageUrl,
      placeholder: (context, url) => Stack(
        children: [
          // Layer 1: Shimmer placeholder
          ShimmerPlaceholder(width: width, height: height),
          // Layer 2: Blurred thumbnail (if available)
          if (thumbnailUrl != null)
            CachedNetworkImage(
              imageUrl: thumbnailUrl!,
              imageBuilder: (context, imageProvider) => Container(
                decoration: BoxDecoration(
                  image: DecorationImage(
                    image: imageProvider,
                    fit: BoxFit.cover,
                  ),
                ),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                  child: const SizedBox.expand(),
                ),
              ),
            ),
        ],
      ),
      fadeInDuration: const Duration(milliseconds: 300),
      memCacheWidth: (width * MediaQuery.of(context).devicePixelRatio).round(),
      errorWidget: (context, url, error) => const ImageErrorPlaceholder(),
    );
  }
}
```

### 7.3.4 Image Cache Configuration

```dart
class ImageCacheConfig {
  static void configure() {
    // In-memory image cache
    PaintingBinding.instance.imageCache.maximumSize = 200; // Max 200 images
    PaintingBinding.instance.imageCache.maximumSizeBytes = 100 * 1024 * 1024; // 100 MB

    // Disk cache (via cached_network_image)
    DefaultCacheManager().emptyCache(); // Only on major version update
  }

  static final cacheManager = CacheManager(
    Config(
      'image_cache',
      stalePeriod: const Duration(days: 14),
      maxNrOfCacheObjects: 500,
      repo: JsonCacheInfoRepository(databaseName: 'image_cache'),
      fileService: HttpFileService(),
    ),
  );
}
```

### 7.3.5 SVG Optimization

```dart
class OptimizedSvg extends StatelessWidget {
  final String assetPath;
  final double size;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return SvgPicture.asset(
      assetPath,
      width: size,
      height: size,
      colorFilter: color != null
          ? ColorFilter.mode(color!, BlendMode.srcIn)
          : null,
      placeholderBuilder: (context) => SizedBox(
        width: size,
        height: size,
      ),
    );
  }
}
```

---

## 7.4 Reducing Network Calls

### 7.4.1 Request Batching

```dart
class BatchRequestManager {
  final _pendingBatches = <String, List<Completer<dynamic>>>{};
  Timer? _batchTimer;
  static const batchWindow = Duration(milliseconds: 100);

  /// Batch multiple individual requests into a single API call
  Future<T> batchedGet<T>(String endpoint, String itemId) async {
    final completer = Completer<T>();
    final batchKey = endpoint;

    _pendingBatches.putIfAbsent(batchKey, () => []);
    _pendingBatches[batchKey]!.add(completer);

    // Start or restart the batch timer
    _batchTimer?.cancel();
    _batchTimer = Timer(batchWindow, () => _executeBatch(batchKey));

    return completer.future;
  }

  Future<void> _executeBatch(String endpoint) async {
    final completers = _pendingBatches.remove(endpoint);
    if (completers == null || completers.isEmpty) return;

    try {
      // Single batch request instead of N individual requests
      final ids = completers.map((c) => c.hashCode.toString()).toList();
      final response = await _apiClient.get('$endpoint/batch', queryParameters: {
        'ids': ids.join(','),
      });

      final results = response.data['data'] as List;
      for (var i = 0; i < completers.length; i++) {
        completers[i].complete(results[i]);
      }
    } catch (e) {
      for (final completer in completers) {
        completer.completeError(e);
      }
    }
  }
}
```

### 7.4.2 Delta Sync

```dart
class DeltaSyncService {
  /// Only fetch data that changed since last sync
  Future<void> syncCourseProgress() async {
    final lastSync = await _prefs.getString('last_progress_sync');

    final response = await _apiClient.get('/users/me/progress', queryParameters: {
      'since': lastSync, // ISO 8601 timestamp
    });

    final delta = response.data['data'];
    if (delta['has_changes'] == true) {
      // Only update changed items
      for (final skill in delta['updated_skills']) {
        await _localDb.updateSkill(skill);
      }
      for (final achievement in delta['new_achievements']) {
        await _localDb.addAchievement(achievement);
      }
    }

    await _prefs.setString('last_progress_sync', delta['sync_timestamp']);
  }
}
```

### 7.4.3 Prefetching Strategy

```dart
class PrefetchService {
  /// Prefetch data that the user is likely to need next
  Future<void> prefetchForScreen(String currentScreen) async {
    switch (currentScreen) {
      case 'home':
        // User likely to start a lesson next
        await _prefetchNextLesson();
        break;
      case 'skill_detail':
        // User likely to start the next lesson in this skill
        await _prefetchLessonExercises();
        // Also prefetch audio files
        await _prefetchAudioAssets();
        break;
      case 'lesson_complete':
        // User might continue or go to leaderboard
        await Future.wait([
          _prefetchNextLesson(),
          _prefetchLeaderboard(),
        ]);
        break;
      case 'leaderboard':
        // Prefetch friend leaderboard data
        await _prefetchFriendLeaderboard();
        break;
    }
  }

  Future<void> _prefetchNextLesson() async {
    final nextSkill = await _repository.getNextAvailableSkill();
    if (nextSkill != null) {
      final lesson = await _repository.getNextLesson(nextSkill.id);
      await _cacheManager.cacheLesson(lesson);
    }
  }

  Future<void> _prefetchAudioAssets() async {
    final pendingExercises = await _repository.getCachedExercises();
    final audioUrls = pendingExercises
        .where((e) => e.prompt.audioUrl != null)
        .map((e) => e.prompt.audioUrl!)
        .toList();

    for (final url in audioUrls) {
      await DefaultCacheManager().downloadFile(url);
    }
  }
}
```

### 7.4.4 Connection-Aware Loading

```dart
class ConnectionAwareLoader {
  final ConnectivityService _connectivity;

  /// Adjust data loading strategy based on connection quality
  Future<LoadingStrategy> getStrategy() async {
    final result = await _connectivity.checkConnectivity();
    final effectiveType = await _connectivity.getEffectiveType();

    if (result == ConnectivityResult.wifi) {
      return LoadingStrategy.full; // Load everything including high-res images
    }

    switch (effectiveType) {
      case EffectiveConnectionType.type4g:
        return LoadingStrategy.standard; // Normal loading, standard-res images
      case EffectiveConnectionType.type3g:
        return LoadingStrategy.reduced; // Reduced images, skip prefetch
      case EffectiveConnectionType.type2g:
      case EffectiveConnectionType.slow2g:
        return LoadingStrategy.minimal; // Text-only where possible, tiny images
      default:
        return LoadingStrategy.standard;
    }
  }
}

enum LoadingStrategy {
  full,     // WiFi: prefetch aggressively, high-res images, auto-download
  standard, // 4G: normal loading, medium-res images
  reduced,  // 3G: skip prefetch, low-res images, defer non-critical
  minimal,  // 2G: text-only, skip images, defer everything non-essential
}
```

### 7.4.5 API Response Compression

```dart
// Enable gzip compression for API responses
class CompressionInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    options.headers['Accept-Encoding'] = 'gzip, deflate';
    handler.next(options);
  }
}
```

### 7.4.6 Debouncing and Throttling

```dart
class EventDebouncer {
  Timer? _timer;
  final Duration delay;

  EventDebouncer({this.delay = const Duration(milliseconds: 500)});

  void run(VoidCallback action) {
    _timer?.cancel();
    _timer = Timer(delay, action);
  }

  void dispose() {
    _timer?.cancel();
  }
}

class EventThrottler {
  DateTime? _lastRun;
  final Duration interval;

  EventThrottler({this.interval = const Duration(seconds: 2)});

  void run(VoidCallback action) {
    final now = DateTime.now();
    if (_lastRun == null || now.difference(_lastRun!) >= interval) {
      _lastRun = now;
      action();
    }
  }
}

// Usage examples:
// Debounce: Username availability check (type → wait 500ms → check)
final _usernameDebouncer = EventDebouncer(delay: const Duration(milliseconds: 500));
void onUsernameChanged(String value) {
  _usernameDebouncer.run(() => _checkUsernameAvailability(value));
}

// Throttle: XP sync to server (max once per 5 seconds)
final _xpThrottler = EventThrottler(interval: const Duration(seconds: 5));
void onXpEarned(int xp) {
  _localXp += xp;
  _xpThrottler.run(() => _syncXpToServer(_localXp));
}
```

### 7.4.7 Network Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to First Byte (TTFB) | < 200ms | Dio interceptor timing |
| API Response Time (P50) | < 500ms | Analytics event per request |
| API Response Time (P99) | < 2000ms | Analytics event per request |
| Cache Hit Rate | > 70% | Counter in cache interceptor |
| Offline Availability | > 95% of core flows | Test coverage of offline paths |
| Sync Queue Processing | < 30s on reconnect | Timer from reconnect to queue empty |
| App Launch to Interactive | < 2s (warm), < 4s (cold) | Performance trace (Firebase) |
| Lesson Load Time | < 1.5s | Duration from tap to first exercise |
| Image Load Time | < 500ms (cached), < 2s (network) | `CachedNetworkImage` callbacks |

### 7.4.8 Build Size Optimization

| Strategy | Impact | Implementation |
|----------|--------|---------------|
| Tree-shaking | Removes unused code | Enabled by default in release builds |
| Deferred loading | Reduces initial bundle | `deferred as` imports for heavy features |
| Asset compression | Smaller APK/IPA | Compress PNGs, use WebP, optimize SVGs |
| ProGuard/R8 (Android) | Smaller DEX files | Enable in `build.gradle` for release |
| Bitcode (iOS) | Apple optimizes binary | Enabled in Xcode build settings |
| Split APKs (Android) | Per-ABI APKs | `flutter build appbundle` (AAB) |
| On-demand resources (iOS) | Download assets later | Tag non-critical assets for on-demand |
| Remove debug symbols | Smaller binary | `--split-debug-info` flag |
| Icon font subsetting | Smaller font files | Only include used glyphs |

**Target App Sizes:**

| Platform | Download Size | Install Size |
|----------|--------------|-------------|
| iOS | < 50 MB | < 150 MB |
| Android (AAB) | < 30 MB | < 100 MB |

### 7.4.9 Runtime Performance Guidelines

| Area | Guideline |
|------|-----------|
| Widget Rebuilds | Use `const` constructors; `select` with BLoC; minimize `setState` scope |
| Lists | Always use `ListView.builder` (not `ListView` with children); add `key` for items |
| Animations | Use `AnimatedBuilder` and `RepaintBoundary`; avoid `setState` during animations |
| Images | Specify `cacheWidth`/`cacheHeight` on `Image` widgets to reduce memory |
| Isolates | Use `compute()` for JSON parsing of large responses (>100KB) |
| Memory | Monitor with DevTools; dispose controllers and streams; avoid circular references |
| Startup | Defer non-critical initialization; use `WidgetsBinding.instance.addPostFrameCallback` |
| Navigation | Precompute routes; avoid building heavy screens during transitions |

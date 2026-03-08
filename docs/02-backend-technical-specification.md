# 2. Backend Technical Specification

## 2.1 System Overview

The Duolingo-style learning platform backend is built on a modular, service-oriented architecture using ASP.NET Core 8. The system is designed to handle millions of daily active users with high availability, low latency, and real-time responsiveness.

### Design Principles

- **Separation of Concerns**: Each module owns its domain logic and data
- **Event-Driven Architecture**: Key actions publish events consumed by downstream services
- **Cache-First Strategy**: Hot data served from Redis to minimize database load
- **Resilience**: Circuit breakers, retries, and graceful degradation
- **Observability**: Structured logging, distributed tracing, and metrics at every layer
- **Security by Default**: All inputs validated, all outputs sanitized, JWT-based auth

### Technology Stack

| Component          | Technology                           |
|--------------------|--------------------------------------|
| Runtime            | .NET 8 (ASP.NET Core)               |
| API Framework      | ASP.NET Core Minimal APIs + Controllers |
| ORM                | Entity Framework Core 8              |
| Database           | MySQL 8.0 (InnoDB)                   |
| Cache              | Redis 7.x (Cluster mode)            |
| Message Queue      | RabbitMQ 3.12 (MassTransit)         |
| Authentication     | JWT RS256 + ASP.NET Core Identity    |
| API Gateway        | YARP (Yet Another Reverse Proxy)     |
| Containerization   | Docker                               |
| Orchestration      | Kubernetes (EKS / AKS)              |
| CI/CD              | GitHub Actions                       |
| Object Storage     | AWS S3 / Azure Blob Storage          |
| CDN                | CloudFront / Cloudflare              |
| Monitoring         | Prometheus + Grafana                 |
| Logging            | Serilog → Elasticsearch (ELK)       |
| Tracing            | OpenTelemetry → Jaeger               |
| Search             | Elasticsearch                        |

---

## 2.2 Backend Modules & Microservices

The backend is organized into the following bounded contexts, each deployable as an independent microservice:

### Module Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (YARP)                       │
│              Rate Limiting │ Auth │ Routing │ SSL               │
└──────────┬──────────┬──────┴──────┬──────────┬─────────────────┘
           │          │             │          │
    ┌──────▼──┐ ┌─────▼────┐ ┌─────▼────┐ ┌──▼──────────┐
    │  Auth   │ │  Course  │ │ Learning │ │ Gamification│
    │ Service │ │  Service │ │ Service  │ │   Service   │
    └────┬────┘ └────┬─────┘ └────┬─────┘ └──────┬──────┘
         │           │            │               │
    ┌────▼──┐  ┌─────▼────┐ ┌────▼────┐  ┌──────▼──────┐
    │ User  │  │ Content  │ │Progress │  │ Leaderboard │
    │Service│  │ Service  │ │ Service │  │   Service   │
    └───┬───┘  └────┬─────┘ └────┬────┘  └──────┬──────┘
        │           │            │               │
    ┌───▼──────┐ ┌──▼───────┐ ┌─▼────────┐ ┌───▼────────┐
    │Social    │ │Notification││ Analytics │ │  Payment   │
    │Service   │ │  Service  │ │ Service  │ │  Service   │
    └──────────┘ └───────────┘ └──────────┘ └────────────┘
```

### Module Details

#### 2.2.1 Auth Service

**Responsibility:** User authentication, token management, OAuth integration

**Key Components:**
- JWT token generation and validation (RS256)
- Refresh token rotation
- OAuth2 provider integration (Google, Apple, Facebook)
- Password hashing (bcrypt, work factor 12)
- Device trust management
- Rate-limited login attempts

**Dependencies:** User Service (for profile data)

**Database Tables:** `users`, `refresh_tokens`, `oauth_accounts`, `device_tokens`, `login_attempts`

#### 2.2.2 User Service

**Responsibility:** User profile management, settings, preferences

**Key Components:**
- Profile CRUD operations
- Avatar upload (to S3) and CDN URL generation
- Privacy settings
- Account deletion (soft delete with 30-day grace)
- GDPR data export

**Dependencies:** Auth Service, Storage Service

**Database Tables:** `user_profiles`, `user_settings`, `user_preferences`, `deletion_requests`

#### 2.2.3 Course Service

**Responsibility:** Course catalog, skill trees, exercise content

**Key Components:**
- Course management and enrollment
- Skill tree structure and ordering
- Exercise content delivery
- Content versioning
- Language pair management

**Dependencies:** Content Service, CDN

**Database Tables:** `courses`, `enrollments`, `skills`, `skill_prerequisites`, `lessons`, `exercises`, `exercise_options`, `word_bank`

#### 2.2.4 Learning Service

**Responsibility:** Lesson sessions, answer evaluation, spaced repetition

**Key Components:**
- Lesson session management
- Answer evaluation engine
- Typo tolerance (Levenshtein distance)
- Spaced repetition algorithm (SM-2 variant)
- Adaptive difficulty
- Heart/life management

**Dependencies:** Course Service, Progress Service, Gamification Service

**Database Tables:** `lesson_sessions`, `session_answers`, `word_strength`, `practice_queue`

#### 2.2.5 Progress Service

**Responsibility:** Tracking XP, crowns, levels, skill strength

**Key Components:**
- XP accumulation and history
- Crown/level progression
- Skill strength decay calculation
- Daily goal tracking
- Progress analytics

**Dependencies:** Learning Service (events), Gamification Service

**Database Tables:** `user_progress`, `xp_history`, `crown_progress`, `daily_goals`, `skill_strength`

#### 2.2.6 Gamification Service

**Responsibility:** Streaks, achievements, rewards, shop

**Key Components:**
- Streak tracking and freeze logic
- Achievement evaluation engine
- Gem/lingot economy
- Shop item management
- Double-or-nothing wagers

**Dependencies:** Progress Service (events)

**Database Tables:** `streaks`, `achievements`, `user_achievements`, `inventory`, `shop_items`, `purchases`, `wagers`

#### 2.2.7 Leaderboard Service

**Responsibility:** Weekly leaderboards, league management

**Key Components:**
- League assignment algorithm
- Weekly XP rankings (Redis sorted sets)
- Promotion/demotion logic
- Historical leaderboard archives

**Dependencies:** Progress Service (events), Redis

**Database Tables:** `leagues`, `league_memberships`, `leaderboard_history`

#### 2.2.8 Social Service

**Responsibility:** Friends, friend requests, activity feeds

**Key Components:**
- Friend management
- Friend request flow
- Activity feed generation
- User search
- Block/report functionality

**Dependencies:** User Service, Notification Service

**Database Tables:** `friendships`, `friend_requests`, `activity_feed`, `blocks`, `reports`

#### 2.2.9 Notification Service

**Responsibility:** Push notifications, emails, in-app notifications

**Key Components:**
- Multi-channel notification dispatch (push, email, in-app)
- Notification templates
- Preference-based routing
- Quiet hours enforcement
- Notification scheduling

**Dependencies:** RabbitMQ, Firebase Cloud Messaging, SendGrid

**Database Tables:** `notifications`, `notification_preferences`, `notification_templates`, `notification_queue`

#### 2.2.10 Analytics Service

**Responsibility:** User analytics, A/B testing, platform metrics

**Key Components:**
- Event ingestion pipeline
- A/B test framework
- Feature flag management
- User cohort analysis
- Retention metrics

**Dependencies:** All services (event consumers), Redis, Elasticsearch

**Database Tables:** `events`, `ab_tests`, `ab_test_assignments`, `feature_flags`, `feature_flag_overrides`

#### 2.2.11 Payment Service

**Responsibility:** Subscription management, billing, App Store/Play Store integration

**Key Components:**
- Subscription lifecycle management
- Apple/Google receipt validation
- Stripe integration for web
- Trial management
- Family plan management

**Dependencies:** User Service, Notification Service

**Database Tables:** `subscriptions`, `payment_history`, `receipts`, `subscription_plans`, `family_groups`

#### 2.2.12 Content Service

**Responsibility:** Audio, image, and media asset management

**Key Components:**
- TTS (Text-to-Speech) integration
- Audio file management
- Image optimization and resizing
- CDN cache invalidation

**Dependencies:** S3, CDN, TTS providers

---

## 2.3 Data Flow Diagrams

### Lesson Completion Data Flow

```
User Device
    │
    ▼
┌─────────────┐
│ API Gateway  │ ── Rate limit check (Redis)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Learning   │ ── Validate session, evaluate answer
│  Service    │
└──────┬──────┘
       │
       ├──────────────────────────────────┐
       │                                  │
       ▼                                  ▼
┌─────────────┐                   ┌──────────────┐
│  MySQL DB   │ ── Store answer   │  RabbitMQ    │ ── Publish events
│  (Primary)  │    & session data │  (Exchange)  │
└─────────────┘                   └──────┬───────┘
                                         │
                    ┌────────────┬────────┼────────┬──────────────┐
                    │            │        │        │              │
                    ▼            ▼        ▼        ▼              ▼
              ┌──────────┐ ┌─────────┐ ┌──────┐ ┌──────────┐ ┌────────┐
              │ Progress │ │Gamific. │ │Leader│ │Analytics │ │Notific.│
              │ Service  │ │Service  │ │board │ │ Service  │ │Service │
              └──────────┘ └─────────┘ └──────┘ └──────────┘ └────────┘
                  │            │          │          │            │
                  ▼            ▼          ▼          ▼            ▼
              Update XP   Check       Update     Record      Send push
              & crowns    achievements rankings   event       if needed
```

### User Registration Data Flow

```
Client
  │
  ▼
┌───────────┐
│API Gateway│
└─────┬─────┘
      │
      ▼
┌───────────┐  1. Validate input, hash password
│   Auth    │  2. Create user record
│  Service  │  3. Generate JWT + refresh token
└─────┬─────┘
      │
      ├──► MySQL: Insert user, profile, settings
      │
      ├──► Redis: Cache user session
      │
      ├──► RabbitMQ: Publish "UserRegistered" event
      │        │
      │        ├──► Notification Service: Send welcome email
      │        ├──► Analytics Service: Track registration event
      │        └──► Gamification Service: Initialize streak, gems
      │
      └──► Response: { userId, accessToken, refreshToken }
```

### Authentication Flow

```
Client                API Gateway            Auth Service           Redis              MySQL
  │                       │                       │                   │                  │
  │──POST /auth/login────►│                       │                   │                  │
  │                       │──Forward──────────────►│                   │                  │
  │                       │                       │──Check rate limit─►│                  │
  │                       │                       │◄─────OK───────────│                  │
  │                       │                       │──Fetch user───────┼─────────────────►│
  │                       │                       │◄─────User data────┼──────────────────│
  │                       │                       │──Verify password   │                  │
  │                       │                       │──Generate JWT      │                  │
  │                       │                       │──Store session────►│                  │
  │                       │◄──Token response──────│                   │                  │
  │◄──200 + JWT──────────│                       │                   │                  │
```

---

## 2.4 Background Jobs

Background jobs run as hosted services within ASP.NET Core using `IHostedService` and are managed via Hangfire for scheduled tasks.

### Job Registry

| Job Name                   | Schedule        | Description                                              | Priority |
|----------------------------|-----------------|----------------------------------------------------------|----------|
| `StreakEvaluationJob`      | Daily 00:05 UTC | Evaluate streaks, apply freezes, reset broken streaks    | Critical |
| `LeaderboardResetJob`      | Weekly Mon 00:00| Reset weekly leaderboards, process promotions/demotions  | Critical |
| `SkillStrengthDecayJob`    | Daily 02:00 UTC | Decay skill strength based on spaced repetition model    | High     |
| `DailyGoalResetJob`        | Daily 00:01 UTC | Reset daily goal tracking per user timezone               | High     |
| `NotificationSchedulerJob` | Every 15 min    | Process scheduled notifications (streak reminders, etc.) | High     |
| `InactiveUserReminderJob`  | Daily 10:00 UTC | Send reminders to users inactive for 24+ hours           | Medium   |
| `AchievementEvaluationJob` | Every 5 min     | Process pending achievement checks from event queue      | Medium   |
| `DataRetentionJob`         | Daily 03:00 UTC | Purge expired data (old sessions, logs, soft deletes)    | Low      |
| `AnalyticsAggregationJob`  | Hourly          | Aggregate raw events into summary metrics                | Low      |
| `CDNCacheWarmJob`          | Daily 04:00 UTC | Pre-warm CDN cache for popular content                   | Low      |
| `DatabaseMaintenanceJob`   | Weekly Sun 03:00| Optimize tables, update statistics, archive old data     | Low      |
| `SubscriptionRenewalJob`   | Every 1 hour    | Check and process subscription renewals                  | High     |
| `ABTestEvaluationJob`      | Daily 06:00 UTC | Evaluate A/B test results and statistical significance   | Low      |

### Job Implementation Pattern

```csharp
public class StreakEvaluationJob : IHostedService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<StreakEvaluationJob> _logger;
    private Timer? _timer;

    public Task StartAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("StreakEvaluationJob starting");
        // Schedule for daily 00:05 UTC
        _timer = new Timer(
            DoWork, null,
            CalculateNextRun(),
            TimeSpan.FromDays(1));
        return Task.CompletedTask;
    }

    private async void DoWork(object? state)
    {
        using var scope = _serviceProvider.CreateScope();
        var streakService = scope.ServiceProvider
            .GetRequiredService<IStreakService>();

        var batchSize = 1000;
        var processed = 0;

        await foreach (var batch in streakService
            .GetUsersForEvaluationAsync(batchSize))
        {
            foreach (var user in batch)
            {
                try
                {
                    await streakService.EvaluateStreakAsync(user.UserId);
                    processed++;
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex,
                        "Failed to evaluate streak for {UserId}",
                        user.UserId);
                }
            }
        }

        _logger.LogInformation(
            "StreakEvaluationJob completed. Processed: {Count}",
            processed);
    }
}
```

---

## 2.5 Notification System

### Architecture

```
Event Source (any service)
       │
       ▼
┌──────────────┐
│   RabbitMQ   │
│ notification │
│   exchange   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Notification    │
│  Service         │
│                  │
│  ┌────────────┐  │
│  │  Template  │  │
│  │  Engine    │  │
│  └─────┬──────┘  │
│        │         │
│  ┌─────▼──────┐  │
│  │ Preference │  │
│  │  Filter    │  │
│  └─────┬──────┘  │
│        │         │
│  ┌─────▼──────┐  │
│  │  Channel   │  │
│  │  Router    │  │
│  └──┬──┬──┬───┘  │
└─────┼──┼──┼──────┘
      │  │  │
      ▼  ▼  ▼
  Push Email In-App
  (FCM)(SMTP)(DB)
```

### Notification Types

| Type                    | Channels           | Trigger                                 |
|-------------------------|--------------------|-----------------------------------------|
| `streak_reminder`       | Push, Email        | No activity detected 2 hours before EOD |
| `streak_lost`           | Push, Email        | Streak broken (no freeze available)     |
| `leaderboard_promotion` | Push, In-App       | Promoted to higher league               |
| `leaderboard_demotion`  | Push, In-App       | Demoted to lower league                 |
| `achievement_earned`    | Push, In-App       | New achievement unlocked                |
| `friend_request`        | Push, In-App       | Received friend request                 |
| `friend_passed_you`     | Push               | Friend surpassed XP this week           |
| `weekly_report`         | Email              | Weekly summary of progress              |
| `subscription_expiring` | Push, Email        | Subscription expiring in 3 days         |
| `welcome`               | Email              | New user registration                   |
| `daily_goal_met`        | Push, In-App       | Daily XP goal achieved                  |
| `comeback`              | Push, Email        | User inactive for 3+ days               |

### Template Engine

Notification templates support variable interpolation and localization:

```json
{
  "templateId": "tmpl_streak_reminder",
  "type": "streak_reminder",
  "channels": {
    "push": {
      "title": "{{streakDays}}-day streak at risk! 🔥",
      "body": "Practice now to keep your {{streakDays}}-day streak alive, {{displayName}}!"
    },
    "email": {
      "subject": "Don't lose your {{streakDays}}-day streak!",
      "templateFile": "streak_reminder.html"
    }
  },
  "localizations": {
    "es": {
      "push": {
        "title": "¡Tu racha de {{streakDays}} días está en riesgo! 🔥",
        "body": "¡Practica ahora para mantener tu racha, {{displayName}}!"
      }
    }
  }
}
```

---

## 2.6 Caching Strategy

### Cache Layers

```
Request
  │
  ▼
┌─────────┐     ┌──────────┐     ┌──────────┐
│ CDN     │ ──► │ Redis    │ ──► │  MySQL   │
│ (Edge)  │     │ (L2)     │     │ (Source)  │
└─────────┘     └──────────┘     └──────────┘
 Static assets   Hot data         Persistent
 5 min - 24 hr   1 min - 1 hr     Source of truth
```

### Redis Cache Strategy

| Cache Key Pattern                          | TTL     | Invalidation Strategy          | Purpose                     |
|--------------------------------------------|---------|--------------------------------|-----------------------------|
| `user:{userId}:profile`                    | 15 min  | Write-through                  | User profile data           |
| `user:{userId}:session`                    | 15 min  | On token refresh               | Active session              |
| `user:{userId}:streak`                     | 5 min   | Event-driven                   | Streak status               |
| `user:{userId}:progress:{courseId}`        | 10 min  | Event-driven                   | Course progress             |
| `user:{userId}:daily-goal`                 | 5 min   | Event-driven                   | Daily goal progress         |
| `course:{courseId}:skill-tree`             | 1 hour  | Admin invalidation             | Skill tree structure        |
| `skill:{skillId}:exercises`               | 1 hour  | Admin invalidation             | Exercise content            |
| `leaderboard:{leagueId}:weekly`           | 1 min   | Sorted set, real-time updates  | Leaderboard rankings        |
| `languages:catalog`                        | 24 hour | Manual invalidation            | Available languages         |
| `shop:items`                               | 30 min  | Admin invalidation             | Shop catalog                |
| `ratelimit:{ip}:{endpoint}`               | 1 min   | Auto-expire                    | Rate limit counters         |
| `feature-flags:all`                        | 5 min   | Admin invalidation             | Feature flag config         |

### Cache Implementation Pattern

```csharp
public class CachedUserProfileService : IUserProfileService
{
    private readonly IDistributedCache _cache;
    private readonly IUserProfileRepository _repo;
    private readonly ILogger<CachedUserProfileService> _logger;

    public async Task<UserProfile?> GetProfileAsync(string userId)
    {
        var cacheKey = $"user:{userId}:profile";

        // Try cache first
        var cached = await _cache.GetStringAsync(cacheKey);
        if (cached != null)
        {
            _logger.LogDebug("Cache HIT for {Key}", cacheKey);
            return JsonSerializer.Deserialize<UserProfile>(cached);
        }

        _logger.LogDebug("Cache MISS for {Key}", cacheKey);

        // Fallback to database
        var profile = await _repo.GetByUserIdAsync(userId);
        if (profile != null)
        {
            await _cache.SetStringAsync(cacheKey,
                JsonSerializer.Serialize(profile),
                new DistributedCacheEntryOptions
                {
                    AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(15)
                });
        }

        return profile;
    }
}
```

### Cache Warming

On application startup and via scheduled jobs, the following caches are pre-warmed:

- Language catalog
- Popular course skill trees
- Shop item catalog
- Feature flag configuration

---

## 2.7 Rate Limiting

### Implementation

Rate limiting is implemented at the API Gateway layer using ASP.NET Core's built-in rate limiting middleware combined with Redis for distributed counting.

### Rate Limit Tiers

| Tier       | Requests/Min | Burst | Applied To              |
|------------|-------------|-------|-------------------------|
| Anonymous  | 20          | 5     | Unauthenticated requests|
| Free User  | 100         | 30    | Free tier users         |
| Premium    | 300         | 60    | Premium subscribers     |
| Admin      | 500         | 100   | Admin users             |
| System     | Unlimited   | -     | Service-to-service      |

### Endpoint-Specific Limits

| Endpoint Pattern        | Limit       | Window | Reason                        |
|-------------------------|-------------|--------|-------------------------------|
| `POST /auth/login`      | 5/min       | 1 min  | Brute force prevention        |
| `POST /auth/register`   | 3/min       | 1 min  | Abuse prevention              |
| `POST /auth/forgot-*`   | 3/hour      | 1 hour | Email abuse prevention        |
| `POST /sessions/*/answer`| 120/min    | 1 min  | Natural usage ceiling         |
| `POST /shop/purchase`   | 10/min      | 1 min  | Purchase abuse prevention     |
| `GET /leaderboards/*`   | 30/min      | 1 min  | Reduce leaderboard load       |

### Rate Limit Algorithm

**Sliding Window Counter** implemented with Redis:

```csharp
public class RateLimitMiddleware
{
    public async Task InvokeAsync(HttpContext context)
    {
        var key = $"ratelimit:{GetClientId(context)}:{GetEndpointKey(context)}";
        var window = TimeSpan.FromMinutes(1);

        var currentCount = await _redis.StringIncrementAsync(key);
        if (currentCount == 1)
        {
            await _redis.KeyExpireAsync(key, window);
        }

        var limit = GetRateLimit(context);
        context.Response.Headers["X-RateLimit-Limit"] = limit.ToString();
        context.Response.Headers["X-RateLimit-Remaining"] =
            Math.Max(0, limit - currentCount).ToString();

        if (currentCount > limit)
        {
            context.Response.StatusCode = 429;
            await context.Response.WriteAsJsonAsync(new
            {
                error = new
                {
                    code = "RATE_LIMIT_EXCEEDED",
                    message = "Too many requests. Please try again later.",
                    retryAfter = await _redis.KeyTimeToLiveAsync(key)
                }
            });
            return;
        }

        await _next(context);
    }
}
```

---

## 2.8 Logging & Monitoring

### Logging Strategy

**Structured Logging** via Serilog with the following sinks:

```
Application Logs ──► Serilog ──┬──► Console (Development)
                               ├──► File (Rolling, 100MB)
                               └──► Elasticsearch (Production)
```

### Log Levels

| Level       | Usage                                            | Example                                    |
|-------------|--------------------------------------------------|--------------------------------------------|
| `Verbose`   | Extremely detailed diagnostic info               | Cache key lookup details                   |
| `Debug`     | Internal state changes, useful during development| "User {UserId} cache hit for profile"      |
| `Information`| Normal operational events                       | "Lesson session started: {SessionId}"      |
| `Warning`   | Unexpected but recoverable situations            | "Streak freeze applied for {UserId}"       |
| `Error`     | Failures that need attention                     | "Payment processing failed: {Error}"       |
| `Fatal`     | Application-crashing errors                      | "Database connection pool exhausted"       |

### Log Format

```json
{
  "timestamp": "2024-06-15T14:30:00.123Z",
  "level": "Information",
  "messageTemplate": "Lesson completed: {SessionId} by {UserId} with {Accuracy}%",
  "properties": {
    "SessionId": "ses_abc123",
    "UserId": "usr_a1b2c3",
    "Accuracy": 83,
    "XpEarned": 20,
    "Duration": 180000,
    "RequestId": "req_xyz789",
    "CorrelationId": "cor_def456",
    "ServiceName": "LearningService",
    "Environment": "production",
    "MachineName": "learn-pod-3a2b1c"
  }
}
```

### Monitoring Stack

```
┌────────────────┐    ┌────────────────┐    ┌──────────────┐
│  Application   │    │  Prometheus    │    │   Grafana    │
│  (Metrics      │───►│  (Scrape &    │───►│ (Dashboards  │
│   Endpoint)    │    │   Store)       │    │  & Alerts)   │
└────────────────┘    └────────────────┘    └──────────────┘
```

### Key Metrics

| Metric                                  | Type      | Description                            |
|-----------------------------------------|-----------|----------------------------------------|
| `http_requests_total`                   | Counter   | Total HTTP requests by method/status   |
| `http_request_duration_seconds`         | Histogram | Request latency distribution           |
| `active_lesson_sessions`                | Gauge     | Currently active lesson sessions       |
| `lessons_completed_total`               | Counter   | Total lessons completed                |
| `xp_earned_total`                       | Counter   | Total XP earned across platform        |
| `auth_login_attempts_total`             | Counter   | Login attempts by result               |
| `cache_hit_ratio`                       | Gauge     | Redis cache hit percentage             |
| `rabbitmq_messages_published_total`     | Counter   | Messages published to RabbitMQ         |
| `rabbitmq_messages_consumed_total`      | Counter   | Messages consumed from RabbitMQ        |
| `db_query_duration_seconds`             | Histogram | Database query latency                 |
| `active_users_gauge`                    | Gauge     | Currently active users                 |
| `premium_subscriptions_active`          | Gauge     | Active premium subscriptions           |
| `streak_breaks_total`                   | Counter   | Daily streak breaks                    |
| `background_job_duration_seconds`       | Histogram | Background job execution time          |
| `background_job_failures_total`         | Counter   | Background job failures                |

### Alert Rules

| Alert                        | Condition                              | Severity | Action                       |
|------------------------------|----------------------------------------|----------|------------------------------|
| High Error Rate              | 5xx rate > 1% for 5 minutes            | Critical | Page on-call                 |
| High Latency                 | p99 > 2s for 5 minutes                 | Warning  | Slack alert                  |
| Database Connection Pool     | Usage > 80%                            | Warning  | Scale up / investigate       |
| Redis Memory                 | Usage > 85%                            | Warning  | Scale up / evict             |
| RabbitMQ Queue Depth         | > 10,000 messages for 10 minutes       | Warning  | Scale consumers              |
| Background Job Failure       | > 3 consecutive failures               | Error    | Slack alert + investigate    |
| Streak Job Not Completed     | Not completed by 00:30 UTC             | Critical | Page on-call                 |
| SSL Certificate Expiring     | < 14 days to expiry                    | Warning  | Auto-renew or alert          |

---

## 2.9 Health Checks

### Health Check Endpoints

| Endpoint                    | Purpose                              |
|-----------------------------|--------------------------------------|
| `GET /health`               | Basic liveness probe                 |
| `GET /health/ready`         | Readiness probe (all deps healthy)   |
| `GET /health/startup`       | Startup probe                        |

### Health Check Response

```json
{
  "status": "Healthy",
  "totalDuration": "00:00:00.0234567",
  "checks": {
    "mysql": {
      "status": "Healthy",
      "duration": "00:00:00.0120000",
      "data": {
        "connectionPool": "12/100"
      }
    },
    "redis": {
      "status": "Healthy",
      "duration": "00:00:00.0050000",
      "data": {
        "memoryUsage": "2.1 GB / 8 GB"
      }
    },
    "rabbitmq": {
      "status": "Healthy",
      "duration": "00:00:00.0080000",
      "data": {
        "queueDepth": 42
      }
    }
  }
}
```

### Dependency Health Matrix

| Dependency | Liveness | Readiness | Recovery Strategy                        |
|------------|----------|-----------|------------------------------------------|
| MySQL      | -        | Required  | Connection retry with exponential backoff|
| Redis      | -        | Degraded  | Fallback to direct DB queries            |
| RabbitMQ   | -        | Degraded  | Buffer events in memory, retry           |
| S3/Blob    | -        | Degraded  | Serve stale CDN content                  |
| FCM/APNS   | -        | Degraded  | Queue notifications for retry            |

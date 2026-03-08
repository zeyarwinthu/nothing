# 7. Additional Documents

## 7.1 Background Job Documentation

### Job Architecture

Background jobs in the platform are implemented using two patterns:

1. **Hosted Services** (`IHostedService`): Long-running or timer-based jobs within each microservice
2. **Message Consumers** (MassTransit + RabbitMQ): Event-driven async processing

```
┌──────────────────────────────────────────────────────────────┐
│                    Job Execution Layer                        │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  Scheduled   │  │   Event-     │  │  On-Demand Jobs    │  │
│  │  Jobs        │  │   Driven     │  │  (Admin-triggered) │  │
│  │  (Timers)    │  │   Jobs       │  │                    │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬───────────┘  │
│         │                 │                    │              │
│  ┌──────▼─────────────────▼────────────────────▼───────────┐  │
│  │              Job Runner / Scheduler                      │  │
│  │       (Hosted Services + MassTransit Consumers)          │  │
│  └──────────────────────────┬──────────────────────────────┘  │
│                             │                                 │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │                    Dependencies                          │  │
│  │   MySQL │ Redis │ RabbitMQ │ S3 │ External APIs          │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Scheduled Jobs Detail

#### StreakEvaluationJob

| Property      | Value                                                    |
|---------------|----------------------------------------------------------|
| **Service**   | Gamification Service                                      |
| **Schedule**  | Daily at 00:05 UTC                                        |
| **Priority**  | Critical                                                  |
| **Timeout**   | 60 minutes                                                |
| **Retry**     | 3 attempts with exponential backoff                       |
| **Idempotent**| Yes (can safely re-run)                                   |
| **Batch Size**| 1,000 users per batch                                     |
| **Dependencies** | MySQL (read/write), Redis (invalidation), RabbitMQ (events) |

**Logic:**
1. Query all users with `streaks.current_count > 0`
2. For each user (batched in parallel, 1,000 at a time):
   - Determine yesterday in user's timezone
   - Check for completed lessons on that date
   - Apply streak freeze or reset streak
3. Publish aggregate metrics to monitoring
4. Alert if completion time exceeds 30 minutes

**Monitoring:**
- `streak_evaluation_users_processed` (counter)
- `streak_evaluation_duration_seconds` (histogram)
- `streak_evaluation_errors_total` (counter)
- `streaks_broken_total` (counter per run)
- `streak_freezes_applied_total` (counter per run)

#### LeaderboardResetJob

| Property      | Value                                                    |
|---------------|----------------------------------------------------------|
| **Service**   | Leaderboard Service                                       |
| **Schedule**  | Weekly, Monday 00:00 UTC                                  |
| **Priority**  | Critical                                                  |
| **Timeout**   | 30 minutes                                                |
| **Retry**     | 3 attempts                                                |
| **Idempotent**| Yes (uses week identifier for deduplication)              |

**Logic:**
1. For each active league group:
   - Snapshot final rankings from Redis sorted sets
   - Write to `leaderboard_history`
   - Calculate promotions (top 10) and demotions (bottom 5)
   - Update `league_memberships` with outcomes
2. Create new league groups for the upcoming week
3. Assign all active users to new groups based on updated tiers
4. Clear Redis sorted sets for the completed week
5. Send promotion/demotion notifications

#### SkillStrengthDecayJob

| Property      | Value                                                    |
|---------------|----------------------------------------------------------|
| **Service**   | Progress Service                                          |
| **Schedule**  | Daily at 02:00 UTC                                        |
| **Priority**  | High                                                      |
| **Timeout**   | 45 minutes                                                |
| **Batch Size**| 5,000 word_strength records per batch                     |

**Logic:**
1. Query `word_strength` records where `next_review < NOW()`
2. For each record, apply decay formula:
   ```
   new_strength = strength * e^(-days_overdue / (interval * ease_factor))
   ```
3. Update strength value in database
4. Invalidate skill strength cache in Redis

#### NotificationSchedulerJob

| Property      | Value                                                    |
|---------------|----------------------------------------------------------|
| **Service**   | Notification Service                                      |
| **Schedule**  | Every 15 minutes                                          |
| **Priority**  | High                                                      |
| **Timeout**   | 10 minutes                                                |

**Logic:**
1. Query users who:
   - Have streak reminders enabled
   - Haven't completed a lesson today
   - Current time is within 2–4 hours before their reminder_time
   - Are not in quiet hours
2. Check notification throttling (max 1 streak reminder per day)
3. Publish notification events to RabbitMQ for dispatch

#### DataRetentionJob

| Property      | Value                                                    |
|---------------|----------------------------------------------------------|
| **Service**   | Shared Infrastructure Service                             |
| **Schedule**  | Daily at 03:00 UTC                                        |
| **Priority**  | Low                                                       |
| **Timeout**   | 120 minutes                                               |

**Logic:**
1. Purge expired refresh tokens (> 7 days past expiry)
2. Delete old notifications (> 90 days)
3. Archive old session answers (> 1 year) to archive table
4. Hard-delete soft-deleted accounts past 30-day recovery window
5. Aggregate and purge raw analytics events (> 6 months)
6. Clean up abandoned lesson sessions (> 7 days, status = 'in_progress')

### Event-Driven Jobs

| Consumer                          | Queue                         | Trigger Event         | Action                              |
|-----------------------------------|-------------------------------|-----------------------|-------------------------------------|
| `XpProgressConsumer`              | `progress.xp_update`         | `LessonCompleted`     | Update user XP, level, crowns       |
| `AchievementCheckConsumer`        | `gamif.achievement_check`     | `LessonCompleted`, `XpEarned` | Evaluate pending achievements |
| `LeaderboardXpConsumer`           | `leaderboard.xp_update`      | `XpEarned`            | Update Redis sorted set             |
| `PushNotificationConsumer`        | `notif.push`                  | Various               | Send push via FCM/APNS              |
| `EmailNotificationConsumer`       | `notif.email`                 | Various               | Send email via SendGrid             |
| `AnalyticsEventConsumer`          | `analytics.events`            | All events            | Write to analytics database          |
| `WelcomeFlowConsumer`            | `user.onboarding`             | `UserRegistered`      | Trigger welcome email sequence       |
| `SubscriptionEventConsumer`      | `payment.subscription`        | `SubscriptionCreated` | Update user premium_tier             |

### Job Error Handling

```csharp
public class JobRetryPolicy
{
    // Exponential backoff: 1s, 2s, 4s, 8s, 16s
    public static readonly int[] RetryDelaysMs = { 1000, 2000, 4000, 8000, 16000 };

    public static async Task ExecuteWithRetry(
        Func<Task> action,
        int maxRetries = 3,
        ILogger? logger = null)
    {
        for (int attempt = 0; attempt <= maxRetries; attempt++)
        {
            try
            {
                await action();
                return;
            }
            catch (Exception ex) when (attempt < maxRetries)
            {
                var delay = RetryDelaysMs[
                    Math.Min(attempt, RetryDelaysMs.Length - 1)];
                logger?.LogWarning(ex,
                    "Job attempt {Attempt} failed, retrying in {Delay}ms",
                    attempt + 1, delay);
                await Task.Delay(delay);
            }
        }
    }
}
```

---

## 7.2 Notification & Email Flow

### Notification Pipeline

```
Trigger Event (any service)
       │
       ▼
┌──────────────┐
│   RabbitMQ   │
│  Exchange:   │
│ notification │
└──────┬───────┘
       │
       ├──► Queue: notif.in_app ──► InAppNotificationConsumer
       │                              │
       │                              ├─► Insert into notifications table
       │                              └─► Update unread count in Redis
       │
       ├──► Queue: notif.push ──► PushNotificationConsumer
       │                            │
       │                            ├─► Check user preferences
       │                            ├─► Check quiet hours
       │                            ├─► Render template with localization
       │                            └─► Send via FCM (Android) / APNS (iOS)
       │
       └──► Queue: notif.email ──► EmailNotificationConsumer
                                     │
                                     ├─► Check email preferences
                                     ├─► Check unsubscribe status
                                     ├─► Render HTML email template
                                     └─► Send via SendGrid
```

### Email Templates

| Template ID              | Trigger                    | Subject Line                          |
|--------------------------|----------------------------|---------------------------------------|
| `welcome`                | User registration          | "Welcome to LingoLearn! 🎉"           |
| `email_verification`     | Registration               | "Verify your email address"            |
| `password_reset`         | Forgot password            | "Reset your password"                  |
| `streak_reminder`        | No activity near EOD       | "Your {{streak}} day streak is at risk! 🔥" |
| `streak_lost`            | Streak broken              | "Your streak was lost 😢"              |
| `weekly_report`          | Weekly (Sunday)            | "Your weekly learning report 📊"       |
| `subscription_welcome`   | New subscription           | "Welcome to Super Duolingo! ✨"        |
| `subscription_expiring`  | 3 days before expiry       | "Your subscription is expiring soon"   |
| `subscription_expired`   | Subscription expired       | "Your Super subscription has ended"    |
| `comeback_3day`          | 3 days inactive            | "We miss you! Come back and learn 🌟"  |
| `comeback_7day`          | 7 days inactive            | "Your skills are getting rusty! 📖"    |
| `friend_request`         | New friend request         | "{{name}} wants to be your friend!"    |
| `achievement_earned`     | Achievement unlocked       | "You earned a new achievement! 🏆"     |

### Push Notification Payloads

```json
{
  "notification": {
    "title": "Don't lose your 16-day streak! 🔥",
    "body": "Practice now to keep your streak alive!",
    "image": "https://cdn.lingolearn.com/notifications/streak.png"
  },
  "data": {
    "type": "streak_reminder",
    "deepLink": "/learn",
    "notificationId": "ntf_abc123",
    "userId": "usr_a1b2c3"
  },
  "android": {
    "priority": "high",
    "notification": {
      "channel_id": "streak_reminders",
      "sound": "streak_alarm"
    }
  },
  "apns": {
    "payload": {
      "aps": {
        "alert": {
          "title": "Don't lose your 16-day streak! 🔥",
          "body": "Practice now to keep your streak alive!"
        },
        "badge": 1,
        "sound": "streak_alarm.caf"
      }
    }
  }
}
```

### Notification Throttling Rules

| Notification Type        | Max Frequency      | Cooldown Period     |
|--------------------------|-------------------|---------------------|
| Streak reminder          | 1 per day         | 24 hours            |
| Leaderboard update       | 3 per day         | 4 hours             |
| Friend activity          | 5 per day         | 2 hours             |
| Achievement earned       | No limit          | -                   |
| Comeback reminder        | 1 per 3 days      | 72 hours            |
| Marketing/promotional    | 1 per week        | 7 days              |

### Quiet Hours Enforcement

```
Algorithm: ShouldSendNotification(userId, notificationType)
──────────────────────────────────────────────────────────
1. Fetch user's notification preferences
2. Check if notification type is enabled
3. Check quiet hours:
   a. Get user's timezone
   b. Calculate current time in user's timezone
   c. IF current_time >= quiet_hours_start
      AND current_time < quiet_hours_end:
      → Queue notification for delivery at quiet_hours_end
      → RETURN false
4. Check throttling:
   a. Query last notification of this type for this user
   b. IF cooldown period has not elapsed:
      → RETURN false
5. RETURN true
```

---

## 7.3 Security Considerations

### Authentication Security

| Measure                        | Implementation                                    |
|--------------------------------|---------------------------------------------------|
| Password Storage               | bcrypt with work factor 12                        |
| JWT Signing                    | RS256 (asymmetric) with 2048-bit RSA keys         |
| Token Expiry                   | Access: 15 min, Refresh: 30 days                  |
| Refresh Token Rotation         | New refresh token issued on each use; old revoked |
| Brute Force Protection         | Account lockout after 5 failed attempts (15 min)  |
| Password Complexity            | Min 8 chars, upper, lower, digit, special         |
| OAuth State Parameter          | CSRF protection for OAuth flows                    |
| Device Fingerprinting          | Track trusted devices for anomaly detection        |

### API Security

| Measure                        | Implementation                                    |
|--------------------------------|---------------------------------------------------|
| HTTPS Only                     | HSTS headers, TLS 1.3                             |
| Input Validation               | FluentValidation on all request models             |
| SQL Injection Prevention       | Entity Framework Core parameterized queries        |
| XSS Prevention                 | Output encoding, Content-Security-Policy headers   |
| CSRF Protection                | SameSite cookies, CSRF tokens for web              |
| Rate Limiting                  | Per-user and per-endpoint limits via Redis          |
| Request Size Limits            | Max 1MB request body, 5MB for file uploads         |
| API Key Management             | Rotating keys for service-to-service auth          |
| CORS Policy                    | Whitelist of allowed origins                        |

### Data Security

| Measure                        | Implementation                                    |
|--------------------------------|---------------------------------------------------|
| Encryption at Rest             | AES-256 for database encryption (MySQL TDE)        |
| Encryption in Transit          | TLS 1.3 for all connections                        |
| PII Handling                   | Email, name encrypted; separate PII store           |
| Data Masking                   | Logs mask email, password, tokens                  |
| Key Management                 | AWS KMS / Azure Key Vault                          |
| Backup Encryption              | All backups encrypted with separate keys            |
| Secrets Management             | Kubernetes Secrets, HashiCorp Vault                |

### Infrastructure Security

| Measure                        | Implementation                                    |
|--------------------------------|---------------------------------------------------|
| Network Segmentation           | VPC with private subnets for data layer            |
| WAF                            | AWS WAF / Cloudflare WAF                           |
| DDoS Protection                | CloudFront + Shield Advanced                       |
| Container Security             | Non-root containers, read-only filesystem          |
| Image Scanning                 | Trivy scanning in CI/CD pipeline                   |
| Dependency Scanning            | Dependabot + Snyk for vulnerability detection      |
| Audit Logging                  | All admin actions logged with user, action, timestamp |
| Penetration Testing            | Quarterly external pen tests                       |

### Security Headers

```csharp
app.Use(async (context, next) =>
{
    context.Response.Headers.Append(
        "Strict-Transport-Security",
        "max-age=31536000; includeSubDomains; preload");
    context.Response.Headers.Append(
        "X-Content-Type-Options", "nosniff");
    context.Response.Headers.Append(
        "X-Frame-Options", "DENY");
    context.Response.Headers.Append(
        "X-XSS-Protection", "0"); // Rely on CSP instead
    context.Response.Headers.Append(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'");
    context.Response.Headers.Append(
        "Referrer-Policy", "strict-origin-when-cross-origin");
    context.Response.Headers.Append(
        "Permissions-Policy",
        "camera=(), microphone=(self), geolocation=()");
    await next();
});
```

### Vulnerability Response

| Severity | Response SLA  | Actions                                            |
|----------|---------------|-----------------------------------------------------|
| Critical | 4 hours       | Immediate patch, hotfix deployment, incident report  |
| High     | 24 hours      | Patch in next deployment cycle, security review      |
| Medium   | 7 days        | Schedule fix in next sprint                         |
| Low      | 30 days       | Track in backlog, fix in next release               |

---

## 7.4 API Rate Limits

### Rate Limit Configuration

```csharp
// Program.cs - Rate Limiting Configuration
builder.Services.AddRateLimiter(options =>
{
    // Global rate limit
    options.GlobalLimiter = PartitionedRateLimiter
        .Create<HttpContext, string>(context =>
    {
        var userId = context.User?.FindFirst("sub")?.Value
            ?? context.Connection.RemoteIpAddress?.ToString()
            ?? "anonymous";

        return RateLimitPartition.GetSlidingWindowLimiter(
            userId, _ => new SlidingWindowRateLimiterOptions
            {
                PermitLimit = 100,
                Window = TimeSpan.FromMinutes(1),
                SegmentsPerWindow = 6,
                QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                QueueLimit = 10
            });
    });

    // Auth-specific rate limit
    options.AddPolicy("auth", context =>
        RateLimitPartition.GetFixedWindowLimiter(
            context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
            _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 10,
                Window = TimeSpan.FromMinutes(1)
            }));

    // Lesson submission rate limit
    options.AddPolicy("lesson", context =>
        RateLimitPartition.GetTokenBucketLimiter(
            context.User?.FindFirst("sub")?.Value ?? "anonymous",
            _ => new TokenBucketRateLimiterOptions
            {
                TokenLimit = 60,
                ReplenishmentPeriod = TimeSpan.FromMinutes(1),
                TokensPerPeriod = 60,
                QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                QueueLimit = 5
            }));

    options.OnRejected = async (context, _) =>
    {
        context.HttpContext.Response.StatusCode = 429;
        await context.HttpContext.Response.WriteAsJsonAsync(new
        {
            error = new
            {
                code = "RATE_LIMIT_EXCEEDED",
                message = "Too many requests. Please wait before trying again.",
                retryAfter = context.Lease.TryGetMetadata(
                    MetadataName.RetryAfter, out var retryAfter)
                    ? retryAfter.TotalSeconds : 60
            }
        });
    };
});
```

### Rate Limit Tiers Summary

| Tier         | Global/min | Auth/min | Lesson/min | Shop/min | Social/min |
|--------------|-----------|----------|------------|----------|------------|
| Anonymous    | 20        | 5        | 0          | 0        | 0          |
| Free User    | 100       | 10       | 60         | 20       | 30         |
| Premium User | 300       | 10       | 120        | 40       | 60         |
| Admin        | 500       | 20       | 120        | 60       | 60         |

### Rate Limit Bypass

Service-to-service communication using internal API keys bypasses rate limiting. Internal requests are identified by:
- `X-Internal-Service-Key` header matching the expected key
- Originating from internal Kubernetes network (pod CIDR)

---

## 7.5 Localization Strategy

### Supported Languages

The platform UI and notifications are localized for:

| Language   | Code  | Status     | Coverage |
|------------|-------|------------|----------|
| English    | `en`  | Complete   | 100%     |
| Spanish    | `es`  | Complete   | 100%     |
| French     | `fr`  | Complete   | 100%     |
| German     | `de`  | Complete   | 100%     |
| Portuguese | `pt`  | Complete   | 100%     |
| Japanese   | `ja`  | Complete   | 100%     |
| Korean     | `ko`  | Complete   | 100%     |
| Chinese    | `zh`  | Complete   | 100%     |
| Italian    | `it`  | Complete   | 98%      |
| Russian    | `ru`  | In Progress| 85%      |
| Arabic     | `ar`  | In Progress| 75%      |

### Localization Architecture

```
Client Request
  │
  │ Accept-Language: es
  │
  ▼
┌─────────────────┐
│   API Gateway   │
│ Extract locale  │
│ from header     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│    Service      │────►│  Localization    │
│  (any)          │     │  Provider        │
│                 │     │  (Redis cached)  │
│                 │◄────│                  │
└─────────────────┘     └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │  Translation DB  │
                        │  (JSON files /   │
                        │   Database)      │
                        └──────────────────┘
```

### Translation File Structure

```
/locales
  /en
    common.json
    notifications.json
    achievements.json
    errors.json
    emails.json
  /es
    common.json
    notifications.json
    achievements.json
    errors.json
    emails.json
  ...
```

**Example: `/locales/es/notifications.json`**
```json
{
  "streak_reminder": {
    "title": "¡Tu racha de {{days}} días está en riesgo! 🔥",
    "body": "¡Practica ahora para mantener tu racha, {{displayName}}!"
  },
  "streak_lost": {
    "title": "Tu racha se ha perdido 😢",
    "body": "Tu racha de {{days}} días ha terminado. ¡Empieza una nueva hoy!"
  },
  "achievement_earned": {
    "title": "¡Logro desbloqueado! 🏆",
    "body": "Has ganado \"{{achievementName}}\""
  },
  "leaderboard_promotion": {
    "title": "¡Ascendiste a {{leagueName}}! 📊",
    "body": "¡Felicitaciones! Sigue aprendiendo para seguir subiendo."
  }
}
```

### API Response Localization

- Error messages are localized based on `Accept-Language` header
- Notification content is localized based on user's configured language
- Course content (exercises, prompts) is managed separately per language pair
- Fallback chain: User's language → English → Error code only

### Server-Side Implementation

```csharp
public class LocalizationService : ILocalizationService
{
    private readonly IDistributedCache _cache;
    private readonly ILogger<LocalizationService> _logger;

    public async Task<string> GetStringAsync(
        string key, string locale, object? parameters = null)
    {
        var cacheKey = $"i18n:{locale}:{key}";
        var template = await _cache.GetStringAsync(cacheKey);

        if (template == null)
        {
            template = await LoadFromResourceAsync(key, locale);
            if (template == null)
            {
                // Fallback to English
                template = await LoadFromResourceAsync(key, "en");
            }
            if (template != null)
            {
                await _cache.SetStringAsync(cacheKey, template,
                    new DistributedCacheEntryOptions
                    {
                        AbsoluteExpirationRelativeToNow =
                            TimeSpan.FromHours(24)
                    });
            }
        }

        return parameters != null
            ? InterpolateTemplate(template ?? key, parameters)
            : template ?? key;
    }
}
```

---

## 7.6 A/B Testing Framework

### Architecture

```
┌───────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Client      │     │   A/B Testing    │     │    Analytics     │
│   Request     │────►│   Middleware      │────►│    Service       │
│               │     │                  │     │                  │
│               │     │  1. Get user ID  │     │  Track variant   │
│               │     │  2. Hash to      │     │  exposure and    │
│               │     │     variant      │     │  outcomes        │
│               │     │  3. Return       │     │                  │
│               │     │     config       │     │                  │
└───────────────┘     └──────────────────┘     └──────────────────┘
```

### A/B Test Data Model

```sql
CREATE TABLE ab_tests (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status ENUM('draft', 'running', 'paused', 'completed') DEFAULT 'draft',
    start_date DATETIME,
    end_date DATETIME,
    target_sample_size INT UNSIGNED DEFAULT 10000,
    traffic_percent DECIMAL(5,2) DEFAULT 100.00,
    created_by CHAR(36),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE ab_test_variants (
    id CHAR(36) PRIMARY KEY,
    test_id CHAR(36) NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    weight DECIMAL(5,2) NOT NULL DEFAULT 50.00,
    config_json JSON,
    FOREIGN KEY (test_id) REFERENCES ab_tests(id)
);

CREATE TABLE ab_test_assignments (
    id CHAR(36) PRIMARY KEY,
    test_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    variant_id CHAR(36) NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY idx_test_user (test_id, user_id),
    FOREIGN KEY (test_id) REFERENCES ab_tests(id),
    FOREIGN KEY (variant_id) REFERENCES ab_test_variants(id)
);

CREATE TABLE ab_test_events (
    id CHAR(36) PRIMARY KEY,
    test_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    variant_id CHAR(36) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_test_event (test_id, event_type),
    FOREIGN KEY (test_id) REFERENCES ab_tests(id)
);
```

### Variant Assignment Algorithm

```
Algorithm: AssignVariant(userId, testId)
───────────────────────────────────────
1. Check if user already has an assignment for this test
   → IF yes, return existing variant

2. Check if test is active and user is in target audience

3. Check traffic allocation:
   hash = SHA256(userId + testId)
   bucket = hash % 10000  // 0–9999
   IF bucket >= (traffic_percent * 100):
     → User is not in experiment, return control

4. Assign variant based on weights:
   variants = GetVariants(testId) ordered by weight
   cumulativeWeight = 0
   variantBucket = hash % 10000

   FOR EACH variant:
     cumulativeWeight += variant.weight * 100
     IF variantBucket < cumulativeWeight:
       → Assign user to this variant
       → Store assignment in ab_test_assignments
       → Cache assignment in Redis
       → RETURN variant

5. Record exposure event
```

### Example A/B Tests

| Test Name                    | Variants                              | Primary Metric        | Duration |
|------------------------------|---------------------------------------|-----------------------|----------|
| Streak Reminder Timing       | 2h before EOD vs 4h before EOD        | Streak retention rate | 4 weeks  |
| Lesson Length                 | 10 exercises vs 15 exercises          | Completion rate       | 6 weeks  |
| XP Bonus Amount              | +3 XP vs +5 XP for perfect lesson     | Perfect lesson rate   | 4 weeks  |
| Leaderboard Group Size       | 20 vs 30 vs 50 users                  | Weekly engagement     | 8 weeks  |
| Heart Regeneration Time      | 3h vs 4h vs 5h                        | Conversion to premium | 6 weeks  |
| Onboarding Flow              | With placement test vs without        | Day-7 retention       | 8 weeks  |

### Statistical Analysis

Tests are evaluated using:
- **Chi-squared test** for conversion metrics
- **T-test** for continuous metrics (XP, time)
- **Minimum sample size**: 1,000 users per variant
- **Significance threshold**: p < 0.05
- **Minimum detectable effect**: 5%
- **Power**: 80%

---

## 7.7 Feature Flag System

### Architecture

Feature flags control the rollout of new features without code deployments.

```
┌──────────────────┐
│  Feature Flag    │
│  Configuration   │
│  (Admin UI /     │
│   Database)      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│  Redis Cache     │────►│  Feature Flag    │
│  (5 min TTL)     │     │  Evaluator       │
└──────────────────┘     │  (in each svc)   │
                         └────────┬─────────┘
                                  │
                         ┌────────▼─────────┐
                         │  Decision:       │
                         │  Enabled/Disabled│
                         │  Per user/global │
                         └──────────────────┘
```

### Feature Flag Data Model

```sql
CREATE TABLE feature_flags (
    id CHAR(36) PRIMARY KEY,
    key_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    flag_type ENUM('boolean', 'percentage', 'user_list', 'property')
        NOT NULL DEFAULT 'boolean',
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    percentage DECIMAL(5,2) DEFAULT 0.00,
    config_json JSON,
    created_by CHAR(36),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE feature_flag_overrides (
    id CHAR(36) PRIMARY KEY,
    flag_id CHAR(36) NOT NULL,
    user_id CHAR(36),
    user_segment VARCHAR(50),
    enabled BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flag_id) REFERENCES feature_flags(id)
);
```

### Flag Types

| Type         | Description                                    | Example                            |
|--------------|------------------------------------------------|------------------------------------|
| `boolean`    | Simple on/off toggle                           | `enable_dark_mode`                 |
| `percentage` | Gradually roll out to % of users               | `new_exercise_type` at 25%         |
| `user_list`  | Enable for specific users                      | `beta_features` for beta testers   |
| `property`   | Enable based on user properties                | `premium_only_feature`             |

### Feature Flag Evaluation

```csharp
public class FeatureFlagService : IFeatureFlagService
{
    private readonly IDistributedCache _cache;
    private readonly IFeatureFlagRepository _repo;

    public async Task<bool> IsEnabledAsync(
        string flagKey, string? userId = null)
    {
        var flag = await GetFlagAsync(flagKey);
        if (flag == null) return false;

        // Check user-specific overrides first
        if (userId != null)
        {
            var @override = await GetOverrideAsync(flag.Id, userId);
            if (@override != null)
                return @override.Enabled;
        }

        // Evaluate based on flag type
        return flag.FlagType switch
        {
            "boolean" => flag.Enabled,

            "percentage" => IsInPercentage(
                userId ?? "anonymous", flagKey, flag.Percentage),

            "user_list" => userId != null &&
                flag.ConfigJson.UserList.Contains(userId),

            "property" => userId != null &&
                await EvaluatePropertyRules(flag, userId),

            _ => false
        };
    }

    private bool IsInPercentage(
        string userId, string flagKey, decimal percentage)
    {
        var hash = ComputeHash($"{userId}:{flagKey}");
        var bucket = hash % 10000;
        return bucket < (percentage * 100);
    }
}
```

### Active Feature Flags (Example)

| Flag Key                      | Type       | Status     | Description                          |
|-------------------------------|------------|------------|--------------------------------------|
| `enable_speaking_exercises`   | percentage | 85%        | Speech recognition exercises         |
| `new_crown_system`            | percentage | 50%        | Revised crown progression            |
| `enable_stories`              | boolean    | enabled    | Story-based lessons                  |
| `holiday_theme`               | boolean    | disabled   | Seasonal UI theme                    |
| `premium_offline_mode`        | property   | premium    | Offline lesson downloads             |
| `beta_new_exercise_type`      | user_list  | beta users | New tap-to-complete exercise type    |
| `reduced_ad_frequency`        | percentage | 25%        | A/B test: fewer but longer ads       |

### Feature Flag API

```
GET /api/v1/feature-flags
Authorization: Bearer <token>
```

**Response:**
```json
{
  "data": {
    "flags": {
      "enable_speaking_exercises": true,
      "new_crown_system": false,
      "enable_stories": true,
      "holiday_theme": false,
      "premium_offline_mode": true,
      "beta_new_exercise_type": false,
      "reduced_ad_frequency": true
    },
    "evaluatedAt": "2024-06-15T14:30:00Z",
    "cacheUntil": "2024-06-15T14:35:00Z"
  }
}
```

---

## 7.8 Data Privacy & GDPR Compliance

### Data Classification

| Classification | Examples                                  | Handling                           |
|---------------|-------------------------------------------|------------------------------------|
| Public         | Display name, avatar, achievements        | Visible to other users              |
| Private        | Email, age, learning progress             | Visible only to account owner       |
| Sensitive      | Password hash, payment data               | Encrypted, access-controlled        |
| System         | Logs, metrics, internal IDs               | Not exposed to users                |

### GDPR Rights Implementation

| Right                  | Implementation                                              |
|------------------------|-------------------------------------------------------------|
| Right to Access        | `GET /api/v1/users/me/data-export` → generates full export  |
| Right to Rectification | `PATCH /api/v1/users/me` → edit personal data               |
| Right to Erasure       | `DELETE /api/v1/users/me` → 30-day soft delete, then purge  |
| Right to Portability   | Data export in JSON format                                   |
| Right to Object        | Opt-out of marketing, analytics via settings                 |
| Right to Restrict      | Suspend processing via support request                       |

### Data Export Format

```json
{
  "exportDate": "2024-06-15T14:30:00Z",
  "userData": {
    "profile": {
      "email": "user@example.com",
      "displayName": "LinguaLearner",
      "joinedAt": "2024-01-15T10:30:00Z"
    },
    "learningData": {
      "courses": [...],
      "lessonsCompleted": 156,
      "totalXp": 4520
    },
    "socialData": {
      "friends": [...],
      "achievements": [...]
    },
    "settings": {...},
    "subscriptionHistory": [...],
    "notifications": [...]
  }
}
```

### Data Deletion Process

```
User requests account deletion
       │
       ▼
┌────────────────┐
│ Soft delete     │
│ status='deleted'│
│ deleted_at=NOW()│
└───────┬────────┘
        │
        │ 30-day grace period
        │ (user can recover)
        │
        ▼
┌────────────────┐
│ Hard delete     │
│ (daily job)     │
│                 │
│ 1. Delete PII   │
│ 2. Anonymize    │
│    analytics    │
│ 3. Remove from  │
│    leaderboards │
│ 4. Delete       │
│    social data  │
│ 5. Revoke all   │
│    tokens       │
│ 6. Delete from  │
│    backups (90d)│
└────────────────┘
```

### Cookie Consent

| Cookie Type     | Purpose                        | Duration  | Requires Consent |
|-----------------|--------------------------------|-----------|------------------|
| Session         | Authentication, CSRF            | Session   | No (essential)    |
| Preferences     | Language, timezone, dark mode    | 1 year    | No (essential)    |
| Analytics       | Usage tracking, A/B tests       | 1 year    | Yes              |
| Marketing       | Ad targeting, remarketing        | 90 days   | Yes              |

### Audit Trail

All data access and modification is logged:

```json
{
  "auditId": "aud_abc123",
  "timestamp": "2024-06-15T14:30:00Z",
  "userId": "usr_a1b2c3",
  "action": "data_export_requested",
  "resource": "user_data",
  "ipAddress": "192.168.1.1",
  "userAgent": "LingoLearn/3.2.1 iOS/17.0",
  "result": "success",
  "details": {
    "exportFormat": "json",
    "dataCategories": ["profile", "learning", "social"]
  }
}
```

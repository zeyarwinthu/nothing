# 3. System Design Document (SDD)

## 3.1 High-Level Architecture

### Architecture Overview

The platform follows a microservices architecture deployed on Kubernetes, with an API Gateway as the single entry point. Services communicate synchronously via HTTP/gRPC and asynchronously via RabbitMQ events.

```
                              ┌──────────────────┐
                              │   CloudFront /   │
                              │   Cloudflare     │
                              │      (CDN)       │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────────────────────────┐
                    │           Load Balancer (L7)          │
                    │          (AWS ALB / Azure LB)         │
                    └──────────────────┬───────────────────┘
                                       │
                    ┌──────────────────────────────────────┐
                    │         API Gateway (YARP)            │
                    │  ┌──────┬──────┬──────┬──────────┐   │
                    │  │ Auth │ Rate │Route │Correlation│   │
                    │  │Check │Limit │ ing  │  ID Gen   │   │
                    │  └──────┴──────┴──────┴──────────┘   │
                    └───┬────┬────┬────┬────┬────┬────┬────┘
                        │    │    │    │    │    │    │
           ┌────────────┘    │    │    │    │    │    └────────────┐
           │                 │    │    │    │    │                 │
     ┌─────▼────┐   ┌───────▼──┐│┌───▼────┐│┌──▼──────┐   ┌─────▼────┐
     │  Auth    │   │ Learning │││Progress │││Gamific. │   │  Social  │
     │ Service  │   │ Service  │││ Service │││ Service │   │ Service  │
     └─────┬────┘   └─────┬───┘│└────┬────┘│└────┬────┘   └─────┬────┘
           │               │    │     │     │     │              │
     ┌─────▼────┐   ┌─────▼──┐│┌────▼───┐│┌────▼─────┐  ┌─────▼────┐
     │  User    │   │ Course ││├─────────┘││Leaderboard│  │Notific.  │
     │ Service  │   │Service ││           ││ Service   │  │ Service  │
     └──────────┘   └────────┘│           │└───────────┘  └──────────┘
                              │           │
                        ┌─────▼──┐  ┌─────▼────┐
                        │Content │  │ Payment  │
                        │Service │  │ Service  │
                        └────────┘  └──────────┘

     ┌────────────────────────────────────────────────────────────┐
     │                    Data Layer                               │
     │  ┌──────────┐  ┌───────────┐  ┌────────────┐  ┌────────┐  │
     │  │MySQL     │  │ Redis     │  │ RabbitMQ   │  │  S3    │  │
     │  │(Primary/ │  │ (Cluster) │  │ (Cluster)  │  │(Media) │  │
     │  │ Replica) │  │           │  │            │  │        │  │
     │  └──────────┘  └───────────┘  └────────────┘  └────────┘  │
     └────────────────────────────────────────────────────────────┘

     ┌────────────────────────────────────────────────────────────┐
     │                  Observability Layer                        │
     │  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
     │  │Prometheus  │  │ Grafana  │  │  ELK     │  │ Jaeger  │  │
     │  │(Metrics)   │  │(Dashbd)  │  │(Logging) │  │(Tracing)│  │
     │  └────────────┘  └──────────┘  └──────────┘  └─────────┘  │
     └────────────────────────────────────────────────────────────┘
```

### Cross-Cutting Concerns

| Concern              | Implementation                                    |
|----------------------|---------------------------------------------------|
| Authentication       | JWT validation middleware at API Gateway           |
| Rate Limiting        | Redis-backed sliding window at API Gateway         |
| Correlation IDs      | Generated at Gateway, propagated via headers       |
| Circuit Breaking     | Polly library in each service                      |
| Service Discovery    | Kubernetes DNS-based service discovery             |
| Configuration        | Kubernetes ConfigMaps + Secrets                    |
| Health Monitoring    | ASP.NET Core health checks + Kubernetes probes     |
| API Versioning       | URL-based (/api/v1/) at Gateway level              |

---

## 3.2 Sequence Diagrams

### Sequence 1: User Login

```
Client          API Gateway      Auth Service       Redis           MySQL
  │                  │                │                │               │
  │──POST /login────►│                │                │               │
  │                  │──Validate JWT──►│                │               │
  │                  │                │──Check lockout─►│               │
  │                  │                │◄──Not locked────│               │
  │                  │                │──Get user──────►│(cache miss)   │
  │                  │                │                │──Query────────►│
  │                  │                │                │◄──User data───│
  │                  │                │◄──User data────│               │
  │                  │                │                │               │
  │                  │                │  Verify bcrypt  │               │
  │                  │                │  password hash  │               │
  │                  │                │                │               │
  │                  │                │──Generate JWT   │               │
  │                  │                │──Store session─►│               │
  │                  │                │──Cache user────►│               │
  │                  │                │                │               │
  │                  │                │──Publish event─►│(RabbitMQ)     │
  │                  │                │  "UserLoggedIn" │               │
  │                  │                │                │               │
  │                  │◄──200 + JWT────│                │               │
  │◄──200 + JWT──────│                │                │               │
```

### Sequence 2: Complete a Lesson Exercise

```
Client        API Gateway     Learning Svc    Course Svc     MySQL       Redis      RabbitMQ
  │                │               │              │            │           │            │
  │──POST answer──►│               │              │            │           │            │
  │                │──Forward─────►│              │            │           │            │
  │                │               │──Get exercise─►           │            │           │
  │                │               │◄──Exercise────│           │            │           │
  │                │               │              │            │           │            │
  │                │               │  Evaluate answer          │           │            │
  │                │               │  (Levenshtein check,      │           │            │
  │                │               │   normalize accents,      │           │            │
  │                │               │   check alternatives)     │           │            │
  │                │               │              │            │           │            │
  │                │               │──Store answer─────────────►           │            │
  │                │               │──Update hearts───────────────────────►│            │
  │                │               │──Publish "AnswerSubmitted"────────────────────────►│
  │                │               │              │            │           │            │
  │                │◄──Result──────│              │            │           │            │
  │◄──200 + result─│              │              │            │           │            │
  │                │               │              │            │           │            │
  │                │               │              │    Event consumers:     │            │
  │                │               │              │    - Progress: +XP      │            │
  │                │               │              │    - Gamification: check │            │
  │                │               │              │      achievements       │            │
  │                │               │              │    - Analytics: record   │            │
```

### Sequence 3: Lesson Completion Flow

```
Client       API Gateway    Learning Svc    Progress Svc   Gamif. Svc   Leaderboard   Notif. Svc
  │               │              │               │              │            │             │
  │──POST         │              │               │              │            │             │
  │  complete────►│              │               │              │            │             │
  │               │──Forward────►│               │              │            │             │
  │               │              │──Validate      │              │            │             │
  │               │              │  session       │              │            │             │
  │               │              │──Calculate     │              │            │             │
  │               │              │  results       │              │            │             │
  │               │              │──Publish "LessonCompleted"    │            │             │
  │               │              │               │              │            │             │
  │               │              │            ┌──▼───┐          │            │             │
  │               │              │            │Update│          │            │             │
  │               │              │            │XP,   │          │            │             │
  │               │              │            │crowns│          │            │             │
  │               │              │            │level │          │            │             │
  │               │              │            └──┬───┘          │            │             │
  │               │              │               │              │            │             │
  │               │              │            Publish "XpEarned"│            │             │
  │               │              │               │              │            │             │
  │               │              │               │         ┌────▼────┐       │             │
  │               │              │               │         │Check    │       │             │
  │               │              │               │         │streak   │       │             │
  │               │              │               │         │achievmts│       │             │
  │               │              │               │         └────┬────┘       │             │
  │               │              │               │              │            │             │
  │               │              │               │         Update streak     │             │
  │               │              │               │              │            │             │
  │               │              │               │         ┌────▼──────────► │             │
  │               │              │               │         │Update weekly XP │             │
  │               │              │               │         └─────────────────┘             │
  │               │              │               │              │                          │
  │               │              │               │         If achievement earned:          │
  │               │              │               │              │──Publish──────────────── ►│
  │               │              │               │              │  "AchievementEarned"      │
  │               │              │               │              │                     Push  │
  │               │              │               │              │                     notif │
  │               │◄──Result─────│               │              │            │             │
  │◄──200 result──│              │               │              │            │             │
```

### Sequence 4: Streak Evaluation (Background Job)

```
Timer            Streak Job       MySQL          Redis        RabbitMQ      Notif. Svc
  │                   │              │              │             │             │
  │──Trigger at       │              │              │             │             │
  │  00:05 UTC───────►│              │              │             │             │
  │                   │──Batch fetch  │              │             │             │
  │                   │  users with   │              │             │             │
  │                   │  active streaks│             │             │             │
  │                   │◄──User batch──│              │             │             │
  │                   │              │              │             │             │
  │                   │  For each user:              │             │             │
  │                   │              │              │             │             │
  │                   │──Get last     │              │             │             │
  │                   │  activity date │             │             │             │
  │                   │              │              │             │             │
  │                   │  If no activity yesterday:   │             │             │
  │                   │  ├─ Check freeze inventory   │             │             │
  │                   │  │                           │             │             │
  │                   │  ├─ If freeze available:     │             │             │
  │                   │  │  ├─ Apply freeze          │             │             │
  │                   │  │  ├─ Decrement inventory   │             │             │
  │                   │  │  └─ Publish "StreakFrozen" │             │             │
  │                   │  │                           │             │             │
  │                   │  └─ If no freeze:            │             │             │
  │                   │     ├─ Reset streak to 0     │             │             │
  │                   │     ├─ Invalidate cache──────►             │             │
  │                   │     └─ Publish "StreakBroken"─────────────►│             │
  │                   │              │              │             │──Push notif──►
  │                   │              │              │             │  "streak_lost"│
  │                   │              │              │             │             │
  │                   │  Log summary  │              │             │             │
  │                   │  metrics      │              │             │             │
```

### Sequence 5: Weekly Leaderboard Reset

```
Timer        Leaderboard Job      Redis          MySQL         RabbitMQ      Notif. Svc
  │                │                 │              │              │             │
  │──Mon 00:00────►│                 │              │              │             │
  │                │──Get all leagues─►              │              │             │
  │                │◄──League data────│              │              │             │
  │                │                 │              │              │             │
  │                │  For each league:│              │              │             │
  │                │                 │              │              │             │
  │                │──Get final       │              │              │             │
  │                │  rankings───────►│              │              │             │
  │                │◄──Sorted set─────│              │              │             │
  │                │                 │              │              │             │
  │                │──Archive to──────┼──────────────►              │             │
  │                │  leaderboard_    │              │              │             │
  │                │  history         │              │              │             │
  │                │                 │              │              │             │
  │                │  Calculate promotions           │              │             │
  │                │  & demotions     │              │              │             │
  │                │                 │              │              │             │
  │                │──Update league   │              │              │             │
  │                │  memberships─────┼──────────────►              │             │
  │                │                 │              │              │             │
  │                │──Clear sorted────►              │              │             │
  │                │  sets            │              │              │             │
  │                │                 │              │              │             │
  │                │──Publish events──┼──────────────┼──────────────►             │
  │                │  "UserPromoted"  │              │              │──Push notifs─►
  │                │  "UserDemoted"   │              │              │             │
  │                │                 │              │              │             │
  │                │──Reassign users  │              │              │             │
  │                │  to new league   │              │              │             │
  │                │  groups          │              │              │             │
```

---

## 3.3 Component Responsibilities

### API Gateway

| Responsibility                | Details                                             |
|-------------------------------|-----------------------------------------------------|
| SSL Termination               | Handles HTTPS, forwards HTTP internally             |
| Authentication                | Validates JWT tokens, rejects invalid requests       |
| Rate Limiting                 | Enforces per-user and per-endpoint limits            |
| Request Routing               | Routes to appropriate microservice                   |
| Correlation ID Generation     | Generates unique request ID for tracing              |
| Request/Response Logging      | Logs all requests for audit trail                    |
| Response Compression          | gzip/Brotli compression for responses                |
| CORS Management               | Handles cross-origin requests                        |
| API Versioning                | Routes to correct service version                    |
| Circuit Breaking              | Fails fast when downstream services are unhealthy    |

### Service Responsibilities Matrix

| Service          | Owns Data           | Publishes Events              | Consumes Events                  |
|------------------|---------------------|-------------------------------|----------------------------------|
| Auth             | Users, Tokens       | UserRegistered, UserLoggedIn  | -                                |
| User             | Profiles, Settings  | ProfileUpdated                | UserRegistered                   |
| Course           | Courses, Skills     | CourseEnrolled                | -                                |
| Learning         | Sessions, Answers   | LessonCompleted, AnswerSubmitted | -                             |
| Progress         | XP, Crowns, Levels  | XpEarned, LevelUp             | LessonCompleted                  |
| Gamification     | Streaks, Achievements| StreakBroken, AchievementEarned| XpEarned, LessonCompleted      |
| Leaderboard      | Rankings, Leagues   | UserPromoted, UserDemoted     | XpEarned                         |
| Social           | Friends, Feed       | -                             | AchievementEarned, LevelUp       |
| Notification     | Notifications       | -                             | All notification-trigger events  |
| Analytics        | Events, Metrics     | -                             | All events                       |
| Payment          | Subscriptions       | SubscriptionCreated           | -                                |
| Content          | Media, Audio        | -                             | -                                |

---

## 3.4 Scaling Strategy

### Horizontal Scaling

Each microservice is independently scalable. Kubernetes Horizontal Pod Autoscaler (HPA) manages scaling based on CPU, memory, and custom metrics.

```
┌──────────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                      │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Auth Service                                     │    │
│  │  min: 2 │ max: 10 │ target CPU: 60%              │    │
│  │  ┌────┐ ┌────┐ ┌────┐                            │    │
│  │  │Pod1│ │Pod2│ │Pod3│ ◄── HPA scales based on    │    │
│  │  └────┘ └────┘ └────┘     login traffic           │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Learning Service                                 │    │
│  │  min: 3 │ max: 20 │ target CPU: 50%              │    │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐             │    │
│  │  │Pod1│ │Pod2│ │Pod3│ │Pod4│ │Pod5│ ◄── Most     │    │
│  │  └────┘ └────┘ └────┘ └────┘ └────┘    traffic   │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Leaderboard Service                              │    │
│  │  min: 2 │ max: 8 │ custom: active_queries        │    │
│  │  ┌────┐ ┌────┐                                    │    │
│  │  │Pod1│ │Pod2│                                    │    │
│  │  └────┘ └────┘                                    │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### Scaling Parameters

| Service           | Min Pods | Max Pods | Scale Metric            | Target Value |
|-------------------|----------|----------|-------------------------|--------------|
| API Gateway       | 3        | 15       | CPU utilization          | 50%          |
| Auth Service      | 2        | 10       | CPU utilization          | 60%          |
| Learning Service  | 3        | 20       | Active sessions          | 500/pod      |
| Course Service    | 2        | 8        | Requests/sec             | 200/pod      |
| Progress Service  | 2        | 12       | RabbitMQ queue depth     | 1000 msgs    |
| Gamification Svc  | 2        | 10       | RabbitMQ queue depth     | 1000 msgs    |
| Leaderboard Svc   | 2        | 8        | CPU utilization          | 60%          |
| Notification Svc  | 2        | 10       | Queue depth              | 2000 msgs    |
| Analytics Svc     | 2        | 6        | Queue depth              | 5000 msgs    |

### Database Scaling

```
                    ┌──────────────────┐
                    │   MySQL Primary  │
                    │   (Writes)       │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │  Replica  │ │  Replica  │ │  Replica  │
        │   (Read)  │ │   (Read)  │ │   (Read)  │
        │  Region A │ │  Region B │ │ Analytics │
        └───────────┘ └───────────┘ └───────────┘
```

**Read/Write Splitting:**
- All writes go to the primary instance
- Reads are distributed across replicas using Entity Framework Core's read-replica configuration
- Analytics queries are routed to a dedicated analytics replica to avoid impact on production reads

### Redis Scaling

```
┌────────────────────────────────────────┐
│         Redis Cluster (6 nodes)        │
│                                        │
│  ┌──────────┐  ┌──────────┐           │
│  │ Master 1 │  │ Replica 1│           │
│  │ Slots    │  │          │           │
│  │ 0-5460   │  │          │           │
│  └──────────┘  └──────────┘           │
│                                        │
│  ┌──────────┐  ┌──────────┐           │
│  │ Master 2 │  │ Replica 2│           │
│  │ Slots    │  │          │           │
│  │ 5461-    │  │          │           │
│  │ 10922    │  │          │           │
│  └──────────┘  └──────────┘           │
│                                        │
│  ┌──────────┐  ┌──────────┐           │
│  │ Master 3 │  │ Replica 3│           │
│  │ Slots    │  │          │           │
│  │ 10923-   │  │          │           │
│  │ 16383    │  │          │           │
│  └──────────┘  └──────────┘           │
└────────────────────────────────────────┘
```

---

## 3.5 Load Handling

### Traffic Patterns

| Time Period          | Traffic Level | Notes                                |
|----------------------|---------------|--------------------------------------|
| 06:00–09:00 local    | High          | Morning practice before work/school  |
| 12:00–14:00 local    | Medium-High   | Lunch break practice                 |
| 18:00–22:00 local    | Peak          | Evening practice window              |
| 22:00–06:00 local    | Low           | Overnight maintenance window         |
| Monday               | Highest       | Weekly leaderboard reset motivation  |
| Sunday night         | High          | Last chance for weekly leaderboard   |

### Load Handling Strategies

| Strategy               | Implementation                              | Trigger                           |
|------------------------|---------------------------------------------|-----------------------------------|
| Auto-scaling           | Kubernetes HPA                              | CPU > 50%, custom metrics         |
| Connection Pooling     | HikariCP-style pool for MySQL               | Startup configuration             |
| Read Replicas          | MySQL read replicas for GET requests        | Always active                     |
| CDN Offloading         | Static assets served from CDN edge          | Always active                     |
| Response Caching       | Redis cache for hot data                    | Cache hit rate < 80%              |
| Queue Buffering        | RabbitMQ absorbs event spikes               | Traffic spikes                    |
| Circuit Breaking       | Polly circuit breaker per service           | > 50% failure rate in 30s window  |
| Graceful Degradation   | Serve stale cache data when DB slow         | DB latency > 2s                   |
| Request Coalescing     | Deduplicate identical concurrent requests   | Leaderboard queries               |
| Backpressure           | RabbitMQ prefetch count limits              | Consumer processing slow          |

### Capacity Planning

| Metric                  | Current Capacity | Growth Target (1 yr) |
|-------------------------|------------------|----------------------|
| Daily Active Users      | 500K             | 2M                   |
| Peak Concurrent Users   | 50K              | 200K                 |
| API Requests/sec        | 5K               | 20K                  |
| Lessons/day             | 2M               | 8M                   |
| Database Size           | 500 GB           | 2 TB                 |
| Redis Memory            | 8 GB             | 32 GB                |
| Events/day (RabbitMQ)   | 10M              | 40M                  |

---

## 3.6 Queueing System

### RabbitMQ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      RabbitMQ Cluster                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                 Exchanges                                 │    │
│  │                                                           │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐  │    │
│  │  │  learning   │  │  progress   │  │  gamification    │  │    │
│  │  │  (topic)    │  │  (topic)    │  │  (topic)         │  │    │
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬─────────┘  │    │
│  │         │                │                   │            │    │
│  └─────────┼────────────────┼───────────────────┼────────────┘    │
│            │                │                   │                 │
│  ┌─────────┼────────────────┼───────────────────┼────────────┐    │
│  │         │           Queues                   │            │    │
│  │         │                │                   │            │    │
│  │  ┌──────▼──────┐  ┌─────▼──────┐  ┌────────▼────────┐   │    │
│  │  │ progress.   │  │ gamif.     │  │ leaderboard.    │   │    │
│  │  │ xp_update   │  │ achievement│  │ xp_update       │   │    │
│  │  │             │  │ _check     │  │                  │   │    │
│  │  └─────────────┘  └────────────┘  └──────────────────┘   │    │
│  │                                                           │    │
│  │  ┌─────────────┐  ┌────────────┐  ┌──────────────────┐   │    │
│  │  │ analytics.  │  │ notif.     │  │ notif.           │   │    │
│  │  │ events      │  │ push       │  │ email            │   │    │
│  │  └─────────────┘  └────────────┘  └──────────────────┘   │    │
│  └───────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### Event Catalog

| Event Name            | Exchange        | Routing Key                    | Published By    | Consumed By                                |
|-----------------------|-----------------|--------------------------------|-----------------|--------------------------------------------|
| `UserRegistered`      | `user`          | `user.registered`              | Auth Service    | User Svc, Gamif. Svc, Notif. Svc, Analytics|
| `UserLoggedIn`        | `user`          | `user.logged_in`               | Auth Service    | Analytics                                  |
| `LessonStarted`      | `learning`      | `learning.lesson.started`      | Learning Svc    | Analytics                                  |
| `AnswerSubmitted`     | `learning`      | `learning.answer.submitted`    | Learning Svc    | Analytics                                  |
| `LessonCompleted`    | `learning`      | `learning.lesson.completed`    | Learning Svc    | Progress, Gamif., Analytics                |
| `XpEarned`           | `progress`      | `progress.xp.earned`           | Progress Svc    | Leaderboard, Analytics                     |
| `LevelUp`            | `progress`      | `progress.level.up`            | Progress Svc    | Notif., Social, Analytics                  |
| `StreakExtended`     | `gamification`  | `gamif.streak.extended`        | Gamif. Svc      | Analytics                                  |
| `StreakBroken`       | `gamification`  | `gamif.streak.broken`          | Gamif. Svc      | Notif., Analytics                          |
| `AchievementEarned` | `gamification`  | `gamif.achievement.earned`     | Gamif. Svc      | Notif., Social, Analytics                  |
| `SubscriptionCreated`| `payment`       | `payment.subscription.created` | Payment Svc     | User Svc, Notif., Analytics                |
| `FriendRequestSent` | `social`        | `social.friend.request_sent`   | Social Svc      | Notif.                                     |

### Event Schema Example

```json
{
  "eventId": "evt_abc123def456",
  "eventType": "LessonCompleted",
  "version": "1.0",
  "timestamp": "2024-06-15T14:30:00.123Z",
  "correlationId": "cor_xyz789",
  "source": "learning-service",
  "data": {
    "userId": "usr_a1b2c3d4",
    "sessionId": "ses_abc123",
    "lessonId": "lsn_basics1_02",
    "courseId": "crs_spanish_en",
    "xpEarned": 15,
    "accuracy": 0.83,
    "durationMs": 180000,
    "exercisesCompleted": 6,
    "correctAnswers": 5
  }
}
```

### Queue Configuration

| Queue                      | Durable | Prefetch | DLQ Enabled | Max Retries | TTL        |
|----------------------------|---------|----------|-------------|-------------|------------|
| `progress.xp_update`      | Yes     | 10       | Yes         | 3           | 24 hours   |
| `gamif.achievement_check`  | Yes     | 5        | Yes         | 3           | 24 hours   |
| `leaderboard.xp_update`   | Yes     | 20       | Yes         | 3           | 12 hours   |
| `notif.push`               | Yes     | 50       | Yes         | 5           | 48 hours   |
| `notif.email`              | Yes     | 20       | Yes         | 5           | 48 hours   |
| `analytics.events`         | Yes     | 100      | No          | 1           | 72 hours   |

### Dead Letter Queue Strategy

Failed messages are routed to a Dead Letter Exchange (DLX) after max retries:

```
Original Queue ──(fail)──► DLQ ──(manual review)──► Retry or Discard
                                                      │
                                                      ▼
                                                   Alert via
                                                   Grafana
```

---

## 3.7 CDN Usage

### CDN Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  CloudFront / Cloudflare                  │
│                                                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│  │  Edge PoP  │  │  Edge PoP  │  │  Edge PoP  │  ...    │
│  │  US-East   │  │  EU-West   │  │  AP-South  │         │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘         │
│         │               │               │                │
│         └───────────────┼───────────────┘                │
│                         │                                │
└─────────────────────────┼────────────────────────────────┘
                          │
                    ┌─────▼──────┐
                    │  Origin    │
                    │  S3 / Blob │
                    └────────────┘
```

### CDN Content Strategy

| Content Type           | Cache Duration | Origin           | Versioning Strategy       |
|------------------------|----------------|------------------|---------------------------|
| Course images/icons    | 30 days        | S3               | Filename hash             |
| Audio files (TTS)      | 30 days        | S3               | Content hash in URL       |
| User avatars           | 7 days         | S3               | Version suffix `_v2`      |
| Skill tree icons       | 30 days        | S3               | Filename hash             |
| Achievement badges     | 30 days        | S3               | Filename hash             |
| Exercise media         | 30 days        | S3               | Content hash              |
| API responses          | Not cached     | API servers      | N/A                       |
| Web app assets (JS/CSS)| 1 year         | S3               | Build hash in filename    |

### CDN Cache Invalidation

| Trigger                    | Strategy                           |
|----------------------------|------------------------------------|
| User avatar update         | Upload with new versioned URL      |
| Course content update      | New content hash, gradual rollout  |
| App deployment             | New build hash in filenames        |
| Emergency                  | Wildcard invalidation via API      |

---

## 3.8 Deployment Architecture

### Environment Strategy

| Environment | Purpose                      | Data            | Auto-Deploy        |
|-------------|------------------------------|-----------------|--------------------|
| Development | Local developer machines     | Seed data       | N/A                |
| CI/CD       | Automated testing            | Test fixtures   | On every commit    |
| Staging     | Pre-production validation    | Anonymized prod | On merge to main   |
| Production  | Live user traffic            | Real data       | Manual approval    |

### CI/CD Pipeline

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Code    │──►│  Build   │──►│  Test    │──►│  Stage   │──►│  Deploy  │
│  Push    │   │  & Lint  │   │  Suite   │   │  Deploy  │   │  Prod    │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
                    │              │              │              │
                    ▼              ▼              ▼              ▼
              Docker build   Unit tests     Staging env    Blue-green
              Code analysis  Integration    Smoke tests    deployment
              Dependency     Contract       Load tests     Canary 5%
              scanning       tests                         then 100%
```

### Deployment Steps

```yaml
# GitHub Actions Workflow (simplified)
name: Deploy
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker images
        run: docker compose build
      - name: Run unit tests
        run: dotnet test --filter "Category=Unit"
      - name: Run integration tests
        run: dotnet test --filter "Category=Integration"
      - name: Push to container registry
        run: docker push $REGISTRY/$IMAGE:$SHA

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: kubectl apply -f k8s/staging/
      - name: Run smoke tests
        run: dotnet test --filter "Category=Smoke"

  deploy-production:
    needs: deploy-staging
    environment: production
    runs-on: ubuntu-latest
    steps:
      - name: Blue-green deployment
        run: |
          kubectl apply -f k8s/production/
          kubectl rollout status deployment/api-gateway
          kubectl rollout status deployment/learning-service
```

### Kubernetes Deployment Configuration

```yaml
# Example: Learning Service Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: learning-service
  namespace: lingolearn
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: learning-service
        image: lingolearn/learning-service:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: ASPNETCORE_ENVIRONMENT
          value: "Production"
        - name: ConnectionStrings__MySQL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: connection-string
```

---

## 3.9 Disaster Recovery

### Recovery Objectives

| Metric | Target     | Description                              |
|--------|------------|------------------------------------------|
| RTO    | 15 minutes | Maximum acceptable downtime              |
| RPO    | 5 minutes  | Maximum acceptable data loss             |

### Backup Strategy

| Component    | Backup Frequency | Retention | Strategy                          |
|--------------|------------------|-----------|-----------------------------------|
| MySQL        | Every 5 min      | 30 days   | Continuous binary log replication  |
| MySQL        | Daily            | 90 days   | Full snapshot backups              |
| Redis        | Every 5 min      | 7 days    | RDB snapshots + AOF persistence   |
| S3 Media     | Continuous       | Unlimited | Cross-region replication           |
| RabbitMQ     | Hourly           | 7 days    | Definition export + message backup |
| Configuration| On every change  | Unlimited | Git-versioned ConfigMaps           |

### Failover Procedure

```
Normal Operation:
  Primary Region (us-east-1) ──► Users

Failover Triggered:
  1. Health check failures detected (3 consecutive)
  2. DNS failover to secondary region
  3. Secondary region promoted to primary
  4. RabbitMQ cluster rejoins
  5. Redis sentinel promotes replica to master

Post-Failover:
  Secondary Region (us-west-2) ──► Users
  Primary Region ──► Recovery & data sync
```

### Incident Response

| Severity | Response Time | Team           | Example                          |
|----------|---------------|----------------|----------------------------------|
| P0       | 5 minutes     | All on-call    | Complete outage, data loss       |
| P1       | 15 minutes    | Primary on-call| Service degradation > 10% users  |
| P2       | 1 hour        | Engineering    | Non-critical feature failure     |
| P3       | Next business  | Engineering    | Minor bug, cosmetic issue        |

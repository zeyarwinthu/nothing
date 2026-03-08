# 1. Admin Panel Functional Specification

> Defines every feature, workflow, and business rule for the Admin Panel of a Duolingo-style learning platform.

---

## 1.1 Overview & Purpose

The Admin Panel is a web-based internal tool used by staff to manage the Duolingo-style learning platform. It serves as the single control plane for:

- Managing learners, instructors, and admin accounts
- Creating and curating language courses, lessons, and exercises
- Moderating user-generated content and reported items
- Viewing platform-wide analytics and engagement metrics
- Managing localization and translation workflows
- Running A/B experiments and toggling feature flags

**Primary users**: Content managers, platform administrators, data analysts, QA engineers, and engineering leads.

**Access**: Internal only — accessible via VPN or allowlisted IP ranges. Requires multi-factor authentication (MFA).

---

## 1.2 User Roles & Permissions

### 1.2.1 Role Definitions

| Role | Description | Scope |
|---|---|---|
| **Super Admin** | Full system access. Can manage all users, content, settings, and configurations. | Global |
| **Content Manager** | Creates and edits courses, lessons, exercises. Can publish and unpublish content. | Content-scoped |
| **Moderator** | Reviews flagged content, manages user reports, and applies sanctions. | Moderation-scoped |
| **Analyst** | Read-only access to analytics dashboards and reporting tools. | Analytics-scoped |
| **Localization Manager** | Manages translation workflows, language packs, and locale settings. | Localization-scoped |
| **QA / Tester** | Access to A/B testing controls and feature flags. Can preview but not publish. | Testing-scoped |

### 1.2.2 Permission Matrix

| Action | Super Admin | Content Mgr | Moderator | Analyst | Localization Mgr | QA / Tester |
|---|---|---|---|---|---|---|
| View dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manage admin users | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage learner users | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Create/edit courses | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Publish courses | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete courses | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Create/edit lessons | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Moderate content | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| View analytics | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Export analytics | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage translations | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| A/B test controls | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Feature flag management | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| View audit logs | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| System settings | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

### 1.2.3 Role Assignment Rules

- Roles are assigned by Super Admins only.
- A user can hold multiple roles (e.g., Content Manager + Localization Manager).
- Role changes are logged in the audit trail.
- Newly created admin accounts default to **no role** — a Super Admin must explicitly assign one.
- Role assignment requires the assigning admin to re-authenticate (step-up authentication).

---

## 1.3 Admin Dashboard Features

### 1.3.1 Dashboard Overview

The dashboard is the landing page after login. It provides a high-level snapshot of platform health and activity.

**Key Metrics (Cards)**:

| Metric | Description | Refresh Rate |
|---|---|---|
| Total Active Users (DAU/MAU) | Daily and monthly active user counts | Real-time (30s polling) |
| New Signups Today | Users who registered today | Real-time |
| Lessons Completed Today | Total lessons finished across all users | Every 5 minutes |
| Average Session Duration | Mean session length for the day | Hourly |
| Active Courses | Number of published courses | On page load |
| Pending Moderation Queue | Items awaiting review | Real-time |
| Active A/B Tests | Currently running experiments | On page load |
| System Health | API latency, error rate, uptime | Real-time (15s polling) |

**Quick Actions**:

- "Create New Course" button
- "Review Flagged Content" link (with badge count)
- "View Reports" link
- "Manage Users" link

### 1.3.2 Activity Feed

A chronological feed of recent admin actions:

```
[2026-03-08 09:30] Sarah K. published "Spanish Basics — Level 3"
[2026-03-08 09:15] John D. banned user @spammer_42 (reason: spam)
[2026-03-08 09:00] System: A/B test "new-hearts-ui" reached 95% confidence
[2026-03-08 08:45] Maria L. approved 12 translations for French locale
```

- Shows the 50 most recent actions by default.
- Supports filtering by action type, actor, and date range.
- Each entry links to the relevant resource.

### 1.3.3 Notification Center

- Bell icon in the top-right navigation bar.
- Displays unread notification count as a badge.
- Categories: Content alerts, moderation alerts, system alerts, experiment results.
- Supports mark-as-read, mark-all-as-read, and notification preferences.

---

## 1.4 Navigation Structure

### 1.4.1 Primary Sidebar Navigation

```
📊 Dashboard
👥 User Management
   ├── Learners
   ├── Admin Users
   └── Roles & Permissions
📚 Course Management
   ├── All Courses
   ├── Course Builder
   └── Skill Trees
✏️ Lesson Editor
   ├── Lessons
   ├── Exercises
   └── Media Library
🛡️ Content Moderation
   ├── Flagged Content
   ├── User Reports
   └── Sanctions
📈 Analytics & Reporting
   ├── Overview
   ├── User Engagement
   ├── Course Performance
   └── Custom Reports
🌍 Localization
   ├── Languages
   ├── Translation Queue
   └── Locale Settings
🧪 Experiments
   ├── A/B Tests
   └── Feature Flags
⚙️ Settings
   ├── System Configuration
   ├── Audit Logs
   └── API Keys
```

### 1.4.2 Navigation Behavior

- Sidebar is collapsible (icon-only mode) for larger workspace.
- Active section is highlighted with an accent color and left border indicator.
- Sub-items expand/collapse on parent click.
- Breadcrumbs displayed above the main content area for deep navigation.
- Navigation items are conditionally rendered based on user role permissions.
- Mobile-responsive: sidebar becomes a hamburger-triggered drawer on narrow viewports (< 1024px).

### 1.4.3 Top Bar

```
[☰ Toggle Sidebar] [🔍 Global Search] [Breadcrumb Trail...] [🔔 Notifications (3)] [👤 Profile ▼]
```

- **Global Search**: Searches across users, courses, lessons, and settings. Keyboard shortcut: `Ctrl+K` / `Cmd+K`.
- **Profile Dropdown**: Account settings, theme toggle (light/dark), log out.

---

## 1.5 User Management

### 1.5.1 Learner Management

**List View**:

- Paginated table with columns: Avatar, Username, Email, Join Date, Last Active, Streak, XP, Status.
- Supports server-side search by username or email.
- Filters: Status (active, suspended, banned), registration date range, country, subscription type.
- Sortable by any column.
- Bulk actions: Suspend, unsuspend, export to CSV.

**Detail View** (clicking a learner row):

- **Profile tab**: Username, email, display name, avatar, join date, country, timezone, subscription.
- **Activity tab**: Login history (last 30 entries), lessons completed, streak history chart.
- **Progress tab**: Per-course progress bars, skill tree completion, XP breakdown.
- **Moderation tab**: Past reports (by/against this user), active sanctions, notes.
- **Actions**: Suspend, ban, reset password, send notification, delete account (requires confirmation + reason).

### 1.5.2 Admin User Management

- Table: Name, Email, Roles, Last Login, Status.
- Create new admin: Email, display name, role selection (multi-select), temporary password (auto-generated).
- Edit admin: Change roles, deactivate account.
- Deactivated admins cannot log in but their actions remain in audit logs.
- Self-service: Admins can change their own display name and password but not their roles.

### 1.5.3 Roles & Permissions Management

- View all roles in a table with role name, description, and user count.
- Click a role to view/edit its permission set.
- Super Admins can create custom roles by selecting from the permission matrix.
- Changing a role's permissions immediately affects all users with that role.
- A confirmation dialog is shown when a role change would affect > 10 users.

---

## 1.6 Course Management

### 1.6.1 Course Listing

- Card or table view (toggle).
- Each card shows: Course thumbnail, title, source language → target language, lesson count, enrolled users, status badge (Draft / Published / Archived), last modified date.
- Filters: Status, language pair, created by, date range.
- Sort: By title, creation date, enrolled users, last modified.

### 1.6.2 Course Builder

**Course Metadata**:

| Field | Type | Required | Validation |
|---|---|---|---|
| Title | Text | Yes | 3–100 characters |
| Description | Rich text | Yes | 10–2000 characters |
| Source Language | Dropdown | Yes | From language registry |
| Target Language | Dropdown | Yes | From language registry; must differ from source |
| Difficulty Level | Dropdown | Yes | Beginner / Intermediate / Advanced |
| Thumbnail | Image upload | No | JPG/PNG, max 2MB, 400×400px recommended |
| Tags | Tag input | No | Max 10 tags, each 2–30 characters |
| Estimated Duration | Number | No | In hours (0.5–500) |
| Prerequisites | Multi-select | No | Other published courses |

**Skill Tree Editor**:

- Visual drag-and-drop tree editor for organizing skills/units.
- Each node represents a skill containing 1–20 lessons.
- Connections between nodes define learning paths.
- Nodes can be reordered via drag-and-drop.
- Each skill node displays: Title, lesson count, completion status indicator.
- Supports branching paths (multiple skills can unlock after a single prerequisite).

**Course Publishing Workflow**:

```
Draft → Review Requested → Under Review → Published
                                       → Rejected (with feedback)
Archived (from Published — reversible)
```

- Only Content Managers and Super Admins can transition states.
- Publishing requires: At least 1 skill with at least 1 lesson, all required metadata filled, thumbnail uploaded.
- A preview mode allows reviewing the course as a learner would see it.

### 1.6.3 Course Versioning

- Every save creates a new version.
- Version history is displayed as a timeline.
- Admins can compare two versions side-by-side (diff view).
- Rolling back to a previous version creates a new version based on the old one.

---

## 1.7 Lesson Editor

### 1.7.1 Lesson Structure

Each lesson belongs to a skill within a course and contains 5–20 exercises.

**Lesson Metadata**:

| Field | Type | Required |
|---|---|---|
| Title | Text (3–100 chars) | Yes |
| Skill (Parent) | Dropdown | Yes |
| Order in Skill | Number (auto-assigned) | Yes |
| XP Reward | Number (5–50) | Yes |
| Time Limit | Seconds (0 = no limit) | No |
| Tips & Notes | Rich text | No |

### 1.7.2 Exercise Types

The editor supports the following exercise types:

| Type | Description | Input Fields |
|---|---|---|
| **Translation** | Translate a sentence from source to target language | Prompt, correct answer(s), accepted alternatives |
| **Multiple Choice** | Select the correct translation from options | Prompt, options (2–6), correct option index |
| **Fill in the Blank** | Complete a sentence with the missing word | Sentence with `___` placeholder, correct word(s) |
| **Word Bank** | Arrange word tiles to form a correct sentence | Prompt, correct sentence, distractor words |
| **Listening** | Listen to audio and type what you hear | Audio file, correct transcript |
| **Speaking** | Read a sentence aloud (speech recognition) | Target sentence, phonetic hints |
| **Matching** | Match pairs (word → translation) | Pairs (3–6), column labels |
| **Image Select** | Select the image that matches the word | Word, images (2–4), correct image index |

### 1.7.3 Exercise Editor Interface

- Tabbed interface: one tab per exercise in the lesson.
- Tabs are draggable for reordering.
- Each tab shows exercise type icon and a short label.
- "Add Exercise" button opens a type selector modal.
- Exercise form is dynamic based on the selected type.
- **Preview pane** on the right shows a live simulation of how the exercise appears to learners.
- **Validation**: The editor validates all required fields before allowing save. Unsaved changes trigger a browser-level "unsaved changes" warning on navigation.

### 1.7.4 Media Library

- Centralized repository for audio files, images, and videos used in exercises.
- Upload: Drag-and-drop or file picker. Supports MP3, WAV, OGG (audio); JPG, PNG, SVG, WebP (images); MP4, WebM (video).
- File size limits: Audio 5MB, Image 2MB, Video 50MB.
- Search by filename, tag, language, or upload date.
- Usage tracking: Shows which exercises reference a given media file.
- Bulk upload with progress indicator.

---

## 1.8 Content Moderation Tools

### 1.8.1 Flagged Content Queue

- Table: Item type (comment, translation, forum post), content preview, reporter, flag reason, date flagged, severity (auto-classified: low / medium / high / critical).
- Filters: Severity, item type, date range, status (pending, reviewed, escalated).
- Sort: By date (newest first default), severity.
- Clicking a row opens a detail panel with full content, reporter info, and action buttons.

**Actions on flagged content**:

| Action | Description | Requires |
|---|---|---|
| Approve | Mark as safe, dismiss the flag | Single click |
| Remove | Remove the content from the platform | Reason (dropdown + optional text) |
| Edit | Modify the content directly | Inline editor |
| Escalate | Forward to a senior moderator or Super Admin | Priority selection |
| Ban Author | Ban the content author | Reason, duration (temporary/permanent) |

### 1.8.2 User Reports

- Separate view for user-to-user reports (harassment, inappropriate profile, etc.).
- Shows: Reporter, reported user, reason, evidence (screenshots, links), date.
- Actions: Dismiss, warn user, suspend user, ban user.
- Moderators can add internal notes visible only to other moderators.

### 1.8.3 Automated Moderation Rules

- Rule builder interface for creating auto-moderation triggers.
- Conditions: Keyword match, regex pattern, user reputation score, content length.
- Actions: Auto-flag, auto-remove, auto-mute author.
- Rules are evaluated in priority order; first match wins.
- Dry-run mode: Test rules against historical data before activating.

### 1.8.4 Sanctions Management

- View all active sanctions (suspensions, bans, mutes) in a table.
- Columns: User, sanction type, reason, applied by, start date, end date, status.
- Actions: Lift sanction early (with reason), extend duration.
- Expired sanctions automatically archive but remain in history.

---

## 1.9 Analytics & Reporting

### 1.9.1 Overview Dashboard

**Key charts and metrics**:

| Visualization | Type | Data |
|---|---|---|
| User Growth | Line chart | Daily/weekly/monthly new registrations |
| DAU/MAU Ratio | Gauge | Stickiness metric |
| Revenue | Bar chart | Daily revenue by subscription tier |
| Retention Funnel | Funnel chart | D1 / D7 / D30 retention rates |
| Geographic Distribution | Choropleth map | Users by country |
| Top Courses | Horizontal bar | Courses ranked by enrolled users |
| Completion Rate | Donut chart | Lessons completed vs. abandoned |

- All charts support date range selection (preset: Today, 7 days, 30 days, 90 days, Custom).
- Data export: CSV, PNG (chart image), PDF (full report).

### 1.9.2 User Engagement Analytics

- **Session metrics**: Average session duration, sessions per user per day, bounce rate.
- **Streak analytics**: Distribution of streak lengths, streak freeze usage.
- **XP distribution**: Histogram of daily XP earned across the user base.
- **Cohort analysis**: Retention by signup cohort (weekly/monthly), filterable by acquisition channel.

### 1.9.3 Course Performance Analytics

- Per-course: Enrollment count, completion rate, average score, drop-off points.
- Per-lesson: Time-to-complete distribution, error rate by exercise, most skipped exercises.
- **Difficulty heatmap**: Visual grid showing which exercises have the highest error rates.
- Drill-down: Click any course → skill → lesson → exercise for granular data.

### 1.9.4 Custom Report Builder

- Drag-and-drop report builder.
- Dimensions: Date, country, language pair, course, subscription tier, device platform.
- Metrics: Users, sessions, lessons completed, XP earned, revenue.
- Filters: Any dimension can be used as a filter.
- Visualizations: Table, line chart, bar chart, pie chart.
- Reports can be saved, shared with other admins, and scheduled for email delivery (daily/weekly/monthly).

---

## 1.10 Localization Tools

### 1.10.1 Language Registry

- Master list of all supported languages with: Language code (ISO 639-1), name, native name, script direction (LTR/RTL), status (active/inactive).
- Add new language: Requires code, name, and at least one translation contributor assigned.
- Deactivating a language hides it from learners but preserves all data.

### 1.10.2 Translation Queue

- Table of pending translations: Source text, source language, target language, context (where it appears), priority, assignee, due date.
- Filters: Target language, priority, assignee, status (pending, in-progress, review, approved).
- Inline translation editor with:
  - Source text displayed alongside the target field.
  - Character count and limit indicator.
  - Glossary sidebar showing previously approved translations for key terms.
  - Machine translation suggestion (pre-populated, editable).
- Translation review workflow: Translator submits → Reviewer approves/rejects → Published.

### 1.10.3 Glossary Management

- Per-language glossary of key terms.
- Columns: Source term, approved translation, context, notes, last updated.
- Import/export as CSV.
- Changes propagate as suggestions to all existing translations containing the term.

### 1.10.4 Locale Settings

- Date/time format, number format, currency symbol per locale.
- UI string overrides: Admin can modify any platform UI string for a given locale.
- Preview: View the learner app in any locale via an embedded preview frame.

---

## 1.11 A/B Testing Controls

### 1.11.1 Experiment Listing

- Table: Experiment name, status (draft, running, paused, completed), target metric, start date, end date, confidence level.
- Status badges are color-coded: Draft (gray), Running (green), Paused (yellow), Completed (blue).

### 1.11.2 Experiment Builder

**Experiment Metadata**:

| Field | Type | Required |
|---|---|---|
| Name | Text (3–100 chars) | Yes |
| Hypothesis | Text (10–500 chars) | Yes |
| Target Metric | Dropdown (e.g., D7 retention, lesson completion rate) | Yes |
| Audience | Segment selector (all users, new users, specific countries) | Yes |
| Traffic Allocation | Percentage slider (1–50% per variant) | Yes |
| Duration | Date range picker | Yes |
| Variants | List of variant definitions | Yes (min 2) |

**Variant Definition**:

- Name (e.g., "Control", "Variant A").
- Feature flag overrides (key-value pairs).
- Description of what changes for this variant.

### 1.11.3 Experiment Monitoring

- Real-time results dashboard per experiment:
  - Metric value per variant over time (line chart).
  - Statistical significance indicator (p-value, confidence interval).
  - Sample size per variant.
  - Estimated time to reach statistical significance.
- Auto-stop rule: If a variant underperforms by more than X% with > 95% confidence, the experiment pauses and alerts the creator.

### 1.11.4 Experiment Conclusion

- "Complete Experiment" action requires selecting a winner or declaring inconclusive.
- Winning variant can be immediately promoted to 100% rollout.
- Post-experiment report is auto-generated with charts, summary stats, and recommendation.

---

## 1.12 Feature Flag Management

### 1.12.1 Feature Flag Listing

- Table: Flag key, description, status (enabled/disabled), rollout percentage, targeting rules, last modified, modified by.
- Search by flag key or description.
- Bulk enable/disable.

### 1.12.2 Feature Flag Editor

**Flag Definition**:

| Field | Type | Required |
|---|---|---|
| Key | Slug (e.g., `new-hearts-system`) | Yes (unique, immutable after creation) |
| Description | Text (10–500 chars) | Yes |
| Type | Boolean / String / Number / JSON | Yes |
| Default Value | Matches type | Yes |
| Enabled | Toggle | Yes |

**Targeting Rules** (evaluated in order):

| Rule Type | Example |
|---|---|
| User segment | `subscription = "premium"` |
| User ID list | Specific user IDs for internal testing |
| Country | `country IN ("US", "GB", "CA")` |
| Percentage rollout | Enable for 25% of eligible users |
| Date range | Active between two dates |

### 1.12.3 Flag Lifecycle

```
Created (disabled) → Enabled (targeted rollout) → Full Rollout (100%) → Archived
```

- Archived flags are hidden by default but can be restored.
- Stale flag detection: Flags unchanged for > 90 days are highlighted for review.
- Dependency tracking: Shows which A/B tests reference a given flag.

### 1.12.4 Emergency Kill Switch

- "Disable All Non-Essential Flags" emergency action available to Super Admins.
- Disables all flags not marked as "critical infrastructure."
- Requires confirmation dialog with reason.
- Triggers an immediate notification to all admin users.
- Logged in the audit trail as a critical action.

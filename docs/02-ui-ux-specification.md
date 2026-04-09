# 2. Frontend UI/UX Specification

> Defines the visual layout, interaction patterns, and accessibility standards for every page and component in the Admin Panel.

---

## 2.1 Design Principles

| Principle | Description |
|---|---|
| **Clarity** | Every element serves a clear purpose. No decorative clutter. Labels are explicit, not clever. |
| **Consistency** | Identical patterns for identical actions across all pages. The same icon always means the same thing. |
| **Efficiency** | Minimize clicks for common tasks. Provide keyboard shortcuts for power users. Batch operations where appropriate. |
| **Feedback** | Every action produces visible feedback — loading spinners, success toasts, error messages. No silent failures. |
| **Safety** | Destructive actions require confirmation. Undo is available where possible. Admin actions are auditable. |
| **Accessibility** | WCAG 2.1 AA compliance. All interactive elements are keyboard-navigable and screen-reader compatible. |

---

## 2.2 Page-by-Page Layout Descriptions

### 2.2.1 Login Page

```
┌──────────────────────────────────────────────────┐
│                                                  │
│              [Platform Logo]                     │
│           Admin Panel Login                      │
│                                                  │
│   ┌──────────────────────────────────┐           │
│   │ Email                            │           │
│   └──────────────────────────────────┘           │
│   ┌──────────────────────────────────┐           │
│   │ Password                  [👁]   │           │
│   └──────────────────────────────────┘           │
│                                                  │
│   [        Sign In        ]                      │
│                                                  │
│   Forgot password?                               │
│                                                  │
│   ─── OR ───                                     │
│                                                  │
│   [   Sign in with SSO    ]                      │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Layout Details**:
- Centered card on a gradient or branded background.
- Card width: 420px max, responsive down to 320px.
- Logo: Platform logo, 48px height.
- Form fields stack vertically with 16px gap.
- "Forgot password?" is a text link below the Sign In button.
- SSO button is visually secondary (outlined style).

### 2.2.2 MFA Verification Page

```
┌──────────────────────────────────────────────────┐
│                                                  │
│              [Platform Logo]                     │
│         Two-Factor Authentication                │
│                                                  │
│   Enter the 6-digit code from your               │
│   authenticator app.                             │
│                                                  │
│   ┌──┐ ┌──┐ ┌──┐  ┌──┐ ┌──┐ ┌──┐               │
│   │  │ │  │ │  │  │  │ │  │ │  │               │
│   └──┘ └──┘ └──┘  └──┘ └──┘ └──┘               │
│                                                  │
│   [        Verify        ]                       │
│                                                  │
│   Didn't receive a code? Use backup code         │
│                                                  │
└──────────────────────────────────────────────────┘
```

- Six individual digit inputs, auto-advancing focus.
- Auto-submit on 6th digit entry.
- "Use backup code" link switches to a single text input for backup codes.

### 2.2.3 Dashboard Page

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ [☰] [🔍 Search...        ] [Breadcrumb] [🔔 3] [👤▼] │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  📊 Dash│  │  DAU    │ │ Signups │ │ Lessons │ │ Queue  │ │
│  👥 Users│  │ 45,231  │ │  1,204  │ │ 28,402  │ │   42   │ │
│  📚 Cours│  │ +3.2% ↑ │ │ -1.1% ↓│ │ +5.8% ↑ │ │ ⚠ High │ │
│  ✏️ Lesson│  └─────────┘ └─────────┘ └─────────┘ └────────┘ │
│  🛡️ Moder│                                                  │
│  📈 Analy│  ┌────────────────────────────────────────────┐  │
│  🌍 Local│  │          User Growth (Line Chart)          │  │
│  🧪 Exper│  │                                            │  │
│  ⚙️ Setti│  │     /\      /\                             │  │
│         │  │    /  \    /  \    /\                      │  │
│         │  │   /    \  /    \  /  \                     │  │
│         │  │  /      \/      \/    \                    │  │
│         │  │ /                      \                   │  │
│         │  └────────────────────────────────────────────┘  │
│         │                                                  │
│         │  ┌──────────────────────┐ ┌────────────────────┐ │
│         │  │  Quick Actions       │ │  Activity Feed     │ │
│         │  │  • Create Course     │ │  [09:30] Sarah...  │ │
│         │  │  • Review Flags (42) │ │  [09:15] John...   │ │
│         │  │  • View Reports      │ │  [09:00] System... │ │
│         │  │  • Manage Users      │ │  [08:45] Maria...  │ │
│         │  └──────────────────────┘ └────────────────────┘ │
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

**Layout Details**:
- **Sidebar**: 260px wide (expanded), 64px (collapsed). Fixed position.
- **Top bar**: 64px height. Sticky.
- **Metric cards**: 4-column grid on desktop, 2-column on tablet, 1-column on mobile. Each card is 200px min-width.
- **Charts section**: Full-width, 400px height. Date range selector in the top-right corner of the chart.
- **Bottom row**: 2-column layout. Quick Actions on the left (40%), Activity Feed on the right (60%).

### 2.2.4 User Management — Learner List

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ 👥 User Management > Learners                     │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  [🔍 Search users...   ] [⏷ Filters] [⬇ Export]  │
│         │                                                  │
│         │  ┌────┬──────────┬──────────┬────────┬────────┐  │
│         │  │ ☐  │ Username │ Email    │ Status │ Last…  │  │
│         │  ├────┼──────────┼──────────┼────────┼────────┤  │
│         │  │ ☐  │ @maria   │ m@e.com  │ Active │ 2h ago │  │
│         │  │ ☐  │ @john_d  │ j@e.com  │ Susp.  │ 1d ago │  │
│         │  │ ☐  │ @learner3│ l@e.com  │ Active │ 5m ago │  │
│         │  │ ☐  │ ...      │ ...      │ ...    │ ...    │  │
│         │  └────┴──────────┴──────────┴────────┴────────┘  │
│         │                                                  │
│         │  Showing 1-25 of 142,039  [< 1 2 3 ... 5682 >]  │
│         │                                                  │
│         │  ── Bulk Actions: [Suspend] [Export] ──          │
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

**Layout Details**:
- **Search bar**: Full-width text input with debounced (300ms) server-side search.
- **Filters**: Expandable filter panel with: Status (multi-select), Registration date (range picker), Country (searchable dropdown), Subscription (multi-select).
- **Table**: Sticky header. Row click navigates to learner detail. Checkbox column for bulk selection.
- **Pagination**: Server-side. Shows current range and total. Page size selector: 25 / 50 / 100.
- **Bulk actions toolbar**: Appears when one or more rows are checked.

### 2.2.5 User Management — Learner Detail

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ 👥 Users > Learners > @maria                      │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  ┌──────────────────────────────────────────────┐│
│         │  │ [Avatar]  Maria López                        ││
│         │  │           @maria · maria@email.com           ││
│         │  │           Joined: 2024-01-15 · Mexico 🇲🇽    ││
│         │  │           Status: ● Active    Streak: 142 🔥 ││
│         │  │                                              ││
│         │  │  [Suspend] [Reset Password] [Send Message]   ││
│         │  └──────────────────────────────────────────────┘│
│         │                                                  │
│         │  [Profile] [Activity] [Progress] [Moderation]    │
│         │  ┌──────────────────────────────────────────────┐│
│         │  │                                              ││
│         │  │  (Tab content rendered here)                 ││
│         │  │                                              ││
│         │  └──────────────────────────────────────────────┘│
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

**Layout Details**:
- **Header card**: Sticky. Shows avatar (64px), name, handle, email, join date, country, status indicator, streak.
- **Action buttons**: Aligned right in the header. Destructive actions (Suspend, Ban) use red/warning colors.
- **Tabs**: Horizontal tab bar below the header. Active tab has a bottom border indicator.
- **Tab content area**: Scrollable independently from the header.

### 2.2.6 Course Management — Course List

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ 📚 Course Management > All Courses                │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  [🔍 Search...] [⏷ Filters] [📊/📋 View] [+ New] │
│         │                                                  │
│         │  ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│         │  │ [Thumbnail] │ │ [Thumbnail] │ │ [Thumb.]   │ │
│         │  │ Spanish     │ │ French      │ │ Japanese   │ │
│         │  │ Basics      │ │ Advanced    │ │ Intro      │ │
│         │  │ EN → ES     │ │ EN → FR     │ │ EN → JA    │ │
│         │  │ 24 lessons  │ │ 18 lessons  │ │ 32 lessons │ │
│         │  │ 12.4K users │ │ 8.2K users  │ │ 5.1K users │ │
│         │  │ ● Published │ │ ● Draft     │ │ ● Published│ │
│         │  └─────────────┘ └─────────────┘ └────────────┘ │
│         │                                                  │
│         │  ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│         │  │ ...         │ │ ...         │ │ ...        │ │
│         │  └─────────────┘ └─────────────┘ └────────────┘ │
│         │                                                  │
│         │  Showing 1-9 of 47  [< 1 2 3 4 5 6 >]           │
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

**Layout Details**:
- **View toggle**: Switch between card grid (default) and table view.
- **Card grid**: 3 columns on desktop (> 1280px), 2 on tablet, 1 on mobile.
- **Card**: 280px min-width. Thumbnail (16:9 aspect ratio), title, language pair, lesson count, enrolled users, status badge.
- **"+ New Course"**: Primary action button, top-right.

### 2.2.7 Course Builder — Edit Course

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ 📚 Courses > Spanish Basics > Edit                │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  [Metadata] [Skill Tree] [Settings] [Preview]    │
│         │  ┌──────────────────────────────────────────────┐│
│         │  │                                              ││
│         │  │  Title: [Spanish Basics                   ]  ││
│         │  │                                              ││
│         │  │  Description:                                ││
│         │  │  ┌──────────────────────────────────────────┐││
│         │  │  │ Rich text editor with formatting toolbar │││
│         │  │  │                                          │││
│         │  │  └──────────────────────────────────────────┘││
│         │  │                                              ││
│         │  │  Source Lang: [English ▼]  Target: [Spanish ▼]││
│         │  │  Difficulty:  [Beginner ▼]                   ││
│         │  │                                              ││
│         │  │  Thumbnail: [📎 Upload] [preview.jpg ✕]      ││
│         │  │                                              ││
│         │  │  Tags: [travel] [basics] [beginner] [+ Add]  ││
│         │  │                                              ││
│         │  └──────────────────────────────────────────────┘│
│         │                                                  │
│         │  [Cancel]                [Save Draft] [Publish ▼]│
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

### 2.2.8 Lesson Editor

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ ✏️ Spanish Basics > Skill 1 > Lesson 3 > Edit     │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  Exercises: [Ex.1|Translation] [Ex.2|MC] [+Add]  │
│         │  ┌─────────────────────┬───────────────────────┐ │
│         │  │  EDITOR             │  PREVIEW              │ │
│         │  │                     │                       │ │
│         │  │  Type: Translation  │  ┌─────────────────┐  │ │
│         │  │                     │  │  Translate this  │  │ │
│         │  │  Prompt:            │  │  sentence:       │  │ │
│         │  │  [Hello, how are    │  │                  │  │ │
│         │  │   you?           ]  │  │  "Hello, how     │  │ │
│         │  │                     │  │   are you?"      │  │ │
│         │  │  Correct Answer:    │  │                  │  │ │
│         │  │  [Hola, ¿cómo       │  │  [___________]   │  │ │
│         │  │   estás?         ]  │  │                  │  │ │
│         │  │                     │  │  [Check]         │  │ │
│         │  │  Alternatives:      │  └─────────────────┘  │ │
│         │  │  [Hola, ¿cómo estás]│                       │ │
│         │  │  [+ Add alternative]│                       │ │
│         │  │                     │                       │ │
│         │  └─────────────────────┴───────────────────────┘ │
│         │                                                  │
│         │  [Cancel]          [Save] [Save & Next Exercise] │
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

**Layout Details**:
- **Exercise tabs**: Horizontal, scrollable. Drag to reorder. Each tab: icon + short label.
- **Split pane**: 50/50 editor/preview. Resizable divider.
- **Editor form**: Dynamic fields based on exercise type.
- **Preview**: Live-updating simulation of the learner experience.
- **Footer**: Sticky action bar with Cancel, Save, and Save & Next.

### 2.2.9 Content Moderation — Flagged Content

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ 🛡️ Content Moderation > Flagged Content            │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  [⏷ Severity: All ▼] [⏷ Type: All ▼] [42 items] │
│         │                                                  │
│         │  ┌────┬──────────┬────────┬────────┬──────────┐  │
│         │  │ ⚠️ │ Content  │ Type   │ Reporter│ Date     │  │
│         │  ├────┼──────────┼────────┼────────┼──────────┤  │
│         │  │ 🔴 │ "F*** yo│ Comment│ @user12│ 2h ago   │  │
│         │  │ 🟡 │ "Buy che│ Forum  │ @mod_a │ 5h ago   │  │
│         │  │ 🟢 │ "Is this│ Transl.│ System │ 1d ago   │  │
│         │  └────┴──────────┴────────┴────────┴──────────┘  │
│         │                                                  │
│         │  ── Detail Panel (slide-in from right) ──        │
│         │  ┌──────────────────────────────────────────────┐│
│         │  │ Flagged Comment #1842                        ││
│         │  │ Author: @troll_user · Flagged by: @user12    ││
│         │  │ Reason: Offensive language                    ││
│         │  │                                              ││
│         │  │ Content:                                      ││
│         │  │ "F*** you and your stupid app"               ││
│         │  │                                              ││
│         │  │ [✓ Approve] [✕ Remove] [✏ Edit] [⬆ Escalate]││
│         │  │ [🚫 Ban Author]                              ││
│         │  └──────────────────────────────────────────────┘│
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

**Layout Details**:
- **Severity indicators**: Color-coded icons (🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low).
- **Content preview**: Truncated to 50 characters in the table, full text in the detail panel.
- **Detail panel**: Slides in from the right (480px width) when a row is clicked. Overlays the table on narrow screens.
- **Action buttons**: Stacked vertically in the detail panel. Destructive actions have confirmation dialogs.

### 2.2.10 Analytics Dashboard

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ 📈 Analytics > Overview                            │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  Date Range: [Last 30 Days ▼] [Mar 7] to [Mar 8]│
│         │                                                  │
│         │  ┌────────────────────────────────────────────┐  │
│         │  │     User Growth Over Time (Line Chart)     │  │
│         │  │  50K ┤                                     │  │
│         │  │  40K ┤         ╱‾‾╲      ╱‾                │  │
│         │  │  30K ┤     ╱‾‾╱    ╲╱‾‾‾╱                  │  │
│         │  │  20K ┤ ╱‾‾╱                                │  │
│         │  │  10K ┤╱                                    │  │
│         │  │      └──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──    │  │
│         │  │       Feb 7   Feb 14  Feb 21  Feb 28  Mar 7│  │
│         │  └────────────────────────────────────────────┘  │
│         │                                                  │
│         │  ┌──────────────────┐ ┌────────────────────────┐ │
│         │  │ Retention Funnel │ │ Top Courses            │ │
│         │  │ D1: ████ 72%    │ │ Spanish ████████ 12.4K │ │
│         │  │ D7: ███  45%    │ │ French  ██████   8.2K  │ │
│         │  │ D30:██   28%    │ │ Japanese████     5.1K  │ │
│         │  └──────────────────┘ └────────────────────────┘ │
│         │                                                  │
│         │  [📥 Export CSV] [📥 Export PDF] [📥 Export PNG]   │
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

### 2.2.11 A/B Testing — Experiment Detail

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ 🧪 Experiments > "New Hearts UI"                   │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  Status: ● Running   Since: Feb 15, 2026         │
│         │  Metric: D7 Retention  Confidence: 87%           │
│         │                                                  │
│         │  ┌────────────────────────────────────────────┐  │
│         │  │   D7 Retention by Variant (Line Chart)     │  │
│         │  │  50% ┤                                     │  │
│         │  │  45% ┤  Control ──  Variant A ─ ─          │  │
│         │  │  40% ┤     ──────────────                  │  │
│         │  │  35% ┤  ─ ─ ─ ─ ─ ─ ─ ─ ─                │  │
│         │  │  30% ┤                                     │  │
│         │  │      └──┬──┬──┬──┬──┬──┬──                 │  │
│         │  └────────────────────────────────────────────┘  │
│         │                                                  │
│         │  ┌──────────────┬───────────┬──────────────────┐ │
│         │  │ Variant      │ D7 Ret.   │ Sample Size      │ │
│         │  ├──────────────┼───────────┼──────────────────┤ │
│         │  │ Control      │ 42.3%     │ 15,204           │ │
│         │  │ Variant A    │ 38.1%     │ 14,987           │ │
│         │  └──────────────┴───────────┴──────────────────┘ │
│         │                                                  │
│         │  [Pause Experiment] [Complete Experiment]         │
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

### 2.2.12 Feature Flag Management

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ 🧪 Experiments > Feature Flags                     │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  [🔍 Search flags...] [+ New Flag]               │
│         │                                                  │
│         │  ┌───────────────────┬────────┬───────┬────────┐ │
│         │  │ Flag Key          │ Status │ Rollout│ Modified│ │
│         │  ├───────────────────┼────────┼───────┼────────┤ │
│         │  │ new-hearts-system │ ● On   │  25%  │ 2d ago │ │
│         │  │ dark-mode         │ ● On   │ 100%  │ 1w ago │ │
│         │  │ ai-tutor-v2       │ ○ Off  │   0%  │ 3h ago │ │
│         │  │ streak-freeze-v3  │ ● On   │  50%  │ 5d ago │ │
│         │  └───────────────────┴────────┴───────┴────────┘ │
│         │                                                  │
│         │  [🚨 Emergency: Disable All Non-Essential Flags]  │
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

### 2.2.13 Localization — Translation Queue

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ 🌍 Localization > Translation Queue                │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  [Language: French ▼] [Priority: All ▼] [Status ▼]│
│         │                                                  │
│         │  ┌──────────────────────────────────────────────┐│
│         │  │ Source (EN)        │ Translation (FR)        ││
│         │  ├────────────────────┼─────────────────────────┤│
│         │  │ "Keep your streak" │ [Gardez votre série  ]  ││
│         │  │ Context: Push notif│ ✅ Machine suggestion    ││
│         │  ├────────────────────┼─────────────────────────┤│
│         │  │ "Great job!"       │ [Bon travail !       ]  ││
│         │  │ Context: Lesson end│ ✅ Machine suggestion    ││
│         │  └────────────────────┴─────────────────────────┘│
│         │                                                  │
│         │  Glossary Sidebar:                               │
│         │  ┌──────────────────────────────────────────────┐│
│         │  │ streak → série     │ lesson → leçon          ││
│         │  │ XP → XP (no trans.)│ heart → cœur            ││
│         │  └──────────────────────────────────────────────┘│
│         │                                                  │
│         │  [Save All] [Submit for Review]                   │
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

### 2.2.14 Settings — Audit Logs

```
┌─────────┬──────────────────────────────────────────────────┐
│         │ ⚙️ Settings > Audit Logs                           │
│  Side   ├──────────────────────────────────────────────────┤
│  bar    │                                                  │
│         │  [Date Range ▼] [Actor ▼] [Action Type ▼] [🔍]   │
│         │                                                  │
│         │  ┌──────────┬──────────┬──────────┬────────────┐ │
│         │  │ Timestamp│ Actor    │ Action   │ Details    │ │
│         │  ├──────────┼──────────┼──────────┼────────────┤ │
│         │  │ 09:30:12 │ Sarah K. │ Publish  │ Course #42 │ │
│         │  │ 09:15:44 │ John D.  │ Ban User │ @spammer42 │ │
│         │  │ 09:00:01 │ System   │ A/B Stop │ hearts-ui  │ │
│         │  │ 08:45:33 │ Maria L. │ Approve  │ 12 strings │ │
│         │  └──────────┴──────────┴──────────┴────────────┘ │
│         │                                                  │
│         │  Showing 1-50 of 12,847  [< 1 2 ... 257 >]      │
│         │  [📥 Export Logs]                                 │
│         │                                                  │
└─────────┴──────────────────────────────────────────────────┘
```

---

## 2.3 Component Hierarchy

### 2.3.1 Application Shell

```
AppComponent
├── AuthLayoutComponent (login, MFA)
│   ├── LoginPageComponent
│   └── MfaPageComponent
└── AdminLayoutComponent (authenticated)
    ├── SidebarComponent
    │   ├── SidebarNavGroupComponent (× N groups)
    │   │   └── SidebarNavItemComponent (× N items)
    │   └── SidebarCollapseToggleComponent
    ├── TopBarComponent
    │   ├── GlobalSearchComponent
    │   ├── BreadcrumbComponent
    │   ├── NotificationBellComponent
    │   └── UserMenuComponent
    └── RouterOutlet (page content)
```

### 2.3.2 Dashboard Page

```
DashboardPageComponent
├── MetricCardComponent (× 4-8)
├── UserGrowthChartComponent
├── QuickActionsCardComponent
└── ActivityFeedComponent
    └── ActivityFeedItemComponent (× N)
```

### 2.3.3 User Management Pages

```
UserManagementModule
├── LearnerListPageComponent
│   ├── SearchBarComponent
│   ├── FilterPanelComponent
│   ├── DataTableComponent
│   │   ├── TableHeaderComponent
│   │   ├── TableRowComponent (× N)
│   │   └── TablePaginationComponent
│   └── BulkActionsToolbarComponent
├── LearnerDetailPageComponent
│   ├── UserHeaderCardComponent
│   ├── TabGroupComponent
│   │   ├── ProfileTabComponent
│   │   ├── ActivityTabComponent
│   │   ├── ProgressTabComponent
│   │   └── ModerationTabComponent
│   └── ActionButtonGroupComponent
├── AdminListPageComponent
└── RolesPermissionsPageComponent
    ├── RoleListComponent
    └── PermissionMatrixComponent
```

### 2.3.4 Course Management Pages

```
CourseManagementModule
├── CourseListPageComponent
│   ├── ViewToggleComponent
│   ├── CourseCardComponent (× N, card view)
│   ├── DataTableComponent (table view)
│   └── PaginationComponent
├── CourseBuilderPageComponent
│   ├── CourseMetadataFormComponent
│   ├── SkillTreeEditorComponent
│   │   └── SkillNodeComponent (× N)
│   ├── CourseSettingsComponent
│   └── CoursePreviewComponent
└── CourseVersionHistoryComponent
```

### 2.3.5 Lesson Editor Pages

```
LessonEditorModule
├── LessonListPageComponent
├── LessonEditorPageComponent
│   ├── ExerciseTabBarComponent
│   │   └── ExerciseTabComponent (× N)
│   ├── ExerciseEditorComponent
│   │   ├── TranslationExerciseFormComponent
│   │   ├── MultipleChoiceExerciseFormComponent
│   │   ├── FillBlankExerciseFormComponent
│   │   ├── WordBankExerciseFormComponent
│   │   ├── ListeningExerciseFormComponent
│   │   ├── SpeakingExerciseFormComponent
│   │   ├── MatchingExerciseFormComponent
│   │   └── ImageSelectExerciseFormComponent
│   └── ExercisePreviewComponent
└── MediaLibraryPageComponent
    ├── MediaUploadComponent
    ├── MediaGridComponent
    │   └── MediaThumbnailComponent (× N)
    └── MediaDetailPanelComponent
```

### 2.3.6 Analytics Pages

```
AnalyticsModule
├── AnalyticsOverviewPageComponent
│   ├── DateRangeSelectorComponent
│   ├── UserGrowthChartComponent
│   ├── RetentionFunnelComponent
│   ├── TopCoursesChartComponent
│   └── ExportToolbarComponent
├── UserEngagementPageComponent
├── CoursePerformancePageComponent
└── CustomReportBuilderPageComponent
    ├── DimensionSelectorComponent
    ├── MetricSelectorComponent
    ├── FilterBuilderComponent
    ├── ChartTypeSelectorComponent
    └── ReportPreviewComponent
```

---

## 2.4 Wireframe-Style Descriptions

### 2.4.1 Responsive Breakpoints

| Breakpoint | Width | Sidebar | Grid Columns | Table Behavior |
|---|---|---|---|---|
| Desktop XL | ≥ 1440px | Expanded (260px) | 4 | Full columns |
| Desktop | ≥ 1280px | Expanded (260px) | 3 | Full columns |
| Tablet | ≥ 768px | Collapsed (64px) | 2 | Horizontal scroll |
| Mobile | < 768px | Drawer (overlay) | 1 | Card layout fallback |

### 2.4.2 Grid System

- 12-column grid with 24px gutters.
- Content max-width: 1440px, centered.
- Page padding: 32px on desktop, 16px on mobile.

### 2.4.3 Spacing Scale

| Token | Value | Usage |
|---|---|---|
| `space-xs` | 4px | Icon padding, inline spacing |
| `space-sm` | 8px | Compact list spacing |
| `space-md` | 16px | Standard element spacing |
| `space-lg` | 24px | Section spacing |
| `space-xl` | 32px | Page padding, card padding |
| `space-2xl` | 48px | Major section separation |

---

## 2.5 Interaction Rules

### 2.5.1 Navigation Interactions

| Interaction | Behavior |
|---|---|
| Sidebar item click | Navigate to the page. Expand sub-items if present. |
| Sidebar collapse toggle | Animate sidebar width from 260px to 64px. Labels fade out, icons remain. |
| Breadcrumb click | Navigate to the breadcrumb target. Confirm if unsaved changes exist. |
| Back browser button | Standard browser history. Unsaved changes trigger a "Leave page?" dialog. |
| `Ctrl+K` / `Cmd+K` | Open global search overlay. |

### 2.5.2 Table Interactions

| Interaction | Behavior |
|---|---|
| Column header click | Toggle sort: ascending → descending → none. Active sort column shows an arrow indicator. |
| Row click | Navigate to detail page (unless a checkbox or action button was clicked). |
| Checkbox click | Toggle row selection. Shift+click selects a range. |
| Header checkbox click | Select/deselect all rows on the current page. |
| Filter change | Immediately apply filter (server-side). Reset pagination to page 1. |
| Search input | Debounce 300ms. Minimum 2 characters. Reset pagination to page 1. |
| Empty search | Clear search filter. Return to unfiltered results. |

### 2.5.3 Form Interactions

| Interaction | Behavior |
|---|---|
| Field focus | Show floating label animation. Blue border. |
| Field blur (invalid) | Show validation error below the field. Red border. |
| Field input | Clear error state if the new value is valid. |
| Form submit (invalid) | Scroll to first invalid field. Focus it. Show all errors. |
| Form submit (valid) | Disable submit button. Show loading spinner inside button. |
| Success response | Show success toast (top-right, 5s auto-dismiss). Navigate or reset form. |
| Error response | Show error toast or inline error. Re-enable submit button. |

### 2.5.4 Modal Interactions

| Interaction | Behavior |
|---|---|
| Open | Fade-in backdrop (150ms) + slide-up modal (200ms). Focus trapped inside modal. |
| Close (X button) | Animate out. Return focus to the element that triggered the modal. |
| Close (backdrop click) | Same as X button, unless the modal is a confirmation dialog (backdrop click disabled). |
| Close (Escape key) | Same as X button. |
| Confirm action | Close modal. Execute the action. Show loading state if async. |

### 2.5.5 Drag & Drop Interactions

| Context | Behavior |
|---|---|
| Skill tree node | Drag to reorder. Drop zone highlights. Snap animation on drop. |
| Exercise tab | Drag to reorder tabs. Insertion indicator shown between tabs. |
| Media upload | Drag files onto the upload zone. Zone border becomes dashed + highlighted. |

### 2.5.6 Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+K` / `Cmd+K` | Open global search |
| `Ctrl+S` / `Cmd+S` | Save current form (when in edit mode) |
| `Escape` | Close modal / drawer / search overlay |
| `Tab` / `Shift+Tab` | Navigate between focusable elements |
| `Enter` | Activate focused button/link |
| `Space` | Toggle focused checkbox/switch |
| `Arrow keys` | Navigate within tables, dropdowns, tab groups |

---

## 2.6 Validation Rules

### 2.6.1 Common Field Validations

| Field Type | Rule | Error Message |
|---|---|---|
| Required field | Must not be empty | "{Field name} is required." |
| Email | RFC 5322 format | "Please enter a valid email address." |
| Password | Min 12 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char | "Password must be at least 12 characters with uppercase, lowercase, number, and special character." |
| Text (min/max) | Character count within bounds | "{Field name} must be between {min} and {max} characters." |
| Number (range) | Within specified range | "{Field name} must be between {min} and {max}." |
| URL | Valid URL format (https preferred) | "Please enter a valid URL." |
| File upload | Type and size checks | "File must be {types} and under {maxSize}." |
| Dropdown | Selection required | "Please select a {field name}." |
| Date range | Start ≤ End | "Start date must be before end date." |
| Unique field | Server-side uniqueness check | "This {field name} is already in use." |

### 2.6.2 Validation Timing

| Trigger | Behavior |
|---|---|
| On blur | Validate the individual field. Show error if invalid. |
| On input (after error) | Re-validate on every keystroke to clear error as soon as value is valid. |
| On submit | Validate all fields. Show all errors. Focus first invalid field. |
| On paste | Validate after paste completes. Trim whitespace for text fields. |

### 2.6.3 Cross-Field Validations

| Scenario | Rule |
|---|---|
| Course source/target language | Must be different languages. |
| Experiment start/end date | End date must be after start date. Duration must be ≥ 1 day. |
| Feature flag percentage | Must be 0–100. Sum across variants ≤ 100%. |
| Exercise correct answer | Must be one of the provided options (multiple choice). |
| Password change | New password must differ from current password. Confirm password must match new password. |

---

## 2.7 Error States & Empty States

### 2.7.1 Error States

**API Error (General)**:
```
┌──────────────────────────────────────────┐
│  ⚠️ Something went wrong                 │
│                                          │
│  We couldn't load this data. Please      │
│  try again.                              │
│                                          │
│  [Retry]                                 │
│                                          │
│  Error code: ERR_500_INTERNAL            │
└──────────────────────────────────────────┘
```

**Network Error**:
```
┌──────────────────────────────────────────┐
│  📡 Connection Lost                       │
│                                          │
│  Please check your internet connection   │
│  and try again.                          │
│                                          │
│  [Retry]                                 │
└──────────────────────────────────────────┘
```

**Unauthorized (403)**:
```
┌──────────────────────────────────────────┐
│  🔒 Access Denied                         │
│                                          │
│  You don't have permission to view this  │
│  page. Contact your administrator if     │
│  you believe this is an error.           │
│                                          │
│  [Go to Dashboard]                       │
└──────────────────────────────────────────┘
```

**Not Found (404)**:
```
┌──────────────────────────────────────────┐
│  🔍 Page Not Found                        │
│                                          │
│  The page you're looking for doesn't     │
│  exist or has been moved.                │
│                                          │
│  [Go to Dashboard]                       │
└──────────────────────────────────────────┘
```

**Session Expired (401)**:
```
┌──────────────────────────────────────────┐
│  ⏱️ Session Expired                       │
│                                          │
│  Your session has expired. Please sign   │
│  in again to continue.                   │
│                                          │
│  [Sign In]                               │
└──────────────────────────────────────────┘
```

### 2.7.2 Empty States

**No Users Found (after search/filter)**:
```
┌──────────────────────────────────────────┐
│  🔍 No users match your search            │
│                                          │
│  Try adjusting your filters or search    │
│  terms.                                  │
│                                          │
│  [Clear Filters]                         │
└──────────────────────────────────────────┘
```

**No Courses Created**:
```
┌──────────────────────────────────────────┐
│  📚 No courses yet                        │
│                                          │
│  Create your first course to get         │
│  started building learning content.      │
│                                          │
│  [+ Create Course]                       │
└──────────────────────────────────────────┘
```

**No Flagged Content**:
```
┌──────────────────────────────────────────┐
│  ✅ All clear!                            │
│                                          │
│  There's no flagged content to review    │
│  right now. Great job keeping the        │
│  platform clean!                         │
└──────────────────────────────────────────┘
```

**No Analytics Data (new platform)**:
```
┌──────────────────────────────────────────┐
│  📊 Not enough data yet                   │
│                                          │
│  Analytics will appear once users start  │
│  engaging with the platform. Check back  │
│  in a few days.                          │
└──────────────────────────────────────────┘
```

**No A/B Tests**:
```
┌──────────────────────────────────────────┐
│  🧪 No experiments running                │
│                                          │
│  Create an A/B test to start optimizing  │
│  the user experience.                    │
│                                          │
│  [+ Create Experiment]                   │
└──────────────────────────────────────────┘
```

### 2.7.3 Loading States

| Component | Loading Indicator |
|---|---|
| Full page | Centered spinner (48px) with "Loading..." text |
| Table | Skeleton rows (8 rows of gray shimmer bars) |
| Chart | Skeleton chart (gray shimmer rectangle) |
| Card | Skeleton card (shimmer for title, value, subtitle) |
| Form | Individual field skeletons while pre-filling data |
| Button (action in progress) | Spinner inside button, button disabled |
| Image | Gray placeholder with shimmer, aspect ratio preserved |
| Sidebar | Fully rendered (cached navigation data) |

---

## 2.8 Accessibility Requirements

### 2.8.1 WCAG 2.1 AA Compliance

| Criterion | Requirement | Implementation |
|---|---|---|
| 1.1.1 Non-text Content | All images have alt text | `alt` attributes on all `<img>`. Decorative images use `alt=""`. |
| 1.3.1 Info and Relationships | Semantic HTML structure | Use `<nav>`, `<main>`, `<aside>`, `<header>`, `<footer>`, `<table>`, `<form>`. Heading hierarchy (h1-h6) is logical. |
| 1.4.1 Use of Color | Color is not the only indicator | Status badges include icons + text, not just color. Error fields have icons in addition to red borders. |
| 1.4.3 Contrast | 4.5:1 for normal text, 3:1 for large text | All color combinations tested with contrast checker. |
| 1.4.4 Resize Text | Content usable at 200% zoom | No content is cut off or overlapping at 200% browser zoom. |
| 2.1.1 Keyboard | All functionality via keyboard | Tab order follows visual order. Custom widgets have appropriate ARIA keyboard patterns. |
| 2.4.1 Skip Nav | Skip navigation link | Hidden "Skip to main content" link, visible on focus. |
| 2.4.7 Focus Visible | Visible focus indicator | 2px solid outline, offset by 2px, using brand accent color. |
| 3.3.1 Error Identification | Errors are described in text | Error messages appear below fields with `aria-describedby`. Fields use `aria-invalid="true"`. |
| 3.3.2 Labels | All inputs have labels | `<label>` elements linked via `for`/`id`. Placeholders are not substitutes for labels. |
| 4.1.2 Name, Role, Value | Custom widgets have ARIA | Custom dropdowns use `role="listbox"`. Tabs use `role="tablist"`. Modals use `role="dialog"`. |

### 2.8.2 ARIA Patterns

| Component | ARIA Pattern |
|---|---|
| Sidebar navigation | `role="navigation"`, `aria-label="Admin navigation"` |
| Collapsible sections | `aria-expanded="true/false"` on toggle button |
| Data table | `role="table"` with `aria-sort` on sortable columns |
| Sortable column | `aria-sort="ascending"`, `aria-sort="descending"`, or `aria-sort="none"` |
| Tab group | `role="tablist"`, `role="tab"`, `role="tabpanel"` with `aria-selected` |
| Modal dialog | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing to title |
| Toast notification | `role="alert"`, `aria-live="polite"` |
| Loading spinner | `role="status"`, `aria-label="Loading"` |
| Search input | `role="search"`, `aria-label="Search {context}"` |
| Breadcrumb | `aria-label="Breadcrumb"`, `aria-current="page"` on last item |
| Pagination | `aria-label="Pagination"`, `aria-current="page"` on active page |

### 2.8.3 Screen Reader Announcements

| Event | Announcement |
|---|---|
| Page navigation | Page title read via `<title>` tag update |
| Toast notification | Alert text read automatically via `aria-live` |
| Table sort change | "Sorted by {column}, {direction}" via `aria-live` region |
| Filter applied | "{N} results found" via `aria-live` region |
| Form submission success | "Form submitted successfully" via `aria-live` region |
| Form submission error | "Form has {N} errors. First error: {message}" via `aria-live` region |
| Modal open | Modal title read automatically via focus management |
| Modal close | Focus returns to trigger element |

### 2.8.4 Color & Theming

**Light Theme (Default)**:

| Token | Value | Usage |
|---|---|---|
| `--color-bg-primary` | `#FFFFFF` | Page background |
| `--color-bg-secondary` | `#F7F8FA` | Card backgrounds, sidebar |
| `--color-text-primary` | `#1A1A2E` | Headings, body text |
| `--color-text-secondary` | `#6B7280` | Labels, captions |
| `--color-accent` | `#58CC02` | Primary actions (Duolingo green) |
| `--color-accent-hover` | `#46A302` | Hover state |
| `--color-error` | `#DC2626` | Error text, error borders |
| `--color-warning` | `#F59E0B` | Warning badges |
| `--color-success` | `#10B981` | Success toasts, status indicators |
| `--color-info` | `#3B82F6` | Informational alerts |

**Dark Theme**:

| Token | Value | Usage |
|---|---|---|
| `--color-bg-primary` | `#1A1A2E` | Page background |
| `--color-bg-secondary` | `#232340` | Card backgrounds, sidebar |
| `--color-text-primary` | `#F0F0F5` | Headings, body text |
| `--color-text-secondary` | `#9CA3AF` | Labels, captions |
| `--color-accent` | `#58CC02` | Primary actions |
| `--color-accent-hover` | `#6EE018` | Hover state |
| `--color-error` | `#EF4444` | Error text, error borders |
| `--color-warning` | `#FBBF24` | Warning badges |
| `--color-success` | `#34D399` | Success toasts |
| `--color-info` | `#60A5FA` | Informational alerts |

### 2.8.5 Motion & Animation

- All animations respect `prefers-reduced-motion: reduce`. When reduced motion is preferred:
  - Transitions have `duration: 0ms`.
  - Skeleton shimmer is replaced with a static gray fill.
  - Slide-in panels appear instantly.
  - Chart animations are disabled.
- Default animation durations:
  - Micro-interactions (hover, focus): 150ms
  - Component transitions (modal, drawer): 200ms
  - Page transitions: 300ms
  - Chart animations: 500ms

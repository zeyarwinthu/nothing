# 2. Mobile UX Specification

> Screen-by-screen interaction design, navigation patterns, gestures, animations, error handling, and accessibility standards for the Duolingo-style learning platform.

---

## 2.1 Screen Inventory

### 2.1.1 Complete Screen List

| # | Screen Name | Route | Type | Auth Required |
|---|-------------|-------|------|---------------|
| 1 | Welcome | `/welcome` | Full screen | No |
| 2 | Language Selection | `/onboarding/language` | Full screen | No |
| 3 | Motivation Selection | `/onboarding/motivation` | Full screen | No |
| 4 | Daily Goal Selection | `/onboarding/goal` | Full screen | No |
| 5 | Experience Level | `/onboarding/level` | Full screen | No |
| 6 | Placement Test Prompt | `/onboarding/placement-prompt` | Full screen | No |
| 7 | Account Creation Prompt | `/onboarding/account-prompt` | Full screen | No |
| 8 | Signup | `/auth/signup` | Full screen | No |
| 9 | Login | `/auth/login` | Full screen | No |
| 10 | Forgot Password | `/auth/forgot-password` | Full screen | No |
| 11 | Reset Password | `/auth/reset-password` | Full screen (deep link) | No |
| 12 | Placement Test Instructions | `/placement/instructions` | Full screen | Yes* |
| 13 | Placement Test Question | `/placement/question` | Full screen | Yes* |
| 14 | Placement Test Results | `/placement/results` | Full screen | Yes* |
| 15 | Home (Skill Tree) | `/home` | Tab shell | Yes |
| 16 | Skill Detail | `/home` (bottom sheet) | Bottom sheet | Yes |
| 17 | Lesson Loading | `/lesson/loading` | Full screen | Yes |
| 18 | Exercise | `/lesson/exercise` | Full screen | Yes |
| 19 | Lesson Complete | `/lesson/complete` | Full screen | Yes |
| 20 | Out of Lives | `/lesson/out-of-lives` | Modal | Yes |
| 21 | Leaderboard | `/leaderboard` | Tab shell | Yes |
| 22 | Shop | `/shop` | Tab shell | Yes |
| 23 | Profile | `/profile` | Tab shell | Yes |
| 24 | Profile Edit | `/profile/edit` | Full screen (push) | Yes |
| 25 | Achievements | `/profile/achievements` | Full screen (push) | Yes |
| 26 | Achievement Detail | `/profile/achievements/:id` | Modal | Yes |
| 27 | Friends List | `/profile/friends` | Full screen (push) | Yes |
| 28 | Settings | `/settings` | Full screen (push) | Yes |
| 29 | Notification Settings | `/settings/notifications` | Full screen (push) | Yes |
| 30 | Course Switcher | `/home` (bottom sheet) | Bottom sheet | Yes |
| 31 | Streak Detail | `/home` (modal) | Modal | Yes |
| 32 | Tips & Notes | `/skill/:id/tips` | Full screen (push) | Yes |
| 33 | Statistics | `/profile/statistics` | Full screen (push) | Yes |

> *Yes = authenticated or anonymous session

### 2.1.2 Screen Layout Templates

#### Full Screen Template

```
┌────────────────────────────────────────┐
│ Status Bar (system)                    │
├────────────────────────────────────────┤
│ App Bar (optional)                     │
│   [Back/Close]  Title  [Action]        │
├────────────────────────────────────────┤
│                                        │
│                                        │
│           Content Area                 │
│        (scrollable if needed)          │
│                                        │
│                                        │
├────────────────────────────────────────┤
│ Bottom Action Area (optional)          │
│        [ Primary CTA ]                 │
├────────────────────────────────────────┤
│ Bottom Tab Bar (if in shell)           │
└────────────────────────────────────────┘
```

#### Bottom Sheet Template

```
┌────────────────────────────────────────┐
│                                        │
│     Dimmed Background                  │
│     (tap to dismiss)                   │
│                                        │
├────────────────────────────────────────┤
│ ──── Drag Handle ────                  │
│                                        │
│ Sheet Content                          │
│ (scrollable if content overflows)      │
│                                        │
│        [ Primary CTA ]                 │
└────────────────────────────────────────┘
```

#### Modal Dialog Template

```
┌────────────────────────────────────────┐
│                                        │
│     Dimmed Background                  │
│     (tap to dismiss, unless blocking)  │
│                                        │
│   ┌────────────────────────────────┐   │
│   │ [X]              Title         │   │
│   │                                │   │
│   │       Content                  │   │
│   │                                │   │
│   │  [Secondary]     [Primary]     │   │
│   └────────────────────────────────┘   │
│                                        │
└────────────────────────────────────────┘
```

---

## 2.2 Navigation Patterns

### 2.2.1 Navigation Architecture

The app uses a hybrid navigation architecture combining:

1. **Tab Navigation** (bottom tab bar) — top-level sections
2. **Stack Navigation** — within each tab
3. **Modal Presentation** — overlays, confirmations, celebrations
4. **Bottom Sheets** — contextual detail views

```
TabShell
├── Home Tab (Stack)
│   ├── Home Screen (root)
│   ├── Skill Detail (bottom sheet)
│   ├── Tips & Notes (push)
│   └── Course Switcher (bottom sheet)
├── Leaderboard Tab (Stack)
│   └── Leaderboard Screen (root)
├── Shop Tab (Stack)
│   └── Shop Screen (root)
└── Profile Tab (Stack)
    ├── Profile Screen (root)
    ├── Profile Edit (push)
    ├── Achievements (push)
    │   └── Achievement Detail (modal)
    ├── Friends (push)
    ├── Statistics (push)
    └── Settings (push)
        └── Notification Settings (push)

Lesson Flow (independent stack, outside tab shell)
├── Lesson Loading
├── Exercise (repeated)
├── Out of Lives (modal)
└── Lesson Complete

Auth Flow (independent stack, outside tab shell)
├── Welcome
├── Signup / Login
└── Forgot Password / Reset Password

Onboarding Flow (independent stack, outside tab shell)
├── Language Selection
├── Motivation
├── Daily Goal
├── Experience Level
├── Placement Test Prompt
└── Account Prompt
```

### 2.2.2 Tab Bar Specification

| Property | Detail |
|----------|--------|
| Type | Fixed bottom tab bar |
| Height | 56dp + safe area inset (bottom) |
| Background | White with 1dp top border (color: `#E5E5E5`) |
| Icons | 24×24dp, centered in 48×48dp touch target |
| Active State | Icon filled + brand green color (`#58CC02`) + label visible |
| Inactive State | Icon outlined + gray color (`#AFAFAF`) + label visible |
| Animation | 150ms color cross-fade on tab switch |
| Badge | Red dot on tab icon for unread notifications (e.g., leaderboard promotion) |
| Behavior | Tapping active tab scrolls to top; tapping inactive tab switches and resets stack |

### 2.2.3 Stack Navigation

| Transition | Animation | Duration |
|------------|-----------|----------|
| Push (forward) | New screen slides in from right | 300ms, ease-in-out |
| Pop (back) | Current screen slides out to right | 300ms, ease-in-out |
| Replace | Cross-fade | 200ms |
| Push (lesson start) | Slide up from bottom | 350ms, ease-out |
| Pop (lesson exit) | Slide down to bottom | 300ms, ease-in |

### 2.2.4 Back Navigation

| Context | Back Behavior |
|---------|---------------|
| Stack screen | System back / back arrow → pop |
| Bottom sheet | Swipe down / tap dimmed area → dismiss |
| Modal | Close button / system back → dismiss |
| Lesson exercise | Close button → confirmation dialog → pop to home |
| Onboarding | Back arrow → previous onboarding step |
| Tab root | System back → exit app confirmation (Android) |

### 2.2.5 Deep Link Routing

| Link Pattern | Target Screen |
|--------------|---------------|
| `app://home` | Home Screen |
| `app://lesson/{skill_id}` | Lesson Loading (auto-start) |
| `app://leaderboard` | Leaderboard Screen |
| `app://shop` | Shop Screen |
| `app://profile/{user_id}` | Profile Screen |
| `app://streak` | Streak Detail Modal |
| `app://achievement/{id}` | Achievement Detail Modal |
| `app://settings` | Settings Screen |
| `app://reset-password?token={t}` | Reset Password Screen |

---

## 2.3 Interaction Rules

### 2.3.1 Tap Interactions

| Element Type | Tap Behavior | Visual Feedback |
|--------------|-------------|-----------------|
| Button (primary) | Execute action | Darken 10% for 100ms (press state), then release |
| Button (disabled) | No action | No visual change; tooltip on long-press explaining why disabled |
| Card (selectable) | Toggle selection | Border highlight + checkmark; scale 0.98 on press, 1.0 on release |
| List Item | Navigate / expand | Ripple effect (Material) or highlight (iOS) |
| Icon Button | Execute action | Scale 0.9 on press, 1.0 on release with spring animation |
| Text Link | Navigate | Underline on press state |
| Word Bank Tile | Add to answer / remove | Tile animates position change (slide to slot / back to bank) |
| Audio Button | Play audio | Pulsing ring animation while playing |

### 2.3.2 Long-Press Interactions

| Element | Long-Press Action |
|---------|-------------------|
| Skill Node | Show context menu: "Download for Offline", "View Tips", "Share" |
| Word (in sentence) | Show word definition tooltip |
| Message / Text | Copy to clipboard |
| Profile Avatar | Open image viewer |
| Achievement Badge | Show sharing options |

### 2.3.3 Input Field Behaviors

| Property | Detail |
|----------|--------|
| Focus | Blue border (2dp) + label floats above field |
| Error | Red border (2dp) + error message below in red |
| Character Counter | Shown for fields with max length (e.g., bio: "45/140") |
| Autocomplete | Email fields: show email autocomplete suggestions |
| Password | Toggle visibility icon (eye) at trailing end |
| Keyboard Type | Email fields: `TextInputType.emailAddress`; number fields: `TextInputType.number` |
| Submit on Enter | Login/signup forms submit on keyboard "Done" action |

### 2.3.4 Button States

| State | Appearance |
|-------|------------|
| Default | Full color, enabled |
| Hover (web/desktop) | Slightly lighter color |
| Pressed | 10% darker, scale 0.98 |
| Disabled | 40% opacity, no interaction |
| Loading | Replace label with circular spinner (same color), disabled |

---

## 2.4 Gestures

### 2.4.1 Supported Gestures

| Gesture | Context | Action |
|---------|---------|--------|
| Vertical Scroll | Skill tree, lists, settings | Scroll content |
| Pull-to-Refresh | Home, leaderboard | Refresh data from API |
| Swipe Down | Bottom sheet | Dismiss sheet |
| Swipe Right (from left edge) | Stack screens | Navigate back (iOS-style) |
| Drag | Word bank tiles | Reorder answer words |
| Pinch-to-Zoom | Tips & notes images | Zoom in/out on images |
| Double Tap | Image in tips | Quick zoom to 2× |
| Long Press + Drag | Matching exercise | Alternative to tap-tap matching |

### 2.4.2 Gesture Configuration

| Property | Detail |
|----------|--------|
| Scroll Physics | `BouncingScrollPhysics` on iOS, `ClampingScrollPhysics` on Android |
| Pull-to-Refresh Threshold | 80dp pull distance to trigger |
| Swipe-Back Threshold | 20dp from left edge, 100dp minimum horizontal travel |
| Drag Sensitivity | 8dp slop distance before drag starts |
| Long-Press Duration | 500ms to trigger |

### 2.4.3 Gesture Conflict Resolution

| Scenario | Resolution |
|----------|------------|
| Vertical scroll vs. pull-to-refresh | Pull-to-refresh only activates when scroll position is at top |
| Horizontal swipe-back vs. horizontal scroll | Edge detection (20dp from left edge = swipe-back) |
| Tap vs. long-press | If finger lifts before 500ms = tap; otherwise = long-press |
| Drag vs. tap on word tile | If finger moves >8dp = drag; otherwise = tap |

---

## 2.5 Animations & Transitions

### 2.5.1 Page Transitions

| Transition | Animation | Duration | Curve |
|------------|-----------|----------|-------|
| Onboarding forward | Slide left + fade in | 300ms | `Curves.easeInOut` |
| Onboarding back | Slide right + fade in | 300ms | `Curves.easeInOut` |
| Tab switch | Cross-fade | 200ms | `Curves.easeIn` |
| Push navigation | Slide from right (Material) / slide from right with parallax (iOS) | 300ms | `Curves.easeInOutCubic` |
| Lesson start | Slide up from bottom | 350ms | `Curves.easeOutCubic` |
| Lesson exit | Slide down | 300ms | `Curves.easeInCubic` |
| Modal appear | Scale from 0.8 + fade in | 250ms | `Curves.easeOutBack` |
| Modal dismiss | Scale to 0.8 + fade out | 200ms | `Curves.easeIn` |
| Bottom sheet appear | Slide up from bottom | 300ms | `Curves.easeOutCubic` |
| Bottom sheet dismiss | Slide down | 250ms | `Curves.easeInCubic` |

### 2.5.2 Micro-Interactions

| Element | Animation | Detail |
|---------|-----------|--------|
| XP counter | Count-up number animation | From 0 to earned amount over 600ms with `Curves.easeOut` |
| Progress bar | Width animation | Smooth fill with spring physics (300ms) |
| Heart loss | Scale + fade | Heart shrinks to 0.5× then fades (400ms) |
| Correct answer | Bottom bar slide up + check icon scale | Bar slides up (250ms), icon scales from 0 to 1 with overshoot (300ms) |
| Incorrect answer | Bottom bar slide up + shake | Bar slides up (250ms), content shakes horizontally 3× (±8dp, 300ms) |
| Streak fire | Pulsing glow | Continuous pulse at milestone (opacity 0.6→1.0, 800ms, repeat) |
| Skill node bounce | Subtle vertical bounce | Available skill nodes bounce 4dp up-down (1200ms period, continuous) |
| Button press | Scale | Scale to 0.95 on press, spring back to 1.0 on release |
| Card selection | Border + scale | Green border fades in (150ms), card scales to 0.98 then 1.0 (200ms) |
| Loading shimmer | Gradient sweep | Left-to-right gradient sweep (1500ms, repeat) |

### 2.5.3 Celebration Animations

| Event | Animation | Duration |
|-------|-----------|----------|
| Lesson complete | Confetti particle system (200 particles, gravity, multi-color) | 2000ms |
| Daily goal met | Star burst + radial shine from progress bar | 1500ms |
| Streak milestone | Fire emoji scales up + particle burst + screen shake | 2000ms |
| Crown earned | Crown icon descends from top, settles on skill node with bounce | 1500ms |
| League promotion | Trophy rises, confetti, league badge morphs | 2500ms |
| Achievement earned | Badge scales up from center with circular ripple | 1800ms |
| Perfect lesson | "Perfect!" text scales up with golden glow + sparkle particles | 1500ms |

### 2.5.4 Loading States

| Context | Loading UI |
|---------|-----------|
| API calls (short, <2s) | Inline spinner or skeleton loader |
| API calls (long, 2s+) | Full-screen loading with mascot animation |
| Image loading | Placeholder shimmer → fade-in image (300ms) |
| Lesson loading | Custom animation: mascot doing lesson prep |
| Content sync | Subtle progress bar in top bar |
| Pull-to-refresh | Custom indicator: mascot pulling down |

### 2.5.5 Animation Performance Rules

| Rule | Detail |
|------|--------|
| Frame Rate | All animations must maintain 60fps minimum |
| Hardware Acceleration | Use `RepaintBoundary` around complex animation widgets |
| Reduced Motion | Respect system reduced-motion setting; replace animations with instant transitions |
| Pre-Computation | Pre-compute particle paths for celebration animations |
| Disposal | Cancel all animation controllers in `dispose()` method |

---

## 2.6 Error States

### 2.6.1 Network Errors

| Scenario | Display | Recovery |
|----------|---------|----------|
| No internet (first load) | Full-screen empty state: "No internet connection" with airplane icon, "Retry" button, "Continue Offline" option | Retry button triggers data fetch; offline option loads cached data |
| No internet (refresh) | Snackbar at bottom: "No internet connection" (3s auto-dismiss) | Pull-to-refresh to retry |
| No internet (mid-lesson) | No interruption; lesson continues; sync queued | Automatic sync on reconnect |
| Timeout (API call) | Snackbar: "Request timed out. Try again." with "Retry" action | Tap retry in snackbar |
| Server error (5xx) | Dialog: "Something went wrong. We're working on it." with "Try Again" and "OK" buttons | "Try Again" retries the request |
| Auth error (401) | Silent token refresh → retry. If refresh fails: "Session expired" dialog → login screen | Automatic |

### 2.6.2 Empty States

| Context | Display |
|---------|---------|
| Leaderboard (no data) | Mascot with magnifying glass: "Complete a lesson to join the leaderboard!" |
| Friends list (empty) | Mascot waving: "Invite friends to learn together!" with "Invite" button |
| Achievements (none earned) | Gray badge grid: "Start earning achievements by completing lessons!" |
| Search results (no match) | Mascot shrugging: "No results found. Try a different search." |
| Offline content (none cached) | Download icon: "Download lessons to practice offline" with "Download" button |

### 2.6.3 Form Validation Errors

| Field | Validation | Error Message |
|-------|-----------|---------------|
| Email (empty) | Required | "Email is required" |
| Email (invalid format) | RFC 5322 regex | "Please enter a valid email address" |
| Email (already exists) | API check | "An account with this email already exists. [Log in instead]" |
| Password (too short) | Min 8 chars | "Password must be at least 8 characters" |
| Password (missing uppercase) | Regex `/[A-Z]/` | "Password must include an uppercase letter" |
| Password (missing number) | Regex `/[0-9]/` | "Password must include a number" |
| Password (missing special) | Regex `/[!@#$%^&*]/` | "Password must include a special character" |
| Username (too short) | Min 3 chars | "Username must be at least 3 characters" |
| Username (invalid chars) | Regex `/^[a-zA-Z0-9_]+$/` | "Username can only contain letters, numbers, and underscores" |
| Username (taken) | API check | "This username is already taken" |
| Passwords (mismatch) | Equality check | "Passwords don't match" |

### 2.6.4 Content Errors

| Scenario | Display | Recovery |
|----------|---------|----------|
| Audio file failed to load | Grayed-out speaker icon with "!" badge; toast: "Audio unavailable" | Exercise continues without audio; tap speaker icon to retry |
| Image failed to load | Placeholder with broken-image icon | Automatic retry on scroll-into-view |
| Exercise data corrupt | Skip exercise silently; log error | Move to next exercise |
| Speech recognition failed | "Couldn't hear you. Try again." with "Retry" and "Skip" options | Tap retry to re-record |

### 2.6.5 Purchase Errors

| Scenario | Display | Recovery |
|----------|---------|----------|
| Insufficient gems | Dialog: "Not enough gems! You need [X] more." with "Get Gems" and "Cancel" | "Get Gems" navigates to gem purchase screen |
| IAP failed | Dialog: "Purchase couldn't be completed. You were not charged." with "Try Again" and "Cancel" | "Try Again" re-initiates purchase |
| Subscription already active | Toast: "You already have an active subscription" | N/A |
| Receipt validation failed | Dialog: "We couldn't verify your purchase. Contact support if charged." with "Contact Support" | Opens support channel |

---

## 2.7 Accessibility Requirements

### 2.7.1 WCAG 2.1 AA Compliance

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| 1.1.1 Non-text Content | All images have alt text | `Semantics(label: ...)` on every `Image` widget |
| 1.3.1 Info and Relationships | Heading hierarchy | Use `Semantics(header: true)` for headings |
| 1.4.1 Use of Color | Color is not sole indicator | All status indicators use icon + color + label |
| 1.4.3 Contrast (Minimum) | 4.5:1 for text, 3:1 for large text | Verified with contrast checker tool |
| 1.4.4 Resize Text | Up to 200% without loss | Dynamic type support via `MediaQuery.textScaleFactor` |
| 1.4.11 Non-text Contrast | 3:1 for UI components | Borders and focus indicators meet contrast requirements |
| 2.1.1 Keyboard | All functionality via keyboard | Full keyboard navigation on tablets/desktop |
| 2.4.3 Focus Order | Logical focus order | Tab order follows visual layout |
| 2.4.6 Headings and Labels | Descriptive headings | Every screen has semantic heading |
| 2.4.7 Focus Visible | Visible focus indicator | 2dp border in brand green color |
| 3.2.2 On Input | No auto-context-change | Forms don't auto-submit on input |
| 4.1.2 Name, Role, Value | All components have accessible names | Semantic labels on all interactive elements |

### 2.7.2 Screen Reader Support

| Feature | Implementation |
|---------|----------------|
| Screen Announcements | `SemanticsService.announce()` for dynamic content changes |
| Live Regions | XP counter, progress bar, streak counter marked as live regions |
| Custom Actions | Semantic actions for complex gestures (e.g., "double-tap to select" for word bank tiles) |
| Route Announcements | `RouteSettings(name: ...)` for automatic screen title announcement |
| Image Descriptions | All illustrations have descriptive labels; decorative images marked `excludeFromSemantics: true` |
| Exercise Reading Order | Prompt → options → check button (logical top-to-bottom order) |
| Answer Feedback | Correct/incorrect results announced immediately via screen reader |
| Grouping | Related elements grouped with `MergeSemantics` (e.g., streak icon + count = "15-day streak") |

### 2.7.3 Motor Accessibility

| Feature | Implementation |
|---------|----------------|
| Touch Target Size | Minimum 48×48dp for all interactive elements |
| Spacing | Minimum 8dp between touch targets |
| Gesture Alternatives | All swipe actions have tap alternatives |
| Timeout Extensions | No time-limited actions in exercises (except optional timed practice) |
| Switch Control | All actions achievable via iOS Switch Control / Android Switch Access |
| One-Hand Mode | Critical actions reachable in bottom 2/3 of screen |

### 2.7.4 Visual Accessibility

| Feature | Implementation |
|---------|----------------|
| Dynamic Type | All text responds to system font size setting (up to 3× default) |
| High Contrast Mode | Alternative color palette with increased contrast ratios (7:1 for text) |
| Colorblind Modes | Three presets adjusting the color palette for protanopia, deuteranopia, tritanopia |
| Dark Mode | Full dark theme support: dark backgrounds, light text, adjusted illustration colors |
| Reduced Motion | Respects `MediaQuery.disableAnimations`; replaces all animations with instant transitions |
| Bold Text | Responds to system bold text setting |

### 2.7.5 Audio Accessibility

| Feature | Implementation |
|---------|----------------|
| Captions | All audio exercises show text transcript |
| Visual Audio Indicator | Animated waveform visualization during audio playback |
| Haptic as Audio Alternative | Correct = single vibration; incorrect = double vibration |
| Volume Independent | No critical information conveyed only through audio |
| Audio Descriptions | Exercise types clearly labeled so users know what to expect |

### 2.7.6 Cognitive Accessibility

| Feature | Implementation |
|---------|----------------|
| Consistent Navigation | Same tab bar and navigation patterns throughout the app |
| Clear Language | All instruction text at 6th-grade reading level (Flesch-Kincaid ≥ 70) |
| Error Prevention | Confirmation dialogs for destructive actions (exit lesson, delete account) |
| Progress Indicators | Clear progress bars showing lesson/course completion |
| Undo Support | Tap-to-remove in word bank; "undo" for accidental purchases (5-second window) |
| Predictable Behavior | Consistent button placement and behavior across all screens |

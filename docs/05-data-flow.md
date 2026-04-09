# 5. Admin Panel Data Flow Documentation

> Describes how data moves between UI components, the state layer, and the backend API. Covers loading states, error handling, optimistic updates, pagination, and real-time data.

---

## 5.1 Overview of Data Flow Architecture

### 5.1.1 Unidirectional Data Flow

The Admin Panel follows a strict unidirectional data flow pattern:

```
User Interaction
      │
      ▼
Component dispatches Action
      │
      ▼
NgRx Reducer updates State (synchronous)
      │
      ▼
NgRx Effect handles side effects (API calls)
      │
      ▼
API Response triggers Success/Failure Action
      │
      ▼
Reducer updates State
      │
      ▼
Selector emits new data
      │
      ▼
Component re-renders via signals/async pipe
```

### 5.1.2 Data Flow Layers

```
┌─────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                 │
│  Components • Templates • Pipes • Directives        │
│  (Reads state via selectors, dispatches actions)     │
├─────────────────────────────────────────────────────┤
│  STATE LAYER                                        │
│  NgRx Store • Reducers • Selectors • Entity Adapter │
│  (Single source of truth, immutable state)          │
├─────────────────────────────────────────────────────┤
│  EFFECT LAYER                                       │
│  NgRx Effects • Side Effect Handlers                │
│  (API calls, navigation, toast notifications)       │
├─────────────────────────────────────────────────────┤
│  SERVICE LAYER                                      │
│  API Services • HTTP Client • Interceptors          │
│  (Transforms requests/responses, handles auth)      │
├─────────────────────────────────────────────────────┤
│  NETWORK LAYER                                      │
│  HTTP Requests • WebSocket • Caching                │
│  (Transport, retry, and caching)                    │
└─────────────────────────────────────────────────────┘
```

---

## 5.2 UI → API → UI Data Lifecycle

### 5.2.1 Read Flow (Loading Data)

**Example: Loading Learner List**

```
Step 1: Component initializes
─────────────────────────────
LearnerListPageComponent.ngOnInit()
  → store.dispatch(UserActions.loadLearners({ page: 1, perPage: 25 }))

Step 2: Reducer sets loading state
──────────────────────────────────
State: { learners: [], loading: true, error: null }
  → Component shows skeleton loader

Step 3: Effect calls API
────────────────────────
UserEffects.loadLearners$
  → userService.getLearners({ page: 1, perPage: 25 })
  → GET /api/admin/users/learners?page=1&perPage=25

Step 4a: Success
────────────────
API returns: { data: [...], meta: { page: 1, perPage: 25, total: 142039 } }
  → store.dispatch(UserActions.loadLearnersSuccess({ learners, meta }))
  → Reducer: { learners: [...], loading: false, error: null, pagination: { ... } }
  → Component renders data table

Step 4b: Failure
────────────────
API returns: HTTP 500
  → store.dispatch(UserActions.loadLearnersFailure({ error: 'Failed to load users' }))
  → Reducer: { learners: [], loading: false, error: 'Failed to load users' }
  → Component shows error state with retry button
```

### 5.2.2 Write Flow (Creating/Updating Data)

**Example: Publishing a Course**

```
Step 1: User clicks "Publish"
─────────────────────────────
CourseBuilderPageComponent.onPublish()
  → confirmDialog.confirm({ title: 'Publish Course?', ... })
  → User confirms
  → store.dispatch(CourseActions.publishCourse({ id: 'course_42' }))

Step 2: Reducer sets saving state
─────────────────────────────────
State: { selectedCourse: { ...course, status: 'draft' }, saving: true }
  → Publish button shows spinner, is disabled

Step 3: Effect calls API
────────────────────────
CourseEffects.publishCourse$
  → courseService.publishCourse('course_42')
  → POST /api/admin/courses/course_42/publish

Step 4a: Success
────────────────
API returns: { data: { ...course, status: 'published' } }
  → store.dispatch(CourseActions.publishCourseSuccess({ course }))
  → Reducer: { selectedCourse: { ...course, status: 'published' }, saving: false }
  → toastService.success('Course published successfully!')
  → router.navigate(['/courses'])

Step 4b: Failure
────────────────
API returns: HTTP 422 { errors: [{ code: 'INCOMPLETE', message: 'Missing lessons' }] }
  → store.dispatch(CourseActions.publishCourseFailure({ error }))
  → Reducer: { saving: false, error: 'Missing lessons in skill "Basics"' }
  → toastService.error('Could not publish: Missing lessons in skill "Basics"')
  → Publish button re-enabled
```

### 5.2.3 Delete Flow

**Example: Deleting a Feature Flag**

```
Step 1: User clicks "Delete"
─────────────────────────────
  → confirmDialog.confirm({
      title: 'Delete Feature Flag?',
      message: 'This will permanently remove "new-hearts-system".',
      confirmVariant: 'danger',
    })
  → User confirms
  → store.dispatch(FlagActions.deleteFlag({ id: 'flag_123' }))

Step 2: Optimistic removal from list
─────────────────────────────────────
Reducer immediately removes the flag from the entity state.
  → UI updates instantly (flag disappears from table)

Step 3: Effect calls API
────────────────────────
  → DELETE /api/admin/feature-flags/flag_123

Step 4a: Success
────────────────
  → toastService.success('Feature flag deleted.')
  → No state change needed (already removed)

Step 4b: Failure
────────────────
  → store.dispatch(FlagActions.deleteFlagFailure({ id: 'flag_123', flag: originalFlag }))
  → Reducer re-inserts the flag into entity state
  → toastService.error('Failed to delete flag. It has been restored.')
```

---

## 5.3 Loading States

### 5.3.1 Loading State Types

| Type | Trigger | UI Behavior | Duration |
|---|---|---|---|
| **Initial Load** | Page navigation | Full skeleton loader | 200ms–3s |
| **Refresh** | Pull-to-refresh, retry | Inline spinner (data stays visible) | 200ms–3s |
| **Pagination** | Page change | Table rows replaced with skeleton | 100ms–1s |
| **Action** | Button click (save, delete) | Button spinner, button disabled | 200ms–5s |
| **Background** | Auto-refresh, polling | No visible indicator (silent update) | Ongoing |
| **Search** | Search input change | Inline spinner in search bar | 300ms–2s |

### 5.3.2 Loading State Implementation

**Global Loading State per Feature**:

```typescript
// State shape for every feature
interface FeatureState {
  data: any[];
  loading: boolean;         // Initial load / hard refresh
  refreshing: boolean;      // Background refresh
  saving: boolean;          // Write operation in progress
  error: string | null;
}
```

**Component Loading Logic**:

```typescript
// Using Angular's new control flow
@Component({
  template: `
    @if (loading()) {
      <app-skeleton-loader type="table" [rows]="pageSize()"></app-skeleton-loader>
    } @else if (error()) {
      <app-error-state [error]="error()" (retry)="reload()"></app-error-state>
    } @else {
      <app-data-table
        [data]="data()"
        [columns]="columns"
        [class.refreshing]="refreshing()">
      </app-data-table>
    }
  `,
})
export class ListPageComponent {
  loading = this.store.selectSignal(selectLoading);
  refreshing = this.store.selectSignal(selectRefreshing);
  error = this.store.selectSignal(selectError);
  data = this.store.selectSignal(selectData);
}
```

### 5.3.3 Skeleton Loader Variants

| Variant | Used For | Structure |
|---|---|---|
| `table` | List pages | Rows of horizontal bars (header + N data rows) |
| `card-grid` | Course cards | Grid of card-shaped rectangles |
| `detail` | Detail pages | Header block + tab bar + content block |
| `chart` | Analytics | Rectangle with subtle axis lines |
| `form` | Edit pages | Stacked input-shaped rectangles |
| `metric-cards` | Dashboard | Row of metric card-shaped rectangles |

### 5.3.4 Minimum Loading Duration

To prevent flickering when API responses are fast:

```typescript
// Utility: Ensure minimum loading duration
function withMinDuration<T>(minMs: number = 300): OperatorFunction<T, T> {
  return (source$) => {
    const start = Date.now();
    return source$.pipe(
      delayWhen(() => {
        const elapsed = Date.now() - start;
        const remaining = Math.max(0, minMs - elapsed);
        return timer(remaining);
      }),
    );
  };
}

// Usage in effect
loadLearners$ = createEffect(() =>
  this.actions$.pipe(
    ofType(UserActions.loadLearners),
    switchMap(({ params }) =>
      this.userService.getLearners(params).pipe(
        withMinDuration(300),
        map((response) => UserActions.loadLearnersSuccess({ ... })),
        catchError((error) => of(UserActions.loadLearnersFailure({ ... }))),
      ),
    ),
  ),
);
```

---

## 5.4 Error Handling

### 5.4.1 Error Classification

| Category | HTTP Status | User Impact | Handling Strategy |
|---|---|---|---|
| **Client Error** | 400 | Invalid input | Show field-level validation errors |
| **Unauthorized** | 401 | Session expired | Redirect to login |
| **Forbidden** | 403 | Insufficient permissions | Show access denied page/message |
| **Not Found** | 404 | Resource deleted/moved | Show 404 page or toast |
| **Conflict** | 409 | Concurrent modification | Show conflict resolution dialog |
| **Validation** | 422 | Business rule violation | Show error details inline |
| **Rate Limited** | 429 | Too many requests | Show warning, disable action temporarily |
| **Server Error** | 500 | Backend failure | Show generic error with retry |
| **Network Error** | 0 / timeout | Connection lost | Show offline banner, retry on reconnect |

### 5.4.2 Error Handling Per Layer

**Interceptor Layer** (global):

```typescript
// Handles cross-cutting concerns
- 401 → Attempt token refresh → Redirect to login if fails
- 403 → Toast: "Access denied"
- 429 → Toast: "Too many requests, please wait"
- 500 → Toast: "Server error, please try again"
- Network error → Toast: "Connection lost"
```

**Effect Layer** (feature-specific):

```typescript
// Handles feature-specific error mapping
loadLearners$ = createEffect(() =>
  this.actions$.pipe(
    ofType(UserActions.loadLearners),
    switchMap(({ params }) =>
      this.userService.getLearners(params).pipe(
        map((response) => UserActions.loadLearnersSuccess({ ... })),
        catchError((error: HttpErrorResponse) => {
          const message = this.mapError(error);
          return of(UserActions.loadLearnersFailure({ error: message }));
        }),
      ),
    ),
  ),
);

private mapError(error: HttpErrorResponse): string {
  if (error.status === 0) return 'Unable to connect to the server.';
  if (error.error?.errors?.length) return error.error.errors[0].message;
  return 'An unexpected error occurred.';
}
```

**Component Layer** (UI):

```typescript
// Displays errors from state
error = this.store.selectSignal(selectError);

// Template
@if (error()) {
  <app-error-state [error]="error()" (retry)="reload()"></app-error-state>
}
```

### 5.4.3 Retry Strategy

```typescript
// Automatic retry for transient errors (network, 5xx)
@Injectable({ providedIn: 'root' })
export class RetryService {
  withRetry<T>(maxRetries = 3, delayMs = 1000): OperatorFunction<T, T> {
    return (source$) =>
      source$.pipe(
        retry({
          count: maxRetries,
          delay: (error, retryCount) => {
            // Only retry on network errors and 5xx
            if (error instanceof HttpErrorResponse) {
              if (error.status === 0 || error.status >= 500) {
                const backoff = delayMs * Math.pow(2, retryCount - 1);
                return timer(backoff);
              }
            }
            // Don't retry client errors
            return throwError(() => error);
          },
        }),
      );
  }
}
```

### 5.4.4 Form Validation Errors

When the API returns 422 with field-level errors:

```typescript
// API Response
{
  "errors": [
    { "code": "INVALID", "field": "title", "message": "Title already exists" },
    { "code": "REQUIRED", "field": "targetLanguage", "message": "Target language is required" }
  ]
}

// Effect maps to form
publishCourseFail$ = createEffect(() =>
  this.actions$.pipe(
    ofType(CourseActions.publishCourseFailure),
    tap(({ errors }) => {
      // Set server-side errors on the form
      errors.forEach((err) => {
        const control = this.courseForm.get(err.field);
        if (control) {
          control.setErrors({ serverError: err.message });
        }
      });
    }),
  ),
  { dispatch: false },
);
```

### 5.4.5 Global Error Boundary

A top-level error handler catches uncaught exceptions:

```typescript
@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  private toastService = inject(ToastService);
  private loggingService = inject(LoggingService);

  handleError(error: unknown): void {
    // Log to monitoring service (e.g., Sentry)
    this.loggingService.captureException(error);

    // Show user-facing message
    if (error instanceof HttpErrorResponse) {
      // Already handled by interceptor
      return;
    }

    this.toastService.error('An unexpected error occurred. Please refresh the page.');
    console.error('Unhandled error:', error);
  }
}
```

---

## 5.5 Optimistic Updates

### 5.5.1 When to Use Optimistic Updates

| Action | Optimistic? | Reason |
|---|---|---|
| Toggle feature flag on/off | ✅ Yes | Low risk, easily reversible |
| Delete item from a list | ✅ Yes | Immediate visual feedback, undo available |
| Reorder items (drag & drop) | ✅ Yes | Must feel instant for good UX |
| Approve/dismiss moderation item | ✅ Yes | Quick, frequent action |
| Create a new entity | ❌ No | Need server-generated ID |
| Publish a course | ❌ No | Significant action, needs server validation |
| Update complex form | ❌ No | Many fields, complex validation |
| Assign user role | ❌ No | Security-sensitive, must confirm server-side |

### 5.5.2 Optimistic Update Pattern

```typescript
// Actions
export const toggleFeatureFlag = createAction(
  '[Feature Flags] Toggle Flag',
  props<{ id: string; enabled: boolean }>(),
);
export const toggleFeatureFlagSuccess = createAction(
  '[Feature Flags API] Toggle Flag Success',
  props<{ flag: FeatureFlag }>(),
);
export const toggleFeatureFlagFailure = createAction(
  '[Feature Flags API] Toggle Flag Failure',
  props<{ id: string; previousEnabled: boolean; error: string }>(),
);

// Reducer — optimistic update
on(toggleFeatureFlag, (state, { id, enabled }) =>
  adapter.updateOne({ id, changes: { enabled } }, state),
),

// Reducer — rollback on failure
on(toggleFeatureFlagFailure, (state, { id, previousEnabled }) =>
  adapter.updateOne({ id, changes: { enabled: previousEnabled } }, state),
),

// Effect
toggleFlag$ = createEffect(() =>
  this.actions$.pipe(
    ofType(toggleFeatureFlag),
    mergeMap(({ id, enabled }) =>
      this.flagService.toggleFlag(id, enabled).pipe(
        map((flag) => toggleFeatureFlagSuccess({ flag })),
        catchError((error) =>
          of(toggleFeatureFlagFailure({
            id,
            previousEnabled: !enabled,
            error: error.message,
          })),
        ),
      ),
    ),
  ),
);
```

### 5.5.3 Undo Pattern

For delete operations with optimistic removal:

```typescript
// Effect with undo toast
deleteItem$ = createEffect(() =>
  this.actions$.pipe(
    ofType(deleteItem),
    mergeMap(({ id, item }) => {
      // Show undo toast
      const toastRef = this.toastService.info('Item deleted.', {
        action: 'Undo',
        duration: 5000,
      });

      return race(
        // User clicks Undo
        toastRef.actionClicked$.pipe(
          map(() => undoDeleteItem({ id, item })),
        ),
        // Toast dismissed (no undo) — proceed with API call
        toastRef.dismissed$.pipe(
          switchMap(() =>
            this.itemService.delete(id).pipe(
              map(() => deleteItemSuccess({ id })),
              catchError((error) =>
                of(deleteItemFailure({ id, item, error: error.message })),
              ),
            ),
          ),
        ),
      );
    }),
  ),
);
```

---

## 5.6 Pagination & Filtering

### 5.6.1 Pagination Model

```typescript
interface PaginationState {
  page: number;        // Current page (1-indexed)
  perPage: number;     // Items per page
  total: number;       // Total items matching current filters
  totalPages: number;  // Computed: ceil(total / perPage)
}

interface PaginatedRequest {
  page: number;
  perPage: number;
  sort?: string;        // Column key
  sortDirection?: 'asc' | 'desc';
  search?: string;
  filters?: Record<string, any>;
}
```

### 5.6.2 Server-Side Pagination Flow

```
1. User changes page → Component dispatches action with new page number
2. Effect sends GET request with page, perPage, sort, filters as query params
3. API returns paginated response with data[] and meta { page, perPage, total }
4. Reducer updates entity state with new data (replaces, not appends)
5. Reducer updates pagination state
6. Component re-renders table with new data and updated pagination controls
```

**URL Synchronization**:

Pagination, sorting, and filter state is synced to the URL query parameters so that:
- Bookmarking preserves the current view.
- Browser back/forward navigates through table states.
- Sharing a URL takes the recipient to the exact same view.

```typescript
// Route query params ↔ Store state synchronization
@Component({ ... })
export class LearnerListPageComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private store = inject(Store);

  ngOnInit(): void {
    // Read initial state from URL
    this.route.queryParams.pipe(take(1)).subscribe((params) => {
      this.store.dispatch(UserActions.loadLearners({
        page: +(params['page'] || 1),
        perPage: +(params['perPage'] || 25),
        sort: params['sort'] || 'joinDate',
        sortDirection: params['dir'] || 'desc',
        search: params['q'] || '',
        filters: this.parseFilters(params),
      }));
    });

    // Sync state changes back to URL
    this.store.select(selectLearnersQueryParams).pipe(
      skip(1), // Skip initial emission
      distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
    ).subscribe((params) => {
      this.router.navigate([], {
        queryParams: params,
        queryParamsHandling: 'merge',
        replaceUrl: true,
      });
    });
  }
}
```

### 5.6.3 Filtering Architecture

**Filter Configuration**:

```typescript
interface FilterConfig {
  key: string;                    // Query param key and state key
  label: string;                  // Display label
  type: 'select' | 'multi-select' | 'date-range' | 'text' | 'number-range';
  options?: { label: string; value: any }[];  // For select types
  defaultValue?: any;
}

// Example: Learner list filters
const learnerFilterConfig: FilterConfig[] = [
  {
    key: 'status',
    label: 'Status',
    type: 'multi-select',
    options: [
      { label: 'Active', value: 'active' },
      { label: 'Suspended', value: 'suspended' },
      { label: 'Banned', value: 'banned' },
    ],
  },
  {
    key: 'registeredAt',
    label: 'Registration Date',
    type: 'date-range',
  },
  {
    key: 'country',
    label: 'Country',
    type: 'select',
    options: [], // Dynamically loaded
  },
  {
    key: 'subscription',
    label: 'Subscription',
    type: 'multi-select',
    options: [
      { label: 'Free', value: 'free' },
      { label: 'Plus', value: 'plus' },
      { label: 'Family', value: 'family' },
    ],
  },
];
```

**Filter Application Flow**:

```
1. User changes a filter value
2. FilterPanelComponent emits filterChange event with the full filter state
3. Component dispatches action: UserActions.setFilters({ filters })
4. Reducer updates filters in state AND resets page to 1
5. Effect detects filter change and triggers a new API request
6. API returns filtered results
7. Reducer updates data and pagination
8. URL query params are updated
```

### 5.6.4 Debounced Search

```typescript
// SearchBarComponent
@Component({
  selector: 'app-search-bar',
  template: `
    <div class="search-bar" role="search">
      <mat-icon>search</mat-icon>
      <input
        type="text"
        [placeholder]="placeholder()"
        [value]="value()"
        (input)="onInput($event)"
        aria-label="{{ placeholder() }}" />
      @if (value()) {
        <button (click)="clear()" aria-label="Clear search">
          <mat-icon>close</mat-icon>
        </button>
      }
      @if (searching()) {
        <mat-spinner diameter="20"></mat-spinner>
      }
    </div>
  `,
})
export class SearchBarComponent {
  placeholder = input<string>('Search...');
  value = input<string>('');
  debounceMs = input<number>(300);
  minLength = input<number>(2);

  searchChange = output<string>();

  private inputSubject = new Subject<string>();

  constructor() {
    this.inputSubject.pipe(
      debounceTime(this.debounceMs()),
      distinctUntilChanged(),
      filter((term) => term.length === 0 || term.length >= this.minLength()),
    ).subscribe((term) => {
      this.searchChange.emit(term);
    });
  }

  onInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.inputSubject.next(value);
  }

  clear(): void {
    this.inputSubject.next('');
  }
}
```

### 5.6.5 Sorting

```
1. User clicks a column header
2. DataTableComponent emits sortChange event: { column: 'email', direction: 'asc' }
3. Component dispatches: UserActions.setSort({ sort: 'email', direction: 'asc' })
4. Reducer updates sort state (page stays the same)
5. Effect triggers API request with new sort params
6. Table header shows sort indicator arrow on the active column
```

**Sort state cycles**: `none → asc → desc → none`

---

## 5.7 Real-Time Updates

### 5.7.1 Polling Strategy

For data that changes frequently:

| Data | Polling Interval | Strategy |
|---|---|---|
| Dashboard metrics | 30 seconds | Full refresh |
| Moderation queue count | 15 seconds | Count-only endpoint |
| Notification count | 15 seconds | Count-only endpoint |
| Experiment results | 60 seconds | Full refresh (when viewing) |
| System health | 15 seconds | Lightweight health endpoint |

```typescript
// Dashboard polling effect
pollDashboardMetrics$ = createEffect(() =>
  this.actions$.pipe(
    ofType(DashboardActions.startPolling),
    switchMap(() =>
      interval(30_000).pipe(
        startWith(0),
        switchMap(() =>
          this.dashboardService.getMetrics().pipe(
            map((metrics) => DashboardActions.metricsUpdated({ metrics })),
            catchError(() => EMPTY), // Silently ignore polling errors
          ),
        ),
        takeUntil(this.actions$.pipe(ofType(DashboardActions.stopPolling))),
      ),
    ),
  ),
);
```

### 5.7.2 WebSocket Connection (Future Enhancement)

For true real-time updates (moderation queue, live analytics):

```typescript
@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket$ = webSocket<WebSocketMessage>({
    url: environment.wsUrl,
    openObserver: { next: () => console.log('WebSocket connected') },
    closeObserver: { next: () => console.log('WebSocket disconnected') },
  });

  subscribe(channel: string): Observable<any> {
    this.socket$.next({ action: 'subscribe', channel });
    return this.socket$.pipe(
      filter((msg) => msg.channel === channel),
      map((msg) => msg.payload),
      retry({ delay: 3000 }), // Auto-reconnect
    );
  }
}
```

---

## 5.8 State Synchronization

### 5.8.1 Cross-Feature State Dependencies

Some actions in one feature affect data in another:

| Action | Source Feature | Affected Features |
|---|---|---|
| Ban a user | Moderation | User list (status change), Dashboard (user count) |
| Publish a course | Course Management | Dashboard (active courses count), Analytics |
| Complete an experiment | Experiments | Feature Flags (winner promoted) |
| Approve translations | Localization | Course content (translated strings) |

**Implementation**: Use a shared action or an effect that dispatches to multiple features:

```typescript
// When a user is banned via moderation...
banUserSuccess$ = createEffect(() =>
  this.actions$.pipe(
    ofType(ModerationActions.banUserSuccess),
    mergeMap(({ userId }) => [
      // Update the user in the users feature
      UserActions.updateUserStatus({ userId, status: 'banned' }),
      // Refresh dashboard metrics
      DashboardActions.refreshMetrics(),
      // Add to activity feed
      DashboardActions.addActivityItem({
        item: { type: 'user_banned', userId, timestamp: Date.now() },
      }),
    ]),
  ),
);
```

### 5.8.2 Stale Data Detection

When navigating back to a list page:

```typescript
// Check if data is stale (loaded more than N seconds ago)
const STALE_THRESHOLD_MS = 60_000; // 1 minute

shouldRefresh$ = createEffect(() =>
  this.router.events.pipe(
    filter((event) => event instanceof NavigationEnd),
    filter((event) => event.url.startsWith('/users')),
    withLatestFrom(this.store.select(selectLearnersLastFetched)),
    filter(([, lastFetched]) => {
      if (!lastFetched) return true; // Never fetched
      return Date.now() - lastFetched > STALE_THRESHOLD_MS;
    }),
    map(() => UserActions.loadLearners({ /* current params */ })),
  ),
);
```

### 5.8.3 Conflict Resolution

When two admins edit the same resource concurrently:

```
1. Admin A loads Course #42 (version 5)
2. Admin B loads Course #42 (version 5)
3. Admin B saves changes → version 6
4. Admin A saves changes → API returns 409 Conflict
5. Frontend shows conflict dialog:
   "This course was modified by Admin B at 09:30.
    Your changes may conflict with theirs.
    [View Changes] [Overwrite] [Discard My Changes]"
6. "View Changes" shows a diff between Admin A's version and the server version
7. "Overwrite" sends the save with a force flag
8. "Discard" reloads the server version
```

Implementation: The API uses ETags or version numbers. The frontend sends `If-Match: <etag>` or includes `version` in the request body. A 409 response triggers the conflict resolution flow.

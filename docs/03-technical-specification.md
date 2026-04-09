# 3. Frontend Technical Specification

> Defines the architecture, tooling, patterns, and implementation details for the Admin Panel frontend built with Angular.

---

## 3.1 Framework Choice — Angular

### 3.1.1 Technology Stack

| Technology | Version | Purpose |
|---|---|---|
| **Angular** | 17+ | Core framework (standalone components, signals, control flow) |
| **TypeScript** | 5.3+ | Type-safe language |
| **NgRx** | 17+ | Global state management (store, effects, entity, component-store) |
| **Angular Material** | 17+ | Base UI component library |
| **Angular CDK** | 17+ | Low-level UI primitives (drag-drop, overlay, a11y) |
| **RxJS** | 7.8+ | Reactive programming |
| **ngx-charts** | 20+ | Chart visualizations |
| **ngx-translate** | 15+ | Admin panel i18n |
| **Angular Router** | 17+ | Routing with lazy loading |
| **date-fns** | 3+ | Date manipulation |

### 3.1.2 Build & Tooling

| Tool | Purpose |
|---|---|
| **Angular CLI** | Scaffolding, building, serving |
| **esbuild** | Build bundler (Angular 17+ default) |
| **ESLint** | Linting with `@angular-eslint` |
| **Prettier** | Code formatting |
| **Husky + lint-staged** | Pre-commit hooks |
| **Karma + Jasmine** | Unit testing |
| **Cypress** | End-to-end testing |
| **Storybook** | Component development & documentation |
| **Compodoc** | API documentation generation |

### 3.1.3 Rationale for Angular

- **Enterprise-grade**: Strong opinions on architecture reduce decision fatigue for large teams.
- **Built-in DI**: Dependency injection is first-class, enabling testable and modular services.
- **Reactive Forms**: Powerful form handling with validation, essential for the admin panel's many forms.
- **Lazy Loading**: Built-in route-based code splitting for optimal load performance.
- **Angular Material**: Battle-tested component library with accessibility baked in.
- **Standalone Components**: Modern Angular (17+) eliminates NgModules overhead while maintaining structure.
- **Signals**: Fine-grained reactivity for optimal change detection.

---

## 3.2 Component Architecture

### 3.2.1 Project Structure

```
src/
├── app/
│   ├── core/                          # Singleton services, guards, interceptors
│   │   ├── auth/
│   │   │   ├── auth.service.ts
│   │   │   ├── auth.guard.ts
│   │   │   ├── auth.interceptor.ts
│   │   │   ├── mfa.service.ts
│   │   │   └── token.service.ts
│   │   ├── api/
│   │   │   ├── api.service.ts         # Base HTTP service
│   │   │   ├── api-error.interceptor.ts
│   │   │   └── api-cache.interceptor.ts
│   │   ├── guards/
│   │   │   ├── role.guard.ts
│   │   │   └── unsaved-changes.guard.ts
│   │   └── services/
│   │       ├── notification.service.ts
│   │       ├── toast.service.ts
│   │       ├── theme.service.ts
│   │       └── global-search.service.ts
│   │
│   ├── shared/                        # Reusable components, directives, pipes
│   │   ├── components/
│   │   │   ├── data-table/
│   │   │   ├── search-bar/
│   │   │   ├── filter-panel/
│   │   │   ├── metric-card/
│   │   │   ├── status-badge/
│   │   │   ├── confirm-dialog/
│   │   │   ├── empty-state/
│   │   │   ├── error-state/
│   │   │   ├── loading-spinner/
│   │   │   ├── skeleton-loader/
│   │   │   ├── toast/
│   │   │   ├── breadcrumb/
│   │   │   ├── file-upload/
│   │   │   ├── rich-text-editor/
│   │   │   ├── tag-input/
│   │   │   └── date-range-picker/
│   │   ├── directives/
│   │   │   ├── permission.directive.ts    # *appHasPermission="'courses.edit'"
│   │   │   ├── debounce-click.directive.ts
│   │   │   ├── auto-focus.directive.ts
│   │   │   └── tooltip.directive.ts
│   │   ├── pipes/
│   │   │   ├── time-ago.pipe.ts
│   │   │   ├── truncate.pipe.ts
│   │   │   ├── file-size.pipe.ts
│   │   │   └── highlight.pipe.ts
│   │   └── models/
│   │       ├── user.model.ts
│   │       ├── course.model.ts
│   │       ├── lesson.model.ts
│   │       ├── exercise.model.ts
│   │       ├── pagination.model.ts
│   │       ├── api-response.model.ts
│   │       └── role.model.ts
│   │
│   ├── features/                      # Feature modules (lazy loaded)
│   │   ├── dashboard/
│   │   │   ├── dashboard.routes.ts
│   │   │   ├── pages/
│   │   │   │   └── dashboard-page/
│   │   │   ├── components/
│   │   │   │   ├── metric-card/
│   │   │   │   ├── user-growth-chart/
│   │   │   │   ├── quick-actions/
│   │   │   │   └── activity-feed/
│   │   │   ├── services/
│   │   │   │   └── dashboard.service.ts
│   │   │   └── store/
│   │   │       ├── dashboard.actions.ts
│   │   │       ├── dashboard.reducer.ts
│   │   │       ├── dashboard.effects.ts
│   │   │       └── dashboard.selectors.ts
│   │   │
│   │   ├── users/
│   │   │   ├── users.routes.ts
│   │   │   ├── pages/
│   │   │   │   ├── learner-list-page/
│   │   │   │   ├── learner-detail-page/
│   │   │   │   ├── admin-list-page/
│   │   │   │   └── roles-page/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── store/
│   │   │
│   │   ├── courses/
│   │   │   ├── courses.routes.ts
│   │   │   ├── pages/
│   │   │   │   ├── course-list-page/
│   │   │   │   ├── course-builder-page/
│   │   │   │   └── skill-tree-page/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── store/
│   │   │
│   │   ├── lessons/
│   │   │   ├── lessons.routes.ts
│   │   │   ├── pages/
│   │   │   │   ├── lesson-list-page/
│   │   │   │   ├── lesson-editor-page/
│   │   │   │   └── media-library-page/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── store/
│   │   │
│   │   ├── moderation/
│   │   │   ├── moderation.routes.ts
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── store/
│   │   │
│   │   ├── analytics/
│   │   │   ├── analytics.routes.ts
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── store/
│   │   │
│   │   ├── localization/
│   │   │   ├── localization.routes.ts
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── store/
│   │   │
│   │   ├── experiments/
│   │   │   ├── experiments.routes.ts
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── store/
│   │   │
│   │   └── settings/
│   │       ├── settings.routes.ts
│   │       ├── pages/
│   │       ├── components/
│   │       ├── services/
│   │       └── store/
│   │
│   ├── layout/                        # Shell layout components
│   │   ├── admin-layout/
│   │   │   └── admin-layout.component.ts
│   │   ├── auth-layout/
│   │   │   └── auth-layout.component.ts
│   │   ├── sidebar/
│   │   │   └── sidebar.component.ts
│   │   └── top-bar/
│   │       └── top-bar.component.ts
│   │
│   ├── app.component.ts
│   ├── app.config.ts
│   └── app.routes.ts
│
├── assets/
│   ├── icons/
│   ├── images/
│   └── i18n/
│       ├── en.json
│       └── ...
│
├── environments/
│   ├── environment.ts
│   ├── environment.development.ts
│   └── environment.staging.ts
│
├── styles/
│   ├── _variables.scss
│   ├── _mixins.scss
│   ├── _typography.scss
│   ├── _reset.scss
│   ├── _animations.scss
│   └── styles.scss
│
└── index.html
```

### 3.2.2 Component Conventions

**Standalone Components** (Angular 17+ pattern):

```typescript
// Example: MetricCardComponent
@Component({
  selector: 'app-metric-card',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule],
  templateUrl: './metric-card.component.html',
  styleUrl: './metric-card.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MetricCardComponent {
  // Input signals (Angular 17+)
  title = input.required<string>();
  value = input.required<string | number>();
  trend = input<'up' | 'down' | 'neutral'>('neutral');
  trendValue = input<string>('');
  icon = input<string>('');
  loading = input<boolean>(false);

  // Computed signals
  trendClass = computed(() => {
    const map = { up: 'trend-positive', down: 'trend-negative', neutral: 'trend-neutral' };
    return map[this.trend()];
  });
}
```

**Naming Conventions**:

| Element | Convention | Example |
|---|---|---|
| Component file | `kebab-case.component.ts` | `metric-card.component.ts` |
| Component class | `PascalCase + Component` | `MetricCardComponent` |
| Component selector | `app-kebab-case` | `app-metric-card` |
| Service file | `kebab-case.service.ts` | `dashboard.service.ts` |
| Service class | `PascalCase + Service` | `DashboardService` |
| Guard file | `kebab-case.guard.ts` | `role.guard.ts` |
| Pipe file | `kebab-case.pipe.ts` | `time-ago.pipe.ts` |
| Directive file | `kebab-case.directive.ts` | `permission.directive.ts` |
| Model file | `kebab-case.model.ts` | `user.model.ts` |
| Interface prefix | `I` (optional, team preference) | `IUser` or `User` |
| Enum | `PascalCase` | `UserStatus`, `ExerciseType` |

### 3.2.3 Smart vs. Presentational Components

| Type | Responsibility | State | Side Effects | Testing |
|---|---|---|---|---|
| **Smart (Container)** | Orchestrates data flow. Connects to store/services. Lives in `pages/`. | Accesses NgRx store via selectors. Dispatches actions. | Triggers API calls via effects. | Integration tests with store mocks. |
| **Presentational (Dumb)** | Renders UI based on inputs. Emits events. Lives in `components/` or `shared/`. | Stateless or local state only. | None. | Shallow unit tests. |

---

## 3.3 State Management Strategy

### 3.3.1 NgRx Global Store

The global NgRx store manages state that is shared across features or needs to survive navigation:

```
AppState
├── auth: AuthState
│   ├── user: AdminUser | null
│   ├── token: string | null
│   ├── permissions: Permission[]
│   ├── isAuthenticated: boolean
│   └── mfaRequired: boolean
│
├── notifications: NotificationState
│   ├── items: Notification[]
│   ├── unreadCount: number
│   └── loading: boolean
│
├── ui: UIState
│   ├── sidebarCollapsed: boolean
│   ├── theme: 'light' | 'dark'
│   └── globalSearchOpen: boolean
│
├── dashboard: DashboardState
│   ├── metrics: DashboardMetrics | null
│   ├── activityFeed: ActivityItem[]
│   ├── loading: boolean
│   └── error: string | null
│
├── users: UsersState
│   ├── learners: EntityState<Learner>
│   ├── admins: EntityState<AdminUser>
│   ├── selectedUser: User | null
│   ├── pagination: PaginationState
│   ├── filters: UserFilters
│   ├── loading: boolean
│   └── error: string | null
│
├── courses: CoursesState
│   ├── courses: EntityState<Course>
│   ├── selectedCourse: Course | null
│   ├── pagination: PaginationState
│   ├── filters: CourseFilters
│   ├── loading: boolean
│   └── error: string | null
│
├── lessons: LessonsState
│   ├── lessons: EntityState<Lesson>
│   ├── selectedLesson: Lesson | null
│   ├── exercises: Exercise[]
│   ├── loading: boolean
│   └── error: string | null
│
├── moderation: ModerationState
│   ├── flaggedItems: EntityState<FlaggedItem>
│   ├── reports: EntityState<UserReport>
│   ├── sanctions: EntityState<Sanction>
│   ├── loading: boolean
│   └── error: string | null
│
├── analytics: AnalyticsState
│   ├── overview: AnalyticsOverview | null
│   ├── dateRange: DateRange
│   ├── loading: boolean
│   └── error: string | null
│
├── localization: LocalizationState
│   ├── languages: Language[]
│   ├── translationQueue: EntityState<TranslationItem>
│   ├── glossary: EntityState<GlossaryEntry>
│   ├── loading: boolean
│   └── error: string | null
│
├── experiments: ExperimentsState
│   ├── experiments: EntityState<Experiment>
│   ├── featureFlags: EntityState<FeatureFlag>
│   ├── loading: boolean
│   └── error: string | null
│
└── settings: SettingsState
    ├── auditLogs: EntityState<AuditLogEntry>
    ├── apiKeys: ApiKey[]
    ├── systemConfig: SystemConfig | null
    ├── loading: boolean
    └── error: string | null
```

### 3.3.2 NgRx Component Store (Local State)

For complex components with local state that doesn't need to be global:

```typescript
// Example: CourseBuilderComponentStore
@Injectable()
export class CourseBuilderStore extends ComponentStore<CourseBuilderState> {
  constructor(private courseService: CourseService) {
    super({
      metadata: null,
      skillTree: [],
      isDirty: false,
      activeTab: 'metadata',
      saving: false,
      validationErrors: {},
    });
  }

  // Selectors
  readonly metadata$ = this.select(state => state.metadata);
  readonly skillTree$ = this.select(state => state.skillTree);
  readonly isDirty$ = this.select(state => state.isDirty);
  readonly activeTab$ = this.select(state => state.activeTab);

  // Updaters
  readonly updateMetadata = this.updater((state, metadata: Partial<CourseMetadata>) => ({
    ...state,
    metadata: { ...state.metadata, ...metadata },
    isDirty: true,
  }));

  // Effects
  readonly saveCourse = this.effect((trigger$) =>
    trigger$.pipe(
      tap(() => this.patchState({ saving: true })),
      withLatestFrom(this.state$),
      switchMap(([, state]) =>
        this.courseService.saveCourse(state.metadata).pipe(
          tapResponse(
            (course) => this.patchState({ saving: false, isDirty: false }),
            (error) => this.patchState({ saving: false }),
          ),
        ),
      ),
    ),
  );
}
```

### 3.3.3 When to Use Each State Management Approach

| Scenario | Approach |
|---|---|
| User authentication state | NgRx Global Store |
| UI preferences (theme, sidebar) | NgRx Global Store |
| Data shared between routes (user list, course list) | NgRx Global Store + Entity Adapter |
| Complex form state (course builder, lesson editor) | NgRx Component Store |
| Simple local UI state (dropdown open, hover) | Angular Signals (`signal()`) |
| Derived values from state | `computed()` or NgRx selectors |
| One-off API calls (no caching needed) | Service + `async` pipe directly |

---

## 3.4 API Integration Strategy

### 3.4.1 Base API Service

```typescript
@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = inject(ENVIRONMENT).apiBaseUrl;
  private readonly http = inject(HttpClient);

  get<T>(path: string, params?: HttpParams): Observable<ApiResponse<T>> {
    return this.http.get<ApiResponse<T>>(`${this.baseUrl}${path}`, { params });
  }

  post<T>(path: string, body: unknown): Observable<ApiResponse<T>> {
    return this.http.post<ApiResponse<T>>(`${this.baseUrl}${path}`, body);
  }

  put<T>(path: string, body: unknown): Observable<ApiResponse<T>> {
    return this.http.put<ApiResponse<T>>(`${this.baseUrl}${path}`, body);
  }

  patch<T>(path: string, body: unknown): Observable<ApiResponse<T>> {
    return this.http.patch<ApiResponse<T>>(`${this.baseUrl}${path}`, body);
  }

  delete<T>(path: string): Observable<ApiResponse<T>> {
    return this.http.delete<ApiResponse<T>>(`${this.baseUrl}${path}`);
  }
}
```

### 3.4.2 Standard API Response Wrapper

```typescript
interface ApiResponse<T> {
  data: T;
  meta?: {
    page: number;
    perPage: number;
    total: number;
    totalPages: number;
  };
  errors?: ApiError[];
}

interface ApiError {
  code: string;
  message: string;
  field?: string;
  details?: Record<string, unknown>;
}
```

### 3.4.3 HTTP Interceptors

**Authentication Interceptor**:

```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const tokenService = inject(TokenService);
  const token = tokenService.getAccessToken();

  if (token) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        // Token expired — attempt refresh
        return tokenService.refreshToken().pipe(
          switchMap((newToken) => {
            req = req.clone({
              setHeaders: { Authorization: `Bearer ${newToken}` },
            });
            return next(req);
          }),
          catchError(() => {
            // Refresh failed — redirect to login
            tokenService.clearTokens();
            inject(Router).navigate(['/login']);
            return throwError(() => error);
          }),
        );
      }
      return throwError(() => error);
    }),
  );
};
```

**Error Interceptor**:

```typescript
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const toastService = inject(ToastService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      switch (error.status) {
        case 0:
          toastService.error('Network error. Please check your connection.');
          break;
        case 403:
          toastService.error('You do not have permission to perform this action.');
          break;
        case 429:
          toastService.warning('Too many requests. Please wait a moment.');
          break;
        case 500:
          toastService.error('An internal server error occurred. Please try again.');
          break;
      }
      return throwError(() => error);
    }),
  );
};
```

**Cache Interceptor**:

```typescript
export const cacheInterceptor: HttpInterceptorFn = (req, next) => {
  const cacheService = inject(HttpCacheService);

  // Only cache GET requests marked as cacheable
  if (req.method !== 'GET' || !req.headers.has('X-Cache')) {
    return next(req);
  }

  const ttl = parseInt(req.headers.get('X-Cache-TTL') || '300', 10); // default 5min
  const cached = cacheService.get(req.urlWithParams);

  if (cached) {
    return of(cached);
  }

  return next(req).pipe(
    tap((event) => {
      if (event instanceof HttpResponse) {
        cacheService.set(req.urlWithParams, event, ttl);
      }
    }),
  );
};
```

---

## 3.5 Caching Strategy

### 3.5.1 Multi-Layer Caching

| Layer | Implementation | TTL | Invalidation |
|---|---|---|---|
| **HTTP Cache** | `HttpCacheService` (in-memory map) | 30s–5min depending on endpoint | On mutation (POST/PUT/DELETE) to the same resource |
| **NgRx Store** | Entity state in NgRx | Until explicitly refreshed | On re-fetch, logout, or state reset |
| **LocalStorage** | Theme, sidebar state, last-used filters | Persistent | On logout or explicit clear |
| **SessionStorage** | Tokens, session metadata | Session lifetime | On logout |

### 3.5.2 Cache Invalidation Rules

| Trigger | Action |
|---|---|
| User creates/updates/deletes a resource | Invalidate the list cache for that resource type |
| User navigates back to a list page | Check if cache is stale (> TTL). Refresh in background if stale. |
| User pulls-to-refresh or clicks Refresh | Force re-fetch, ignoring cache |
| User logs out | Clear all caches (memory, localStorage, sessionStorage) |
| Token refresh | Clear auth-related caches only |

### 3.5.3 Stale-While-Revalidate Pattern

For list pages (users, courses, lessons), the UI uses a stale-while-revalidate pattern:

1. Show cached data immediately (if available).
2. Fetch fresh data from the API in the background.
3. Update the UI once the fresh data arrives.
4. Show a subtle "Updated just now" indicator if the data changed.

---

## 3.6 Form Handling

### 3.6.1 Reactive Forms Strategy

All forms use Angular Reactive Forms for:

- Type-safe form models
- Declarative validation
- Dynamic form generation (exercise editor)
- Cross-field validation
- Easy unit testing

**Example: Course Metadata Form**:

```typescript
@Component({ ... })
export class CourseMetadataFormComponent implements OnInit {
  private fb = inject(FormBuilder);

  courseForm = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(100)]],
    description: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(2000)]],
    sourceLanguage: ['', Validators.required],
    targetLanguage: ['', Validators.required],
    difficulty: ['', Validators.required],
    thumbnail: [null as File | null],
    tags: [[] as string[]],
    estimatedDuration: [null as number | null, [Validators.min(0.5), Validators.max(500)]],
    prerequisites: [[] as string[]],
  }, {
    validators: [differentLanguagesValidator],
  });
}

// Cross-field validator
function differentLanguagesValidator(group: AbstractControl): ValidationErrors | null {
  const source = group.get('sourceLanguage')?.value;
  const target = group.get('targetLanguage')?.value;
  return source && target && source === target
    ? { sameLanguage: true }
    : null;
}
```

### 3.6.2 Dynamic Exercise Forms

The lesson editor uses a form factory pattern:

```typescript
@Injectable({ providedIn: 'root' })
export class ExerciseFormFactory {
  private fb = inject(FormBuilder);

  createForm(type: ExerciseType): FormGroup {
    const baseFields = {
      type: [type, Validators.required],
      order: [0, Validators.required],
    };

    switch (type) {
      case ExerciseType.Translation:
        return this.fb.group({
          ...baseFields,
          prompt: ['', [Validators.required, Validators.maxLength(500)]],
          correctAnswer: ['', [Validators.required, Validators.maxLength(500)]],
          alternatives: this.fb.array([]),
        });
      case ExerciseType.MultipleChoice:
        return this.fb.group({
          ...baseFields,
          prompt: ['', Validators.required],
          options: this.fb.array([], [Validators.minLength(2), Validators.maxLength(6)]),
          correctOptionIndex: [null, Validators.required],
        });
      // ... other types
    }
  }
}
```

### 3.6.3 Form State Persistence

- **Unsaved changes detection**: A `CanDeactivate` guard checks for dirty forms and prompts the user.
- **Auto-save drafts**: Complex forms (course builder, lesson editor) auto-save to `localStorage` every 30 seconds.
- **Form restoration**: On page load, check `localStorage` for saved drafts and offer to restore.

```typescript
@Injectable()
export class FormPersistenceService {
  save(key: string, value: unknown): void {
    localStorage.setItem(`form_draft_${key}`, JSON.stringify({
      data: value,
      savedAt: Date.now(),
    }));
  }

  restore<T>(key: string, maxAgeMs = 24 * 60 * 60 * 1000): T | null {
    const raw = localStorage.getItem(`form_draft_${key}`);
    if (!raw) return null;

    const { data, savedAt } = JSON.parse(raw);
    if (Date.now() - savedAt > maxAgeMs) {
      this.clear(key);
      return null;
    }
    return data as T;
  }

  clear(key: string): void {
    localStorage.removeItem(`form_draft_${key}`);
  }
}
```

---

## 3.7 Routing Structure

### 3.7.1 Route Configuration

```typescript
// app.routes.ts
export const appRoutes: Routes = [
  {
    path: '',
    component: AuthLayoutComponent,
    children: [
      { path: 'login', loadComponent: () => import('./features/auth/login-page.component') },
      { path: 'mfa', loadComponent: () => import('./features/auth/mfa-page.component') },
      { path: 'forgot-password', loadComponent: () => import('./features/auth/forgot-password-page.component') },
    ],
  },
  {
    path: '',
    component: AdminLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadChildren: () => import('./features/dashboard/dashboard.routes'),
      },
      {
        path: 'users',
        loadChildren: () => import('./features/users/users.routes'),
        canActivate: [roleGuard],
        data: { permissions: ['users.view'] },
      },
      {
        path: 'courses',
        loadChildren: () => import('./features/courses/courses.routes'),
        canActivate: [roleGuard],
        data: { permissions: ['courses.view'] },
      },
      {
        path: 'lessons',
        loadChildren: () => import('./features/lessons/lessons.routes'),
        canActivate: [roleGuard],
        data: { permissions: ['lessons.view'] },
      },
      {
        path: 'moderation',
        loadChildren: () => import('./features/moderation/moderation.routes'),
        canActivate: [roleGuard],
        data: { permissions: ['moderation.view'] },
      },
      {
        path: 'analytics',
        loadChildren: () => import('./features/analytics/analytics.routes'),
        canActivate: [roleGuard],
        data: { permissions: ['analytics.view'] },
      },
      {
        path: 'localization',
        loadChildren: () => import('./features/localization/localization.routes'),
        canActivate: [roleGuard],
        data: { permissions: ['localization.view'] },
      },
      {
        path: 'experiments',
        loadChildren: () => import('./features/experiments/experiments.routes'),
        canActivate: [roleGuard],
        data: { permissions: ['experiments.view'] },
      },
      {
        path: 'settings',
        loadChildren: () => import('./features/settings/settings.routes'),
        canActivate: [roleGuard],
        data: { permissions: ['settings.view'] },
      },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
```

### 3.7.2 Feature Routes Example

```typescript
// features/users/users.routes.ts
export default [
  { path: '', redirectTo: 'learners', pathMatch: 'full' },
  {
    path: 'learners',
    loadComponent: () => import('./pages/learner-list-page/learner-list-page.component'),
  },
  {
    path: 'learners/:id',
    loadComponent: () => import('./pages/learner-detail-page/learner-detail-page.component'),
  },
  {
    path: 'admins',
    loadComponent: () => import('./pages/admin-list-page/admin-list-page.component'),
    canActivate: [roleGuard],
    data: { permissions: ['admins.view'] },
  },
  {
    path: 'roles',
    loadComponent: () => import('./pages/roles-page/roles-page.component'),
    canActivate: [roleGuard],
    data: { permissions: ['roles.view'] },
  },
] as Routes;
```

### 3.7.3 Route Guards

| Guard | Purpose | Applied To |
|---|---|---|
| `authGuard` | Redirects to `/login` if not authenticated | All admin routes |
| `roleGuard` | Checks `data.permissions` against user roles. Shows 403 page if unauthorized. | Feature routes |
| `unsavedChangesGuard` | Prompts user if leaving a page with unsaved form changes | Edit pages (course builder, lesson editor) |
| `mfaGuard` | Redirects to `/mfa` if MFA is required but not completed | Post-login routes |

---

## 3.8 Authentication & Session Handling

### 3.8.1 Authentication Flow

```
1. User visits /login
2. User enters email + password → POST /api/auth/login
3. Server returns { accessToken, refreshToken, mfaRequired }
4. If mfaRequired:
   a. Redirect to /mfa
   b. User enters TOTP code → POST /api/auth/mfa/verify
   c. Server returns { accessToken, refreshToken }
5. Store tokens:
   - accessToken → in-memory (not localStorage for XSS protection)
   - refreshToken → HttpOnly secure cookie (set by server)
6. Redirect to /dashboard
7. All API requests include Authorization: Bearer <accessToken>
```

### 3.8.2 Token Management

```typescript
@Injectable({ providedIn: 'root' })
export class TokenService {
  private accessToken: string | null = null;
  private refreshPromise: Promise<string> | null = null;

  setAccessToken(token: string): void {
    this.accessToken = token;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  clearTokens(): void {
    this.accessToken = null;
    // Server-side: clear HttpOnly refreshToken cookie via API call
  }

  async refreshToken(): Promise<string> {
    // Deduplicate concurrent refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = firstValueFrom(
      this.http.post<{ accessToken: string }>('/api/auth/refresh', {}).pipe(
        tap(({ accessToken }) => {
          this.accessToken = accessToken;
          this.refreshPromise = null;
        }),
        map(({ accessToken }) => accessToken),
        catchError((err) => {
          this.refreshPromise = null;
          this.clearTokens();
          throw err;
        }),
      ),
    );

    return this.refreshPromise;
  }
}
```

### 3.8.3 Session Timeout

- **Access token TTL**: 15 minutes.
- **Refresh token TTL**: 7 days (sliding window — extends on use).
- **Idle timeout**: 30 minutes of inactivity. A warning modal appears at 25 minutes: "Your session will expire in 5 minutes. [Extend Session]".
- **Absolute timeout**: 12 hours from login. Requires re-authentication.
- **Activity detection**: Mouse movements, keyboard input, and API calls reset the idle timer.

### 3.8.4 Logout Flow

```
1. User clicks "Log Out" or session expires
2. POST /api/auth/logout (invalidates refresh token server-side)
3. Clear access token from memory
4. Clear all application state (NgRx store reset)
5. Clear localStorage drafts (optional: keep theme preference)
6. Redirect to /login
```

---

## 3.9 Role-Based Access Control (RBAC)

### 3.9.1 Permission System

Permissions are structured as `resource.action`:

```typescript
enum Permission {
  // Dashboard
  DashboardView = 'dashboard.view',

  // Users
  UsersView = 'users.view',
  UsersEdit = 'users.edit',
  UsersSuspend = 'users.suspend',
  UsersBan = 'users.ban',
  UsersDelete = 'users.delete',
  UsersExport = 'users.export',

  // Admin Users
  AdminsView = 'admins.view',
  AdminsCreate = 'admins.create',
  AdminsEdit = 'admins.edit',
  AdminsDeactivate = 'admins.deactivate',

  // Roles
  RolesView = 'roles.view',
  RolesEdit = 'roles.edit',
  RolesCreate = 'roles.create',

  // Courses
  CoursesView = 'courses.view',
  CoursesCreate = 'courses.create',
  CoursesEdit = 'courses.edit',
  CoursesPublish = 'courses.publish',
  CoursesDelete = 'courses.delete',

  // Lessons
  LessonsView = 'lessons.view',
  LessonsCreate = 'lessons.create',
  LessonsEdit = 'lessons.edit',
  LessonsDelete = 'lessons.delete',

  // Moderation
  ModerationView = 'moderation.view',
  ModerationAction = 'moderation.action',
  ModerationEscalate = 'moderation.escalate',

  // Analytics
  AnalyticsView = 'analytics.view',
  AnalyticsExport = 'analytics.export',
  AnalyticsCustomReports = 'analytics.custom_reports',

  // Localization
  LocalizationView = 'localization.view',
  LocalizationEdit = 'localization.edit',
  LocalizationPublish = 'localization.publish',

  // Experiments
  ExperimentsView = 'experiments.view',
  ExperimentsCreate = 'experiments.create',
  ExperimentsEdit = 'experiments.edit',
  ExperimentsComplete = 'experiments.complete',

  // Feature Flags
  FlagsView = 'flags.view',
  FlagsCreate = 'flags.create',
  FlagsEdit = 'flags.edit',
  FlagsEmergencyDisable = 'flags.emergency_disable',

  // Settings
  SettingsView = 'settings.view',
  SettingsEdit = 'settings.edit',
  AuditLogsView = 'audit_logs.view',
  AuditLogsExport = 'audit_logs.export',
}
```

### 3.9.2 Permission Directive

```typescript
@Directive({
  selector: '[appHasPermission]',
  standalone: true,
})
export class HasPermissionDirective implements OnInit, OnDestroy {
  private appHasPermission = input.required<string | string[]>();
  private appHasPermissionOp = input<'AND' | 'OR'>('AND');

  private store = inject(Store);
  private templateRef = inject(TemplateRef<unknown>);
  private viewContainer = inject(ViewContainerRef);
  private subscription?: Subscription;
  private hasView = false;

  ngOnInit(): void {
    this.subscription = this.store
      .select(selectUserPermissions)
      .subscribe((permissions) => {
        const required = Array.isArray(this.appHasPermission())
          ? this.appHasPermission() as string[]
          : [this.appHasPermission() as string];
        const op = this.appHasPermissionOp();

        const hasPermission = op === 'AND'
          ? required.every((p) => permissions.includes(p))
          : required.some((p) => permissions.includes(p));

        if (hasPermission && !this.hasView) {
          this.viewContainer.createEmbeddedView(this.templateRef);
          this.hasView = true;
        } else if (!hasPermission && this.hasView) {
          this.viewContainer.clear();
          this.hasView = false;
        }
      });
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }
}
```

**Usage in templates**:

```html
<!-- Single permission -->
<button *appHasPermission="'courses.publish'">Publish Course</button>

<!-- Multiple permissions (AND) -->
<section *appHasPermission="['users.view', 'users.edit']">
  Edit User Section
</section>

<!-- Multiple permissions (OR) -->
<button *appHasPermission="['courses.edit', 'courses.publish']"
        [appHasPermissionOp]="'OR'">
  Manage Course
</button>
```

### 3.9.3 Permission Service

```typescript
@Injectable({ providedIn: 'root' })
export class PermissionService {
  private store = inject(Store);

  hasPermission(permission: string): Observable<boolean> {
    return this.store.select(selectUserPermissions).pipe(
      map((permissions) => permissions.includes(permission)),
    );
  }

  hasAnyPermission(permissions: string[]): Observable<boolean> {
    return this.store.select(selectUserPermissions).pipe(
      map((userPermissions) =>
        permissions.some((p) => userPermissions.includes(p)),
      ),
    );
  }

  hasAllPermissions(permissions: string[]): Observable<boolean> {
    return this.store.select(selectUserPermissions).pipe(
      map((userPermissions) =>
        permissions.every((p) => userPermissions.includes(p)),
      ),
    );
  }
}
```

### 3.9.4 Server-Side RBAC Enforcement

- **Frontend RBAC is for UX only** — it hides UI elements but does not secure data.
- **All permissions are enforced server-side**. The API returns 403 if the user lacks the required permission.
- The frontend permission set is loaded at login and refreshed on token refresh.
- If the API returns 403, the error interceptor shows an "Access Denied" message and optionally redirects.

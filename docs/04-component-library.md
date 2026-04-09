# 4. Component Library Documentation

> Defines every reusable UI component in the Admin Panel, including design tokens, props, events, and usage examples.

---

## 4.1 Design Tokens & Theming

### 4.1.1 Color Tokens

```scss
// _variables.scss

// Brand Colors
$color-primary: #58CC02;          // Duolingo green
$color-primary-hover: #46A302;
$color-primary-active: #3B8A02;
$color-primary-light: #D7FFB8;

// Semantic Colors
$color-success: #10B981;
$color-warning: #F59E0B;
$color-error: #DC2626;
$color-info: #3B82F6;

// Neutral Colors
$color-gray-50: #F9FAFB;
$color-gray-100: #F3F4F6;
$color-gray-200: #E5E7EB;
$color-gray-300: #D1D5DB;
$color-gray-400: #9CA3AF;
$color-gray-500: #6B7280;
$color-gray-600: #4B5563;
$color-gray-700: #374151;
$color-gray-800: #1F2937;
$color-gray-900: #111827;

// Surface Colors (theme-aware via CSS custom properties)
--color-bg-primary: #{$color-gray-50};       // Light theme
--color-bg-secondary: #FFFFFF;
--color-bg-tertiary: #{$color-gray-100};
--color-text-primary: #{$color-gray-900};
--color-text-secondary: #{$color-gray-500};
--color-border: #{$color-gray-200};
```

### 4.1.2 Typography Tokens

```scss
// Font Family
$font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
$font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;

// Font Sizes
$font-size-xs: 0.75rem;    // 12px
$font-size-sm: 0.875rem;   // 14px
$font-size-base: 1rem;     // 16px
$font-size-lg: 1.125rem;   // 18px
$font-size-xl: 1.25rem;    // 20px
$font-size-2xl: 1.5rem;    // 24px
$font-size-3xl: 1.875rem;  // 30px
$font-size-4xl: 2.25rem;   // 36px

// Font Weights
$font-weight-regular: 400;
$font-weight-medium: 500;
$font-weight-semibold: 600;
$font-weight-bold: 700;

// Line Heights
$line-height-tight: 1.25;
$line-height-normal: 1.5;
$line-height-relaxed: 1.75;
```

### 4.1.3 Spacing Tokens

```scss
$space-0: 0;
$space-1: 0.25rem;   // 4px
$space-2: 0.5rem;    // 8px
$space-3: 0.75rem;   // 12px
$space-4: 1rem;      // 16px
$space-5: 1.25rem;   // 20px
$space-6: 1.5rem;    // 24px
$space-8: 2rem;      // 32px
$space-10: 2.5rem;   // 40px
$space-12: 3rem;     // 48px
$space-16: 4rem;     // 64px
```

### 4.1.4 Shadow Tokens

```scss
$shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
$shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
$shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
$shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

### 4.1.5 Border Radius Tokens

```scss
$radius-sm: 0.25rem;   // 4px
$radius-md: 0.375rem;  // 6px
$radius-lg: 0.5rem;    // 8px
$radius-xl: 0.75rem;   // 12px
$radius-2xl: 1rem;     // 16px
$radius-full: 9999px;  // Pill shape
```

### 4.1.6 Breakpoint Tokens

```scss
$breakpoint-sm: 640px;
$breakpoint-md: 768px;
$breakpoint-lg: 1024px;
$breakpoint-xl: 1280px;
$breakpoint-2xl: 1440px;
```

### 4.1.7 Z-Index Scale

```scss
$z-index-dropdown: 100;
$z-index-sticky: 200;
$z-index-fixed: 300;
$z-index-drawer: 400;
$z-index-modal-backdrop: 500;
$z-index-modal: 600;
$z-index-toast: 700;
$z-index-tooltip: 800;
```

---

## 4.2 Buttons

### 4.2.1 Button Component

**Selector**: `app-button`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `variant` | `'primary' \| 'secondary' \| 'outline' \| 'ghost' \| 'danger'` | `'primary'` | Visual style |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Button size |
| `disabled` | `boolean` | `false` | Disabled state |
| `loading` | `boolean` | `false` | Shows spinner and disables button |
| `icon` | `string` | `''` | Material icon name (left icon) |
| `iconPosition` | `'left' \| 'right'` | `'left'` | Icon placement |
| `fullWidth` | `boolean` | `false` | Stretches to container width |
| `type` | `'button' \| 'submit' \| 'reset'` | `'button'` | HTML button type |

**Events**:

| Output | Payload | Description |
|---|---|---|
| `clicked` | `MouseEvent` | Emitted on click (not emitted when disabled or loading) |

**Size Specifications**:

| Size | Height | Padding | Font Size | Icon Size |
|---|---|---|---|---|
| `sm` | 32px | 8px 12px | 14px | 16px |
| `md` | 40px | 10px 16px | 14px | 20px |
| `lg` | 48px | 12px 24px | 16px | 24px |

**Visual Variants**:

| Variant | Background | Text | Border | Hover |
|---|---|---|---|---|
| `primary` | `$color-primary` | `#FFFFFF` | none | `$color-primary-hover` |
| `secondary` | `$color-gray-100` | `$color-gray-700` | none | `$color-gray-200` |
| `outline` | transparent | `$color-gray-700` | `$color-gray-300` | `$color-gray-50` bg |
| `ghost` | transparent | `$color-gray-600` | none | `$color-gray-100` bg |
| `danger` | `$color-error` | `#FFFFFF` | none | `#B91C1C` |

**Example Usage**:

```html
<!-- Primary button with icon -->
<app-button variant="primary" icon="add" (clicked)="createCourse()">
  Create Course
</app-button>

<!-- Loading state -->
<app-button variant="primary" [loading]="saving()" (clicked)="save()">
  Save Changes
</app-button>

<!-- Danger button for destructive actions -->
<app-button variant="danger" icon="delete" (clicked)="confirmDelete()">
  Delete Course
</app-button>

<!-- Outline button group -->
<div class="button-group">
  <app-button variant="outline" icon="grid_view" [active]="viewMode() === 'grid'">Grid</app-button>
  <app-button variant="outline" icon="list" [active]="viewMode() === 'list'">List</app-button>
</div>
```

### 4.2.2 Icon Button Component

**Selector**: `app-icon-button`

For icon-only buttons (must include `aria-label`).

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `icon` | `string` | (required) | Material icon name |
| `ariaLabel` | `string` | (required) | Accessible label |
| `variant` | `'ghost' \| 'outline'` | `'ghost'` | Visual style |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Size |
| `disabled` | `boolean` | `false` | Disabled state |
| `badge` | `number \| null` | `null` | Notification badge count |

**Example**:

```html
<app-icon-button icon="notifications" ariaLabel="Notifications" [badge]="unreadCount()"></app-icon-button>
<app-icon-button icon="edit" ariaLabel="Edit course" variant="outline"></app-icon-button>
<app-icon-button icon="delete" ariaLabel="Delete item" variant="ghost"></app-icon-button>
```

---

## 4.3 Inputs & Form Controls

### 4.3.1 Text Input

**Selector**: `app-text-input`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `label` | `string` | `''` | Label text |
| `placeholder` | `string` | `''` | Placeholder text |
| `type` | `'text' \| 'email' \| 'password' \| 'number' \| 'url'` | `'text'` | Input type |
| `hint` | `string` | `''` | Helper text below input |
| `error` | `string` | `''` | Error message (shows red state when non-empty) |
| `prefix` | `string` | `''` | Prefix text (e.g., "https://") |
| `suffix` | `string` | `''` | Suffix text (e.g., "hours") |
| `maxLength` | `number \| null` | `null` | Max characters (shows counter when set) |
| `disabled` | `boolean` | `false` | Disabled state |
| `required` | `boolean` | `false` | Shows required indicator (*) |
| `showPasswordToggle` | `boolean` | `false` | Eye icon for password fields |

**Form Integration**: Implements `ControlValueAccessor` for use with Reactive Forms.

**Example**:

```html
<app-text-input
  label="Course Title"
  placeholder="Enter a title for your course"
  [maxLength]="100"
  [required]="true"
  [error]="titleError()"
  formControlName="title">
</app-text-input>

<app-text-input
  label="Email Address"
  type="email"
  placeholder="admin@example.com"
  [error]="emailError()"
  formControlName="email">
</app-text-input>

<app-text-input
  label="Password"
  type="password"
  [showPasswordToggle]="true"
  [error]="passwordError()"
  formControlName="password">
</app-text-input>
```

### 4.3.2 Textarea

**Selector**: `app-textarea`

**Props**: Same as `app-text-input` plus:

| Input | Type | Default | Description |
|---|---|---|---|
| `rows` | `number` | `4` | Number of visible rows |
| `autoResize` | `boolean` | `false` | Auto-grow with content |

### 4.3.3 Toggle / Switch

**Selector**: `app-toggle`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `label` | `string` | `''` | Label text |
| `disabled` | `boolean` | `false` | Disabled state |
| `size` | `'sm' \| 'md'` | `'md'` | Toggle size |

**Example**:

```html
<app-toggle label="Enable Feature Flag" formControlName="enabled"></app-toggle>
<app-toggle label="Auto-save drafts" [disabled]="isReadOnly()"></app-toggle>
```

### 4.3.4 Checkbox

**Selector**: `app-checkbox`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `label` | `string` | `''` | Label text |
| `indeterminate` | `boolean` | `false` | Indeterminate state (for "select all" headers) |
| `disabled` | `boolean` | `false` | Disabled state |

### 4.3.5 Radio Group

**Selector**: `app-radio-group`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `label` | `string` | `''` | Group label |
| `options` | `{ label: string; value: string; disabled?: boolean }[]` | `[]` | Radio options |
| `direction` | `'horizontal' \| 'vertical'` | `'vertical'` | Layout direction |

### 4.3.6 Tag Input

**Selector**: `app-tag-input`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `label` | `string` | `''` | Label text |
| `placeholder` | `string` | `'Add a tag...'` | Input placeholder |
| `maxTags` | `number` | `10` | Maximum number of tags |
| `allowDuplicates` | `boolean` | `false` | Allow duplicate tags |
| `suggestions` | `string[]` | `[]` | Autocomplete suggestions |

**Events**:

| Output | Payload | Description |
|---|---|---|
| `tagAdded` | `string` | Tag value added |
| `tagRemoved` | `string` | Tag value removed |

**Example**:

```html
<app-tag-input
  label="Tags"
  placeholder="Type and press Enter"
  [maxTags]="10"
  [suggestions]="['beginner', 'grammar', 'vocabulary', 'travel']"
  formControlName="tags">
</app-tag-input>
```

---

## 4.4 Dropdowns & Select Menus

### 4.4.1 Select Dropdown

**Selector**: `app-select`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `label` | `string` | `''` | Label text |
| `placeholder` | `string` | `'Select...'` | Placeholder when no selection |
| `options` | `{ label: string; value: any; disabled?: boolean; group?: string }[]` | `[]` | Options list |
| `multiple` | `boolean` | `false` | Allow multi-select |
| `searchable` | `boolean` | `false` | Show search input in dropdown |
| `clearable` | `boolean` | `false` | Show clear button |
| `error` | `string` | `''` | Error message |
| `disabled` | `boolean` | `false` | Disabled state |

**Events**:

| Output | Payload | Description |
|---|---|---|
| `selectionChange` | `any \| any[]` | Selected value(s) |

**Example**:

```html
<!-- Simple select -->
<app-select
  label="Difficulty Level"
  [options]="difficultyOptions"
  formControlName="difficulty">
</app-select>

<!-- Searchable multi-select -->
<app-select
  label="Prerequisites"
  [options]="courseOptions"
  [multiple]="true"
  [searchable]="true"
  [clearable]="true"
  formControlName="prerequisites">
</app-select>
```

### 4.4.2 Dropdown Menu

**Selector**: `app-dropdown-menu`

For action menus (not form selects).

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `trigger` | `TemplateRef` | (required) | Template for the trigger button |
| `items` | `DropdownItem[]` | `[]` | Menu items |
| `position` | `'bottom-start' \| 'bottom-end'` | `'bottom-start'` | Menu position |

**DropdownItem Interface**:

```typescript
interface DropdownItem {
  label: string;
  icon?: string;
  action: () => void;
  disabled?: boolean;
  divider?: boolean;      // Renders a divider before this item
  danger?: boolean;        // Red text styling
}
```

**Example**:

```html
<app-dropdown-menu [items]="courseActions" position="bottom-end">
  <ng-template #trigger>
    <app-icon-button icon="more_vert" ariaLabel="Course actions"></app-icon-button>
  </ng-template>
</app-dropdown-menu>
```

```typescript
courseActions: DropdownItem[] = [
  { label: 'Edit', icon: 'edit', action: () => this.editCourse() },
  { label: 'Duplicate', icon: 'content_copy', action: () => this.duplicateCourse() },
  { label: 'Archive', icon: 'archive', action: () => this.archiveCourse(), divider: true },
  { label: 'Delete', icon: 'delete', action: () => this.deleteCourse(), danger: true },
];
```

---

## 4.5 Modals & Dialogs

### 4.5.1 Modal Component

**Selector**: `app-modal`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `title` | `string` | `''` | Modal title |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl' \| 'full'` | `'md'` | Modal width |
| `closable` | `boolean` | `true` | Show close button |
| `closeOnBackdrop` | `boolean` | `true` | Close when clicking backdrop |
| `closeOnEscape` | `boolean` | `true` | Close on Escape key |

**Events**:

| Output | Payload | Description |
|---|---|---|
| `closed` | `void` | Modal was closed |

**Size Specifications**:

| Size | Max Width |
|---|---|
| `sm` | 400px |
| `md` | 560px |
| `lg` | 720px |
| `xl` | 960px |
| `full` | 100vw - 64px |

**Content Projection Slots**:

```html
<app-modal title="Confirm Deletion" size="sm" (closed)="onClose()">
  <!-- Default slot: modal body -->
  <p>Are you sure you want to delete this course? This action cannot be undone.</p>

  <!-- Named slot: modal footer -->
  <ng-container modal-footer>
    <app-button variant="outline" (clicked)="onClose()">Cancel</app-button>
    <app-button variant="danger" (clicked)="onConfirm()">Delete</app-button>
  </ng-container>
</app-modal>
```

### 4.5.2 Confirm Dialog Service

A programmatic API for simple confirmations:

```typescript
@Injectable({ providedIn: 'root' })
export class ConfirmDialogService {
  confirm(options: ConfirmOptions): Observable<boolean>;
}

interface ConfirmOptions {
  title: string;
  message: string;
  confirmLabel?: string;    // default: "Confirm"
  cancelLabel?: string;     // default: "Cancel"
  confirmVariant?: 'primary' | 'danger';  // default: 'primary'
  icon?: string;
}
```

**Usage**:

```typescript
this.confirmDialog.confirm({
  title: 'Delete Course',
  message: 'Are you sure you want to delete "Spanish Basics"? This cannot be undone.',
  confirmLabel: 'Delete',
  confirmVariant: 'danger',
  icon: 'delete',
}).subscribe((confirmed) => {
  if (confirmed) {
    this.store.dispatch(CourseActions.deleteCourse({ id: this.courseId }));
  }
});
```

### 4.5.3 Drawer / Side Panel

**Selector**: `app-drawer`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `title` | `string` | `''` | Drawer title |
| `position` | `'left' \| 'right'` | `'right'` | Slide-in direction |
| `width` | `string` | `'480px'` | Drawer width |
| `showBackdrop` | `boolean` | `true` | Show semi-transparent backdrop |

---

## 4.6 Tables & Data Grids

### 4.6.1 Data Table Component

**Selector**: `app-data-table`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `columns` | `ColumnDef[]` | `[]` | Column definitions |
| `data` | `any[]` | `[]` | Row data |
| `loading` | `boolean` | `false` | Show skeleton rows |
| `selectable` | `boolean` | `false` | Show row checkboxes |
| `sortable` | `boolean` | `true` | Enable column sorting |
| `stickyHeader` | `boolean` | `true` | Sticky table header |
| `rowClickable` | `boolean` | `true` | Rows are clickable |
| `emptyStateMessage` | `string` | `'No data found.'` | Empty state text |
| `emptyStateIcon` | `string` | `'search_off'` | Empty state icon |

**ColumnDef Interface**:

```typescript
interface ColumnDef {
  key: string;                    // Property path (supports dot notation)
  label: string;                  // Column header text
  sortable?: boolean;             // Override table-level sortable
  width?: string;                 // Fixed width (e.g., '120px', '15%')
  align?: 'left' | 'center' | 'right';
  type?: 'text' | 'date' | 'number' | 'status' | 'avatar' | 'custom';
  format?: string;                // date-fns format string for date type
  statusMap?: Record<string, { label: string; color: string }>;
  template?: TemplateRef<any>;    // Custom cell template
}
```

**Events**:

| Output | Payload | Description |
|---|---|---|
| `rowClick` | `{ row: any; index: number }` | Row clicked |
| `sortChange` | `{ column: string; direction: 'asc' \| 'desc' \| null }` | Sort changed |
| `selectionChange` | `any[]` | Selected rows changed |
| `selectAll` | `boolean` | Header checkbox toggled |

**Example**:

```html
<app-data-table
  [columns]="learnerColumns"
  [data]="learners()"
  [loading]="loading()"
  [selectable]="true"
  (rowClick)="openLearnerDetail($event.row)"
  (sortChange)="onSort($event)"
  (selectionChange)="onSelect($event)">
</app-data-table>
```

```typescript
learnerColumns: ColumnDef[] = [
  { key: 'avatar', label: '', type: 'avatar', width: '48px', sortable: false },
  { key: 'username', label: 'Username', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'joinDate', label: 'Joined', type: 'date', format: 'MMM d, yyyy', sortable: true },
  { key: 'lastActive', label: 'Last Active', type: 'date', format: 'relative', sortable: true },
  { key: 'streak', label: 'Streak', type: 'number', align: 'right', sortable: true },
  {
    key: 'status',
    label: 'Status',
    type: 'status',
    sortable: true,
    statusMap: {
      active: { label: 'Active', color: 'success' },
      suspended: { label: 'Suspended', color: 'warning' },
      banned: { label: 'Banned', color: 'error' },
    },
  },
];
```

### 4.6.2 Pagination Component

**Selector**: `app-pagination`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `page` | `number` | `1` | Current page |
| `perPage` | `number` | `25` | Items per page |
| `total` | `number` | `0` | Total items |
| `perPageOptions` | `number[]` | `[25, 50, 100]` | Page size options |
| `showPageSizeSelector` | `boolean` | `true` | Show page size dropdown |
| `showTotalCount` | `boolean` | `true` | Show "Showing X-Y of Z" |

**Events**:

| Output | Payload | Description |
|---|---|---|
| `pageChange` | `number` | New page number |
| `perPageChange` | `number` | New page size |

**Example**:

```html
<app-pagination
  [page]="currentPage()"
  [perPage]="pageSize()"
  [total]="totalUsers()"
  (pageChange)="onPageChange($event)"
  (perPageChange)="onPageSizeChange($event)">
</app-pagination>
```

---

## 4.7 Charts & Visualizations

### 4.7.1 Chart Wrapper Component

**Selector**: `app-chart`

All charts use ngx-charts under the hood, wrapped in a consistent container with loading, empty, and error states.

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `type` | `'line' \| 'bar' \| 'pie' \| 'donut' \| 'funnel' \| 'gauge' \| 'heatmap'` | `'line'` | Chart type |
| `data` | `ChartData[]` | `[]` | Chart data |
| `loading` | `boolean` | `false` | Show skeleton chart |
| `height` | `string` | `'400px'` | Chart container height |
| `title` | `string` | `''` | Chart title |
| `showLegend` | `boolean` | `true` | Show legend |
| `showXAxis` | `boolean` | `true` | Show x-axis |
| `showYAxis` | `boolean` | `true` | Show y-axis |
| `colorScheme` | `string[]` | Brand colors | Custom color array |
| `animations` | `boolean` | `true` | Enable chart animations |

**Events**:

| Output | Payload | Description |
|---|---|---|
| `pointClick` | `{ name: string; value: number; series?: string }` | Data point clicked |

**Example**:

```html
<app-chart
  type="line"
  title="User Growth"
  [data]="userGrowthData()"
  [loading]="loading()"
  height="350px"
  [showLegend]="true"
  (pointClick)="drillDown($event)">
</app-chart>
```

### 4.7.2 Metric Card Component

**Selector**: `app-metric-card`

**Props**:

| Input | Type | Default | Description |
|---|---|---|---|
| `title` | `string` | (required) | Metric title |
| `value` | `string \| number` | (required) | Metric value |
| `trend` | `'up' \| 'down' \| 'neutral'` | `'neutral'` | Trend direction |
| `trendValue` | `string` | `''` | Trend text (e.g., "+3.2%") |
| `icon` | `string` | `''` | Material icon |
| `loading` | `boolean` | `false` | Skeleton loading state |
| `clickable` | `boolean` | `false` | Show hover effect and cursor |

**Example**:

```html
<div class="metric-grid">
  <app-metric-card
    title="Daily Active Users"
    [value]="metrics()?.dau | number"
    trend="up"
    trendValue="+3.2%"
    icon="people"
    [loading]="loading()"
    [clickable]="true"
    (click)="navigateTo('/analytics/users')">
  </app-metric-card>

  <app-metric-card
    title="Pending Moderation"
    [value]="metrics()?.pendingModeration"
    icon="shield"
    [loading]="loading()">
  </app-metric-card>
</div>
```

---

## 4.8 Reusable Patterns

### 4.8.1 Search & Filter Bar Pattern

A common pattern used across all list pages:

```html
<div class="list-toolbar">
  <app-search-bar
    placeholder="Search users..."
    [value]="searchTerm()"
    (searchChange)="onSearch($event)">
  </app-search-bar>

  <app-filter-panel [filters]="filterConfig" [values]="activeFilters()" (filterChange)="onFilter($event)">
  </app-filter-panel>

  <div class="toolbar-actions">
    <app-button variant="outline" icon="download" (clicked)="export()">Export</app-button>
    <app-button variant="primary" icon="add" (clicked)="create()">New User</app-button>
  </div>
</div>
```

### 4.8.2 List Page Pattern

Standard structure for all list/table pages:

```
┌─ Page Header (title + description + primary action) ─┐
├─ Toolbar (search + filters + actions) ───────────────┤
├─ Data Table ─────────────────────────────────────────┤
├─ Pagination ─────────────────────────────────────────┤
└─ Bulk Actions Bar (when items selected) ─────────────┘
```

### 4.8.3 Detail Page Pattern

Standard structure for all detail/edit pages:

```
┌─ Breadcrumb ─────────────────────────────────────────┐
├─ Entity Header (avatar, name, metadata, actions) ────┤
├─ Tab Navigation ─────────────────────────────────────┤
├─ Tab Content Area ───────────────────────────────────┤
└─ Sticky Footer (Cancel + Save actions, for edit pages)┘
```

### 4.8.4 Empty State Pattern

```html
<app-empty-state
  icon="school"
  title="No courses yet"
  description="Create your first course to start building learning content."
  actionLabel="Create Course"
  (action)="createCourse()">
</app-empty-state>
```

### 4.8.5 Error State Pattern

```html
<app-error-state
  [error]="error()"
  (retry)="reload()">
</app-error-state>
```

### 4.8.6 Loading State Pattern

```html
@if (loading()) {
  <app-skeleton-loader type="table" [rows]="8"></app-skeleton-loader>
} @else if (error()) {
  <app-error-state [error]="error()" (retry)="reload()"></app-error-state>
} @else if (data().length === 0) {
  <app-empty-state icon="inbox" title="No items found"></app-empty-state>
} @else {
  <app-data-table [data]="data()" [columns]="columns"></app-data-table>
}
```

---

## 4.9 Naming Conventions

### 4.9.1 Component Naming

| Convention | Example |
|---|---|
| Feature page components | `LearnerListPageComponent`, `CourseBuilderPageComponent` |
| Shared components | `DataTableComponent`, `SearchBarComponent` |
| Feature-specific components | `ActivityFeedComponent`, `SkillTreeEditorComponent` |
| Layout components | `AdminLayoutComponent`, `SidebarComponent` |

### 4.9.2 File Naming

```
component-name.component.ts       // Component class
component-name.component.html     // Template
component-name.component.scss     // Styles
component-name.component.spec.ts  // Unit test
```

### 4.9.3 CSS Class Naming (BEM)

```scss
// Block
.metric-card { }

// Element
.metric-card__title { }
.metric-card__value { }
.metric-card__trend { }

// Modifier
.metric-card--loading { }
.metric-card__trend--up { }
.metric-card__trend--down { }
```

### 4.9.4 Event Naming

| Convention | Example |
|---|---|
| Output events | Verb phrase: `clicked`, `selectionChange`, `sortChange` |
| Store actions | `[Source] Verb Noun`: `[User List] Load Users`, `[Course API] Load Courses Success` |
| Method handlers | `on` + event: `onSearch()`, `onSort()`, `onPageChange()` |

---

## 4.10 Props & Events Reference

### 4.10.1 Common Input Patterns

```typescript
// Required string input
title = input.required<string>();

// Optional input with default
variant = input<'primary' | 'secondary'>('primary');

// Boolean input with default
loading = input<boolean>(false);

// Complex object input
options = input<SelectOption[]>([]);

// Computed from inputs
isDisabled = computed(() => this.disabled() || this.loading());
```

### 4.10.2 Common Output Patterns

```typescript
// Simple event
clicked = output<void>();

// Event with payload
selectionChange = output<string[]>();

// Event with complex payload
sortChange = output<{ column: string; direction: 'asc' | 'desc' | null }>();
```

### 4.10.3 ControlValueAccessor Pattern

All form components implement `ControlValueAccessor`:

```typescript
@Component({
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => TextInputComponent),
    multi: true,
  }],
})
export class TextInputComponent implements ControlValueAccessor {
  value = signal('');
  disabled = signal(false);

  private onChange: (value: string) => void = () => {};
  private onTouched: () => void = () => {};

  writeValue(value: string): void {
    this.value.set(value ?? '');
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(disabled: boolean): void {
    this.disabled.set(disabled);
  }

  onInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.value.set(value);
    this.onChange(value);
  }

  onBlur(): void {
    this.onTouched();
  }
}
```

---

## 4.11 Example Usage

### 4.11.1 Complete List Page Example

```typescript
@Component({
  selector: 'app-learner-list-page',
  standalone: true,
  imports: [
    SearchBarComponent,
    FilterPanelComponent,
    DataTableComponent,
    PaginationComponent,
    BulkActionsToolbarComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    SkeletonLoaderComponent,
    ButtonComponent,
    HasPermissionDirective,
  ],
  template: `
    <div class="page-header">
      <h1>Learners</h1>
      <p class="page-description">Manage learner accounts and activity.</p>
    </div>

    <div class="list-toolbar">
      <app-search-bar
        placeholder="Search by username or email..."
        [value]="searchTerm()"
        (searchChange)="onSearch($event)">
      </app-search-bar>

      <app-filter-panel
        [filters]="filterConfig"
        [values]="activeFilters()"
        (filterChange)="onFilter($event)">
      </app-filter-panel>

      <div class="toolbar-actions">
        <app-button
          *appHasPermission="'users.export'"
          variant="outline"
          icon="download"
          (clicked)="exportUsers()">
          Export
        </app-button>
      </div>
    </div>

    @if (loading()) {
      <app-skeleton-loader type="table" [rows]="10"></app-skeleton-loader>
    } @else if (error()) {
      <app-error-state [error]="error()" (retry)="loadUsers()"></app-error-state>
    } @else if (learners().length === 0) {
      <app-empty-state
        icon="people"
        title="No users match your search"
        description="Try adjusting your filters or search terms."
        actionLabel="Clear Filters"
        (action)="clearFilters()">
      </app-empty-state>
    } @else {
      <app-data-table
        [columns]="columns"
        [data]="learners()"
        [selectable]="true"
        (rowClick)="openDetail($event.row)"
        (sortChange)="onSort($event)"
        (selectionChange)="onSelectionChange($event)">
      </app-data-table>

      <app-pagination
        [page]="currentPage()"
        [perPage]="pageSize()"
        [total]="totalCount()"
        (pageChange)="onPageChange($event)"
        (perPageChange)="onPageSizeChange($event)">
      </app-pagination>
    }

    @if (selectedRows().length > 0) {
      <app-bulk-actions-toolbar [count]="selectedRows().length">
        <app-button
          *appHasPermission="'users.suspend'"
          variant="outline"
          icon="block"
          (clicked)="bulkSuspend()">
          Suspend Selected
        </app-button>
        <app-button variant="outline" icon="download" (clicked)="exportSelected()">
          Export Selected
        </app-button>
      </app-bulk-actions-toolbar>
    }
  `,
})
export class LearnerListPageComponent {
  private store = inject(Store);
  private router = inject(Router);

  // Selectors
  learners = this.store.selectSignal(selectLearners);
  loading = this.store.selectSignal(selectLearnersLoading);
  error = this.store.selectSignal(selectLearnersError);
  currentPage = this.store.selectSignal(selectLearnersPage);
  pageSize = this.store.selectSignal(selectLearnersPageSize);
  totalCount = this.store.selectSignal(selectLearnersTotal);
  searchTerm = this.store.selectSignal(selectLearnersSearchTerm);
  activeFilters = this.store.selectSignal(selectLearnersFilters);

  // Local state
  selectedRows = signal<Learner[]>([]);

  // ... column definitions, filter config, event handlers
}
```

### 4.11.2 Complete Form Page Example

```typescript
@Component({
  selector: 'app-course-builder-page',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    TextInputComponent,
    TextareaComponent,
    SelectComponent,
    TagInputComponent,
    FileUploadComponent,
    ButtonComponent,
    RichTextEditorComponent,
  ],
  template: `
    <div class="page-header">
      <h1>{{ isEditMode() ? 'Edit Course' : 'New Course' }}</h1>
    </div>

    <form [formGroup]="courseForm" (ngSubmit)="onSubmit()">
      <div class="form-section">
        <app-text-input
          label="Course Title"
          placeholder="e.g., Spanish for Beginners"
          [maxLength]="100"
          [required]="true"
          [error]="getError('title')"
          formControlName="title">
        </app-text-input>

        <app-rich-text-editor
          label="Description"
          [required]="true"
          [error]="getError('description')"
          formControlName="description">
        </app-rich-text-editor>

        <div class="form-row">
          <app-select
            label="Source Language"
            [options]="languageOptions()"
            [required]="true"
            [error]="getError('sourceLanguage')"
            formControlName="sourceLanguage">
          </app-select>

          <app-select
            label="Target Language"
            [options]="languageOptions()"
            [required]="true"
            [error]="getError('targetLanguage')"
            formControlName="targetLanguage">
          </app-select>
        </div>

        @if (courseForm.hasError('sameLanguage')) {
          <p class="cross-field-error">Source and target languages must be different.</p>
        }

        <app-select
          label="Difficulty Level"
          [options]="difficultyOptions"
          [required]="true"
          formControlName="difficulty">
        </app-select>

        <app-file-upload
          label="Thumbnail"
          accept="image/jpeg,image/png"
          [maxSizeMb]="2"
          hint="JPG or PNG, max 2MB, recommended 400×400px"
          formControlName="thumbnail">
        </app-file-upload>

        <app-tag-input
          label="Tags"
          [maxTags]="10"
          [suggestions]="tagSuggestions()"
          formControlName="tags">
        </app-tag-input>
      </div>

      <div class="form-actions">
        <app-button variant="outline" (clicked)="cancel()">Cancel</app-button>
        <app-button variant="secondary" (clicked)="saveDraft()" [loading]="savingDraft()">
          Save Draft
        </app-button>
        <app-button type="submit" variant="primary" [loading]="publishing()" [disabled]="courseForm.invalid">
          Publish
        </app-button>
      </div>
    </form>
  `,
})
export class CourseBuilderPageComponent {
  // ... form setup, submission logic, error handling
}
```

# 7. Security & Compliance

> Defines the security architecture, access control policies, audit logging, data protection, and compliance requirements for the Admin Panel.

---

## 7.1 Security Architecture Overview

### 7.1.1 Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│  NETWORK LAYER                                              │
│  VPN / IP Allowlist · TLS 1.3 · DDoS Protection            │
├─────────────────────────────────────────────────────────────┤
│  AUTHENTICATION LAYER                                       │
│  OAuth 2.0 + JWT · MFA (TOTP) · Session Management         │
├─────────────────────────────────────────────────────────────┤
│  AUTHORIZATION LAYER                                        │
│  RBAC · Permission Directives · Route Guards                │
├─────────────────────────────────────────────────────────────┤
│  APPLICATION LAYER                                          │
│  Input Validation · CSP · XSS Prevention · CSRF Protection  │
├─────────────────────────────────────────────────────────────┤
│  DATA LAYER                                                 │
│  Encryption at Rest · PII Masking · Audit Logging           │
├─────────────────────────────────────────────────────────────┤
│  MONITORING LAYER                                           │
│  Security Event Logging · Anomaly Detection · Alerting      │
└─────────────────────────────────────────────────────────────┘
```

### 7.1.2 Threat Model — Key Risks

| Threat | Risk Level | Mitigation |
|---|---|---|
| **Unauthorized access** | Critical | MFA, IP allowlisting, session timeout |
| **Privilege escalation** | Critical | Server-side RBAC enforcement, step-up auth for role changes |
| **XSS attacks** | High | CSP headers, Angular's built-in sanitization, strict template binding |
| **CSRF attacks** | High | SameSite cookies, CSRF tokens on state-changing requests |
| **Session hijacking** | High | HttpOnly cookies, short-lived tokens, token rotation |
| **Data exfiltration** | High | Audit logging, rate limiting on exports, PII access controls |
| **Insider threat** | Medium | Audit logs, least-privilege access, role separation |
| **Brute force login** | Medium | Account lockout, rate limiting, progressive delays |
| **API abuse** | Medium | Rate limiting, request throttling, anomaly detection |

### 7.1.3 Security Principles

| Principle | Implementation |
|---|---|
| **Defense in Depth** | Multiple security layers; no single point of failure. |
| **Least Privilege** | Users get only the permissions they need. Default is no access. |
| **Fail Secure** | On error, deny access rather than grant it. |
| **Zero Trust** | Verify every request. Never trust client-side checks alone. |
| **Separation of Duties** | Content creation and publishing require different roles. |
| **Audit Everything** | Every admin action is logged with actor, action, timestamp, and details. |

---

## 7.2 Role-Based Access Control

### 7.2.1 RBAC Implementation

**Frontend (UI-level, for UX)**:

- Navigation items are conditionally rendered based on user permissions.
- Action buttons are hidden or disabled for unauthorized users.
- Route guards redirect unauthorized users to a 403 page.
- The `*appHasPermission` directive controls element visibility.

**Backend (API-level, for security)**:

- Every API endpoint checks the user's permissions before processing.
- Permissions are embedded in the JWT token and validated on each request.
- The frontend permission set is a convenience cache; the server is the authority.

### 7.2.2 Permission Granularity

Permissions follow the `resource.action` convention:

```
users.view         – View user list and details
users.edit         – Edit user profile fields
users.suspend      – Suspend a user account
users.ban          – Ban a user account
users.delete       – Permanently delete a user account
users.export       – Export user data to CSV

courses.view       – View course list and details
courses.create     – Create new courses
courses.edit       – Edit existing courses
courses.publish    – Publish courses (state transition)
courses.delete     – Delete courses

moderation.view    – View moderation queue
moderation.action  – Take moderation actions (approve, remove, etc.)
moderation.escalate – Escalate items to senior moderators

analytics.view     – View analytics dashboards
analytics.export   – Export analytics data
analytics.custom_reports – Create and run custom reports

experiments.view   – View A/B tests and feature flags
experiments.create – Create new experiments
experiments.edit   – Edit experiment parameters
experiments.complete – Complete experiments and promote winners

flags.view         – View feature flags
flags.create       – Create feature flags
flags.edit         – Edit feature flags (including toggle)
flags.emergency_disable – Emergency disable all flags

settings.view      – View system settings
settings.edit      – Modify system settings
audit_logs.view    – View audit logs
audit_logs.export  – Export audit logs
```

### 7.2.3 Step-Up Authentication

Certain high-risk actions require the admin to re-authenticate:

| Action | Step-Up Required | Method |
|---|---|---|
| Assign/remove admin roles | Yes | Password re-entry |
| Delete user account | Yes | Password re-entry + reason |
| Emergency disable all flags | Yes | Password re-entry + confirmation code |
| Export PII data | Yes | MFA code |
| Modify system settings | Yes | Password re-entry |
| Create/deactivate admin account | Yes | Password re-entry |

**Implementation**:

```typescript
@Injectable({ providedIn: 'root' })
export class StepUpAuthService {
  private dialog = inject(MatDialog);
  private authService = inject(AuthService);

  requireReauth(): Observable<boolean> {
    return this.dialog
      .open(ReauthDialogComponent, {
        width: '400px',
        disableClose: true,
      })
      .afterClosed()
      .pipe(
        switchMap((password: string | null) => {
          if (!password) return of(false);
          return this.authService.verifyPassword(password);
        }),
      );
  }

  requireMfa(): Observable<boolean> {
    return this.dialog
      .open(MfaDialogComponent, {
        width: '400px',
        disableClose: true,
      })
      .afterClosed()
      .pipe(
        switchMap((code: string | null) => {
          if (!code) return of(false);
          return this.authService.verifyMfa(code);
        }),
      );
  }
}
```

### 7.2.4 Separation of Duties Matrix

| Action | Requires Role | Cannot Be Same Person As |
|---|---|---|
| Create course content | Content Manager | Course publisher |
| Publish course | Content Manager / Super Admin | Content creator (recommended) |
| Review flagged content | Moderator | Content author |
| Approve translations | Localization Manager | Translator (recommended) |
| Create admin account | Super Admin | The new admin themselves |
| Complete experiment | QA / Tester | Experiment creator (recommended) |

---

## 7.3 Audit Logs

### 7.3.1 What Gets Logged

**Every admin action** is logged. No exceptions.

| Category | Actions Logged |
|---|---|
| **Authentication** | Login success, login failure, MFA success, MFA failure, logout, password change, token refresh |
| **User Management** | View user PII, edit user, suspend, unsuspend, ban, delete, export users, create admin, edit admin roles |
| **Course Management** | Create, edit, publish, unpublish, archive, delete course. Create/edit skill. Create/edit/delete lesson. Create/edit/delete exercise. |
| **Content Moderation** | Approve, remove, edit, escalate flagged content. Ban/warn users. |
| **Analytics** | Access analytics page, export data, create/run custom report |
| **Localization** | Edit translation, approve translation, edit glossary, import/export glossary |
| **Experiments** | Create, start, pause, complete experiment. Toggle feature flag. Emergency disable. |
| **Settings** | Edit system settings, view/export audit logs, manage API keys |

### 7.3.2 Audit Log Entry Structure

```typescript
interface AuditLogEntry {
  id: string;
  timestamp: string;            // ISO 8601 with milliseconds
  actor: {
    id: string;
    email: string;
    displayName: string;
    ipAddress: string;
    userAgent: string;
  };
  action: string;               // e.g., 'user.ban', 'course.publish'
  resource: {
    type: string;               // e.g., 'user', 'course', 'feature_flag'
    id: string;
    name: string;               // Human-readable resource name
  };
  details: Record<string, any>; // Action-specific metadata
  previousState?: Record<string, any>;  // Before the change (for edits)
  newState?: Record<string, any>;       // After the change (for edits)
  result: 'success' | 'failure';
  failureReason?: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}
```

### 7.3.3 Audit Log Example Entries

**User Ban**:

```json
{
  "id": "audit_8f3a2b",
  "timestamp": "2026-03-08T09:15:44.123Z",
  "actor": {
    "id": "admin_42",
    "email": "john.d@company.com",
    "displayName": "John D.",
    "ipAddress": "10.0.1.45",
    "userAgent": "Mozilla/5.0..."
  },
  "action": "user.ban",
  "resource": {
    "type": "user",
    "id": "user_9876",
    "name": "@spammer_42"
  },
  "details": {
    "reason": "Repeated spam in forums",
    "permanent": true
  },
  "previousState": { "status": "active" },
  "newState": { "status": "banned" },
  "result": "success",
  "riskLevel": "high"
}
```

**Feature Flag Emergency Disable**:

```json
{
  "id": "audit_7c1d4e",
  "timestamp": "2026-03-08T10:00:00.456Z",
  "actor": {
    "id": "admin_01",
    "email": "super.admin@company.com",
    "displayName": "Super Admin",
    "ipAddress": "10.0.1.10",
    "userAgent": "Mozilla/5.0..."
  },
  "action": "flags.emergency_disable",
  "resource": {
    "type": "system",
    "id": "feature_flags",
    "name": "All Non-Essential Feature Flags"
  },
  "details": {
    "reason": "Production incident — reverting all experiments",
    "flagsDisabled": 12,
    "flagsPreserved": 3
  },
  "result": "success",
  "riskLevel": "critical"
}
```

### 7.3.4 Audit Log Retention

| Category | Retention Period | Storage |
|---|---|---|
| Authentication events | 2 years | Hot storage (database) |
| User management actions | 5 years | Hot (1 year) + cold (archive) |
| Content changes | 3 years | Hot (6 months) + cold |
| Configuration changes | 5 years | Hot (1 year) + cold |
| Critical actions (bans, deletes, emergency) | 7 years | Hot (2 years) + cold |

### 7.3.5 Audit Log Access Control

- Only Super Admins can view audit logs.
- Audit logs themselves are append-only — no one can modify or delete them.
- Accessing audit logs is itself logged (meta-audit).
- Export of audit logs requires step-up authentication.

---

## 7.4 Sensitive Data Handling

### 7.4.1 PII Classification

| Data | Classification | Handling |
|---|---|---|
| Email address | PII | Displayed to authorized roles. Masked in logs. |
| IP address | PII | Stored in audit logs only. Not displayed in UI. |
| Password | Sensitive | Never stored in frontend. Never logged. |
| MFA secret | Sensitive | Never stored in frontend. |
| User location (country) | PII | Displayed in aggregated analytics. Individual display requires `users.view`. |
| User activity history | PII | Access requires `users.view`. Not exported without `users.export`. |
| Payment/subscription data | Financial PII | Read-only display. No modification via admin panel. |

### 7.4.2 Data Masking in UI

| Context | Masking Rule |
|---|---|
| Email in user list | Full email visible to authorized admins |
| Email in audit log display | `j***n@example.com` (first and last char visible) |
| IP addresses | Not displayed in UI (only in audit log exports) |
| User IDs in logs | Full ID visible (not considered PII) |
| Exported CSV files | Watermarked with exporting admin's ID and timestamp |

### 7.4.3 Frontend Data Protection

**In-Memory Token Storage**:

```typescript
// Access token is stored ONLY in JavaScript memory (not localStorage/sessionStorage)
// This protects against XSS-based token theft
private accessToken: string | null = null;
```

**No Sensitive Data in URLs**:

- Tokens are never passed as URL parameters.
- Search queries involving user emails use POST requests to avoid logging in server access logs.
- Sensitive route parameters use opaque IDs, not email addresses or usernames.

**Clipboard Protection**:

```typescript
// When copying sensitive data (e.g., API keys), clear clipboard after 60 seconds
copyToClipboard(text: string): void {
  navigator.clipboard.writeText(text);
  this.toastService.info('Copied to clipboard. Will be cleared in 60 seconds.');
  setTimeout(() => navigator.clipboard.writeText(''), 60_000);
}
```

**Browser Storage Policy**:

| Storage Type | Allowed Data |
|---|---|
| `localStorage` | Theme preference, sidebar state, form drafts (no PII), last-used filters |
| `sessionStorage` | Tab-specific UI state only |
| Cookies | Refresh token (HttpOnly, Secure, SameSite=Strict) — set by server |
| IndexedDB | Not used |

### 7.4.4 Data Minimization

- API responses include only the fields needed for the current view.
- List endpoints return summary DTOs (fewer fields than detail endpoints).
- The `fields` query parameter enables sparse fieldsets.
- The frontend never requests data it won't display.

---

## 7.5 Rate Limiting on Admin Actions

### 7.5.1 Rate Limits by Action Category

| Action | Rate Limit | Window | Scope |
|---|---|---|---|
| Login attempts | 5 attempts | 15 minutes | Per IP + email |
| MFA attempts | 5 attempts | 15 minutes | Per user |
| User search | 60 requests | 1 minute | Per admin |
| Data export | 10 exports | 1 hour | Per admin |
| Bulk operations | 5 operations | 5 minutes | Per admin |
| Content moderation actions | 100 actions | 1 minute | Per admin |
| API write operations (general) | 120 requests | 1 minute | Per admin |
| API read operations (general) | 600 requests | 1 minute | Per admin |
| Emergency actions | 1 per type | 1 hour | Global |

### 7.5.2 Rate Limit Response Handling

```typescript
// API returns 429 with Retry-After header
// HTTP/1.1 429 Too Many Requests
// Retry-After: 45
// X-RateLimit-Limit: 60
// X-RateLimit-Remaining: 0
// X-RateLimit-Reset: 1709892000

// Frontend interceptor handling
export const rateLimitInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 429) {
        const retryAfter = parseInt(error.headers.get('Retry-After') || '60', 10);
        const toastService = inject(ToastService);
        toastService.warning(
          `Too many requests. Please wait ${retryAfter} seconds before trying again.`,
          { duration: retryAfter * 1000 },
        );
      }
      return throwError(() => error);
    }),
  );
};
```

### 7.5.3 Client-Side Throttling

Preemptive client-side throttling to avoid hitting server rate limits:

```typescript
@Injectable({ providedIn: 'root' })
export class ThrottleService {
  private actionTimestamps = new Map<string, number[]>();

  canPerform(action: string, limit: number, windowMs: number): boolean {
    const now = Date.now();
    const timestamps = this.actionTimestamps.get(action) || [];

    // Remove timestamps outside the window
    const recent = timestamps.filter((t) => now - t < windowMs);

    if (recent.length >= limit) {
      return false;
    }

    recent.push(now);
    this.actionTimestamps.set(action, recent);
    return true;
  }
}

// Usage
if (!this.throttle.canPerform('export', 10, 3600000)) {
  this.toast.warning('Export limit reached. Please try again later.');
  return;
}
```

### 7.5.4 Progressive Delays

For login attempts:

```
Attempt 1-3:   No delay
Attempt 4:     5 second delay
Attempt 5:     15 second delay
After 5:       Account locked for 15 minutes
```

The frontend displays a countdown timer and disables the submit button during the delay period.

---

## 7.6 Content Security Policy

### 7.6.1 CSP Headers

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' https://cdn.example.com data:;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.example.com wss://ws.example.com;
  media-src 'self' https://cdn.example.com;
  frame-src 'none';
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
```

### 7.6.2 XSS Prevention

| Vector | Prevention |
|---|---|
| Template injection | Angular's built-in template sanitization. Never use `bypassSecurityTrust*` without code review. |
| DOM manipulation | Always use Angular's Renderer2, never direct DOM access for user-supplied content. |
| URL injection | Validate all URLs. Only allow `https://` scheme. |
| SVG injection | Sanitize SVG uploads server-side. Display with `<img>` (not inline `<svg>`). |
| Rich text editor | Server-side HTML sanitization. Client-side: Use a sanitization library (e.g., DOMPurify) before rendering. |

### 7.6.3 CSRF Protection

- All state-changing requests (POST, PUT, PATCH, DELETE) include a CSRF token.
- The CSRF token is stored in a cookie (`XSRF-TOKEN`) and sent as a header (`X-XSRF-TOKEN`).
- Angular's `HttpClient` automatically handles this with `HttpClientXsrfModule`.

### 7.6.4 Subresource Integrity

All third-party scripts and stylesheets loaded from CDNs include SRI hashes:

```html
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Inter"
      integrity="sha384-..."
      crossorigin="anonymous">
```

---

## 7.7 GDPR & Data Privacy Compliance

### 7.7.1 Admin Panel GDPR Responsibilities

| Requirement | Implementation |
|---|---|
| **Right to Access** | Admin can export a user's complete data profile via the user detail page. |
| **Right to Erasure** | "Delete Account" action permanently removes all PII. Content is anonymized (author shown as "[Deleted User]"). |
| **Data Minimization** | API returns only necessary fields. Sparse fieldsets support. |
| **Consent Management** | Not directly managed in admin panel (handled in learner-facing app). Admin can view consent status. |
| **Data Portability** | Export user data in machine-readable format (JSON/CSV). |
| **Breach Notification** | Audit logs enable incident investigation. Monitoring detects anomalies. |

### 7.7.2 Data Retention UI

The admin panel displays data retention policies and allows Super Admins to:

- View the data retention schedule per data category.
- Initiate manual data purge for specific users (subject to legal hold checks).
- View users pending data deletion (scheduled by the automated retention system).
- Override retention for legal holds.

### 7.7.3 PII Export Safeguards

When exporting user data:

1. Step-up authentication required (MFA re-verification).
2. Export is logged in the audit trail with: Exporting admin, data scope, row count, timestamp.
3. Exported file is watermarked with: Admin email, export timestamp, expiration notice.
4. Export count is rate-limited (max 10 per hour per admin).
5. Notification sent to the Super Admin channel about the export.

### 7.7.4 Account Deletion Flow

```
1. Admin selects "Delete Account" for learner
2. Step-up auth: Admin re-enters password
3. Admin provides reason (dropdown + free text)
4. Admin types the user's email as confirmation
5. System shows preview of what will be deleted:
   - Profile data (name, email, avatar)
   - Learning progress
   - Forum posts (anonymized, not deleted)
   - Subscription data (forwarded to billing team)
6. Admin confirms
7. Account enters "pending deletion" state (30-day grace period)
8. After 30 days, automated system permanently erases data
9. Audit log entry created with full details
```

---

## 7.8 Security Testing & Review Checklist

### 7.8.1 Pre-Release Security Checklist

| Category | Check | Passed |
|---|---|---|
| **Authentication** | MFA enforcement for all admin accounts | ☐ |
| | Session timeout after 30 minutes of inactivity | ☐ |
| | Absolute session timeout after 12 hours | ☐ |
| | Account lockout after 5 failed login attempts | ☐ |
| | Refresh token rotation on use | ☐ |
| **Authorization** | All routes protected by auth guards | ☐ |
| | All routes protected by role guards | ☐ |
| | All API endpoints enforce server-side RBAC | ☐ |
| | UI elements hidden for unauthorized roles | ☐ |
| | Step-up auth for high-risk actions | ☐ |
| **XSS Prevention** | No use of `innerHTML` with user data | ☐ |
| | No use of `bypassSecurityTrust*` without review | ☐ |
| | CSP headers configured correctly | ☐ |
| | Rich text content is sanitized before rendering | ☐ |
| **CSRF** | CSRF token on all state-changing requests | ☐ |
| | SameSite cookie attribute set to Strict | ☐ |
| **Data Protection** | Access tokens stored in memory only | ☐ |
| | No PII in URLs or query parameters | ☐ |
| | No sensitive data in localStorage | ☐ |
| | Exported data is watermarked and rate-limited | ☐ |
| **Audit** | All admin actions are logged | ☐ |
| | Audit logs are append-only | ☐ |
| | Audit log access is itself audited | ☐ |
| **Rate Limiting** | Login rate limits enforced | ☐ |
| | API rate limits enforced | ☐ |
| | Export rate limits enforced | ☐ |
| | Client-side throttling matches server limits | ☐ |
| **Dependencies** | No known CVEs in npm dependencies | ☐ |
| | `npm audit` shows no critical or high vulnerabilities | ☐ |
| | SRI hashes on CDN resources | ☐ |

### 7.8.2 Security Testing Activities

| Activity | Frequency | Responsibility |
|---|---|---|
| Static analysis (ESLint security rules) | Every commit (CI) | Automated |
| Dependency vulnerability scan (`npm audit`) | Daily (CI) | Automated |
| OWASP ZAP scan | Weekly | Security team |
| Penetration testing | Quarterly | External vendor |
| RBAC permission matrix review | Every release | Engineering + Security |
| Audit log review | Weekly | Security team |
| Incident response drill | Bi-annually | Security team + Engineering |

### 7.8.3 Incident Response Procedure

```
1. DETECT
   - Monitoring alerts on anomalous admin activity
   - Unusual login patterns (new IP, unusual time)
   - Spike in data exports or user modifications

2. CONTAIN
   - Super Admin can immediately disable compromised admin account
   - Emergency disable all feature flags if system integrity is at risk
   - Revoke all sessions for the affected admin

3. INVESTIGATE
   - Review audit logs for the affected admin's recent actions
   - Filter by actor, time range, and action type
   - Export relevant logs for forensic analysis

4. REMEDIATE
   - Revert unauthorized changes using version history
   - Reset credentials for affected accounts
   - Update access controls if privilege escalation occurred

5. REPORT
   - Generate incident report from audit log data
   - Notify affected parties per GDPR requirements (within 72 hours for breaches)
   - Update security policies based on lessons learned
```

### 7.8.4 Security Headers Reference

| Header | Value | Purpose |
|---|---|---|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Force HTTPS |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `X-XSS-Protection` | `0` | Disable legacy XSS filter (rely on CSP instead) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer information |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Disable unnecessary APIs |
| `Content-Security-Policy` | (See Section 7.6.1) | Prevent XSS, injection attacks |
| `Cache-Control` | `no-store, no-cache, must-revalidate` | Prevent caching of sensitive admin pages |

# GetMailZen - Product Improvement Action List

## 🔧 Critical Improvements (Must Implement Before Launch)

### 1. User Authentication & Session Management
**Priority: CRITICAL**

**Current State:** No user authentication - anyone can access the dashboard

**Required Changes:**
- [ ] Add user registration system
  - Email/password with bcrypt hashing
  - Email verification flow
  - Password strength requirements

- [ ] Implement login system
  - Flask-Login for session management
  - Remember me functionality
  - Login rate limiting

- [ ] Add user database schema
  ```sql
  CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    email_verified BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(50),
    trial_ends_at TIMESTAMP
  );
  ```

- [ ] Protect all routes with @login_required decorator
- [ ] Add logout functionality
- [ ] Implement password reset flow

**Files to Create/Modify:**
- `app/auth.py` (new authentication module)
- `app/models.py` (new database models)
- `web_app.py` (add auth routes and protection)
- `templates/login.html` (new)
- `templates/register.html` (new)

---

### 2. Gmail OAuth Per-User Storage
**Priority: CRITICAL**

**Current State:** Single OAuth token stored globally - only works for one user

**Required Changes:**
- [ ] Store Gmail credentials per user in database
  ```sql
  CREATE TABLE gmail_credentials (
    user_id INTEGER REFERENCES users(id),
    gmail_email VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
  );
  ```

- [ ] Encrypt tokens before storage (use cryptography.fernet)
- [ ] Implement automatic token refresh
- [ ] Add OAuth disconnect functionality
- [ ] Support multiple Gmail accounts per user

**Files to Modify:**
- `app/gmail_service.py` - Accept user_id parameter
- `web_app.py` - Add OAuth callback route per user
- Create `app/encryption.py` - Token encryption utilities

---

### 3. Payment & Subscription System
**Priority: CRITICAL**

**Current State:** No payment integration

**Required Changes:**
- [ ] Integrate Stripe
  - Create Stripe account
  - Add API keys to environment variables
  - Install stripe Python library

- [ ] Implement subscription tiers
  ```sql
  CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    tier VARCHAR(50), -- starter, professional, business
    status VARCHAR(50), -- active, canceled, past_due
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE
  );
  ```

- [ ] Add usage tracking
  - Track emails processed per month
  - Enforce tier limits
  - Upgrade prompts when limit reached

- [ ] Implement webhooks
  - Payment succeeded
  - Payment failed
  - Subscription canceled
  - Trial ending soon

**Files to Create:**
- `app/stripe_integration.py`
- `templates/pricing.html`
- `templates/billing.html`
- `app/usage_tracker.py`

---

### 4. Email Notifications System
**Priority: HIGH**

**Current State:** No email communication with users

**Required Changes:**
- [ ] Set up transactional email service (Postmark or SendGrid)
- [ ] Create email templates:
  - Welcome email
  - Email verification
  - Password reset
  - Trial ending reminder (7 days, 3 days, 1 day)
  - Payment failed notification
  - Invoice receipt
  - Monthly usage summary
  - Account deletion confirmation

- [ ] Add email preferences
  - Allow users to control notification settings
  - Unsubscribe links
  - Preference center

**Files to Create:**
- `app/email_service.py`
- `templates/emails/` directory with all email templates

---

### 5. Database Integration
**Priority: CRITICAL**

**Current State:** Using file-based config.json - not suitable for multiple users

**Required Changes:**
- [ ] Set up PostgreSQL database
- [ ] Create migration system (Alembic)
- [ ] Define all database models:
  - Users
  - Subscriptions
  - Gmail Credentials
  - Email Processing History
  - User Settings
  - Retention Policies (per user)
  - Whitelist (per user)

- [ ] Migrate from config.json to database
- [ ] Add database connection pooling
- [ ] Implement proper error handling

**Files to Create:**
- `app/database.py` - Database connection and session management
- `app/models.py` - SQLAlchemy models
- `migrations/` directory - Alembic migrations
- `alembic.ini` - Migration configuration

---

## 🎯 Important Improvements (Implement Soon)

### 6. Improved Onboarding Flow
**Priority: HIGH**

**Current State:** Users dropped into dashboard with no guidance

**Required Changes:**
- [ ] Create multi-step onboarding wizard
  - Step 1: Welcome & explain value
  - Step 2: Connect Gmail account
  - Step 3: Run first inbox analysis
  - Step 4: Review AI suggestions
  - Step 5: Set up retention policy
  - Step 6: Complete!

- [ ] Add onboarding checklist
  - Shows progress
  - Allows skipping steps
  - Tracks completion

- [ ] Implement tutorial tooltips (product tour)
- [ ] Add sample/demo data for empty accounts

**Files to Create:**
- `templates/onboarding.html`
- `app/onboarding.py`
- Add onboarding state to user model

---

### 7. Error Handling & User Feedback
**Priority: HIGH**

**Current State:** Errors shown in console, not helpful for users

**Required Changes:**
- [ ] Implement user-friendly error messages
  - "Something went wrong" → "Unable to connect to Gmail. Please reconnect your account."
  - Show actionable solutions

- [ ] Add error logging
  - Log to file
  - Send critical errors to monitoring service (Sentry)

- [ ] Implement retry logic
  - Auto-retry failed API calls
  - Exponential backoff

- [ ] Add success feedback
  - Toast notifications for all actions
  - Progress indicators
  - Confirmation messages

**Files to Modify:**
- All Python files - Add try/except with user-friendly messages
- `web_app.py` - Add error handler routes
- `templates/dashboard.html` - Ensure all API calls show errors

---

### 8. Rate Limiting & Abuse Prevention
**Priority: HIGH**

**Current State:** No limits - could be abused or cause API quota issues

**Required Changes:**
- [ ] Implement rate limiting
  - Per user: 100 requests/hour
  - Per IP: 1000 requests/hour
  - Gmail API: 250 quota units/user/second

- [ ] Add usage quotas per tier
  - Starter: 1,000 emails/month
  - Professional: 5,000 emails/month
  - Business: Unlimited

- [ ] Track and display usage
  - "You've processed 245/1,000 emails this month"
  - Upgrade prompt when approaching limit

- [ ] Implement queue system for background jobs
  - Use Celery + Redis
  - Process large batches in background
  - Show job progress to user

**Files to Create:**
- `app/rate_limiter.py`
- `app/usage_monitor.py`
- `app/celery_tasks.py`

---

### 9. Settings & Preferences
**Priority: MEDIUM**

**Current State:** Global config - no per-user customization

**Required Changes:**
- [ ] Create user settings page
  - Email notification preferences
  - Retention policy defaults
  - Whitelist management
  - Category customization
  - Time zone
  - Language (future)

- [ ] Add data export
  - GDPR compliance
  - Download all user data as JSON

- [ ] Account deletion
  - Delete Gmail credentials
  - Delete processing history
  - Cancel subscription
  - Soft delete (keep for 30 days)

**Files to Create:**
- `templates/settings.html`
- `app/user_preferences.py`
- `app/data_export.py`

---

### 10. Analytics & Insights Dashboard
**Priority: MEDIUM**

**Current State:** Basic stats, no historical tracking

**Required Changes:**
- [ ] Track historical data
  - Inbox health score over time
  - Emails processed per day/week/month
  - Storage saved
  - Time saved estimation

- [ ] Create insights dashboard
  - Line charts showing trends
  - Comparison: "Your inbox is 45% cleaner than last month"
  - Achievements: "You've deleted 1,000 emails!"

- [ ] Add email breakdown
  - Pie chart: Categories distribution
  - Top senders
  - Most common subjects
  - Email volume by hour/day

**Files to Create:**
- `app/analytics.py`
- `templates/insights.html`
- Add analytics tables to database

---

## 🚀 Nice-to-Have Improvements (Future Features)

### 11. Advanced Automation Rules
**Priority: LOW**

- [ ] Custom automation rules builder
  - "If email from X, then label Y and archive"
  - Visual rule builder (drag-drop)
  - Schedule rules to run at specific times

- [ ] AI-powered smart rules
  - "Learn from my actions and automate similar emails"
  - Suggest rules based on behavior

---

### 12. Multi-Email Provider Support
**Priority: LOW**

- [ ] Add support for Outlook/Office 365
- [ ] Add support for Yahoo Mail
- [ ] Add support for custom IMAP accounts
- [ ] Unified inbox view

---

### 13. Team Features
**Priority: LOW**

- [ ] Team accounts (multiple users, shared billing)
- [ ] Role-based access
- [ ] Shared retention policies
- [ ] Team analytics

---

### 14. Mobile App
**Priority: LOW**

- [ ] React Native mobile app
- [ ] Push notifications
- [ ] Quick actions from mobile
- [ ] Simplified mobile dashboard

---

### 15. API & Integrations
**Priority: LOW**

- [ ] Public API for third-party integrations
- [ ] Zapier integration
- [ ] Slack notifications
- [ ] IFTTT support
- [ ] Browser extension

---

## 📋 Code Quality Improvements

### 16. Testing
**Current State:** No tests

**Required:**
- [ ] Unit tests for all modules (pytest)
- [ ] Integration tests for API endpoints
- [ ] End-to-end tests for user flows
- [ ] Test coverage > 80%

---

### 17. Documentation
**Current State:** Basic README

**Required:**
- [ ] API documentation
- [ ] Developer setup guide
- [ ] Architecture diagram
- [ ] Code comments for complex functions
- [ ] User documentation/help center

---

### 18. Performance Optimization
**Current State:** Works for single user, untested at scale

**Required:**
- [ ] Database query optimization (add indexes)
- [ ] Implement caching (Redis)
- [ ] Paginate large result sets
- [ ] Lazy loading for frontend
- [ ] Background job processing for slow operations
- [ ] CDN for static assets

---

## 🎨 UI/UX Improvements

### 19. Accessibility
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] ARIA labels
- [ ] Color contrast compliance (WCAG AA)
- [ ] Focus indicators

---

### 20. Mobile Responsiveness
**Current State:** Responsive but could be optimized

**Improvements:**
- [ ] Test on actual devices
- [ ] Optimize touch targets (44px minimum)
- [ ] Simplified mobile navigation
- [ ] Mobile-specific layouts for complex tables

---

## 🔄 Continuous Improvement

### 21. User Feedback Loop
- [ ] In-app feedback widget
- [ ] NPS survey (monthly)
- [ ] Feature request voting system
- [ ] Bug report template

---

### 22. A/B Testing
- [ ] Test pricing page variations
- [ ] Test onboarding flows
- [ ] Test CTA button copy
- [ ] Test email subject lines

---

## Implementation Priority Matrix

| Priority | Time to Implement | Impact | Start Week |
|----------|-------------------|---------|------------|
| User Auth | 3-5 days | CRITICAL | Week 2 |
| Per-User OAuth | 2-3 days | CRITICAL | Week 2 |
| Database | 3-4 days | CRITICAL | Week 1 |
| Payments | 4-5 days | CRITICAL | Week 2 |
| Email System | 2-3 days | HIGH | Week 2 |
| Onboarding | 2-3 days | HIGH | Week 3 |
| Rate Limiting | 1-2 days | HIGH | Week 3 |
| Error Handling | 2-3 days | HIGH | Week 3 |
| Settings | 2-3 days | MEDIUM | Week 3 |
| Analytics | 3-4 days | MEDIUM | Week 4 |

---

This action list transforms GetMailZen from a functional prototype into a production-ready SaaS product. Focus on Critical and High priority items first.

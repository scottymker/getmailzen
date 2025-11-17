# Database Setup Guide - GetMailZen

## Step 1: Get Your Railway Database URL

You mentioned you have PostgreSQL ready in Railway. Here's how to get the connection URL:

1. Go to your Railway project dashboard
2. Click on your PostgreSQL service
3. Click on the **Variables** tab
4. Copy the `DATABASE_URL` value (it should look like this):
   ```
   postgresql://postgres:password@containers-us-west-123.railway.app:5432/railway
   ```

**Important:** Railway provides two URLs:
- **DATABASE_URL** (private network) - Use this for local development
- **DATABASE_PUBLIC_URL** (public network) - Use this if deploying elsewhere

For now, copy the **DATABASE_URL**.

---

## Step 2: Generate Encryption Key

The encryption key is used to encrypt OAuth tokens in the database.

Run this command:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output (it will look like: `8xK7vP2mQ9nR1sT6uV3wX4yZ5aB8cD9eF0gH1iJ2kL3=`)

---

## Step 3: Generate Flask Secret Key

The Flask secret key is used for session management.

Run this command:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (it will be a 64-character hex string)

---

## Step 4: Update Your .env File

1. Open or create `.env` in the project root
2. Add these variables (replace with your actual values):

```bash
# Claude API Key (you already have this)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Database URL from Railway (paste your actual URL)
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:PORT/railway

# Encryption key (paste the key you generated in Step 2)
ENCRYPTION_KEY=your-generated-encryption-key-here

# Flask secret key (paste the key you generated in Step 3)
FLASK_SECRET_KEY=your-generated-flask-secret-key-here

# Redis URL (if you have Redis in Railway, paste its URL; otherwise use localhost)
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development
```

---

## Step 5: Create Initial Database Migration

Once your .env is set up, create the initial migration:

```bash
/Users/scottymker/Library/Python/3.9/bin/alembic revision --autogenerate -m "Initial database schema"
```

This will create a migration file in `migrations/versions/` with all your database tables.

---

## Step 6: Apply Migration to Railway Database

Run the migration to create all tables in your Railway PostgreSQL database:

```bash
/Users/scottymker/Library/Python/3.9/bin/alembic upgrade head
```

This will:
- Create `users` table
- Create `gmail_credentials` table
- Create `subscriptions` table
- Create `processing_history` table
- Create `user_settings` table
- Create `retention_policies` table
- Create `whitelists` table
- Create `email_categories` table
- Create `inbox_health_snapshots` table
- Create `usage_tracking` table
- Create `audit_logs` table

---

## Step 7: Test Database Connection

Test that everything is working:

```bash
python3 -c "from app.database import test_connection; test_connection()"
```

You should see: `Database connection successful!`

---

## Step 8: Create Your First User (Manual for Now)

Until we build the registration UI, you can create a test user using Python:

```python
python3 -c "
from app.database import SessionLocal
from app.models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SessionLocal()

# Create test user
user = User(
    email='your-email@example.com',
    password_hash=bcrypt.generate_password_hash('your-password').decode('utf-8'),
    email_verified=True,
    subscription_tier='trial'
)

db.add(user)
db.commit()
print(f'User created: {user.email} (ID: {user.id})')
db.close()
"
```

---

## Troubleshooting

### Error: "DATABASE_URL environment variable is not set"
- Make sure your `.env` file is in the project root directory
- Make sure you don't have typos (it's `DATABASE_URL` not `DB_URL`)

### Error: "could not connect to server"
- Check that your Railway database is running
- Verify you copied the correct DATABASE_URL
- Try using `DATABASE_PUBLIC_URL` instead if private network fails

### Error: "relation does not exist"
- You haven't run migrations yet
- Run: `/Users/scottymker/Library/Python/3.9/bin/alembic upgrade head`

### Error: "password authentication failed"
- Your DATABASE_URL has the wrong credentials
- Get fresh credentials from Railway dashboard

---

## Next Steps After Database Setup

Once your database is working:

1. **Create Authentication System** (`app/auth.py`)
   - Registration route
   - Login route
   - Password reset

2. **Update web_app.py**
   - Add Flask-Login setup
   - Protect routes with `@login_required`
   - Add per-user OAuth handling

3. **Migrate from config.json to Database**
   - Move categories to `email_categories` table
   - Move settings to `user_settings` table
   - Delete `config.json`

4. **Test Multi-User Functionality**
   - Create 2-3 test users
   - Ensure data isolation
   - Test Gmail OAuth per-user

---

## Database Schema Overview

**Users Table:**
- Stores user accounts (email, password, subscription tier)
- Tracks trial expiration
- Onboarding progress

**Gmail Credentials Table:**
- Encrypted OAuth tokens per user
- Multiple Gmail accounts per user supported
- Automatic token refresh

**Subscriptions Table:**
- Stripe customer/subscription tracking
- Billing cycle management
- Cancellation handling

**Processing History:**
- Track all email operations
- Usage analytics
- AI API usage tracking

**User Settings:**
- Email notification preferences
- Default retention policies
- Custom categories
- Timezone/language

**Retention Policies:**
- Per-user auto-deletion rules
- Category-specific policies
- Whitelist management

All relationships are properly set up with cascading deletes for data integrity.

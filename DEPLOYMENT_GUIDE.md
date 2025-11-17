# GetMailZen Deployment Guide
## Deploy to Railway with Custom Domain (getmailzen.com)

---

## Prerequisites Checklist

- ✅ Railway account with PostgreSQL database already set up
- ✅ Domain: **getmailzen.com** (owned and ready)
- ✅ Google Cloud Console OAuth credentials (`credentials.json`)
- ✅ Environment variables ready (from `.env`)

---

## Part 1: Update Google OAuth for Production

### Step 1: Add Production Redirect URI

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Select your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", **add both**:
   ```
   https://getmailzen.com/gmail-oauth-callback
   http://localhost:5000/gmail-oauth-callback
   ```
   (Keep localhost for local testing)

4. Click **Save**

---

## Part 2: Deploy to Railway

### Step 1: Initialize Git Repository (if not already done)

```bash
cd /Users/scottymker/gmail-agent
git init
git add .
git commit -m "Initial commit - GetMailZen production ready"
```

### Step 2: Create New Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. If your repo isn't on GitHub yet:
   - Create a new GitHub repo: **getmailzen**
   - Push your code:
     ```bash
     git remote add origin https://github.com/YOUR_USERNAME/getmailzen.git
     git branch -M main
     git push -u origin main
     ```

5. In Railway, select your **getmailzen** repository
6. Railway will auto-detect it's a Python app

### Step 3: Link Existing PostgreSQL Database

1. In your new Railway project, click **"+ New"**
2. Select **"Database" → "Add PostgreSQL"** (if you don't have one)
3. Or link your existing database:
   - Click on your web service
   - Go to **"Variables"** tab
   - Railway should auto-connect to your existing Postgres

### Step 4: Configure Environment Variables

In Railway project → **Variables** tab, add these:

```bash
# Database (should already be set by Railway)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Security Keys (use your actual values from .env)
ENCRYPTION_KEY=8xK7vP2mQ9nR1sT6uV3wX4yZ5aB8cD9eF0gH1iJ2kL3=
FLASK_SECRET_KEY=f63507915fd5b76df9cf1e9b900f0b67223cc0109e596777e9fce578c1dcb377

# API Keys
ANTHROPIC_API_KEY=<your-anthropic-api-key>

# Production Settings
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
```

**IMPORTANT:** DO NOT paste `credentials.json` content as an environment variable. We'll handle this differently.

### Step 5: Add Google OAuth Credentials to Railway

Since `credentials.json` can't be in the repo (security), we need to add it via Railway's file system:

**Option A: Use Railway CLI (Recommended)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Add credentials file
railway run --  bash -c "cat > credentials.json << 'EOF'
$(cat credentials.json)
EOF"
```

**Option B: Add via Web UI**
1. In Railway, go to your service
2. Click **"Settings"** → **"Deploy"**
3. Under **"Build Command"**, add:
   ```bash
   echo '$GOOGLE_CREDENTIALS_JSON' > credentials.json && pip install -r requirements.txt
   ```
4. In **Variables**, add:
   ```
   GOOGLE_CREDENTIALS_JSON=<paste entire credentials.json content>
   ```

### Step 6: Run Database Migrations

In Railway → **"Deploy"** tab → **"Deploy Logs"**, once deployed, run:

```bash
railway run alembic upgrade head
```

Or add this to your railway.json build process (already configured).

---

## Part 3: Configure Custom Domain

### Step 1: Add Domain in Railway

1. In Railway project → Click your web service
2. Go to **"Settings"** tab
3. Scroll to **"Domains"** section
4. Click **"+ Custom Domain"**
5. Enter: **getmailzen.com**
6. Railway will show you DNS records to configure

### Step 2: Configure DNS at Your Domain Registrar

Railway will provide either:

**Option A: CNAME Record (Preferred)**
```
Type: CNAME
Name: @  (or blank for root domain)
Value: <your-railway-app>.up.railway.app
TTL: 3600
```

**Option B: A Record**
```
Type: A
Name: @
Value: <Railway IP address>
TTL: 3600
```

**For www subdomain (recommended):**
```
Type: CNAME
Name: www
Value: <your-railway-app>.up.railway.app
TTL: 3600
```

### Step 3: Enable SSL (Automatic)

Railway automatically provisions SSL certificates via Let's Encrypt once DNS is configured. This takes 5-15 minutes after DNS propagates.

---

## Part 4: Post-Deployment Setup

### Step 1: Verify Deployment

1. Visit **https://getmailzen.com**
2. You should see the GetMailZen login page
3. Test registration:
   ```
   Email: test@example.com
   Password: TestPass123
   ```

### Step 2: Test Gmail OAuth Flow

1. Register/Login to GetMailZen
2. Go to **Settings** tab
3. Click **"Connect Gmail Account"**
4. Should redirect to Google OAuth
5. Approve access
6. Should redirect back to **https://getmailzen.com/dashboard**
7. Gmail account should show as connected

### Step 3: Verify Database Connection

In Railway → **Deploy Logs**, check for:
```
Database connection successful!
```

If you see connection errors, verify DATABASE_URL is set correctly.

### Step 4: Test Email Processing

1. In dashboard, go to **"Process Emails"** tab
2. Click **"Start Processing"**
3. Should fetch emails from your connected Gmail
4. Check logs for any errors

---

## Part 5: Monitoring & Logs

### View Logs in Railway

1. Go to your Railway project
2. Click on your web service
3. Go to **"Deployments"** tab
4. Click latest deployment
5. View real-time logs

### Common Issues

**Issue: "No module named 'app'"**
- Solution: Ensure `web_app.py` is in root directory
- Check Procfile: `web: gunicorn web_app:app`

**Issue: "Database connection failed"**
- Solution: Verify DATABASE_URL in environment variables
- Check Railway Postgres is linked

**Issue: "OAuth state mismatch"**
- Solution: Verify redirect URI in Google Cloud Console matches:
  `https://getmailzen.com/gmail-oauth-callback`

**Issue: "credentials.json not found"**
- Solution: Re-run credentials setup from Step 5 above

**Issue: "Port already in use"**
- Solution: Railway handles port automatically via `$PORT` variable
- Don't hardcode port 5000 in production

---

## Part 6: Production Checklist

### Security
- ✅ `.env` file NOT in git repository
- ✅ `credentials.json` NOT in git repository
- ✅ HTTPS enabled (Railway auto-SSL)
- ✅ FLASK_DEBUG=False in production
- ✅ Strong FLASK_SECRET_KEY and ENCRYPTION_KEY
- ✅ Database credentials encrypted

### Performance
- ✅ Gunicorn with 4 workers (adjust based on traffic)
- ✅ Database connection pooling enabled (SQLAlchemy)
- ✅ Static files served efficiently

### Functionality
- ✅ User registration works
- ✅ User login works
- ✅ Gmail OAuth connection works
- ✅ Email processing works
- ✅ Token auto-refresh works
- ✅ Multiple users can use the app simultaneously

---

## Part 7: Scaling & Optimization (Optional)

### Enable Redis Caching (Future)

1. In Railway, add **Redis** service
2. Update environment variables:
   ```
   REDIS_URL=${{Redis.REDIS_URL}}
   ```
3. Implement caching in `web_app.py`

### Increase Workers for High Traffic

Edit `Procfile`:
```
web: gunicorn web_app:app --bind 0.0.0.0:$PORT --workers 8 --timeout 120
```

### Enable Database Backups

1. Railway → Postgres service → **"Settings"**
2. Enable **"Automated Backups"**
3. Set backup retention period

---

## Quick Reference: Railway Commands

```bash
# View logs
railway logs

# Run migrations
railway run alembic upgrade head

# Open shell in production
railway shell

# Connect to production database
railway run psql $DATABASE_URL

# Check environment variables
railway variables

# Deploy latest changes
git push origin main
# (Railway auto-deploys on push)
```

---

## Support

If you encounter issues:

1. Check Railway logs: `railway logs`
2. Verify environment variables: `railway variables`
3. Test database connection: `railway run python3 -c "from app.database import test_connection; test_connection()"`
4. Check Google OAuth settings in Cloud Console

---

**Your GetMailZen app should now be live at https://getmailzen.com!** 🎉


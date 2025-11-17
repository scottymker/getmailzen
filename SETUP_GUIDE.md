# Gmail Agent - Step-by-Step Setup Guide

Follow these steps to get your Gmail automation agent up and running.

## Prerequisites

- Python 3.9 or higher
- Gmail account
- Web browser
- Internet connection

## Step 1: Install Dependencies

```bash
cd gmail-agent
pip3 install -r requirements.txt
```

This will install:
- Google Gmail API libraries
- Anthropic Claude SDK
- Flask web framework
- Other utilities

**Expected time**: 2-3 minutes

## Step 2: Set Up Gmail API Access

### 2.1 Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" at the top
3. Click "New Project"
4. Name it "Gmail Agent" (or any name you prefer)
5. Click "Create"
6. Wait for project creation (about 10 seconds)

### 2.2 Enable Gmail API

1. In the Google Cloud Console, click the hamburger menu (☰)
2. Navigate to "APIs & Services" → "Library"
3. Search for "Gmail API"
4. Click on "Gmail API" in results
5. Click the blue "Enable" button
6. Wait for it to enable (about 5 seconds)

### 2.3 Create OAuth Credentials

1. In Google Cloud Console, go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" at the top
3. Select "OAuth client ID"
4. If prompted, configure OAuth consent screen:
   - Choose "External" user type
   - Fill in app name: "Gmail Agent"
   - Add your email as developer contact
   - Click "Save and Continue" through the steps
5. Back at "Create OAuth client ID":
   - Application type: **Desktop app**
   - Name: "Gmail Agent Desktop"
   - Click "Create"
6. A popup shows your credentials - click "Download JSON"
7. Save the file as `credentials.json` in the `gmail-agent` folder

**Important**: Keep `credentials.json` secure - it allows access to your Gmail!

## Step 3: Get Claude API Key

### 3.1 Sign Up for Anthropic

1. Go to https://console.anthropic.com/
2. Sign up or log in with your account
3. Add payment method (required for API access)
   - Claude charges per usage: ~$0.003 per email
   - Set a reasonable budget limit (e.g., $10/month)

### 3.2 Generate API Key

1. In Anthropic Console, go to "API Keys"
2. Click "Create Key"
3. Name it "Gmail Agent"
4. Copy the key (starts with `sk-ant-...`)
5. **Save it immediately** - you won't see it again!

## Step 4: Configure Environment Variables

```bash
# Create .env file from template
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

Add your Claude API key:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Save and close (in nano: Ctrl+X, then Y, then Enter)

## Step 5: Verify File Structure

Your `gmail-agent` folder should now contain:

```
✓ credentials.json  (Gmail OAuth - YOU created this)
✓ .env              (Claude API key - YOU created this)
✓ requirements.txt  (Python packages)
✓ web_app.py        (Main application)
✓ config.json       (Email categories)
✓ app/              (Code modules)
✓ templates/        (Web interface)
```

## Step 6: First Run

```bash
python3 web_app.py
```

**What happens**:
1. App starts Flask server
2. You'll see: "Access the dashboard at: http://localhost:5000"
3. Your browser will automatically open for Gmail authentication (first time only)

### 6.1 Gmail Authentication Flow

1. Browser opens to Google sign-in
2. Select your Gmail account
3. You'll see: "Google hasn't verified this app"
   - Click "Advanced"
   - Click "Go to Gmail Agent (unsafe)" - this is YOUR app, it's safe!
4. Review permissions:
   - Read, compose, send, and permanently delete email
   - Manage labels
   - These are needed for the agent to work
5. Click "Allow"
6. See "The authentication flow has completed"
7. Close that browser tab

**First-time only**: A `token.json` file is created - this saves your authentication so you won't need to sign in again.

## Step 7: Access the Dashboard

1. Open browser to: http://localhost:5000
2. You should see the Gmail Agent Dashboard
3. Click "Test Connection" to verify everything works

### Expected result:
```
✓ Successfully connected to Gmail and Claude API!
```

## Step 8: Test Email Processing (Dry Run)

**IMPORTANT**: First run should ALWAYS be in dry-run mode!

1. Ensure "Dry Run" checkbox is ✓ checked
2. Set "Maximum Emails" to 10 (start small)
3. Keep query as "Unread emails only"
4. Click "Process Emails"

**What happens**:
- Fetches 10 unread emails
- AI analyzes each one
- Shows what WOULD happen (but doesn't do it)
- Displays results with categories, priorities, and recommended actions

**Review the results**:
- Do the categories make sense?
- Are the actions appropriate?
- Is the AI making good decisions?

## Step 9: First Real Processing

Once you're comfortable with dry-run results:

1. **Uncheck** "Dry Run" checkbox
2. Process just 5-10 emails first
3. Click "Process Emails"
4. Check your Gmail to verify actions were performed correctly

## Step 10: Customize Categories (Optional)

Edit `config.json` to customize for your needs:

```json
{
  "categories": [
    {
      "name": "Work",
      "description": "Emails from my company domain or work-related topics"
    },
    {
      "name": "Family",
      "description": "Emails from family members"
    }
  ]
}
```

Or use the **"AI Suggest Categories"** button to let Claude analyze your inbox and suggest categories!

## Ongoing Usage

### Daily Workflow

1. Start the app: `python3 web_app.py`
2. Open dashboard: http://localhost:5000
3. Click "Process Emails" whenever you want to organize
4. Review results in the dashboard

### Automated Scheduling (Advanced)

To run automatically every hour:

```bash
# Add to crontab (Mac/Linux)
crontab -e

# Add this line:
0 * * * * cd /Users/scottymker/gmail-agent && python3 -c "from app.email_processor import EmailProcessor; EmailProcessor().process_inbox(dry_run=False)"
```

## Troubleshooting

### Error: "credentials.json not found"
→ Download OAuth credentials from Google Cloud Console (Step 2.3)

### Error: "ANTHROPIC_API_KEY not found"
→ Create `.env` file with your API key (Step 4)

### Browser doesn't open for Gmail auth
→ Copy the URL from terminal and paste into browser manually

### "This app isn't verified by Google"
→ Click "Advanced" → "Go to Gmail Agent (unsafe)" - it's your own app!

### No emails being processed
→ Check you have unread emails matching your query filter

### Actions not executing
→ Uncheck "Dry Run" mode in the dashboard

## Security Tips

1. **Never commit these files to git**:
   - `.env` (your API keys)
   - `credentials.json` (Gmail OAuth)
   - `token.json` (access token)

   These are already in `.gitignore`

2. **Protect your API keys**:
   - Don't share screenshots showing keys
   - Regenerate if accidentally exposed
   - Set spending limits in Anthropic Console

3. **Review permissions**:
   - The app can delete emails - use dry-run mode first!
   - Start with small batches
   - Monitor the AI's decisions

## Cost Monitoring

Check your usage:
- **Claude API**: https://console.anthropic.com/ → "Usage"
- **Gmail API**: https://console.cloud.google.com/ → "APIs & Services" → "Dashboard"

Expected costs for personal use:
- 100 emails/day × 30 days = 3,000 emails/month
- 3,000 × $0.003 = **~$9/month** for Claude API
- Gmail API: **$0** (free for personal use)

## Next Steps

1. Run daily email processing to keep inbox organized
2. Customize categories for your needs
3. Experiment with different Gmail queries
4. Monitor AI accuracy and adjust categories as needed
5. Set up automated scheduling (optional)

## Questions or Issues?

1. Check README.md for detailed documentation
2. Review code comments in `app/` folder
3. Check Gmail API docs: https://developers.google.com/gmail/api
4. Check Claude API docs: https://docs.anthropic.com/

---

**You're all set!** Your Gmail Agent is ready to intelligently organize your inbox. Start with dry-run mode and small batches, then scale up as you get comfortable.

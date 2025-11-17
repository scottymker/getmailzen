# Gmail Agent Dashboard - Quick Start Guide

## Getting Started in 3 Steps

### Step 1: Start the Server
```bash
cd /Users/scottymker/gmail-agent
python3 web_app.py
```

You should see:
```
============================================================
Gmail Agent Web Interface
============================================================

Starting server...
Access the dashboard at: http://localhost:5000

Press Ctrl+C to stop the server
============================================================
```

### Step 2: Open the Dashboard

Open your web browser and navigate to:
```
http://localhost:5000/dashboard
```

### Step 3: Explore the Features

The dashboard has 4 main tabs:

## 1. HOME TAB - Your Inbox Overview

**What you'll see:**
- A large circular health score (0-100) with a letter grade
- Your inbox health metrics (total emails, unread count, storage, age)
- AI-powered "Attention Needed" suggestions

**What to do first:**
1. Click "Refresh Score" to analyze your inbox
2. Review your health score and grade
3. Click "Get AI Suggestions" for personalized recommendations
4. Use the quick action buttons on each suggestion

**Understanding Your Score:**
- 90-100 (A) = Excellent
- 80-89 (B) = Good
- 70-79 (C) = Average
- 60-69 (D) = Needs Work
- Below 60 (F) = Critical

## 2. PROCESS EMAILS TAB - AI-Powered Automation

**What you'll see:**
- Settings to control how emails are processed
- A "Dry Run" checkbox (highly recommended for first use)
- Progress bar during processing
- Beautiful results display with statistics

**What to do first:**
1. Keep "Dry Run Mode" CHECKED (this is safe mode)
2. Set "Maximum Emails" to 10-20 for testing
3. Choose "Unread emails only" filter
4. Click "Start Processing"
5. Watch the progress bar
6. Review the results

**Settings Explained:**
- **Maximum Emails**: How many to process (start small!)
- **Filter Query**: Which emails to process
- **Dry Run**: Preview mode (no actual changes made)

**When to disable Dry Run:**
- After you're comfortable with the results
- When you trust the AI categorization
- For production use

## 3. CLEANUP TOOLS TAB - Advanced Management

### Feature 1: Email Retention Policy

**What it does:**
Automatically finds and deletes old emails to free up space

**How to use:**
1. Move the slider to select age (e.g., 6 months)
2. Optionally choose a category to filter
3. Click "Analyze Old Emails" to see what would be deleted
4. Review the results
5. Click "Delete Old Emails" to execute (requires confirmation)

**Safety tip:** Always analyze before deleting!

### Feature 2: Protected Senders Whitelist

**What it does:**
Protects important emails from automatic deletion

**How to use:**
1. Type an email address (e.g., boss@company.com)
2. Click "Add"
3. That sender is now protected forever

**Who to add:**
- Your boss
- Family members
- Important vendors
- Financial institutions
- Government agencies

### Feature 3: Unsubscribe Opportunities

**What it does:**
Finds newsletters you can unsubscribe from

**How to use:**
1. Click "Scan for Subscriptions"
2. Wait for AI analysis
3. Review the list of newsletters
4. Click "Unsubscribe" on unwanted ones
5. You'll be taken to the unsubscribe page

**When to use:**
- When inbox feels cluttered
- To reduce daily email volume
- Monthly maintenance routine

### Feature 4: Duplicate Detection

**What it does:**
Finds and removes duplicate emails

**How to use:**
1. Click "Scan for Duplicates"
2. Review the duplicate sets found
3. Click "Delete Duplicates" on each set
4. Confirm the deletion

**When to use:**
- After importing emails
- Quarterly maintenance
- When storage is full

## 4. SETTINGS TAB - Configuration

**What you'll see:**
- Default processing settings
- All configured email categories
- Category actions and descriptions

**What to do:**
1. Review the existing categories
2. Adjust default settings to your preferences
3. Click "Save Settings"

## First-Time User Workflow

### Day 1: Initial Setup
1. Start server and open dashboard
2. Check connection status (top right)
3. Review Home tab health score
4. Read smart suggestions

### Day 2: Test Processing (Dry Run)
1. Go to Process Emails tab
2. Enable Dry Run mode
3. Process 10-20 emails
4. Review how AI categorizes them
5. Repeat until comfortable

### Day 3: Live Processing
1. Disable Dry Run mode
2. Process larger batches (50-100 emails)
3. Monitor results
4. Adjust categories if needed

### Week 2: Cleanup
1. Use retention policy to analyze old emails
2. Add important senders to whitelist
3. Scan for unsubscribe opportunities
4. Remove duplicates

### Monthly: Maintenance
1. Check health score
2. Review smart suggestions
3. Process any unread emails
4. Clean up old emails
5. Scan for new subscriptions

## Tips for Success

### For Non-Technical Users
- Always use Dry Run first
- Start with small batches
- Read the tooltips (? icons)
- Check connection status before starting
- Review results carefully

### For Power Users
- Create custom Gmail queries
- Use category filters in cleanup
- Maintain a comprehensive whitelist
- Schedule regular maintenance
- Adjust retention policies per category

### Best Practices
- Run health analysis weekly
- Process emails daily
- Clean up monthly
- Review subscriptions monthly
- Update whitelist as needed

## Common Questions

### Q: Is it safe to use?
**A:** Yes! Dry Run mode lets you preview everything first. Nothing happens until you confirm.

### Q: Will it delete important emails?
**A:** No, if you use the whitelist feature. Add important senders to the whitelist and they're protected forever.

### Q: How often should I use it?
**A:** Daily for processing, weekly for health checks, monthly for cleanup.

### Q: What if I don't like the AI's decisions?
**A:** Use Dry Run mode to preview first. You can adjust categories in Settings.

### Q: Can I undo deletions?
**A:** Gmail has a trash folder where deleted emails stay for 30 days. Always check trash before permanent deletion.

### Q: Why is my health score low?
**A:** Common reasons:
- Too many unread emails
- Lots of old emails taking up space
- Poor organization/labeling
- Many subscriptions

## Visual Guide

### Connection Status (Top Right)
- Green dot = Connected
- Red dot = Disconnected
- If disconnected, click "Refresh" button

### Color Coding
- **Green** = Good/Success
- **Yellow** = Warning/Medium
- **Red** = Danger/High Priority
- **Blue** = Info/Normal
- **Purple** = Category/Special

### Buttons
- **Primary (Purple)** = Main actions
- **Secondary (Gray)** = Helper actions
- **Success (Green)** = Positive actions
- **Danger (Red)** = Destructive actions (require confirmation)
- **Warning (Yellow)** = Caution actions

## Keyboard Shortcuts

Currently none, but you can use:
- Tab to navigate between fields
- Enter to submit forms
- Esc to close modals (when implemented)

## Mobile Usage

The dashboard is fully responsive! On mobile:
- Tabs stack vertically
- Cards adjust to screen width
- Touch-friendly buttons
- Swipe-friendly scrolling

## Getting Help

### Check These First
1. Connection status indicator
2. Browser console (F12)
3. Flask server logs
4. .env file configuration

### Error Messages
- Look for red alert boxes
- Read the error message carefully
- Check connection status
- Try refreshing the page

### Still Stuck?
- Check the main DASHBOARD_README.md for technical details
- Review Flask server output
- Verify Gmail API credentials
- Test with smaller batches

## Advanced Features (Future)

Coming soon:
- Email preview pane
- Bulk selection checkboxes
- Custom category builder UI
- Scheduled automation
- Dark mode
- Multi-account support

---

**You're all set!** Start with the Home tab, check your health score, and take it from there. Remember: Dry Run mode is your friend!

**Generated with Claude Code**

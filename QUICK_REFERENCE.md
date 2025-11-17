# Gmail Agent Dashboard - Quick Reference Card

## Start the Server
```bash
cd /Users/scottymker/gmail-agent
python3 web_app.py
```

## Access URLs
- **New Dashboard**: http://localhost:5000/dashboard
- **Classic Dashboard**: http://localhost:5000/

## Tab Overview

### 🏠 HOME
- **Health Score**: See how organized your inbox is (0-100, A-F)
- **Smart Suggestions**: Get AI recommendations
- **Quick Stats**: Total emails, unread, storage, age

### ⚡ PROCESS EMAILS
- **Settings**: Max emails (1-500), query filter, dry run mode
- **Actions**: Process emails, suggest categories
- **Results**: See what AI did with each email

### 🧹 CLEANUP TOOLS
- **Retention**: Delete emails older than X months
- **Whitelist**: Protect important senders
- **Unsubscribe**: Find and leave newsletters
- **Duplicates**: Remove duplicate emails

### ⚙️ SETTINGS
- **Defaults**: Set your preferences
- **Categories**: View email categories

## Safety Checklist

✅ Always enable "Dry Run" first
✅ Check connection status (top right)
✅ Start with small batches (10-20 emails)
✅ Add important senders to whitelist
✅ Analyze before deleting
✅ Review AI suggestions before executing

## First-Time Workflow

1. **Start server** → `python3 web_app.py`
2. **Open browser** → http://localhost:5000/dashboard
3. **Check connection** → Green dot = good
4. **View health** → Home tab → "Refresh Score"
5. **Test processing** → Process tab → Dry Run ON → 10 emails
6. **Review results** → Check what AI did
7. **Go live** → Dry Run OFF → Larger batches

## Common Tasks

### Check Inbox Health
Home tab → "Refresh Score"

### Process Unread Emails
Process tab → "Unread emails only" → "Start Processing"

### Delete Old Emails
Cleanup tab → Set months → "Analyze" → "Delete"

### Protect a Sender
Cleanup tab → Whitelist → Type email → "Add"

### Find Subscriptions
Cleanup tab → Unsubscribe → "Scan for Subscriptions"

### Remove Duplicates
Cleanup tab → Duplicates → "Scan for Duplicates"

## Color Guide

- **Purple** = Primary actions
- **Green** = Success/Good
- **Yellow** = Warning/Medium
- **Red** = Danger/Delete
- **Blue** = Info/Normal

## Health Score Guide

- **90-100 (A)** = Excellent
- **80-89 (B)** = Good
- **70-79 (C)** = Average
- **60-69 (D)** = Needs Work
- **Below 60 (F)** = Critical

## Tooltips

Every [?] icon has helpful information. Hover over them!

## Documentation

- **Quick Start**: DASHBOARD_QUICKSTART.md
- **Full Docs**: DASHBOARD_README.md
- **Features**: DASHBOARD_FEATURES.md
- **Summary**: NEW_DASHBOARD_SUMMARY.md

## Troubleshooting

**Connection Failed**
→ Check .env file, verify Gmail/Claude API keys

**Health Score Not Loading**
→ Click "Refresh", check connection status

**Processing Slow**
→ Reduce max emails, check internet connection

**No Suggestions**
→ Need more emails to analyze, check Claude API

## Support

1. Check browser console (F12)
2. Review Flask logs
3. Verify .env configuration
4. Test with dry run mode

## Quick Tips

- Use tooltips ([?] icons) for help
- Always start with dry run
- Process daily, cleanup monthly
- Maintain whitelist of important senders
- Review suggestions regularly

---

**Print this card and keep it handy!**

Generated with Claude Code

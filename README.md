# GetMailZen

**AI-Powered Email Management SaaS**

GetMailZen is a multi-user SaaS platform that uses Claude AI to automatically categorize, organize, and manage Gmail inboxes. Built with Flask, PostgreSQL, and Railway deployment ready.

## Features

- **AI-Powered Categorization**: Uses Claude API to intelligently categorize emails
- **Automatic Actions**: Label, archive, delete, and star emails based on AI analysis
- **Web Dashboard**: Clean, modern interface to manage and trigger email processing
- **Smart Categories**: AI suggests custom categories based on your inbox
- **Dry Run Mode**: Preview actions before executing them
- **Flexible Filtering**: Process all emails, unread only, or custom Gmail queries

## Quick Start

### 1. Install Dependencies

```bash
cd gmail-agent
pip3 install -r requirements.txt
```

### 2. Set Up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials JSON file
5. Save the downloaded file as `credentials.json` in the `gmail-agent` directory

### 3. Get Claude API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Generate an API key
4. Copy the API key

### 4. Configure Environment

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your Claude API key
# ANTHROPIC_API_KEY=your-api-key-here
```

### 5. Run the Web Interface

```bash
python3 web_app.py
```

Open your browser to `http://localhost:5000`

### 6. First Run - Gmail Authentication

On first run, the app will:
1. Open your browser for Gmail OAuth authentication
2. Ask you to grant permissions to the app
3. Save a `token.json` file for future use (no re-authentication needed)

## Usage

### Web Dashboard

The web interface provides:

1. **Process Emails Button**: Analyze and organize emails using AI
2. **Test Connection**: Verify Gmail and Claude API are working
3. **AI Suggest Categories**: Let AI analyze your inbox and suggest custom categories

### Configuration Options

- **Max Emails**: How many emails to process at once (1-500)
- **Query Filter**: Gmail search query (e.g., "is:unread", "from:example.com")
- **Dry Run**: Preview actions without actually executing them (recommended for first use)

### Customizing Categories

Edit `config.json` to customize email categories:

```json
{
  "categories": [
    {
      "name": "Newsletter",
      "description": "Marketing emails and subscriptions"
    }
  ],
  "processing_settings": {
    "max_emails": 50,
    "query": "is:unread",
    "dry_run": true
  }
}
```

## How It Works

1. **Fetch Emails**: Connects to Gmail API and fetches emails based on your query
2. **AI Analysis**: Sends email details to Claude AI for categorization
3. **Smart Actions**: Claude determines:
   - Which category the email belongs to
   - What actions to take (label, archive, delete, star)
   - Priority level (high/medium/low)
   - Confidence in the decision
4. **Execute**: Performs actions via Gmail API (unless in dry-run mode)
5. **Report**: Shows results in the web dashboard

## Actions

The AI can recommend these actions:

- `label:<name>` - Apply a Gmail label (creates if doesn't exist)
- `archive` - Remove from inbox (still accessible in "All Mail")
- `delete` - Permanently delete the email
- `star` - Flag as important
- `unstar` - Remove star
- `mark_read` / `mark_unread` - Change read status (coming soon)

## API Costs

### Claude API (Anthropic)
- Model: Claude 3.5 Sonnet
- Cost: ~$0.003 per email analyzed
- 50 emails ≈ $0.15
- 1000 emails ≈ $3.00

### Gmail API (Google)
- **Free** for personal use
- No costs for reading/modifying your own emails

## Security & Privacy

- **API Keys**: Stored in `.env` file (git-ignored)
- **Gmail OAuth**: Uses official Google OAuth 2.0 (no password storage)
- **Local Processing**: All data processing happens locally
- **Token Storage**: Gmail access token saved in `token.json` (git-ignored)
- **AI Privacy**: Email content sent to Claude API for analysis (review Anthropic's privacy policy)

## File Structure

```
gmail-agent/
├── app/
│   ├── __init__.py
│   ├── gmail_service.py      # Gmail API integration
│   ├── ai_categorizer.py     # Claude AI categorization
│   └── email_processor.py    # Main processing logic
├── templates/
│   └── index.html             # Web dashboard
├── web_app.py                 # Flask web server
├── config.json                # Category configuration
├── requirements.txt           # Python dependencies
├── .env                       # API keys (create this)
├── .env.example               # Template for .env
├── credentials.json           # Gmail OAuth credentials (create this)
├── token.json                 # Gmail access token (auto-generated)
└── README.md                  # This file
```

## Troubleshooting

### "credentials.json not found"
- Download OAuth credentials from Google Cloud Console
- Save as `credentials.json` in project root

### "ANTHROPIC_API_KEY not found"
- Create `.env` file from `.env.example`
- Add your Claude API key

### "Gmail API not enabled"
- Go to Google Cloud Console
- Enable Gmail API for your project

### Emails not being processed
- Check "Dry Run" is unchecked to execute actions
- Verify query filter matches emails you want to process
- Check Gmail API quotas in Google Cloud Console

## Advanced Usage

### Command Line Processing

You can also run processing directly from Python:

```python
from app.email_processor import EmailProcessor

processor = EmailProcessor()
results = processor.process_inbox(
    max_emails=50,
    query='is:unread',
    dry_run=True
)
print(results)
```

### Custom Gmail Queries

Use Gmail's search syntax:

- `is:unread` - Unread emails
- `from:example.com` - From specific sender
- `subject:invoice` - Emails with "invoice" in subject
- `newer_than:7d` - From last 7 days
- `category:promotions` - Gmail's promotion category
- `has:attachment` - Emails with attachments

Combine with AND/OR:
- `from:amazon.com OR from:ebay.com`
- `is:unread newer_than:30d`

## Roadmap

- [ ] Email scheduling (run automatically on schedule)
- [ ] Advanced rule builder in web UI
- [ ] Email templates and auto-replies
- [ ] Analytics and reporting
- [ ] Multiple inbox support
- [ ] Chrome extension for one-click processing

## License

MIT License - feel free to use and modify for personal or commercial use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Gmail API documentation
3. Review Claude API documentation
4. Check the code comments for implementation details

## Credits

Built with:
- **Flask** - Web framework
- **Google Gmail API** - Email access
- **Anthropic Claude** - AI categorization
- **Python** - Backend logic

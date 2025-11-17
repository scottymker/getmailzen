# Gmail Agent - Modern Dashboard

A completely redesigned, user-friendly dashboard for the Gmail Agent with AI-powered email management features.

## Overview

The new dashboard provides a modern, intuitive interface for managing your Gmail inbox with artificial intelligence. It features a tabbed interface with four main sections and includes visual health scoring, smart suggestions, and powerful cleanup tools.

## Accessing the Dashboard

Start the Flask server:
```bash
python3 web_app.py
```

Then navigate to:
- **New Dashboard**: http://localhost:5000/dashboard
- **Classic Dashboard**: http://localhost:5000/

## Features

### 1. Home Tab - Inbox Overview

**Inbox Health Score**
- Large circular progress chart showing your inbox health (0-100)
- Color-coded grade (A-F) based on organization quality
- AI-powered analysis of inbox cleanliness
- Key metrics display:
  - Total emails count
  - Unread emails count
  - Storage used
  - Inbox age (oldest email)

**Smart Suggestions**
- AI-generated recommendations for inbox improvement
- "Attention Needed" section with actionable suggestions
- Quick action buttons for each suggestion
- Real-time updates based on inbox analysis

### 2. Process Emails Tab - AI Email Processing

**Enhanced Email Processing**
- Visual progress bars during processing
- Configurable batch size (1-500 emails)
- Gmail query filters:
  - Unread emails only
  - All emails
  - Unread from last 7 days
  - Promotions category
  - Social category
- Dry run mode for safe previewing
- AI-powered category suggestions

**Results Display**
- Beautiful card-based results layout
- Color-coded priority badges (high/medium/low)
- Confidence scores for AI decisions
- Action tracking (labeled, archived, starred, deleted)
- AI reasoning explanations

**Statistics Dashboard**
- Real-time processing stats
- Total emails processed
- Actions breakdown by type
- Visual stat cards

### 3. Cleanup Tools Tab - Advanced Management

**Email Retention Policy**
- Visual slider for retention period (3-24 months)
- Category-specific filtering
- Analysis before deletion
- Protected sender whitelist
- Dry run analysis

**Whitelist Management**
- Add/remove protected email addresses
- Emails from whitelisted senders never auto-deleted
- Visual list management interface

**Unsubscribe Opportunities**
- AI detection of newsletter subscriptions
- Display subscription frequency
- Direct unsubscribe links
- Last received date tracking

**Duplicate Detection**
- Scan for duplicate emails
- Group duplicates by subject/content
- Bulk deletion options
- Storage savings estimates

### 4. Settings Tab - Configuration

**Processing Defaults**
- Default maximum emails per batch
- Default query filter
- Dry run preferences
- Auto-save to localStorage

**Category Management**
- View all configured categories
- See category descriptions
- Review assigned actions
- AI-suggested categories

## Design Features

### User Experience
- **Mobile Responsive**: Works on all screen sizes
- **Tooltips**: Help icons explain every feature
- **Loading States**: Spinners and progress indicators
- **Smooth Animations**: Fade-ins, slides, hover effects
- **Color Coding**: Visual indicators for status/priority

### Visual Design
- **Purple Gradient Theme**: Consistent with existing branding
- **Card-Based Layout**: Modern, clean organization
- **Icon-Rich Interface**: Visual clarity for actions
- **Chart Visualizations**: Chart.js for health score

### Safety Features
- **Confirmation Dialogs**: For destructive actions
- **Dry Run Mode**: Preview before executing
- **Success/Error Messages**: Clear feedback
- **Connection Status**: Real-time API status indicator

## Technical Details

### Frontend Technologies
- Pure HTML5/CSS3/JavaScript (no framework dependencies)
- Chart.js 4.4.0 for visualizations (CDN)
- Modern CSS with Flexbox and Grid
- CSS Variables for easy theming
- LocalStorage for settings persistence

### API Integration
The dashboard connects to these backend endpoints:

**Core APIs**
- `/api/test-connection` - Test Gmail/Claude connectivity
- `/api/inbox-health` - Get inbox health score
- `/api/smart-suggestions` - Get AI suggestions
- `/api/process` - Process emails with AI
- `/api/suggest-categories` - AI category suggestions
- `/api/config` - Get/update configuration

**Cleanup APIs**
- `/api/retention/analyze` - Analyze old emails
- `/api/retention/delete` - Delete old emails
- `/api/unsubscribe-opportunities` - Find subscriptions
- `/api/duplicates` - Find duplicate emails

### Browser Compatibility
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Usage Examples

### Check Inbox Health
1. Navigate to Home tab
2. Click "Refresh Score"
3. View your health score and grade
4. Review key metrics

### Process Emails
1. Go to Process Emails tab
2. Set maximum emails to process
3. Choose a filter query
4. Enable/disable dry run
5. Click "Start Processing"
6. Watch progress bar
7. Review results and statistics

### Clean Up Old Emails
1. Open Cleanup Tools tab
2. Set retention period with slider
3. Choose optional category filter
4. Click "Analyze Old Emails"
5. Review analysis results
6. Click "Delete Old Emails" to execute
7. Confirm in popup dialog

### Add Protected Senders
1. Go to Cleanup Tools tab
2. Scroll to Whitelist section
3. Enter email address
4. Click "Add"
5. Email is now protected from auto-deletion

### Find Subscriptions
1. Open Cleanup Tools tab
2. Find "Unsubscribe Opportunities"
3. Click "Scan for Subscriptions"
4. Review list of newsletters
5. Click "Unsubscribe" on unwanted ones

## Customization

### Changing Colors
Edit CSS variables in the `<style>` section:
```css
:root {
    --primary-gradient-start: #667eea;  /* Change to your color */
    --primary-gradient-end: #764ba2;    /* Change to your color */
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
}
```

### Adjusting Health Score Thresholds
Modify the `updateHealthChart()` function:
```javascript
if (score >= 80) color = '#10b981'; // Green for 80+
else if (score >= 60) color = '#f59e0b'; // Yellow for 60+
else color = '#ef4444'; // Red for <60
```

### Adding New Tabs
1. Add tab button to `.tabs` section
2. Create new `.tab-content` div
3. Add `switchTab()` case for initialization
4. Implement tab-specific functions

## Tips for Non-Technical Users

### Understanding Health Score
- **90-100 (A)**: Excellent! Your inbox is well-organized
- **80-89 (B)**: Good organization with minor improvements needed
- **70-79 (C)**: Average - consider using cleanup tools
- **60-69 (D)**: Below average - take action on suggestions
- **Below 60 (F)**: Needs attention - use all available tools

### Using Dry Run Mode
Always enable "Dry Run" when:
- Testing new category configurations
- Processing emails for the first time
- Trying new query filters
- Making large-scale changes

### Safety Best Practices
1. Always analyze before deleting old emails
2. Maintain a whitelist of important senders
3. Review AI suggestions before executing
4. Check connection status before operations
5. Use dry run mode for testing

### Getting the Most Value
- Run health analysis weekly
- Review smart suggestions regularly
- Process unread emails daily
- Clean up old emails monthly
- Scan for duplicates quarterly
- Review subscriptions monthly

## Troubleshooting

### Health Score Not Loading
- Check connection status indicator
- Click "Refresh" button
- Verify Gmail API credentials in `.env`
- Check browser console for errors

### Processing Takes Too Long
- Reduce max emails per batch
- Use more specific query filters
- Check internet connection
- Verify Claude API quota

### No Suggestions Appearing
- Ensure you have enough emails to analyze
- Click "Get AI Suggestions" button
- Check that Claude API is connected
- Review browser console for errors

### Whitelist Not Saving
- Whitelist is session-based currently
- Implement persistent storage if needed
- Check browser localStorage support

## Future Enhancements

Potential features for future versions:
- Email preview pane
- Bulk action checkboxes
- Custom category creation UI
- Schedule automated cleanups
- Export/import settings
- Email threading visualization
- Attachment management
- Search functionality
- Dark mode toggle
- Multi-account support

## Support

For issues or questions:
1. Check browser console for errors
2. Verify API connections
3. Review Flask server logs
4. Check `.env` configuration
5. Test with dry run mode first

## File Location

Dashboard HTML: `/Users/scottymker/gmail-agent/templates/dashboard.html`
Web Server: `/Users/scottymker/gmail-agent/web_app.py`

---

**Generated with Claude Code**
Modern, user-friendly dashboard for intelligent Gmail management.

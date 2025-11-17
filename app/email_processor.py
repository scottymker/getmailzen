"""
Email Processor
Orchestrates Gmail service and AI categorization to process emails
"""
from app.gmail_service import GmailService
from app.ai_categorizer import EmailCategorizer


class EmailProcessor:
    """Main email processing engine"""

    def __init__(self, user_id=None, gmail_service=None, categorizer=None):
        """
        Initialize EmailProcessor

        Args:
            user_id (int, optional): User ID for per-user Gmail OAuth.
                                    If None, uses legacy file-based auth.
            gmail_service (GmailService, optional): Custom Gmail service instance
            categorizer (EmailCategorizer, optional): Custom AI categorizer instance
        """
        self.gmail = gmail_service or GmailService(user_id=user_id)
        self.ai = categorizer or EmailCategorizer()

    def process_inbox(self, max_emails=50, query='is:unread', categories=None, dry_run=False):
        """
        Process emails in inbox using AI categorization

        Args:
            max_emails: Maximum number of emails to process
            query: Gmail query to filter emails (default: unread emails)
            categories: List of category definitions (if None, uses defaults)
            dry_run: If True, don't actually perform actions, just return what would be done

        Returns:
            Dictionary with processing results and statistics
        """

        if categories is None:
            categories = self._get_default_categories()

        # Fetch emails
        print(f"Fetching emails with query: '{query}'...")
        messages = self.gmail.get_messages(max_results=max_emails, query=query)

        if not messages:
            return {
                'total': 0,
                'processed': 0,
                'results': [],
                'stats': {}
            }

        print(f"Found {len(messages)} emails to process")

        # Extract email details
        emails = []
        for msg in messages:
            details = self.gmail.get_message_details(msg)
            emails.append(details)

        # Categorize emails using AI
        print("Categorizing emails with AI...")
        categorizations = self.ai.batch_categorize(emails, categories)

        # Process actions
        results = []
        stats = {
            'labeled': 0,
            'archived': 0,
            'deleted': 0,
            'starred': 0,
            'errors': 0
        }

        for i, cat_result in enumerate(categorizations):
            email = emails[i]
            email_id = email['id']

            result = {
                'email_id': email_id,
                'subject': email['subject'],
                'sender': email['sender'],
                'category': cat_result['category'],
                'actions_taken': [],
                'actions_planned': cat_result['actions'],
                'reasoning': cat_result['reasoning'],
                'priority': cat_result['priority'],
                'confidence': cat_result['confidence']
            }

            # Execute actions
            if not dry_run:
                for action in cat_result['actions']:
                    success = self._execute_action(email_id, action)

                    if success:
                        result['actions_taken'].append(action)
                        self._update_stats(stats, action)
                    else:
                        stats['errors'] += 1
                        result['actions_taken'].append(f"{action} (FAILED)")
            else:
                result['actions_taken'] = ['DRY RUN - no actions performed']

            results.append(result)

        return {
            'total': len(messages),
            'processed': len(results),
            'results': results,
            'stats': stats,
            'dry_run': dry_run
        }

    def _execute_action(self, email_id, action):
        """Execute a single action on an email"""

        try:
            if action.startswith('label:'):
                label_name = action.split(':', 1)[1]
                return self.gmail.apply_label(email_id, label_name)

            elif action == 'archive':
                return self.gmail.archive_message(email_id)

            elif action == 'delete':
                return self.gmail.delete_message(email_id)

            elif action == 'star':
                return self.gmail.star_message(email_id)

            elif action == 'unstar':
                return self.gmail.unstar_message(email_id)

            elif action in ['mark_read', 'mark_unread']:
                # These would require additional Gmail API calls
                # For now, just log that we'd do it
                print(f"Action '{action}' not yet implemented")
                return False

            else:
                print(f"Unknown action: {action}")
                return False

        except Exception as e:
            print(f"Error executing action '{action}': {e}")
            return False

    def _update_stats(self, stats, action):
        """Update statistics based on action"""
        if action.startswith('label:'):
            stats['labeled'] += 1
        elif action == 'archive':
            stats['archived'] += 1
        elif action == 'delete':
            stats['deleted'] += 1
        elif action == 'star':
            stats['starred'] += 1

    def _get_default_categories(self):
        """Return default email categories"""
        return [
            {
                'name': 'Newsletters',
                'description': 'Marketing emails, newsletters, and subscriptions that are sent regularly'
            },
            {
                'name': 'Shopping',
                'description': 'E-commerce receipts, shipping notifications, order confirmations, promotional offers'
            },
            {
                'name': 'Social',
                'description': 'Social media notifications, friend requests, comments, likes'
            },
            {
                'name': 'Finance',
                'description': 'Bank statements, credit card bills, payment confirmations, financial alerts'
            },
            {
                'name': 'Work',
                'description': 'Professional correspondence, work-related emails, business communications'
            },
            {
                'name': 'Personal',
                'description': 'Personal emails from friends and family, one-to-one correspondence'
            },
            {
                'name': 'Travel',
                'description': 'Flight bookings, hotel reservations, travel itineraries'
            },
            {
                'name': 'Spam',
                'description': 'Unwanted promotional emails, suspicious emails, low-value marketing'
            },
            {
                'name': 'Important',
                'description': 'Time-sensitive emails, urgent matters, important notifications'
            }
        ]

    def suggest_categories(self, sample_size=50):
        """
        Analyze inbox and suggest custom categories

        Args:
            sample_size: Number of emails to analyze

        Returns:
            List of suggested categories
        """
        print(f"Fetching {sample_size} sample emails...")
        messages = self.gmail.get_messages(max_results=sample_size, query='')

        emails = []
        for msg in messages:
            details = self.gmail.get_message_details(msg)
            emails.append(details)

        print("Analyzing emails to suggest categories...")
        suggestions = self.ai.suggest_new_categories(emails)

        return suggestions

    def get_inbox_stats(self):
        """Get statistics about the inbox"""
        try:
            # Get message counts
            unread = self.gmail.get_messages(max_results=1, query='is:unread')
            total = self.gmail.get_messages(max_results=1, query='')

            # Note: This is a simplified version
            # In production, you'd want to use the Gmail API's message count features

            return {
                'total_messages': 'Use Gmail API stats',
                'unread_count': len(unread) if unread else 0,
                'sample_fetched': True
            }

        except Exception as e:
            print(f"Error getting inbox stats: {e}")
            return {
                'error': str(e)
            }

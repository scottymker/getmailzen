"""
Retention Manager
Handles auto-deletion and email retention policies
"""
from datetime import datetime, timedelta
from app.gmail_service import GmailService


class RetentionManager:
    """Manages email retention and auto-deletion policies"""

    def __init__(self, user_id=None, gmail_service=None):
        """
        Initialize RetentionManager

        Args:
            user_id (int, optional): User ID for per-user Gmail OAuth.
                                    If None, uses legacy file-based auth.
            gmail_service (GmailService, optional): Custom Gmail service instance
        """
        self.gmail = gmail_service or GmailService(user_id=user_id)

    def analyze_old_emails(self, months=6, category_filter=None):
        """
        Analyze emails older than specified months

        Args:
            months: Age threshold in months
            category_filter: Optional category to filter (e.g., "Newsletters")

        Returns:
            Dictionary with analysis results
        """
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        cutoff_timestamp = int(cutoff_date.timestamp())

        # Build query
        query = f'before:{cutoff_date.strftime("%Y/%m/%d")}'
        if category_filter:
            query += f' category:{category_filter}'

        messages = self.gmail.get_messages(max_results=500, query=query)

        analysis = {
            'total_old_emails': len(messages),
            'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
            'months': months,
            'breakdown': {},
            'emails': []
        }

        # Analyze by sender
        sender_counts = {}
        for msg in messages:
            details = self.gmail.get_message_details(msg)
            sender = details['sender']

            if sender not in sender_counts:
                sender_counts[sender] = {'count': 0, 'examples': []}

            sender_counts[sender]['count'] += 1
            if len(sender_counts[sender]['examples']) < 3:
                sender_counts[sender]['examples'].append(details['subject'])

            analysis['emails'].append({
                'id': details['id'],
                'subject': details['subject'],
                'sender': sender,
                'date': details['date']
            })

        analysis['breakdown'] = sender_counts
        return analysis

    def delete_old_emails(self, months=6, category_filter=None, whitelist=None, dry_run=True):
        """
        Delete emails older than specified months

        Args:
            months: Delete emails older than this many months
            category_filter: Optional category filter
            whitelist: List of sender emails to never delete
            dry_run: If True, don't actually delete

        Returns:
            Dictionary with deletion results
        """
        whitelist = whitelist or []
        cutoff_date = datetime.now() - timedelta(days=months * 30)

        query = f'before:{cutoff_date.strftime("%Y/%m/%d")}'
        if category_filter:
            query += f' category:{category_filter}'

        messages = self.gmail.get_messages(max_results=500, query=query)

        results = {
            'scanned': len(messages),
            'deleted': 0,
            'skipped': 0,
            'whitelisted': 0,
            'errors': 0,
            'dry_run': dry_run,
            'details': []
        }

        for msg in messages:
            details = self.gmail.get_message_details(msg)
            sender = details['sender']

            # Check whitelist
            if any(wl_sender in sender.lower() for wl_sender in whitelist):
                results['whitelisted'] += 1
                results['details'].append({
                    'id': details['id'],
                    'subject': details['subject'],
                    'action': 'whitelisted'
                })
                continue

            # Delete email
            if not dry_run:
                success = self.gmail.delete_message(details['id'])
                if success:
                    results['deleted'] += 1
                    results['details'].append({
                        'id': details['id'],
                        'subject': details['subject'],
                        'sender': sender,
                        'action': 'deleted'
                    })
                else:
                    results['errors'] += 1
            else:
                results['deleted'] += 1
                results['details'].append({
                    'id': details['id'],
                    'subject': details['subject'],
                    'sender': sender,
                    'action': 'would_delete'
                })

        return results

    def get_retention_recommendations(self, email_details):
        """
        Get AI recommendations for retention policy

        Args:
            email_details: List of email details

        Returns:
            Recommendations for what to keep/delete
        """
        recommendations = {
            'safe_to_delete': [],
            'keep': [],
            'review': []
        }

        for email in email_details:
            sender = email.get('sender', '').lower()
            subject = email.get('subject', '').lower()
            labels = email.get('labels', [])

            # Safe to delete: old newsletters, promotions
            if any(keyword in sender for keyword in ['newsletter', 'promo', 'marketing', 'unsubscribe']):
                recommendations['safe_to_delete'].append(email)
            # Keep: important, starred, work emails
            elif 'IMPORTANT' in labels or 'STARRED' in labels:
                recommendations['keep'].append(email)
            # Review: everything else
            else:
                recommendations['review'].append(email)

        return recommendations

    def find_large_emails(self, min_size_mb=5):
        """
        Find emails with large attachments

        Args:
            min_size_mb: Minimum size in MB to flag

        Returns:
            List of large emails
        """
        # Note: Gmail API doesn't directly expose size in list
        # This is a placeholder for future implementation
        query = f'size:{min_size_mb}m'
        messages = self.gmail.get_messages(max_results=100, query=query)

        large_emails = []
        for msg in messages:
            details = self.gmail.get_message_details(msg)
            large_emails.append({
                'id': details['id'],
                'subject': details['subject'],
                'sender': details['sender'],
                'date': details['date']
            })

        return large_emails

    def detect_duplicates(self, max_emails=500):
        """
        Detect duplicate emails (same subject, similar content)

        Args:
            max_emails: Maximum emails to scan

        Returns:
            List of duplicate groups
        """
        messages = self.gmail.get_messages(max_results=max_emails, query='')

        # Group by subject
        subject_groups = {}
        for msg in messages:
            details = self.gmail.get_message_details(msg)
            subject = details['subject'].strip().lower()

            if subject not in subject_groups:
                subject_groups[subject] = []

            subject_groups[subject].append(details)

        # Find groups with 2+ emails
        duplicates = []
        for subject, emails in subject_groups.items():
            if len(emails) >= 2:
                duplicates.append({
                    'subject': subject,
                    'count': len(emails),
                    'emails': emails
                })

        return sorted(duplicates, key=lambda x: x['count'], reverse=True)

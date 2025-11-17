"""
Inbox Health Analyzer
Uses AI to analyze inbox health and provide smart recommendations
"""
import json
from app.gmail_service import GmailService
from app.ai_categorizer import EmailCategorizer
from datetime import datetime, timedelta


class InboxAnalyzer:
    """Analyzes inbox health and provides AI-powered recommendations"""

    def __init__(self, user_id=None, gmail_service=None, categorizer=None):
        """
        Initialize InboxAnalyzer

        Args:
            user_id (int, optional): User ID for per-user Gmail OAuth.
                                    If None, uses legacy file-based auth.
            gmail_service (GmailService, optional): Custom Gmail service instance
            categorizer (EmailCategorizer, optional): Custom AI categorizer instance
        """
        self.gmail = gmail_service or GmailService(user_id=user_id)
        self.ai = categorizer or EmailCategorizer()

    def analyze_inbox_health(self, sample_size=100):
        """
        Comprehensive inbox health analysis

        Returns:
            Dictionary with health score, insights, and recommendations
        """
        # Fetch recent emails
        messages = self.gmail.get_messages(max_results=sample_size, query='')
        unread_messages = self.gmail.get_messages(max_results=sample_size, query='is:unread')

        emails = []
        for msg in messages:
            details = self.gmail.get_message_details(msg)
            emails.append(details)

        # Basic metrics
        metrics = {
            'total_emails_sampled': len(emails),
            'unread_count': len(unread_messages),
            'unread_percentage': (len(unread_messages) / len(emails) * 100) if emails else 0
        }

        # Analyze categories
        category_breakdown = self._analyze_categories(emails)

        # Detect issues
        issues = self._detect_issues(emails, unread_messages, metrics)

        # Calculate health score (0-100)
        health_score = self._calculate_health_score(metrics, issues)

        # Generate AI recommendations
        recommendations = self._generate_recommendations(metrics, issues, category_breakdown)

        return {
            'health_score': health_score,
            'grade': self._get_grade(health_score),
            'metrics': metrics,
            'category_breakdown': category_breakdown,
            'issues': issues,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }

    def _analyze_categories(self, emails):
        """Analyze email distribution by category"""
        categories = {}

        for email in emails:
            labels = email.get('labels', [])

            # Simplified category detection
            if 'CATEGORY_PROMOTIONS' in labels:
                category = 'Promotions'
            elif 'CATEGORY_SOCIAL' in labels:
                category = 'Social'
            elif 'CATEGORY_UPDATES' in labels:
                category = 'Updates'
            elif 'CATEGORY_FORUMS' in labels:
                category = 'Forums'
            else:
                category = 'Primary'

            if category not in categories:
                categories[category] = 0
            categories[category] += 1

        return categories

    def _detect_issues(self, emails, unread_messages, metrics):
        """Detect potential inbox issues"""
        issues = []

        # Too many unread emails
        if metrics['unread_percentage'] > 50:
            issues.append({
                'type': 'high_unread',
                'severity': 'high',
                'message': f"{len(unread_messages)} unread emails ({metrics['unread_percentage']:.0f}%)",
                'suggestion': 'Consider bulk archiving or deleting old unread emails'
            })

        # Old emails detection (placeholder - would need date analysis)
        cutoff_date = datetime.now() - timedelta(days=365)

        # Repeated senders (newsletters)
        sender_counts = {}
        for email in emails:
            sender = email['sender']
            sender_counts[sender] = sender_counts.get(sender, 0) + 1

        # Find senders with 10+ emails
        frequent_senders = {s: c for s, c in sender_counts.items() if c >= 10}
        if frequent_senders:
            issues.append({
                'type': 'frequent_senders',
                'severity': 'medium',
                'message': f"{len(frequent_senders)} senders with 10+ emails",
                'suggestion': 'Consider unsubscribing from newsletters or creating filters',
                'details': list(frequent_senders.items())[:5]  # Top 5
            })

        return issues

    def _calculate_health_score(self, metrics, issues):
        """Calculate inbox health score (0-100)"""
        score = 100

        # Deduct for unread percentage
        if metrics['unread_percentage'] > 70:
            score -= 30
        elif metrics['unread_percentage'] > 50:
            score -= 20
        elif metrics['unread_percentage'] > 30:
            score -= 10

        # Deduct for each issue
        for issue in issues:
            if issue['severity'] == 'high':
                score -= 15
            elif issue['severity'] == 'medium':
                score -= 10
            else:
                score -= 5

        return max(0, min(100, score))

    def _get_grade(self, score):
        """Convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _generate_recommendations(self, metrics, issues, category_breakdown):
        """Generate AI-powered recommendations"""
        recommendations = []

        # Unread backlog
        if metrics['unread_percentage'] > 30:
            recommendations.append({
                'title': 'Clear Unread Backlog',
                'description': f"You have {metrics['unread_percentage']:.0f}% unread emails",
                'action': 'bulk_archive_old',
                'priority': 'high',
                'impact': 'High - Will significantly improve inbox clarity'
            })

        # Promotions cleanup
        if category_breakdown.get('Promotions', 0) > 20:
            recommendations.append({
                'title': 'Clean Up Promotions',
                'description': f"{category_breakdown['Promotions']} promotional emails found",
                'action': 'delete_promotions',
                'priority': 'medium',
                'impact': 'Medium - Reduce clutter from marketing emails'
            })

        # Newsletter management
        for issue in issues:
            if issue['type'] == 'frequent_senders':
                recommendations.append({
                    'title': 'Manage Newsletter Subscriptions',
                    'description': f"Found {len(issue.get('details', []))} high-volume senders",
                    'action': 'unsubscribe_newsletters',
                    'priority': 'medium',
                    'impact': 'High - Prevent future inbox clutter'
                })

        return recommendations

    def get_smart_suggestions(self, sample_size=100):
        """
        Get AI-powered smart suggestions for inbox cleanup

        Returns:
            List of actionable suggestions with one-click actions
        """
        # Fetch sample emails
        messages = self.gmail.get_messages(max_results=sample_size, query='')

        emails_data = []
        for msg in messages:
            details = self.gmail.get_message_details(msg)
            emails_data.append({
                'subject': details['subject'],
                'sender': details['sender'],
                'date': details['date'],
                'snippet': details['snippet']
            })

        # Build AI prompt
        prompt = f"""Analyze this email inbox sample and provide specific, actionable cleanup suggestions.

Sample of {len(emails_data)} recent emails:
{json.dumps(emails_data[:20], indent=2)}

Provide 3-5 specific suggestions in JSON format:
{{
    "suggestions": [
        {{
            "title": "Short, actionable title",
            "description": "Specific explanation with numbers",
            "action_type": "delete_old|unsubscribe|archive|label",
            "target": "specific sender or category",
            "estimated_impact": "Number of emails affected",
            "priority": "high|medium|low"
        }}
    ]
}}

Focus on:
1. High-volume senders to unsubscribe from
2. Old emails safe to delete
3. Categories to archive
4. Specific actions with measurable impact

Respond ONLY with the JSON object."""

        try:
            message = self.ai.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text

            # Parse JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)

            return result.get('suggestions', [])

        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return []

    def detect_unsubscribe_opportunities(self, max_emails=200):
        """
        Detect emails with unsubscribe links (newsletters)

        Returns:
            List of senders you can unsubscribe from
        """
        messages = self.gmail.get_messages(max_results=max_emails, query='')

        unsubscribe_candidates = {}

        for msg in messages:
            details = self.gmail.get_message_details(msg)
            snippet = details['snippet'].lower()
            sender = details['sender']

            # Look for unsubscribe keywords
            if any(keyword in snippet for keyword in ['unsubscribe', 'opt out', 'email preferences']):
                if sender not in unsubscribe_candidates:
                    unsubscribe_candidates[sender] = {
                        'count': 0,
                        'examples': []
                    }

                unsubscribe_candidates[sender]['count'] += 1
                if len(unsubscribe_candidates[sender]['examples']) < 3:
                    unsubscribe_candidates[sender]['examples'].append(details['subject'])

        # Sort by frequency
        sorted_candidates = sorted(
            unsubscribe_candidates.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        return [
            {
                'sender': sender,
                'email_count': data['count'],
                'examples': data['examples']
            }
            for sender, data in sorted_candidates[:20]  # Top 20
        ]

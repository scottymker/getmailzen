"""
AI Categorization Engine
Uses Claude API to intelligently categorize and analyze emails
"""
import os
import json
from anthropic import Anthropic


class EmailCategorizer:
    """Uses Claude AI to categorize and analyze emails"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)

    def categorize_email(self, email_details, categories):
        """
        Analyze an email and determine its category and recommended actions

        Args:
            email_details: Dictionary with email info (subject, sender, snippet, etc.)
            categories: List of category definitions

        Returns:
            Dictionary with category, actions, reasoning, and priority
        """

        # Build the prompt for Claude
        prompt = self._build_categorization_prompt(email_details, categories)

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse Claude's response
            response_text = message.content[0].text
            result = self._parse_categorization_response(response_text)

            return result

        except Exception as e:
            print(f"Error categorizing email: {e}")
            return {
                'category': 'Uncategorized',
                'actions': [],
                'reasoning': f'Error: {str(e)}',
                'priority': 'medium',
                'confidence': 'low'
            }

    def batch_categorize(self, emails, categories):
        """
        Categorize multiple emails in batch

        Args:
            emails: List of email detail dictionaries
            categories: List of category definitions

        Returns:
            List of categorization results
        """
        results = []

        for email in emails:
            result = self.categorize_email(email, categories)
            result['email_id'] = email['id']
            results.append(result)

        return results

    def _build_categorization_prompt(self, email_details, categories):
        """Build the prompt for Claude to categorize an email"""

        categories_text = "\n".join([
            f"- {cat['name']}: {cat['description']}"
            for cat in categories
        ])

        prompt = f"""You are an email organization assistant. Analyze the following email and categorize it appropriately.

Email Details:
- Subject: {email_details['subject']}
- From: {email_details['sender']}
- Preview: {email_details['snippet']}
- Date: {email_details['date']}

Available Categories:
{categories_text}

Based on this email, provide your analysis in the following JSON format:
{{
    "category": "name of the most appropriate category",
    "actions": ["list", "of", "recommended", "actions"],
    "reasoning": "brief explanation of why you chose this category",
    "priority": "high|medium|low",
    "confidence": "high|medium|low"
}}

Recommended actions can include:
- "label:<category_name>" - Apply a label
- "archive" - Archive the email
- "delete" - Delete the email
- "star" - Star/flag as important
- "mark_read" - Mark as read
- "mark_unread" - Mark as unread

Consider:
1. Is this a newsletter, promotional email, personal correspondence, work-related, or spam?
2. How urgent or important is this email?
3. Should it be kept for reference or can it be archived/deleted?
4. Does it require action or is it informational?

Respond ONLY with the JSON object, no additional text."""

        return prompt

    def _parse_categorization_response(self, response_text):
        """Parse Claude's JSON response"""
        try:
            # Extract JSON from response (in case Claude adds explanation)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                raise ValueError("No JSON found in response")

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response was: {response_text}")
            return {
                'category': 'Uncategorized',
                'actions': [],
                'reasoning': 'Failed to parse AI response',
                'priority': 'medium',
                'confidence': 'low'
            }

    def suggest_new_categories(self, sample_emails):
        """
        Analyze a batch of emails and suggest useful categories

        Args:
            sample_emails: List of email details to analyze

        Returns:
            List of suggested category definitions
        """

        # Build summary of emails
        email_summaries = []
        for email in sample_emails[:20]:  # Limit to 20 for token efficiency
            email_summaries.append(
                f"- From: {email['sender']}, Subject: {email['subject']}"
            )

        emails_text = "\n".join(email_summaries)

        prompt = f"""You are analyzing a user's Gmail inbox to suggest useful email categories for automatic organization.

Sample of emails:
{emails_text}

Based on these emails, suggest 5-8 useful categories for organizing this inbox. For each category, provide:
1. A clear name (suitable for a Gmail label)
2. A description of what emails belong in this category
3. Example keywords or patterns to identify emails in this category

Respond in JSON format:
{{
    "categories": [
        {{
            "name": "Category Name",
            "description": "Description of what belongs here",
            "examples": ["example keywords", "sender patterns"]
        }}
    ]
}}

Common useful categories might include:
- Newsletters & Subscriptions
- Social Media Notifications
- Shopping & Receipts
- Work/Professional
- Finance & Banking
- Travel & Bookings
- Personal
- Spam/Promotions

Respond ONLY with the JSON object."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Parse JSON response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)

            return result.get('categories', [])

        except Exception as e:
            print(f"Error suggesting categories: {e}")
            return []

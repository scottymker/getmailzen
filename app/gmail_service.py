"""
Gmail Service Module
Handles authentication and interactions with Gmail API
Supports both per-user OAuth (database) and legacy file-based auth
"""
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes - we need full Gmail access for labeling, deleting, etc.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]


class GmailService:
    """Handles Gmail API operations with per-user or legacy authentication"""

    def __init__(self, user_id=None, credentials_file='credentials.json', token_file='token.json'):
        """
        Initialize Gmail service

        Args:
            user_id (int, optional): User ID for per-user OAuth from database.
                                    If None, falls back to legacy file-based auth.
            credentials_file (str): Path to OAuth credentials file
            token_file (str): Path to legacy token file (only used if user_id is None)
        """
        self.user_id = user_id
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        creds = None

        # Use per-user OAuth if user_id is provided
        if self.user_id:
            from app.oauth_manager import OAuthManager
            oauth_manager = OAuthManager()
            creds = oauth_manager.get_credentials(self.user_id)
            oauth_manager.close()

            if not creds:
                raise ValueError(
                    f"No Gmail credentials found for user {self.user_id}. "
                    "Please connect your Gmail account first."
                )
        else:
            # Legacy file-based authentication (for backward compatibility)
            # Load existing token if available
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)

            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(
                            f"Credentials file '{self.credentials_file}' not found. "
                            "Please download it from Google Cloud Console."
                        )
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials for next time
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def get_messages(self, max_results=100, query=''):
        """
        Fetch messages from Gmail

        Args:
            max_results: Maximum number of messages to fetch
            query: Gmail search query (e.g., 'is:unread', 'from:example.com')

        Returns:
            List of message objects with id, threadId, and snippet
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])

            # Fetch full message details
            detailed_messages = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                detailed_messages.append(message)

            return detailed_messages

        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def get_message_details(self, message):
        """Extract useful information from a message object"""
        headers = message['payload']['headers']

        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')

        # Get message body (simplified - just snippet for now)
        snippet = message.get('snippet', '')

        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'snippet': snippet,
            'labels': message.get('labelIds', [])
        }

    def apply_label(self, message_id, label_name):
        """Apply a label to a message (creates label if it doesn't exist)"""
        try:
            # Get or create label
            label_id = self.get_or_create_label(label_name)

            # Apply label to message
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()

            return True

        except HttpError as error:
            print(f'Error applying label: {error}')
            return False

    def remove_label(self, message_id, label_name):
        """Remove a label from a message"""
        try:
            label_id = self.get_label_id(label_name)
            if not label_id:
                return False

            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': [label_id]}
            ).execute()

            return True

        except HttpError as error:
            print(f'Error removing label: {error}')
            return False

    def archive_message(self, message_id):
        """Archive a message (remove INBOX label)"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error archiving message: {error}')
            return False

    def delete_message(self, message_id):
        """Permanently delete a message"""
        try:
            self.service.users().messages().delete(
                userId='me',
                id=message_id
            ).execute()
            return True
        except HttpError as error:
            print(f'Error deleting message: {error}')
            return False

    def delete_email(self, message_id):
        """Alias for delete_message - permanently delete an email"""
        return self.delete_message(message_id)

    def star_message(self, message_id):
        """Add star to a message"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['STARRED']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error starring message: {error}')
            return False

    def unstar_message(self, message_id):
        """Remove star from a message"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['STARRED']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error unstarring message: {error}')
            return False

    def get_or_create_label(self, label_name):
        """Get label ID or create new label if it doesn't exist"""
        try:
            # Get all labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            # Check if label exists
            for label in labels:
                if label['name'] == label_name:
                    return label['id']

            # Create new label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }

            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()

            return created_label['id']

        except HttpError as error:
            print(f'Error getting/creating label: {error}')
            return None

    def get_label_id(self, label_name):
        """Get label ID by name"""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            for label in labels:
                if label['name'] == label_name:
                    return label['id']

            return None

        except HttpError as error:
            print(f'Error getting label: {error}')
            return None

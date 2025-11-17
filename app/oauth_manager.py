"""
Per-User OAuth Manager
Handles Gmail OAuth credentials storage and retrieval per user
"""
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from app.models import GmailCredential
from app.database import SessionLocal
from app.encryption import encrypt_token, decrypt_token
import os


class OAuthManager:
    """Manages per-user Gmail OAuth credentials"""

    SCOPES = [
        'https://mail.google.com/'  # Full Gmail access (includes delete, modify, labels, etc.)
    ]

    def __init__(self):
        self.db = SessionLocal()
        self.credentials_file = 'credentials.json'

    def close(self):
        """Close database session"""
        self.db.close()

    def create_oauth_flow(self, redirect_uri):
        """
        Create OAuth flow for user to authorize Gmail access

        Args:
            redirect_uri (str): OAuth callback URL

        Returns:
            Flow: OAuth flow object
        """
        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        return flow

    def get_authorization_url(self, redirect_uri, state=None):
        """
        Get Gmail OAuth authorization URL

        Args:
            redirect_uri (str): OAuth callback URL
            state (str): Optional state parameter for security

        Returns:
            tuple: (authorization_url, state)
        """
        flow = self.create_oauth_flow(redirect_uri)

        # Debug: Log the scopes being requested
        print(f"🔍 OAuth scopes being requested: {self.SCOPES}")
        print(f"🔍 Flow scopes: {flow.client_config.get('scopes', 'NOT FOUND')}")

        authorization_url, state = flow.authorization_url(
            access_type='offline',  # Get refresh token
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent to get refresh token
        )

        # Debug: Log the generated URL
        print(f"🔍 Authorization URL: {authorization_url}")

        return authorization_url, state

    def handle_oauth_callback(self, user_id, authorization_response, redirect_uri):
        """
        Handle OAuth callback and store credentials

        Args:
            user_id (int): User ID
            authorization_response (str): Full callback URL with auth code
            redirect_uri (str): OAuth callback URL

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            print(f"🔍 [OAuth] Starting callback handler for user {user_id}")
            print(f"🔍 [OAuth] Redirect URI: {redirect_uri}")

            flow = self.create_oauth_flow(redirect_uri)
            print(f"🔍 [OAuth] Created OAuth flow")

            flow.fetch_token(authorization_response=authorization_response)
            print(f"🔍 [OAuth] Successfully fetched token")

            credentials = flow.credentials
            print(f"🔍 [OAuth] Got credentials, has refresh token: {credentials.refresh_token is not None}")

            # Extract user's Gmail email from token info
            print(f"🔍 [OAuth] Extracting Gmail email...")
            gmail_email = self._get_gmail_email_from_credentials(credentials)
            print(f"🔍 [OAuth] Gmail email: {gmail_email}")

            # Check if this Gmail account is already connected to another user
            existing = self.db.query(GmailCredential).filter(
                GmailCredential.gmail_email == gmail_email,
                GmailCredential.user_id != user_id
            ).first()

            if existing:
                print(f"❌ [OAuth] Gmail account already connected to another user")
                return False, f"This Gmail account is already connected to another GetMailZen account"

            # Check if this user already has this Gmail account
            existing_user_cred = self.db.query(GmailCredential).filter(
                GmailCredential.user_id == user_id,
                GmailCredential.gmail_email == gmail_email
            ).first()

            if existing_user_cred:
                # Update existing credentials
                print(f"🔍 [OAuth] Updating existing credentials for {gmail_email}")
                self._update_credentials(existing_user_cred, credentials)
                print(f"✅ [OAuth] Successfully updated credentials")
                return True, f"Gmail account {gmail_email} reconnected successfully"
            else:
                # Create new credentials
                print(f"🔍 [OAuth] Storing new credentials for {gmail_email}")
                self._store_new_credentials(user_id, gmail_email, credentials)
                print(f"✅ [OAuth] Successfully stored new credentials")
                return True, f"Gmail account {gmail_email} connected successfully"

        except Exception as e:
            print(f"❌ [OAuth] Exception in callback handler: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"OAuth callback failed: {str(e)}"

    def _get_gmail_email_from_credentials(self, credentials):
        """
        Extract Gmail email address from credentials

        Args:
            credentials: Google OAuth credentials

        Returns:
            str: Gmail email address
        """
        # Import here to avoid circular dependency
        from googleapiclient.discovery import build

        service = build('gmail', 'v1', credentials=credentials)
        profile = service.users().getProfile(userId='me').execute()
        return profile.get('emailAddress', 'unknown@gmail.com')

    def _store_new_credentials(self, user_id, gmail_email, credentials):
        """Store new Gmail credentials in database"""
        # Encrypt tokens before storage
        encrypted_access_token = encrypt_token(credentials.token)
        encrypted_refresh_token = encrypt_token(credentials.refresh_token) if credentials.refresh_token else None

        gmail_cred = GmailCredential(
            user_id=user_id,
            gmail_email=gmail_email,
            encrypted_access_token=encrypted_access_token,
            encrypted_refresh_token=encrypted_refresh_token,
            token_expiry=credentials.expiry,
            scopes=list(credentials.scopes) if credentials.scopes else self.SCOPES
        )

        self.db.add(gmail_cred)
        self.db.commit()

    def _update_credentials(self, gmail_cred, credentials):
        """Update existing Gmail credentials"""
        gmail_cred.encrypted_access_token = encrypt_token(credentials.token)
        if credentials.refresh_token:
            gmail_cred.encrypted_refresh_token = encrypt_token(credentials.refresh_token)
        gmail_cred.token_expiry = credentials.expiry
        gmail_cred.updated_at = datetime.utcnow()

        self.db.commit()

    def get_credentials(self, user_id, gmail_email=None):
        """
        Get Gmail credentials for user

        Args:
            user_id (int): User ID
            gmail_email (str): Optional Gmail email (if user has multiple accounts)

        Returns:
            Credentials or None: Google OAuth credentials
        """
        # Query for user's Gmail credentials
        query = self.db.query(GmailCredential).filter(
            GmailCredential.user_id == user_id
        )

        if gmail_email:
            query = query.filter(GmailCredential.gmail_email == gmail_email)

        gmail_cred = query.first()

        if not gmail_cred:
            return None

        # Decrypt tokens
        access_token = decrypt_token(gmail_cred.encrypted_access_token)
        refresh_token = decrypt_token(gmail_cred.encrypted_refresh_token) if gmail_cred.encrypted_refresh_token else None

        # Create credentials object
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=self._get_client_id(),
            client_secret=self._get_client_secret(),
            scopes=gmail_cred.scopes or self.SCOPES
        )

        # Set expiry
        if gmail_cred.token_expiry:
            credentials.expiry = gmail_cred.token_expiry

        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                # Update database with new tokens
                self._update_credentials(gmail_cred, credentials)
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                return None

        return credentials

    def _get_client_id(self):
        """Get OAuth client ID from credentials file"""
        import json
        with open(self.credentials_file, 'r') as f:
            creds_data = json.load(f)
            # Support both 'web' and 'installed' OAuth client types
            if 'web' in creds_data:
                return creds_data['web']['client_id']
            return creds_data['installed']['client_id']

    def _get_client_secret(self):
        """Get OAuth client secret from credentials file"""
        import json
        with open(self.credentials_file, 'r') as f:
            creds_data = json.load(f)
            # Support both 'web' and 'installed' OAuth client types
            if 'web' in creds_data:
                return creds_data['web']['client_secret']
            return creds_data['installed']['client_secret']

    def get_user_gmail_accounts(self, user_id):
        """
        Get all Gmail accounts connected by user

        Args:
            user_id (int): User ID

        Returns:
            list: List of GmailCredential objects
        """
        return self.db.query(GmailCredential).filter(
            GmailCredential.user_id == user_id
        ).all()

    def disconnect_gmail_account(self, user_id, gmail_email):
        """
        Disconnect Gmail account from user

        Args:
            user_id (int): User ID
            gmail_email (str): Gmail email to disconnect

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            gmail_cred = self.db.query(GmailCredential).filter(
                GmailCredential.user_id == user_id,
                GmailCredential.gmail_email == gmail_email
            ).first()

            if not gmail_cred:
                return False, "Gmail account not found"

            self.db.delete(gmail_cred)
            self.db.commit()

            return True, f"Gmail account {gmail_email} disconnected successfully"

        except Exception as e:
            self.db.rollback()
            return False, f"Failed to disconnect: {str(e)}"

    def has_gmail_connected(self, user_id):
        """
        Check if user has any Gmail account connected

        Args:
            user_id (int): User ID

        Returns:
            bool: True if user has at least one Gmail account connected
        """
        count = self.db.query(GmailCredential).filter(
            GmailCredential.user_id == user_id
        ).count()
        return count > 0

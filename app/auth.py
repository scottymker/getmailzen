"""
Authentication Module
Handles user registration, login, password management
"""
from flask_bcrypt import Bcrypt
from app.models import User, UserSettings
from app.database import SessionLocal
from datetime import datetime, timedelta
import secrets
import string

bcrypt = Bcrypt()


class AuthService:
    """Handles all authentication operations"""

    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        """Close database session"""
        self.db.close()

    def register_user(self, email, password):
        """
        Register a new user

        Args:
            email (str): User email
            password (str): Plain text password

        Returns:
            tuple: (success: bool, user or error_message)
        """
        try:
            # Check if user already exists
            existing_user = self.db.query(User).filter_by(email=email.lower()).first()
            if existing_user:
                return False, "Email already registered"

            # Validate password strength
            if len(password) < 8:
                return False, "Password must be at least 8 characters"

            # Create password hash
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

            # Create user
            user = User(
                email=email.lower(),
                password_hash=password_hash,
                email_verified=False,  # Will implement email verification later
                subscription_tier='trial',
                trial_ends_at=datetime.utcnow() + timedelta(days=14)
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            # Create default user settings
            self._create_default_settings(user.id)

            return True, user

        except Exception as e:
            self.db.rollback()
            return False, f"Registration failed: {str(e)}"

    def _create_default_settings(self, user_id):
        """Create default settings for new user"""
        settings = UserSettings(
            user_id=user_id,
            notify_trial_ending=True,
            notify_monthly_summary=True,
            notify_payment_failed=True,
            notify_usage_limit=True,
            default_retention_months=6,
            auto_process_enabled=False,
            auto_process_frequency='weekly',
            timezone='UTC',
            language='en'
        )
        self.db.add(settings)
        self.db.commit()

    def authenticate_user(self, email, password):
        """
        Authenticate user with email and password

        Args:
            email (str): User email
            password (str): Plain text password

        Returns:
            tuple: (success: bool, user or error_message)
        """
        try:
            user = self.db.query(User).filter_by(email=email.lower()).first()

            if not user:
                return False, "Invalid email or password"

            # Check if account is active
            if not user.is_active:
                return False, "Account is deactivated"

            # Verify password
            if not bcrypt.check_password_hash(user.password_hash, password):
                return False, "Invalid email or password"

            # Update last login (we'll add this field later if needed)
            return True, user

        except Exception as e:
            return False, f"Authentication failed: {str(e)}"

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.db.query(User).filter_by(id=user_id).first()

    def get_user_by_email(self, email):
        """Get user by email"""
        return self.db.query(User).filter_by(email=email.lower()).first()

    def change_password(self, user_id, old_password, new_password):
        """
        Change user password

        Args:
            user_id (int): User ID
            old_password (str): Current password
            new_password (str): New password

        Returns:
            tuple: (success: bool, message)
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"

            # Verify old password
            if not bcrypt.check_password_hash(user.password_hash, old_password):
                return False, "Current password is incorrect"

            # Validate new password
            if len(new_password) < 8:
                return False, "New password must be at least 8 characters"

            # Update password
            user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            self.db.commit()

            return True, "Password updated successfully"

        except Exception as e:
            self.db.rollback()
            return False, f"Password change failed: {str(e)}"

    def generate_reset_token(self):
        """Generate a secure password reset token"""
        return secrets.token_urlsafe(32)

    def request_password_reset(self, email):
        """
        Request password reset (generates token)

        Args:
            email (str): User email

        Returns:
            tuple: (success: bool, token or error_message)
        """
        try:
            user = self.get_user_by_email(email)
            if not user:
                # Don't reveal if email exists for security
                return True, None

            # Generate reset token
            reset_token = self.generate_reset_token()

            # TODO: Store reset token in database with expiry
            # TODO: Send reset email

            return True, reset_token

        except Exception as e:
            return False, str(e)

    def reset_password_with_token(self, token, new_password):
        """
        Reset password using token

        Args:
            token (str): Reset token
            new_password (str): New password

        Returns:
            tuple: (success: bool, message)
        """
        # TODO: Implement token validation and password reset
        # This will require adding a password_reset_tokens table
        return False, "Password reset not yet implemented"

    def verify_email(self, user_id):
        """Mark user email as verified"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"

            user.email_verified = True
            self.db.commit()

            return True, "Email verified successfully"

        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def deactivate_user(self, user_id):
        """Deactivate user account"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"

            user.is_active = False
            self.db.commit()

            return True, "Account deactivated"

        except Exception as e:
            self.db.rollback()
            return False, str(e)


def validate_password_strength(password):
    """
    Validate password meets security requirements

    Args:
        password (str): Password to validate

    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if len(password) > 128:
        return False, "Password must be less than 128 characters"

    # Check for at least one number
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"

    # Check for at least one letter
    if not any(char.isalpha() for char in password):
        return False, "Password must contain at least one letter"

    return True, "Password is valid"


def validate_email(email):
    """
    Basic email validation

    Args:
        email (str): Email to validate

    Returns:
        bool: True if valid email format
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

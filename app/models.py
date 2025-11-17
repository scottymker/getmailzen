"""
Database Models
SQLAlchemy models for GetMailZen multi-user SaaS platform
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app.database import Base


class User(Base, UserMixin):
    """User account model"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Account status
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Subscription
    subscription_tier = Column(String(50), default='trial')  # trial, starter, professional, business
    trial_ends_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))

    # Onboarding
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=0)

    # Relationships
    gmail_credentials = relationship('GmailCredential', back_populates='user', cascade='all, delete-orphan')
    subscriptions = relationship('Subscription', back_populates='user', cascade='all, delete-orphan')
    processing_history = relationship('ProcessingHistory', back_populates='user', cascade='all, delete-orphan')
    user_settings = relationship('UserSettings', back_populates='user', uselist=False, cascade='all, delete-orphan')
    retention_policies = relationship('RetentionPolicy', back_populates='user', cascade='all, delete-orphan')
    whitelists = relationship('Whitelist', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    def is_trial_expired(self):
        """Check if trial period has expired"""
        if self.subscription_tier == 'trial' and self.trial_ends_at:
            return datetime.utcnow() > self.trial_ends_at
        return False

    def has_active_subscription(self):
        """Check if user has an active paid subscription"""
        return self.subscription_tier in ['starter', 'professional', 'business']


class GmailCredential(Base):
    """Per-user Gmail OAuth credentials (encrypted)"""
    __tablename__ = 'gmail_credentials'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    gmail_email = Column(String(255), nullable=False)

    # Encrypted tokens
    encrypted_access_token = Column(Text)
    encrypted_refresh_token = Column(Text)

    # Token metadata
    token_expiry = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Scopes granted
    scopes = Column(JSON)  # List of granted OAuth scopes

    # Relationship
    user = relationship('User', back_populates='gmail_credentials')

    def __repr__(self):
        return f'<GmailCredential {self.gmail_email}>'

    def is_token_expired(self):
        """Check if access token is expired"""
        if self.token_expiry:
            return datetime.utcnow() > self.token_expiry
        return True


class Subscription(Base):
    """Stripe subscription tracking"""
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Stripe IDs
    stripe_customer_id = Column(String(255), unique=True)
    stripe_subscription_id = Column(String(255), unique=True)

    # Subscription details
    tier = Column(String(50), nullable=False)  # starter, professional, business
    status = Column(String(50), nullable=False)  # active, canceled, past_due, trialing
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    canceled_at = Column(DateTime)

    # Relationship
    user = relationship('User', back_populates='subscriptions')

    def __repr__(self):
        return f'<Subscription {self.tier} - {self.status}>'


class ProcessingHistory(Base):
    """Track email processing history for analytics and usage limits"""
    __tablename__ = 'processing_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Processing details
    emails_processed = Column(Integer, default=0)
    emails_deleted = Column(Integer, default=0)
    emails_archived = Column(Integer, default=0)
    emails_labeled = Column(Integer, default=0)

    # AI usage
    ai_api_calls = Column(Integer, default=0)

    # Timestamp
    processed_at = Column(DateTime, default=datetime.utcnow, index=True)
    processing_type = Column(String(50))  # categorize, retention, cleanup, etc.

    # Relationship
    user = relationship('User', back_populates='processing_history')

    def __repr__(self):
        return f'<ProcessingHistory user_id={self.user_id} emails={self.emails_processed}>'


class UserSettings(Base):
    """Per-user customizable settings"""
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True, index=True)

    # Email notification preferences
    notify_trial_ending = Column(Boolean, default=True)
    notify_monthly_summary = Column(Boolean, default=True)
    notify_payment_failed = Column(Boolean, default=True)
    notify_usage_limit = Column(Boolean, default=True)

    # Default retention policy (months)
    default_retention_months = Column(Integer, default=6)

    # Processing preferences
    auto_process_enabled = Column(Boolean, default=False)
    auto_process_frequency = Column(String(50), default='weekly')  # daily, weekly, monthly

    # Category customization (JSON)
    custom_categories = Column(JSON)

    # Timezone
    timezone = Column(String(50), default='UTC')

    # Language
    language = Column(String(10), default='en')

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship('User', back_populates='user_settings')

    def __repr__(self):
        return f'<UserSettings user_id={self.user_id}>'


class RetentionPolicy(Base):
    """Per-user retention policies for automatic deletion"""
    __tablename__ = 'retention_policies'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Policy details
    name = Column(String(100), nullable=False)
    category = Column(String(100))  # Newsletter, Shopping, etc. (null = all categories)
    retention_months = Column(Integer, nullable=False)  # Delete emails older than X months

    # Policy settings
    is_active = Column(Boolean, default=True)
    dry_run = Column(Boolean, default=True)  # Safety: preview before actual deletion

    # Last execution
    last_run_at = Column(DateTime)
    emails_deleted_last_run = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship('User', back_populates='retention_policies')

    def __repr__(self):
        return f'<RetentionPolicy {self.name} - {self.retention_months} months>'


class Whitelist(Base):
    """Per-user whitelist (senders to never delete/archive)"""
    __tablename__ = 'whitelists'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Whitelist entry
    email_pattern = Column(String(255), nullable=False)  # e.g., "@company.com" or "boss@company.com"
    description = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship('User', back_populates='whitelists')

    def __repr__(self):
        return f'<Whitelist {self.email_pattern}>'


class EmailCategory(Base):
    """Global and per-user email categories"""
    __tablename__ = 'email_categories'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Null = global category

    # Category details
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Actions (JSON array)
    actions = Column(JSON)  # e.g., ["label:Newsletters", "archive"]

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<EmailCategory {self.name}>'


class InboxHealthSnapshot(Base):
    """Track inbox health over time for analytics"""
    __tablename__ = 'inbox_health_snapshots'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Health metrics
    health_score = Column(Integer)  # 0-100
    grade = Column(String(1))  # A, B, C, D, F
    total_emails = Column(Integer)
    unread_count = Column(Integer)
    unread_percentage = Column(Integer)

    # Category breakdown (JSON)
    category_breakdown = Column(JSON)

    # Issues detected (JSON)
    issues = Column(JSON)

    # Snapshot timestamp
    snapshot_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<InboxHealthSnapshot score={self.health_score} at {self.snapshot_at}>'


class UsageTracking(Base):
    """Track monthly usage for tier limits and billing"""
    __tablename__ = 'usage_tracking'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Usage period
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)

    # Email processing
    emails_processed = Column(BigInteger, default=0)
    emails_deleted = Column(BigInteger, default=0)
    emails_archived = Column(BigInteger, default=0)

    # AI API usage
    ai_api_calls = Column(BigInteger, default=0)
    ai_tokens_used = Column(BigInteger, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UsageTracking {self.year}-{self.month} - {self.emails_processed} emails>'


class AuditLog(Base):
    """Security and compliance audit log"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)

    # Event details
    event_type = Column(String(100), nullable=False, index=True)  # login, logout, email_deleted, etc.
    event_description = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(Text)

    # Event metadata (JSON)
    event_metadata = Column(JSON)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<AuditLog {self.event_type} at {self.created_at}>'

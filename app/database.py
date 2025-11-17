"""
Database Connection Management
Handles PostgreSQL connection and session management
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Test connections before using them
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max connections beyond pool_size
    echo=False  # Set to True for SQL query debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Scoped session for thread-safe database access
db_session = scoped_session(SessionLocal)

# Base class for all models
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """
    Initialize database (create all tables)
    Only use this for initial setup - use Alembic for migrations in production
    """
    import app.models  # Import models to register them
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def get_db():
    """
    Dependency for Flask routes to get database session
    Usage in routes:
        db = get_db()
        try:
            # Use db here
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def close_db():
    """Close the database connection"""
    db_session.remove()


def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

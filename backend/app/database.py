from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ace_db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,  # Maximum number of connections to keep open
    max_overflow=20,  # Maximum number of connections that can be created beyond pool_size
    echo=False  # Set to True for SQL query logging (useful for debugging)
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db() -> Generator:
    """
    Database session dependency.
    Creates a new database session for each request and closes it after the request is completed.
    
    Usage in endpoints:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables
def init_db():
    """
    Initialize database by creating all tables.
    Call this function when starting the application.
    """
    # Import all models here to ensure they are registered with Base
    from app.models import (
        User, UserProfile,
        TestTemplate, TestSection, TestAttempt,
        ListeningQuestion, ListeningAnswer,
        ReadingPassage, ReadingQuestion, ReadingAnswer,
        WritingTask, SpeakingTask,
        ListeningSubmission, ReadingSubmission,
        WritingSubmission, SpeakingSubmission,
        WritingGrade, SpeakingGrade, TestResult
    )
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

# Function to drop all tables (use with caution!)
def drop_db():
    """
    Drop all database tables.
    WARNING: This will delete all data!
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️ All database tables dropped!")

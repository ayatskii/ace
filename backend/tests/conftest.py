"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
import sys
import os

# Set environment variable for test database BEFORE importing app
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["TESTING"] = "True"

# Add the app directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def completion_question_data():
    """Sample data for completion question tests"""
    return {
        "type_specific_data": {
            "template_text": "The meeting starts at [BLANK_1] on [BLANK_2].",
            "blanks": [
                {"blank_id": "BLANK_1", "max_words": 2, "case_sensitive": False},
                {"blank_id": "BLANK_2", "max_words": 1, "case_sensitive": False}
            ]
        },
        "answer_data": {
            "blanks": {
                "BLANK_1": ["9 am", "nine am", "9:00"],
                "BLANK_2": ["Monday"]
            }
        }
    }


@pytest.fixture
def matching_question_data():
    """Sample data for matching question tests"""
    return {
        "type_specific_data": {
            "items": [
                {"item_number": 1, "item_text": "The capital of France"},
                {"item_number": 2, "item_text": "The capital of Germany"},
                {"item_number": 3, "item_text": "The capital of Italy"}
            ],
            "options": [
                {"option_label": "A", "option_text": "Berlin"},
                {"option_label": "B", "option_text": "Paris"},
                {"option_label": "C", "option_text": "Rome"},
                {"option_label": "D", "option_text": "Madrid"}
            ],
            "allow_option_reuse": False
        },
        "answer_data": {
            "mappings": {"1": "B", "2": "A", "3": "C"}
        }
    }


@pytest.fixture
def mcq_question_data():
    """Sample data for MCQ question tests"""
    return {
        "type_specific_data": {
            "options": [
                {"option_label": "A", "option_text": "Option A"},
                {"option_label": "B", "option_text": "Option B"},
                {"option_label": "C", "option_text": "Option C"},
                {"option_label": "D", "option_text": "Option D"}
            ],
            "allow_multiple": False
        },
        "answer_data": {
            "correct_options": ["B"]
        }
    }


@pytest.fixture
def tfng_question_data():
    """Sample data for True/False/Not Given question tests"""
    return {
        "type_specific_data": {
            "statements": [
                {"statement_number": 1, "statement_text": "The sky is blue."},
                {"statement_number": 2, "statement_text": "Fish can fly."},
                {"statement_number": 3, "statement_text": "The author mentions climate change."}
            ],
            "answer_type": "true_false_not_given"
        },
        "answer_data": {
            "answers": {"1": "TRUE", "2": "FALSE", "3": "NOT GIVEN"}
        }
    }


@pytest.fixture
def diagram_question_data():
    """Sample data for diagram labeling question tests"""
    return {
        "type_specific_data": {
            "image_url": "/uploads/diagram.png",
            "labels": [
                {"label_id": "1", "x": 25.5, "y": 30.0},
                {"label_id": "2", "x": 60.0, "y": 45.5},
                {"label_id": "3", "x": 80.0, "y": 70.0}
            ],
            "max_words_per_label": 2
        },
        "answer_data": {
            "labels": {
                "1": ["library", "the library"],
                "2": ["cafe", "coffee shop"],
                "3": ["parking lot", "car park"]
            }
        }
    }


@pytest.fixture
def short_answer_question_data():
    """Sample data for short answer question tests"""
    return {
        "type_specific_data": {
            "max_words": 3,
            "case_sensitive": False
        },
        "answer_data": {
            "correct_answers": ["global warming", "climate change", "greenhouse effect"]
        }
    }

# --- Integration Test Fixtures ---

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Get a TestClient with the database dependency overridden.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def user_factory(db):
    """
    Fixture to create a user directly in the database.
    """
    from app.models import User
    from app.core.security import get_password_hash
    
    def create_user(email, password="password123", role="student", full_name="Test User"):
        user = User(
            email=email,
            password_hash=get_password_hash(password),
            role=role,
            full_name=full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
        
    return create_user


@pytest.fixture(scope="function")
def test_template_factory(db, user_factory):
    """
    Fixture to create a test template with sections.
    """
    from app.models import TestTemplate, TestSection, WritingTask, SpeakingTask
    import uuid
    
    def create_template(title="Test Template", test_type="ACADEMIC", is_published=True, creator=None):
        if not creator:
            creator = user_factory(email=f"creator_{uuid.uuid4()}@test.com", role="admin")
            
        template = TestTemplate(
            title=title,
            test_type=test_type,
            duration_minutes=180,
            is_published=is_published,
            created_by=creator.id
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        
        # Create Listening Section
        listening_section = TestSection(
            test_template_id=template.id,
            section_type="listening",
            order=1,
            total_questions=40,
            duration_minutes=30
        )
        db.add(listening_section)
        
        # Create Reading Section
        reading_section = TestSection(
            test_template_id=template.id,
            section_type="reading",
            order=2,
            total_questions=40,
            duration_minutes=60
        )
        db.add(reading_section)

        # Create Writing Section & Task
        writing_section = TestSection(
            test_template_id=template.id,
            section_type="writing",
            order=3,
            total_questions=2,
            duration_minutes=60
        )
        db.add(writing_section)
        db.commit()
        db.refresh(writing_section)
        
        writing_task = WritingTask(
            section_id=writing_section.id,
            task_number=1,
            task_type="writing_task_1",
            prompt_text="Write about this chart.",
            word_limit_min=150,
            time_limit_minutes=20
        )
        db.add(writing_task)
        
        # Create Speaking Section & Task
        speaking_section = TestSection(
            test_template_id=template.id,
            section_type="speaking",
            order=4,
            total_questions=3,
            duration_minutes=15
        )
        db.add(speaking_section)
        db.commit()
        db.refresh(speaking_section)
        
        speaking_task = SpeakingTask(
            section_id=speaking_section.id,
            part_number=1,
            task_type="speaking_part_1",
            prompt_text="Talk about your hometown.",
            speaking_time_seconds=300,
            order=1
        )
        db.add(speaking_task)
        
        db.commit()
        db.refresh(template)
        return template
        
    return create_template


@pytest.fixture(scope="function")
def submission_factory(db, test_template_factory, user_factory):
    """
    Fixture to create a submission (writing or speaking) for grading tests.
    """
    from app.models import TestAttempt, WritingSubmission, SpeakingSubmission
    from datetime import datetime, timezone
    import uuid
    
    def create_submission(user=None, template=None, submission_type="writing", status="pending"):
        if not user:
            user = user_factory(email=f"student_{uuid.uuid4()}@test.com")
        if not template:
            template = test_template_factory()
            
        # Create Attempt
        attempt = TestAttempt(
            user_id=user.id,
            test_template_id=template.id,
            status="submitted",
            end_time=datetime.now(timezone.utc)
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        
        submission = None
        if submission_type == "writing":
            # Get task
            section = next(s for s in template.sections if s.section_type == "writing")
            task = section.writing_tasks[0]
            
            submission = WritingSubmission(
                test_attempt_id=attempt.id,
                task_id=task.id,
                response_text="This is a sample essay response.",
                word_count=150,
                status=status,
                submitted_at=datetime.now(timezone.utc)
            )
            db.add(submission)
            
        elif submission_type == "speaking":
            # Get task
            section = next(s for s in template.sections if s.section_type == "speaking")
            task = section.speaking_tasks[0]
            
            submission = SpeakingSubmission(
                test_attempt_id=attempt.id,
                task_id=task.id,
                audio_url="http://test.com/audio.mp3",
                duration_seconds=120,
                status=status,
                submitted_at=datetime.now(timezone.utc)
            )
            db.add(submission)
            
        db.commit()
        db.refresh(submission)
        return submission
        
    return create_submission

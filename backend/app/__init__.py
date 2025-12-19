from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import QuestionTypeTemplate, QuestionTypeEnum
from app.core.security import get_password_hash
from app.models import User

def init_question_types(db: Session):
    """Initialize predefined question types"""
    question_types = [
        # Listening types
        QuestionTypeTemplate(
            name="Multiple Choice",
            type_enum=QuestionTypeEnum.LISTENING_MULTIPLE_CHOICE.value,
            section_type="listening",
            description="Choose the correct answer from options",
            is_active=True
        ),
        QuestionTypeTemplate(
            name="Fill in the Blank",
            type_enum=QuestionTypeEnum.LISTENING_FILL_IN_BLANK.value,
            section_type="listening",
            description="Complete the sentence or notes",
            is_active=True
        ),
        # Reading types
        QuestionTypeTemplate(
            name="True/False/Not Given",
            type_enum=QuestionTypeEnum.READING_TRUE_FALSE_NOT_GIVEN.value,
            section_type="reading",
            description="Determine if statements are true, false, or not given",
            is_active=True
        ),
        # Add more types...
    ]
    
    for qt in question_types:
        existing = db.query(QuestionTypeTemplate).filter(
            QuestionTypeTemplate.type_enum == qt.type_enum
        ).first()
        if not existing:
            db.add(qt)
    
    db.commit()

def create_admin_user(db: Session):
    """Create default admin user"""
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            full_name="System Admin",
            role="admin",
            password_hash=get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()
        print("✅ Admin user created: admin@example.com / admin123")

def init_database():
    """Initialize database with default data"""
    db = SessionLocal()
    try:
        print("🔧 Initializing database...")
        init_question_types(db)
        create_admin_user(db)
        print("✅ Database initialized successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()

"""
Seed script to create a student account
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash

def seed_student_account():
    db = SessionLocal()
    try:
        student_exists = db.query(User).filter(User.email == "student@example.com").first()
        if not student_exists:
            student_user = User(
                email="student@example.com",
                full_name="Test Student",
                role="student",
                password_hash=get_password_hash("password123")
            )
            db.add(student_user)
            db.commit()
            print("✅ Created student account: student@example.com")
        else:
            print("ℹ️  Student account already exists")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding student: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_student_account()

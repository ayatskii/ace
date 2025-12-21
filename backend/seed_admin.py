"""
Seed script to create initial admin and teacher accounts
Run this once to set up platform administrators
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User
from app.core.security import get_password_hash


def seed_admin_accounts():
    """Create initial admin and teacher accounts"""
    db = SessionLocal()
    
    try:
        # Create admin account
        admin_exists = db.query(User).filter(User.email == "admin@ielts.com").first()
        if not admin_exists:
            admin_user = User(
                email="miras@shluha.com",
                full_name="Miras Pidaras",
                role="admin",
                password_hash=get_password_hash("AdickGandon123!")
            )
            db.add(admin_user)
            print("✅ Created admin account: admin@ielts.com")
        else:
            print("ℹ️  Admin account already exists")
        
        # Create teacher account
        teacher_exists = db.query(User).filter(User.email == "teacher@ielts.com").first()
        if not teacher_exists:
            teacher_user = User(
                email="teacher@ielts.com",
                full_name="Head Teacher",
                role="teacher",
                password_hash=get_password_hash("Teacher123!")
            )
            db.add(teacher_user)
            print("✅ Created teacher account: teacher@ielts.com")
        else:
            print("ℹ️  Teacher account already exists")
        
        db.commit()
        print("\n🎉 Seed completed successfully!")
        print("\nLogin credentials:")
        print("  Admin  - admin@ielts.com / Admin123!")
        print("  Teacher - teacher@ielts.com / Teacher123!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding admin and teacher accounts...\n")
    seed_admin_accounts()

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    ListeningQuestion, ReadingQuestion, ListeningAnswer, ReadingAnswer
)

def seed_answers():
    db = SessionLocal()
    try:
        print("🌱 Seeding answers...")
        
        # 1. Seed Listening Answers
        l_questions = db.query(ListeningQuestion).all()
        print(f"Found {len(l_questions)} listening questions")
        
        for q in l_questions:
            # Check if answer already exists
            if q.answers:
                continue
                
            # Assign a default correct answer based on question type or just "A" / "True"
            correct_ans = "A"
            if "map" in str(q.question_type).lower():
                correct_ans = "Library"
            elif "blank" in str(q.question_type).lower():
                correct_ans = "technology"
            
            answer = ListeningAnswer(
                question_id=q.id,
                correct_answer=correct_ans,
                alternative_answers=["Option A", "tech"] if correct_ans == "A" else []
            )
            db.add(answer)
            
        # 2. Seed Reading Answers
        r_questions = db.query(ReadingQuestion).all()
        print(f"Found {len(r_questions)} reading questions")
        
        for q in r_questions:
            if q.answers:
                continue
                
            correct_ans = "A"
            if "true" in str(q.question_type).lower():
                correct_ans = "TRUE"
            elif "heading" in str(q.question_type).lower():
                correct_ans = "i"
            elif "completion" in str(q.question_type).lower():
                correct_ans = "universe"
                
            answer = ReadingAnswer(
                question_id=q.id,
                correct_answer=correct_ans,
                alternative_answers=["Option A"] if correct_ans == "A" else []
            )
            db.add(answer)
            
        db.commit()
        print("✅ Answers seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding answers: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_answers()

from sqlalchemy import text
from app.database import engine

def add_columns():
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # Listening Questions
        try:
            print("Checking listening_questions...")
            conn.execute(text("ALTER TABLE listening_questions ADD COLUMN IF NOT EXISTS type_specific_data JSONB"))
            conn.execute(text("ALTER TABLE listening_questions ADD COLUMN IF NOT EXISTS answer_data JSONB"))
            conn.execute(text("ALTER TABLE listening_questions ADD COLUMN IF NOT EXISTS options JSONB"))
            print("Updated listening_questions")
        except Exception as e:
            print(f"Error updating listening_questions: {e}")

        # Reading Questions
        try:
            print("Checking reading_questions...")
            conn.execute(text("ALTER TABLE reading_questions ADD COLUMN IF NOT EXISTS type_specific_data JSONB"))
            conn.execute(text("ALTER TABLE reading_questions ADD COLUMN IF NOT EXISTS answer_data JSONB"))
            conn.execute(text("ALTER TABLE reading_questions ADD COLUMN IF NOT EXISTS options JSONB"))
            print("Updated reading_questions")
        except Exception as e:
            print(f"Error updating reading_questions: {e}")

if __name__ == "__main__":
    print("Starting schema update...")
    add_columns()
    print("Schema update complete.")

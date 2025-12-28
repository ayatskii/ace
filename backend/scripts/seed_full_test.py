import sys
import os
import logging
from datetime import datetime
from sqlalchemy.orm import Session

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.test import TestTemplate, TestSection, SectionType, TestType, TestAttempt
from app.models.question import (
    ListeningPart, ListeningQuestion, ListeningAnswer,
    ReadingPassage, ReadingQuestion, ReadingAnswer,
    WritingTask, SpeakingTask
)
from app.core.security import get_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_db():
    db = SessionLocal()
    try:
        logger.info("Starting database seeding...")

        # 1. Create Admin User
        admin_email = "admin@ace.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                password_hash=get_password_hash("admin123"),
                full_name="Admin User",
                role=UserRole.ADMIN
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.info(f"Created admin user: {admin_email}")
        else:
            logger.info(f"Admin user already exists: {admin_email}")

        # 2. Create Test
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_title = f"IELTS Comprehensive Mock Test {timestamp}"
        
        test = TestTemplate(
            title=test_title,
            description="A full mock test covering all question types for verification.",
            test_type=TestType.ACADEMIC,
            duration_minutes=160, # Approx total time
            is_published=True,
            created_by=admin.id
        )
        db.add(test)
        db.commit()
        db.refresh(test)
        logger.info(f"Created test: {test_title}")
            
        # 3. Create Sections
        sections = {}
        section_configs = {
            SectionType.LISTENING: {"order": 1, "marks": 40, "questions": 40, "duration": 30},
            SectionType.READING: {"order": 2, "marks": 40, "questions": 40, "duration": 60},
            SectionType.WRITING: {"order": 3, "marks": 9, "questions": 2, "duration": 60},
            SectionType.SPEAKING: {"order": 4, "marks": 9, "questions": 3, "duration": 15}
        }

        for section_type in [SectionType.LISTENING, SectionType.READING, SectionType.WRITING, SectionType.SPEAKING]:
            section = db.query(TestSection).filter(
                TestSection.test_template_id == test.id,
                TestSection.section_type == section_type
            ).first()
            
            config = section_configs[section_type]
            
            if not section:
                section = TestSection(
                    test_template_id=test.id,
                    section_type=section_type,
                    order=config["order"],
                    total_questions=config["questions"],
                    duration_minutes=config["duration"]
                )
                db.add(section)
                db.commit()
                db.refresh(section)
                logger.info(f"Created section: {section_type}")
            sections[section_type] = section

        # 4. Populate Listening Section
        listening_section = sections[SectionType.LISTENING]
        if not db.query(ListeningPart).filter(ListeningPart.section_id == listening_section.id).first():
            # Create 4 Parts
            for part_num in range(1, 5):
                part = ListeningPart(
                    section_id=listening_section.id,
                    part_number=part_num,
                    audio_url=f"https://example.com/audio/part{part_num}.mp3",
                    transcript=f"Transcript for Part {part_num}..."
                )
                db.add(part)
                db.commit()
                
                # Create 10 questions per part
                start_q = (part_num - 1) * 10 + 1
                for i in range(10):
                    q_num = start_q + i
                    q_type = "listening_multiple_choice" # Default filler
                    q_text = f"Question {q_num} text..."
                    
                    # Specific types for demonstration
                    if part_num == 1 and i < 5:
                        q_type = "listening_form_completion"
                        q_text = "Complete the form."
                    elif part_num == 2 and i < 5:
                        q_type = "listening_multiple_choice"
                    elif part_num == 3 and i < 5:
                        q_type = "listening_matching_headings"
                        q_text = "Match the headings."
                    elif part_num == 4 and i < 5:
                        q_type = "listening_summary_completion"
                        q_text = "Complete the summary."
                        
                    q = ListeningQuestion(
                        section_id=listening_section.id,
                        part_id=part.id,
                        question_number=q_num,
                        question_type=q_type,
                        question_text=q_text,
                        order=q_num,
                        marks=1,
                        has_options=(q_type == "listening_multiple_choice"),
                        options=[{"option_label": "A", "option_text": "Option A"}, {"option_label": "B", "option_text": "Option B"}, {"option_label": "C", "option_text": "Option C"}] if q_type == "listening_multiple_choice" else None,
                        type_specific_data={
                            "template_text": "Field: [BLANK_1]",
                            "blanks": [{"blank_id": "BLANK_1", "max_words": 2}]
                        } if "completion" in q_type else (
                            {
                                "items": [{"item_number": q_num, "item_text": "Item to match"}],
                                "options": [
                                    {"option_label": "A", "option_text": "Answer Option A"},
                                    {"option_label": "B", "option_text": "Answer Option B"},
                                    {"option_label": "C", "option_text": "Answer Option C"},
                                    {"option_label": "D", "option_text": "Answer Option D"}
                                ],
                                "allow_option_reuse": False
                            } if "matching" in q_type else {
                                "options": [
                                    {"option_label": "A", "option_text": "Option A"},
                                    {"option_label": "B", "option_text": "Option B"},
                                    {"option_label": "C", "option_text": "Option C"}
                                ],
                                "allow_multiple": False
                            }
                        ),
                        answer_data={
                            "blanks": {"BLANK_1": ["Answer"]}
                        } if "completion" in q_type else (
                            {str(q_num): "A"} if "matching" in q_type else {"correct_options": ["A"]}
                        )
                    )
                    db.add(q)
                    db.flush()
                    db.add(ListeningAnswer(question_id=q.id, correct_answer="Answer" if "completion" in q_type else "A"))
                db.commit()

            logger.info("Populated Listening Section with 40 questions")

        # 5. Populate Reading Section
        reading_section = sections[SectionType.READING]
        if not db.query(ReadingPassage).filter(ReadingPassage.section_id == reading_section.id).first():
            # Create 3 Passages
            questions_per_passage = [13, 13, 14]
            current_q = 1
            
            for p_idx, q_count in enumerate(questions_per_passage):
                passage_num = p_idx + 1
                passage = ReadingPassage(
                    section_id=reading_section.id,
                    passage_number=passage_num,
                    title=f"Reading Passage {passage_num}",
                    content=f"Content for Passage {passage_num}..." * 50,
                    order=passage_num
                )
                db.add(passage)
                db.commit()
                
                for i in range(q_count):
                    q_num = current_q
                    q_type = "reading_multiple_choice" # Default
                    
                    if passage_num == 1 and i < 5:
                        q_type = "reading_true_false_not_given"
                    elif passage_num == 2 and i < 5:
                        q_type = "reading_matching_headings"
                    elif passage_num == 3 and i < 5:
                        q_type = "reading_summary_completion"
                        
                    q = ReadingQuestion(
                        passage_id=passage.id,
                        question_number=q_num,
                        question_type=q_type,
                        question_text=f"Question {q_num}...",
                        order=q_num,
                        marks=1,
                        has_options=(q_type == "reading_multiple_choice"),
                        options=[{"option_label": "A", "option_text": "Option A"}, {"option_label": "B", "option_text": "Option B"}, {"option_label": "C", "option_text": "Option C"}, {"option_label": "D", "option_text": "Option D"}] if q_type == "reading_multiple_choice" else None,
                        type_specific_data={
                            "statements": [{"statement_number": 1, "statement_text": "Statement..."}],
                            "answer_type": "true_false_not_given"
                        } if "true_false" in q_type else (
                            {
                                "items": [{"item_number": q_num, "item_text": "Item to match"}],
                                "options": [
                                    {"option_label": "A", "option_text": "Heading Option A"},
                                    {"option_label": "B", "option_text": "Heading Option B"},
                                    {"option_label": "C", "option_text": "Heading Option C"},
                                    {"option_label": "D", "option_text": "Heading Option D"}
                                ],
                                "allow_option_reuse": False
                            } if "matching" in q_type else (
                                {
                                    "template_text": "Summary: [BLANK_1]",
                                    "blanks": [{"blank_id": "BLANK_1", "max_words": 2}]
                                } if "completion" in q_type else {
                                    "options": [
                                        {"option_label": "A", "option_text": "Option A"},
                                        {"option_label": "B", "option_text": "Option B"},
                                        {"option_label": "C", "option_text": "Option C"},
                                        {"option_label": "D", "option_text": "Option D"}
                                    ],
                                    "allow_multiple": False
                                }
                            )
                        ),
                        answer_data={
                            "1": "TRUE"
                        } if "true_false" in q_type else (
                            {str(q_num): "A"} if "matching" in q_type else (
                                {"blanks": {"BLANK_1": ["Answer"]}} if "completion" in q_type else {"correct_options": ["A"]}
                            )
                        )
                    )
                    db.add(q)
                    db.flush()
                    db.add(ReadingAnswer(question_id=q.id, correct_answer="TRUE" if "true_false" in q_type else "A"))
                    current_q += 1
                db.commit()
            
            logger.info("Populated Reading Section with 40 questions")

        # 6. Populate Writing Section
        writing_section = sections[SectionType.WRITING]
        if not db.query(WritingTask).filter(WritingTask.section_id == writing_section.id).first():
            task1 = WritingTask(
                section_id=writing_section.id,
                task_number=1,
                task_type="writing_task_1",
                prompt_text="The chart below shows the number of men and women in further education in Britain in three periods and whether they were studying full-time or part-time. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
                image_url="https://example.com/chart.png",
                word_limit_min=150,
                time_limit_minutes=20
            )
            db.add(task1)
            
            task2 = WritingTask(
                section_id=writing_section.id,
                task_number=2,
                task_type="writing_task_2",
                prompt_text="Some people believe that unpaid community service should be a compulsory part of high school programmes (for example working for a charity, improving the neighbourhood or teaching sports to younger children). To what extent do you agree or disagree?",
                word_limit_min=250,
                time_limit_minutes=40
            )
            db.add(task2)
            db.commit()
            logger.info("Populated Writing Section")

        # 7. Populate Speaking Section
        speaking_section = sections[SectionType.SPEAKING]
        if not db.query(SpeakingTask).filter(SpeakingTask.section_id == speaking_section.id).first():
            part1 = SpeakingTask(
                section_id=speaking_section.id,
                part_number=1,
                task_type="speaking_part_1",
                prompt_text="Let's talk about your hometown. Where is your hometown? What do you like about it?",
                speaking_time_seconds=300,
                order=1
            )
            db.add(part1)
            
            part2 = SpeakingTask(
                section_id=speaking_section.id,
                part_number=2,
                task_type="speaking_part_2",
                prompt_text="Describe a book you have recently read.",
                preparation_time_seconds=60,
                speaking_time_seconds=120,
                order=2,
                cue_card_points=[
                    "What the book is",
                    "Who wrote it",
                    "What it is about",
                    "And explain why you liked or disliked it"
                ]
            )
            db.add(part2)
            
            part3 = SpeakingTask(
                section_id=speaking_section.id,
                part_number=3,
                task_type="speaking_part_3",
                prompt_text="How have reading habits changed in your country in recent years?",
                speaking_time_seconds=300,
                order=3
            )
            db.add(part3)
            db.commit()
            logger.info("Populated Speaking Section")

        logger.info("Database seeding completed successfully!")

    except Exception as e:
        import traceback
        error_msg = f"Error seeding database: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        with open("/app/seed_error.log", "w") as f:
            f.write(error_msg)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()

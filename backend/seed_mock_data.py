"""
Seed script to create a full IELTS Mock Test with all question types
"""
import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    User, TestTemplate, TestSection, ListeningPart, ListeningQuestion,
    ReadingPassage, ReadingQuestion, WritingTask, SpeakingTask,
    QuestionTypeEnum
)

def seed_mock_data():
    db = SessionLocal()
    try:
        print("🌱 Seeding mock test data...")

        # Get admin user
        admin = db.query(User).filter(User.email == "admin@ielts.com").first()
        if not admin:
            print("❌ Admin user not found. Please run seed_admin.py first.")
            return

        # 1. Create Test Template
        test = TestTemplate(
            title="IELTS Academic Mock Test 1",
            description="A full-length academic mock test with all question types.",
            test_type="academic",
            difficulty_level="intermediate",
            duration_minutes=164,
            is_published=True,
            created_by=admin.id
        )
        db.add(test)
        db.commit()
        db.refresh(test)
        print(f"✅ Created Test: {test.title}")

        # 2. Create Sections (Auto-created by router, but we are doing manual here so we create them)
        # Check if sections exist (they shouldn't if we just created the test manually without router logic)
        # Actually, let's create them manually to be sure.
        
        # Listening Section
        listening_section = TestSection(
            test_template_id=test.id,
            section_type="listening",
            order=1,
            total_questions=40,
            duration_minutes=30
        )
        db.add(listening_section)
        
        # Reading Section
        reading_section = TestSection(
            test_template_id=test.id,
            section_type="reading",
            order=2,
            total_questions=40,
            duration_minutes=60
        )
        db.add(reading_section)
        
        # Writing Section
        writing_section = TestSection(
            test_template_id=test.id,
            section_type="writing",
            order=3,
            total_questions=2,
            duration_minutes=60
        )
        db.add(writing_section)
        
        # Speaking Section
        speaking_section = TestSection(
            test_template_id=test.id,
            section_type="speaking",
            order=4,
            total_questions=3,
            duration_minutes=14
        )
        db.add(speaking_section)
        db.commit()
        
        # Refresh to get IDs
        db.refresh(listening_section)
        db.refresh(reading_section)
        db.refresh(writing_section)
        db.refresh(speaking_section)
        print("✅ Created 4 Test Sections")

        # 3. Populate Listening
        # Part 1: Multiple Choice
        part1 = ListeningPart(
            section_id=listening_section.id,
            part_number=1,
            audio_url="https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav", # Mock URL
            transcript="This is a transcript for Part 1."
        )
        db.add(part1)
        db.commit()
        db.refresh(part1)

        q1 = ListeningQuestion(
            section_id=listening_section.id,
            part_id=part1.id,
            question_number=1,
            question_type=QuestionTypeEnum.LISTENING_MULTIPLE_CHOICE,
            question_text="What is the main topic of the conversation?",
            order=1,
            has_options=True,
            options=[
                {"option_label": "A", "option_text": "University admission"},
                {"option_label": "B", "option_text": "Job interview"},
                {"option_label": "C", "option_text": "Renting an apartment"},
                {"option_label": "D", "option_text": "Booking a flight"}
            ],
            marks=1
        )
        db.add(q1)

        # Part 2: Map/Diagram
        part2 = ListeningPart(
            section_id=listening_section.id,
            part_number=2,
            audio_url="https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand60.wav",
            transcript="Transcript for Part 2 map."
        )
        db.add(part2)
        db.commit()
        db.refresh(part2)

        q2 = ListeningQuestion(
            section_id=listening_section.id,
            part_id=part2.id,
            question_number=11,
            question_type=QuestionTypeEnum.LISTENING_MAP_DIAGRAM,
            question_text="Label the library on the map.",
            order=1,
            marks=1,
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Map_of_Geneva.svg/1200px-Map_of_Geneva.svg.png" # Mock Map
        )
        db.add(q2)

        # Part 3: Matching
        part3 = ListeningPart(
            section_id=listening_section.id,
            part_number=3,
            audio_url="https://www2.cs.uic.edu/~i101/SoundFiles/PinkPanther60.wav",
            transcript="Transcript for Part 3."
        )
        db.add(part3)
        db.commit()
        db.refresh(part3)

        q3 = ListeningQuestion(
            section_id=listening_section.id,
            part_id=part3.id,
            question_number=21,
            question_type=QuestionTypeEnum.LISTENING_MATCHING,
            question_text="Match the student to their project topic.",
            order=1,
            has_options=True,
            options=[
                {"option_label": "A", "option_text": "Climate Change"},
                {"option_label": "B", "option_text": "Urban Planning"},
                {"option_label": "C", "option_text": "Marine Biology"}
            ],
            marks=1
        )
        db.add(q3)

        # Part 4: Fill in Blank (Loop to fill up to 40 questions)
        part4 = ListeningPart(
            section_id=listening_section.id,
            part_number=4,
            audio_url="https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav",
            transcript="Transcript for Part 4."
        )
        db.add(part4)
        db.commit()
        db.refresh(part4)

        # Create questions 31-40
        for i in range(31, 41):
            q = ListeningQuestion(
                section_id=listening_section.id,
                part_id=part4.id,
                question_number=i,
                question_type=QuestionTypeEnum.LISTENING_FILL_IN_BLANK,
                question_text=f"The lecture discusses the impact of ______ on global economy (Question {i}).",
                order=i,
                marks=1
            )
            db.add(q)
        
        print("✅ Populated Listening Section (40 Questions)")

        # 4. Populate Reading
        passage1 = ReadingPassage(
            section_id=reading_section.id,
            passage_number=1,
            title="The History of Silk",
            content="Silk is a natural protein fiber, some forms of which can be woven into textiles. The protein fiber of silk is composed mainly of fibroin and is produced by certain insect larvae to form cocoons. The best-known silk is obtained from the cocoons of the larvae of the mulberry silkworm Bombyx mori reared in captivity (sericulture). The shimmering appearance of silk is due to the triangular prism-like structure of the silk fibre, which allows silk cloth to refract incoming light at different angles, thus producing different colors.",
            order=1,
            word_count=500
        )
        db.add(passage1)
        db.commit()
        db.refresh(passage1)

        # Create questions 1-13 for Passage 1
        for i in range(1, 14):
            q_type = QuestionTypeEnum.READING_TRUE_FALSE_NOT_GIVEN if i <= 7 else QuestionTypeEnum.READING_MULTIPLE_CHOICE
            rq = ReadingQuestion(
                passage_id=passage1.id,
                question_number=i,
                question_type=q_type,
                question_text=f"Sample reading question {i} about Silk.",
                order=i,
                has_options=(q_type == QuestionTypeEnum.READING_MULTIPLE_CHOICE),
                options=[
                    {"option_label": "A", "option_text": "Option A"},
                    {"option_label": "B", "option_text": "Option B"},
                    {"option_label": "C", "option_text": "Option C"},
                    {"option_label": "D", "option_text": "Option D"}
                ] if q_type == QuestionTypeEnum.READING_MULTIPLE_CHOICE else None,
                marks=1
            )
            db.add(rq)
            
        # Passage 2 (Questions 14-26)
        passage2 = ReadingPassage(
            section_id=reading_section.id,
            passage_number=2,
            title="The Future of AI",
            content="Artificial Intelligence (AI) is rapidly evolving...",
            order=2,
            word_count=600
        )
        db.add(passage2)
        db.commit()
        db.refresh(passage2)
        
        for i in range(14, 27):
            rq = ReadingQuestion(
                passage_id=passage2.id,
                question_number=i,
                question_type=QuestionTypeEnum.READING_MATCHING_HEADINGS,
                question_text=f"Match the heading for paragraph {i-13}.",
                order=i,
                marks=1
            )
            db.add(rq)

        # Passage 3 (Questions 27-40)
        passage3 = ReadingPassage(
            section_id=reading_section.id,
            passage_number=3,
            title="Space Exploration",
            content="Space exploration is the use of astronomy and space technology...",
            order=3,
            word_count=700
        )
        db.add(passage3)
        db.commit()
        db.refresh(passage3)
        
        for i in range(27, 41):
            rq = ReadingQuestion(
                passage_id=passage3.id,
                question_number=i,
                question_type=QuestionTypeEnum.READING_SENTENCE_COMPLETION,
                question_text=f"Space exploration helps us understand ______ (Question {i}).",
                order=i,
                marks=1
            )
            db.add(rq)

        print("✅ Populated Reading Section (40 Questions)")

        # 5. Populate Writing
        wt1 = WritingTask(
            section_id=writing_section.id,
            task_number=1,
            task_type=QuestionTypeEnum.WRITING_TASK1_ACADEMIC,
            prompt_text="The chart below shows the number of men and women in further education in Britain in three periods and whether they were studying full-time or part-time. Summarise the information by selecting and reporting the main features, and make comparisons where relevant.",
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Standard_deviation_diagram.svg/1200px-Standard_deviation_diagram.svg.png", # Safe Wiki Image
            word_limit_min=150,
            time_limit_minutes=20
        )
        db.add(wt1)

        wt2 = WritingTask(
            section_id=writing_section.id,
            task_number=2,
            task_type=QuestionTypeEnum.WRITING_TASK2_ESSAY,
            prompt_text="Some people believe that unpaid community service should be a compulsory part of high school programmes (for example working for a charity, improving the neighbourhood or teaching sports to younger children). To what extent do you agree or disagree?",
            word_limit_min=250,
            time_limit_minutes=40
        )
        db.add(wt2)
        print("✅ Populated Writing Section")

        # 6. Populate Speaking
        st1 = SpeakingTask(
            section_id=speaking_section.id,
            part_number=1,
            task_type=QuestionTypeEnum.SPEAKING_PART1,
            prompt_text="Let's talk about your home town. Where is your home town?",
            speaking_time_seconds=300,
            order=1
        )
        db.add(st1)

        st2 = SpeakingTask(
            section_id=speaking_section.id,
            part_number=2,
            task_type=QuestionTypeEnum.SPEAKING_PART2,
            prompt_text="Describe a book you have recently read.",
            cue_card_points=[
                "What the book is",
                "Who wrote it",
                "What it is about",
                "And explain why you liked or disliked it"
            ],
            preparation_time_seconds=60,
            speaking_time_seconds=120,
            order=2
        )
        db.add(st2)
        print("✅ Populated Speaking Section")

        db.commit()
        print("\n🎉 Mock data seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding mock data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_mock_data()

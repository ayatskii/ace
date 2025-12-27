import pytest
from app.services.grading_service import GradingService
from app.models import (
    TestAttempt, ListeningSubmission, ReadingSubmission, 
    WritingSubmission, SpeakingSubmission, WritingGrade, SpeakingGrade,
    TestResult, ListeningQuestion, ReadingQuestion
)
from datetime import datetime, timezone

# --- Unit Tests ---

def test_calculate_band_score():
    # Exact
    assert GradingService.calculate_band_score(6.0, 6.0, 6.0, 6.0) == 6.0
    # Round up to .5
    assert GradingService.calculate_band_score(6.1) == 6.0 # 6.1 -> 6.0
    assert GradingService.calculate_band_score(6.25) == 6.5 # 6.25 -> 6.5
    assert GradingService.calculate_band_score(6.75) == 7.0 # 6.75 -> 7.0
    assert GradingService.calculate_band_score(6.875) == 7.0 # 6.875 -> 7.0
    # Empty
    assert GradingService.calculate_band_score() == 0.0

def test_convert_correct_answers_to_band():
    # Max score
    assert GradingService.convert_correct_answers_to_band(40, 40, "listening") == 9.0
    # Min score
    assert GradingService.convert_correct_answers_to_band(0, 40, "listening") == 2.5
    # Mid range
    assert GradingService.convert_correct_answers_to_band(30, 40, "listening") == 7.0 # 75%
    # Empty total
    assert GradingService.convert_correct_answers_to_band(10, 0, "listening") == 0.0

# --- Integration Tests ---

def test_calculate_listening_score(db, submission_factory, test_template_factory):
    # Create template with sections
    template = test_template_factory()
    listening_section = next(s for s in template.sections if s.section_type == "listening")
    
    # Create 40 questions
    for i in range(40):
        q = ListeningQuestion(
            section_id=listening_section.id,
            part_id=1, # Assuming part 1 exists or not enforced by FK (it is enforced usually, but let's check model)
            # Wait, ListeningQuestion needs part_id. 
            # test_template_factory doesn't create parts for listening.
            # I need to create a part first.
            question_number=i+1,
            question_type="listening_multiple_choice",
            question_text="q",
            order=i+1
        )
        # Hack: if part_id is required, I need to create a part.
        # Let's check ListeningQuestion model. It has part_id.
        # And ListeningPart model.
        # I'll create a part.
        pass

    # Better approach: Create a part and questions properly
    from app.models import ListeningPart
    part = ListeningPart(section_id=listening_section.id, part_number=1, audio_url="url")
    db.add(part)
    db.commit()
    db.refresh(part)

    questions = []
    for i in range(40):
        q = ListeningQuestion(
            section_id=listening_section.id,
            part_id=part.id,
            question_number=i+1,
            question_type="listening_multiple_choice",
            question_text="q",
            order=i+1
        )
        db.add(q)
        questions.append(q)
    db.commit()
    
    # Create attempt
    submission = submission_factory(template=template, submission_type="writing") 
    attempt_id = submission.test_attempt_id
    
    # Create listening submissions
    # 30 correct out of 40 -> 7.0
    for i, q in enumerate(questions):
        sub = ListeningSubmission(
            test_attempt_id=attempt_id,
            question_id=q.id,
            user_answer="ans",
            is_correct=(i < 30)
        )
        db.add(sub)
    db.commit()
    
    score = GradingService.calculate_listening_score(db, attempt_id)
    assert score == 7.0

def test_calculate_reading_score(db, submission_factory, test_template_factory):
    template = test_template_factory()
    reading_section = next(s for s in template.sections if s.section_type == "reading")
    
    # Create passage
    from app.models import ReadingPassage
    passage = ReadingPassage(section_id=reading_section.id, passage_number=1, title="t", content="c", order=1, word_count=100)
    db.add(passage)
    db.commit()
    db.refresh(passage)

    questions = []
    for i in range(40):
        q = ReadingQuestion(
            passage_id=passage.id,
            question_number=i+1,
            question_type="reading_multiple_choice",
            question_text="q",
            order=i+1
        )
        db.add(q)
        questions.append(q)
    db.commit()
    
    # Create attempt
    submission = submission_factory(template=template, submission_type="writing") 
    attempt_id = submission.test_attempt_id
    
    # Create reading submissions
    # 35 correct out of 40 -> 8.0
    for i, q in enumerate(questions):
        sub = ReadingSubmission(
            test_attempt_id=attempt_id,
            question_id=q.id,
            user_answer="ans",
            is_correct=(i < 35)
        )
        db.add(sub)
    db.commit()
    
    score = GradingService.calculate_reading_score(db, attempt_id)
    assert score == 8.0

def test_get_writing_score(db, submission_factory):
    # Create attempt with writing submission
    submission = submission_factory(submission_type="writing", status="graded")
    attempt_id = submission.test_attempt_id
    
    # Add grade
    grade = WritingGrade(
        submission_id=submission.id,
        overall_band_score=6.5,
        task_achievement_score=6.0,
        coherence_cohesion_score=7.0,
        lexical_resource_score=6.0,
        grammatical_range_score=7.0,
        feedback_text="Good"
    )
    db.add(grade)
    db.commit()
    
    score = GradingService.get_writing_score(db, attempt_id)
    assert score == 6.5

def test_get_speaking_score(db, submission_factory):
    # Create attempt with speaking submission
    submission = submission_factory(submission_type="speaking", status="graded")
    attempt_id = submission.test_attempt_id
    
    # Add grade
    grade = SpeakingGrade(
        submission_id=submission.id,
        overall_band_score=7.5,
        fluency_coherence_score=7.0,
        lexical_resource_score=8.0,
        grammatical_range_score=7.0,
        pronunciation_score=8.0,
        feedback_text="Excellent"
    )
    db.add(grade)
    db.commit()
    
    score = GradingService.get_speaking_score(db, attempt_id)
    assert score == 7.5

def test_calculate_overall_score(db, submission_factory, test_template_factory):
    # Setup full test attempt
    template = test_template_factory()
    
    # Create Listening Questions
    from app.models import ListeningPart
    l_sec = next(s for s in template.sections if s.section_type == "listening")
    l_part = ListeningPart(section_id=l_sec.id, part_number=1, audio_url="url")
    db.add(l_part)
    db.commit()
    l_questions = []
    for i in range(40):
        q = ListeningQuestion(section_id=l_sec.id, part_id=l_part.id, question_number=i+1, question_type="mcq", question_text="q", order=i+1)
        db.add(q)
        l_questions.append(q)
        
    # Create Reading Questions
    from app.models import ReadingPassage
    r_sec = next(s for s in template.sections if s.section_type == "reading")
    r_pass = ReadingPassage(section_id=r_sec.id, passage_number=1, title="t", content="c", order=1, word_count=100)
    db.add(r_pass)
    db.commit()
    r_questions = []
    for i in range(40):
        q = ReadingQuestion(passage_id=r_pass.id, question_number=i+1, question_type="mcq", question_text="q", order=i+1)
        db.add(q)
        r_questions.append(q)
    db.commit()

    submission = submission_factory(template=template, submission_type="writing")
    attempt_id = submission.test_attempt_id
    
    # Listening: 6.0 (23/40 = 57.5% -> 5.5? No, 23 is 5.5, 24 is 6.0. Wait. 23/40=0.575. 
    # 60% is 6.0. 24/40 = 0.6.
    # Let's use 24 correct for 6.0
    for i, q in enumerate(l_questions):
        db.add(ListeningSubmission(test_attempt_id=attempt_id, question_id=q.id, user_answer="a", is_correct=(i < 24)))
    
    # Reading: 7.0 (30/40 = 75%)
    for i, q in enumerate(r_questions):
        db.add(ReadingSubmission(test_attempt_id=attempt_id, question_id=q.id, user_answer="a", is_correct=(i < 30)))
        
    # Writing: 6.5
    # submission_factory already created a writing submission
    w_sub = submission
    w_sub.status = "graded"
    w_sub.word_count = 100
    w_sub.response_text = "text"
    db.add(w_sub)
    db.flush()
    db.add(WritingGrade(
        submission_id=w_sub.id, 
        overall_band_score=6.5,
        task_achievement_score=6.0,
        coherence_cohesion_score=7.0,
        lexical_resource_score=6.0,
        grammatical_range_score=7.0,
        feedback_text="Good"
    ))
    
    # Speaking: 7.5
    s_sec = next(s for s in template.sections if s.section_type == "speaking")
    s_task = s_sec.speaking_tasks[0]
    s_sub = SpeakingSubmission(test_attempt_id=attempt_id, task_id=s_task.id, audio_url="url", status="graded", duration_seconds=100)
    db.add(s_sub)
    db.flush()
    db.add(SpeakingGrade(
        submission_id=s_sub.id, 
        overall_band_score=7.5,
        fluency_coherence_score=7.0,
        lexical_resource_score=8.0,
        grammatical_range_score=7.0,
        pronunciation_score=8.0
    ))
    
    db.commit()
    
    l, r, w, s, overall = GradingService.calculate_overall_score(db, attempt_id)
    
    assert l == 6.0
    assert r == 7.0
    assert w == 6.5
    assert s == 7.5
    assert overall == 7.0

def test_generate_test_result(db, submission_factory, test_template_factory):
    template = test_template_factory()
    l_sec = next(s for s in template.sections if s.section_type == "listening")
    from app.models import ListeningPart
    l_part = ListeningPart(section_id=l_sec.id, part_number=1, audio_url="url")
    db.add(l_part)
    db.commit()
    q = ListeningQuestion(section_id=l_sec.id, part_id=l_part.id, question_number=1, question_type="mcq", question_text="q", order=1)
    db.add(q)
    db.commit()

    submission = submission_factory(template=template, submission_type="writing")
    attempt_id = submission.test_attempt_id
    
    # Add some data
    db.add(ListeningSubmission(test_attempt_id=attempt_id, question_id=q.id, user_answer="a", is_correct=True))
    db.commit()
    
    result = GradingService.generate_test_result(db, attempt_id)
    assert result.test_attempt_id == attempt_id
    assert result.overall_band_score > 0

def test_is_test_complete(db, submission_factory):
    # Case 1: Not submitted
    sub1 = submission_factory(submission_type="writing", status="pending")
    attempt1 = db.query(TestAttempt).get(sub1.test_attempt_id)
    attempt1.status = "in_progress"
    db.commit()
    assert GradingService.is_test_complete(db, attempt1.id) == False
    
    # Case 2: Submitted but not graded
    attempt1.status = "submitted"
    db.commit()
    assert GradingService.is_test_complete(db, attempt1.id) == False
    
    # Case 3: Graded
    sub1.status = "graded"
    db.commit()
    assert GradingService.is_test_complete(db, attempt1.id) == True

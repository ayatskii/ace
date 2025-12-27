from typing import List, Tuple
from sqlalchemy.orm import Session

from app.models import (
    TestAttempt,
    ListeningSubmission,
    ReadingSubmission,
    WritingSubmission,
    SpeakingSubmission,
    WritingGrade,
    SpeakingGrade,
    TestResult
)


class GradingService:
    """Service for calculating IELTS band scores"""
    
    @staticmethod
    def calculate_band_score(*scores: float) -> float:
        """
        Calculate average band score rounded to nearest 0.5
        
        IELTS band scores are rounded to nearest 0.5:
        - 6.25 → 6.5
        - 6.75 → 7.0
        - 6.1 → 6.0
        """
        if not scores:
            return 0.0
        
        avg = sum(scores) / len(scores)
        decimal_part = avg % 1
        whole_part = int(avg)
        
        if decimal_part < 0.25:
            return float(whole_part)
        elif decimal_part < 0.75:
            return whole_part + 0.5
        else:
            return float(whole_part + 1)
    
    @staticmethod
    def convert_correct_answers_to_band(correct_count: int, total: int, section_type: str) -> float:
        """
        Convert number of correct answers to IELTS band score
        
        Simplified conversion (adjust based on official IELTS scoring):
        - Listening: 40 questions
        - Reading: 40 questions
        """
        if total == 0:
            return 0.0
        
        percentage = (correct_count / total) * 100
        
        # IELTS band conversion (approximate)
        if percentage >= 97.5:
            return 9.0
        elif percentage >= 92.5:
            return 8.5
        elif percentage >= 87.5:
            return 8.0
        elif percentage >= 82.5:
            return 7.5
        elif percentage >= 75:
            return 7.0
        elif percentage >= 67.5:
            return 6.5
        elif percentage >= 60:
            return 6.0
        elif percentage >= 52.5:
            return 5.5
        elif percentage >= 45:
            return 5.0
        elif percentage >= 37.5:
            return 4.5
        elif percentage >= 30:
            return 4.0
        elif percentage >= 22.5:
            return 3.5
        elif percentage >= 15:
            return 3.0
        else:
            return 2.5
    
    @staticmethod
    def calculate_listening_score(db: Session, test_attempt_id: int) -> float:
        """Calculate listening section band score"""
        submissions = db.query(ListeningSubmission).filter(
            ListeningSubmission.test_attempt_id == test_attempt_id
        ).all()
        
        if not submissions:
            return 0.0
        
        correct_count = sum(1 for s in submissions if s.is_correct)
        total = len(submissions)
        
        return GradingService.convert_correct_answers_to_band(correct_count, total, "listening")
    
    @staticmethod
    def calculate_reading_score(db: Session, test_attempt_id: int) -> float:
        """Calculate reading section band score"""
        submissions = db.query(ReadingSubmission).filter(
            ReadingSubmission.test_attempt_id == test_attempt_id
        ).all()
        
        if not submissions:
            return 0.0
        
        correct_count = sum(1 for s in submissions if s.is_correct)
        total = len(submissions)
        
        return GradingService.convert_correct_answers_to_band(correct_count, total, "reading")
    
    @staticmethod
    def get_writing_score(db: Session, test_attempt_id: int) -> float:
        """Get writing section band score (average of all writing task grades)"""
        writing_submissions = db.query(WritingSubmission).filter(
            WritingSubmission.test_attempt_id == test_attempt_id
        ).all()
        
        grades = []
        for submission in writing_submissions:
            grade = db.query(WritingGrade).filter(
                WritingGrade.submission_id == submission.id
            ).first()
            if grade:
                grades.append(grade.overall_band_score)
        
        if not grades:
            return 0.0
        
        return GradingService.calculate_band_score(*grades)
    
    @staticmethod
    def get_speaking_score(db: Session, test_attempt_id: int) -> float:
        """Get speaking section band score (average of all speaking task grades)"""
        speaking_submissions = db.query(SpeakingSubmission).filter(
            SpeakingSubmission.test_attempt_id == test_attempt_id
        ).all()
        
        grades = []
        for submission in speaking_submissions:
            grade = db.query(SpeakingGrade).filter(
                SpeakingGrade.submission_id == submission.id
            ).first()
            if grade:
                grades.append(grade.overall_band_score)
        
        if not grades:
            return 0.0
        
        return GradingService.calculate_band_score(*grades)
    
    @staticmethod
    def calculate_overall_score(db: Session, test_attempt_id: int) -> Tuple[float, float, float, float, float]:
        """
        Calculate all section scores and overall band score
        
        Returns: (listening, reading, writing, speaking, overall)
        """
        listening_score = GradingService.calculate_listening_score(db, test_attempt_id)
        reading_score = GradingService.calculate_reading_score(db, test_attempt_id)
        writing_score = GradingService.get_writing_score(db, test_attempt_id)
        speaking_score = GradingService.get_speaking_score(db, test_attempt_id)
        
        # Overall is average of all four sections
        scores = [s for s in [listening_score, reading_score, writing_score, speaking_score] if s > 0]
        overall_score = GradingService.calculate_band_score(*scores) if scores else 0.0
        
        return listening_score, reading_score, writing_score, speaking_score, overall_score
    
    @staticmethod
    def generate_test_result(db: Session, test_attempt_id: int) -> TestResult:
        """
        Generate or update test result for an attempt
        """
        # Calculate scores
        listening, reading, writing, speaking, overall = GradingService.calculate_overall_score(
            db, test_attempt_id
        )
        
        # Check if result already exists
        existing_result = db.query(TestResult).filter(
            TestResult.test_attempt_id == test_attempt_id
        ).first()
        
        if existing_result:
            # Update existing result
            existing_result.listening_score = listening if listening > 0 else None
            existing_result.reading_score = reading if reading > 0 else None
            existing_result.writing_score = writing if writing > 0 else None
            existing_result.speaking_score = speaking if speaking > 0 else None
            existing_result.overall_band_score = overall
            db.commit()
            db.refresh(existing_result)
            return existing_result
        else:
            # Create new result
            result = TestResult(
                test_attempt_id=test_attempt_id,
                listening_score=listening if listening > 0 else None,
                reading_score=reading if reading > 0 else None,
                writing_score=writing if writing > 0 else None,
                speaking_score=speaking if speaking > 0 else None,
                overall_band_score=overall
            )
            db.add(result)
            db.commit()
            db.refresh(result)
            return result
    
    @staticmethod
    def is_test_complete(db: Session, test_attempt_id: int) -> bool:
        """
        Check if all sections of a test are completed and graded
        """
        attempt = db.query(TestAttempt).filter(TestAttempt.id == test_attempt_id).first()
        if not attempt or attempt.status != "submitted":
            return False
        
        # Check if all writing submissions are graded
        writing_submissions = db.query(WritingSubmission).filter(
            WritingSubmission.test_attempt_id == test_attempt_id
        ).all()
        
        for submission in writing_submissions:
            if submission.status != "graded":
                return False
        
        # Check if all speaking submissions are graded
        speaking_submissions = db.query(SpeakingSubmission).filter(
            SpeakingSubmission.test_attempt_id == test_attempt_id
        ).all()
        
        for submission in speaking_submissions:
            if submission.status != "graded":
                return False
        
        return True


grading_service = GradingService()

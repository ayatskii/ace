from pydantic import BaseModel, ConfigDict
from typing import Optional


class StudentStatsResponse(BaseModel):
    """Statistics for student dashboard"""
    tests_completed: int
    average_score: Optional[float]
    next_test: Optional[str]


class TeacherStatsResponse(BaseModel):
    """Statistics for teacher dashboard"""
    pending_writing: int
    pending_speaking: int
    graded_today: int
    avg_grading_time: str


class AdminStatsResponse(BaseModel):
    """Statistics for admin dashboard"""
    total_users: int
    total_students: int
    total_teachers: int
    total_tests: int
    active_tests: int
    completed_attempts: int


class RecentSubmissionResponse(BaseModel):
    """Recent submission for teacher dashboard"""
    id: int
    student_name: str
    type: str  # 'Writing' or 'Speaking'
    task: str
    submitted: str  # Relative time like "2 hours ago"
    
    model_config = ConfigDict(from_attributes=True)

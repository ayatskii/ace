from typing import Optional, List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import TestTemplate, TestSection, TestAttempt
from app.schemas.test import (
    TestTemplateCreate, TestTemplateUpdate,
    TestSectionCreate, TestSectionUpdate,
    TestAttemptCreate, TestAttemptUpdate
)


class CRUDTestTemplate(CRUDBase[TestTemplate, TestTemplateCreate, TestTemplateUpdate]):
    """CRUD operations for TestTemplate"""
    
    def get_published(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[TestTemplate]:
        """Get all published test templates"""
        return db.query(TestTemplate).filter(
            TestTemplate.is_published == True
        ).offset(skip).limit(limit).all()
    
    def get_by_type(self, db: Session, *, test_type: str, skip: int = 0, limit: int = 100):
        """Get tests by type (academic/general_training)"""
        return db.query(TestTemplate).filter(
            TestTemplate.test_type == test_type,
            TestTemplate.is_published == True
        ).offset(skip).limit(limit).all()
    
    def get_by_creator(self, db: Session, *, creator_id: int, skip: int = 0, limit: int = 100):
        """Get tests created by a specific user"""
        return db.query(TestTemplate).filter(
            TestTemplate.created_by == creator_id
        ).offset(skip).limit(limit).all()
    
    def publish(self, db: Session, *, db_obj: TestTemplate) -> TestTemplate:
        """Publish a test template"""
        db_obj.is_published = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def unpublish(self, db: Session, *, db_obj: TestTemplate) -> TestTemplate:
        """Unpublish a test template"""
        db_obj.is_published = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDTestSection(CRUDBase[TestSection, TestSectionCreate, TestSectionUpdate]):
    """CRUD operations for TestSection"""
    
    def get_by_template(self, db: Session, *, template_id: int) -> List[TestSection]:
        """Get all sections for a test template"""
        return db.query(TestSection).filter(
            TestSection.test_template_id == template_id
        ).order_by(TestSection.order).all()
    
    def get_by_type(self, db: Session, *, template_id: int, section_type: str) -> Optional[TestSection]:
        """Get section by template and type"""
        return db.query(TestSection).filter(
            TestSection.test_template_id == template_id,
            TestSection.section_type == section_type
        ).first()


class CRUDTestAttempt(CRUDBase[TestAttempt, TestAttemptCreate, TestAttemptUpdate]):
    """CRUD operations for TestAttempt"""
    
    def get_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[TestAttempt]:
        """Get all attempts by a user"""
        return db.query(TestAttempt).filter(
            TestAttempt.user_id == user_id
        ).order_by(TestAttempt.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_in_progress(self, db: Session, *, user_id: int) -> List[TestAttempt]:
        """Get user's in-progress attempts"""
        return db.query(TestAttempt).filter(
            TestAttempt.user_id == user_id,
            TestAttempt.status == "in_progress"
        ).all()
    
    def get_by_template(self, db: Session, *, template_id: int, skip: int = 0, limit: int = 100):
        """Get all attempts for a specific template"""
        return db.query(TestAttempt).filter(
            TestAttempt.test_template_id == template_id
        ).offset(skip).limit(limit).all()
    
    def mark_submitted(self, db: Session, *, db_obj: TestAttempt) -> TestAttempt:
        """Mark attempt as submitted"""
        from datetime import datetime, timezone
        db_obj.status = "submitted"
        db_obj.end_time = datetime.now(timezone.utc)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create instances
test_template = CRUDTestTemplate(TestTemplate)
test_section = CRUDTestSection(TestSection)
test_attempt = CRUDTestAttempt(TestAttempt)

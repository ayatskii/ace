import pytest
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.crud.user import user as crud_user
from app.crud.test import test_template as crud_test_template
from app.crud.test import test_section as crud_test_section
from app.crud.test import test_attempt as crud_test_attempt
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.test import TestTemplateCreate, TestTemplateUpdate, TestSectionCreate, TestAttemptCreate
from app.models import User, TestTemplate, TestSection, TestAttempt

# ==================== Generic CRUD Tests ====================

def test_crud_base(db: Session, user_factory):
    # Create a user first for the foreign key
    user = user_factory(email="generic@test.com", role="admin")
    
    # We'll use TestTemplate as a generic model for testing CRUDBase
    # Create - pass dict to include created_by which is not in schema
    obj_in_data = {
        "title": "Generic Test",
        "description": "Generic Description",
        "test_type": "ACADEMIC",
        "duration_minutes": 60,
        "difficulty_level": "medium",
        "created_by": user.id
    }
    # Note: CRUDBase.create accepts dict too because jsonable_encoder handles it
    obj = crud_test_template.create(db, obj_in=obj_in_data)
    assert obj.title == "Generic Test"
    assert obj.id is not None
    
    # Get
    stored_obj = crud_test_template.get(db, id=obj.id)
    assert stored_obj is not None
    assert stored_obj.id == obj.id
    
    # Get Multi
    objs = crud_test_template.get_multi(db)
    assert len(objs) >= 1
    
    # Update
    update_data = TestTemplateUpdate(title="Updated Generic Test")
    updated_obj = crud_test_template.update(db, db_obj=obj, obj_in=update_data)
    assert updated_obj.title == "Updated Generic Test"
    
    # Count
    count = crud_test_template.count(db)
    assert count >= 1
    
    # Delete
    crud_test_template.delete(db, id=obj.id)
    deleted_obj = crud_test_template.get(db, id=obj.id)
    assert deleted_obj is None

# ==================== User CRUD Tests ====================

def test_create_user(db: Session):
    email = "newuser@example.com"
    password = "password123"
    user_in = UserCreate(email=email, password=password, full_name="New User", role="student")
    user = crud_user.create(db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "password_hash")

def test_authenticate_user(db: Session):
    email = "authuser@example.com"
    password = "password123"
    user_in = UserCreate(email=email, password=password, full_name="Auth User", role="student")
    user = crud_user.create(db, obj_in=user_in)
    
    authenticated_user = crud_user.authenticate(db, email=email, password=password)
    assert authenticated_user is not None
    assert authenticated_user.email == email
    
    wrong_password_user = crud_user.authenticate(db, email=email, password="wrongpassword")
    assert wrong_password_user is None
    
    non_existent_user = crud_user.authenticate(db, email="wrong@example.com", password=password)
    assert non_existent_user is None

def test_get_user_by_email(db: Session):
    email = "getbyemail@example.com"
    user_in = UserCreate(email=email, password="password", full_name="Email User", role="student")
    crud_user.create(db, obj_in=user_in)
    
    user = crud_user.get_by_email(db, email=email)
    assert user is not None
    assert user.email == email

def test_update_user_password(db: Session):
    email = "updatepass@example.com"
    password = "oldpassword"
    user_in = UserCreate(email=email, password=password, full_name="Pass User", role="student")
    user = crud_user.create(db, obj_in=user_in)
    
    new_password = "newpassword"
    updated_user = crud_user.update_password(db, db_obj=user, new_password=new_password)
    assert crud_user.authenticate(db, email=email, password=new_password) is not None
    assert crud_user.authenticate(db, email=email, password=password) is None

def test_get_users_by_role(db: Session):
    # Create students
    for i in range(3):
        crud_user.create(db, obj_in=UserCreate(email=f"student{i}@test.com", password="password123", role="student", full_name=f"S{i}"))
    # Create teacher
    crud_user.create(db, obj_in=UserCreate(email="teacher@test.com", password="password123", role="teacher", full_name="T"))
    
    students = crud_user.get_by_role(db, role="student")
    assert len(students) >= 3
    for s in students:
        assert s.role == "student"
        
    teachers = crud_user.get_by_role(db, role="teacher")
    assert len(teachers) >= 1
    for t in teachers:
        assert t.role == "teacher"

# ==================== Test Template CRUD Tests ====================

def test_crud_test_template_methods(db: Session, user_factory):
    # Setup
    admin = user_factory(email="creator@test.com", role="admin")
    
    # Create published test - pass dict with created_by
    t1_data = {
        "title": "Published Test", 
        "test_type": "ACADEMIC", 
        "duration_minutes": 60, 
        "is_published": True,
        "created_by": admin.id
    }
    t1 = crud_test_template.create(db, obj_in=t1_data)
    
    # Create unpublished test
    t2_data = {
        "title": "Unpublished Test", 
        "test_type": "GENERAL_TRAINING", 
        "duration_minutes": 60, 
        "is_published": False,
        "created_by": admin.id
    }
    t2 = crud_test_template.create(db, obj_in=t2_data)
    
    # Test get_published
    published = crud_test_template.get_published(db)
    assert len(published) >= 1
    assert any(t.id == t1.id for t in published)
    assert not any(t.id == t2.id for t in published)
    
    # Test get_by_type
    academic = crud_test_template.get_by_type(db, test_type="ACADEMIC")
    assert any(t.id == t1.id for t in academic)
    
    # Test get_by_creator
    created = crud_test_template.get_by_creator(db, creator_id=admin.id)
    assert len(created) >= 2
    
    # Test publish/unpublish
    crud_test_template.unpublish(db, db_obj=t1)
    assert t1.is_published == False
    
    crud_test_template.publish(db, db_obj=t2)
    assert t2.is_published == True

# ==================== Test Section CRUD Tests ====================

def test_crud_test_section_methods(db: Session, user_factory):
    # Setup template
    admin = user_factory(email="section_creator@test.com", role="admin")
    template_data = {
        "title": "Section Test", 
        "test_type": "ACADEMIC", 
        "duration_minutes": 60,
        "created_by": admin.id
    }
    template = crud_test_template.create(db, obj_in=template_data)
    
    # Create sections
    s1 = crud_test_section.create(db, obj_in=TestSectionCreate(
        test_template_id=template.id, section_type="listening", order=1, total_questions=10, duration_minutes=30
    ))
    s2 = crud_test_section.create(db, obj_in=TestSectionCreate(
        test_template_id=template.id, section_type="reading", order=2, total_questions=10, duration_minutes=60
    ))
    
    # Test get_by_template
    sections = crud_test_section.get_by_template(db, template_id=template.id)
    assert len(sections) == 2
    assert sections[0].id == s1.id
    assert sections[1].id == s2.id
    
    # Test get_by_type
    sec = crud_test_section.get_by_type(db, template_id=template.id, section_type="listening")
    assert sec.id == s1.id
    
    sec_none = crud_test_section.get_by_type(db, template_id=template.id, section_type="writing")
    assert sec_none is None

# ==================== Test Attempt CRUD Tests ====================

def test_crud_test_attempt_methods(db: Session, user_factory):
    # Setup
    user = user_factory(email="attempter@test.com")
    admin = user_factory(email="attempt_creator@test.com", role="admin")
    
    template_data = {
        "title": "Attempt Test", 
        "test_type": "ACADEMIC", 
        "duration_minutes": 60,
        "created_by": admin.id
    }
    template = crud_test_template.create(db, obj_in=template_data)
    
    # Create attempts - manually setting user_id and status because Create schema only has template_id
    # But CRUDBase.create takes obj_in. 
    # TestAttemptCreate only has test_template_id.
    # We need to pass user_id.
    
    a1_data = {
        "test_template_id": template.id,
        "user_id": user.id,
        "status": "in_progress"
    }
    a1 = crud_test_attempt.create(db, obj_in=a1_data)
    
    a2_data = {
        "test_template_id": template.id,
        "user_id": user.id,
        "status": "submitted"
    }
    a2 = crud_test_attempt.create(db, obj_in=a2_data)
    
    # Test get_by_user
    attempts = crud_test_attempt.get_by_user(db, user_id=user.id)
    assert len(attempts) >= 2
    
    # Test get_in_progress
    in_progress = crud_test_attempt.get_in_progress(db, user_id=user.id)
    assert len(in_progress) >= 1
    assert any(a.id == a1.id for a in in_progress)
    
    # Test get_by_template
    tpl_attempts = crud_test_attempt.get_by_template(db, template_id=template.id)
    assert len(tpl_attempts) == 2
    
    # Test mark_submitted
    crud_test_attempt.mark_submitted(db, db_obj=a1)
    assert a1.status == "submitted"
    assert a1.end_time is not None

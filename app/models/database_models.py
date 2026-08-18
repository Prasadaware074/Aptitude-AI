from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

import hashlib
import secrets

def hash_password(password: str) -> str:
    salt = secrets.token_hex(8)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return f"{salt}:{pw_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or ":" not in stored_hash:
        return False
    salt, pw_hash = stored_hash.split(":", 1)
    calc_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return secrets.compare_digest(pw_hash, calc_hash)

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, default="Standard Learner")
    email = Column(String, unique=True, nullable=True, index=True)
    password_hash = Column(String, nullable=True)
    token = Column(String, nullable=True, index=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(String, nullable=True)
    is_onboarded = Column(Boolean, default=False)
    user_level = Column(String, default="Beginner") # Beginner, Intermediate, Advanced
    diagnostic_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class TopicModel(Base):
    __tablename__ = "topics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False) # Quantitative Aptitude, Logical Reasoning, Verbal Ability
    description = Column(Text, nullable=True)

class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String, nullable=False) # option_a, option_b, option_c, option_d
    explanation = Column(Text, nullable=False)
    topic = Column(String, nullable=False)
    category = Column(String, nullable=False)
    difficulty = Column(String, default="medium")
    is_validated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AttemptModel(Base):
    __tablename__ = "attempts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), default="default_user")
    question_id = Column(String, ForeignKey("questions.id"), nullable=True)
    topic = Column(String, nullable=False)
    category = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    selected_answer = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Float, default=0.0) # in seconds
    timestamp = Column(DateTime, default=datetime.utcnow)

class MockTestModel(Base):
    __tablename__ = "mock_tests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), default="default_user")
    title = Column(String, nullable=False)
    category = Column(String, default="All")
    topic = Column(String, default="All")
    difficulty = Column(String, default="medium")
    total_questions = Column(Integer, nullable=False)
    time_limit_minutes = Column(Integer, nullable=False)
    score = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class MockTestQuestionModel(Base):
    __tablename__ = "mock_test_questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mock_test_id = Column(String, ForeignKey("mock_tests.id"), nullable=False)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    user_selected = Column(String, nullable=True)
    is_correct = Column(Boolean, nullable=True)

class FlashcardModel(Base):
    __tablename__ = "flashcards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), default="default_user")
    card_type = Column(String, nullable=False) # formula, shortcut, concept, vocabulary, mistake
    topic = Column(String, nullable=False)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    example = Column(Text, nullable=True)
    is_mastered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PerformanceModel(Base):
    __tablename__ = "performance"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), default="default_user")
    topic = Column(String, nullable=False)
    total_attempted = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

class StudyPlanModel(Base):
    __tablename__ = "study_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), default="default_user")
    summary = Column(Text, nullable=False)
    plan_data = Column(JSON, nullable=False) # List of plan dicts
    created_at = Column(DateTime, default=datetime.utcnow)

class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), default="default_user")
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    intent = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

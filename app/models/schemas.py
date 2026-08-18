from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- Authentication Schemas ---
class UserRegisterRequest(BaseModel):
    name: str = Field(description="User's full name")
    email: str = Field(description="User's email address")
    password: str = Field(description="User's password")

class UserLoginRequest(BaseModel):
    email: str = Field(description="User's email address")
    password: str = Field(description="User's password")

class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str
    name: str
    current_streak: int = 0
    longest_streak: int = 0
    is_onboarded: bool = False
    user_level: str = "Beginner"

class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    name: str
    current_streak: int = 0
    longest_streak: int = 0
    is_onboarded: bool = False
    user_level: str = "Beginner"

# --- Aptitude Topics & Categories ---
class CategoryTopics(BaseModel):
    category: str
    topics: List[str]

# --- Question Schemas ---
class QuestionOption(BaseModel):
    key: str # 'option_a', 'option_b', 'option_c', 'option_d'
    value: str

class QuestionSchema(BaseModel):
    id: Optional[str] = None
    question: str = Field(description="The question prompt")
    option_a: str = Field(description="Option A")
    option_b: str = Field(description="Option B")
    option_c: str = Field(description="Option C")
    option_d: str = Field(description="Option D")
    correct_answer: str = Field(description="Correct option key, e.g. option_a, option_b, option_c, option_d")
    explanation: str = Field(description="Detailed step-by-step solution")
    topic: str = Field(description="Subtopic name, e.g. Percentage, Profit and Loss")
    category: str = Field(description="Quantitative Aptitude, Logical Reasoning, or Verbal Ability")
    difficulty: str = Field(description="easy, medium, or hard")

class ValidationResult(BaseModel):
    is_valid: bool
    reasons: List[str]
    suggested_fix: Optional[str] = None

# --- Learning Agent Schemas ---
class LessonRequest(BaseModel):
    topic: str
    difficulty: Optional[str] = "medium"
    user_query: Optional[str] = None

class LessonResponse(BaseModel):
    topic: str
    category: str
    topic_overview: str
    definition: str
    core_concepts: List[str]
    important_formulas: List[str]
    explanation: str
    worked_examples: List[Dict[str, str]]
    shortcuts: List[str]
    common_mistakes: List[str]
    exam_tips: List[str]
    practice_questions: List[QuestionSchema]
    follow_up_suggestions: List[str]

# --- Practice Agent Schemas ---
class PracticeGenerateRequest(BaseModel):
    topic: str
    category: Optional[str] = "Quantitative Aptitude"
    difficulty: Optional[str] = "medium"
    number_of_questions: Optional[int] = 5

class PracticeSubmitRequest(BaseModel):
    user_id: str = "default_user"
    question_id: str
    topic: str
    category: str
    difficulty: str
    selected_answer: str # 'option_a', 'option_b', 'option_c', 'option_d'
    time_taken: Optional[float] = 0.0

class AttemptResultResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
    user_selected: str

# --- Mock Test Schemas ---
class MockTestCreateRequest(BaseModel):
    category: Optional[str] = "All"
    topic: Optional[str] = "All"
    difficulty: Optional[str] = "medium"
    number_of_questions: int = 10 # 5, 10, 20, 30, 50
    time_limit_minutes: int = 15

class UserAnswerSubmission(BaseModel):
    question_id: str
    selected_answer: Optional[str] = None # None if unattempted
    topic: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    time_taken: Optional[float] = 0.0

class OnboardingSubmitRequest(BaseModel):
    user_id: str
    submissions: List[UserAnswerSubmission]

class OnboardingResponse(BaseModel):
    user_id: str
    accuracy: float
    detected_level: str
    is_onboarded: bool
    weak_topics: List[str]
    message: str

class MockTestSubmitRequest(BaseModel):
    mock_test_id: str
    user_id: str = "default_user"
    submissions: List[UserAnswerSubmission]

class TopicPerformance(BaseModel):
    topic: str
    total: int
    correct: int
    accuracy: float

class MockQuestionDetailSchema(BaseModel):
    question_id: str
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    selected_answer: Optional[str] = None
    correct_answer: str
    is_correct: Optional[bool] = None
    explanation: str
    topic: str
    category: str
    difficulty: str

class MockTestHistorySummarySchema(BaseModel):
    mock_test_id: str
    title: str
    category: str
    topic: str
    difficulty: str
    total_questions: int
    score: float
    percentage: float
    completed: bool
    completed_at: Optional[datetime] = None

class MockTestResultResponse(BaseModel):
    mock_test_id: str
    total_questions: int
    attempted: int
    correct: int
    wrong: int
    unattempted: int
    score: float
    percentage: float
    accuracy: float
    time_taken_seconds: float
    topic_wise_accuracy: Dict[str, float]
    difficulty_wise_accuracy: Dict[str, float]
    strong_topics: List[str]
    weak_topics: List[str]
    detailed_questions: List[MockQuestionDetailSchema] = []

# --- Card Schemas ---
class FlashcardSchema(BaseModel):
    id: Optional[str] = None
    card_type: str # 'formula', 'shortcut', 'concept', 'vocabulary', 'mistake'
    topic: str
    category: str
    title: str
    content: str
    example: Optional[str] = None
    user_id: Optional[str] = "default_user"

# --- Performance & Analytics Schemas ---
class UserPerformanceSummary(BaseModel):
    user_id: str
    total_questions_attempted: int
    overall_accuracy: float
    category_accuracy: Dict[str, float]
    topic_accuracy: Dict[str, float]
    difficulty_accuracy: Dict[str, float]
    recent_trend: List[Dict[str, Any]]
    weak_topics: List[str]
    strong_topics: List[str]
    topics_needing_revision: List[str]
    current_streak: int = 0
    longest_streak: int = 0
    is_onboarded: bool = False
    user_level: str = "Beginner"

# --- Study Plan Schemas ---
class StudyPlanItem(BaseModel):
    date: str
    topic: str
    activity: str # 'Learn Concept', 'Solve Practice Questions', 'Take Mock Test', 'Revise Flashcards'
    estimated_duration_minutes: int
    number_of_questions: int
    priority: str # 'High', 'Medium', 'Low'
    reason: str

class StudyPlanResponse(BaseModel):
    user_id: str
    created_at: str
    summary: str
    plan_items: List[StudyPlanItem]

# --- Natural Language Chat / Router Schemas ---
class ChatRequest(BaseModel):
    user_id: str = "default_user"
    message: str

class ChatResponse(BaseModel):
    user_id: str
    intent: str
    reply: str
    data: Optional[Dict[str, Any]] = None

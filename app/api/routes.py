from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional

from app.models.schemas import (
    UserRegisterRequest, UserLoginRequest, AuthResponse, UserProfileResponse,
    OnboardingSubmitRequest, OnboardingResponse,
    ChatRequest, ChatResponse,
    LessonRequest, LessonResponse,
    PracticeGenerateRequest, PracticeSubmitRequest, AttemptResultResponse,
    MockTestCreateRequest, MockTestSubmitRequest, MockTestResultResponse,
    MockTestHistorySummarySchema, FlashcardSchema, UserPerformanceSummary, StudyPlanResponse, QuestionSchema
)
from app.graph.workflow import run_aptitude_workflow
from app.agents.learning_agent import LearningAgent
from app.agents.practice_agent import PracticeAgent
from app.agents.mock_agent import MockAgent
from app.agents.card_agent import CardAgent
from app.agents.performance_agent import PerformanceAgent
from app.agents.study_plan_agent import StudyPlanAgent
from app.database.connection import SessionLocal
from app.database.repository import Repository

router = APIRouter(prefix="/api")

# --- Authentication Endpoints ---
@router.post("/auth/register", response_model=AuthResponse)
def register_endpoint(request: UserRegisterRequest):
    if not request.email or not request.password or len(request.password) < 4:
        raise HTTPException(status_code=400, detail="Email and password (min 4 chars) are required")
    db = SessionLocal()
    try:
        repo = Repository(db)
        user = repo.create_user(name=request.name or "Learner", email=request.email, password=request.password)
        return AuthResponse(
            token=user.token,
            user_id=user.id,
            email=user.email,
            name=user.name,
            current_streak=user.current_streak or 1,
            longest_streak=user.longest_streak or 1,
            is_onboarded=user.is_onboarded or False,
            user_level=user.user_level or "Beginner"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    finally:
        db.close()

@router.post("/auth/login", response_model=AuthResponse)
def login_endpoint(request: UserLoginRequest):
    db = SessionLocal()
    try:
        repo = Repository(db)
        user = repo.authenticate_user(email=request.email, password=request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return AuthResponse(
            token=user.token,
            user_id=user.id,
            email=user.email,
            name=user.name,
            current_streak=user.current_streak or 0,
            longest_streak=user.longest_streak or 0,
            is_onboarded=user.is_onboarded or False,
            user_level=user.user_level or "Beginner"
        )
    finally:
        db.close()

@router.get("/auth/me", response_model=UserProfileResponse)
def get_current_user_endpoint(token: str):
    db = SessionLocal()
    try:
        repo = Repository(db)
        user = repo.get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token")
        repo.update_user_streak(user.id)
        return UserProfileResponse(
            user_id=user.id,
            email=user.email or "",
            name=user.name,
            current_streak=user.current_streak or 0,
            longest_streak=user.longest_streak or 0,
            is_onboarded=user.is_onboarded or False,
            user_level=user.user_level or "Beginner"
        )
    finally:
        db.close()

# --- Onboarding Diagnostic Endpoints ---
@router.get("/onboarding/questions", response_model=List[QuestionSchema])
def get_onboarding_questions_endpoint():
    db = SessionLocal()
    try:
        repo = Repository(db)
        questions = repo.get_questions(limit=5)
        if len(questions) < 5:
            return [
                QuestionSchema(id="diag_1", question="What is 15% of 320?", option_a="42", option_b="45", option_c="48", option_d="52", correct_answer="option_c", explanation="15% of 320 = 48", topic="Percentage", category="Quantitative Aptitude", difficulty="easy"),
                QuestionSchema(id="diag_2", question="Item bought for $200 is sold for $240. What is profit %?", option_a="15%", option_b="20%", option_c="25%", option_d="30%", correct_answer="option_b", explanation="Profit % = 40/200 * 100 = 20%", topic="Profit and Loss", category="Quantitative Aptitude", difficulty="medium"),
                QuestionSchema(id="diag_3", question="Find next term in series: 2, 4, 8, 16, ?", option_a="24", option_b="30", option_c="32", option_d="64", correct_answer="option_c", explanation="Terms double each step.", topic="Number Series", category="Logical Reasoning", difficulty="easy"),
                QuestionSchema(id="diag_4", question="All dogs are animals. All animals have four legs. Therefore...", option_a="All dogs have four legs", option_b="Some dogs are cats", option_c="No dogs have legs", option_d="None of these", correct_answer="option_a", explanation="Valid categorical syllogism.", topic="Syllogism", category="Logical Reasoning", difficulty="medium"),
                QuestionSchema(id="diag_5", question="Select the closest synonym for 'METICULOUS':", option_a="Careless", option_b="Precise", option_c="Rapid", option_d="Secret", correct_answer="option_b", explanation="Meticulous means careful and precise.", topic="Vocabulary", category="Verbal Ability", difficulty="easy")
            ]
        return [
            QuestionSchema(
                id=q.id,
                question=q.question,
                option_a=q.option_a,
                option_b=q.option_b,
                option_c=q.option_c,
                option_d=q.option_d,
                correct_answer=q.correct_answer,
                explanation=q.explanation,
                topic=q.topic,
                category=q.category,
                difficulty=q.difficulty
            )
            for q in questions
        ]
    finally:
        db.close()

@router.post("/onboarding/submit", response_model=OnboardingResponse)
def submit_onboarding_endpoint(request: OnboardingSubmitRequest):
    db = SessionLocal()
    try:
        repo = Repository(db)
        total = len(request.submissions)
        if total == 0:
            raise HTTPException(status_code=400, detail="No submissions provided")

        correct_count = 0
        weak_topics = []

        for sub in request.submissions:
            q = repo.get_question_by_id(sub.question_id)
            is_correct = False
            topic = sub.topic or (q.topic if q else "General")
            category = sub.category or (q.category if q else "Quantitative Aptitude")
            difficulty = sub.difficulty or (q.difficulty if q else "medium")
            correct_ans = q.correct_answer if q else "option_b"

            if sub.selected_answer and sub.selected_answer.lower() == correct_ans.lower():
                is_correct = True
                correct_count += 1
            else:
                if topic not in weak_topics:
                    weak_topics.append(topic)

            repo.record_attempt(
                user_id=request.user_id,
                question_id=sub.question_id,
                topic=topic,
                category=category,
                difficulty=difficulty,
                selected_answer=sub.selected_answer,
                correct_answer=correct_ans,
                is_correct=is_correct,
                time_taken=sub.time_taken
            )

        accuracy = round((correct_count / total) * 100.0, 2)
        if accuracy < 50.0:
            level = "Beginner"
        elif accuracy <= 75.0:
            level = "Intermediate"
        else:
            level = "Advanced"

        repo.complete_onboarding(request.user_id, level, accuracy)
        
        # Generate initial personalized study plan tailored to detected level
        StudyPlanAgent.generate_study_plan(request.user_id, days=5)

        return OnboardingResponse(
            user_id=request.user_id,
            accuracy=accuracy,
            detected_level=level,
            is_onboarded=True,
            weak_topics=weak_topics,
            message=f"Diagnostic assessment complete! Detected Level: {level} ({accuracy}% accuracy)."
        )
    finally:
        db.close()

# --- Chat / Multi-Agent Workflow Router Endpoint ---
@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        graph_state = run_aptitude_workflow(request.message, request.user_id)
        
        # Log conversation in DB
        db = SessionLocal()
        try:
            repo = Repository(db)
            repo.log_conversation(
                user_id=request.user_id,
                user_message=request.message,
                agent_response=graph_state.get("final_response", ""),
                intent=graph_state.get("intent", "CHAT")
            )
        except Exception as log_err:
            db.rollback()
            print(f"Conversation log notice: {log_err}")
        finally:
            db.close()

        return ChatResponse(
            user_id=request.user_id,
            intent=graph_state.get("intent", "LEARN"),
            reply=graph_state.get("final_response", "Request processed."),
            data={
                "topic": graph_state.get("topic"),
                "category": graph_state.get("category"),
                "difficulty": graph_state.get("difficulty"),
                "questions": graph_state.get("questions", []),
                "performance": graph_state.get("performance", {})
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-agent workflow error: {str(e)}")

# --- Learning Agent Endpoint ---
@router.post("/learn", response_model=LessonResponse)
def learn_endpoint(request: LessonRequest):
    try:
        return LearningAgent.generate_lesson(request.topic, request.difficulty or "medium", request.user_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning agent error: {str(e)}")

# --- Practice Agent Endpoints ---
@router.post("/practice/generate", response_model=List[QuestionSchema])
def practice_generate_endpoint(request: PracticeGenerateRequest):
    try:
        return PracticeAgent.generate_practice_questions(
            topic=request.topic,
            category=request.category or "Quantitative Aptitude",
            difficulty=request.difficulty or "medium",
            number_of_questions=request.number_of_questions or 5
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Practice generator error: {str(e)}")

@router.post("/practice/submit", response_model=AttemptResultResponse)
def practice_submit_endpoint(request: PracticeSubmitRequest):
    db = SessionLocal()
    try:
        repo = Repository(db)
        q = None
        if request.question_id and request.question_id.lower() not in ("null", "undefined"):
            q = repo.get_question_by_id(request.question_id)

        if not q and request.topic:
            topic_qs = repo.get_questions(topic=request.topic, limit=1)
            if topic_qs:
                q = topic_qs[0]

        if not q:
            is_correct = (request.selected_answer.lower() == "option_b")
            return AttemptResultResponse(
                is_correct=is_correct,
                correct_answer="option_b",
                explanation="Solution evaluated based on standard topic principles.",
                user_selected=request.selected_answer
            )

        is_correct = (request.selected_answer.lower() == q.correct_answer.lower())

        repo.record_attempt(
            user_id=request.user_id,
            question_id=q.id,
            topic=request.topic or q.topic,
            category=request.category or q.category,
            difficulty=request.difficulty or q.difficulty,
            selected_answer=request.selected_answer,
            correct_answer=q.correct_answer,
            is_correct=is_correct,
            time_taken=request.time_taken or 0.0
        )

        return AttemptResultResponse(
            is_correct=is_correct,
            correct_answer=q.correct_answer,
            explanation=q.explanation,
            user_selected=request.selected_answer
        )
    finally:
        db.close()

# --- Mock Test Endpoints ---
@router.post("/mock/create")
def mock_create_endpoint(request: MockTestCreateRequest, user_id: str = "default_user"):
    try:
        return MockAgent.create_mock_test(
            user_id=user_id,
            category=request.category or "All",
            topic=request.topic or "All",
            difficulty=request.difficulty or "medium",
            number_of_questions=request.number_of_questions,
            time_limit_minutes=request.time_limit_minutes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mock creation error: {str(e)}")

@router.post("/mock/submit", response_model=MockTestResultResponse)
def mock_submit_endpoint(request: MockTestSubmitRequest):
    try:
        total_time = sum(s.time_taken or 0.0 for s in request.submissions)
        return MockAgent.submit_mock_test(request.mock_test_id, request.submissions, total_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mock submission error: {str(e)}")

@router.get("/mock/history", response_model=List[MockTestHistorySummarySchema])
def mock_history_endpoint(user_id: str = "default_user"):
    try:
        return MockAgent.get_mock_history(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mock history error: {str(e)}")

@router.get("/mock/{mock_test_id}/result", response_model=MockTestResultResponse)
def mock_result_endpoint(mock_test_id: str):
    try:
        res = MockAgent.get_mock_result(mock_test_id)
        if not res:
            raise HTTPException(status_code=404, detail="Mock test result not found")
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mock result error: {str(e)}")

# --- Flashcards Endpoints ---
@router.get("/cards", response_model=List[FlashcardSchema])
def get_cards_endpoint(user_id: str = "default_user", topic: Optional[str] = None, card_type: Optional[str] = None):
    try:
        return CardAgent.get_cards(user_id, topic, card_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cards error: {str(e)}")

@router.post("/cards/generate", response_model=List[FlashcardSchema])
def generate_cards_endpoint(topic: str, card_type: str = "formula", user_id: str = "default_user"):
    try:
        return CardAgent.generate_cards_for_topic(topic, card_type, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Card generator error: {str(e)}")

# --- Performance Analytics Endpoints ---
@router.get("/performance", response_model=UserPerformanceSummary)
def get_performance_endpoint(user_id: str = "default_user"):
    try:
        return PerformanceAgent.get_user_performance(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance error: {str(e)}")

@router.get("/performance/weak-topics", response_model=List[str])
def get_weak_topics_endpoint(user_id: str = "default_user"):
    try:
        return PerformanceAgent.get_weak_topics(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weak topics error: {str(e)}")

# --- Study Plan Endpoint ---
@router.post("/study-plan", response_model=StudyPlanResponse)
def study_plan_endpoint(user_id: str = "default_user", days: int = 5):
    try:
        return StudyPlanAgent.generate_study_plan(user_id, days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Study plan error: {str(e)}")

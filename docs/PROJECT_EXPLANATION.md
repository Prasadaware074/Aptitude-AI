# Project Technical Documentation & Architecture Explanation

## 1. Problem Statement
Aptitude tests are a standard gateway for academic admissions, competitive exams, and job interviews across Quantitative Aptitude, Logical Reasoning, and Verbal Ability. However, existing preparation solutions suffer from static content, lack of mathematical verification in AI-generated questions, and missing adaptive personal feedback loops.

## 2. Objectives
- Build a production-grade multi-agent architecture using **LangGraph** to coordinate specialized agents.
- Integrate **Google Gemini** as the primary reasoning LLM using Pydantic structured outputs.
- Implement an **AST-based Safe Calculator** tool and a **Question Validation Pipeline** to eliminate mathematically flawed questions.
- Provide a persistent **RAG system** (ChromaDB) for authoritative educational context.
- Support full user attempt tracking, performance analytics, weak topic identification, and adaptive study plans.
- Expose a clean **FastAPI** REST backend and responsive **Frontend UI**.

## 3. System Architecture
The application uses a multi-layered design:
- **Presentation Layer**: Responsive HTML5/CSS3/JavaScript single-page application using Glassmorphic visual tokens.
- **API & Routing Layer**: FastAPI REST API endpoints connected to the LangGraph workflow orchestrator.
- **Agent Orchestration Layer**: LangGraph `StateGraph` with state dictionary (`AptitudeState`) passing intent, user history, questions, and performance context.
- **Service & Agent Layer**: 7 specialized agents (Router, Learning, Practice, Mock Test, Cards, Performance, Study Plan).
- **Data & Verification Tools**: AST Calculator tool, Question Validator pipeline, Test Scorer engine, and Performance Analyzer.
- **Persistence Layer**: SQLite database via SQLAlchemy repository pattern + ChromaDB persistent vector database.

## 4. Agent Architecture
Each agent is designed with single responsibility:
- **Router Agent**: Classifies user queries into discrete operational intents and extracts query parameters.
- **Learning Agent**: Delivers 11-section structured lessons enriched with RAG vector search snippets.
- **Practice Agent**: Generates MCQs through a candidate-generation and validation-retry loop.
- **Mock Test Agent**: Assembles multi-question test sessions, conceals correct answers until submission, and triggers detailed scoring.
- **Card Agent**: Generates and retrieves Formula, Shortcut, Concept, Vocabulary, and Mistake flashcards.
- **Performance Agent**: Computes historical accuracy metrics across topics, categories, and difficulty levels.
- **Study Plan Agent**: Creates adaptive daily schedules prioritizing weak topics.

## 5. LangGraph Workflow
LangGraph manages state transitions using `AptitudeState`.
Conditional routing function `route_intent` evaluates state intent and branches to the target node (`learning`, `practice`, `mock`, `cards`, `performance`, or `study_plan`), before returning the final response.

## 6. RAG Pipeline
The RAG pipeline indexes educational markdown documents from `knowledge_base/` using ChromaDB (`data/chroma_db`). Queries trigger vector similarity search, supplying top-k context snippets to the Learning Agent.

## 7. Question Validation Pipeline
LLMs can occasionally output incorrect math. The `QuestionValidator` enforces:
1. Four distinct options.
2. One valid correct option key.
3. Logical agreement between explanation and correct option.
4. AST mathematical check via `SafeCalculator`.
Validation failures trigger automatic question regeneration up to a retry limit.

## 8. Tool Calling & Safe Calculator
The `SafeCalculator` parses expressions using Python's `ast` module. It explicitly disallows arbitrary Python execution (`eval()`, `__import__`) and permits only safe arithmetic operations (`+`, `-`, `*`, `/`, `%`, `^`, `sqrt`, `avg`, `ncr`, `npr`, `percent_of`).

## 9. Database Design
The SQLite database stores:
- `users`: User metadata.
- `questions`: Validated MCQ storage.
- `attempts`: Individual user question attempt logs.
- `mock_tests` & `mock_test_questions`: Mock session tracking.
- `flashcards`: Study card repository.
- `performance`: Aggregated topic accuracy metrics.
- `study_plans`: Generated daily learning schedules.
- `conversations`: Chat history.

## 10. API Architecture
Built with FastAPI using Pydantic models for strict request/response validation. Endpoints feature CORS headers for frontend integration and OpenAPI interactive documentation at `/docs`.

## 11. Frontend Architecture
The UI is a modern dark-mode Glassmorphic Single Page Application featuring interactive tab switching, real-time analytics updates, practice solver cards with immediate solution feedback, timed mock test countdown timers, flappable flashcards, and an AI Tutor natural-language chat interface.

## 12. Performance Analysis & 13. Personalization
Overall accuracy is calculated as `(correct / attempted) * 100`. Weak topics are identified when topic accuracy falls below 60% with a configurable minimum attempt threshold (`MIN_ATTEMPTS_FOR_WEAK_ANALYSIS = 2`), preventing false positives from single attempts. The Study Plan Agent prioritizes these weak topics in the daily schedule.

## 14. Security
- API keys stored securely in `.env`.
- No arbitrary Python execution.
- Pydantic input sanitization and parameterized SQL queries via SQLAlchemy.

## 15. Limitations & 16. Future Scope
- **Current Limitations**: Local SQLite database; single-user state default.
- **Future Scope**: Multi-tenant OAuth2 authentication, real-time WebSocket test proctoring, support for image-based Data Interpretation charts.

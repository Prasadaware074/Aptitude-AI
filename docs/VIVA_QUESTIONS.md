# Multi-Agent Aptitude System - Viva Questions & Technical Answers

### Q1: Why did you choose LangGraph over traditional sequential LangChain chains?
**Answer:** Sequential chains follow rigid, linear execution paths. LangGraph provides graph-based stateful orchestration with conditional branching, node looping, and shared state (`AptitudeState`). This allows our Router Agent to dynamically branch to specialized agents (Learning, Practice, Mock, Cards, Performance, Study Plan) while preserving state context across turns.

---

### Q2: How do you prevent LLM mathematical hallucinations in aptitude questions?
**Answer:** We implemented a dedicated **Question Validation Pipeline** (`QuestionValidator`) coupled with an **AST Safe Calculator Tool** (`SafeCalculator`). Before a question is delivered to the user, the validator checks:
1. Four distinct options with exactly one valid correct option key.
2. Logical agreement between explanation and correct option.
3. Numerical verification: Mathematical expressions in the explanation are parsed into Python Abstract Syntax Trees (AST) and evaluated against claimed values. If validation fails, the question is regenerated up to a retry limit.

---

### Q3: Why is using `eval()` unsafe for a calculator tool, and how does your implementation solve this?
**Answer:** `eval()` can execute arbitrary, malicious Python code (such as file system deletion or code injection). Our `SafeCalculator` uses Python's `ast.parse(mode='eval')` to construct a syntax tree, recursively evaluating ONLY whitelisted mathematical AST nodes (`ast.Add`, `ast.Sub`, `ast.Mult`, `ast.Div`, `ast.Pow`) and explicit safe functions (`sqrt`, `avg`, `ncr`, `npr`, `percent_of`). Any non-whitelisted node or function raises an immediate `ValueError`.

---

### Q4: Explain the RAG pipeline architecture in your system.
**Answer:** The RAG pipeline indexes authoritative educational markdown material from `knowledge_base/` into ChromaDB (`data/chroma_db`). Text is split into overlapping chunks, embedded using Gemini embeddings (with local normalized vector fallbacks), and retrieved via cosine similarity search when the Learning Agent requires background concept definitions and formulas.

---

### Q5: How does the system calculate performance metrics and avoid misclassifying weak topics on small sample sizes?
**Answer:** Performance metrics track individual user attempts in SQLite. Topic accuracy is `(correct / attempted) * 100`. To prevent marking a topic as weak after a single failed attempt, the `PerformanceAnalyzer` checks `settings.MIN_ATTEMPTS_FOR_WEAK_ANALYSIS` (e.g., minimum 2 attempts). Only topics meeting the threshold with accuracy < 60% are flagged as weak topics.

---

### Q6: How does the Study Plan Agent personalize the daily learning schedule?
**Answer:** The Study Plan Agent inspects the user's historical performance summary. It places highest priority ("High") on weak topics identified by the Performance Agent, allocating practice MCQs and concept reviews first. It then schedules flashcard formula revisions for medium-accuracy topics, followed by timed mock tests for strong topics.

---

### Q7: How are correct answers secured during a Mock Test?
**Answer:** When a user initiates a mock test via `MockAgent.create_mock_test()`, the backend stores question entities in the database but strips `correct_answer` and `explanation` from the JSON response delivered to the frontend. Correct answers are only evaluated server-side upon calling `POST /api/mock/submit`.

---

### Q8: What database strategy is used, and how can it scale for production?
**Answer:** The system uses SQLite with SQLAlchemy ORM using clean Repository pattern methods (`Repository`). For production scale, changing `DATABASE_URL` in `.env` to PostgreSQL or MySQL requires zero code changes to repository operations or agent business logic.

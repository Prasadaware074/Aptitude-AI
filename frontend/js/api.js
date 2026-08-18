const API_BASE = "";

const ApiService = {
    getCurrentUser() {
        try {
            const raw = localStorage.getItem("aptitude_user");
            return raw ? JSON.parse(raw) : null;
        } catch(e) {
            return null;
        }
    },

    getUserId() {
        const u = this.getCurrentUser();
        return u ? u.user_id : "default_user";
    },

    async register(name, email, password) {
        const response = await fetch(`${API_BASE}/api/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password })
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || "Registration failed");
        }
        return response.json();
    },

    async login(email, password) {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || "Login failed");
        }
        return response.json();
    },

    async getMe() {
        const u = this.getCurrentUser();
        if (!u || !u.token) return null;
        const response = await fetch(`${API_BASE}/api/auth/me?token=${u.token}`);
        if (!response.ok) return null;
        return response.json();
    },

    async getDiagnosticQuestions() {
        const response = await fetch(`${API_BASE}/api/onboarding/questions`);
        if (!response.ok) throw new Error("Failed to fetch diagnostic questions");
        return response.json();
    },

    async submitOnboarding(submissions) {
        const response = await fetch(`${API_BASE}/api/onboarding/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: this.getUserId(),
                submissions
            })
        });
        if (!response.ok) throw new Error("Failed to submit diagnostic assessment");
        return response.json();
    },

    async sendChat(message, userId = null) {
        const uid = userId || this.getUserId();
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, user_id: uid })
        });
        if (!response.ok) throw new Error("Chat request failed");
        return response.json();
    },

    async getLesson(topic, difficulty = "medium", userQuery = null) {
        const response = await fetch(`${API_BASE}/api/learn`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ topic, difficulty, user_query: userQuery })
        });
        if (!response.ok) throw new Error("Failed to fetch lesson");
        return response.json();
    },

    async generatePractice(topic, category = "Quantitative Aptitude", difficulty = "medium", count = 5) {
        const response = await fetch(`${API_BASE}/api/practice/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ topic, category, difficulty, number_of_questions: parseInt(count) })
        });
        if (!response.ok) throw new Error("Failed to generate practice questions");
        return response.json();
    },

    async submitPracticeAnswer(questionId, selectedAnswer, topic, category, difficulty, timeTaken = 10.0) {
        const response = await fetch(`${API_BASE}/api/practice/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: this.getUserId(),
                question_id: questionId,
                topic,
                category,
                difficulty,
                selected_answer: selectedAnswer,
                time_taken: timeTaken
            })
        });
        if (!response.ok) throw new Error("Failed to submit practice answer");
        return response.json();
    },

    async createMockTest(category = "All", topic = "All", difficulty = "medium", count = 10, timeLimit = 15) {
        const uid = this.getUserId();
        const response = await fetch(`${API_BASE}/api/mock/create?user_id=${encodeURIComponent(uid)}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                category,
                topic,
                difficulty,
                number_of_questions: parseInt(count),
                time_limit_minutes: parseInt(timeLimit)
            })
        });
        if (!response.ok) throw new Error("Failed to create mock test");
        return response.json();
    },

    async submitMockTest(mockTestId, submissions) {
        const response = await fetch(`${API_BASE}/api/mock/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mock_test_id: mockTestId,
                user_id: this.getUserId(),
                submissions
            })
        });
        if (!response.ok) throw new Error("Failed to submit mock test");
        return response.json();
    },

    async getMockHistory(userId = null) {
        const uid = userId || this.getUserId();
        const response = await fetch(`${API_BASE}/api/mock/history?user_id=${encodeURIComponent(uid)}`);
        if (!response.ok) throw new Error("Failed to fetch mock test history");
        return response.json();
    },

    async getMockResult(mockTestId) {
        const response = await fetch(`${API_BASE}/api/mock/${mockTestId}/result`);
        if (!response.ok) throw new Error("Failed to fetch mock test result");
        return response.json();
    },

    async getCards(topic = null, cardType = null) {
        const uid = this.getUserId();
        let url = `${API_BASE}/api/cards?user_id=${encodeURIComponent(uid)}`;
        if (topic) url += `&topic=${encodeURIComponent(topic)}`;
        if (cardType && cardType !== "all") url += `&card_type=${encodeURIComponent(cardType)}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error("Failed to fetch flashcards");
        return response.json();
    },

    async getPerformance() {
        const uid = this.getUserId();
        const response = await fetch(`${API_BASE}/api/performance?user_id=${encodeURIComponent(uid)}`);
        if (!response.ok) throw new Error("Failed to fetch performance analytics");
        return response.json();
    },

    async getStudyPlan(days = 5) {
        const uid = this.getUserId();
        const response = await fetch(`${API_BASE}/api/study-plan?user_id=${encodeURIComponent(uid)}&days=${days}`, {
            method: "POST"
        });
        if (!response.ok) throw new Error("Failed to fetch study plan");
        return response.json();
    }
};

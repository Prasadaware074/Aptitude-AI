document.addEventListener("DOMContentLoaded", () => {
    // --- Auth Management ---
    const authOverlay = document.getElementById("auth-modal-overlay");
    const formLogin = document.getElementById("form-login");
    const formRegister = document.getElementById("form-register");
    const tabLoginBtn = document.getElementById("tab-login-btn");
    const tabRegisterBtn = document.getElementById("tab-register-btn");
    const loginErrorMsg = document.getElementById("login-error-msg");
    const regErrorMsg = document.getElementById("reg-error-msg");
    const btnLogout = document.getElementById("btn-logout");

    const onboardingOverlay = document.getElementById("onboarding-modal-overlay");

    function checkAuthSession() {
        const user = ApiService.getCurrentUser();
        if (user && user.user_id) {
            authOverlay.style.display = "none";
            document.getElementById("sidebar-user-name").textContent = user.name || "Learner";
            document.getElementById("sidebar-user-email").textContent = user.email ? `● ${user.email}` : "● Logged In";
            
            const initials = (user.name || "Learner").split(" ").map(n => n[0]).join("").toUpperCase().substring(0, 2);
            document.getElementById("sidebar-avatar").textContent = initials || "SL";
            btnLogout.style.display = "inline-block";

            // Update Header Streak Counter
            const streakCountEl = document.getElementById("streak-count");
            if (streakCountEl) streakCountEl.textContent = user.current_streak || 0;

            // Trigger Onboarding Assessment for un-onboarded users
            if (!user.is_onboarded) {
                loadOnboardingModal();
            } else if (onboardingOverlay) {
                onboardingOverlay.style.display = "none";
            }
        } else {
            authOverlay.style.display = "flex";
            if (onboardingOverlay) onboardingOverlay.style.display = "none";
            document.getElementById("sidebar-user-name").textContent = "Guest User";
            document.getElementById("sidebar-user-email").textContent = "● Not Signed In";
            document.getElementById("sidebar-avatar").textContent = "GU";
            btnLogout.style.display = "none";
        }
    }

    async function loadOnboardingModal() {
        if (!onboardingOverlay) return;
        onboardingOverlay.style.display = "flex";
        const container = document.getElementById("onboarding-questions-container");
        container.innerHTML = `<div class="loading-spinner">Fetching diagnostic questions...</div>`;

        try {
            const questions = await ApiService.getDiagnosticQuestions();
            if (!questions || questions.length === 0) {
                container.innerHTML = `<div class="text-muted">No diagnostic questions available.</div>`;
                return;
            }

            let html = questions.map((q, idx) => `
                <div class="mcq-card mb-md p-md glass-card">
                    <div class="mcq-header">
                        <strong>Question ${idx + 1} of ${questions.length} [${q.topic}]</strong>
                        <span class="badge-tag badge-neutral">${q.difficulty.toUpperCase()}</span>
                    </div>
                    <div class="mcq-question-text mt-xs mb-sm">${q.question}</div>
                    <div class="options-grid">
                        <label class="option-btn" style="cursor:pointer; display:block;">
                            <input type="radio" name="diag_q_${q.id}" value="option_a"> A) ${q.option_a}
                        </label>
                        <label class="option-btn" style="cursor:pointer; display:block;">
                            <input type="radio" name="diag_q_${q.id}" value="option_b"> B) ${q.option_b}
                        </label>
                        <label class="option-btn" style="cursor:pointer; display:block;">
                            <input type="radio" name="diag_q_${q.id}" value="option_c"> C) ${q.option_c}
                        </label>
                        <label class="option-btn" style="cursor:pointer; display:block;">
                            <input type="radio" name="diag_q_${q.id}" value="option_d"> D) ${q.option_d}
                        </label>
                    </div>
                </div>
            `).join("");

            html += `<button id="btn-submit-onboarding" class="btn btn-accent btn-block w-full mt-lg">Submit Diagnostic & Detect Level</button>`;
            container.innerHTML = html;

            document.getElementById("btn-submit-onboarding").addEventListener("click", async () => {
                const submissions = [];
                questions.forEach(q => {
                    const selected = container.querySelector(`input[name="diag_q_${q.id}"]:checked`);
                    submissions.push({
                        question_id: q.id,
                        selected_answer: selected ? selected.value : null,
                        topic: q.topic,
                        category: q.category,
                        difficulty: q.difficulty,
                        time_taken: 10.0
                    });
                });

                container.innerHTML = `<div class="loading-spinner">Evaluating diagnostic accuracy and generating personalized study plan...</div>`;
                try {
                    const res = await ApiService.submitOnboarding(submissions);
                    const currentUser = ApiService.getCurrentUser() || {};
                    currentUser.is_onboarded = true;
                    currentUser.user_level = res.detected_level;
                    currentUser.current_streak = 1;
                    localStorage.setItem("aptitude_user", JSON.stringify(currentUser));

                    container.innerHTML = `
                        <div class="text-center p-md">
                            <span class="big-icon">🎯</span>
                            <h2>Diagnostic Complete!</h2>
                            <p class="mt-sm">Baseline Skill Level Detected: <strong class="text-cyan">${res.detected_level}</strong> (${res.accuracy}% Accuracy)</p>
                            <p class="text-muted mt-xs">A personalized study plan tailored to your level has been generated.</p>
                            <button id="btn-finish-onboarding" class="btn btn-primary mt-lg">Start Learning Journey 🚀</button>
                        </div>
                    `;

                    document.getElementById("btn-finish-onboarding").addEventListener("click", () => {
                        onboardingOverlay.style.display = "none";
                        checkAuthSession();
                        loadDashboardData();
                        loadStudyPlanData();
                    });
                } catch (err) {
                    alert("Error submitting diagnostic: " + err.message);
                    loadOnboardingModal();
                }
            });
        } catch (e) {
            container.innerHTML = `<div class="text-muted">Error loading diagnostic assessment: ${e.message}</div>`;
        }
    }

    if (tabLoginBtn && tabRegisterBtn) {
        tabLoginBtn.addEventListener("click", () => {
            tabLoginBtn.classList.add("active");
            tabRegisterBtn.classList.remove("active");
            formLogin.style.display = "block";
            formRegister.style.display = "none";
            loginErrorMsg.style.display = "none";
        });

        tabRegisterBtn.addEventListener("click", () => {
            tabRegisterBtn.classList.add("active");
            tabLoginBtn.classList.remove("active");
            formRegister.style.display = "block";
            formLogin.style.display = "none";
            regErrorMsg.style.display = "none";
        });
    }

    if (formLogin) {
        formLogin.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value;
            loginErrorMsg.style.display = "none";

            try {
                const auth = await ApiService.login(email, password);
                localStorage.setItem("aptitude_user", JSON.stringify(auth));
                checkAuthSession();
                loadDashboardData();
            } catch (err) {
                loginErrorMsg.textContent = err.message;
                loginErrorMsg.style.display = "block";
            }
        });
    }

    if (formRegister) {
        formRegister.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("reg-name").value.trim();
            const email = document.getElementById("reg-email").value.trim();
            const password = document.getElementById("reg-password").value;
            regErrorMsg.style.display = "none";

            try {
                const auth = await ApiService.register(name, email, password);
                localStorage.setItem("aptitude_user", JSON.stringify(auth));
                checkAuthSession();
                loadDashboardData();
            } catch (err) {
                regErrorMsg.textContent = err.message;
                regErrorMsg.style.display = "block";
            }
        });
    }

    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            localStorage.removeItem("aptitude_user");
            checkAuthSession();
        });
    }

    checkAuthSession();

    // --- Navigation Tabs ---
    const navItems = document.querySelectorAll(".nav-item");
    const tabViews = document.querySelectorAll(".tab-view");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");

    const titlesMap = {
        "dashboard": { title: "Dashboard", subtitle: "Real-time learning analytics and preparation readiness" },
        "learn": { title: "Learn Topics", subtitle: "Structured concept explanations powered by RAG context" },
        "practice": { title: "Practice MCQs", subtitle: "Validated questions with AST Calculator verification" },
        "mock": { title: "Mock Tests", subtitle: "Timed full-length exam simulations" },
        "cards": { title: "Flashcards", subtitle: "Formula cards, shortcuts, concepts, and mistake logs" },
        "performance": { title: "Performance Analytics", subtitle: "Topic accuracy breakdown and weak topic detection" },
        "study-plan": { title: "Study Plan", subtitle: "Personalized adaptive daily learning schedule" },
        "tutor": { title: "AI Tutor Chat", subtitle: "Natural-language interaction with LangGraph Multi-Agent Orchestrator" }
    };

    function switchTab(tabId) {
        navItems.forEach(item => {
            if (item.getAttribute("data-tab") === tabId) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        tabViews.forEach(view => {
            if (view.id === `view-${tabId}`) {
                view.classList.add("active");
            } else {
                view.classList.remove("active");
            }
        });

        if (titlesMap[tabId]) {
            pageTitle.textContent = titlesMap[tabId].title;
            pageSubtitle.textContent = titlesMap[tabId].subtitle;
        }

        // Trigger view-specific data loading
        if (tabId === "dashboard") loadDashboardData();
        else if (tabId === "performance") loadPerformanceData();
        else if (tabId === "study-plan") loadStudyPlanData();
        else if (tabId === "cards") loadCardsData();
        else if (tabId === "mock") loadMockHistory();
    }

    const mobileMenuToggle = document.getElementById("mobile-menu-toggle");
    const sidebar = document.querySelector(".sidebar");

    if (mobileMenuToggle && sidebar) {
        mobileMenuToggle.addEventListener("click", (e) => {
            e.stopPropagation();
            sidebar.classList.toggle("open");
        });

        document.addEventListener("click", (e) => {
            if (window.innerWidth <= 1024 && sidebar.classList.contains("open") && !sidebar.contains(e.target) && e.target !== mobileMenuToggle) {
                sidebar.classList.remove("open");
            }
        });
    }

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            switchTab(item.getAttribute("data-tab"));
            if (window.innerWidth <= 1024 && sidebar) {
                sidebar.classList.remove("open");
            }
        });
    });

    document.getElementById("btn-quick-practice").addEventListener("click", () => switchTab("practice"));
    document.getElementById("btn-today-plan").addEventListener("click", () => switchTab("study-plan"));

    // --- Dashboard Data Loading ---
    async function loadDashboardData() {
        try {
            const perf = await ApiService.getPerformance();
            document.getElementById("dash-questions-count").textContent = perf.total_questions_attempted || 0;
            document.getElementById("dash-accuracy").textContent = `${perf.overall_accuracy || 0}%`;

            const streakCountEl = document.getElementById("streak-count");
            if (streakCountEl) streakCountEl.textContent = perf.current_streak || 0;

            const weakContainer = document.getElementById("dash-weak-topics-list");
            if (perf.weak_topics && perf.weak_topics.length > 0) {
                weakContainer.innerHTML = perf.weak_topics.map(t => `<span class="badge-tag badge-weak">⚠️ ${t} (${perf.topic_accuracy[t]}%)</span>`).join("");
            } else {
                weakContainer.innerHTML = `<span class="badge-tag badge-neutral">No weak topics flagged yet (Threshold: Min ${perf.min_attempts || 2} attempts)</span>`;
            }

            const strongContainer = document.getElementById("dash-strong-topics-list");
            if (perf.strong_topics && perf.strong_topics.length > 0) {
                strongContainer.innerHTML = perf.strong_topics.map(t => `<span class="badge-tag badge-strong">🏆 ${t} (${perf.topic_accuracy[t]}%)</span>`).join("");
            } else {
                strongContainer.innerHTML = `<span class="badge-tag badge-neutral">Keep practicing to unlock strong topic badges!</span>`;
            }
        } catch (e) {
            console.error("Dashboard error:", e);
        }
    }

    // Quick AI Router from Dashboard
    document.getElementById("dash-btn-ask").addEventListener("click", async () => {
        const query = document.getElementById("dash-quick-query").value.trim();
        if (!query) return;
        switchTab("tutor");
        sendChatMessage(query);
        document.getElementById("dash-quick-query").value = "";
    });

    // --- Learn View Handler ---
    document.getElementById("btn-generate-lesson").addEventListener("click", async () => {
        const topic = document.getElementById("learn-topic-select").value;
        const diff = document.getElementById("learn-diff-select").value;
        const container = document.getElementById("lesson-container");

        container.innerHTML = `<div class="loading-spinner">Generating comprehensive AI lesson with RAG context for ${topic}...</div>`;

        try {
            const lesson = await ApiService.getLesson(topic, diff);
            container.innerHTML = `
                <div class="lesson-view">
                    <span class="badge-tag badge-neutral">${lesson.category} | ${lesson.topic}</span>
                    <h2 class="mt-lg">${lesson.topic_overview}</h2>
                    <div class="explanation-box mt-lg">
                        <strong>Definition:</strong> ${lesson.definition}
                    </div>

                    <h3 class="mt-xl">💡 Core Concepts</h3>
                    <ul>${lesson.core_concepts.map(c => `<li class="mt-lg">${c}</li>`).join("")}</ul>

                    <h3 class="mt-xl">📐 Key Formulas</h3>
                    <div class="glass-card mt-lg">
                        ${lesson.important_formulas.map(f => `<p><code>${f}</code></p>`).join("")}
                    </div>

                    <h3 class="mt-xl">📝 Explanation & Example</h3>
                    <p class="mt-lg">${lesson.explanation}</p>
                    ${lesson.worked_examples.map(ex => `
                        <div class="glass-card mt-lg">
                            <strong>Problem:</strong> ${ex.problem}<br>
                            <span class="text-muted">Solution: ${ex.solution}</span>
                        </div>
                    `).join("")}

                    <h3 class="mt-xl">⚡ Exam Shortcuts & Tips</h3>
                    <ul>${lesson.shortcuts.map(s => `<li>${s}</li>`).join("")}</ul>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="text-muted">Error loading lesson: ${e.message}</div>`;
        }
    });

    function getCategoryForTopic(topic) {
        const reasoning = ["Number Series", "Coding-Decoding", "Syllogism", "Blood Relations", "Seating Arrangement"];
        const verbal = ["Vocabulary", "Grammar", "Reading Comprehension"];
        if (reasoning.includes(topic)) return "Logical Reasoning";
        if (verbal.includes(topic)) return "Verbal Ability";
        return "Quantitative Aptitude";
    }

    // --- Practice View Handler ---
    document.getElementById("btn-start-practice").addEventListener("click", async () => {
        const topic = document.getElementById("practice-topic-select").value;
        const diff = document.getElementById("practice-diff-select").value;
        const count = document.getElementById("practice-count-select").value;
        const container = document.getElementById("practice-mcq-container");

        container.innerHTML = `<div class="loading-spinner">Generating and validating ${count} MCQs...</div>`;

        try {
            const cat = getCategoryForTopic(topic);
            const questions = await ApiService.generatePractice(topic, cat, diff, count);
            renderPracticeQuestions(questions, container);
        } catch (e) {
            container.innerHTML = `<div class="text-muted">Error generating practice: ${e.message}</div>`;
        }
    });

    function renderPracticeQuestions(questions, container) {
        if (!questions || questions.length === 0) {
            container.innerHTML = `<div class="text-muted">No questions available.</div>`;
            return;
        }

        let html = questions.map((q, idx) => {
            const qId = q.id || ('pq_' + idx);
            return `
            <div class="mcq-card" id="q-card-${qId}">
                <div class="mcq-header">
                    <span>Question ${idx + 1} of ${questions.length} | ${q.topic}</span>
                    <span class="badge-tag badge-neutral">${(q.difficulty || 'medium').toUpperCase()}</span>
                </div>
                <div class="mcq-question-text">${q.question}</div>
                <div class="options-grid">
                    <button class="option-btn" data-qid="${qId}" data-opt="option_a">A) ${q.option_a}</button>
                    <button class="option-btn" data-qid="${qId}" data-opt="option_b">B) ${q.option_b}</button>
                    <button class="option-btn" data-qid="${qId}" data-opt="option_c">C) ${q.option_c}</button>
                    <button class="option-btn" data-qid="${qId}" data-opt="option_d">D) ${q.option_d}</button>
                </div>
                <button class="btn btn-primary btn-submit-opt" data-qid="${qId}" data-topic="${q.topic}" data-cat="${q.category}" data-diff="${q.difficulty}">Submit Answer</button>
                <div class="explanation-box hidden" id="exp-${qId}" style="display:none;"></div>
            </div>
        `;
        }).join("");

        container.innerHTML = html;

        // Selection & Submit handling
        container.querySelectorAll(".option-btn").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const qid = btn.getAttribute("data-qid");
                const card = document.getElementById(`q-card-${qid}`);
                card.querySelectorAll(".option-btn").forEach(b => b.classList.remove("selected"));
                btn.classList.add("selected");
            });
        });

        container.querySelectorAll(".btn-submit-opt").forEach(btn => {
            btn.addEventListener("click", async () => {
                const qid = btn.getAttribute("data-qid");
                const topic = btn.getAttribute("data-topic");
                const cat = btn.getAttribute("data-cat");
                const diff = btn.getAttribute("data-diff");
                const card = document.getElementById(`q-card-${qid}`);
                const selectedBtn = card.querySelector(".option-btn.selected");

                if (!selectedBtn) {
                    alert("Please select an option first!");
                    return;
                }

                const selectedOpt = selectedBtn.getAttribute("data-opt");
                try {
                    const result = await ApiService.submitPracticeAnswer(qid, selectedOpt, topic, cat, diff);
                    
                    // Style options
                    card.querySelectorAll(".option-btn").forEach(b => {
                        const optKey = b.getAttribute("data-opt");
                        if (optKey.toLowerCase() === result.correct_answer.toLowerCase()) {
                            b.classList.add("correct-opt");
                        } else if (optKey.toLowerCase() === selectedOpt.toLowerCase() && !result.is_correct) {
                            b.classList.add("wrong-opt");
                        }
                    });

                    const expBox = document.getElementById(`exp-${qid}`);
                    expBox.style.display = "block";
                    expBox.innerHTML = `
                        <strong>${result.is_correct ? '✅ Correct!' : '❌ Incorrect'}</strong><br>
                        <span class="text-muted">Solution: ${result.explanation}</span>
                    `;

                    btn.disabled = true;
                } catch (e) {
                    alert("Error submitting answer: " + e.message);
                }
            });
        });
    }

    // --- Mock Test Handler ---
    let mockTimerInterval = null;

    document.getElementById("btn-create-mock").addEventListener("click", async () => {
        const cat = document.getElementById("mock-cat-select").value;
        const topicElem = document.getElementById("mock-topic-select");
        const topic = topicElem ? topicElem.value : "All";
        const diffElem = document.getElementById("mock-diff-select");
        const diff = diffElem ? diffElem.value : "medium";
        const count = document.getElementById("mock-count-select").value;
        const container = document.getElementById("mock-active-container");

        container.innerHTML = `<div class="loading-spinner">Creating timed mock test with ${count} questions...</div>`;

        try {
            const timeLimit = parseInt(count) >= 20 ? 30 : (parseInt(count) >= 10 ? 15 : 8);
            const mock = await ApiService.createMockTest(cat, topic, diff, count, timeLimit);
            renderMockTest(mock, container);
        } catch (e) {
            container.innerHTML = `<div class="text-muted">Error creating test: ${e.message}</div>`;
        }
    });

    function renderMockTest(mock, container) {
        if (mockTimerInterval) {
            clearInterval(mockTimerInterval);
            mockTimerInterval = null;
        }

        const qList = mock.questions;
        let userAnswers = {};
        let isMockSubmitted = false;
        const mockStartTime = Date.now();
        const timeLimitMinutes = mock.time_limit_minutes || 15;
        const mockEndTime = mockStartTime + timeLimitMinutes * 60 * 1000;

        let html = `
            <div class="glass-panel mb-lg flex-between">
                <div>
                    <h2>${mock.title}</h2>
                    <p class="text-muted">${mock.total_questions} Questions | Limit: ${mock.time_limit_minutes} Minutes</p>
                </div>
                <div class="stat-value text-cyan" id="mock-timer-display">${String(timeLimitMinutes).padStart(2, '0')}:00</div>
            </div>

            <div id="mock-questions-list">
                ${qList.map((q, idx) => `
                    <div class="mcq-card">
                        <div class="mcq-header">
                            <span>Question ${idx + 1} of ${qList.length} | ${q.topic}</span>
                            <span class="badge-tag badge-neutral">${(q.difficulty || 'medium').toUpperCase()}</span>
                        </div>
                        <div class="mcq-question-text">${q.question}</div>
                        <div class="options-grid">
                            <button class="option-btn mock-opt-btn" data-qid="${q.id}" data-opt="option_a">A) ${q.option_a}</button>
                            <button class="option-btn mock-opt-btn" data-qid="${q.id}" data-opt="option_b">B) ${q.option_b}</button>
                            <button class="option-btn mock-opt-btn" data-qid="${q.id}" data-opt="option_c">C) ${q.option_c}</button>
                            <button class="option-btn mock-opt-btn" data-qid="${q.id}" data-opt="option_d">D) ${q.option_d}</button>
                        </div>
                    </div>
                `).join("")}
            </div>

            <button id="btn-submit-mock-test" class="btn btn-primary mt-lg">🏆 Submit Complete Mock Test</button>
        `;

        container.innerHTML = html;

        // Start Real Countdown Timer based on absolute timestamp
        function updateTimer() {
            const now = Date.now();
            const remainingMs = Math.max(0, mockEndTime - now);
            const remainingSec = Math.floor(remainingMs / 1000);
            const mins = Math.floor(remainingSec / 60);
            const secs = remainingSec % 60;
            const timerEl = document.getElementById("mock-timer-display");

            if (timerEl) {
                timerEl.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
                if (remainingSec <= 60) {
                    timerEl.style.color = "#ef4444";
                }
            }

            if (remainingSec <= 0) {
                if (mockTimerInterval) {
                    clearInterval(mockTimerInterval);
                    mockTimerInterval = null;
                }
                if (!isMockSubmitted) {
                    handleMockSubmission(true);
                }
            }
        }

        updateTimer();
        mockTimerInterval = setInterval(updateTimer, 1000);

        container.querySelectorAll(".mock-opt-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                if (isMockSubmitted) return;
                const qid = btn.getAttribute("data-qid");
                const opt = btn.getAttribute("data-opt");
                userAnswers[qid] = opt;
                btn.parentElement.querySelectorAll(".mock-opt-btn").forEach(b => b.classList.remove("selected"));
                btn.classList.add("selected");
            });
        });

        async function handleMockSubmission(isTimeout = false) {
            if (isMockSubmitted) return;
            isMockSubmitted = true;

            if (mockTimerInterval) {
                clearInterval(mockTimerInterval);
                mockTimerInterval = null;
            }

            const submitBtn = document.getElementById("btn-submit-mock-test");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = isTimeout ? "⌛ Time Expired - Auto Submitting..." : "Submitting Test...";
            }

            container.querySelectorAll(".mock-opt-btn").forEach(b => {
                b.disabled = true;
                b.style.cursor = "not-allowed";
                b.style.opacity = "0.7";
            });

            const totalTimeTakenSeconds = Math.round((Date.now() - mockStartTime) / 1000);
            const submissions = qList.map(q => ({
                question_id: q.id,
                selected_answer: userAnswers[q.id] || null,
                time_taken: Math.round(totalTimeTakenSeconds / Math.max(qList.length, 1))
            }));

            try {
                const res = await ApiService.submitMockTest(mock.mock_test_id, submissions, totalTimeTakenSeconds);
                renderMockTestResults(res, container);
                loadMockHistory();
            } catch (e) {
                alert("Error submitting mock test: " + e.message);
            }
        }

        document.getElementById("btn-submit-mock-test").addEventListener("click", () => handleMockSubmission(false));
    }

    function renderMockTestResults(res, container) {
        const detailedQs = res.detailed_questions || [];

        let topicBadges = Object.entries(res.topic_wise_accuracy || {})
            .map(([t, acc]) => `<span class="badge-tag ${acc >= 75 ? 'badge-success' : acc < 60 ? 'badge-danger' : 'badge-neutral'}">${t}: ${acc}%</span>`)
            .join(" ");

        let diffBadges = Object.entries(res.difficulty_wise_accuracy || {})
            .map(([d, acc]) => `<span class="badge-tag badge-neutral">${d.toUpperCase()}: ${acc}%</span>`)
            .join(" ");

        let html = `
            <div class="glass-panel mb-lg">
                <div class="flex-between">
                    <div>
                        <h2>🏆 Mock Test Marks & Performance Analysis</h2>
                        <p class="text-muted">Test ID: ${res.mock_test_id.substring(0, 8)}...</p>
                    </div>
                    <button class="btn btn-secondary btn-sm" id="btn-back-mock-start">⬅️ Back to Test Config</button>
                </div>

                <div class="stats-grid mt-lg">
                    <div class="stat-card glass-card">
                        <div class="stat-data">
                            <span class="stat-value">${res.score} / ${res.total_questions}</span>
                            <span class="stat-label">Total Score</span>
                        </div>
                    </div>
                    <div class="stat-card glass-card">
                        <div class="stat-data">
                            <span class="stat-value">${res.percentage}%</span>
                            <span class="stat-label">Percentage</span>
                        </div>
                    </div>
                    <div class="stat-card glass-card">
                        <div class="stat-data">
                            <span class="stat-value">${res.accuracy}%</span>
                            <span class="stat-label">Accuracy</span>
                        </div>
                    </div>
                    <div class="stat-card glass-card">
                        <div class="stat-data">
                            <span class="stat-value text-cyan">${res.correct} ✅ | ${res.wrong} ❌</span>
                            <span class="stat-label">Correct / Wrong (${res.unattempted} Unattempted)</span>
                        </div>
                    </div>
                </div>

                <div class="mt-md">
                    <strong>Topic Accuracy:</strong> ${topicBadges || '<span class="text-muted">N/A</span>'}<br>
                    <strong class="mt-xs inline-block">Difficulty Accuracy:</strong> ${diffBadges || '<span class="text-muted">N/A</span>'}
                </div>

                ${res.weak_topics && res.weak_topics.length > 0 ? `
                    <div class="alert alert-warning mt-md" style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); padding: 12px; border-radius: 8px;">
                        ⚠️ <strong>Weak Topics Requiring Revision:</strong> ${res.weak_topics.join(", ")}
                    </div>
                ` : ''}
            </div>

            <h3 class="mb-md">📝 Question Solutions & Explanations (${detailedQs.length} Questions)</h3>
            <div id="mock-detailed-solutions">
                ${detailedQs.map((q, idx) => {
                    const isUnattempted = !q.selected_answer;
                    const isCorrect = q.is_correct === true;
                    
                    const badge = isUnattempted
                        ? `<span class="badge-tag badge-warning">⚠️ Unattempted</span>`
                        : (isCorrect 
                            ? `<span class="badge-tag badge-success">✅ Correct</span>` 
                            : `<span class="badge-tag badge-danger">❌ Incorrect</span>`);

                    const optClass = (optKey) => {
                        const isSelected = q.selected_answer && q.selected_answer.toLowerCase() === optKey.toLowerCase();
                        const isRight = q.correct_answer && q.correct_answer.toLowerCase() === optKey.toLowerCase();
                        if (isRight) return "correct-opt";
                        if (isSelected && !isRight) return "wrong-opt";
                        return "";
                    };

                    return `
                        <div class="mcq-card mb-lg">
                            <div class="mcq-header">
                                <span>Question ${idx + 1} of ${detailedQs.length} | ${q.topic}</span>
                                ${badge}
                            </div>
                            <div class="mcq-question-text">${q.question}</div>
                            <div class="options-grid">
                                <div class="option-btn ${optClass('option_a')}">A) ${q.option_a} ${q.selected_answer === 'option_a' ? '(Your Choice)' : ''}</div>
                                <div class="option-btn ${optClass('option_b')}">B) ${q.option_b} ${q.selected_answer === 'option_b' ? '(Your Choice)' : ''}</div>
                                <div class="option-btn ${optClass('option_c')}">C) ${q.option_c} ${q.selected_answer === 'option_c' ? '(Your Choice)' : ''}</div>
                                <div class="option-btn ${optClass('option_d')}">D) ${q.option_d} ${q.selected_answer === 'option_d' ? '(Your Choice)' : ''}</div>
                            </div>
                            <div class="explanation-box mt-md" style="display:block;">
                                <strong>Correct Answer:</strong> ${q.correct_answer.toUpperCase()}<br>
                                <span class="text-muted"><strong>Solution Explanation:</strong> ${q.explanation}</span>
                            </div>
                        </div>
                    `;
                }).join("")}
            </div>
        `;

        container.innerHTML = html;

        document.getElementById("btn-back-mock-start").addEventListener("click", () => {
            container.innerHTML = `
                <div class="placeholder-state glass-panel">
                    <span class="big-icon">⏱️</span>
                    <h3>No Active Mock Test</h3>
                    <p>Configure parameters above and click 'Create Timed Mock Test' to start your exam simulation.</p>
                </div>
            `;
        });
    }

    async function loadMockHistory() {
        const historyList = document.getElementById("mock-history-list");
        if (!historyList) return;

        try {
            const history = await ApiService.getMockHistory();
            if (!history || history.length === 0) {
                historyList.innerHTML = `<div class="text-muted">No past mock tests found. Complete a test above to view history!</div>`;
                return;
            }

            let html = history.map(item => `
                <div class="glass-card mb-md p-md flex-between flex-wrap">
                    <div>
                        <strong>${item.title}</strong><br>
                        <span class="text-muted">${item.total_questions} Questions | ${item.completed ? 'Completed' : 'Incomplete'} ${item.completed_at ? '| ' + new Date(item.completed_at).toLocaleString() : ''}</span>
                    </div>
                    <div class="flex-align gap-md mt-sm">
                        <span class="badge-tag ${item.percentage >= 75 ? 'badge-success' : item.percentage >= 50 ? 'badge-neutral' : 'badge-danger'}">Score: ${item.score}/${item.total_questions} (${item.percentage}%)</span>
                        <button class="btn btn-secondary btn-sm btn-revisit-mock" data-mockid="${item.mock_test_id}">🔍 Revisit Analysis & Solutions</button>
                    </div>
                </div>
            `).join("");

            historyList.innerHTML = html;

            historyList.querySelectorAll(".btn-revisit-mock").forEach(btn => {
                btn.addEventListener("click", async () => {
                    const mockId = btn.getAttribute("data-mockid");
                    const activeContainer = document.getElementById("mock-active-container");
                    activeContainer.innerHTML = `<div class="loading-spinner">Fetching detailed test analysis...</div>`;
                    try {
                        const res = await ApiService.getMockResult(mockId);
                        renderMockTestResults(res, activeContainer);
                        window.scrollTo({ top: activeContainer.offsetTop - 50, behavior: 'smooth' });
                    } catch (e) {
                        activeContainer.innerHTML = `<div class="text-muted">Error loading test result: ${e.message}</div>`;
                    }
                });
            });
        } catch (e) {
            historyList.innerHTML = `<div class="text-muted">Error loading history: ${e.message}</div>`;
        }
    }

    const btnRefreshHistory = document.getElementById("btn-load-mock-history");
    if (btnRefreshHistory) {
        btnRefreshHistory.addEventListener("click", loadMockHistory);
    }

    // --- Flashcards Handler ---
    async function loadCardsData() {
        const topic = document.getElementById("card-topic-select").value;
        const cardType = document.getElementById("card-type-select").value;
        const container = document.getElementById("cards-viewer-container");

        container.innerHTML = `<div class="loading-spinner">Fetching study cards...</div>`;

        try {
            const cards = await ApiService.getCards(topic, cardType);
            if (!cards || cards.length === 0) {
                container.innerHTML = `<div class="text-muted">No cards found for this topic.</div>`;
                return;
            }

            container.innerHTML = cards.map(c => `
                <div class="flashcard-item">
                    <div>
                        <span class="badge-tag badge-neutral">${c.card_type.toUpperCase()}</span>
                        <div class="flashcard-title mt-lg">${c.title}</div>
                        <div class="flashcard-content">${c.content}</div>
                    </div>
                    ${c.example ? `<div class="flashcard-example">Example: ${c.example}</div>` : ''}
                </div>
            `).join("");
        } catch (e) {
            container.innerHTML = `<div class="text-muted">Error loading cards: ${e.message}</div>`;
        }
    }

    document.getElementById("btn-fetch-cards").addEventListener("click", loadCardsData);

    // --- Performance Analytics Handler ---
    async function loadPerformanceData() {
        const container = document.getElementById("performance-content-container");
        container.innerHTML = `<div class="loading-spinner">Aggregating historical metrics...</div>`;

        try {
            const perf = await ApiService.getPerformance();
            container.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card glass-card">
                        <div class="stat-icon cyan">📊</div>
                        <div class="stat-data">
                            <span class="stat-value">${perf.total_questions_attempted}</span>
                            <span class="stat-label">Total Attempted</span>
                        </div>
                    </div>
                    <div class="stat-card glass-card">
                        <div class="stat-icon emerald">📈</div>
                        <div class="stat-data">
                            <span class="stat-value">${perf.overall_accuracy}%</span>
                            <span class="stat-label">Overall Accuracy</span>
                        </div>
                    </div>
                </div>

                <div class="glass-panel mt-lg">
                    <h3>Topic Accuracy Breakdown</h3>
                    <div class="topic-tags-container mt-lg">
                        ${Object.entries(perf.topic_accuracy || {}).map(([t, acc]) => `
                            <div class="glass-card" style="min-width:180px;">
                                <strong>${t}</strong><br>
                                <span class="stat-value text-cyan">${acc}%</span>
                            </div>
                        `).join("")}
                    </div>
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="text-muted">Error loading performance: ${e.message}</div>`;
        }
    }

    // --- Study Plan Handler ---
    async function loadStudyPlanData() {
        const container = document.getElementById("study-plan-container");
        container.innerHTML = `<div class="loading-spinner">Generating adaptive study plan...</div>`;

        try {
            const plan = await ApiService.getStudyPlan(5);
            container.innerHTML = `
                <p class="text-muted mb-lg">${plan.summary}</p>
                <div class="plans-timeline">
                    ${plan.plan_items.map(item => `
                        <div class="glass-panel mb-lg">
                            <div class="flex-between">
                                <span class="badge-tag ${item.priority === 'High' ? 'badge-weak' : 'badge-neutral'}">${item.priority} Priority</span>
                                <span class="text-muted">${item.date} (${item.estimated_duration_minutes} mins)</span>
                            </div>
                            <h3 class="mt-lg">${item.topic}: ${item.activity}</h3>
                            <p class="mt-lg"><strong>Target:</strong> ${item.number_of_questions} Questions</p>
                            <p class="text-muted mt-lg">Reasoning: ${item.reason}</p>
                        </div>
                    `).join("")}
                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div class="text-muted">Error loading study plan: ${e.message}</div>`;
        }
    }

    document.getElementById("btn-refresh-plan").addEventListener("click", loadStudyPlanData);

    // --- AI Tutor Chat Handler ---
    const chatContainer = document.getElementById("chat-messages-container");
    const chatInput = document.getElementById("chat-input-text");
    const sendBtn = document.getElementById("btn-send-chat");

    async function sendChatMessage(msgText = null) {
        const query = msgText || chatInput.value.trim();
        if (!query) return;

        // Render user message
        const userDiv = document.createElement("div");
        userDiv.className = "message user-msg";
        userDiv.textContent = query;
        chatContainer.appendChild(userDiv);
        chatInput.value = "";
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Render loading bot message
        const botDiv = document.createElement("div");
        botDiv.className = "message bot-msg";
        botDiv.textContent = "Processing via Multi-Agent Router...";
        chatContainer.appendChild(botDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const res = await ApiService.sendChat(query);
            botDiv.innerHTML = `<strong>Agent [${res.intent}]:</strong><br>${res.reply.replace(/\n/g, "<br>")}`;
        } catch (e) {
            botDiv.textContent = "Error communicating with AI Tutor: " + e.message;
        }
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    sendBtn.addEventListener("click", () => sendChatMessage());
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") sendChatMessage();
    });

    // Initial Dashboard Load
    loadDashboardData();
});

from typing import List, Dict, Any, Tuple
from app.models.schemas import MockTestResultResponse, UserAnswerSubmission, QuestionSchema, MockQuestionDetailSchema

class TestScorer:
    """Calculates test scores, percentages, accuracy breakdown, and performance topics."""

    @staticmethod
    def score_mock_test(
        mock_test_id: str,
        questions: List[QuestionSchema],
        submissions: List[UserAnswerSubmission],
        time_taken_seconds: float = 0.0
    ) -> MockTestResultResponse:
        sub_map = {s.question_id: s.selected_answer for s in submissions}
        
        total_questions = len(questions)
        attempted = 0
        correct = 0
        wrong = 0
        unattempted = 0

        topic_stats: Dict[str, Dict[str, int]] = {} # topic -> {total, correct}
        diff_stats: Dict[str, Dict[str, int]] = {}  # diff -> {total, correct}
        detailed_questions: List[MockQuestionDetailSchema] = []

        for q in questions:
            t = q.topic
            d = q.difficulty

            if t not in topic_stats:
                topic_stats[t] = {"total": 0, "correct": 0}
            if d not in diff_stats:
                diff_stats[d] = {"total": 0, "correct": 0}

            topic_stats[t]["total"] += 1
            diff_stats[d]["total"] += 1

            ans = sub_map.get(q.id)
            is_correct_val = None

            if not ans:
                unattempted += 1
            else:
                attempted += 1
                if ans.lower() == q.correct_answer.lower():
                    correct += 1
                    is_correct_val = True
                    topic_stats[t]["correct"] += 1
                    diff_stats[d]["correct"] += 1
                else:
                    wrong += 1
                    is_correct_val = False

            detailed_questions.append(
                MockQuestionDetailSchema(
                    question_id=q.id or "",
                    question=q.question,
                    option_a=q.option_a,
                    option_b=q.option_b,
                    option_c=q.option_c,
                    option_d=q.option_d,
                    selected_answer=ans,
                    correct_answer=q.correct_answer,
                    is_correct=is_correct_val,
                    explanation=q.explanation,
                    topic=q.topic,
                    category=q.category,
                    difficulty=q.difficulty
                )
            )

        score = float(correct)
        percentage = round((correct / max(total_questions, 1)) * 100.0, 2)
        accuracy = round((correct / max(attempted, 1)) * 100.0, 2)

        topic_accuracy = {
            t: round((s["correct"] / s["total"]) * 100.0, 2)
            for t, s in topic_stats.items()
        }
        
        difficulty_accuracy = {
            d: round((s["correct"] / s["total"]) * 100.0, 2)
            for d, s in diff_stats.items()
        }

        strong_topics = [t for t, acc in topic_accuracy.items() if acc >= 75.0]
        weak_topics = [t for t, acc in topic_accuracy.items() if acc < 60.0]

        return MockTestResultResponse(
            mock_test_id=mock_test_id,
            total_questions=total_questions,
            attempted=attempted,
            correct=correct,
            wrong=wrong,
            unattempted=unattempted,
            score=score,
            percentage=percentage,
            accuracy=accuracy,
            time_taken_seconds=time_taken_seconds,
            topic_wise_accuracy=topic_accuracy,
            difficulty_wise_accuracy=difficulty_accuracy,
            strong_topics=strong_topics,
            weak_topics=weak_topics,
            detailed_questions=detailed_questions
        )

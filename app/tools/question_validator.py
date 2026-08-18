import re
from typing import List, Tuple, Dict, Any, Optional
from app.models.schemas import QuestionSchema, ValidationResult
from app.tools.calculator import SafeCalculator

class QuestionValidator:
    """Dedicated validation pipeline for LLM-generated aptitude questions."""

    @staticmethod
    def validate(question: QuestionSchema) -> ValidationResult:
        reasons: List[str] = []

        # Rule 1: Question prompt must not be empty or truncated
        if not question.question or len(question.question.strip()) < 10:
            reasons.append("Question prompt is empty or too short.")

        # Rule 2: Exactly 4 options must be present
        opts = [
            ("option_a", question.option_a),
            ("option_b", question.option_b),
            ("option_c", question.option_c),
            ("option_d", question.option_d)
        ]
        
        empty_opts = [k for k, v in opts if not v or not str(v).strip()]
        if empty_opts:
            reasons.append(f"Missing option content for: {', '.join(empty_opts)}")

        # Rule 3: No duplicate options
        opt_values = [str(v).strip().lower() for k, v in opts if v]
        if len(opt_values) != len(set(opt_values)):
            reasons.append("Options contain duplicate choices.")

        # Rule 4: Correct answer key must be valid
        valid_keys = ["option_a", "option_b", "option_c", "option_d"]
        clean_correct = str(question.correct_answer).strip().lower()
        if clean_correct not in valid_keys:
            reasons.append(f"Invalid correct_answer key '{question.correct_answer}'. Must be one of {valid_keys}.")

        # Rule 5: Explanation must exist and provide step-by-step reasoning
        if not question.explanation or len(question.explanation.strip()) < 5:
            reasons.append("Explanation is missing or insufficient.")

        # Rule 6: Check numerical calculations in explanation if numerical expressions exist
        math_check = QuestionValidator._check_numerical_consistency(question)
        if not math_check[0]:
            reasons.append(f"Numerical calculation check failed: {math_check[1]}")

        is_valid = len(reasons) == 0
        suggested_fix = None if is_valid else "; ".join(reasons)
        
        return ValidationResult(
            is_valid=is_valid,
            reasons=reasons,
            suggested_fix=suggested_fix
        )

    @staticmethod
    def _check_numerical_consistency(question: QuestionSchema) -> Tuple[bool, str]:
        """Check if simple mathematical equations in the explanation evaluate correctly using SafeCalculator."""
        text = f"{question.question}\n{question.explanation}"
        
        # Look for explicit math equalities like: "15% of 320 = 48" or "(15 / 100) * 320 = 48"
        # Match lines or phrases around '='
        for line in text.split('\n'):
            if '=' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    left_raw, right_raw = parts[0].strip(), parts[1].strip()
                    # Clean right side number (extract leading number)
                    right_match = re.search(r'^-?\d+(?:\.\d+)?', right_raw)
                    if not right_match:
                        continue
                    claimed_val = float(right_match.group(0))

                    # Clean left side expression - extract trailing math expression
                    left_match = re.search(r'[\d\.\+\-\*\/\(\)\s\^\%]+$', left_raw)
                    if not left_match:
                        continue
                    expr_clean = left_match.group(0).strip()
                    
                    if not any(op in expr_clean for op in ['+', '-', '*', '/', '^', '%']):
                        continue

                    try:
                        # Handle percentage expression if present, e.g. "15% of 320" -> "percent_of(15, 320)"
                        if '%' in expr_clean and 'of' in left_raw.lower():
                            pct_match = re.search(r'(\d+(?:\.\d+)?)\%\s*of\s*(\d+(?:\.\d+)?)', left_raw, re.IGNORECASE)
                            if pct_match:
                                expr_clean = f"percent_of({pct_match.group(1)}, {pct_match.group(2)})"

                        actual_val = SafeCalculator.evaluate(expr_clean)
                        if abs(actual_val - claimed_val) > 0.01:
                            return False, f"Expression '{expr_clean}' evaluated to {actual_val}, but text claimed {claimed_val}"
                    except Exception:
                        continue

        return True, "Numerical consistency verified."

def question_validator_tool(question_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Tool wrapper for agent workflow question validation."""
    try:
        q_schema = QuestionSchema(**question_dict)
        val = QuestionValidator.validate(q_schema)
        return {
            "is_valid": val.is_valid,
            "reasons": val.reasons,
            "suggested_fix": val.suggested_fix
        }
    except Exception as e:
        return {
            "is_valid": False,
            "reasons": [f"Malformed question dictionary: {str(e)}"],
            "suggested_fix": "Regenerate question in valid Pydantic format."
        }

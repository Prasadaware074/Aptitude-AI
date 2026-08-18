import ast
import operator
import math
from typing import Dict, Any, Union

# Safe AST operators mapping
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_ncr(n: int, r: int) -> int:
    if r < 0 or r > n:
        return 0
    return math.comb(n, r)

def safe_npr(n: int, r: int) -> int:
    if r < 0 or r > n:
        return 0
    return math.perm(n, r)

def safe_avg(*args) -> float:
    if not args:
        return 0.0
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        args = args[0]
    return sum(args) / len(args)

SAFE_FUNCTIONS = {
    "sqrt": math.sqrt,
    "abs": abs,
    "round": round,
    "pow": math.pow,
    "avg": safe_avg,
    "min": min,
    "max": max,
    "factorial": math.factorial,
    "ncr": safe_ncr,
    "npr": safe_npr,
    "percent": lambda part, whole: (part / whole) * 100.0 if whole != 0 else 0.0,
    "percent_of": lambda pct, whole: (pct / 100.0) * whole,
    "percent_change": lambda old_val, new_val: ((new_val - old_val) / old_val) * 100.0 if old_val != 0 else 0.0,
    "ratio": lambda a, b: a / b if b != 0 else 0.0,
}

class SafeCalculator:
    """A safe AST-based mathematical evaluator for Aptitude problem calculations."""

    @staticmethod
    def evaluate(expression: str) -> Union[int, float]:
        """Safely evaluate a mathematical expression string without using eval()."""
        if not expression or not expression.strip():
            raise ValueError("Expression is empty")
        
        # Clean expression
        clean_expr = expression.replace("^", "**").replace("×", "*").replace("÷", "/")
        
        try:
            node = ast.parse(clean_expr, mode='eval')
            return SafeCalculator._eval_node(node.body)
        except Exception as e:
            raise ValueError(f"Invalid math expression '{expression}': {str(e)}")

    @staticmethod
    def _eval_node(node: ast.AST) -> Union[int, float]:
        if isinstance(node, ast.Constant): # Number literal
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

        elif isinstance(node, ast.BinOp): # Binary operator: a + b, a * b
            left = SafeCalculator._eval_node(node.left)
            right = SafeCalculator._eval_node(node.right)
            op_type = type(node.op)
            if op_type in OPERATORS:
                if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                    raise ZeroDivisionError("Division by zero in calculation")
                return OPERATORS[op_type](left, right)
            raise ValueError(f"Unsupported operator: {op_type}")

        elif isinstance(node, ast.UnaryOp): # Unary operator: -a, +a
            operand = SafeCalculator._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in OPERATORS:
                return OPERATORS[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type}")

        elif isinstance(node, ast.Call): # Function call: sqrt(16), ncr(5, 2)
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function names are supported")
            func_name = node.func.id.lower()
            if func_name not in SAFE_FUNCTIONS:
                raise ValueError(f"Function '{func_name}' is not allowed")
            
            args = [SafeCalculator._eval_node(arg) for arg in node.args]
            return SAFE_FUNCTIONS[func_name](*args)

        else:
            raise ValueError(f"Unsupported AST node type: {type(node).__name__}")

def calculator_tool(expression: str) -> Dict[str, Any]:
    """Tool function to be invoked by agents or validators."""
    try:
        res = SafeCalculator.evaluate(expression)
        return {
            "success": True,
            "expression": expression,
            "result": res
        }
    except Exception as e:
        return {
            "success": False,
            "expression": expression,
            "error": str(e)
        }

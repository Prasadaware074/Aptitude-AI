import pytest
from app.tools.calculator import SafeCalculator, calculator_tool

def test_basic_arithmetic():
    assert SafeCalculator.evaluate("25 + 15") == 40
    assert SafeCalculator.evaluate("100 - 35") == 65
    assert SafeCalculator.evaluate("12 * 8") == 96
    assert SafeCalculator.evaluate("144 / 12") == 12.0
    assert SafeCalculator.evaluate("10 % 3") == 1

def test_advanced_math_operations():
    assert SafeCalculator.evaluate("2 ^ 3") == 8
    assert SafeCalculator.evaluate("sqrt(144)") == 12.0
    assert SafeCalculator.evaluate("percent(20, 100)") == 20.0
    assert SafeCalculator.evaluate("percent_of(15, 320)") == 48.0
    assert SafeCalculator.evaluate("avg(10, 20, 30)") == 20.0
    assert SafeCalculator.evaluate("ncr(5, 2)") == 10
    assert SafeCalculator.evaluate("npr(5, 2)") == 20

def test_safe_rejection_of_arbitrary_code():
    with pytest.raises(ValueError):
        SafeCalculator.evaluate("__import__('os').system('dir')")

    with pytest.raises(ValueError):
        SafeCalculator.evaluate("eval('1 + 1')")

def test_calculator_tool_dict_output():
    res = calculator_tool("percent_of(25, 400)")
    assert res["success"] is True
    assert res["result"] == 100.0

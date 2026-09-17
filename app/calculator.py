"""Small calculator engine with real arithmetic and number-theory logic.

Kept independent of Flask so it can be unit tested in isolation.
"""

from __future__ import annotations

import math


class CalculatorError(ValueError):
    """Raised when a calculator operation receives invalid input."""


def add(a: float, b: float) -> float:
    """Return a + b."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return a - b."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return a * b."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return a / b.

    Raises:
        CalculatorError: if ``b`` is zero.
    """
    if b == 0:
        raise CalculatorError("division by zero is not allowed")
    return a / b


def percentage(value: float, percent: float) -> float:
    """Return ``percent`` percent of ``value``."""
    return value * (percent / 100)


def is_prime(n: int) -> bool:
    """Return True if ``n`` is a prime number."""
    if not isinstance(n, int):
        raise CalculatorError("is_prime requires an integer")
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for divisor in range(3, int(math.isqrt(n)) + 1, 2):
        if n % divisor == 0:
            return False
    return True


def factorial(n: int) -> int:
    """Return n! for a non-negative integer ``n``."""
    if not isinstance(n, int) or n < 0:
        raise CalculatorError("factorial requires a non-negative integer")
    return math.factorial(n)


OPERATIONS = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
}


def calculate(operation: str, a: float, b: float) -> float:
    """Dispatch a binary arithmetic ``operation`` by name.

    Raises:
        CalculatorError: if the operation name is unknown.
    """
    func = OPERATIONS.get(operation)
    if func is None:
        raise CalculatorError(f"unsupported operation: {operation!r}")
    return func(a, b)

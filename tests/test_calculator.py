"""Unit tests for app.calculator — pure logic, no Flask involved."""

import pytest

from app.calculator import (
    CalculatorError,
    add,
    calculate,
    divide,
    factorial,
    is_prime,
    multiply,
    percentage,
    subtract,
)


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2


def test_multiply():
    assert multiply(4, 3) == 12
    assert multiply(-2, 3) == -6


def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5


def test_divide_by_zero_raises():
    with pytest.raises(CalculatorError):
        divide(1, 0)


def test_percentage():
    assert percentage(200, 50) == 100
    assert percentage(50, 10) == 5


@pytest.mark.parametrize(
    "n, expected",
    [
        (0, False),
        (1, False),
        (2, True),
        (3, True),
        (4, False),
        (17, True),
        (18, False),
        (97, True),
    ],
)
def test_is_prime(n, expected):
    assert is_prime(n) is expected


def test_is_prime_rejects_non_int():
    with pytest.raises(CalculatorError):
        is_prime(3.5)


def test_factorial():
    assert factorial(0) == 1
    assert factorial(5) == 120


def test_factorial_rejects_negative():
    with pytest.raises(CalculatorError):
        factorial(-1)


def test_calculate_dispatch():
    assert calculate("add", 2, 3) == 5
    assert calculate("subtract", 5, 2) == 3
    assert calculate("multiply", 3, 3) == 9
    assert calculate("divide", 8, 4) == 2


def test_calculate_unknown_operation_raises():
    with pytest.raises(CalculatorError):
        calculate("modulo", 5, 2)

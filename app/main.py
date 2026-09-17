"""Flask REST API: a tiny calculator + todo service.

This is the sample application that the CI/CD pipeline in this repo
builds, lints, tests, scans, and containerizes.
"""

from __future__ import annotations

from flask import Flask, jsonify, request

from app.calculator import CalculatorError, calculate, factorial, is_prime
from app.todo_store import TodoNotFoundError, TodoStore, TodoValidationError


def create_app() -> Flask:
    """Application factory so tests can spin up isolated instances."""
    app = Flask(__name__)
    store = TodoStore()

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.post("/calculate")
    def do_calculate():
        payload = request.get_json(silent=True) or {}
        operation = payload.get("operation")
        a = payload.get("a")
        b = payload.get("b")
        if operation is None or a is None or b is None:
            return jsonify(error="operation, a, and b are required"), 400
        try:
            result = calculate(operation, float(a), float(b))
        except CalculatorError as exc:
            return jsonify(error=str(exc)), 400
        except (TypeError, ValueError):
            return jsonify(error="a and b must be numbers"), 400
        return jsonify(operation=operation, a=a, b=b, result=result), 200

    @app.get("/calculate/is-prime/<int:number>")
    def check_prime(number: int):
        return jsonify(number=number, is_prime=is_prime(number)), 200

    @app.get("/calculate/factorial/<int:number>")
    def do_factorial(number: int):
        try:
            result = factorial(number)
        except CalculatorError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(number=number, result=result), 200

    @app.get("/todos")
    def list_todos():
        return jsonify([todo.to_dict() for todo in store.list_all()]), 200

    @app.post("/todos")
    def create_todo():
        payload = request.get_json(silent=True) or {}
        try:
            todo = store.add(payload.get("title", ""))
        except TodoValidationError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(todo.to_dict()), 201

    @app.get("/todos/<int:todo_id>")
    def get_todo(todo_id: int):
        try:
            todo = store.get(todo_id)
        except TodoNotFoundError:
            return jsonify(error="todo not found"), 404
        return jsonify(todo.to_dict()), 200

    @app.put("/todos/<int:todo_id>")
    def update_todo(todo_id: int):
        payload = request.get_json(silent=True) or {}
        try:
            todo = store.update(
                todo_id,
                title=payload.get("title"),
                completed=payload.get("completed"),
            )
        except TodoNotFoundError:
            return jsonify(error="todo not found"), 404
        except TodoValidationError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(todo.to_dict()), 200

    @app.patch("/todos/<int:todo_id>/toggle")
    def toggle_todo(todo_id: int):
        try:
            todo = store.toggle(todo_id)
        except TodoNotFoundError:
            return jsonify(error="todo not found"), 404
        return jsonify(todo.to_dict()), 200

    @app.delete("/todos/<int:todo_id>")
    def delete_todo(todo_id: int):
        try:
            store.delete(todo_id)
        except TodoNotFoundError:
            return jsonify(error="todo not found"), 404
        return "", 204

    return app


app = create_app()

if __name__ == "__main__":
    # Bind to localhost by default for safe local development; a real
    # deployment would run this behind gunicorn/uwsgi in the container
    # (see Dockerfile) rather than via the Flask dev server.
    app.run(host="127.0.0.1", port=5000)

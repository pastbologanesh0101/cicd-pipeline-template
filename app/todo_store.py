"""In-memory todo list store with real validation logic.

This is deliberately not backed by a database so the sample project
stays dependency-free; swap ``TodoStore`` for a real repository layer
in a production deployment.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Optional


class TodoNotFoundError(KeyError):
    """Raised when a todo id does not exist in the store."""


class TodoValidationError(ValueError):
    """Raised when a todo's title fails validation."""


@dataclass
class Todo:
    id: int
    title: str
    completed: bool = False

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "completed": self.completed}


class TodoStore:
    """A simple, thread-unsafe in-memory todo store."""

    def __init__(self) -> None:
        self._todos: dict[int, Todo] = {}
        self._id_counter = itertools.count(1)

    @staticmethod
    def _validate_title(title: str) -> str:
        if not isinstance(title, str) or not title.strip():
            raise TodoValidationError("title must be a non-empty string")
        cleaned = title.strip()
        if len(cleaned) > 200:
            raise TodoValidationError("title must be 200 characters or fewer")
        return cleaned

    def add(self, title: str) -> Todo:
        """Create and store a new todo, returning it."""
        cleaned = self._validate_title(title)
        todo_id = next(self._id_counter)
        todo = Todo(id=todo_id, title=cleaned, completed=False)
        self._todos[todo_id] = todo
        return todo

    def list_all(self) -> list[Todo]:
        """Return all todos ordered by id."""
        return [self._todos[key] for key in sorted(self._todos)]

    def get(self, todo_id: int) -> Todo:
        """Return a single todo by id.

        Raises:
            TodoNotFoundError: if no todo with that id exists.
        """
        try:
            return self._todos[todo_id]
        except KeyError as exc:
            raise TodoNotFoundError(f"todo {todo_id} not found") from exc

    def update(
        self, todo_id: int, title: Optional[str] = None, completed: Optional[bool] = None
    ) -> Todo:
        """Update fields on an existing todo and return it."""
        todo = self.get(todo_id)
        if title is not None:
            todo.title = self._validate_title(title)
        if completed is not None:
            todo.completed = bool(completed)
        return todo

    def toggle(self, todo_id: int) -> Todo:
        """Flip the completed flag on a todo and return it."""
        todo = self.get(todo_id)
        todo.completed = not todo.completed
        return todo

    def delete(self, todo_id: int) -> None:
        """Remove a todo from the store.

        Raises:
            TodoNotFoundError: if no todo with that id exists.
        """
        if todo_id not in self._todos:
            raise TodoNotFoundError(f"todo {todo_id} not found")
        del self._todos[todo_id]

    def clear(self) -> None:
        """Remove all todos (mainly useful for tests)."""
        self._todos.clear()
        self._id_counter = itertools.count(1)

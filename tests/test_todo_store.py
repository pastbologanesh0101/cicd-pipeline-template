"""Unit tests for app.todo_store — pure logic, no Flask involved."""

import pytest

from app.todo_store import TodoNotFoundError, TodoStore, TodoValidationError


@pytest.fixture
def store():
    return TodoStore()


def test_add_returns_todo_with_incrementing_id(store):
    first = store.add("Buy milk")
    second = store.add("Walk the dog")
    assert first.id == 1
    assert second.id == 2
    assert first.title == "Buy milk"
    assert first.completed is False


def test_add_strips_whitespace(store):
    todo = store.add("  Buy milk  ")
    assert todo.title == "Buy milk"


def test_add_rejects_empty_title(store):
    with pytest.raises(TodoValidationError):
        store.add("   ")


def test_add_rejects_too_long_title(store):
    with pytest.raises(TodoValidationError):
        store.add("x" * 201)


def test_list_all_ordered_by_id(store):
    store.add("first")
    store.add("second")
    titles = [todo.title for todo in store.list_all()]
    assert titles == ["first", "second"]


def test_get_existing_todo(store):
    added = store.add("Buy milk")
    fetched = store.get(added.id)
    assert fetched is added


def test_get_missing_todo_raises(store):
    with pytest.raises(TodoNotFoundError):
        store.get(999)


def test_update_title(store):
    todo = store.add("Buy milk")
    updated = store.update(todo.id, title="Buy oat milk")
    assert updated.title == "Buy oat milk"


def test_update_completed(store):
    todo = store.add("Buy milk")
    updated = store.update(todo.id, completed=True)
    assert updated.completed is True


def test_update_missing_todo_raises(store):
    with pytest.raises(TodoNotFoundError):
        store.update(999, title="anything")


def test_toggle_flips_completed(store):
    todo = store.add("Buy milk")
    assert todo.completed is False
    store.toggle(todo.id)
    assert store.get(todo.id).completed is True
    store.toggle(todo.id)
    assert store.get(todo.id).completed is False


def test_delete_removes_todo(store):
    todo = store.add("Buy milk")
    store.delete(todo.id)
    with pytest.raises(TodoNotFoundError):
        store.get(todo.id)


def test_delete_missing_todo_raises(store):
    with pytest.raises(TodoNotFoundError):
        store.delete(999)


def test_clear_resets_ids(store):
    store.add("first")
    store.clear()
    todo = store.add("second")
    assert todo.id == 1

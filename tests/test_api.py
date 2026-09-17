"""Integration tests for the Flask REST API endpoints in app.main."""

import pytest

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_calculate_add(client):
    response = client.post("/calculate", json={"operation": "add", "a": 2, "b": 3})
    assert response.status_code == 200
    assert response.get_json()["result"] == 5


def test_calculate_divide_by_zero(client):
    response = client.post("/calculate", json={"operation": "divide", "a": 1, "b": 0})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_calculate_missing_fields(client):
    response = client.post("/calculate", json={"operation": "add"})
    assert response.status_code == 400


def test_calculate_unknown_operation(client):
    response = client.post("/calculate", json={"operation": "modulo", "a": 1, "b": 2})
    assert response.status_code == 400


def test_is_prime_endpoint(client):
    response = client.get("/calculate/is-prime/17")
    assert response.status_code == 200
    assert response.get_json() == {"number": 17, "is_prime": True}


def test_factorial_endpoint(client):
    response = client.get("/calculate/factorial/5")
    assert response.status_code == 200
    assert response.get_json() == {"number": 5, "result": 120}


def test_create_and_list_todos(client):
    create_resp = client.post("/todos", json={"title": "Buy milk"})
    assert create_resp.status_code == 201
    todo = create_resp.get_json()
    assert todo["title"] == "Buy milk"
    assert todo["completed"] is False

    list_resp = client.get("/todos")
    assert list_resp.status_code == 200
    assert len(list_resp.get_json()) == 1


def test_create_todo_rejects_empty_title(client):
    response = client.post("/todos", json={"title": ""})
    assert response.status_code == 400


def test_get_single_todo(client):
    created = client.post("/todos", json={"title": "Buy milk"}).get_json()
    response = client.get(f"/todos/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Buy milk"


def test_get_missing_todo_returns_404(client):
    response = client.get("/todos/999")
    assert response.status_code == 404


def test_update_todo(client):
    created = client.post("/todos", json={"title": "Buy milk"}).get_json()
    response = client.put(
        f"/todos/{created['id']}", json={"title": "Buy oat milk", "completed": True}
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["title"] == "Buy oat milk"
    assert body["completed"] is True


def test_toggle_todo(client):
    created = client.post("/todos", json={"title": "Buy milk"}).get_json()
    response = client.patch(f"/todos/{created['id']}/toggle")
    assert response.status_code == 200
    assert response.get_json()["completed"] is True


def test_delete_todo(client):
    created = client.post("/todos", json={"title": "Buy milk"}).get_json()
    delete_resp = client.delete(f"/todos/{created['id']}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/todos/{created['id']}")
    assert get_resp.status_code == 404


def test_delete_missing_todo_returns_404(client):
    response = client.delete("/todos/999")
    assert response.status_code == 404

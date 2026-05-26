import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aplicacion.base_de_datos import Base, get_db
from aplicacion.principal import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tareas.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _create_task(client, **kwargs):
    payload = {"title": "Test task", **kwargs}
    resp = client.post("/tasks/", json=payload)
    assert resp.status_code == 201
    return resp.json()


def test_update_done_task_returns_400(client):
    task = _create_task(client, status="done")

    resp = client.patch(f"/tasks/{task['id']}", json={"title": "New title"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Cannot update a completed task"


def test_update_pending_task_succeeds(client):
    task = _create_task(client)

    resp = client.patch(f"/tasks/{task['id']}", json={"title": "Updated"})

    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


def test_update_in_progress_task_succeeds(client):
    task = _create_task(client, status="in_progress")

    resp = client.patch(
        f"/tasks/{task['id']}", json={"status": "done"}
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_update_done_task_status_change_blocked(client):
    task = _create_task(client, status="done")

    resp = client.patch(f"/tasks/{task['id']}", json={"status": "pending"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Cannot update a completed task"


# ---------------------------------------------------------------------------
# Casos de error 404: endpoints que reciben un id inexistente
# ---------------------------------------------------------------------------

def test_get_task_not_found(client):
    resp = client.get("/tasks/999")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Task not found"


def test_delete_task_not_found(client):
    resp = client.delete("/tasks/999")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Task not found"


def test_update_task_not_found(client):
    resp = client.patch("/tasks/999", json={"title": "Ghost"})

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Task not found"


# ---------------------------------------------------------------------------
# Validación de entrada: POST con cuerpo inválido
# ---------------------------------------------------------------------------

def test_create_task_without_title(client):
    resp = client.post("/tasks/", json={})

    assert resp.status_code == 422


def test_create_task_with_invalid_status(client):
    resp = client.post("/tasks/", json={"title": "T", "status": "invalid"})

    assert resp.status_code == 422


def test_update_task_with_invalid_status(client):
    task = _create_task(client)

    resp = client.patch(f"/tasks/{task['id']}", json={"status": "invalid"})

    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Happy paths necesarios para cobertura completa
# ---------------------------------------------------------------------------

def test_list_tasks_empty(client):
    resp = client.get("/tasks/")

    assert resp.status_code == 200
    assert resp.json() == []


def test_list_tasks_returns_all(client):
    _create_task(client, title="A")
    _create_task(client, title="B")

    resp = client.get("/tasks/")

    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_task_success(client):
    task = _create_task(client, title="Read me")

    resp = client.get(f"/tasks/{task['id']}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Read me"
    assert data["id"] == task["id"]


def test_delete_task_success(client):
    task = _create_task(client)

    resp = client.delete(f"/tasks/{task['id']}")
    assert resp.status_code == 204

    resp = client.get(f"/tasks/{task['id']}")
    assert resp.status_code == 404


def test_create_task_default_status(client):
    task = _create_task(client)

    assert task["status"] == "pending"


def test_create_task_with_description(client):
    task = _create_task(client, description="Some details")

    assert task["description"] == "Some details"


def test_update_task_partial_fields(client):
    task = _create_task(client, title="Old", description="Desc")

    resp = client.patch(f"/tasks/{task['id']}", json={"description": "New desc"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Old"
    assert data["description"] == "New desc"

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


def test_update_task_title_too_short_returns_422(client):
    task = _create_task(client)

    resp = client.patch(f"/tasks/{task['id']}", json={"title": "AB"})

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "title"]


def test_update_done_task_status_change_blocked(client):
    task = _create_task(client, status="done")

    resp = client.patch(f"/tasks/{task['id']}", json={"status": "pending"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Cannot update a completed task"


def test_delete_all_tasks_clears_list(client):
    _create_task(client, title="Tarea 1")
    _create_task(client, title="Tarea 2")

    resp = client.delete("/tasks/")

    assert resp.status_code == 204
    assert client.get("/tasks/").json() == []


def test_delete_all_tasks_on_empty_db_returns_204(client):
    resp = client.delete("/tasks/")

    assert resp.status_code == 204
    assert client.get("/tasks/").json() == []


def test_create_task_with_description(client):
    resp = client.post(
        "/tasks/", json={"title": "Tarea", "description": "Descripción válida"}
    )

    assert resp.status_code == 201
    assert resp.json()["description"] == "Descripción válida"


def test_create_task_description_too_long_returns_422(client):
    long_desc = "a" * 501

    resp = client.post("/tasks/", json={"title": "Tarea", "description": long_desc})

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "description"]


def test_create_task_description_max_length_accepted(client):
    desc = "a" * 500

    resp = client.post("/tasks/", json={"title": "Tarea", "description": desc})

    assert resp.status_code == 201
    assert resp.json()["description"] == desc


def test_update_task_description_too_long_returns_422(client):
    task = _create_task(client)
    long_desc = "b" * 501

    resp = client.patch(
        f"/tasks/{task['id']}", json={"description": long_desc}
    )

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "description"]


def test_update_task_description_succeeds(client):
    task = _create_task(client)

    resp = client.patch(
        f"/tasks/{task['id']}", json={"description": "Nueva descripción"}
    )

    assert resp.status_code == 200
    assert resp.json()["description"] == "Nueva descripción"


def test_complete_task_pending(client):
    task = _create_task(client)

    resp = client.patch(f"/tasks/{task['id']}/complete")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "done"
    assert data["id"] == task["id"]


def test_complete_task_in_progress(client):
    task = _create_task(client, status="in_progress")

    resp = client.patch(f"/tasks/{task['id']}/complete")

    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_complete_task_already_done_returns_400(client):
    task = _create_task(client, status="done")

    resp = client.patch(f"/tasks/{task['id']}/complete")

    assert resp.status_code == 400
    assert resp.json()["detail"] == "La tarea ya está completada"


def test_complete_task_not_found_returns_404(client):
    resp = client.patch("/tasks/9999/complete")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Tarea no encontrada"

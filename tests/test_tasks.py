import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from aplicacion.base_de_datos import Base, get_db
from aplicacion.principal import app

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
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


# --- Tests de regresión: Bug 1 — validación update_task ---


def test_update_done_task_returns_400(client):
    """Una tarea completada no puede modificarse (ni título ni estado)."""
    task = _create_task(client, status="done")

    resp = client.patch(f"/tasks/{task['id']}", json={"title": "Nuevo título"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "No se puede modificar una tarea completada"


def test_update_done_task_status_change_blocked(client):
    """No se puede cambiar el estado de una tarea ya completada."""
    task = _create_task(client, status="done")

    resp = client.patch(f"/tasks/{task['id']}", json={"status": "pending"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "No se puede modificar una tarea completada"


def test_transition_to_done_is_allowed(client):
    """Se puede marcar como done una tarea in_progress."""
    task = _create_task(client, status="in_progress")

    resp = client.patch(f"/tasks/{task['id']}", json={"status": "done"})

    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_update_pending_task_succeeds(client):
    """Se puede actualizar una tarea pendiente sin restricciones."""
    task = _create_task(client)

    resp = client.patch(f"/tasks/{task['id']}", json={"title": "Actualizado"})

    assert resp.status_code == 200
    assert resp.json()["title"] == "Actualizado"


# --- Tests de regresión: Bug 2 — validación min_length título en create ---


def test_create_task_title_too_short_returns_422(client):
    """Crear una tarea con título menor a 3 caracteres devuelve 422."""
    resp = client.post("/tasks/", json={"title": "AB"})

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["loc"] == ["body", "title"]


def test_create_task_title_min_length_accepted(client):
    """Crear una tarea con exactamente 3 caracteres es válido."""
    resp = client.post("/tasks/", json={"title": "ABC"})

    assert resp.status_code == 201
    assert resp.json()["title"] == "ABC"

import uuid
from datetime import datetime
from typing import Any
from fastapi.testclient import TestClient
from sqlmodel import select
from sqlalchemy import and_

from app.models.user import User  # tu modelo
from app.schemas.user.user_schemas import UserInput, UserOutput  # asume nombres


def _create_test_user(client: TestClient, db, suffix: str = "@") -> dict[str, Any]:
    payload: UserInput = UserInput(
        email=f"test{suffix}@example.com",
        password="StrongPass123!",
        name=f"Test{suffix}",
        last_name=f"Doe{suffix}",
    )
    r = client.post("/users/", json=payload.model_dump())
    assert r.status_code == 201
    data = r.json()
    # valida UserOutput
    assert uuid.UUID(data["id"])
    assert data["email"] == payload.email
    return data


def test_root(client: TestClient):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()  # {} o {"message": "OK"}


def test_create_user(client: TestClient, db):
    payload = UserInput(
        email="create@example.com",
        password="StrongPass123!",
        name="Create",
        last_name="User",
    )
    r = client.post("/users/", json=payload.model_dump())
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == payload.email
    assert "date_created" in data

    # verifica en BD
    stmt = select(User).where(User.email == payload.email)
    user_db = db.execute(stmt).first()
    assert user_db[0] is not None
    assert str(user_db[0].id) == data["id"]


def test_create_user_duplicate_email(client: TestClient, db):
    payload = UserInput(
        email="dup@example.com",
        password="StrongPass123!",
        name="Dup",
        last_name="User",
    )
    client.post("/users/", json=payload.model_dump())  # crea primero
    r = client.post("/users/", json=payload.model_dump())
    assert r.status_code in (409, 422)  # tu servicio lanza HTTP 409?


def test_get_paged_users(client: TestClient, db):
    # crea 5 usuarios
    for i in range(5):
        _create_test_user(client, db, f"paged{i}")

    # paginado básico
    r = client.get("/users/?page=1&size=2&ascending=true&offset_field=id")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["total"] == 7

    # filtros
    r2 = client.get("/users/?page=1&size=10&email=paged0@example.com")
    assert r2.status_code == 200
    data2 = r2.json()
    assert any(item["email"].endswith("paged0@example.com") for item in data2["items"])


def test_get_user_by_id(client: TestClient, db):
    created = _create_test_user(client, db, "get")
    user_id = created["id"]

    r = client.get(f"/users/{user_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == user_id
    assert data["name"] == "Testget"


def test_get_user_by_id_not_found(client: TestClient):
    fake_id = str(uuid.uuid4())
    r = client.get(f"/users/{fake_id}")
    assert r.status_code == 404  # asume tu servicio lanza 404


def test_update_user(client: TestClient, db):
    created = _create_test_user(client, db, "update")
    user_id = uuid.UUID(created["id"])

    payload = {"name": "Updated", "last_name": "User"}  # UserUpdateInput
    r = client.put(f"/users/{user_id}", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Updated"
    assert data["last_name"] == "User"

    # verifica en BD (date_updated actualizada)
    user_db = db.get(User, user_id)
    assert user_db.name == "Updated"


def test_delete_user(client: TestClient, db):
    created = _create_test_user(client, db, "delete")
    user_id = uuid.UUID(created["id"])

    r = client.delete(f"/users/{user_id}")
    assert r.status_code == 204

    user_db = db.get(User, user_id)
    # assert user_db[0] is None
    assert user_db.is_deleted == True


def test_get_user_invalid_uuid(client: TestClient):
    r = client.get("/users/not-a-uuid")
    assert r.status_code == 422
    assert "uuid" in str(r.json())


def test_create_user_validation(client: TestClient):
    invalid = {"email": "invalid", "name": ""}  # faltan password, last_name
    r = client.post("/users/", json=invalid)
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert any("password" in e["loc"] for e in detail)
    assert any("last_name" in e["loc"] for e in detail)


def test_get_paged_invalid_params(client: TestClient):
    r = client.get("/users/?page=0&size=0")  # min=1
    assert r.status_code == 422
    r2 = client.get("/users/?size=101")  # max=100
    assert r2.status_code == 422
    r3 = client.get("/users/?offset_field=invalid")
    assert r3.status_code == 422  # enum

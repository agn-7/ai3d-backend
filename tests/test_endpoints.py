import pytest

from ai3d import models, schemas, crud
from ai3d.database import AsyncSession
from . import client


### Integration Tests ###


def test_get_root():
    response = client.client.get("/api")
    assert response.status_code == 200
    assert response.json() == "Hello from Ai3D!"


@pytest.mark.asyncio
async def test_get_all_interactions(db: AsyncSession):
    interaction1 = models.Interaction(settings={"prompt": "something"})
    interaction2 = models.Interaction(settings={"prompt": "something else"})
    db.add(interaction1)
    db.add(interaction2)
    await db.commit()

    response = client.client.get("/api/interactions")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_create_interaction(db: AsyncSession):
    user_schema = schemas.UserCreate(username="user1", password="password1")
    await crud.create_user(db, user_schema)

    login_response = client.client.post(
        "/api/token",
        data={"username": "user1", "password": "password1"},
    )
    token = login_response.json()["access_token"]

    response = client.client.post(
        "/api/interactions",
        json={
            "prompt": "something",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["settings"] == {
        "prompt": "something",
        "model": "gpt-4-1106-preview",
        "role": "system",
    }


@pytest.mark.asyncio
async def test_read_users_me(db: AsyncSession):
    user_schema = schemas.UserCreate(username="user1", password="password1")
    await crud.create_user(db, user_schema)

    login_response = client.client.post(
        "/api/token",
        data={"username": "user1", "password": "password1"},
    )
    token = login_response.json()["access_token"]

    response = client.client.get(
        "/api/user/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "user1"


@pytest.mark.asyncio
async def test_get_user(db: AsyncSession):
    user1 = models.User(username="user1", password="password1")
    db.add(user1)
    await db.commit()

    response = client.client.get(f"/api/user/{user1.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(user1.id)


@pytest.mark.asyncio
async def test_create_user(db: AsyncSession):
    user_schema = schemas.UserCreate(username="user1", password="password1")

    response = client.client.post("/api/user", json=user_schema.model_dump())
    assert response.status_code == 200
    assert response.json()["username"] == "user1"

import pytest

from unittest.mock import ANY

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
async def test_get_interaction(db: AsyncSession):
    interaction1 = models.Interaction(settings={"prompt": "something"})
    db.add(interaction1)
    await db.commit()

    response = client.client.get(f"/api/interactions/{interaction1.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(interaction1.id)


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
    assert response.status_code == 201
    assert response.json()["settings"] == {
        "prompt": "something",
        "model": "gpt-4-1106-preview",
        "role": "system",
    }


@pytest.mark.asyncio
async def test_update_interaction(db: AsyncSession):
    user_schema = schemas.UserCreate(username="user1", password="password1")
    await crud.create_user(db, user_schema)

    login_response = client.client.post(
        "/api/token",
        data={"username": "user1", "password": "password1"},
    )
    token = login_response.json()["access_token"]

    interaction1 = models.Interaction(settings={"prompt": "something"})
    db.add(interaction1)
    await db.commit()

    response = client.client.put(
        f"/api/interactions/{interaction1.id}",
        json={
            "prompt": "something else",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["settings"] == {
        "prompt": "something else",
        "model": "gpt-4-1106-preview",
        "role": "system",
    }


@pytest.mark.asyncio
async def test_get_all_message_in_interaction(db: AsyncSession):
    interaction_schema = schemas.InteractionCreate(settings={"prompt": "something"})
    interaction = await crud.create_interaction(db, interaction_schema)

    message_data_1 = {"role": "user", "content": "Hello"}
    message_data_2 = {"role": "assistant", "content": "World!"}
    message_schema_1 = schemas.MessageCreate(**message_data_1)
    message_schema_2 = schemas.MessageCreate(**message_data_2)
    await crud.create_message(db, [message_schema_1, message_schema_2], interaction.id)

    user_schema = schemas.UserCreate(username="user1", password="password1")
    await crud.create_user(db, user_schema)

    login_response = client.client.post(
        "/api/token",
        data={"username": "user1", "password": "password1"},
    )
    token = login_response.json()["access_token"]

    messages = client.client.get(
        f"/api/interactions/{interaction.id}/messages",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert messages.status_code == 200
    assert len(messages.json()) == 2
    assert messages.json()[0]["content"] == "Hello"
    assert messages.json()[1]["content"] == "World!"
    assert messages.json()[0]["role"] == "user"
    assert messages.json()[1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_create_message(db: AsyncSession, mock_generate_ai_response):
    # user_schema = schemas.UserCreate(username="user1", password="password1")
    # await crud.create_user(db, user_schema)

    # login_response = client.client.post(
    #     "/api/token",
    #     data={"username": "user1", "password": "password1"},
    # )
    # token = login_response.json()["access_token"]

    interaction1 = models.Interaction(settings={"prompt": "something"})
    db.add(interaction1)
    await db.commit()

    message_data = {"role": "user", "content": "Hello"}
    response = client.client.post(
        f"/api/interactions/{interaction1.id}/messages",
        json=message_data,
        # headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["content"] == "AI response"
    assert response.json()["role"] == "assistant"
    mock_generate_ai_response.assert_called_once_with(
        db=ANY, content="Hello", interaction=ANY
    )


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
    user_schema2 = schemas.UserCreate(username="user2", password="password2")
    await crud.create_user(db, user_schema)

    login_response = client.client.post(
        "/api/token",
        data={"username": "user1", "password": "password1"},
    )
    token = login_response.json()["access_token"]

    response = client.client.post(
        "/api/user",
        json=user_schema2.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["username"] == "user2"


@pytest.mark.asyncio
async def test_login(db: AsyncSession):
    user_schema = schemas.UserCreate(username="user1", password="password1")
    await crud.create_user(db, user_schema)

    response = client.client.post(
        "/api/token",
        data={"username": "user1", "password": "password1"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

import pytest

from ai3d import crud, models, schemas, utils
from ai3d.database import AsyncSession


### Unit Tests ###


@pytest.mark.asyncio
async def test_get_interactions(db: AsyncSession):
    interaction1 = models.Interaction(
        settings=dict(model="model1", role="role1", prompt="prompt1"),
    )
    interaction2 = models.Interaction(
        settings=dict(model="model2", role="role2", prompt="prompt2"),
    )
    db.add(interaction1)
    db.add(interaction2)
    await db.commit()

    interactions = await crud.get_interactions(db)
    assert len(interactions) == 2
    assert interactions[0].settings["model"] == "model1"
    assert interactions[1].settings["model"] == "model2"


@pytest.mark.asyncio
async def test_get_interaction(db: AsyncSession):
    interaction = models.Interaction(
        settings=dict(model="model", role="role", prompt="prompt"),
    )
    db.add(interaction)
    await db.commit()

    retrieved_interaction = await crud.get_interaction(db, interaction.id)
    assert retrieved_interaction.id == interaction.id
    assert retrieved_interaction.settings["model"] == "model"


@pytest.mark.asyncio
async def test_get_user(db: AsyncSession):
    user1 = models.User(username="user1", password="password1")
    db.add(user1)
    await db.commit()

    user = await crud.get_user(db, "user1")
    assert user.username == "user1"


@pytest.mark.asyncio
async def test_get_user_by_id(db: AsyncSession):
    user1 = models.User(username="user1", password="password1")
    db.add(user1)
    await db.commit()

    user = await crud.get_user_by_id(db, user1.id)
    assert user.id == user1.id


@pytest.mark.asyncio
async def test_create_user(db: AsyncSession):
    try:
        # Mocking utils.get_hashed_password function
        def mock_get_hashed_password(password: str) -> str:
            return "hashed" + password

        get_hashed_password = utils.get_hashed_password
        utils.get_hashed_password = mock_get_hashed_password

        user_schema = schemas.UserCreate(username="user1", password="password1")
        user = await crud.create_user(db, user_schema)

        assert user.username == "user1"
        assert user.password == "hashedpassword1"
    finally:
        # Unmocking utils.get_hashed_password function
        utils.get_hashed_password = get_hashed_password

    assert user.username == "user1"
    assert user.password == "hashedpassword1"

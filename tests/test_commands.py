import pytest

from asyncclick.testing import CliRunner
from unittest.mock import patch

from ai3d import crud, commands
from ai3d.database import AsyncSession


@pytest.mark.asyncio
@patch("ai3d.commands.click.prompt", side_effect=["testuser", "testemail@asa.com"])
@patch("ai3d.commands.getpass", side_effect=["testpassword", "testpassword"])
async def test_create_superuser(
    mock_getpass, mock_prompt, mock_get_hashed_password, db: AsyncSession
):
    with mock_get_hashed_password:
        runner = CliRunner()
        result = await runner.invoke(commands.create_superuser, obj=db)

        assert result.exit_code == 0
        mock_prompt.assert_any_call("Username", type=str)
        mock_prompt.assert_any_call("Email (optional)", type=str, default="")
        mock_getpass.assert_any_call("Password: ")
        mock_getpass.assert_any_call("Confirm Password: ")

        user = await crud.get_user(db=db, username="testuser")
        assert user.username == "testuser"
        assert user.email == "testemail@asa.com"
        assert user.password == "hashedtestpassword"
        assert user.role == "admin"

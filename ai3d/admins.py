from datetime import timedelta

from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend

from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette import status

from . import models, auth, database


class UserAdmin(ModelView, model=models.User):
    column_list = [
        models.User.id,
        models.User.role,
        models.User.email,
        models.User.username,
    ]

    can_delete = False


class InteractionAdmin(ModelView, model=models.Interaction):
    column_list = [
        models.Interaction.id,
        models.Interaction.created_at,
    ]


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        async for db in database.get_db():
            user = await auth.authenticate_user(db, username, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        if user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
            )

        admin_token_expires = timedelta(days=auth.TOKEN_EXPIRATION)
        admin_token = auth.create_access_token(
            data={"sub": user.username}, expires_delta=admin_token_expires
        )
        request.session.update({"admin_token": admin_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("admin_token")

        if not token:
            return False

        # Check the token in depth
        return True

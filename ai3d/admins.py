from sqladmin import ModelView

from . import models


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

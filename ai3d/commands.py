import asyncclick as click
import inspect

from getpass import getpass
from typing import Callable, TypeVar, Generic, AsyncGenerator

from . import crud, schemas, database

T = TypeVar('T')


class Provider(Generic[T]):
    def __init__(self, factory: Callable[..., AsyncGenerator[T, None]]):
        self.factory = factory


def inject_db(f):
    async def wrapped(*args, **kwargs):
        sig = inspect.signature(f)
        bound_args = sig.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()

        for name, param in sig.parameters.items():
            if isinstance(bound_args.arguments[name], Provider):
                gen = bound_args.arguments[name].factory()
                async for item in gen:
                    bound_args.arguments[name] = item
                    await f(*bound_args.args, **bound_args.kwargs)

    return wrapped


@click.group()
def cli():
    pass


@cli.command(name="create_superuser")
@inject_db
async def create_superuser(db: database.AsyncSession = Provider(database.get_db)):
    username = click.prompt("Username", type=str)
    email = click.prompt("Email (optional)", type=str, default="")
    password = getpass("Password: ")
    confirm_password = getpass("Confirm Password: ")

    if password != confirm_password:
        click.echo("Passwords do not match")
        return

    user = schemas.UserAdminCreate(
        username=username,
        email=None if not email else email,
        password=password,
        role="admin",
    )
    await crud.create_user(db=db, user=user)


if __name__ == "__main__":
    cli()

cli.add_command(create_superuser)

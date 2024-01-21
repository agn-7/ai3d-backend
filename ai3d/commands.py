import asyncclick as click
import inspect

from getpass import getpass

from . import crud, schemas, database


class Provide:
    def __init__(self, value):
        self.value = value


def inject_db(f):
    sig = inspect.signature(f)

    async def wrapper(*args, **kwargs):
        for param in sig.parameters.values():
            if isinstance(param.default, Provide):
                async for db in param.default.value():
                    kwargs[param.name] = db
                    await f(*args, **kwargs)

    return wrapper


@click.group()
@click.pass_context
async def cli(ctx):
    pass


@cli.command(name="create_superuser")
@click.pass_context
@inject_db
async def create_superuser(ctx, db: database.AsyncSession = Provide(database.get_db)):
    if ctx.obj is not None:
        """ctx comes from test"""
        db = ctx.obj

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

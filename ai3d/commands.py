import asyncclick as click

from getpass import getpass

from . import crud, schemas, database


@click.group()
def cli():
    pass


@cli.command(name="create_superuser")
async def create_superuser():
    username = click.prompt("Username", type=str)
    email = click.prompt("Email (optional)", type=str, default="")
    password = getpass("Password: ")
    confirm_password = getpass("Confirm Password: ")

    if password != confirm_password:
        click.echo("Passwords do not match")
        return

    async for db in database.get_db():
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

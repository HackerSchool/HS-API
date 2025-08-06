import click

from sqlalchemy import select

from flask.cli import with_appcontext
from flask import Flask

from app.models.member_model import Member
from app.extensions import db

def register_cli_commands(app: Flask):
    @click.command("create-admin")
    @click.argument("username")
    @click.argument("password")
    @with_appcontext
    def create_admin_member(username, password):
        if db.session.execute(select(Member).where(Member.username == username)).scalars().one_or_none() is not None:
            click.echo(f'Member with name {username} already exists')
            return

        db.session.add(Member(username=username, password=password, name="admin", email="admin", roles=["sysadmin"]))
        db.session.commit()
        click.echo(f"Admin member '{username}' created successfully.")

    app.cli.add_command(create_admin_member)





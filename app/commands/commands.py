import os
import click

from flask import Flask

from app.extensions import db

# DEPRECATED please use migrations
def register_initialize_db_command(app: Flask):
    @app.cli.command('init-db')
    def initialize_db():
        from app.models import Project, Member, MemberProjects
        db.create_all()

def register_create_admin_user_command(app: Flask):
    @app.cli.command('create-admin')
    def populate_admin_user():
        from app.models import Member
        admin_username = app.config.get("ADMIN_USERNAME", "")
        admin_password = app.config.get("ADMIN_PASSWORD", "")
        if not admin_username or not admin_password:
            app.logger.warning("Missing environmental variables 'ADMIN_USERNAME' and 'ADMIN_PASSWORD")
            return

        if Member.query.filter_by(username=admin_username).first():
            app.logger.warning(f"User with name {admin_username} already exists")
            return

        admin = Member(
            username=admin_username,
            password=admin_password,
            ist_id="ist1"+admin_username,
            member_number=0,
            name=admin_username,
            join_date="1970-01-01",
            course=admin_username,
            email=admin_username,
            exit_date="",
            description="Admin user created with create-admin command",
            extra=admin_username,
            roles=["sysadmin"]
        )
        db.session.add(admin)
        db.session.commit()
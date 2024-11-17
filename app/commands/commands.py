import os
import click

from flask import Flask

from app.extensions import db
from app.extensions import roles_handler

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
            name=admin_username,
            email=admin_username,
            course=admin_username,
            member_number=0,
            join_date="1970-01-01",
            exit_date="",
            description="Admin user created with create-admin command",
            extra=admin_username,
            roles=["sysadmin"]
        )
        db.session.add(admin)
        db.session.commit()
    
def register_populate_dummy_db_command(app: Flask):
    @app.cli.command('populate-db')
    def populate_dummy():
        from app.models import Member, Project, MemberProjects
        def get_state(i: int) -> str:
            state = ["Active", "Ended", "Paused"]
            return state[i % len(state)]
            
        projects_names = ["wormhole", "time-machine", "rocket", "robotic-arm"]
        projects = []
        for i, p in enumerate(projects_names, 0):
            project = Project(
                name=p,
                start_date="1970-01-01",
                state=get_state(i),
                description=f"Project of a {p}"
            )
            projects.append(project)
            db.session.add(project)

        def get_course(i: int) -> str:
            courses = ["LEIC", "LMAC", "LEEC", "LEFT", "LMAer", "LETI", "LEBiom"]
            return courses[i % len(courses)]
        
        def random_proj(i: int) -> Project:
            return projects[i % len(projects)]

        roles = roles_handler.roles.keys()
        for i, r in enumerate(roles, 1):
            member = Member(
                username=r,
                password="password",
                ist_id="ist1"+str(i),
                name=r,
                email=f"{r}@hackerschool.dev",
                course=get_course(i),
                member_number=i,
                join_date="1970-01-01",
                exit_date="",
                description="Description",
                extra="",
                roles=[r]
            )
            assoc = MemberProjects(
                entry_date="1970-01-01",
            )
            assoc.member = member
            random_proj(i).members.append(assoc)

            db.session.add(member)
        db.session.commit()

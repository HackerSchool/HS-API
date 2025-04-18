# member_project.py
from typing import List

from app.extensions import db

from app.models import Member, Project, MemberProjects


def create_member_project(
    member: Member,
    project: Project,
    entry_date: str,
    contributions: str = "",
) -> MemberProjects:
    new_assoc = MemberProjects(
        entry_date=entry_date,
        contributions=contributions,
    )
    new_assoc.member = member
    project.members.append(new_assoc)
    db.session.commit()
    return new_assoc


def delete_member_project(
    member: Member,
    proj_name: str,
) -> int | None:
    project = Project.query.filter_by(name=proj_name).first()
    if not project or project not in member.projects:
        return None

    member.projects.remove(project)
    db.session.commit()

    return project.id


def delete_project_member(
    project: Project,
    username: str,
) -> int | None:
    member = Member.query.filter_by(username=username).first()
    if not member or project not in member.projects:
        return None

    project.members.remove(member)
    db.session.commit()

    return member.id


def get_member_projects(member: Member) -> List[MemberProjects]:
    return [assoc for assoc in member.projects if assoc.project]


def get_project_members(project: Project) -> List[Member]:
    return [assoc for assoc in project.members if assoc.member]

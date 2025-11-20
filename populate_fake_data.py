#!/usr/bin/env python3
"""
Script to populate the Hacker League API database with fake data for testing.
"""

import os
import sys
from datetime import date, timedelta
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import create_app
from app.extensions import db
from app.models.member_model import Member
from app.models.project_model import Project
from app.models.project_participation_model import ProjectParticipation
from app.models.task_model import Task
from app.models.team_task_model import TeamTask
from app.utils import ProjectStateEnum, PointTypeEnum

def create_fake_members():
    """Create fake members"""
    members_data = [
        {
            "username": "admin",
            "name": "Administrator",
            "email": "admin@tecnico.ulisboa.pt",
            "ist_id": "ist123456",
            "password": "admin123",
            "member_number": 1,
            "course": "LEIC",
            "join_date": "2023-09-01",
            "roles": ["sysadmin", "member"]
        },
        {
            "username": "alexchen",
            "name": "Alex Chen",
            "email": "alex.chen@tecnico.ulisboa.pt",
            "ist_id": "ist123457",
            "password": "password123",
            "member_number": 2,
            "course": "LEIC",
            "join_date": "2023-09-15",
            "roles": ["member"]
        },
        {
            "username": "mariasantos",
            "name": "Maria Santos",
            "email": "maria.santos@tecnico.ulisboa.pt",
            "ist_id": "ist123458",
            "password": "password123",
            "member_number": 3,
            "course": "LEIC",
            "join_date": "2023-10-01",
            "roles": ["member"]
        },
        {
            "username": "davidkim",
            "name": "David Kim",
            "email": "david.kim@tecnico.ulisboa.pt",
            "ist_id": "ist123459",
            "password": "password123",
            "member_number": 4,
            "course": "LEIC",
            "join_date": "2023-10-15",
            "roles": ["member"]
        },
        {
            "username": "sophiawang",
            "name": "Sophia Wang",
            "email": "sophia.wang@tecnico.ulisboa.pt",
            "ist_id": "ist123460",
            "password": "password123",
            "member_number": 5,
            "course": "LEIC",
            "join_date": "2023-11-01",
            "roles": ["member"]
        },
        {
            "username": "joaosilva",
            "name": "João Silva",
            "email": "joao.silva@tecnico.ulisboa.pt",
            "ist_id": "ist123461",
            "password": "password123",
            "member_number": 6,
            "course": "LEIC",
            "join_date": "2023-11-15",
            "roles": ["member"]
        },
        {
            "username": "anaribeiro",
            "name": "Ana Ribeiro",
            "email": "ana.ribeiro@tecnico.ulisboa.pt",
            "ist_id": "ist123462",
            "password": "password123",
            "member_number": 7,
            "course": "LEIC",
            "join_date": "2023-12-01",
            "roles": ["member"]
        },
        {
            "username": "pedroalves",
            "name": "Pedro Alves",
            "email": "pedro.alves@tecnico.ulisboa.pt",
            "ist_id": "ist123463",
            "password": "password123",
            "member_number": 8,
            "course": "LEIC",
            "join_date": "2023-12-15",
            "roles": ["member"]
        }
    ]
    
    existing_members = Member.query.all()
    members = []
    existing_usernames = {m.username for m in existing_members}
    existing_ist_ids = {m.ist_id for m in existing_members}
    for member_data in members_data:
        if member_data["username"] in existing_usernames or member_data["ist_id"] in existing_ist_ids:
            continue

        member = Member(**member_data)
        db.session.add(member)
        members.append(member)
        existing_usernames.add(member.username)
        existing_ist_ids.add(member.ist_id)
    
    db.session.commit()
    print(f"Created {len(members)} members")
    return Member.query.all()

def create_fake_projects():
    """Create fake projects"""
    projects_data = [
        {
            "name": "Hacker League Web App",
            "state": ProjectStateEnum.ACTIVE,
            "start_date": "2023-09-01",
            "description": "Main web application for the Hacker League gamification system"
        },
        {
            "name": "API Development",
            "state": ProjectStateEnum.ACTIVE,
            "start_date": "2023-09-15",
            "description": "Backend API for Hacker League system"
        },
        {
            "name": "Mobile App",
            "state": ProjectStateEnum.ACTIVE,
            "start_date": "2023-10-01",
            "description": "Mobile application for Hacker League"
        },
        {
            "name": "Database Optimization",
            "state": ProjectStateEnum.ACTIVE,
            "start_date": "2023-10-15",
            "description": "Database performance optimization project"
        },
        {
            "name": "Testing Framework",
            "state": ProjectStateEnum.INACTIVE,
            "start_date": "2023-11-01",
            "end_date": "2023-12-01",
            "description": "Automated testing framework development"
        }
    ]
    
    projects = []
    existing_names = {p.name for p in Project.query.all()}
    existing_slugs = {p.slug for p in Project.query.all()}

    for project_data in projects_data:
        if project_data["name"] in existing_names:
            continue

        project = Project(**project_data)
        db.session.add(project)
        projects.append(project)
        existing_names.add(project.name)
        existing_slugs.add(project.slug)
    
    db.session.commit()
    print(f"Created {len(projects)} projects")
    return Project.query.all()

def create_fake_participations(members, projects):
    """Create fake project participations"""
    if not members:
        members = Member.query.all()
    if not members:
        print("Created 0 project participations (no members available)")
        return ProjectParticipation.query.all()

    member_lookup = {m.username: m for m in members}
    admin_member = member_lookup.get("admin") or members[0]

    team_leader_1 = member_lookup.get("alexchen")
    if team_leader_1 is None or team_leader_1.id == admin_member.id:
        team_leader_1 = next(
            (m for m in members if m.id != admin_member.id),
            admin_member
        )

    team_leader_2 = member_lookup.get("davidkim")
    if team_leader_2 is None or team_leader_2.id in {admin_member.id, team_leader_1.id}:
        team_leader_2 = next(
            (m for m in members if m.id not in {admin_member.id, team_leader_1.id}),
            team_leader_1
        )

    excluded_ids = {admin_member.id, team_leader_1.id, team_leader_2.id}
    remaining_members = [m for m in members if m.id not in excluded_ids]

    participations = []

    existing_pairs = {
        (pp.member_id, pp.project_id)
        for pp in ProjectParticipation.query.all()
    }
    
    # Admin participates in all projects
    for project in projects:
        participation = ProjectParticipation(
            member=admin_member,
            project=project,
            roles=["admin"],
            join_date=project.start_date
        )
        if (participation.member_id, participation.project_id) not in existing_pairs:
            db.session.add(participation)
            participations.append(participation)
            existing_pairs.add((participation.member_id, participation.project_id))
    
    # Team leaders participate in multiple projects
    for i, project in enumerate(projects[:3]):  # First 3 projects
        participation = ProjectParticipation(
            member=team_leader_1,
            project=project,
            roles=["team_leader"],
            join_date=project.start_date
        )
        if (participation.member_id, participation.project_id) not in existing_pairs:
            db.session.add(participation)
            participations.append(participation)
            existing_pairs.add((participation.member_id, participation.project_id))
        
        participation = ProjectParticipation(
            member=team_leader_2,
            project=project,
            roles=["team_leader"],
            join_date=project.start_date
        )
        if (participation.member_id, participation.project_id) not in existing_pairs:
            db.session.add(participation)
            participations.append(participation)
            existing_pairs.add((participation.member_id, participation.project_id))
    
    # Regular members participate in 1-2 projects each
    for member in remaining_members:
        # Each member participates in 1-2 random projects
        num_projects = random.randint(1, 2)
        selected_projects = random.sample(projects, min(num_projects, len(projects)))
        
        for project in selected_projects:
            participation = ProjectParticipation(
                member=member,
                project=project,
                roles=["member"],
                join_date=project.start_date
            )
            if (participation.member_id, participation.project_id) not in existing_pairs:
                db.session.add(participation)
                participations.append(participation)
                existing_pairs.add((participation.member_id, participation.project_id))
    
    db.session.commit()
    print(f"Created {len(participations)} project participations")
    return ProjectParticipation.query.all()

def create_fake_tasks(participations):
    """Create fake tasks"""
    task_descriptions = [
        "Implemented user authentication system",
        "Fixed bug in leaderboard calculation",
        "Added new API endpoint for user profiles",
        "Optimized database queries",
        "Created unit tests for member model",
        "Updated frontend components",
        "Implemented real-time notifications",
        "Added data validation",
        "Created documentation",
        "Fixed security vulnerabilities",
        "Implemented caching system",
        "Added error handling",
        "Created integration tests",
        "Optimized image upload",
        "Implemented search functionality"
    ]
    
    tasks = []
    for participation in participations:
        # Each participation gets 2-5 tasks
        num_tasks = random.randint(2, 5)
        
        for i in range(num_tasks):
            # Random date between project start and now
            start_date = date.fromisoformat(participation.join_date)
            end_date = date.today()
            days_diff = (end_date - start_date).days
            random_days = random.randint(0, max(0, days_diff - 1))
            task_date = start_date + timedelta(days=random_days)
            
            task = Task(
                participation=participation,
                point_type=random.choice([PointTypeEnum.PJ, PointTypeEnum.PCC, PointTypeEnum.PS]),
                points=random.randint(5, 50),
                description=random.choice(task_descriptions),
                finished_at=task_date.isoformat()
            )
            db.session.add(task)
            tasks.append(task)
    
    db.session.commit()
    print(f"Created {len(tasks)} tasks")
    return Task.query.all()


def create_fake_team_tasks(projects):
    """Create fake team tasks"""
    team_task_descriptions = [
        "Team completed milestone delivery",
        "Presented sprint demo to stakeholders",
        "Organized internal knowledge sharing session",
        "Resolved high priority production issue",
        "Prepared release notes and documentation",
    ]

    team_tasks = []
    for project in projects:
        db.session.refresh(project)
        participants = [pp.member.username for pp in project.project_participations]
        if not participants:
            continue

        existing_tasks = {
            (task.description, task.finished_at or "")
            for task in project.team_tasks
        }
        num_team_tasks = random.randint(1, 3)
        for _ in range(num_team_tasks):
            contributors = random.sample(
                participants,
                k=min(len(participants), random.randint(1, min(3, len(participants))))
            )

            start_date = date.fromisoformat(project.start_date)
            end_date = date.today()
            days_diff = (end_date - start_date).days
            random_days = random.randint(0, max(0, days_diff)) if days_diff > 0 else 0
            finished_at = (start_date + timedelta(days=random_days)).isoformat()

            description = random.choice(team_task_descriptions)
            if (description, finished_at or "") in existing_tasks:
                continue

            team_task = TeamTask(
                project=project,
                point_type=random.choice([PointTypeEnum.PJ, PointTypeEnum.PCC, PointTypeEnum.PS]),
                points=random.randint(10, 80),
                description=description,
                finished_at=finished_at,
                contributors=contributors,
            )
            db.session.add(team_task)
            team_tasks.append(team_task)
            existing_tasks.add((description, finished_at or ""))

    db.session.commit()
    print(f"Created {len(team_tasks)} team tasks")
    return TeamTask.query.all()

def main():
    """Main function to populate the database"""
    print("🚀 Starting Hacker League API database population...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Check if data already exists
        existing_members = Member.query.count()
        if existing_members > 0:
            print(f"⚠️  Database already contains {existing_members} members. Adding test data...")
        
        # Create fake data
        members = create_fake_members()
        projects = create_fake_projects()
        participations = create_fake_participations(members, projects)
        tasks = create_fake_tasks(participations)
        team_tasks = create_fake_team_tasks(projects)
        
        print("\n🎉 Database populated successfully!")
        print(f"📊 Summary:")
        print(f"   - Members: {len(members)}")
        print(f"   - Projects: {len(projects)}")
        print(f"   - Participations: {len(participations)}")
        print(f"   - Tasks: {len(tasks)}")
        print(f"   - Team Tasks: {len(team_tasks)}")
        
        print("\n🔑 Test credentials:")
        print("   - admin / admin123 (Administrator)")
        print("   - alexchen / password123 (Team Leader)")
        print("   - mariasantos / password123 (Member)")
        print("   - davidkim / password123 (Team Leader)")

if __name__ == "__main__":
    main()


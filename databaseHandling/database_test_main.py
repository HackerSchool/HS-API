# main.py
from database_handler import DatabaseHandler
from member import create_member, list_members, get_member_id_by_name, delete_member
from project import create_project, list_projects, get_project_id_by_name, delete_project
from member_project import associate_member_with_project, list_projects_for_member, list_members_for_project
from datetime import date

def main():
    # Initialize the database handler with the database name
    db_handler = DatabaseHandler('hackerschool.db')

    # Example: Creating some members
    create_member(db_handler, 'ist123', 1, 'John Doe', 'johndoe', 'password', str(date.today()), 'Computer Science', 'Student', '{}', 'path/to/logo.png', ['tag1', 'tag2'])
    create_member(db_handler, 'ist124', 2, 'Jane Doe', 'janedoe', 'password', str(date.today()), 'Electrical Engineering', 'Student', '{}', 'path/to/logo.png', ['tag2', 'tag3'])

    # Example: Creating some projects
    create_project(db_handler, 'Project Alpha', 'Description of Project Alpha', str(date.today()), 'Ongoing', 'path/to/alpha_logo.png')
    create_project(db_handler, 'Project Beta', 'Description of Project Beta', str(date.today()), 'Planned', 'path/to/beta_logo.png')

    # Example: Associating members with projects using the get_member_id_by_name and get_project_id_by_name functions
    john_id = get_member_id_by_name(db_handler, 'John Doe')
    jane_id = get_member_id_by_name(db_handler, 'Jane Doe')
    alpha_id = get_project_id_by_name(db_handler, 'Project Alpha')
    beta_id = get_project_id_by_name(db_handler, 'Project Beta')

    associate_member_with_project(db_handler, john_id, alpha_id, str(date.today()), None)  # John Doe in Project Alpha
    associate_member_with_project(db_handler, jane_id, alpha_id, str(date.today()), None)  # Jane Doe in Project Alpha
    associate_member_with_project(db_handler, john_id, beta_id, str(date.today()), None)  # John Doe in Project Beta

    # Example: Listing all projects for John Doe
    john_projects = list_projects_for_member(db_handler, john_id)  # John Doe's projects
    print("Projects for John Doe:", john_projects)

    # Example: Listing all members for Project Alpha
    alpha_members = list_members_for_project(db_handler, alpha_id)  # Members in Project Alpha
    print("Members in Project Alpha:", alpha_members)

    # Deleting members and projects
    delete_member(db_handler, john_id)
    delete_member(db_handler, jane_id)
    delete_project(db_handler, alpha_id)
    delete_project(db_handler, beta_id)

    create_member(db_handler, 'ist1103592', 1, 'Filipe Piçarra', 'fpicarras', 'password', str(date.today()), 'MEEC', 'Student', '{}', 'path/to/logo.png', ['sysadmin', 'dev']) 

if __name__ == '__main__':
    main()


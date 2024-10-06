# member_project.py
import sqlite3

class MemberProjectHandler:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def validate_request(cursor, member_id, project_id):
        cursor.execute('SELECT * FROM Members WHERE ID = ?', (member_id,))
        if not cursor.fetchone():
            print(f"Member {member_id} does not exist.")
            return False
        cursor.execute('SELECT * FROM Projects WHERE ID = ?', (project_id,))
        if not cursor.fetchone():
            print(f"Project {project_id} does not exist.")
            return False
        return True

    def associateMemberWithProject(self, member_id, project_id, entry_date, contributions, exit_date=None):
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()

            # If member or project does not exist, return
            if not self.validate_request(cursor, member_id, project_id):
                return
            # If member-project relationship already exists, return
            cursor.execute('SELECT * FROM MemberProject WHERE MemberID = ? AND ProjectID = ?', (member_id, project_id))
            if cursor.fetchone():
                print(f"Member {member_id} is already associated with project {project_id}.")
                return
            cursor.execute('''
                INSERT INTO MemberProject (MemberID, ProjectID, Entry_date, Contributions, Exit_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (member_id, project_id, entry_date, contributions, exit_date))
            conn.commit()
            print(f"Member {member_id} associated with project {project_id} successfully!")

    def editMemberProjectRelation(self, member_id, project_id, **kwargs):
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()

            # If member-project relationship does not exist, return
            cursor.execute('SELECT * FROM MemberProject WHERE MemberID = ? AND ProjectID = ?', (member_id, project_id))
            if not cursor.fetchone():
                print(f"Member {member_id} is not associated with project {project_id}.")
                return
            columns = ', '.join(f"{key} = ?" for key in kwargs.keys())
            values = list(kwargs.values())
            values.append(member_id)
            values.append(project_id)
            query = f"UPDATE MemberProject SET {columns} WHERE MemberID = ? AND ProjectID = ?"
            cursor.execute(query, values)
            conn.commit()
            print(f"Member-Project relationship for MemberID {member_id} and ProjectID {project_id} updated successfully!")

    # Function to list all projects a member is in, ordered by entry date
    def listProjectsForMember(self, member_id):
        query = """
        SELECT p.ID, p.Name, p.Description, p.Start_date, p.State, p.Logo, mp.Entry_date, mp.Exit_date
        FROM MemberProject mp
        JOIN Projects p ON mp.ProjectID = p.ID
        WHERE mp.MemberID = ?
        ORDER BY mp.Entry_date
        """
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (member_id,))
            projects = cursor.fetchall()

        return projects  # Return the list of projects for the member

    # Function to list all members in a project, ordered by entry date
    def listMembersForProject(self, project_id):
        query = """
        SELECT m.ID, m.Name, m.Username, mp.Entry_date, mp.Exit_date
        FROM MemberProject mp
        JOIN Members m ON mp.MemberID = m.ID
        WHERE mp.ProjectID = ?
        ORDER BY mp.Entry_date
        """
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (project_id,))
            members = cursor.fetchall()

        return members  # Return the list of members in the project
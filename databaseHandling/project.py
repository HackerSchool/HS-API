# project.py
import sqlite3

class ProjectHandler:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def createProject(self, name, description, start_date, state, logo):
        try:
            with self.db_handler.get_connection() as conn:
                cursor = conn.cursor()

                # If project with the same name already exists, return
                cursor.execute('SELECT * FROM Projects WHERE Name = ?', (name,))
                if cursor.fetchone():
                    print(f"Project with the name \"{name}\" already exists.")
                    return (False, "Project with the same name already exists.")
                cursor.execute('''
                    INSERT INTO Projects (Name, Description, Start_date, State, Logo)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, description, start_date, state, logo))
                conn.commit()
                print(f"Project {name} created successfully!")
                return (True,)
        except sqlite3.IntegrityError as e:
            print(f"Error: {str(e)} (Can't open Database)")
            return (False, "Can't open Database")

    def editProject(self, project_id, **kwargs):
        try:
            with self.db_handler.get_connection() as conn:
                cursor = conn.cursor()
                columns = ', '.join(f"{key} = ?" for key in kwargs.keys())
                values = list(kwargs.values())
                values.append(project_id)
                query = f"UPDATE Projects SET {columns} WHERE ID = ?"
                cursor.execute(query, values)
                conn.commit()
                print(f"Project with ID {project_id} updated successfully!")
                return (True,)
        except sqlite3.IntegrityError as e:
            print(f"Error: {str(e)} (There may be a conflict with unique values.)")
            return (False, "There may be a conflict with unique values.")

    def deleteProject(self, project_id):
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()

            # Delete associated relationships from MemberProject
            cursor.execute('DELETE FROM MemberProject WHERE ProjectID = ?', (project_id,))

            # Delete project from Projects table
            cursor.execute('DELETE FROM Projects WHERE ID = ?', (project_id,))
            conn.commit()

            print(f"Project with ID {project_id} and its relations have been deleted.")

    def listProjects(self, **filters):
        query = "SELECT * FROM Projects"
        conditions = []
        values = []

        # Build the query based on the provided filters
        for key, value in filters.items():
            conditions.append(f"{key} = ?")
            values.append(value)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            projects = cursor.fetchall()

        return projects  # Return the list of projects

    def getProjectIdByName(self, project_name):
        query = "SELECT ID FROM Projects WHERE Name = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (project_name,))
            result = cursor.fetchone()
        
        return result[0] if result else None  # Return the ID if found, otherwise None

    def getProjectInfo(self, projectName):
        query = "SELECT * FROM Projects WHERE Name = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (projectName,))
            result = cursor.fetchone()
        
        return result if result else None      # Return the project information

    def exists(self, proj_id):
        query = "SELECT * FROM Projects WHERE ID = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (proj_id,))
            result = cursor.fetchone()
        return result is not None
    
    def getLogo(self, proj_id):
        query = "SELECT Logo FROM Projects WHERE ID = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (proj_id,))
            result = cursor.fetchone()
        
        return result[0] if result else None  # Return the logo if found, otherwise None
    
    def setLogo(self, proj_id, logo):
        query = "UPDATE Projects SET Logo = ? WHERE ID = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (logo, proj_id))
            conn.commit()
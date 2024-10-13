# member.py
import sqlite3, time
import bcrypt

# Hashing the password
def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

class MemberHandler:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def createMember(self, istID, memberNumber, name, username, password, entry_date, course, description, mail, extra, logo, tags):
        try:
            with self.db_handler.get_connection() as conn:
                hash = hash_password(password)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Members (istID, memberNumber, Name, Username, Password, Entry_date, Course, Description, Mail, Extra, Logo, Tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (istID, memberNumber, name, username, hash, entry_date, course, description, mail, extra, logo, ",".join(tags)))
                conn.commit()
                print(f"Member {name} created successfully!")
                return (True,)
        except sqlite3.IntegrityError as e:
            print(f"Error: {str(e)} (A member with this istID, memberNumber, or username may already exist.)")
            return (False, "A member with this istID, memberNumber, or username may already exist.")

    def editMember(self, member_id, **kwargs):
        if not kwargs:
            print("No fields to update.")
            return (False, "No fields to update.")
        try:
            with self.db_handler.get_connection() as conn:
                # Hash the password if it is being updated
                if 'password' in kwargs:
                    kwargs['password'] = hash_password(kwargs['password'])
                cursor = conn.cursor()
                columns = ', '.join(f"{key} = ?" for key in kwargs.keys())
                values = list(kwargs.values())
                values.append(member_id)
                query = f"UPDATE Members SET {columns} WHERE ID = ?"
                cursor.execute(query, values)
                conn.commit()
                print(f"Member with ID {member_id} updated successfully!")
                return (True, f"Member with ID {member_id} updated successfully!")
        except sqlite3.IntegrityError as e:
            print(f"Error: {str(e)} (There may be a conflict with unique values.)")
            return (False, "There may be a conflict with unique values.")

    def deleteMember(self, member_id):
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()

            # Delete associated relationships from MemberProject
            cursor.execute('DELETE FROM MemberProject WHERE MemberID = ?', (member_id,))

            # Delete member from Members table
            cursor.execute('DELETE FROM Members WHERE ID = ?', (member_id,))
            conn.commit()

            print(f"Member with ID {member_id} and their relations have been deleted.")
            return (True, f"Member with ID {member_id} and their relations have been deleted.")

    def addTag(self, member_id, tag):
        return_message = ""

        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT Tags FROM Members WHERE ID = ?', (member_id,))
            tags = cursor.fetchone()[0].split(',')
            if tag not in tags:
                tags.append(tag)
                cursor.execute('UPDATE Members SET Tags = ? WHERE ID = ?', (",".join(tags), member_id))
                conn.commit()
                print(f"Tag '{tag}' added to member {member_id}.")
                return_message = f"Tag '{tag}' added to member {member_id}."
            else:
                print(f"Tag '{tag}' already exists for member {member_id}.")
                return_message = f"Tag '{tag}' already exists for member {member_id}."
            return (True, return_message)

    def removeTag(self, member_id, tag):
        return_message = ""

        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT Tags FROM Members WHERE ID = ?', (member_id,))
            tags = cursor.fetchone()[0].split(',')
            if tag in tags:
                tags.remove(tag)
                cursor.execute('UPDATE Members SET Tags = ? WHERE ID = ?', (",".join(tags), member_id))
                conn.commit()
                print(f"Tag '{tag}' removed from member {member_id}.")
                return_message = f"Tag '{tag}' removed from member {member_id}."
            else:
                print(f"Tag '{tag}' not found for member {member_id}.")
                return_message = f"Tag '{tag}' not found for member {member_id}."
            return (True, return_message)

    def getTags(self, member_username):
        query = "SELECT Tags FROM Members WHERE Username = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (member_username,))
            result = cursor.fetchone()
        
        return result[0].split(',') if result else None  # Return the list of tags if found, otherwise None


    def listMembers(self, **filters):
        query = "SELECT * FROM Members"
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
            members = cursor.fetchall()

        return members  # Return the list of members

    def getMemberIdByName(self, member_name):
        query = "SELECT ID FROM Members WHERE Name = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (member_name,))
            result = cursor.fetchone()
        
        return result[0] if result else None  # Return the ID if found, otherwise None

    def getMemberIdByUsername(self, username):
        query = "SELECT ID FROM Members WHERE Username = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username,))
            result = cursor.fetchone()
        
        return result[0] if result else None  # Return the ID if found, otherwise None

    def getMemberInfo(self, username):
        query = "SELECT * FROM Members WHERE Username = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username,))
            result = cursor.fetchone()
        
        return result if result else None  # Return the member info if found, otherwise None
    
    def getLogo(self, username):
        query = "SELECT Logo FROM Members WHERE Username = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username,))
            result = cursor.fetchone()
        
        return result[0] if result else None  # Return the logo if found, otherwise None
    
    def setLogo(self, username, logo):
        query = "UPDATE Members SET Logo = ? WHERE Username = ?"
        
        with self.db_handler.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (logo, username))
            conn.commit()
        
        print(f"Logo for member {username} updated successfully!")
        return True
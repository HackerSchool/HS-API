import sqlite3

class LoginManager:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def login(self, username, password):
        # If there is a username and a login that matches the input, return an hach with the user's data
        # Otherwise, return None
        conn = self.db_handler.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM members WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        if user:
            # Get the user's tags
            query = "SELECT Tags FROM Members WHERE Username = ?"        
            with self.db_handler.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (username,))
                result = cursor.fetchone()
            return result[0] if result else None  # Return the list of tags if found, otherwise None
        else:
            return None
    
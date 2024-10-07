import sqlite3, bcrypt

# Verifying the password
def check_password(stored_hash, password):
    # Ensure stored_hash is bytes; if stored as a string in DB, convert it back
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')
    
    # Check if the password matches the hash
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

class LoginManager:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def login(self, username, password):
        # If there is a username and a login that matches the input, return an hach with the user's data
        # Otherwise, return None
        conn = self.db_handler.get_connection()
        c = conn.cursor()
        # Check if the username exists and get it's hashed password
        c.execute("SELECT * FROM members WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if not user or not check_password(user[5], password):
            return None
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
    
# database_handler.py
import sqlite3

def setup_database():
    # Create a connection to the SQLite database
    conn = sqlite3.connect('hackerschool.db', check_same_thread=False)
    
    # Create a cursor object
    cursor = conn.cursor()

    # Create Members table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Members (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        istID TEXT NOT NULL,
        memberNumber INTEGER UNIQUE NOT NULL,
        Name TEXT NOT NULL,
        Username TEXT UNIQUE NOT NULL,
        Password TEXT NOT NULL,
        Entry_date TEXT NOT NULL,
        Exit_date TEXT,
        Course TEXT,
        Description TEXT,
        Extra TEXT,
        Logo TEXT,
        Tags TEXT
    );
    ''')

    # Create Projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Projects (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT,
        Start_date TEXT NOT NULL,
        State TEXT,
        Logo TEXT
    );
    ''')

    # Create MemberProject (junction) table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS MemberProject (
        MemberID INTEGER,
        ProjectID INTEGER,
        Entry_date TEXT NOT NULL,
        Contributions TEXT,
        Exit_date TEXT,
        PRIMARY KEY (MemberID, ProjectID),
        FOREIGN KEY (MemberID) REFERENCES Members(ID),
        FOREIGN KEY (ProjectID) REFERENCES Projects(ID)
    );
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

class DatabaseHandler:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db_setup = False

    def get_connection(self):
        try:
            if not self.db_setup:
                setup_database()
                self.db_setup = True
            conn = sqlite3.connect(self.db_name)
        except sqlite3.OperationalError:
            print("Error: Database not found or could not be opened.")
            return None
        return conn

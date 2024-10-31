# database_handler.py
import sqlite3

from flask import Flask

def setup_database(db_name: str) -> None:
    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_name, check_same_thread=False)
    
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
        Mail TEXT,
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
    def __init__(self):
        self.db_name = None 
        self.db_setup = False

    def init_app(self, app: Flask) -> None:
        self.db_name = app.config['DATABASE_PATH']

    def get_connection(self) -> sqlite3.Connection:
        try:
            if not self.db_setup:
                setup_database(self.db_name)
                self.db_setup = True
            conn = sqlite3.connect(self.db_name)
        except sqlite3.OperationalError:
            print(f"Error: Database '%s' not found or could not be opened.", self.db_name)
            return None
        return conn

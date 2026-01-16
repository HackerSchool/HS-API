#!/usr/bin/env python3
"""
Script to change a user's password in the Hacker League API database.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import create_app
from app.extensions import db
from app.models.member_model import Member

def change_password(username: str, new_password: str):
    """Change password for a user"""
    app = create_app()
    
    with app.app_context():
        # Find the user
        member = db.session.query(Member).filter_by(username=username).first()
        
        if not member:
            print(f"❌ User '{username}' not found!")
            return False
        
        # Change password using the setter (which will hash it automatically)
        member.password = new_password
        
        # Commit the change
        db.session.commit()
        
        print(f"✅ Password changed successfully for user '{username}'!")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python change_password.py <username> <new_password>")
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    
    change_password(username, new_password)


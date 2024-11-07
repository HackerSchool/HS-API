import bcrypt

from app.models import Member

from app.services.login_service import exceptions

# Verifying the password
def _check_password(stored_hash, password):
    # Ensure stored_hash is bytes; if stored as a string in DB, convert it back
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')
    
    # Check if the password matches the hash
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

def login(username, password):
    member = Member.query.filter_by(username=username).first()
    if not member or not _check_password(member.password, password):
        raise exceptions.AuthError("Invalid credentials")
    return [member.tags,] if "," not in member.tags else member.tags.split(",")
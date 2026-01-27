import json
import os
from datetime import datetime

DB_FILE = 'users.json'

def init_db():
    """Initialize the users file if it doesn't exist."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump([], f)

def get_all_users():
    """Read all users from the file."""
    init_db()
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_users(users):
    """Write list of users to the file."""
    with open(DB_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def get_user_by_email(email):
    """Find a user by email."""
    users = get_all_users()
    for user in users:
        if user.get('email') == email:
            return user
    return None

def get_user_by_id(user_id):
    """Find a user by ID."""
    users = get_all_users()
    for user in users:
        if user.get('id') == user_id:
            return user
    return None

def create_user(first_name, last_name, mobile, email, password_hash):
    """Create a new user and save to storage."""
    users = get_all_users()
    
    # Check if email already exists
    if get_user_by_email(email):
        return False, "Email already exists"

    new_user = {
        'id': str(len(users) + 1),  # Simple ID generation
        'first_name': first_name,
        'last_name': last_name,
        'mobile': mobile,
        'email': email,
        'password_hash': password_hash,
        'created_at': datetime.now().isoformat()
    }
    
    users.append(new_user)
    save_users(users)
    return True, new_user

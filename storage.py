from models import db, User, HistoryItem
from datetime import datetime
import os

def init_db():
    """Initialize the database tables."""
    db.create_all()

def get_all_users():
    """Read all users."""
    users = User.query.all()
    return [u.to_dict() for u in users]

def get_user_by_email(email):
    """Find a user by email."""
    user = User.query.filter_by(email=email).first()
    return user.to_dict() if user else None

def get_user_by_id(user_id):
    """Find a user by ID."""
    user = db.session.get(User, int(user_id))
    return user.to_dict() if user else None

def create_user(first_name, last_name, mobile, email, password_hash):
    """Create a new user and save to storage."""
    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return False, "Email already exists"

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        mobile=mobile,
        email=email,
        password_hash=password_hash
    )
    db.session.add(new_user)
    
    try:
        db.session.commit()
        return True, new_user.to_dict()
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def add_score(user_id, points):
    """Adds gamification points to a user."""
    user = db.session.get(User, int(user_id))
    if user:
        if user.developer_score is None:
            user.developer_score = 0
        user.developer_score += int(points)
        try:
            db.session.commit()
            return True, user.developer_score
        except Exception:
            db.session.rollback()
    return False, 0

def save_history(user_id, action_type, code, result):
    """Save an analysis or generation result to a user's history in SQLite."""
    user = db.session.get(User, int(user_id))
    if not user:
        return False
        
    code_snippet = code[:200] + '...' if len(code) > 200 else code
            
    history_item = HistoryItem(
        user_id=int(user_id),
        type=action_type,
        code_snippet=code_snippet,
        result=result
    )
    db.session.add(history_item)
    
    # Check history count
    count = HistoryItem.query.filter_by(user_id=int(user_id)).count()
    if count >= 50:
        # keep last 49 + the new 1
        excess = count - 49
        oldest = HistoryItem.query.filter_by(user_id=int(user_id)).order_by(HistoryItem.timestamp.asc()).limit(excess).all()
        for item in oldest:
            db.session.delete(item)
            
    try:
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

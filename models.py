from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    developer_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to history
    history = db.relationship('HistoryItem', backref='user', lazy=True, order_by='desc(HistoryItem.timestamp)')
    
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "mobile": self.mobile,
            "email": self.email,
            "password_hash": self.password_hash,
            "developer_score": self.developer_score if self.developer_score else 0,
            "level": (self.developer_score // 100) + 1 if self.developer_score else 1,
            "history": [item.to_dict() for item in self.history]
        }

class HistoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # "analysis", "test_generation"
    code_snippet = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "type": self.type,
            "code_snippet": self.code_snippet,
            "result": self.result,
            "created_at": self.timestamp.isoformat()
        }

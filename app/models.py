"""
app/models.py  —  Week 3: Post Model Added
"""
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(db.Model, UserMixin):
    """Registered user."""
    __tablename__ = 'user'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),  unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    joined   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    posts    = db.relationship('Post', backref='author', lazy=True,
                               cascade='all, delete-orphan')

    def __repr__(self): return f"User('{self.username}')"


class Post(db.Model):
    """A blog post written by a User."""
    __tablename__ = 'post'
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    content     = db.Column(db.Text, nullable=False)
    category    = db.Column(db.String(50), nullable=False, default='General')
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    author_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self): return f"Post('{self.title}')"

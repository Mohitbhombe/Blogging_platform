"""
app/models.py  —  Week 4: Comment Model Added
"""
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(db.Model, UserMixin):
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
    __tablename__ = 'post'
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    content     = db.Column(db.Text, nullable=False)
    category    = db.Column(db.String(50), nullable=False, default='General')
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    author_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments    = db.relationship('Comment', backref='post', lazy=True,
                                  cascade='all, delete-orphan')

    def __repr__(self): return f"Post('{self.title}')"


class Comment(db.Model):
    """A comment on a blog post."""
    __tablename__ = 'comment'
    id          = db.Column(db.Integer, primary_key=True)
    body        = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    post_id     = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    commenter   = db.relationship('User', backref='comments', lazy=True)

    def __repr__(self): return f"Comment(post={self.post_id}, by={self.author_id})"

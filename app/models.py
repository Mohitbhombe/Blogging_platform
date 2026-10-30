"""
app/models.py
Database Models
----------------
Defines the structure of our database tables as Python classes.
Flask-SQLAlchemy converts these classes into actual database tables.

UserMixin from Flask-Login adds helper methods:
  - is_authenticated (True if user is logged in)
  - is_active         (True if user account is active)
  - get_id()          (Returns the user's ID as a string)
"""

from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone


# ── User Loader ───────────────────────────────────────────────────────
# Flask-Login needs this to reload the user from the session.
# Every time a page loads, it calls this function with the stored user ID
# to get the current user object.
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ── User Table ────────────────────────────────────────────────────────
class User(db.Model, UserMixin):
    """
    Represents a registered user in the database.
    Maps to the 'user' table in SQLite.
    """
    __tablename__ = 'user'

    # Columns (each variable = one column in the table)
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)   # stores hashed password
    joined   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship: One user can have many posts (added in Week 3)
    # posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        """String representation — useful for debugging."""
        return f"User('{self.username}', '{self.email}')"

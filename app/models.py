"""
app/models.py
Database Models
----------------
Week 3 adds the Post model.
Week 4 adds the Comment model.
Week 5 adds bio/avatar_color to User.
Week 6 adds the Like model (Post likes) + reading_time property on Post.
- One User can have MANY Posts (One-to-Many relationship)
- One Post can have MANY Comments
- Each Comment belongs to a User and a Post
- One Post can be liked by MANY Users (Many-to-Many via Like)
"""

from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone
import math


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ── User Table ────────────────────────────────────────────────────────
class User(db.Model, UserMixin):
    """Registered user in the database."""
    __tablename__ = 'user'

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(20),  unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password     = db.Column(db.String(256), nullable=False)
    joined       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Week 5: profile fields
    bio          = db.Column(db.String(300), nullable=True, default='')
    avatar_color = db.Column(db.String(7),  nullable=False, default='#6c63ff')

    # ── Relationships ──────────────────────────────────────────────
    # 'posts' gives us user.posts — a list of all posts by this user
    # backref='author' lets us use post.author to get the user object
    # lazy=True means posts are only loaded from DB when accessed
    posts = db.relationship('Post', backref='author', lazy=True,
                            cascade='all, delete-orphan')

    # Week 6: likes relationship
    likes = db.relationship('Like', backref='user', lazy=True,
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


# ── Post Table ────────────────────────────────────────────────────────
class Post(db.Model):
    """
    A blog post written by a User.

    Relationship:
        Post.author_id  →  User.id   (Foreign Key)
        post.author     →  User object (via backref in User model)
    """
    __tablename__ = 'post'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    content     = db.Column(db.Text, nullable=False)
    category    = db.Column(db.String(50), nullable=False, default='General')
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign Key: links this post to a user in the 'user' table
    author_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship — one post can have many comments
    comments = db.relationship('Comment', backref='post', lazy=True,
                               cascade='all, delete-orphan')

    # Week 6: likes relationship
    likes = db.relationship('Like', backref='post', lazy=True,
                            cascade='all, delete-orphan')

    @property
    def reading_time(self):
        """
        Week 6: Estimated reading time in minutes.
        Average reading speed: ~200 words per minute.
        """
        word_count = len(self.content.split())
        minutes = math.ceil(word_count / 200)
        return max(1, minutes)

    @property
    def like_count(self):
        """Return number of likes for this post."""
        return len(self.likes)

    def is_liked_by(self, user):
        """Return True if the given user has liked this post."""
        return any(like.user_id == user.id for like in self.likes)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# ── Comment Table ─────────────────────────────────────────────────────
class Comment(db.Model):
    """
    A comment left on a blog post by a registered user.

    Relationships:
        Comment.post_id   → Post.id   (Foreign Key)
        Comment.author_id → User.id   (Foreign Key)
        comment.post      → Post object  (via backref in Post model)
        comment.author    → User object  (via backref in User model)
    """
    __tablename__ = 'comment'

    id          = db.Column(db.Integer, primary_key=True)
    body        = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign Keys
    post_id   = db.Column(db.Integer, db.ForeignKey('post.id'),   nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'),   nullable=False)

    # backref lets us use comment.author to get the User object
    commenter = db.relationship('User', backref='comments', lazy=True)

    def __repr__(self):
        return f"Comment(post={self.post_id}, by={self.author_id})"


# ── Like Table (Week 6) ───────────────────────────────────────────────
class Like(db.Model):
    """
    A like/upvote given by a User to a Post.
    Uses a composite unique constraint to prevent duplicate likes.

    Relationships:
        Like.user_id → User.id (Foreign Key)
        Like.post_id → Post.id (Foreign Key)
    """
    __tablename__ = 'like'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Composite unique constraint: one user can only like a post once
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),
    )

    def __repr__(self):
        return f"Like(user={self.user_id}, post={self.post_id})"

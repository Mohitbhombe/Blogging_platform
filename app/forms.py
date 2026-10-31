"""
app/forms.py
Web Forms using Flask-WTF
---------------------------
Week 3 adds PostForm for creating and editing blog posts.
Week 4 adds CommentForm for the comment system.
Week 5 adds ProfileForm for editing user profile.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from app.models import User


# ── Registration Form ──────────────────────────────────────────────────
class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=20)]
    )
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account with this email already exists.')


# ── Login Form ─────────────────────────────────────────────────────────
class LoginForm(FlaskForm):
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember = BooleanField('Remember Me')
    submit   = SubmitField('Sign In')


# ── Post Form (Week 3) ─────────────────────────────────────────────────
class PostForm(FlaskForm):
    """
    Form for creating and editing blog posts.
    Used on both /post/new (create) and /post/<id>/edit (update).
    """
    title = StringField(
        'Post Title',
        validators=[
            DataRequired(message='Title is required.'),
            Length(min=3, max=200, message='Title must be between 3 and 200 characters.')
        ]
    )

    category = SelectField(
        'Category',
        choices=[
            ('General',      'General'),
            ('Tutorial',     'Tutorial'),
            ('Opinion',      'Opinion'),
            ('Announcement', 'Announcement'),
            ('Technology',   'Technology'),
            ('Python',       'Python'),
            ('Flask',        'Flask'),
            ('Career',       'Career'),
        ],
        validators=[DataRequired()]
    )

    content = TextAreaField(
        'Content',
        validators=[
            DataRequired(message='Content cannot be empty.'),
            Length(min=10, message='Post content must be at least 10 characters.')
        ]
    )

    submit = SubmitField('Publish Post')


# ── Comment Form (Week 4) ─────────────────────────────────────────────────────
class CommentForm(FlaskForm):
    """Simple one-field form for leaving a comment on a post."""
    body = TextAreaField(
        'Your Comment',
        validators=[
            DataRequired(message='Comment cannot be empty.'),
            Length(min=2, max=1000, message='Comment must be between 2 and 1000 characters.')
        ]
    )
    submit = SubmitField('Post Comment')


# ── Profile Form (Week 5) ─────────────────────────────────────────────────────
class ProfileForm(FlaskForm):
    """Form for editing the user's public profile."""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=20)]
    )
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email()]
    )
    bio = TextAreaField(
        'Bio',
        validators=[Optional(), Length(max=300, message='Bio must be under 300 characters.')]
    )
    submit = SubmitField('Save Changes')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('An account with this email already exists.')

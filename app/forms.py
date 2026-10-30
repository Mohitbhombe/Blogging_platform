"""
app/forms.py
Web Forms using Flask-WTF
---------------------------
Flask-WTF extends WTForms to integrate with Flask.
Each form class = one HTML form.
Each field in the class = one input in the form.
Validators automatically check user input on the server side.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError
)
from app.models import User


# ── Registration Form ──────────────────────────────────────────────────
class RegistrationForm(FlaskForm):
    """
    Form for new user sign-up.
    Validators run automatically when form.validate_on_submit() is called.
    """

    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required.'),
            Length(min=3, max=20, message='Username must be 3–20 characters.')
        ]
    )

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Please enter a valid email address.')
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=6, message='Password must be at least 6 characters.')
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords must match.')
        ]
    )

    submit = SubmitField('Create Account')

    # ── Custom Validators ──────────────────────────────────────────
    # If you name a method validate_<fieldname>, WTForms calls it
    # automatically during validation.

    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'This username is already taken. Please choose another.'
            )

    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'An account with this email already exists. Please log in.'
            )


# ── Login Form ─────────────────────────────────────────────────────────
class LoginForm(FlaskForm):
    """Form for existing user login."""

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Please enter a valid email address.')
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.')
        ]
    )

    # "Remember Me" checkbox — keeps user logged in after browser closes
    remember = BooleanField('Remember Me')

    submit = SubmitField('Sign In')

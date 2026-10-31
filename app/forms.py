"""
app/forms.py  —  Week 5: ProfileForm added
"""
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField,
                     SubmitField, TextAreaField, SelectField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from app.models import User


class RegistrationForm(FlaskForm):
    username         = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email            = StringField('Email Address', validators=[DataRequired(), Email()])
    password         = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    email    = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit   = SubmitField('Sign In')


class PostForm(FlaskForm):
    title = StringField('Post Title',
        validators=[DataRequired(), Length(min=3, max=200)])
    category = SelectField('Category', choices=[
        ('General','General'),('Tutorial','Tutorial'),('Opinion','Opinion'),
        ('Announcement','Announcement'),('Technology','Technology'),
        ('Python','Python'),('Flask','Flask'),('Career','Career'),
    ], validators=[DataRequired()])
    content = TextAreaField('Content',
        validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Publish Post')


class CommentForm(FlaskForm):
    body   = TextAreaField('Your Comment',
        validators=[DataRequired(), Length(min=2, max=1000)])
    submit = SubmitField('Post Comment')


class ProfileForm(FlaskForm):
    """Edit the logged-in user's public profile."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email    = StringField('Email Address', validators=[DataRequired(), Email()])
    bio      = TextAreaField('Bio', validators=[Optional(), Length(max=300)])
    submit   = SubmitField('Save Changes')

    def validate_username(self, username):
        if username.data != current_user.username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('Username already taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            if User.query.filter_by(email=email.data).first():
                raise ValidationError('Email already registered.')

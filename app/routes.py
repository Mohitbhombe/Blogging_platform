"""
app/routes.py
URL Routes (Pages)
-------------------
Defines all URL routes using Flask Blueprints.
Week 2 adds: register, login, logout, dashboard routes.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm

# Blueprint groups all our routes
main = Blueprint('main', __name__)


# ══════════════════════════════════════════════════════════════════
# PUBLIC PAGES
# ══════════════════════════════════════════════════════════════════

@main.route('/')
@main.route('/home')
def home():
    """Homepage — shows sample posts (real posts added in Week 3)."""
    posts = [
        {
            'title': 'Welcome to FlaskBlog!',
            'author': 'Mohit Bhombe',
            'date': 'October 30, 2026',
            'content': 'This is our first blog post. We built this platform using Python and Flask!',
            'category': 'Announcement'
        },
        {
            'title': 'Getting Started with Flask',
            'author': 'Mohit Bhombe',
            'date': 'October 30, 2026',
            'content': 'Flask is a lightweight and powerful web framework for Python. Here we explore why Flask is great for beginners.',
            'category': 'Tutorial'
        },
        {
            'title': 'Why Python is Amazing',
            'author': 'Mohit Bhombe',
            'date': 'October 30, 2026',
            'content': 'Python is one of the most popular languages in the world. Here are some reasons why developers love it.',
            'category': 'Opinion'
        },
    ]
    return render_template('home.html', posts=posts, title='Home')


@main.route('/about')
def about():
    """About page."""
    return render_template('about.html', title='About')


# ══════════════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ══════════════════════════════════════════════════════════════════

@main.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration Route.
    GET  → Show the registration form.
    POST → Process the form data, create user, redirect to login.

    If a user is already logged in, redirect them to home.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # ── Hash the password (NEVER store plain text!) ────────────
        # generate_password_hash creates a secure hash like:
        # 'scrypt:32768:8:1$...' — impossible to reverse
        hashed_password = generate_password_hash(form.password.data)

        # ── Create a new User object ───────────────────────────────
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        # ── Save to database ───────────────────────────────────────
        db.session.add(user)    # Stage the new user
        db.session.commit()     # Write to the database file

        # ── Show success message ───────────────────────────────────
        flash(f'Account created for {form.username.data}! You can now log in.', 'success')

        # ── Redirect to login page ─────────────────────────────────
        return redirect(url_for('main.login'))

    return render_template('auth/register.html', form=form, title='Register')


@main.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login Route.
    GET  → Show the login form.
    POST → Check credentials, log in user, redirect to dashboard.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        # ── Find user by email ─────────────────────────────────────
        user = User.query.filter_by(email=form.email.data).first()

        # ── Check password against stored hash ─────────────────────
        # check_password_hash compares form input with the stored hash
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            # Redirect to the page the user originally wanted to visit
            # (Flask-Login saves it in 'next' query parameter)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}! 👋', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')

    return render_template('auth/login.html', form=form, title='Login')


@main.route('/logout')
@login_required  # Only logged-in users can access this route
def logout():
    """Log out the current user and redirect to homepage."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.home'))


# ══════════════════════════════════════════════════════════════════
# PROTECTED PAGES (require login)
# ══════════════════════════════════════════════════════════════════

@main.route('/dashboard')
@login_required  # Redirects to login if not authenticated
def dashboard():
    """
    User Dashboard — only accessible when logged in.
    @login_required decorator automatically redirects to login page
    if the user is not authenticated.
    """
    return render_template('dashboard.html', title='Dashboard')

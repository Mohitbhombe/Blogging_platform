"""
app/__init__.py
Flask Application Factory
--------------------------
This file initializes the Flask app and all its extensions.
Using the 'Application Factory' pattern allows us to create
multiple instances of the app (e.g., for testing).
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize extensions (without binding to any app yet)
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    """
    Application Factory Function.
    Creates and configures the Flask application.
    """
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///blog.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Initialize extensions with app ─────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)

    # Redirect unauthorized users to login page
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # ── Register Blueprints (route groups) ─────────────────────────
    from app.routes import main
    app.register_blueprint(main)

    # ── Create database tables if they don't exist ─────────────────
    with app.app_context():
        db.create_all()

    return app

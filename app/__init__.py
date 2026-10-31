"""
app/__init__.py  —  Week 8: CSRFProtect added for AJAX support
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from markupsafe import Markup
from dotenv import load_dotenv
import os

load_dotenv()

db           = SQLAlchemy()
login_manager = LoginManager()
csrf         = CSRFProtect()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY']                 = os.environ.get('SECRET_KEY', 'fallback-dev-key')
    app.config['SQLALCHEMY_DATABASE_URI']    = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_HEADERS']           = ['X-CSRFToken', 'X-CSRF-Token']

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view           = 'main.login'
    login_manager.login_message_category = 'info'

    from app.routes import main
    app.register_blueprint(main)

    from app import models  # noqa: F401

    @app.template_filter('nl2br')
    def nl2br_filter(text):
        return Markup(str(text).replace('\n', '<br>\n'))

    with app.app_context():
        db.create_all()

    return app

"""
app/routes.py
URL Routes (Pages)
-------------------
This file defines all the URL routes for the application.
Each route is a function that runs when a user visits that URL.
We use Flask's Blueprint to group related routes together.
"""

from flask import Blueprint, render_template

# Create a Blueprint named 'main'
# Think of it as a mini-app that handles a group of related routes
main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    """
    Homepage route.
    When a user visits '/' or '/home', this function runs
    and returns the rendered home.html template.
    """
    # Sample posts data (later this will come from the database)
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
            'content': 'Flask is a lightweight and powerful web framework for Python. In this post, we explore why Flask is great for beginners.',
            'category': 'Tutorial'
        },
        {
            'title': 'Why Python is Amazing',
            'author': 'Mohit Bhombe',
            'date': 'October 30, 2026',
            'content': 'Python is one of the most popular programming languages in the world. Here are some reasons why developers love it.',
            'category': 'Opinion'
        },
    ]
    return render_template('home.html', posts=posts, title='Home')


@main.route('/about')
def about():
    """About page route."""
    return render_template('about.html', title='About')

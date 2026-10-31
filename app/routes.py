"""
app/routes.py  —  Week 3: Blog Post CRUD
C - Create  -> /post/new
R - Read    -> /  and  /post/<id>
U - Update  -> /post/<id>/edit
D - Delete  -> /post/<id>/delete
"""
from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request, abort)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Post
from app.forms import RegistrationForm, LoginForm, PostForm

main = Blueprint('main', __name__)

POSTS_PER_PAGE = 6


# ── PUBLIC PAGES ──────────────────────────────────────────────

@main.route('/')
@main.route('/home')
def home():
    page  = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('home.html', posts=posts, title='Home')


@main.route('/about')
def about():
    return render_template('about.html', title='About')


# ── AUTH ──────────────────────────────────────────────────────

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    password=generate_password_hash(form.password.data))
        db.session.add(user); db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', form=form, title='Register')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.username}! 👋', 'success')
            return redirect(request.args.get('next') or url_for('main.dashboard'))
        flash('Login failed. Check email and password.', 'danger')
    return render_template('auth/login.html', form=form, title='Login')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.home'))


# ── DASHBOARD ─────────────────────────────────────────────────

@main.route('/dashboard')
@login_required
def dashboard():
    user_posts = Post.query.filter_by(author_id=current_user.id)\
                           .order_by(Post.date_posted.desc()).all()
    return render_template('dashboard.html', title='Dashboard', posts=user_posts)


# ── POST CRUD ─────────────────────────────────────────────────

@main.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data,
                    category=form.category.data, author=current_user)
        db.session.add(post); db.session.commit()
        flash('Your post has been published! 🎉', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))
    return render_template('post/create.html', form=form,
                           title='New Post', legend='Create New Post')


@main.route('/post/<int:post_id>')
def post_detail(post_id):
    post = db.get_or_404(Post, post_id)
    return render_template('post/detail.html', post=post, title=post.title)


@main.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title    = form.title.data
        post.content  = form.content.data
        post.category = form.category.data
        db.session.commit()
        flash('Post updated! ✅', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data    = post.title
        form.content.data  = post.content
        form.category.data = post.category
    return render_template('post/create.html', form=form,
                           title='Edit Post', legend='Edit Post')


@main.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post); db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('main.home'))


@main.route('/user/<string:username>')
def user_posts(username):
    user  = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
                      .order_by(Post.date_posted.desc()).all()
    return render_template('home.html', posts=posts,
                           title=f"{username}'s Posts", author_filter=user)

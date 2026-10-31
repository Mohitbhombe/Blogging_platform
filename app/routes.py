"""
app/routes.py  —  Week 5: User Profile Page
"""
from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request, abort)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Post, Comment, Like
from app.forms import RegistrationForm, LoginForm, PostForm, CommentForm, ProfileForm

main = Blueprint('main', __name__)
POSTS_PER_PAGE = 6


@main.route('/')
@main.route('/home')
def home():
    page     = request.args.get('page', 1, type=int)
    category = request.args.get('category', '', type=str).strip()
    query    = Post.query.order_by(Post.date_posted.desc())
    if category:
        query = query.filter_by(category=category)
    pagination = query.paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    posts      = pagination.items
    all_cats   = db.session.query(Post.category).distinct().order_by(Post.category).all()
    categories = [c[0] for c in all_cats]
    return render_template('home.html', posts=posts, pagination=pagination,
                           category=category, categories=categories, title='Home')


@main.route('/about')
def about():
    return render_template('about.html', title='About')


@main.route('/search')
def search():
    q        = request.args.get('q', '', type=str).strip()
    category = request.args.get('category', '', type=str).strip()
    page     = request.args.get('page', 1, type=int)
    if not q and not category:
        flash('Please enter a search term or pick a category.', 'info')
        return redirect(url_for('main.home'))
    query = Post.query
    if q:
        like  = f'%{q}%'
        query = query.filter(db.or_(Post.title.ilike(like), Post.content.ilike(like)))
    if category:
        query = query.filter_by(category=category)
    query      = query.order_by(Post.date_posted.desc())
    pagination = query.paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    posts      = pagination.items
    all_cats   = db.session.query(Post.category).distinct().order_by(Post.category).all()
    categories = [c[0] for c in all_cats]
    return render_template('home.html', posts=posts, pagination=pagination,
                           search_query=q, category=category, categories=categories,
                           title=f'Search: {q}' if q else f'Category: {category}')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    password=generate_password_hash(form.password.data))
        db.session.add(user); db.session.commit()
        flash(f'Account created!', 'success')
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


@main.route('/dashboard')
@login_required
def dashboard():
    user_posts = Post.query.filter_by(author_id=current_user.id)\
                           .order_by(Post.date_posted.desc()).all()
    return render_template('dashboard.html', title='Dashboard', posts=user_posts)


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Week 5: Edit logged-in user's profile."""
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email    = form.email.data
        current_user.bio      = form.bio.data
        db.session.commit()
        flash('Profile updated successfully! ✅', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data    = current_user.email
        form.bio.data      = current_user.bio or ''
    return render_template('profile.html', form=form, title='Edit Profile')


@main.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data,
                    category=form.category.data, author=current_user)
        db.session.add(post); db.session.commit()
        flash('Post published! 🎉', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))
    return render_template('post/create.html', form=form, title='New Post', legend='Create New Post')


@main.route('/post/<int:post_id>')
def post_detail(post_id):
    post     = db.get_or_404(Post, post_id)
    comments = Comment.query.filter_by(post_id=post_id)\
                            .order_by(Comment.date_posted.asc()).all()
    form = CommentForm()
    return render_template('post/detail.html', post=post,
                           comments=comments, form=form, title=post.title)


@main.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)
    if post.author != current_user: abort(403)
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
    return render_template('post/create.html', form=form, title='Edit Post', legend='Edit Post')


@main.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    if post.author != current_user: abort(403)
    db.session.delete(post); db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('main.home'))


@main.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    pagination = Post.query.filter_by(author=user)\
                           .order_by(Post.date_posted.desc())\
                           .paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    return render_template('home.html', posts=pagination.items, pagination=pagination,
                           title=f"{username}'s Posts", author_filter=user)


@main.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = db.get_or_404(Post, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post_id=post.id, author_id=current_user.id)
        db.session.add(comment); db.session.commit()
        flash('Comment posted! 💬', 'success')
    else:
        for field, errors in form.errors.items():
            for e in errors: flash(e, 'danger')
    return redirect(url_for('main.post_detail', post_id=post_id) + '#comments')


@main.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    post_id = comment.post_id
    if comment.author_id != current_user.id and comment.post.author != current_user:
        abort(403)
    db.session.delete(comment); db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(url_for('main.post_detail', post_id=post_id) + '#comments')


# ── WEEK 6: LIKE SYSTEM ───────────────────────────────────────

@main.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    """Toggle like/unlike on a post. Returns JSON for AJAX."""
    from flask import jsonify
    post          = db.get_or_404(Post, post_id)
    existing_like = Like.query.filter_by(user_id=current_user.id,
                                         post_id=post_id).first()
    if existing_like:
        db.session.delete(existing_like); db.session.commit(); liked = False
    else:
        db.session.add(Like(user_id=current_user.id, post_id=post_id))
        db.session.commit(); liked = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'liked': liked, 'like_count': post.like_count})
    return redirect(url_for('main.post_detail', post_id=post_id))

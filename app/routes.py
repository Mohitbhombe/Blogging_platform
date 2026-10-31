"""
app/routes.py
URL Routes — Week 5-8: Profile + Likes + Markdown + Error Pages
---------------------------------------------------------------
C - Create  → /post/new
R - Read    → / (all posts, paginated)  and  /post/<id> (single post + comments)
U - Update  → /post/<id>/edit
D - Delete  → /post/<id>/delete
Comments    → POST /post/<id>/comment   DELETE /comment/<id>/delete
Search      → /search?q=<query>&category=<cat>
Profile     → /profile  (Week 5)
User Page   → /user/<username>
Likes       → POST /post/<id>/like (Week 6)
"""

from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request, abort, jsonify)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Post, Comment, Like
from app.forms import RegistrationForm, LoginForm, PostForm, CommentForm, ProfileForm

# Week 7: Markdown support
import markdown as md
from markupsafe import Markup

main = Blueprint('main', __name__)

# Posts per page for pagination
POSTS_PER_PAGE = 6


# ══════════════════════════════════════════════════════════════════
# PUBLIC PAGES
# ══════════════════════════════════════════════════════════════════

@main.route('/')
@main.route('/home')
def home():
    """
    Homepage — paginated posts feed.
    Supports optional category filter via ?category=<name>.
    """
    page     = request.args.get('page', 1, type=int)
    category = request.args.get('category', '', type=str).strip()

    query = Post.query.order_by(Post.date_posted.desc())

    if category:
        query = query.filter_by(category=category)

    pagination = query.paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    posts      = pagination.items

    # Collect unique categories that actually have posts
    all_categories = db.session.query(Post.category).distinct().order_by(Post.category).all()
    categories     = [c[0] for c in all_categories]

    return render_template(
        'home.html',
        posts=posts,
        pagination=pagination,
        category=category,
        categories=categories,
        title='Home',
    )


@main.route('/about')
def about():
    return render_template('about.html', title='About')


# ══════════════════════════════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════════════════════════════

@main.route('/search')
def search():
    """
    Full-text search across post titles and content.
    GET /search?q=<query>&category=<optional>
    """
    q        = request.args.get('q', '', type=str).strip()
    category = request.args.get('category', '', type=str).strip()
    page     = request.args.get('page', 1, type=int)

    if not q and not category:
        flash('Please enter a search term or pick a category.', 'info')
        return redirect(url_for('main.home'))

    query = Post.query

    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                Post.title.ilike(like),
                Post.content.ilike(like)
            )
        )

    if category:
        query = query.filter_by(category=category)

    query = query.order_by(Post.date_posted.desc())
    pagination = query.paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    posts      = pagination.items

    all_categories = db.session.query(Post.category).distinct().order_by(Post.category).all()
    categories     = [c[0] for c in all_categories]

    return render_template(
        'home.html',
        posts=posts,
        pagination=pagination,
        search_query=q,
        category=category,
        categories=categories,
        title=f'Search: {q}' if q else f'Category: {category}',
    )


# ══════════════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ══════════════════════════════════════════════════════════════════

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now log in.', 'success')
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
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}! 👋', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    return render_template('auth/login.html', form=form, title='Login')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.home'))


# ══════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════

@main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard shows the logged-in user's own posts."""
    user_posts = Post.query.filter_by(author_id=current_user.id)\
                           .order_by(Post.date_posted.desc()).all()
    return render_template('dashboard.html', title='Dashboard', posts=user_posts)


# ══════════════════════════════════════════════════════════════════
# WEEK 5: USER PROFILE
# ══════════════════════════════════════════════════════════════════

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Week 5: Edit the logged-in user's profile (username, email, bio).
    GET  → Show current profile in editable form.
    POST → Validate and save changes.
    """
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


@main.route('/user/<string:username>')
def user_posts(username):
    """
    Week 5: Public user page — shows all posts by that author + their bio.
    """
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()

    pagination = Post.query.filter_by(author=user)\
                           .order_by(Post.date_posted.desc())\
                           .paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    posts = pagination.items

    return render_template(
        'home.html',
        posts=posts,
        pagination=pagination,
        title=f"{username}'s Posts",
        author_filter=user,
    )


# ══════════════════════════════════════════════════════════════════
# BLOG POST CRUD
# ══════════════════════════════════════════════════════════════════

# ── C: CREATE ─────────────────────────────────────────────────────
@main.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    """
    Create a new blog post.
    GET  → Show blank PostForm.
    POST → Validate, save to DB, redirect to the new post.
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            author=current_user   # Flask-SQLAlchemy uses the backref 'author'
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been published! 🎉', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))
    return render_template('post/create.html', form=form, title='New Post',
                           legend='Create New Post')


# ── R: READ (single post) ─────────────────────────────────────────
@main.route('/post/<int:post_id>')
def post_detail(post_id):
    """
    View a single blog post along with its comments.
    Week 7: content is rendered as Markdown → HTML.
    """
    post = db.get_or_404(Post, post_id)
    comments = Comment.query.filter_by(post_id=post_id)\
                            .order_by(Comment.date_posted.asc()).all()
    form = CommentForm()

    # Week 7: Render Markdown content to safe HTML
    rendered_content = Markup(md.markdown(
        post.content,
        extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
    ))

    # Week 6: Did current user like this post?
    user_liked = False
    if current_user.is_authenticated:
        user_liked = post.is_liked_by(current_user)

    return render_template('post/detail.html', post=post,
                           comments=comments, form=form,
                           rendered_content=rendered_content,
                           user_liked=user_liked,
                           title=post.title)


# ── U: UPDATE (edit) ──────────────────────────────────────────────
@main.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """
    Edit an existing post.
    Only the AUTHOR of the post can edit it.
    abort(403) = HTTP 403 Forbidden error.
    """
    post = db.get_or_404(Post, post_id)

    # Security check: only the author can edit their own post
    if post.author != current_user:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        # Update the post fields
        post.title    = form.title.data
        post.content  = form.content.data
        post.category = form.category.data
        db.session.commit()   # No need for db.session.add() — post is already tracked
        flash('Your post has been updated! ✅', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))

    elif request.method == 'GET':
        # Pre-fill the form with existing post data
        form.title.data    = post.title
        form.content.data  = post.content
        form.category.data = post.category

    return render_template('post/create.html', form=form, title='Edit Post',
                           legend='Edit Post')


# ── D: DELETE ─────────────────────────────────────────────────────
@main.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """
    Delete a blog post.
    Only accepts POST requests (form submission) — never GET.
    This prevents accidental deletion if someone visits the URL directly.
    """
    post = db.get_or_404(Post, post_id)

    # Security check: only the author can delete their own post
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.', 'info')
    return redirect(url_for('main.home'))


# ══════════════════════════════════════════════════════════════════
# COMMENT SYSTEM
# ══════════════════════════════════════════════════════════════════

@main.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """
    Add a comment to a blog post.
    Only accepts POST requests.
    Logged-in users only.
    """
    post = db.get_or_404(Post, post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            post_id=post.id,
            author_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted! 💬', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'danger')

    return redirect(url_for('main.post_detail', post_id=post_id) + '#comments')


@main.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """
    Delete a comment.
    Only the comment author OR the post author can delete a comment.
    """
    comment = db.get_or_404(Comment, comment_id)
    post_id = comment.post_id

    # Security check
    if comment.author_id != current_user.id and comment.post.author != current_user:
        abort(403)

    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(url_for('main.post_detail', post_id=post_id) + '#comments')


# ══════════════════════════════════════════════════════════════════
# WEEK 6: LIKE SYSTEM
# ══════════════════════════════════════════════════════════════════

@main.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    """
    Week 6: Toggle like/unlike on a post.
    Returns JSON with updated like count and liked status.
    Supports both AJAX (JSON) and plain form POST (redirect).
    """
    post = db.get_or_404(Post, post_id)

    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if existing_like:
        # Already liked → unlike
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        # Not liked → like
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        liked = True

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
       request.accept_mimetypes.accept_json:
        return jsonify({
            'liked': liked,
            'like_count': post.like_count
        })

    # Fallback: redirect back to post page
    return redirect(url_for('main.post_detail', post_id=post_id))


# ══════════════════════════════════════════════════════════════════
# WEEK 8: CUSTOM ERROR PAGES
# ══════════════════════════════════════════════════════════════════

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html', title='403 Forbidden'), 403


@main.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html', title='404 Not Found'), 404


@main.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html', title='500 Server Error'), 500

# 📝 FlaskBlog — Full-Stack Blogging Platform

A premium, full-stack blogging platform built with **Python Flask**, developed as an 8-week internship project.  
Features a stunning dark-themed UI with glassmorphism, smooth animations, and a complete feature set.

---

## ✨ Features

| Week | Feature |
|------|---------|
| Week 1 | Project setup, Flask app factory, Bootstrap dark UI |
| Week 2 | User Registration & Login with Flask-Login + Flask-WTF |
| Week 3 | Blog Post CRUD (Create, Read, Update, Delete) |
| Week 4 | Comment system, Search & Filter, Pagination |
| Week 5 | User Profile page (bio, avatar, post/comment stats) |
| Week 6 | Post Like / Unlike system (AJAX), Estimated reading time |
| Week 7 | Markdown rendering for post content (headers, code blocks, tables) |
| Week 8 | Custom error pages (403, 404, 500), polished README |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.x, Flask 3.1, Flask-SQLAlchemy, Flask-Login, Flask-WTF |
| **Database** | SQLite (via SQLAlchemy ORM) |
| **Frontend** | HTML5, Bootstrap 5, Vanilla CSS (custom dark theme) |
| **Markdown** | Python-Markdown library |
| **Icons** | Bootstrap Icons |
| **Fonts** | Google Fonts (Inter + Playfair Display) |
| **Auth** | Werkzeug password hashing, Flask-Login sessions |

---

## 🗂️ Project Structure

```
Blogging_Platform/
├── app/
│   ├── __init__.py        # App factory
│   ├── models.py          # User, Post, Comment, Like models
│   ├── forms.py           # WTForms (Register, Login, Post, Comment, Profile)
│   ├── routes.py          # All URL routes & views
│   └── templates/
│       ├── base.html      # Shared layout + navbar + footer
│       ├── home.html      # Posts feed + search + pagination
│       ├── dashboard.html # User's own posts
│       ├── profile.html   # Edit user profile (Week 5)
│       ├── about.html
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── post/
│       │   ├── create.html  # Create & Edit post form
│       │   └── detail.html  # Post view + likes + comments
│       └── errors/
│           ├── 403.html
│           ├── 404.html
│           └── 500.html
├── static/
│   ├── css/style.css      # 2000+ lines custom dark theme
│   └── js/main.js         # Scroll effects, animations
├── instance/
│   └── blog.db            # SQLite database
├── run.py                 # App entry point
├── requirements.txt
└── .env                   # SECRET_KEY, DATABASE_URL
```

---

## 📦 Setup Instructions

```bash
# Clone the repository
git clone https://github.com/Mohitbhombe/Blogging_platform.git
cd Blogging_platform

# Create & activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Run the development server
python run.py
```

Then open your browser at **http://127.0.0.1:5000** 🚀

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///blog.db
```

---

## 🎯 Key Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Homepage — paginated posts feed |
| `/search?q=<query>` | GET | Full-text search |
| `/register` | GET/POST | User registration |
| `/login` | GET/POST | User login |
| `/dashboard` | GET | User's own posts (auth required) |
| `/profile` | GET/POST | Edit profile (auth required) |
| `/post/new` | GET/POST | Create a post (auth required) |
| `/post/<id>` | GET | View post + comments |
| `/post/<id>/edit` | GET/POST | Edit post (author only) |
| `/post/<id>/delete` | POST | Delete post (author only) |
| `/post/<id>/like` | POST | Toggle like (AJAX, auth required) |
| `/post/<id>/comment` | POST | Add comment (auth required) |
| `/user/<username>` | GET | Public author page |

---

## 👨‍💻 Author

**Mohit Bhombe**  
8-Week Flask Full-Stack Internship Project  
© 2026

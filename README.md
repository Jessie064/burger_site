# ============================================================
# BurgerCraft – Django Burger Restaurant Website
# ============================================================

A secure, locally-run Django web application for a fictional burger restaurant.

---

## Prerequisites

- Python 3.10 or higher
- pip

---

## Setup & Run

```powershell
# 1. Navigate to the project folder
cd "c:\Users\Jessie\OneDrive\Desktop\Web_pentest\burger_site"

# 2. (Recommended) Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. Create a superuser (admin account)
python manage.py createsuperuser

# 6. (Optional) Add sample burgers via the Django admin
#    After step 7, go to http://127.0.0.1:8000/django-admin/
#    and add some Burger entries.

# 7. Start the development server
python manage.py runserver
```

Open your browser and visit: **http://127.0.0.1:8000/**

---

## Pages

| URL | Page | Access |
|---|---|---|
| `/` | Home | Public |
| `/menu/` | Full Menu | Public |
| `/contact/` | Feedback / Contact | Public |
| `/login/` | Login | Public |
| `/register/` | Register | Public |
| `/logout/` | Logout (POST) | Logged-in users |
| `/profile/` | My Profile | Logged-in users |
| `/admin-panel/` | Staff Dashboard | Staff users only |
| `/django-admin/` | Django Built-in Admin | Superusers only |

---

## Security Features

| Feature | Implementation |
|---|---|
| SQL Injection prevention | Django ORM only — no raw SQL |
| XSS prevention | Django auto-escaping in all templates |
| CSRF protection | `{% csrf_token %}` on every form |
| Password strength | 4 built-in validators (min 8 chars, no common passwords) |
| Admin page guard | `@login_required` + `@user_passes_test(is_staff)` |
| No IDOR | Profile page uses `request.user` — no user ID in URL |
| Secure cookies | `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'` |

---

## Project Structure

```
burger_site/
├── manage.py
├── requirements.txt
├── README.md
├── burger_site/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── restaurant/
    ├── models.py        ← Burger, Feedback, UserProfile
    ├── views.py         ← All views (secured)
    ├── forms.py         ← Registration, Login, Feedback, Profile forms
    ├── urls.py          ← URL routing
    ├── admin.py         ← Model registration
    ├── templates/restaurant/
    │   ├── base.html
    │   ├── home.html
    │   ├── menu.html
    │   ├── login.html
    │   ├── register.html
    │   ├── contact.html
    │   ├── admin_panel.html
    │   └── profile.html
    └── static/restaurant/
        └── style.css
```

---

## Notes

- `DEBUG = True` in `settings.py` is fine for local development. Set it to `False` for any real deployment.
- The `SECRET_KEY` reads from the `DJANGO_SECRET_KEY` environment variable. If not set, a local default is used — **change this before any real deployment**.

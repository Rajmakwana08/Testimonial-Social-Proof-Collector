# Proofly - Testimonial & Social Proof Collector

A simple Django application for collecting customer testimonials, moderating them, and presenting approved feedback in a branded Wall of Love.

## What is included

- Owner accounts, signup, login, password reset, and an in-app email-verification simulation
- Branded Spaces with custom prompts, logo upload, optional avatar, optional ratings, and custom questions
- Public no-login testimonial forms at `/collect/<space-slug>/`
- A dashboard with filtering, search, rating filters, moderation, featured/liked controls, and rating metrics
- A public Wall of Love at `/wall/<space-slug>/` and iframe-friendly embed at `/embed/<space-slug>/`
- JSON token endpoints with an access token response and rotating refresh token in an HttpOnly cookie

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`, create an account, then create your first Space. For development, Django uses the console email backend: password-reset mail and similar messages appear in the terminal.

## Useful routes

| Route | Purpose |
| --- | --- |
| `/dashboard/` | Owner moderation and analytics dashboard |
| `/spaces/new/` | Create a branded collection Space |
| `/collect/<slug>/` | Public testimonial collection form |
| `/wall/<slug>/` | Public showcase of approved testimonials |
| `/embed/<slug>/` | Responsive iframe view for an external site |
| `/api/token/` | `POST` username/password for a JWT access token |
| `/api/token/refresh/` | `POST` to renew from the refresh-cookie token |

## Notes

- Uploaded logos and avatars are saved under `media/` in development.
- Set `DEBUG=False`, a strong `SECRET_KEY`, valid `ALLOWED_HOSTS`, and `SECURE_COOKIES=True` before deployment.

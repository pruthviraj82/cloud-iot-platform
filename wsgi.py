import os

# Keep this file minimal and environment-driven so deployment platforms
# (GitHub, Render, Heroku, etc.) can set environment variables externally.
# Do NOT hardcode absolute paths here so the app is portable.

# Ensure a production env by default; platforms may override this.
os.environ.setdefault('FLASK_ENV', 'production')
# Allow SECRET_KEY to come from the environment; a placeholder is used when
# not provided (replace this on production deployments).
os.environ.setdefault('SECRET_KEY', 'change-me-to-a-secret-key')

# Create the Flask application instance used by WSGI servers (gunicorn).
from app import create_app

application = create_app()

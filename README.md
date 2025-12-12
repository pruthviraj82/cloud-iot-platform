# Smart IoT Platform

Minimal notes to run and deploy this Flask-based IoT dashboard.

Prerequisites
- Python 3.8+ (3.11 recommended)
- pip

Run locally
1. Create and activate a virtualenv:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app locally:

```bash
python run.py
# or
flask run
```

Deployment (Render / Heroku)
- The repo includes a `Procfile` to run Gunicorn: `web: gunicorn wsgi:application`.
- Configure environment variables on the host: `SECRET_KEY`, and any DB settings.

Notes
- Do not commit secrets to the repo. Use environment variables for production.
- The `wsgi.py` file is environment-driven so hosting platforms can set paths and secrets.

If you want, I can also prepare a `render.yaml` or GitHub Actions workflow next.
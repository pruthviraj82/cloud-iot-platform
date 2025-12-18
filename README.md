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

Local Serial Agent (forward serial data to hosted app)
--------------------------------------------------

If you run the Flask app on Render (or any cloud host) it cannot access your machine's USB/COM ports. Use the local agent on the machine with the USB device to forward serial lines to the hosted app.

1. On the server (host), set an agent token environment variable:

```bash
export DEVICE_AGENT_TOKEN="your_secret_token"
# Windows PowerShell:
$env:DEVICE_AGENT_TOKEN="your_secret_token"
```

2. Run the web app as usual.

3. On your local machine (where the Arduino is), install dependencies and run the agent:

```bash
pip install -r requirements.txt
python agent/serial_agent.py --port COM3 --baud 9600 --server http://<your-app>/api/forward-serial --token your_secret_token
```

The agent will read lines from the serial port and forward them securely to the app, which will treat them as live device data.
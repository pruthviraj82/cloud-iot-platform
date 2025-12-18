from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets
from flask import session, request, abort

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super_secure_key_123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'
    login_manager.login_message_category = 'info'
    
    with app.app_context():
        # Import models
        from app.models import User, DeviceConnection
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Import and register blueprints
        from app.routes import routes
        app.register_blueprint(routes)
        
        # Create all database tables
        db.create_all()

    # CSRF protection: generate per-session token and enforce for unsafe methods
    @app.before_request
    def ensure_csrf():
        # Only enforce for state-changing methods
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return

        # If agent provides valid token header, allow (used by local agents)
        agent_token = request.headers.get('X-DEVICE-AGENT-TOKEN')
        expected = app.config.get('DEVICE_AGENT_TOKEN') or os.getenv('DEVICE_AGENT_TOKEN')
        if expected and agent_token and agent_token == expected:
            return

        # Otherwise require per-session CSRF token header
        # Create token if missing
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)

        header = request.headers.get('X-CSRF-Token')
        if not header or header != session.get('csrf_token'):
            # Allow if endpoint is explicitly safe or unauthenticated GETs handled elsewhere
            # Reject the request
            abort(401, description='Missing or invalid CSRF token')

    @app.context_processor
    def inject_csrf_token():
        # Ensure token exists
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)
        return {'csrf_token': session.get('csrf_token')}
    
    return app
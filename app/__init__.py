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

    # CSRF protection removed to avoid blocking local web app requests
    # If you need CSRF protection later, reintroduce middleware or use Flask-WTF's CSRFProtect.
    
    return app
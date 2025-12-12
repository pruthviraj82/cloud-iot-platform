from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class DeviceConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    port_name = db.Column(db.String(100), nullable=False)
    baudrate = db.Column(db.Integer, default=9600)
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    disconnected_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='connected')
    
    user = db.relationship('User', backref=db.backref('devices', lazy=True))
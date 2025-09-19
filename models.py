from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    parental_control_enabled = db.Column(db.Boolean, default=False, nullable=False)
    generations = db.relationship('Generation', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Generation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    style_type = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)
    public_image_path = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='private')
    download_status = db.Column(db.String(20), nullable=False, default='none')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_deleted_by_user = db.Column(db.Boolean, default=False, nullable=False)
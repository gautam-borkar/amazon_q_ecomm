from flask_login import UserMixin
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    otp_secret = db.Column(db.String(16))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # One-to-many relationship with Cart
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    
    # One-to-many relationship with Order
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
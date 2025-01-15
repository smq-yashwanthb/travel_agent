from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import db
from app import login_manager

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_type = db.Column(db.String(20), nullable=False)  # hotel/transport
    status = db.Column(db.String(20), nullable=False)
    booking_details = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    payment_status = db.Column(db.String(20))
    payment_id = db.Column(db.String(100))
    total_amount = db.Column(db.Float)
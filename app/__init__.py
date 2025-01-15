# app/__init__.py
from flask import Flask
from app.routes import main
from .db import db, login_manager  # Import db and login_manager from db.py
from config import Config
from .auth import auth  # Import auth blueprint

def create_app():
    
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
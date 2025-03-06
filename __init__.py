import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import load_user

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.update(SECRET_KEY=os.urandom(24))
    login_manager.init_app(app)
    login_manager.user_loader(load_user)
    return app

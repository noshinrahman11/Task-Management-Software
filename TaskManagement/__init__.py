import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from TaskManagement.models import load_user
from flask_mail import Mail

mail = Mail() # Initialize Flask-Mail
login_manager = LoginManager()

MAIL_USERNAME="taskmanagementsystemcs264@gmail.com"
MAIL_PASSWORD="aebn jexs dokr whwb"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Use an in-memory test database
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing forms

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.update(SECRET_KEY=os.urandom(24))

    

    # Configure Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    # app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    # app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') 
    # app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_USERNAME'] = MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = MAIL_USERNAME

    login_manager.init_app(app)
    mail.init_app(app)
    
    login_manager.user_loader(load_user)

    def print_routes():
        print("Registered Routes:")
        for rule in app.url_map.iter_rules():
            print(f"Endpoint: {rule.endpoint}, URL: {rule.rule}")
    
    # Uncomment the following line to print routes on every request (for debugging)
    # app.before_request(print_routes) 

    return app





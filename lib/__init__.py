from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise RuntimeError('DATABASE_URL environment variable must be set for production.')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
    app.config['FRONTEND_BASE_URL'] = os.environ.get('FRONTEND_BASE_URL', 'http://localhost:5173')
    app.config['FRONTEND_ROUTES'] = {
        'HOME': '/',
        'LOGIN': '/login',
        'REGISTER': '/register',
        'DASHBOARD': '/dashboard',
        'MARKETPLACE': '/marketplace',
        'RESOURCES': '/resources/articles',
        'PASSWORD_RESET': '/reset-password',
        # Add all routes that match your frontend structure
    }
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['FRONTEND_BASE_URL'],
            "supports_credentials": True
        }
    })
    
    # Register blueprints
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app